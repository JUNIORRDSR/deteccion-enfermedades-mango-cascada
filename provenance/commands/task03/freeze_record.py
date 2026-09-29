"""Write the TASK-03 freeze record: the root of trust the Kaggle renderer checks (round-5 H-02).

It fixes the final manifest path and hash, the hash of every audit input and of the split
code, the exact command and the counts. It is committed; the renderer refuses a manifest
whose path or hash differ from this record, or a record that is not committed and clean.
"""

import csv
import datetime
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = 'data/manifests/model1_clean_manifest.csv'
INPUTS = ('data/audits/model1/adjudications.csv', 'data/audits/model1/adjudication_resolution.csv',
          'data/audits/model1/clusters.csv', 'data/audits/model1/extra_relations.csv',
          'data/audits/model1/supplementary_adjudications.csv',
          'data/audits/model1/supplementary_resolution.csv',
          'data/audits/model1/supplementary_relations.csv',
          'data/manifests/legacy_dataset_inventory.csv', 'src/leakage_audit/split.py')
COMMAND = ('python -m src.leakage_audit.split --audit data/audits/model1 --seed 42 --ratios '
           '0.70 0.15 0.15 --extra-relations data/audits/model1/supplementary_relations.csv '
           f'--out {MANIFEST} --proposal reports/model1_split_proposal.md')


def sha(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    declared = (ROOT / (MANIFEST + '.sha256')).read_text(encoding='ascii').split()[0]
    if sha(MANIFEST) != declared:
        raise SystemExit('manifest differs from its sidecar')
    rows = list(csv.DictReader(open(ROOT / MANIFEST, encoding='utf-8')))
    counts = {}
    for split in ('train', 'valid', 'test'):
        members = [r for r in rows if r['proposed_split'] == split]
        counts[split] = {'images': len(members), 'groups': len({r['group_id'] for r in members})}
    record = {'task': 'TASK-03', 'status': 'FROZEN_PENDING_INDEPENDENT_REVIEW',
              'manifest_path': MANIFEST, 'manifest_sha256': declared,
              'grouping_rule': 'SPEC section 5 frozen rule: the sakit_mp4 montage is one group '
                               '(option A); PROTOCOL-AMENDMENT-009 withdrawn (DECISION-032)',
              'inputs': {p: sha(p) for p in INPUTS if (ROOT / p).is_file()},
              'missing_inputs': [p for p in INPUTS if not (ROOT / p).is_file()],
              'command': COMMAND, 'counts': counts,
              'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (ROOT / 'data/manifests/model1_clean_manifest.freeze.json').write_text(
        json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
