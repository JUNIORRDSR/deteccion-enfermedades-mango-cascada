"""PROTOCOL-AMENDMENT-009: find rotated or mirrored copies that plain pHash misses."""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.evaluation.provenance import (  # noqa: E402
    authorized_root, check_output, configure_environment, verify_environment,
)
from src.leakage_audit.audit import (  # noqa: E402
    dihedral_hashes, hamming, rotation_invariant_distance,
)

HAMMING_LT, CANDIDATE_MAX = 5, 10


def main() -> int:
    root = authorized_root()
    configure_environment(root)
    verify_environment(root)
    from PIL import Image
    legacy = Path(json.loads((root / 'configs/root_mapping.json').read_text(encoding='utf-8'))
                  ['legacy_corpus'])
    inventory = [r for r in csv.DictReader(open(root / 'data/manifests/legacy_dataset_inventory.csv',
                                                encoding='utf-8-sig'))
                 if r['dataset_id'] == 'DATA-001']
    hashes = {}
    for row in inventory:
        with Image.open(legacy / row['relative_path']) as image:
            hashes[row['source_id']] = dihedral_hashes(image)
    meta = {r['source_id']: r for r in inventory}
    ids = sorted(hashes)
    found = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            plain = hamming(hashes[a][0], hashes[b][0])
            invariant = rotation_invariant_distance(hashes[a], hashes[b])
            # Only what plain pHash did NOT already surface as a candidate.
            if invariant <= CANDIDATE_MAX and plain > CANDIDATE_MAX:
                found.append({
                    'source_id_a': a, 'source_id_b': b,
                    'plain_distance': plain, 'invariant_distance': invariant,
                    'split_a': meta[a]['split'], 'split_b': meta[b]['split'],
                    'cross_split': str(meta[a]['split'] != meta[b]['split']).lower(),
                    'in_threshold': str(invariant < HAMMING_LT).lower(),
                    'review_decision': 'PENDING_ADJUDICATION'})
    out = check_output(root, root / 'data/audits/model1/rotation_candidates.csv')
    fields = ['source_id_a', 'source_id_b', 'plain_distance', 'invariant_distance', 'split_a',
              'split_b', 'cross_split', 'in_threshold', 'review_decision']
    with out.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(found)
    summary = {
        'images': len(ids), 'transforms_per_image': 8,
        'new_candidates_missed_by_plain_phash': len(found),
        'of_which_invariant_below_threshold': sum(f['in_threshold'] == 'true' for f in found),
        'of_which_cross_split': sum(f['cross_split'] == 'true' for f in found),
        'of_which_touch_test': sum('test' in (f['split_a'], f['split_b']) for f in found),
    }
    check_output(root, root / 'data/audits/model1/rotation_audit_summary.json').write_text(
        json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
