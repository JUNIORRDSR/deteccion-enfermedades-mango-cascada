"""PROTOCOL-AMENDMENT-009: candidate generator for same-fruit, different-photograph relations.

Both blind reviewers found two montage frames showing the same fruit in two
different photographs. That relation is invisible to any perceptual hash, even a
rotation-invariant one (plain 30, invariant 26). This generator ranks every pair
by cosine similarity of a GENERIC ImageNet embedding (ART-004, never trained on
these images) and proposes the top pairs for blind visual adjudication.

It proposes; it never decides. The review horizon N is fixed here, before any
result is seen: 40 pairs. Pairs below the horizon are unreviewed and declared as
residual risk.
"""

import csv
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.evaluation.provenance import (  # noqa: E402
    authorized_root, check_output, configure_environment, lock_ultralytics, verify_environment,
)

HORIZON = 40
ART004_SHA256 = 'c62d41bf9625777760018bf914d2e6cd472420ccd01706d97a61cb6c82502bd7'
RELATED = {'NEAR_DUPLICATE', 'POSSIBLE_SEQUENCE_RELATION'}


def known_relations(audit: Path) -> set[frozenset]:
    known = set()
    for row in csv.DictReader(open(audit / 'candidate_pairs.csv', encoding='utf-8')):
        if row['in_threshold'] == 'true':
            known.add(frozenset((row['source_id_a'], row['source_id_b'])))
    finals = {r['candidate_id']: r['final_adjudication']
              for r in csv.DictReader(open(audit / 'adjudications.csv', encoding='utf-8'))}
    for r in csv.DictReader(open(audit / 'adjudication_resolution.csv', encoding='utf-8')):
        if r.get('final'):
            finals[r['candidate_id']] = r['final']
    for r in csv.DictReader(open(audit / 'adjudications.csv', encoding='utf-8')):
        members = [m for m in r['member_ids'].split(';') if m]
        if finals[r['candidate_id']] in RELATED and r['unit_type'] == 'pair':
            known.add(frozenset(members))
    return known


def main() -> int:
    root = authorized_root()
    configure_environment(root)
    verify_environment(root)
    os.environ['YOLO_OFFLINE'] = 'true'
    legacy = Path(json.loads((root / 'configs/root_mapping.json').read_text(encoding='utf-8'))
                  ['legacy_corpus'])
    weights = check_output(root, root / 'provenance/runtime_state/models/yolo11n-cls.pt')
    weights.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(legacy / 'Mango-vision/yolo11n-cls.pt', weights)
    digest = hashlib.sha256(weights.read_bytes()).hexdigest()
    if digest != ART004_SHA256:
        raise SystemExit(f'ART-004 digest mismatch: {digest}')

    import numpy as np
    from ultralytics import SETTINGS, YOLO
    lock_ultralytics(SETTINGS, root)
    model = YOLO(str(weights))
    inventory = [r for r in csv.DictReader(open(root / 'data/manifests/legacy_dataset_inventory.csv',
                                                encoding='utf-8-sig')) if r['dataset_id'] == 'DATA-001']
    ids = [r['source_id'] for r in inventory]
    vectors = []
    for row in inventory:
        embedding = model.embed(str(legacy / row['relative_path']), verbose=False)[0]
        vectors.append(embedding.cpu().numpy().ravel())
    matrix = np.stack(vectors).astype('float64')
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)
    similarity = matrix @ matrix.T

    known = known_relations(root / 'data/audits/model1')
    meta = {r['source_id']: r for r in inventory}
    ranked = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            pair = frozenset((ids[i], ids[j]))
            if pair in known or meta[ids[i]]['sha256'] == meta[ids[j]]['sha256']:
                continue
            ranked.append((float(similarity[i, j]), ids[i], ids[j]))
    ranked.sort(key=lambda item: (-item[0], item[1], item[2]))
    chosen = ranked[:HORIZON]
    out = check_output(root, root / 'data/audits/model1/embedding_candidates.csv')
    with out.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream, lineterminator='\n')
        writer.writerow(['rank', 'cosine', 'source_id_a', 'source_id_b', 'split_a', 'split_b',
                         'review_decision'])
        for rank, (value, a, b) in enumerate(chosen, 1):
            writer.writerow([rank, f'{value:.6f}', a, b, meta[a]['split'], meta[b]['split'],
                             'PENDING_ADJUDICATION'])
    summary = {'embedding_model': 'ART-004 yolo11n-cls ImageNet base, sha256 ' + digest,
               'images': len(ids), 'pairs_ranked': len(ranked), 'horizon': HORIZON,
               'cosine_at_rank_1': round(chosen[0][0], 4),
               'cosine_at_horizon': round(chosen[-1][0], 4),
               'residual': ('pairs below the horizon are not visually reviewed; their relations, '
                            'if any, are declared residual risk')}
    check_output(root, root / 'data/audits/model1/embedding_summary.json').write_text(
        json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
