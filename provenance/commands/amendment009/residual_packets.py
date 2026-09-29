"""PROTOCOL-AMENDMENT-009: blind residual check for same-fruit relations hashes cannot see.

Pre-registered before any answer is seen:
- every test image of the option-B draft is a query, shown with its 5 nearest
  NON-test neighbours by the generic ImageNet embedding (ART-004);
- k=5 because the only known same-fruit/different-photo pair was the 5th
  neighbour of its query in the calibration;
- a neighbour flagged as the same fruit by AT LEAST ONE reviewer is merged with
  the query's group. This errs toward separation and cannot inflate results;
- controls: 2 positives built from the known same-fruit pair, 2 negatives.
"""

import csv
import hashlib
import json
import os
import random
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.evaluation.provenance import (  # noqa: E402
    authorized_root, check_output, configure_environment, lock_ultralytics, verify_environment,
)

K = 5
QUESTION = ('Panel 1 is the query. Does any of panels 2 to 6 show the SAME PHYSICAL FRUIT as '
            'panel 1, either the same photograph or a different photograph of that same fruit? '
            'Answer with the panel numbers, or an empty list if none.')


def sheet(paths, destination):
    from PIL import Image, ImageDraw
    tile = 240
    canvas = Image.new('RGB', (tile * len(paths), tile + 24), 'white')
    draw = ImageDraw.Draw(canvas)
    for i, path in enumerate(paths):
        with Image.open(path) as image:
            thumb = image.convert('RGB')
            thumb.thumbnail((tile, tile))
        canvas.paste(thumb, (i * tile + (tile - thumb.width) // 2, 24 + (tile - thumb.height) // 2))
        draw.text((i * tile + 6, 4), f'panel {i + 1}' + (' (query)' if i == 0 else ''), fill='black')
    canvas.save(destination, format='PNG')


def main(packet_root: Path) -> int:
    root = authorized_root()
    configure_environment(root)
    verify_environment(root)
    os.environ['YOLO_OFFLINE'] = 'true'
    import numpy as np
    from ultralytics import SETTINGS, YOLO
    lock_ultralytics(SETTINGS, root)
    legacy = Path(json.loads((root / 'configs/root_mapping.json').read_text(encoding='utf-8'))
                  ['legacy_corpus'])
    inventory = {r['source_id']: r for r in csv.DictReader(
        open(root / 'data/manifests/legacy_dataset_inventory.csv', encoding='utf-8-sig'))
        if r['dataset_id'] == 'DATA-001'}
    draft = {r['image_id']: r for r in csv.DictReader(
        open(root / 'data/manifests/model1_clean_manifest_B_draft.csv', encoding='utf-8'))}
    ids = sorted(inventory)
    cache = check_output(root, root / 'data/derived/embeddings_art004.npy')
    if cache.exists():
        matrix = np.load(cache)
    else:
        model = YOLO(str(root / 'provenance/runtime_state/models/yolo11n-cls.pt'))
        matrix = np.stack([model.embed(str(legacy / inventory[s]['relative_path']), verbose=False)[0]
                           .cpu().numpy().ravel() for s in ids]).astype('float64')
        matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)
        cache.parent.mkdir(parents=True, exist_ok=True)
        np.save(cache, matrix)
    index = {s: i for i, s in enumerate(ids)}
    similarity = matrix @ matrix.T

    queries = []
    for sid in ids:
        if draft[sid]['proposed_split'] != 'test':
            continue
        order = np.argsort(-similarity[index[sid]])
        neighbours = [ids[j] for j in order if ids[j] != sid
                      and draft[ids[j]]['proposed_split'] != 'test'][:K]
        queries.append({'kind': 'residual_query', 'query': sid, 'neighbours': neighbours})

    rng = random.Random(2026)
    pool = [s for s in ids if draft[s]['proposed_split'] != 'test']
    known_a, known_b = 'SRC-010049', 'SRC-010072'
    for _ in range(2):
        others = rng.sample([s for s in pool if s not in (known_a, known_b)], K - 1)
        slot = rng.randrange(K)
        queries.append({'kind': 'control_positive', 'query': known_a,
                        'neighbours': others[:slot] + [known_b] + others[slot:]})
    for _ in range(2):
        picks = rng.sample(pool, K + 1)
        queries.append({'kind': 'control_negative', 'query': picks[0], 'neighbours': picks[1:]})

    key = {'k': K, 'rule': 'merge if at least one reviewer flags a neighbour', 'reviewers': {}}
    for reviewer, seed in (('a', 11), ('b', 12)):
        order = list(queries)
        random.Random(seed).shuffle(order)
        directory = packet_root / reviewer
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True)
        questions, mapping = [], {}
        for position, item in enumerate(order, 1):
            qid = 'Q-' + hashlib.sha256(
                f"{reviewer}|{item['kind']}|{item['query']}|{position}".encode()).hexdigest()[:10]
            members = [item['query']] + item['neighbours']
            sheet([legacy / inventory[m]['relative_path'] for m in members], directory / f'{qid}.png')
            questions.append({'question_id': qid, 'position': position, 'sheet': f'{qid}.png',
                              'panels': len(members), 'kind': 'query', 'question': QUESTION})
            mapping[qid] = {'kind': item['kind'], 'query': item['query'],
                            'panel_members': members}
        (directory / 'questions.json').write_text(json.dumps({
            'reviewer': reviewer.upper(),
            'instructions': ('Judge only what you see. For every question, list the panel numbers '
                             '(2 to 6) that show the same physical fruit as panel 1, or an empty '
                             'list. Give a one-sentence rationale and a confidence of low, medium '
                             'or high.'),
            'questions': questions}, indent=2), encoding='utf-8')
        key['reviewers'][reviewer] = mapping
    check_output(root, root / 'data/audits/model1/residual_key.json').write_text(
        json.dumps(key, indent=2), encoding='utf-8')
    print(json.dumps({'queries': len(queries),
                      'test_queries': sum(q['kind'] == 'residual_query' for q in queries),
                      'controls': 4}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(Path(sys.argv[1])))
