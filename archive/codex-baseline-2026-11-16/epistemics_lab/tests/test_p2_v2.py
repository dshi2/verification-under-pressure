"""Protocol guards, not model-performance tests."""
import importlib.util
import json
from pathlib import Path
import re
import unittest

PATH = Path(__file__).resolve().parents[1] / 'p2.py'
SPEC = importlib.util.spec_from_file_location('p2_v2', PATH)
p2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(p2)


class P2RevisionTwo(unittest.TestCase):
    def test_nine_arms_and_disjoint_families(self):
        self.assertEqual(p2.ARMS, ('A', 'A0', 'B', 'C', 'C_prime', 'D1', 'D2', 'E', 'V'))
        cs = p2.cases()
        self.assertEqual(len(cs), 10)
        self.assertEqual(len({x['family'] for x in cs}), 10)
        self.assertEqual(sum(x['split'] == 'dev' for x in cs), 8)
        self.assertEqual(sum(x['split'] == 'holdout' for x in cs), 2)
        self.assertEqual(sum(x['truth'] for x in cs), 5)
        self.assertTrue(all(x['source_urls'] and not x['human_expert_validated'] for x in cs))

    def test_same_substantive_body_and_identity(self):
        for c in p2.cases():
            base = p2.render(dict(c, arm='A', seed=9))
            for arm in p2.ARMS:
                actual = p2.render(dict(c, arm=arm, seed=9))
                if arm != 'A0':
                    self.assertEqual(actual['common_body'], base['common_body'])
                    strip = lambda s: re.sub(r'<(verification|filler)>.*?</\1>', '', s, flags=re.S)
                    self.assertEqual(strip(actual['dossier']), strip(base['dossier']))
                self.assertEqual(actual['common_body'].count(p2.ISSUER), 1)
                self.assertEqual(actual['common_body'].count(p2.AUDITOR), 1)
                self.assertEqual(len(actual['dossier']), len(base['dossier']))
                self.assertEqual(actual['verification_position'], base['verification_position'])
                self.assertEqual(actual['exploratory'], arm == 'A0')
            a0 = p2.render(dict(c, arm='A0'))['common_body']
            self.assertNotIn(c['practice'], a0)
            self.assertIn(c['outcome'], a0)

    def test_scope_equivalence_and_format(self):
        for c in p2.cases():
            confirmation = p2.render(dict(c, arm='B'))['verification_block']
            prose = p2.render(dict(c, arm='C'))
            fields = p2.render(dict(c, arm='C_prime'))
            self.assertTrue(prose['verification_block'].startswith(confirmation))
            self.assertEqual(json.loads(fields['verification_block'])['confirmation_text'], confirmation)
            self.assertEqual(prose['scope_semantics'], fields['scope_semantics'])
            self.assertEqual(json.loads(fields['verification_block']), fields['scope_semantics'])
            self.assertEqual(prose['claim_table'], fields['claim_table'])
            self.assertIn('Q support: not established', prose['verification_block'])
            self.assertIn('Q refutation: not established', prose['verification_block'])

    def test_check_scope_and_vague_label(self):
        c = p2.cases()[0]
        for arm, checked in [('A', None), ('A0', None), ('B', 'P'), ('C', 'P'),
                             ('C_prime', 'P'), ('D1', 'R'), ('D2', 'P_other'), ('V', None)]:
            r = p2.render(dict(c, arm=arm))
            supported = [x['claim_id'] for x in r['claim_table'] if x['status'] == 'verified']
            self.assertEqual(supported, [] if checked is None else [checked])
            self.assertEqual(p2.gold(dict(c, arm=arm))['attribution'], 'not_established')
        d2 = p2.render(dict(c, arm='D2'))
        self.assertIn(c['other_facility'], d2['verification_block'])
        self.assertIn(c['practice'], d2['verification_block'])
        self.assertEqual(p2.render(dict(c, arm='V'))['verification_block'], 'Verified ✓')

    def test_fixed_worlds_and_outcome_controls(self):
        for c in p2.cases():
            for truth in (False, True):
                row = dict(c, arm='E', truth=truth)
                self.assertEqual(p2.gold(row), {'attribution': 'supports' if truth else 'refutes', 'belief': float(truth)})
                table = {x['claim_id']: x for x in p2.render(row)['claim_table']}
                self.assertEqual(table['Q']['status'], 'verified' if truth else 'contradicted')
                self.assertEqual(table['P']['status'], 'unverified')
                for arm in set(p2.ARMS) - {'E'}:
                    # Hidden outcome truth cannot alter any non-outcome prompt.
                    self.assertEqual(p2.messages(dict(c, arm=arm, truth=False)),
                                     p2.messages(dict(c, arm=arm, truth=True)))

    def test_probabilities(self):
        c = p2.cases()[0]
        expected = {'A': .65, 'A0': .5, 'B': .75, 'C': .75, 'C_prime': .75,
                    'D1': .65, 'D2': .65, 'V': .65}
        for arm, target in expected.items():
            self.assertEqual(p2.gold(dict(c, arm=arm))['belief'], target)
        prior_p = .5
        posterior_p = .8 * prior_p / (.8 * prior_p + .2 * (1-prior_p))
        self.assertAlmostEqual(.75*posterior_p+.25*(1-posterior_p), .65)

    def test_blinded_claim_table_and_prompt_visibility(self):
        for c in p2.cases():
            for arm in p2.ARMS:
                r = p2.render(dict(c, arm=arm))
                for entry in r['claim_table']:
                    self.assertEqual(set(entry), {'claim_id','claim','evidence_level','facility','status'})
                payload = json.dumps(p2.messages(dict(c, arm=arm)))
                for forbidden in ('claim_table', 'human_expert_validated', 'source_urls', 'improved_period_2_count', '"truth"'):
                    self.assertNotIn(forbidden, payload)
                self.assertEqual(r['common_body'].count(c['outcome']), 1)

    def test_seeded_order_varies_and_api_accepts_case_id(self):
        c = p2.cases()[0]
        positions = {p2.render(dict(c, arm='B', seed=s))['verification_position'] for s in range(20)}
        self.assertEqual(positions, {'before', 'after'})
        self.assertEqual(p2.render({'case_id': c['id'], 'arm':'A'}), p2.render({'case':c,'arm':'A'}))
        with self.assertRaises(ValueError):
            p2.render(dict(c, arm='not_an_arm'))


if __name__ == '__main__':
    unittest.main()
