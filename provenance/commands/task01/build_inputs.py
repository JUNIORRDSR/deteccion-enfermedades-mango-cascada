"""Materialize portable references without changing observed manifests."""

import csv
import json
from pathlib import Path

from src.evaluation.provenance import sha256, validate_locations

root = Path.cwd().resolve()
legacy = Path('C:/Users/junio/Downloads/mango-vision').resolve()
external = Path('C:/Users/junio/Downloads').resolve()
mapping = {'legacy_corpus': str(legacy), 'external_mail': str(external), 'revision': str(root)}
(root / 'configs').mkdir(exist_ok=True)
(root / 'configs/root_mapping.json').write_text(json.dumps(mapping, indent=2) + '\n', encoding='utf-8')

with (root / 'provenance/source_manifest.csv').open(encoding='utf-8-sig', newline='') as stream:
    manifest = list(csv.DictReader(stream))
locations = []
for row in manifest:
    source = Path(row['path']).resolve()
    if source.is_relative_to(legacy):
        name, base = 'legacy_corpus', legacy
    elif source.is_relative_to(external):
        name, base = 'external_mail', external
    else:
        raise ValueError(f"{row['source_id']}: unmapped original path")
    locations.append({'source_id': row['source_id'], 'logical_root': name,
                      'logical_path': source.relative_to(base).as_posix(),
                      'local_absolute_path': str(source), 'sha256': row['sha256']})
validate_locations(manifest, locations)
with (root / 'provenance/source_locations.csv').open('w', encoding='utf-8', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(locations[0]))
    writer.writeheader()
    writer.writerows(locations)

by_source = {row['source_id']: row for row in locations}
with (root / 'provenance/artifact_registry.csv').open(encoding='utf-8-sig', newline='') as stream:
    artifacts = {row['artifact_id']: row for row in csv.DictReader(stream)}
weights = []
for art_id in ('ART-001', 'ART-002', 'ART-003', 'ART-004'):
    art = artifacts[art_id]
    source = by_source[art['source_id']]
    if art['sha256'] != source['sha256']:
        raise ValueError(f'{art_id}: registry SHA256 differs from source manifest')
    weights.append({'artifact_id': art_id, **source, 'status': 'PRESENT_HASH_PENDING_VERIFICATION'})

inputs = {
    'environment': {'kind': 'RECONSTRUCTED', 'python': '3.12.14',
                    'ultralytics': '8.4.52', 'historical_model1_ultralytics': '8.4.39'},
    'source_manifest_sha256': sha256(root / 'provenance/source_manifest.csv'),
    'weights': weights,
    'datasets': [
        {'dataset_id': 'DATA-001', 'logical_root': 'legacy_corpus',
         'logical_path': 'SemilleroTI-Mangos/docs/MangosDataset',
         'inventory': 'data/manifests/legacy_dataset_inventory.csv'},
        {'dataset_id': 'DATA-004', 'logical_root': 'legacy_corpus',
         'logical_path': 'Mango-vision/DatasetMango_YOLO_clean',
         'inventory': 'data/manifests/legacy_dataset_inventory.csv'},
        {'dataset_id': 'DATA-005', 'logical_root': 'legacy_corpus',
         'logical_path': 'Mango-vision/DatasetMango_YOLO_cls',
         'inventory': 'data/manifests/legacy_dataset_inventory.csv'},
    ],
    'model1_base_checkpoint': {'name': 'yolo26n.pt', 'status': 'BLOCKED_MISSING_BASE_CHECKPOINT',
                               'source_id': None, 'sha256': None},
}
(root / 'configs/inputs.json').write_text(json.dumps(inputs, indent=2) + '\n', encoding='utf-8')
print(f"materialized {len(locations)} source locations and {len(weights)} weight references")
