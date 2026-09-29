"""TASK-06: a JSON summary of the committed benchmark CSV, so the manuscript number registry can
re-derive the latency values (audit B, B-08). Pure function of artifacts/metrics/benchmark_raw.csv,
with the benchmark's own summarize(); wall stages only, measured repetitions that succeeded,
values in milliseconds. Never overwrites a different summary.
"""

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.benchmarks.run import SUMMARY_DEFINITION, summarize  # noqa: E402

RAW = ROOT / 'artifacts/metrics/benchmark_raw.csv'
OUT = ROOT / 'artifacts/metrics/benchmark_summary.json'
STAGES = ('read', 'decode', 'm1', 'm2_crops', 'annotate', 'encode', 'cascade', 'end_to_end')


def main() -> int:
    rows = [r for r in csv.DictReader(open(RAW, encoding='utf-8'))
            if r['kind'] == 'wall' and r['status'] == 'ok']
    summary = {'source': RAW.relative_to(ROOT).as_posix(),
               'source_sha256': hashlib.sha256(RAW.read_bytes()).hexdigest(),
               'unit': 'ms', 'definition': SUMMARY_DEFINITION, 'stages': {}}
    for stage in STAGES:
        s = summarize([int(r['wall_ns']) for r in rows if r['stage'] == stage])
        summary['stages'][stage] = {'n': s['n'], **{k: s[k] / 1e6 for k in
                                                    ('mean', 'median', 'std', 'p95', 'min', 'max')}}
    data = (json.dumps(summary, indent=2) + '\n').encode('utf-8')
    if OUT.exists() and OUT.read_bytes() != data:
        raise SystemExit(f'{OUT} exists with other bytes')
    OUT.write_bytes(data)
    print(json.dumps({k: v['median'] for k, v in summary['stages'].items()}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
