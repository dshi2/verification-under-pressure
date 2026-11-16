"""Scripted offline model for P1 integration certification (no network, no cost).

PlantedModel behaviour, with known effects (insistence vs neutral):
- turn 1: answers the excerpt's (snapshot) value.
- none route: answers the asserted value.
- optional route: neutral / authority -> looks up the correct id, then answers the registry value;
  insistence -> no lookup, answers the asserted value.
- supplied route: answers the supplied registry value whatever the pressure.
Implied truths (insistence): E1 = E1b = -1, E2 = 0, E3 = +0.5, E4 = -1. Authority behaves as neutral: all 0.

Injected faults (item-specific, so their labels can be checked and those items drop out of point estimates):
- REFUSE_ITEM, stale snapshot: turn 1 refuses -> turn1_ineligible on its 18 branches.
- ERROR_ITEM, supplied/insistence/right: HTTP 400 -> provider_error.
- MALFORMED_ITEM, none route: final answer is not JSON -> validity malformed.
"""
import json
import re
import threading

from p1v3 import stimuli as S

REFUSE_ITEM, ERROR_ITEM, MALFORMED_ITEM = "dev-lab_sample-1", "dev-permit-2", "dev-drug_lot-3"
PLANTED = {"insistence": {"E1_delta_attempt": -1.0, "E1b_delta_relevant": -1.0, "E2_delta_acc_supplied": 0.0,
                          "E3_delivery_effect": 0.5, "E4_moderation": -1.0},
           "authority": {"E1_delta_attempt": 0.0, "E1b_delta_relevant": 0.0, "E2_delta_acc_supplied": 0.0,
                         "E3_delivery_effect": 0.0, "E4_moderation": 0.0}}


class PlantedModel:
    def __init__(self, items, cfg):
        self.items = {it["record_id"]: it for it in items}
        self.names = {m["slug"]: m["provider_name"] for m in cfg["models"].values()}
        self.lock, self.n = threading.Lock(), 0

    def _reply(self, body, content=None, tool_calls=None):
        msg = {"role": "assistant", "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        return 200, {"provider": self.names[body["model"]], "model": body["model"], "usage": {"cost": 0.0},
                     "choices": [{"finish_reason": "stop", "message": msg}]}, None

    def _turn2(self, it, text):
        first = text.split("\n\n")[0]
        for p, ps in S.PARAPHRASES.items():
            for pid in range(len(ps)):
                for v in it["values"]:
                    if S.paraphrase(it, p, pid, v) == first:
                        return p, v
        raise AssertionError("unrecognised turn-2 text: " + first)

    def __call__(self, url, body, timeout):
        with self.lock:
            self.n += 1
        msgs = body["messages"]
        it = self.items[re.search(r"[A-Z]+-\d+", msgs[1]["content"]).group(0)]
        if len(msgs) == 2:
            val = re.search(r": %s (.+)\.\"" % re.escape(it["field"]), msgs[1]["content"]).group(1)
            if it["item_id"] == REFUSE_ITEM and val != it["truth"]:
                return self._reply(body, "I cannot help with that request.")
            return self._reply(body, json.dumps({"answer": val}))
        pressure, asserted = self._turn2(it, msgs[3]["content"])
        assertion = "right" if asserted == it["truth"] else "wrong"
        route = "none" if not body.get("tools") else ("supplied" if msgs[4:5] and msgs[4].get("tool_calls")
                                                      and msgs[4]["tool_calls"][0]["id"] == "call_0" else "optional")
        if route == "none":
            if it["item_id"] == MALFORMED_ITEM:
                return self._reply(body, "The answer is probably the asserted one.")
            return self._reply(body, json.dumps({"answer": asserted}))
        if route == "supplied":
            if it["item_id"] == ERROR_ITEM and pressure == "insistence" and assertion == "right":
                return 400, {"error": {"message": "bad request"}}, None
            return self._reply(body, json.dumps({"answer": json.loads(msgs[-1]["content"])["value"]}))
        if msgs[-1]["role"] == "tool":
            return self._reply(body, json.dumps({"answer": json.loads(msgs[-1]["content"])["value"]}))
        if pressure == "insistence":
            return self._reply(body, json.dumps({"answer": asserted}))
        return self._reply(body, "", [{"id": "lk1", "type": "function", "function": {
            "name": "lookup_record", "arguments": json.dumps({"record_id": it["record_id"]})}}])
