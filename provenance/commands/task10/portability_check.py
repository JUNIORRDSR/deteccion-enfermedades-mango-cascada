"""TASK-10: portability of the source identities (reports/portability_check.json).

The smallest real legacy sources are copied (read only) into a temporary root under their logical
paths; an alternate root mapping must resolve every one to the same SHA-256, independent of the
absolute prefix. A missing root, an escaping or absolute logical path and an absent file must fail.
The temporary root is deleted; the report records only logical data and the check results.
"""

import csv
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.evaluation.provenance import (  # noqa: E402
    authorized_root, check_output, resolve_source, sha256, verify_sources,
)

LOCATIONS = ROOT / 'provenance/source_locations.csv'
MAPPING = ROOT / 'configs/root_mapping.json'
OUT = 'reports/portability_check.json'
SAMPLE = 20


def main() -> int:
    root = authorized_root()
    out = check_output(root, root / OUT)
    mapping = json.loads(MAPPING.read_text(encoding='utf-8'))
    rows = [r for r in csv.DictReader(open(LOCATIONS, encoding='utf-8'))
            if r['logical_root'] == 'legacy_corpus']
    for r in rows:
        r['_size'] = resolve_source(r, mapping).stat().st_size
    sample = sorted(rows, key=lambda r: (r['_size'], r['source_id']))[:SAMPLE]
    checks = {}
    with tempfile.TemporaryDirectory() as tmp:
        alternate = Path(tmp) / 'otro_prefijo' / 'corpus'
        for r in sample:
            target = alternate / r['logical_path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(resolve_source(r, mapping), target)
        clean = [{k: v for k, v in r.items() if not k.startswith('_')} for r in sample]
        roots = {'legacy_corpus': str(alternate)}
        same = all(sha256(resolve_source(r, roots)) == r['sha256'] for r in clean)
        discrepancies = verify_sources(clean, roots)
        checks['alternate_prefix_same_sha256'] = same and not discrepancies

        def fails(call, error) -> bool:
            try:
                call()
            except error:
                return True
            return False
        r0 = clean[0]
        checks['missing_root_fails'] = fails(lambda: resolve_source(r0, {}), ValueError)
        checks['escaping_path_fails'] = fails(
            lambda: resolve_source({**r0, 'logical_path': '../fuera.bin'}, roots), ValueError)
        checks['absolute_path_fails'] = fails(
            lambda: resolve_source({**r0, 'logical_path': 'C:/absoluto.bin'}, roots), ValueError)
        checks['absent_file_fails'] = fails(
            lambda: resolve_source({**r0, 'logical_path': 'no_existe.bin'}, roots), FileNotFoundError)
        (alternate / r0['logical_path']).write_bytes(b'alterado')
        checks['altered_byte_detected'] = len(verify_sources([r0], roots)) == 1
    report = {'task': 'TASK-10 portability', 'sample': [
        {'source_id': r['source_id'], 'logical_root': r['logical_root'],
         'logical_path': r['logical_path'], 'sha256': r['sha256']} for r in sample],
        'mapping_roots': sorted(mapping), 'checks': checks, 'passed': all(checks.values()),
        'note': 'the local absolute paths of this machine are local data, not part of the identity'}
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(checks))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
