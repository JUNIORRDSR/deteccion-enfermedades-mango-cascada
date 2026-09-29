"""Write <EXP>/predictions.jsonl from the definitive committed attempt (TASK-05 rounds 3-4).

The derivation is evaluate.write_predictions: the attempt is the one the committed ledger of
the phase's experiment (EXP-V01 or EXP-R02) marks definitive, its reconciliation must
re-derive byte for byte from its committed files, and evaluate.rebuild_predictions turns its
raw predictions into records. The operating-point freeze, test scoring and intervals rerun
the same derivation, so nothing written here is trusted on its own. The frozen command
`evaluate --model-id model1 ... --run-dir <EXP>` calls the same function.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.evaluation.evaluate import SPLIT_NAMES, write_predictions  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', type=Path, required=True,
                        help='experiments/model1/EXP-V01 or experiments/model1/EXP-R02')
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--phase', choices=('val', 'valid', 'test'), required=True)
    args = parser.parse_args()
    identities = write_predictions(args.run_dir, args.config, args.manifest,
                                   SPLIT_NAMES[args.phase])
    print(json.dumps(identities, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
