import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import harness_v2 as h
from budget import BudgetError

class Revision2Tests(unittest.TestCase):
    def setUp(self):
        self.data=h.generate(n=8)
        self.a=next(r for r in self.data['trials'] if r['project']=='P1' and r['route']=='optional')
        self.b=next(r for r in self.data['trials'] if r['project']=='P2')

    def test_09_identical_system_tool_and_matched_pressure_length(self):
        systems=[];lengths=[]
        for pressure in h.PRESSURES:
            for route in h.ROUTES:
                r=dict(self.a,route=route,pressure=pressure)
                systems.append(h.initial_messages(r)[0]);lengths.append(len(h.challenge(r)))
        self.assertTrue(all(s==systems[0] for s in systems));self.assertEqual(len(set(lengths)),1)
        self.assertNotIn('use tools',h.SYSTEM.lower());self.assertNotIn('when unsure',h.TOOL['function']['description'])

    def test_10_native_tool_pair_exactly_matches(self):
        cache={};opt=h.execute(dict(self.a,route='optional'),h.Mock(),cache)
        supplied=h.execute(dict(self.a,route='supplied'),h.Mock(),cache)
        o=opt['trace'][-1]['request']['messages'][-2:]
        s=supplied['trace'][-1]['request']['messages'][-2:]
        self.assertEqual(o,s);self.assertEqual(o[1]['role'],'tool')

    def test_initial_answer_is_model_generated_and_cached(self):
        model=h.Mock();cache={}
        first=h.execute(self.a,model,cache)
        second=h.execute(dict(self.a,route='supplied',pressure='authority'),model,cache)
        self.assertEqual(first['initial_answer'],second['initial_answer'])
        self.assertEqual(len(cache),1)
        self.assertFalse(any(t['stage']=='initial' for t in second['trace']))

    def test_14_wrong_id_checked_not_relevant(self):
        class WrongID(h.Mock):
            def complete(self,messages,tools,choice,row,stage):
                if stage=='optional_decision':return h.tool_pair(row,'wrong')[0],{'fixture':True}
                return super().complete(messages,tools,choice,row,stage)
        result=h.execute(self.a,WrongID(),{})
        self.assertEqual(result['metrics']['checked'],1);self.assertEqual(result['metrics']['relevant'],0)
        self.assertIn('record_not_found',result['trace'][-1]['request']['messages'][-1]['content'])

    def test_15_grader_blind_to_metadata(self):
        result=h.execute(self.b,h.Mock(),{})
        packet=result['grader_packet'];self.assertEqual(set(packet),{'response','claim_table'})
        self.assertNotIn('arm',packet);self.assertNotIn('verification_block',packet)
        self.assertTrue(all(set(x)=={'claim_id','claim','evidence_level','facility','status'} for x in packet['claim_table']))

    def test_16_family_enforcement_and_confirmatory_block(self):
        h.validate_dataset(self.data,'dev')
        with self.assertRaises(ValueError):h.validate_dataset(self.data,'holdout')
        wrong=copy.deepcopy(self.data)
        target=next(x for x in wrong['trials'] if x['split']=='dev');target['split']='holdout'
        wrong['trials_sha256']=h.sha(wrong['trials'])
        with self.assertRaises(ValueError):h.validate_dataset(wrong,'dev')

    def test_17_repeats_do_not_increase_independent_items(self):
        r1={'trial':{'item_id':'item1','arm':'B'},'metrics':{'error':1}}
        r2={'trial':{'item_id':'item1','arm':'A'},'metrics':{'error':0}}
        one=h.contrast([r1,r2],'error',lambda r:r['arm']=='B',lambda r:r['arm']=='A')
        repeated=h.contrast([copy.deepcopy(r) for _ in range(5) for r in [r1,r2]],'error',lambda r:r['arm']=='B',lambda r:r['arm']=='A')
        self.assertEqual(one,repeated);self.assertEqual(repeated['scheduled_items'],1)

    def test_18_real_analysis_rejects_mock_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'simulated'/'test';h.run(self.data,path,h.Mock())
            with self.assertRaises(ValueError):h.analyze(path,'real')
            self.assertEqual(h.analyze(path,'simulated')['kind'],'simulated')
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):h.run(self.data,Path(tmp)/'real'/'test',h.Mock())

    def test_11_12_13_itt_floor_secondary(self):
        class NeverChecks(h.Mock):
            def complete(self,messages,tools,choice,row,stage):
                if stage=='optional_decision':return {'role':'assistant','content':h.canon({'answer':row['assertion']})},{'fixture':True}
                return super().complete(messages,tools,choice,row,stage)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'simulated'/'test';h.run(self.data,path,NeverChecks())
            report=h.analyze(path,'simulated')
        self.assertEqual(report['pilot_gates']['neutral_acquisition_floor']['mean'],0)
        self.assertEqual(report['pilot_gates']['neutral_acquisition_floor']['decision'],'revise_task_fresh_pilot')
        self.assertEqual(report['primary']['P1_insistence-optional-correct']['scheduled_items'],6)
        self.assertEqual(report['primary']['P1_insistence-optional-correct']['complete_items'],6)
        self.assertIn('P1_supplied_insistence-adoption-user_correct=False',report['secondary'])
        self.assertIn('P1_supplied_insistence-user_correctness_interaction',report['secondary'])

    def test_12_wrong_id_floor_is_not_false_pass(self):
        class WrongID(h.Mock):
            def complete(self,messages,tools,choice,row,stage):
                if stage=='optional_decision':return h.tool_pair(row,'wrong')[0],{'fixture':True}
                return super().complete(messages,tools,choice,row,stage)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'simulated'/'test';h.run(self.data,path,WrongID())
            gate=h.analyze(path,'simulated')['pilot_gates']['neutral_acquisition_floor']
            self.assertEqual(gate['mean'],1)
            self.assertEqual(gate['relevant']['mean'],0)
            self.assertEqual(gate['decision'],'revise_lookup_measurement_fresh_pilot')

    def test_08_required_estimands(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'simulated'/'test';h.run(self.data,path,h.Mock());r=h.analyze(path,'simulated')
        for x in ['P2_attribution_B-A','P2_attribution_B-D1','P2_attribution_C-B','P2_E_correct_endorsement','P2_E_correct_refutation']:
            self.assertIn(x,r['primary'])
        self.assertIn('P2_attribution_C_prime-C',r['secondary'])

    def config(self,tmp,cap):
        return dict(endpoint='https://example.invalid/v1/chat/completions',model='test',provider='mocked-http',cap_usd=cap,
                    input_usd_per_million='1',output_usd_per_million='1',ledger_path=str(Path(tmp)/'shared.sqlite'),
                    input_token_upper_bound=10000,max_completion_tokens=128,pricing_reference='test-only arbitrary rates',allow_live=True)

    def test_19_cap_required_and_preflight_refusal(self):
        with self.assertRaises(ValueError):h.HTTPModel({})
        with tempfile.TemporaryDirectory() as tmp:
            adapter=h.HTTPModel(self.config(tmp,'.00001'))
            with patch('urllib.request.urlopen') as network:
                with self.assertRaises(BudgetError):adapter.complete([],[],'none',self.a,'test')
                network.assert_not_called()

    def test_19_run_halts_not_skips(self):
        class Exhausts(h.Mock):
            def complete(self,*args):raise BudgetError('fixture budget exhausted')
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'simulated'/'test';status=h.run(self.data,path,Exhausts())
            self.assertEqual(status,'halted_budget')
            lines=(path/'results.jsonl').read_text().splitlines();self.assertEqual(len(lines),1)
            report=h.analyze(path,'simulated');self.assertEqual(report['status_counts']['not_completed'],report['scheduled']-1)

    def test_19_actual_usage_and_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            config=self.config(tmp,'1');adapter=h.HTTPModel(config)
            body={'usage':{'prompt_tokens':100,'completion_tokens':10},'choices':[{'message':{'role':'assistant','content':'{"answer":"amber"}'}}]}
            with patch('urllib.request.urlopen') as call:
                call.return_value.__enter__.return_value.read.return_value=json.dumps(body).encode()
                adapter.complete([],[],'none',self.a,'test')
            spent=adapter.ledger.snapshot()['spent_nanos'];self.assertEqual(spent,110000)
            self.assertEqual(h.HTTPModel(config).ledger.snapshot()['spent_nanos'],spent)

    def test_19_unknown_usage_stops_and_keeps_reservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            adapter=h.HTTPModel(self.config(tmp,'1'))
            with patch('urllib.request.urlopen') as call:
                call.return_value.__enter__.return_value.read.return_value=b'{"choices":[]}'
                with self.assertRaises(BudgetError):adapter.complete([],[],'none',self.a,'test')
            state=adapter.ledger.snapshot();self.assertGreater(state['reserved_nanos'],0);self.assertTrue(state['blocked'])

if __name__=='__main__':unittest.main()
