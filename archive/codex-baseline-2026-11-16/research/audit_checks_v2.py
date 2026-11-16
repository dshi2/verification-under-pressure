#!/usr/bin/env python3
"""Independent revision-2 audit: offline only, no paid model calls.
Run from any directory: python3 outputs/research/audit_checks_v2.py
"""
import concurrent.futures
import copy
import itertools
import json
from pathlib import Path
import re
import statistics
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1] / 'epistemics_lab'
sys.path.insert(0, str(ROOT))
import harness_v2 as h
import p2
from budget import BudgetLedger, RateCard, BudgetError, BudgetExhausted, BudgetBlocked


class IndependentV2Audit(unittest.TestCase):
    def setUp(self):
        self.data = h.generate(n=8, repeats=2)
        self.a = next(r for r in self.data['trials'] if r['project']=='P1' and r['route']=='optional' and r['pressure']=='neutral')

    def test_01_05_content_diff_and_mutation(self):
        def content(dossier):
            return re.sub(r'<(verification|filler)>.*?</\1>', '', dossier, flags=re.S)
        for case in p2.cases():
            baseline = p2.render(dict(case, arm='A', seed=11))
            for arm in ('B', 'D1', 'D2'):
                rendered = p2.render(dict(case, arm=arm, seed=11))
                self.assertEqual(content(rendered['dossier']), content(baseline['dossier']))
                self.assertEqual(len(rendered['dossier']), len(baseline['dossier']))
            bad = copy.deepcopy(case)
            bad['practice'] += ' altered practice'
            self.assertNotEqual(content(p2.render(dict(bad, arm='B', seed=11))['dossier']), content(baseline['dossier']))

    def test_02_03_06_07_scope_labels_independently(self):
        for case in p2.cases():
            for arm, supported in [('A', []), ('A0', []), ('B', ['P']), ('C', ['P']), ('C_prime', ['P']), ('D1', ['R']), ('D2', ['P_other']), ('V', [])]:
                r = p2.render(dict(case, arm=arm))
                actual = [x['claim_id'] for x in r['claim_table'] if x['status']=='verified']
                self.assertEqual(actual, supported)
                self.assertIn(p2.ISSUER, r['common_body'])
                self.assertIn(p2.AUDITOR, r['common_body'])
                if arm=='A0':
                    self.assertNotIn(case['practice'], r['common_body'])
                    self.assertTrue(r['exploratory'])
            for truth in (False, True):
                r = p2.render(dict(case, arm='E', truth=truth))
                self.assertIn('supports Q' if truth else 'refutes Q', r['verification_block'])
                self.assertEqual(p2.gold(dict(case, arm='E', truth=truth))['belief'], int(truth))

    def test_04_scope_same_semantics(self):
        for case in p2.cases():
            prose = p2.render(dict(case, arm='C'))
            fields = p2.render(dict(case, arm='C_prime'))
            parsed = json.loads(fields['verification_block'])
            self.assertEqual(parsed, prose['scope_semantics'])
            narrow = p2.render(dict(case, arm='B'))['verification_block']
            self.assertTrue(prose['verification_block'].startswith(narrow))
            self.assertEqual(parsed['confirmation_text'], narrow)
            self.assertIn(case['facility'], prose['verification_block'])
            self.assertIn('Q support: not established', prose['verification_block'])
            self.assertIn('Q refutation: not established', prose['verification_block'])

    def test_09_10_native_pair_and_actual_initial_cache(self):
        class InitialUnknown(h.Mock):
            def complete(self, messages, tools, choice, row, stage):
                if stage=='initial':
                    self.calls += 1
                    return {'role':'assistant','content':'{"answer":"unknown"}'}, {'fixture':True}
                return super().complete(messages, tools, choice, row, stage)
        adapter = InitialUnknown(); cache = {}
        optional = h.execute(self.a, adapter, cache)
        supplied = h.execute(dict(self.a, route='supplied'), adapter, cache)
        self.assertEqual(optional['initial_answer'], {'answer':'unknown'})
        self.assertEqual(supplied['initial_answer'], optional['initial_answer'])
        self.assertFalse(any(t['stage']=='initial' for t in supplied['trace']))
        self.assertEqual(optional['trace'][-1]['request']['messages'][-2:], supplied['trace'][-1]['request']['messages'][-2:])
        self.assertEqual(optional['trace'][-1]['request']['tools'], supplied['trace'][-1]['request']['tools'])
        self.assertEqual(optional['trace'][-1]['request']['messages'][0], supplied['trace'][-1]['request']['messages'][0])

    def test_14_wrong_id_not_relevant(self):
        class Wrong(h.Mock):
            def complete(self,messages,tools,choice,row,stage):
                if stage=='optional_decision':
                    return h.tool_pair(row,'WRONG-RECORD')[0], {'fixture':True}
                return super().complete(messages,tools,choice,row,stage)
        r=h.execute(self.a,Wrong(),{})
        self.assertEqual(r['metrics']['checked'],1)
        self.assertEqual(r['metrics']['relevant'],0)
        source=ROOT/'simulated'/'rev2_oracle'
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'simulated'/'wrong_id_floor';target.mkdir(parents=True)
            (target/'manifest.json').write_text((source/'manifest.json').read_text())
            rows=[json.loads(s) for s in (source/'results.jsonl').read_text().splitlines()]
            for row in rows:
                trial=row['trial']
                if trial['project']=='P1' and trial['route']=='optional' and trial['pressure']=='neutral':
                    row['metrics'].update(checked=1,relevant=0)
            (target/'results.jsonl').write_text('\n'.join(json.dumps(x) for x in rows))
            self.assertEqual(h.analyze(target,'simulated')['pilot_gates']['neutral_acquisition_floor']['decision'],'revise_lookup_measurement_fresh_pilot')

    def test_15_blind_packet_and_hidden_truth(self):
        for case in p2.cases():
            for arm in p2.ARMS:
                row=dict(case,project='P2',arm=arm)
                r=h.execute(row,h.Mock(),{})
                self.assertEqual(set(r['grader_packet']),{'response','claim_table'})
                self.assertNotIn('arm',json.dumps(r['grader_packet']))
                self.assertNotIn('verification_block',json.dumps(r['grader_packet']))
                if arm!='E':
                    self.assertEqual(p2.messages(dict(row,truth=False)),p2.messages(dict(row,truth=True)))

    def test_16_family_holdout_is_blocked(self):
        h.validate_dataset(self.data,'dev')
        with self.assertRaises(ValueError):h.validate_dataset(self.data,'holdout')
        bad=copy.deepcopy(self.data)
        next(x for x in bad['trials'] if x['split']=='dev')['split']='holdout'
        bad['trials_sha256']=h.sha(bad['trials'])
        with self.assertRaises(ValueError):h.validate_dataset(bad,'dev')

    def test_17_missingness_bounds_exhaustive(self):
        rows=[{'trial':{'item_id':'i','side':side},'metrics':{} if x is None else {'x':x}} for side,x in [('l',1),('l',None),('r',0),('r',None)]]
        c=h.contrast(rows,'x',lambda r:r['side']=='l',lambda r:r['side']=='r',draws=50)
        all_d=[(1+a)/2-b/2 for a,b in itertools.product([0,1],repeat=2)]
        self.assertEqual(c['missing_bounds'],[min(all_d),max(all_d)])
        replicated=h.contrast(rows*3,'x',lambda r:r['side']=='l',lambda r:r['side']=='r',draws=50)
        self.assertEqual(c,replicated)

    def test_08_11_13_18_persisted_raw_arithmetic(self):
        for name in ('rev2_oracle','rev2_biased'):
            folder=ROOT/'simulated'/name
            self.assertTrue(folder.exists(), 'Published validation artifact missing')
            rows=[json.loads(s) for s in (folder/'results.jsonl').read_text().splitlines()]
            with self.assertRaises(ValueError):h.analyze(folder,'real')
            analysis=h.analyze(folder,'simulated')
            self.assertTrue(all(r['trial']['split']=='dev' for r in rows))
            self.assertEqual(analysis['scheduled'],len(rows))
            a=[r for r in rows if r['trial']['project']=='P1']
            def acc(route,pressure,user=None):
                subset=[r for r in a if r['trial']['route']==route and r['trial']['pressure']==pressure and (user is None or r['trial']['user_correct']==user)]
                return statistics.mean(json.loads(r['trace'][-1]['message']['content'])['answer']==r['trial']['truth'] for r in subset)
            for pressure in ('insistence','authority'):
                expected=(acc('supplied',pressure)-acc('supplied','neutral'))-(acc('optional',pressure)-acc('optional','neutral'))
                self.assertEqual(expected,analysis['primary'][f'P1_{pressure}-accuracy_interaction']['estimate'])
                for user in (False,True):
                    self.assertEqual(acc('supplied',pressure,user)-acc('supplied','neutral',user),analysis['secondary'][f'P1_supplied_{pressure}-adoption-user_correct={user}']['estimate'])
                full=(acc('supplied',pressure,True)-acc('supplied','neutral',True))-(acc('supplied',pressure,False)-acc('supplied','neutral',False))
                self.assertEqual(full,analysis['secondary'][f'P1_supplied_{pressure}-user_correctness_interaction']['estimate'])
            b=[r for r in rows if r['trial']['project']=='P2']
            def err(arm):
                results=[json.loads(r['trace'][-1]['message']['content']) for r in b if r['trial']['arm']==arm]
                return statistics.mean(x['attribution']!='not_established' or 'Q' in x['claims_verified'] for x in results)
            for l,r in [('B','A'),('B','D1'),('C','B')]:
                self.assertEqual(err(l)-err(r),analysis['primary'][f'P2_attribution_{l}-{r}']['estimate'])

    def test_19_ledger_concurrency_restart_exhaustion(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'shared.sqlite'; card=RateCard('fixture','fixture','1','1')
            BudgetLedger(path,'0.0000001',card)
            def attempt(_):
                ledger=BudgetLedger(path,'0.0000001',card)
                try:return ledger.reserve(11)
                except BudgetExhausted:return None
            with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
                results=list(pool.map(attempt,range(20)))
            accepted=[r for r in results if r]
            self.assertEqual(len(accepted),9)
            restarted=BudgetLedger(path,'0.0000001',card)
            self.assertEqual(restarted.snapshot()['reserved_nanos'],99)
            with self.assertRaises(BudgetExhausted):restarted.reserve(2)
            with self.assertRaises(BudgetBlocked):restarted.abandon(accepted[0])
            with self.assertRaises(BudgetBlocked):BudgetLedger(path,'0.0000001',card).reserve(1)

    def test_19_no_network_after_preflight_cap_failure(self):
        with tempfile.TemporaryDirectory() as t:
            config=dict(endpoint='https://example.invalid',model='fixture',provider='fixture',cap_usd='.000001',
                        input_usd_per_million='1',output_usd_per_million='1',ledger_path=str(Path(t)/'budget.sqlite'),
                        input_token_upper_bound=10000,max_completion_tokens=128,pricing_reference='audit fixture only',allow_live=True)
            adapter=h.HTTPModel(config)
            with patch('urllib.request.urlopen') as net:
                with self.assertRaises(BudgetError):adapter.complete([],[],'none',self.a,'initial')
                net.assert_not_called()


if __name__=='__main__':unittest.main(verbosity=2)
