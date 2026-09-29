"""Apply the PRE-REGISTERED residual rule of PROTOCOL-AMENDMENT-009, unchanged.

Rule written before any answer was seen: a neighbour flagged as the same fruit by
AT LEAST ONE reviewer is merged with its query; the partition is recomputed ONCE.
Test members that appear only after that single recomputation are not re-checked
and are declared residual. The rule is applied as written even if its outcome is
unwelcome, including a BLOCKED partition.
"""

import collections
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main(packet_root: Path) -> int:
    key = json.loads((ROOT / 'data/audits/model1/residual_key.json').read_text(encoding='utf-8'))
    answers = {r: json.loads((packet_root / r / 'answers.json').read_text(encoding='utf-8'))['answers']
               for r in ('a', 'b')}
    for r in ('a', 'b'):
        if set(answers[r]) != set(key['reviewers'][r]):
            raise SystemExit(f'reviewer {r} did not answer every question')

    calibration, flags = {}, collections.defaultdict(dict)
    for r in ('a', 'b'):
        ok = []
        for qid, meta in key['reviewers'][r].items():
            got = answers[r][qid]['same_fruit_panels']
            members = meta['panel_members']
            if meta['kind'] == 'control_positive':
                ok.append(members.index('SRC-010072') + 1 in got)
            elif meta['kind'] == 'control_negative':
                ok.append(got == [])
            else:
                flags[meta['query']][r] = {members[p - 1] for p in got if 2 <= p <= len(members)}
        calibration[r] = {'controls_correct': sum(ok), 'controls_total': len(ok)}

    relations, agreement = [], collections.Counter()
    for query, by in sorted(flags.items()):
        a, b = by.get('a', set()), by.get('b', set())
        agreement['both_none'] += not a and not b
        agreement['query_flagged_by_both'] += bool(a) and bool(b)
        agreement['query_flagged_only_a'] += bool(a) and not b
        agreement['query_flagged_only_b'] += bool(b) and not a
        for neighbour in sorted(a | b):
            who = 'A+B' if neighbour in a and neighbour in b else ('A' if neighbour in a else 'B')
            relations.append({'source_id_a': query, 'source_id_b': neighbour,
                              'final': 'POSSIBLE_SEQUENCE_RELATION',
                              'evidence': f'residual blind check, flagged by {who}'})
    agreement['neighbour_pairs_flagged_by_both'] = sum(r['evidence'].endswith('A+B') for r in relations)
    agreement['neighbour_pairs_flagged_by_one'] = sum(not r['evidence'].endswith('A+B') for r in relations)

    base = list(csv.DictReader(open(ROOT / 'data/audits/model1/extra_relations.csv', encoding='utf-8')))
    out = ROOT / 'data/audits/model1/extra_relations_with_residual.csv'
    with out.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['source_id_a', 'source_id_b', 'final', 'evidence'],
                                lineterminator='\n')
        writer.writeheader()
        writer.writerows(base + relations)

    split = subprocess.run(
        [sys.executable, '-m', 'src.leakage_audit.split', '--audit', 'data/audits/model1',
         '--seed', '42', '--ratios', '0.70', '0.15', '0.15', '--group-montage-by-identity',
         '--extra-relations', str(out.relative_to(ROOT)),
         '--out', 'data/manifests/model1_clean_manifest_B.csv',
         '--proposal', 'reports/model1_split_proposal_B.md'],
        capture_output=True, text=True, cwd=ROOT)
    summary = {'rule': key['rule'], 'calibration': calibration, 'agreement': dict(agreement),
               'relations_added': len(relations), 'split_exit_code': split.returncode,
               'split_stdout': split.stdout[-4000:], 'split_stderr': split.stderr[-1500:]}
    (ROOT / 'data/audits/model1/residual_outcome.json').write_text(
        json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in summary.items() if not k.startswith('split_std')}, indent=2))
    print(split.stdout[-2500:] or split.stderr[-1500:])
    return 0


if __name__ == '__main__':
    raise SystemExit(main(Path(sys.argv[1])))
