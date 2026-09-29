"""TASK-06: m1_conf of configs/benchmark.json is the frozen M1 operating point, copied from the
sealed configs/evaluation_frozen.json (validated by evaluate.sealed_config), never typed.

Run once after the freeze is committed; the benchmark CLI refuses to run while m1_conf is null.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.evaluation import evaluate  # noqa: E402

BENCHMARK = ROOT / 'configs/benchmark.json'


def main() -> int:
    frozen = evaluate.sealed_config(ROOT / evaluate.FROZEN_CONFIG, ROOT / evaluate.M1_MANIFEST, ROOT)
    config = json.loads(BENCHMARK.read_text(encoding='utf-8'))
    if config['m1_conf'] is not None:
        raise SystemExit(f"m1_conf is already {config['m1_conf']}")
    if config['m1_weights']['sha256'] != frozen['checkpoint_sha256']:
        raise SystemExit('the benchmark weights are not the checkpoint the freeze seals')
    config['m1_conf'] = frozen['threshold']
    config['notes']['m1_conf'] = (f"threshold of {evaluate.FROZEN_CONFIG} (sha256 "
                                  f"{evaluate._sha(ROOT / evaluate.FROZEN_CONFIG)}), copied by "
                                  'provenance/commands/task06/set_benchmark_conf.py')
    BENCHMARK.write_text(json.dumps(config, indent=2, ensure_ascii=False) + '\n',
                         encoding='utf-8', newline='\n')
    print(json.dumps({'m1_conf': config['m1_conf']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
