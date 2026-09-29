"""TASK-02 supplementary adjudication: resolve every PENDING candidate that already exists.

The rotation-invariant pHash audit (7 pairs) and the ART-004 embedding ranking (top 40 of
223,419 pairs, horizon fixed before any result) left 47 pairs PENDING_ADJUDICATION. SPEC
section 5 says a visual case without two passes blocks the grouping decision that depends
on it, so all 47 are adjudicated under the same blind A/B contract as the original audit.

The candidate set is split-independent: every pair is reviewed whatever split it would
fall in, so the review cannot be steered by the partition. Pairs below the horizons stay
unreviewed and are declared residual risk.

Consistency controls are pairs already adjudicated by two blind reviewers in the original
audit. They measure agreement with that record, not biological ground truth:
- positive: two pHash near-duplicates both reviewers called NEAR_DUPLICATE, and the
  same-fruit/different-photograph pair both reviewers identified (extra_relations.csv);
- negative: the pHash-band pair both reviewers called UNRELATED (a visually similar
  negative) and the first two two-member documentary families both called UNRELATED.
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import random  # noqa: E402

from src.evaluation.provenance import authorized_root, check_output  # noqa: E402
from src.leakage_audit.adjudication import render  # noqa: E402

AUDIT = ROOT / 'data/audits/model1'


def candidates(seed: int = 42) -> list[dict]:
    out = []
    for name, reason in (('rotation_candidates.csv', 'rotation-invariant pHash distance {}'),
                         ('embedding_candidates.csv', 'ART-004 embedding cosine {}')):
        for r in csv.DictReader(open(AUDIT / name, encoding='utf-8')):
            value = r.get('invariant_distance') or r.get('cosine')
            out.append({'category': name.split('_')[0], 'reason': reason.format(value),
                        'member_ids': sorted((r['source_id_a'], r['source_id_b']))})
    prior = sorted(csv.DictReader(open(AUDIT / 'adjudications.csv', encoding='utf-8')),
                   key=lambda r: r['candidate_id'])
    pairs = [r for r in prior if len(r['member_ids'].split(';')) == 2]

    def pick(category, decision, n):
        return [r for r in pairs if r['category'] == category
                and r['decision_a'] == r['decision_b'] == decision][:n]

    positives = pick('threshold_cross_split', 'NEAR_DUPLICATE', 2)
    negatives = pick('band_cross_split', 'UNRELATED', 1) + pick('documentary_family', 'UNRELATED', 2)
    for r in positives:
        out.append({'category': 'control_positive', 'member_ids': r['member_ids'].split(';'),
                    'reason': f"consistency: {r['candidate_id']} both NEAR_DUPLICATE"})
    extra = next(csv.DictReader(open(AUDIT / 'extra_relations.csv', encoding='utf-8')))
    out.append({'category': 'control_positive',
                'member_ids': sorted((extra['source_id_a'], extra['source_id_b'])),
                'reason': 'consistency: same fruit, different photograph, both reviewers'})
    for r in negatives:
        out.append({'category': 'control_negative', 'member_ids': r['member_ids'].split(';'),
                    'reason': f"consistency: {r['candidate_id']} both UNRELATED"})
    keys = [frozenset(c['member_ids']) for c in out]
    if len(set(keys)) != len(keys) or len(out) != 53:
        raise SystemExit(f'expected 53 distinct units, got {len(set(keys))} of {len(out)}')
    random.Random(seed).shuffle(out)  # the number must not encode the category
    for index, c in enumerate(out, start=1):
        c['candidate_id'] = f'SUPP-{index:03d}'
    return out


def main(packet_root: Path) -> int:
    root = authorized_root()
    legacy = Path(json.loads((root / 'configs/root_mapping.json').read_text(encoding='utf-8'))
                  ['legacy_corpus'])
    inventory = {r['source_id']: r for r in csv.DictReader(
        open(root / 'data/manifests/legacy_dataset_inventory.csv', encoding='utf-8-sig'))
        if r['dataset_id'] == 'DATA-001'}
    key_path = check_output(root, AUDIT / 'supplementary_key.json')
    render(candidates(), inventory, legacy, packet_root, key_path, seed=4242)
    print(json.dumps({'units': 53, 'key': str(key_path), 'packets': str(packet_root)}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(Path(sys.argv[1])))
