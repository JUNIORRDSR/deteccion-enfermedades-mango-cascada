"""Table 4: M1 on validation at the frozen operating point (experiments/model1/EXP-V01/metrics_frozen.json).

The validation records were predicted under configs/evaluation.json, so `--score` with the frozen
config refuses them (the run embeds the validation config). This derives the same scoring:
_score_split re-verifies the predictions against their own config (provenance, environment,
AP), the threshold comes from the sealed frozen config, and the operating metrics use the
evaluator's own functions. The threshold was chosen on these records, so P, R, F1 and F2 are
optimistic; Table 4 says so."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.evaluation import evaluate  # noqa: E402

PREDICTIONS = ROOT / 'experiments/model1/EXP-V01/predictions.jsonl'
CONFIG = ROOT / 'configs/evaluation.json'
FROZEN = ROOT / 'configs/evaluation_frozen.json'
MANIFEST = ROOT / evaluate.M1_MANIFEST
OUT = ROOT / 'experiments/model1/EXP-V01/metrics_frozen.json'


def main() -> int:
    out = evaluate._new(OUT)
    result = evaluate._score_split(PREDICTIONS, CONFIG, MANIFEST, evaluate.VALIDATION_SPLIT)
    threshold = evaluate.sealed_config(FROZEN, MANIFEST)['threshold']
    config = evaluate.read_config(CONFIG)
    records = evaluate.load_records(PREDICTIONS, evaluate.VALIDATION_SPLIT,
                                    evaluate.read_manifest(MANIFEST), config['class_names'])
    scored = evaluate.score(records, config, threshold)
    if scored['average_precision'] != result['average_precision'] or scored['counts'] != result['counts']:
        raise SystemExit('the frozen scoring disagrees with the verified validation scoring')
    evaluate._write_json(out, {
        **result, 'threshold': threshold, 'operating_metrics': scored['operating_metrics'],
        'detection_confusion': scored['detection_confusion'],
        'frozen_config_sha256': hashlib.sha256(FROZEN.read_bytes()).hexdigest(),
        'note': 'threshold chosen on these validation records: P, R, F1 and F2 are optimistic'})
    print(f'wrote {out.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
