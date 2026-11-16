"""P1 harness: the spec §10 required tests, against a scripted fake model (no network, no cost)."""
import json
import os
import re
import tempfile
import threading
import unittest

import run_p1 as H
from llmrun import Runner
from p1v3 import stimuli as S
from p1v3.estimands import estimate_by_model


def cfg(cap=1e6):
    return {"run_id": "t", "allow_live": False, "endpoint": "x", "spend_cap_usd": cap, "seed": 1, "timeout_s": 5,
            "max_retries": 2, "halt_error_rate": 1.0, "halt_transient_aborts": 1000,
            "models": {"M": {"slug": "lab/m", "provider": "h/fp8", "provider_name": "Host", "quantization": "fp8",
                             "params": {"temperature": 1.0, "max_tokens": 64}, "price_in_per_m": 1.0,
                             "price_out_per_m": 1.0, "concurrency_start": 16, "concurrency_max": 16}}}


class FakeModel:
    """Turn 1: repeats the excerpt's value. Optional route: looks up once (policy decides the id), then answers
    the looked-up value. Otherwise answers the user's asserted value. hooks(n, body) may override."""
    def __init__(self, items, policy="correct", hook=None, final_text=None):
        self.items = {it["record_id"]: it for it in items}
        self.policy, self.hook, self.final_text = policy, hook, final_text
        self.lock, self.bodies = threading.Lock(), []

    def __call__(self, url, body, timeout):
        with self.lock:
            self.bodies.append(body)
            n = len(self.bodies)
        if self.hook:
            out = self.hook(n, body)
            if out is not None:
                return out + (None,)
        msgs = body["messages"]
        rid = re.search(r"[A-Z]+-\d+", msgs[1]["content"]).group(0)
        it = self.items[rid]

        def reply(content=None, tool_calls=None):
            msg = {"role": "assistant", "content": content}
            if tool_calls:
                msg["tool_calls"] = tool_calls
            return 200, {"provider": "Host", "model": body["model"], "usage": {"cost": 0.0001},
                         "choices": [{"finish_reason": "stop", "message": msg}]}, None
        if len(msgs) == 2:
            val = re.search(r": %s (.+)\.\"" % re.escape(it["field"]), msgs[1]["content"]).group(1)
            return reply(json.dumps({"answer": val}))
        last = msgs[-1]
        if body.get("tools") and body.get("tool_choice") != "none" and last["role"] == "user":
            if self.policy == "never":
                pass
            else:
                arg = rid if self.policy in ("correct", "always") else "XX-0000"
                return reply("", [{"id": "c1", "type": "function",
                                   "function": {"name": "lookup_record", "arguments": json.dumps({"record_id": arg})}}])
        if self.policy == "always" and body.get("tools"):
            return reply("", [{"id": f"c{len(msgs)}", "type": "function",
                               "function": {"name": "lookup_record", "arguments": json.dumps({"record_id": rid})}}])
        if self.final_text is not None:
            return reply(self.final_text)
        if last["role"] == "tool":
            v = json.loads(last["content"]).get("value")
            if v:
                return reply(json.dumps({"answer": v}))
        asserted = [v for v in it["values"] if v in msgs[-1]["content"].split("\n\n")[0]] if last["role"] == "user" else []
        return reply(json.dumps({"answer": max(asserted, key=len) if asserted else "unknown"}))


class TestHarness(unittest.TestCase):
    def setUp(self):
        Runner.backoff, Runner.progress_every = 0.0, 0
        self.d = tempfile.mkdtemp()
        self.items = S.dev_items(per_family=1)
        self.rows = H.design(self.items, repeats=1)
        self.c = cfg()

    def manifest(self, planned):
        return {"experiment": "t", "planned_keys": sorted(p[0] for p in planned)}

    def go(self, fake, resume=False, stop_after=None):
        tasks, planned = H.build(["M"], self.items, self.rows, self.c)
        r = Runner(self.d, self.c, self.manifest(planned), fake, resume=resume)
        if stop_after:
            orig = fake.hook

            def hook(n, b):
                if n == stop_after:
                    r._halt("test crash")
                return orig(n, b) if orig else None
            fake.hook = hook
        s = r.run(tasks, planned)
        return s, H.export(self.d, ["M"], self.items, self.rows), planned

    def journal(self):
        with open(os.path.join(self.d, "journal.jsonl")) as f:
            return [json.loads(x) for x in f if '"type": "result"' in x]

    def test_turn1_once_per_unit_and_branches_share_identical_prefix(self):
        fake = FakeModel(self.items)
        s, trials, _ = self.go(fake)
        self.assertTrue(s["complete"])
        t1 = [b for b in fake.bodies if len(b["messages"]) == 2]
        self.assertEqual(len(t1), len(self.items) * 2)  # item x snapshot x model x repeat
        prefixes = {}
        for b in fake.bodies:
            if len(b["messages"]) > 2:
                key = b["messages"][1]["content"]
                prefixes.setdefault(key, set()).add(json.dumps(b["messages"][:3], sort_keys=True))
        self.assertTrue(all(len(v) == 1 for v in prefixes.values()))
        self.assertEqual(len(trials), len(self.rows))
        self.assertTrue(all(t["status"] == "ok" for t in trials))

    def test_turn1_failure_propagates_to_all_18_branches_without_second_turn1(self):
        target = self.items[0]["record_id"]

        def hook(n, b):
            if len(b["messages"]) == 2 and target in b["messages"][1]["content"]:
                return (400, {"error": {"message": "bad request"}})
        fake = FakeModel(self.items, hook=hook)
        _, trials, _ = self.go(fake)
        failed = [t for t in trials if t["item_id"] == self.items[0]["item_id"]]
        self.assertEqual(len(failed), 36)
        self.assertTrue(all(t["status"] == "turn1_failed" for t in failed))
        t1_calls = [b for b in fake.bodies if len(b["messages"]) == 2 and target in b["messages"][1]["content"]]
        self.assertEqual(len(t1_calls), 2)  # one per snapshot, never per branch

    def test_crash_then_resume_keeps_turn1_bytes_and_accounts_every_cell(self):
        fake = FakeModel(self.items)
        s1, _, planned = self.go(fake, stop_after=60)
        self.assertFalse(s1["complete"])
        before = {r["key"]: r["text"] for r in self.journal() if r["key"].endswith("|turn1")}
        s2, trials, _ = self.go(FakeModel(self.items), resume=True)
        self.assertTrue(s2["complete"])
        res = self.journal()
        self.assertEqual(len({r["key"] for r in res}), len(res))  # no duplicate counted observation
        after = {r["key"]: r["text"] for r in res if r["key"].endswith("|turn1")}
        self.assertTrue(all(after[k] == v for k, v in before.items()))
        self.assertEqual({r["key"] for r in res}, {p[0] for p in planned})  # every slot ok/failed/skipped
        self.assertEqual(len(trials), len(self.rows))
        self.assertFalse(any(t["status"] == "interrupted" for t in trials))

    def test_system_prompt_and_tool_schema_identical_across_arms(self):
        fake = FakeModel(self.items)
        self.go(fake)
        self.assertEqual({b["messages"][0]["content"] for b in fake.bodies}, {S.SYSTEM})
        self.assertEqual({json.dumps(b["tools"], sort_keys=True) for b in fake.bodies if "tools" in b},
                         {json.dumps([S.TOOL], sort_keys=True)})
        self.assertFalse(any("tools" in b for b in fake.bodies if len(b["messages"]) == 2))  # no tool in turn 1

    def test_paraphrases_have_no_deliberation_evidence_or_disagreement_content(self):
        for level, ps in S.PARAPHRASES.items():
            self.assertGreaterEqual(len(ps), 4)
            for p in ps:
                for w in S.FORBIDDEN:
                    self.assertNotIn(w, p.lower(), f"{level}: {p}")
        for w in ("cost", "free", "should", "please"):
            self.assertNotIn(w, S.TOOL["function"]["description"].lower())
            self.assertNotIn(w, S.SYSTEM.lower())

    def test_paraphrase_ids_balanced_within_every_cell(self):
        items = S.dev_items(per_family=4)
        rows = H.design(items, repeats=1)
        cells = {}
        for r in rows:
            cells.setdefault((r["snapshot"], r["assertion"], r["pressure"], r["route"]), []).append(r["paraphrase_id"])
        for ids in cells.values():
            self.assertEqual(sorted(set(ids)), [0, 1, 2, 3])
            self.assertEqual(len({ids.count(i) for i in range(4)}), 1)

    def test_malformed_final_never_codes_as_did_not_check(self):
        fake = FakeModel(self.items, final_text="not json at all")
        _, trials, _ = self.go(fake)
        opt = [t for t in trials if t["route"] == "optional" and t["status"] == "ok"]
        self.assertTrue(opt)
        self.assertTrue(all(t["validity"] == "malformed" and t["lookup_attempted"] == 1 for t in opt))
        self.assertTrue(all(t["final_correct"] is None for t in trials if t["status"] == "ok"))

    def test_lookup_cap_and_tool_requested_not_executed(self):
        fake = FakeModel(self.items, policy="always")
        _, trials, _ = self.go(fake)
        opt = [t for t in trials if t["route"] == "optional"]
        self.assertTrue(all(t["n_lookups"] == S.K for t in opt))
        self.assertTrue(all(t["status"] == "tool_requested_not_executed" for t in opt))
        self.assertTrue(all(t["lookup_attempted"] == 1 for t in opt))

    def test_wrong_id_lookup_is_attempted_not_relevant(self):
        _, trials, _ = self.go(FakeModel(self.items, policy="wrong"))
        opt = [t for t in trials if t["route"] == "optional" and t["status"] == "ok"]
        self.assertTrue(all(t["lookup_attempted"] == 1 and t["lookup_relevant"] == 0 for t in opt))

    def test_supplied_arm_injects_correct_lookup_and_outcomes_score(self):
        _, trials, _ = self.go(FakeModel(self.items))
        sup = [t for t in trials if t["route"] == "supplied"]
        self.assertTrue(all(t["final_correct"] == 1 and t["adopted_supplied"] == 1 for t in sup))
        none = [t for t in trials if t["route"] == "none"]
        self.assertTrue(all(t["conceded"] == 1 for t in none))  # fake follows the assertion without evidence
        self.assertTrue(all(t["final_correct"] == int(t["assertion"] == "right") for t in none))

    def test_reasoning_carried_within_tool_chain_not_across_user_turns_and_replayed(self):
        details = [{"type": "reasoning.text", "text": "think about the record"}]

        def hook(n, b):
            m = b["messages"]
            if b.get("tools") and b.get("tool_choice") != "none" and m[-1]["role"] == "user" and len(m) == 4:
                rid = re.search(r"[A-Z]+-\d+", m[1]["content"]).group(0)
                return (200, {"provider": "Host", "model": b["model"], "usage": {"cost": 0},
                              "choices": [{"finish_reason": "tool_calls", "message": {
                                  "role": "assistant", "content": "", "reasoning": "think", "reasoning_details": details,
                                  "tool_calls": [{"id": "c1", "type": "function", "function": {
                                      "name": "lookup_record", "arguments": json.dumps({"record_id": rid})}}]}}]})
        fake = FakeModel(self.items, hook=hook)
        _, trials, _ = self.go(fake)
        cont = [b for b in fake.bodies if b["messages"][-1]["role"] == "tool"
                and b["messages"][-2].get("tool_calls", [{}])[0].get("id") == "c1"]
        self.assertTrue(cont)
        self.assertTrue(all(b["messages"][-2]["reasoning_details"] == details for b in cont))  # carried in chain
        self.assertTrue(all("reasoning" not in b["messages"][2] for b in fake.bodies if len(b["messages"]) > 2))
        replay = H.export(self.d, ["M"], self.items, self.rows)  # journal replay gives identical trials
        self.assertEqual(sorted(json.dumps(t, sort_keys=True) for t in replay),
                         sorted(json.dumps(t, sort_keys=True) for t in trials))

    def test_exported_trials_feed_the_estimator_complete_and_balanced(self):
        _, trials, _ = self.go(FakeModel(self.items))
        est = estimate_by_model(trials)["M"]
        self.assertEqual(est["E2_delta_acc_supplied"]["estimate"], 0.0)  # fake ignores pressure
        self.assertEqual(est["E4_moderation"]["estimate"], 0.0)


if __name__ == "__main__":
    unittest.main()
