"""Regenerate the TASK-01 artifact registry rows from the exact bytes on disk.

Closes finding N2 round 2: ART-103 carried a stale size and SHA256 because the
row was written before the file was trimmed and never regenerated. A consumer
following the registry would have had to reject the artifact.

Also closes the linkage half of finding 10 round 2: the new rows left
source_id, experiment_ids and reproduced blank while every prior row fills them.
"""

import csv
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.evaluation.provenance import authorized_root, check_output  # noqa: E402

PRODUCED_BY = {
    'reports/source_verification.json':
        'provenance/commands/task01/command.txt: source verification',
    'provenance/environment/runtime_path_report.json':
        'provenance/commands/task01/verify_runtime_paths.py',
    'provenance/environment/pip_config_redacted.txt':
        'provenance/commands/task01/install_reconstructed.py, redacted consolidation',
    'provenance/commands/task01/command.txt':
        'provenance/commands/task01/register_artifacts.py companion record',
    'provenance/incidents/INCIDENT-001.json':
        'provenance/commands/task01/verify_runtime_paths.py, first version',
    'provenance/environment/cpu_topology_probe.json':
        'provenance/commands/task01/probe_cpu_topology.py',
}


def main() -> int:
    root = authorized_root()
    registry = root / 'provenance' / 'artifact_registry.csv'
    with registry.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)

    by_path = {row['path']: row for row in rows}
    next_id = max(int(row['artifact_id'].split('-')[1]) for row in rows) + 1
    changed, added = [], []

    for relative, producer in PRODUCED_BY.items():
        raw = (root / relative).read_bytes()
        digest, size = hashlib.sha256(raw).hexdigest(), str(len(raw))
        row = by_path.get(relative)
        if row is None:
            row = {field: '' for field in fields}
            row['artifact_id'] = f'ART-{next_id:03d}'
            next_id += 1
            row['path'] = relative
            rows.append(row)
            by_path[relative] = row
            added.append(row['artifact_id'])
        elif row.get('sha256') != digest or row.get('size_bytes') != size:
            changed.append((row['artifact_id'], row.get('sha256', '')[:12], digest[:12]))
        row['sha256'], row['size_bytes'] = digest, size
        # Match the registry's established nonblank semantics.
        for key, value in (('source_id', 'DERIVED_IN_REVISION'),
                           ('experiment_id', 'TASK-01'),
                           ('experiment_ids', 'TASK-01'),
                           ('reproduced', 'NO'),
                           ('artifact_type', row.get('artifact_type') or 'task-01 evidence'),
                           ('relation', row.get('relation') or f'produced by {producer}')):
            if key in row and not (row.get(key) or '').strip():
                row[key] = value

    destination = check_output(root, registry)
    with destination.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    mismatches = []
    with destination.open(encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream):
            path = root / row['path']
            declared = (row.get('sha256') or '').strip()
            if not path.is_file() or not declared:
                continue
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != declared or int(row['size_bytes']) != len(raw):
                mismatches.append(row['artifact_id'])
    print(f'corrected={changed} added={added} remaining_mismatches={mismatches}')
    return 0 if not mismatches else 2


if __name__ == '__main__':
    raise SystemExit(main())
