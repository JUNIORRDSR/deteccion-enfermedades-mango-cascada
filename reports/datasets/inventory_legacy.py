"""Read-only structural inventory; reuse captured SHA256, never decode images/models.

Writes only this reports directory and the permitted legacy inventory CSV.
No dataset preparation, pHash, split assignment, training, or evaluation runs.
"""
import csv
import itertools
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'ALBUS26_major_revision/provenance/source_manifest.csv'
SOURCES = list(csv.DictReader(MANIFEST.open(encoding='utf-8-sig', newline='')))
BY_PATH = {r['relative_path'].replace('\\', '/'): r for r in SOURCES}
CLASSES = ['Saludable', 'Antracnosis', 'Cancro_bacteriano', 'Costras', 'Podredumbre_Extremo_tallo']
DATASETS = [
    ('DATA-001', 'SemilleroTI-Mangos/docs/MangosDataset', 'yolo', ['Enfermo', 'Saludable']),
    ('DATA-002', 'Mango-vision/MangoDHDS A Dataset of Diseased and Healthy Mangoe', 'raw_cls', []),
    ('DATA-003', 'Mango-vision/DatasetMango_YOLO', 'yolo', CLASSES),
    ('DATA-004', 'Mango-vision/DatasetMango_YOLO_clean', 'yolo', CLASSES),
    ('DATA-005', 'Mango-vision/DatasetMango_YOLO_cls', 'cls', CLASSES),
    ('DATA-006', 'Mango-vision/DatasetMango_Propias', 'yolo', ['mango']),
    ('DATA-007', 'Mango-vision/Datasets Sucios personal', 'personal', []),
    ('DATA-008', 'Mango-vision/DatasetMango_Detector', 'absent', ['mango']),
]
IMAGE_EXT = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}


def write_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


inventory = []
summary = []
issues = []
for dataset_id, prefix, kind, names in DATASETS:
    source_rows = [r for p, r in BY_PATH.items() if p.startswith(prefix + '/')]
    images = [r for r in source_rows if r['type'].lower() in IMAGE_EXT]
    label_sources = [r for r in source_rows if '/labels/' in r['relative_path'] and r['type'] == '.txt']
    summary.append({'dataset_id': dataset_id, 'root': prefix, 'exists': (ROOT / prefix).is_dir(),
                    'image_files': len(images), 'label_files': len(label_sources),
                    'all_files': len(source_rows), 'file_types': dict(Counter(r['type'] for r in source_rows))})
    used_labels = set()
    for source in images:
        relative = source['relative_path']
        sub = Path(relative).relative_to(prefix)
        split = sub.parts[0] if kind in {'yolo', 'cls'} else 'unsplit'
        label_path = ''
        label_source = {}
        ids = []
        class_names = []
        boxes = 0
        polygons = 0
        full_boxes = 0
        status = 'not_applicable'
        if kind == 'yolo':
            label_path = f'{prefix}/{split}/labels/{sub.stem}.txt'
            label_source = BY_PATH.get(label_path, {})
            status = 'missing' if not label_source else 'present'
            if label_source:
                used_labels.add(label_path)
                lines = (ROOT / label_path).read_text(encoding='utf-8-sig').splitlines()
                for line_number, line in enumerate(lines, 1):
                    if not line.strip():
                        continue
                    parts = line.split()
                    try:
                        assert len(parts) == 5 or (len(parts) >= 7 and len(parts) % 2 == 1), 'unrecognized YOLO geometry'
                        cls = int(parts[0])
                        assert 0 <= cls < len(names), 'class out of range'
                        coords = [float(x) for x in parts[1:]]
                        assert all(0 <= x <= 1 for x in coords), 'coordinate out of range'
                        if len(parts) == 5:
                            assert coords[2] > 0 and coords[3] > 0, 'non-positive size'
                        ids.append(cls)
                        class_names.append(names[cls])
                        boxes += len(parts) == 5
                        polygons += len(parts) > 5
                        full_boxes += coords == [0.5, 0.5, 1.0, 1.0]
                    except (AssertionError, ValueError) as exc:
                        issues.append({'dataset_id': dataset_id, 'path': label_path,
                                       'line': line_number, 'issue': str(exc)})
                if not ids:
                    status = 'empty_or_invalid'
        elif kind == 'cls':
            class_names = [sub.parts[1]]
            ids = [names.index(class_names[0])]
        elif kind == 'raw_cls':
            class_names = [sub.parts[1]]
        stem = sub.stem
        base = stem.split('.rf.')[0]
        base = re.sub(r'_(?:jpg|jpeg|png|JPG|JPEG|PNG)$', '', base)
        sequence = 'sakit_mp4' if re.match(r'^sakit_mp4-\d+', stem) else ''
        burst = re.match(r'^(IMG_\d+_\d+)_Burst\d+', stem)
        if burst:
            sequence = burst[1] + '_Burst'
        inventory.append({'dataset_id': dataset_id, 'split': split,
                          'class_ids': ';'.join(map(str, sorted(set(ids)))),
                          'class_names': ';'.join(sorted(set(class_names))),
                          'annotation_count': len(class_names), 'box_count': boxes,
                          'polygon_count': polygons, 'full_image_box_count': full_boxes,
                          'instance_classes': ';'.join(class_names),
                          'label_status': status, 'relative_path': relative,
                          'source_id': source['source_id'], 'sha256': source['sha256'],
                          'size_bytes': source['size_bytes'], 'label_path': label_path,
                          'label_source_id': label_source.get('source_id', ''),
                          'label_sha256': label_source.get('sha256', ''),
                          'filename': sub.name, 'normalized_filename_base': base,
                          'sequence_name_hint': sequence})
    for label in label_sources:
        if label['relative_path'] not in used_labels:
            issues.append({'dataset_id': dataset_id, 'path': label['relative_path'], 'line': '', 'issue': 'orphan label'})

write_csv(ROOT / 'ALBUS26_major_revision/data/manifests/legacy_dataset_inventory.csv', inventory)
write_csv(OUT / 'structural_issues.csv', issues, ['dataset_id', 'path', 'line', 'issue'])

counts = []
for dataset_id, prefix, kind, names in DATASETS:
    items = [r for r in inventory if r['dataset_id'] == dataset_id]
    for split in sorted({r['split'] for r in items}):
        samples = [r for r in items if r['split'] == split]
        for cls in ['ALL'] + sorted({c for r in samples for c in r['class_names'].split(';') if c}):
            selected = samples if cls == 'ALL' else [r for r in samples if cls in r['class_names'].split(';')]
            counts.append({'dataset_id': dataset_id, 'split': split, 'class': cls,
                           'image_files': len(selected), 'label_files': sum(r['label_status'] in {'present', 'empty_or_invalid'} for r in selected),
                           'instances': sum(r['annotation_count'] if cls == 'ALL' else r['instance_classes'].split(';').count(cls) for r in selected),
                           'box_rows': sum(r['box_count'] for r in selected),
                           'polygon_rows': sum(r['polygon_count'] for r in selected),
                           'full_image_boxes': sum(r['full_image_box_count'] for r in selected)})
write_csv(OUT / 'counts_by_split_class.csv', counts)

duplicate_rows = []
duplicate_summary = []
for dataset_id, prefix, kind, names in DATASETS:
    items = [r for r in inventory if r['dataset_id'] == dataset_id]
    hashes = defaultdict(list)
    for r in items:
        hashes[r['sha256']].append(r)
    groups = [group for group in hashes.values() if len(group) > 1]
    cross = 0
    split_pairs = Counter()
    for group in groups:
        for a, b in itertools.combinations(group, 2):
            is_cross = a['split'] != b['split']
            cross += is_cross
            if is_cross:
                split_pairs['|'.join(sorted([a['split'], b['split']]))] += 1
            duplicate_rows.append({'dataset_id': dataset_id, 'cross_split': is_cross,
                                   'sha256': a['sha256'], 'split_a': a['split'], 'split_b': b['split'],
                                   'source_a': a['source_id'], 'source_b': b['source_id'],
                                   'path_a': a['relative_path'], 'path_b': b['relative_path']})
    duplicate_summary.append({'dataset_id': dataset_id, 'unique_byte_hashes': len(hashes),
                              'duplicate_groups': len(groups), 'files_in_duplicate_groups': sum(map(len, groups)),
                              'cross_split_pairs': cross, 'cross_split_pair_counts': dict(split_pairs)})
write_csv(OUT / 'exact_duplicate_pairs_preliminary.csv', duplicate_rows)

base_rows = []
for dataset_id, prefix, kind, names in DATASETS:
    groups = defaultdict(list)
    for r in inventory:
        if r['dataset_id'] == dataset_id:
            groups[r['normalized_filename_base']].append(r)
    for base, group in groups.items():
        if len({r['split'] for r in group}) > 1:
            for r in group:
                base_rows.append({'dataset_id': dataset_id, 'base': base, 'split': r['split'],
                                  'source_id': r['source_id'], 'path': r['relative_path']})
write_csv(OUT / 'shared_filename_bases_preliminary.csv', base_rows,
          ['dataset_id', 'base', 'split', 'source_id', 'path'])

historical = list(csv.DictReader((ROOT / 'Articulo/reports/leakage_pairs.csv').open(encoding='utf-8-sig')))
historical_mapping = []
for index, pair in enumerate(historical, 2):
    raw_a = next(r for r in inventory if r['dataset_id'] == 'DATA-003' and r['split'] == pair['split_a'] and r['filename'] == pair['name_a'])
    raw_b = next(r for r in inventory if r['dataset_id'] == 'DATA-003' and r['split'] == pair['split_b'] and r['filename'] == pair['name_b'])
    mapped = {'legacy_pairs_csv_line': index, **pair, 'same_sha256': raw_a['sha256'] == raw_b['sha256']}
    for dataset in ['DATA-004', 'DATA-005']:
        for side in ['a', 'b']:
            raw = raw_a if side == 'a' else raw_b
            found = [r for r in inventory if r['dataset_id'] == dataset and r['filename'] == pair[f'name_{side}'] and r['sha256'] == raw['sha256']]
            assert len(found) == 1, (dataset, raw['relative_path'], len(found))
            mapped[f'{dataset}_split_{side}'] = found[0]['split']
    historical_mapping.append(mapped)
write_csv(OUT / 'historical_phash_pairs_current_locations.csv', historical_mapping)

cross_dataset = []
for a_id, b_id in itertools.combinations([x[0] for x in DATASETS], 2):
    a = [r for r in inventory if r['dataset_id'] == a_id]
    b = [r for r in inventory if r['dataset_id'] == b_id]
    hashes_a, hashes_b = {r['sha256'] for r in a}, {r['sha256'] for r in b}
    bases_a, bases_b = {r['normalized_filename_base'] for r in a}, {r['normalized_filename_base'] for r in b}
    cross_dataset.append({'dataset_a': a_id, 'dataset_b': b_id, 'shared_unique_sha256': len(hashes_a & hashes_b),
                          'images_a_matching_b_bytes': sum(r['sha256'] in hashes_b for r in a),
                          'images_b_matching_a_bytes': sum(r['sha256'] in hashes_a for r in b),
                          'shared_filename_bases': len(bases_a & bases_b)})
write_csv(OUT / 'cross_dataset_matches_preliminary.csv', cross_dataset)

sequence = Counter((r['dataset_id'], r['split'], r['sequence_name_hint']) for r in inventory if r['sequence_name_hint'])
write_csv(OUT / 'sequence_name_hints.csv', [{'dataset_id': key[0], 'split': key[1], 'name_hint': key[2], 'image_files': value} for key, value in sequence.items()])

notebooks = []
for path in sorted((ROOT / 'Mango-vision/notebooks').glob('*.ipynb')):
    nb = json.loads(path.read_text(encoding='utf-8'))
    relative = path.relative_to(ROOT).as_posix()
    notebooks.append({'path': relative, 'source_id': BY_PATH[relative]['source_id'],
                      'cells': len(nb['cells']), 'output_objects': sum(len(c.get('outputs', [])) for c in nb['cells']),
                      'executed_cells': sum(c.get('execution_count') is not None for c in nb['cells'])})

result = {'source_manifest': str(MANIFEST), 'image_total': len(inventory), 'datasets': summary,
          'exact_duplicates': duplicate_summary, 'structural_issues': len(issues), 'notebooks': notebooks,
          'historical_phash_pairs': len(historical),
          'historical_distance_counts': dict(Counter(x['dist'] for x in historical)),
          'historical_pairs_exact_bytes': sum(x['same_sha256'] for x in historical_mapping),
          'historical_pairs_still_cross_split_DATA004': sum(x['DATA-004_split_a'] != x['DATA-004_split_b'] for x in historical_mapping),
          'historical_pairs_still_cross_split_DATA005': sum(x['DATA-005_split_a'] != x['DATA-005_split_b'] for x in historical_mapping)}
(OUT / 'inventory_summary.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
assert len(inventory) == sum(x['image_files'] for x in summary)
assert sum(x['image_files'] for x in counts if x['class'] == 'ALL') == len(inventory)
assert all(x['source_id'] and len(x['sha256']) == 64 for x in inventory)
print(json.dumps(result, indent=2, ensure_ascii=False))
