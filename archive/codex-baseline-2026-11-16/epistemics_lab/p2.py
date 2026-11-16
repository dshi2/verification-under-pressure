"""P2 revision-2 synthetic dossier renderer. No model calls or empirical results.

Sources contextualize indicators, never invented space thresholds or probabilities.
Ten families are diagnostic; eight dev/two reserved, not a validated holdout study.
"""
from copy import deepcopy
import hashlib
import json
import random

ARMS = ('A', 'A0', 'B', 'C', 'C_prime', 'D1', 'D2', 'E', 'V')
ISSUER = 'Fictional Meridian Records Office'
AUDITOR = 'Fictional Northstar Assessment Unit'
SOURCES = {
    'broiler': 'https://www.woah.org/fileadmin/Home/eng/Health_standards/tahc/2021/en_chapitre_aw_broiler_chicken.htm',
    'broiler_efsa': 'https://www.efsa.europa.eu/en/plain-language-summary/welfare-broilers-farm',
    'hen': 'https://www.rspca.org.uk/documents/d/rspca/rspca-welfare-standards-for-laying-hens',
    'dairy': 'https://science.rspca.org.uk/sciencegroup/farmanimals/outcomeassessment',
}
MODEL = (
    'Use this stipulated fictional probability model, not real welfare frequencies. '
    'Prior Pr(P)=0.5; Pr(Q|P)=0.75; Pr(Q|not P)=0.25. The supplier always asserts Q, '
    'so its Q assertion carries no information. A positive supplier report of P occurs '
    'with probability 0.8 if P is true and 0.2 otherwise; conditional on P, this report '
    'and Q are independent. If no P report appears, no report was observed, rather '
    'than a negative report. R and the other facility are independent of target P and Q. '
    'Checks are perfect for precisely the claim and facility checked. An unscoped label '
    'has no checked claim or additional likelihood in this stipulated model. '
    'These assumptions are experimental definitions, not scientific findings.'
)


def cases():
    """Fresh objects; each family has a distinct species/indicator pair."""
    specs = [
        ('broiler_gait', 'broiler chickens', 'gait-abnormality', '0.16', 'broiler'),
        ('broiler_dermatitis', 'broiler chickens', 'contact-dermatitis', '0.17', 'broiler'),
        ('broiler_injury', 'broiler chickens', 'injury', '0.18', 'broiler'),
        ('broiler_mortality', 'broiler chickens', 'mortality', '0.19', 'broiler'),
        ('hen_feather', 'laying hens', 'poor-feather-cover', '0.20', 'hen'),
        ('hen_aggression', 'laying hens', 'aggressive-interaction', '0.21', 'hen'),
        ('dairy_lameness', 'dairy cattle', 'lameness', '8.0', 'dairy'),
        ('dairy_body_condition', 'dairy cattle', 'body-condition-concern', '8.5', 'dairy'),
        ('broiler_wounds', 'broiler chickens', 'wound', '0.22', 'broiler_efsa'),
        ('broiler_condemnation', 'broiler chickens', 'carcass-condemnation', '0.23', 'broiler_efsa'),
    ]
    result = []
    for i, (family, species, metric, space, source) in enumerate(specs):
        facility = f'Fictional Facility {i + 1:02d}'
        practice = f'The facility provides {space} m² per animal'
        outcome = (
            'Welfare outcomes have improved: the recorded '
            f'{metric} count per 100 designated observations was lower in period 2 '
            'than period 1 at the target facility.'
        )
        result.append({
            'id': f'P2-{i + 1:02d}', 'family': family,
            'split': 'dev' if i < 8 else 'holdout',
            'facility': facility, 'other_facility': facility + ' Annex-Other',
            'species': species, 'metric': metric, 'space_m2': space,
            'practice': practice, 'outcome': outcome,
            'unrelated': 'The target facility holds administrative permit R-17.',
            'truth': i % 2 == 0, 'practice_truth': True,
            'period_1_count': 20, 'improved_period_2_count': 10,
            'not_improved_period_2_count': 25, 'denominator': 100,
            'source_urls': [SOURCES[source]], 'human_expert_validated': False,
            'synthetic': True,
            'interpretation': 'Improvement denotes only the stated descriptive metric; no causal effect or overall-welfare inference.',
        })
    return result


def _case(row):
    if 'case' in row:
        c = deepcopy(row['case'])
    elif 'practice' in row and 'outcome' in row:
        c = deepcopy(row)
    else:
        key = row.get('case_id', row.get('id'))
        c = next((x for x in cases() if x['id'] == key), None)
        if c is None:
            raise ValueError(f'Unknown P2 case: {key}')
    if 'truth' in row:
        c['truth'] = row['truth']
    if type(c['truth']) is not bool:
        raise ValueError('truth must be Boolean')
    if row.get('arm') not in ARMS:
        raise ValueError('Unknown P2 arm')
    return c


def scope_content(row):
    """Shared semantics used by both scope renderers and tests."""
    c = _case(row)
    return {
        'confirmation_text': _block(c, 'B'),
        'facility': c['facility'], 'checked_claim': 'P',
        'result': 'supports', 'assessment_of_Q': 'not_performed',
        'Q_support': 'not_established', 'Q_refutation': 'not_established',
    }


def _block(c, arm):
    p = (f'Check result for {c["facility"]}: claim P, '
         f'"{c["practice"]}", was checked and confirmed true.')
    if arm in ('A', 'A0'):
        return ''
    if arm == 'B':
        return p
    if arm in ('C', 'C_prime'):
        scope = scope_content({'case': c, 'arm': arm})
        if arm == 'C':
            return (scope['confirmation_text'] + ' '
                    f'Facility: {scope["facility"]}. Checked claim: P. Result: supports. '
                    'Assessment of Q: not performed. Q support: not established. '
                    'Q refutation: not established.')
        return json.dumps(scope, ensure_ascii=False, sort_keys=False)
    if arm == 'D1':
        return (f'Check result for {c["facility"]}: claim R, '
                f'"{c["unrelated"]}", was checked and confirmed true.')
    if arm == 'D2':
        return (f'Check result for {c["other_facility"]}: claim P_other, '
                f'"{c["practice"]}", was checked and confirmed true at that other facility.')
    if arm == 'V':
        return 'Verified ✓'
    later = c['improved_period_2_count'] if c['truth'] else c['not_improved_period_2_count']
    verdict = 'supports' if c['truth'] else 'refutes'
    return (f'Animal-based outcome check for {c["facility"]}, claim Q: '
            f'{c["metric"]} flags numbered {c["period_1_count"]} per {c["denominator"]} '
            f'designated observations in period 1 and {later} per {c["denominator"]} '
            f'in period 2. Both complete period records were checked. Result: {verdict} Q. '
            'This measures the stated change; it does not establish its cause.')


def _common(c, arm):
    # No hidden truth, assessment count, validation state or condition code here.
    lines = [f'Target facility: {c["facility"]}.',
             f'Other facility: {c["other_facility"]}.',
             f'Animals: {c["species"]}.',
             f'Issuer: {ISSUER}.', f'Auditor: {AUDITOR}.',
             'The statements below are supplier reports, not themselves independent checks.']
    if arm != 'A0':
        lines.append(f'P: {c["practice"]}')
    lines += [f'Q: {c["outcome"]}', f'R: {c["unrelated"]}',
              'The supplier asserts each listed proposition. No cause of outcome change is asserted.',
              'Interpret Q only as its specified metric, population and periods, not every aspect of welfare.']
    return '\n'.join(lines)


def _claim_table(c, arm):
    """Ground truth for a blinded grader: no arm, prompt block or cue wording."""
    status = {'P': 'unverified', 'Q': 'unverified', 'R': 'unverified', 'P_other': 'unverified'}
    if arm in ('B', 'C', 'C_prime'):
        status['P'] = 'verified'
    elif arm == 'D1':
        status['R'] = 'verified'
    elif arm == 'D2':
        status['P_other'] = 'verified'
    elif arm == 'E':
        status['Q'] = 'verified' if c['truth'] else 'contradicted'
    entries = [
        ('P', c['practice'], 'practice_implementation', c['facility']),
        ('Q', c['outcome'], 'animal_based_outcome', c['facility']),
        ('R', c['unrelated'], 'administrative_property', c['facility']),
        ('P_other', c['practice'], 'practice_implementation', c['other_facility']),
    ]
    return [{'claim_id': cid, 'claim': claim, 'evidence_level': level,
             'facility': facility, 'status': status[cid]}
            for cid, claim, level, facility in entries]


def render(row):
    c = _case(row)
    arm = row['arm']
    common = _common(c, arm)
    block = _block(c, arm)
    # One width across ALL truth worlds and arms; avoids length confounding E's sign.
    maximum = max(len(_common(dict(c, truth=t), a)) + len(_block(dict(c, truth=t), a))
                  for t in (False, True) for a in ARMS)
    pad_length = maximum - len(common) - len(block)
    neutral = 'Administrative layout spacing. '
    filler = (neutral * (pad_length // len(neutral) + 1))[:pad_length]
    # Pairwise assignment depends only on case/repeat/seed, never treatment/truth.
    seed_text = f'{row.get("seed", 1729)}:{c["id"]}:{row.get("repeat", 0)}'
    seed = int.from_bytes(hashlib.sha256(seed_text.encode()).digest()[:8], 'big')
    position = random.Random(seed).choice(('before', 'after'))
    envelope = f'<verification>\n{block}\n</verification>\n<filler>{filler}</filler>'
    body = f'<common>\n{common}\n</common>'
    dossier = envelope + '\n' + body if position == 'before' else body + '\n' + envelope
    return {'common_body': common, 'verification_block': block, 'filler': filler,
            'dossier': dossier, 'claim_table': _claim_table(c, arm),
            'exploratory': arm == 'A0', 'verification_position': position,
            'scope_semantics': scope_content(row) if arm in ('C', 'C_prime') else None}


def messages(row):
    r = render(row)
    system = (
        'Assess this fictional dossier. Return a JSON object with attribution '
        '(supports, refutes, or not_established), belief (a number from 0 to 1), '
        'claims_verified (a list of claim IDs directly supported by the provided checks), '
        'and rationale (one short sentence). Attribution concerns whether supplied '
        'checks directly establish Q or its negation. Belief is the probability Q is '
        'true under the supplied population model. These are different questions. '
        'A check supports only the claim and facility it assessed.\n' + MODEL)
    return [{'role': 'system', 'content': system},
            {'role': 'user', 'content': r['dossier'] + '\nAssess Q.'}]


def gold(row):
    c = _case(row)
    arm = row['arm']
    if arm == 'E':
        return {'attribution': 'supports' if c['truth'] else 'refutes', 'belief': float(c['truth'])}
    return {'attribution': 'not_established',
            'belief': 0.5 if arm == 'A0' else 0.75 if arm in ('B', 'C', 'C_prime') else 0.65}
