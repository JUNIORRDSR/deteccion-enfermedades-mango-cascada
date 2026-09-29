"""Render the Kaggle kernel for M1 from the frozen manifest (PROTOCOL-AMENDMENT-008 v5).

probe: verifies the whole public corpus and the base digest; builds no model.
train: EXP-R01, train and valid only; the payload never names a test file.
capacity: non-scientific, a few epochs on the frozen train/valid to time a full run; its
  weights are deleted and its validation output silenced (round-5 M-01).
predict: EXP-V01 (phase valid) or EXP-R02 (phase test), only that phase's images, with the
  checkpoint attached from the training kernel and checked against its sealed hash. The test
  phase renders only from a COMMITTED, unmodified configs/evaluation_frozen.json.

Every render is one attempt: experiments/model1/<EXP>/v<N>/, never overwritten. Version N>1
needs the committed ledger <EXP>/attempts.jsonl (written by verify_kaggle_run.py) and the
retained files of version N-1, from which retry_allowed is re-derived (RETRY_POLICY, round-6
H-03). Training also needs the retained capacity-probe evidence, byte-checked (round-6 N-06).

The label digest uses LF line endings: the public commit stores LF and the local copy
was checked out with core.autocrlf=true (DECISION-033). The raw local label must still
match the manifest before it is normalised.
"""

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.evaluation import kaggle_job as job  # noqa: E402
from src.evaluation.provenance import ULTRALYTICS_OFF, authorized_root, check_output  # noqa: E402
from src.evaluation.train_model1 import FROZEN  # noqa: E402

REPO = 'DANN-MAGE/SemilleroTI-Mangos'
COMMIT = '98614804dd967e19a77af9fc58c27364d2e43bc9'
FREEZE_RECORD = 'data/manifests/model1_clean_manifest.freeze.json'
SELECTION_RECORD = 'experiments/model1/EXP-R01/selection_record.json'
CAPACITY = 'experiments/model1/KAGGLE-CAPACITY-001'
AMENDMENT = 'provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.json'
CAPACITY_EPOCHS = 3
BASE = {'url': 'https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26n.pt',
        'sha256': '9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef',
        'size': 5544453}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def committed_clean(root: Path, *paths: str) -> bool:
    """TASK-05 round 9: working bytes equal to their HEAD blob, not git status."""
    from src.evaluation.authority import committed_clean as clean
    return clean(root, *paths)


def approved(root: Path, mode: str, checkpoint: str | None = None) -> dict:
    """Round-5 H-02: the root of trust is committed, not supplied by the caller; and the
    amendment must permit this mode (TASK-05 review round 2 HIGH-01)."""
    if not committed_clean(root, FREEZE_RECORD, AMENDMENT):
        raise SystemExit('the freeze record and the amendment must be committed and unmodified')
    freeze = json.loads((root / FREEZE_RECORD).read_text(encoding='utf-8'))
    amendment = json.loads((root / AMENDMENT).read_text(encoding='utf-8'))
    selection = None
    if mode == 'predict':
        if not committed_clean(root, SELECTION_RECORD):
            raise SystemExit('the EXP-R01 selection record must be committed and unmodified')
        selection = json.loads((root / SELECTION_RECORD).read_text(encoding='utf-8'))
    job.authorize(mode, amendment, selection, checkpoint)
    if mode == 'train':
        capacity_retained(root)
    code = amendment['approved_code']
    return {'manifest_path': freeze['manifest_path'], 'manifest_sha256': freeze['manifest_sha256'],
            'trainer_sha256': code['trainer_sha256'], 'job_sha256': code['job_sha256']}


def capacity_retained(root: Path) -> None:
    """Round-6 N-06: before EXP-R01, every evidence byte of the capacity probe is retained,
    committed and equal to its receipt, and the probe found that the run fits."""
    receipt = json.loads((root / CAPACITY / 'receipt.json').read_text(encoding='utf-8'))
    verification = json.loads((root / CAPACITY / 'verification.json').read_text(encoding='utf-8'))
    names = [f'{CAPACITY}/evidence/{name}' for name in receipt['evidence']]
    if not committed_clean(root, f'{CAPACITY}/receipt.json', f'{CAPACITY}/verification.json',
                           f'{CAPACITY}/platform.json', f'{CAPACITY}/platform_log.json', *names):
        raise SystemExit('the capacity evidence must be retained and committed')
    for name, digest in receipt['evidence'].items():
        if sha(root / CAPACITY / 'evidence' / name) != digest:
            raise SystemExit(f'capacity evidence {name} differs from its receipt')
    if verification['capacity']['fits'] is not True:
        raise SystemExit('the capacity probe did not find that EXP-R01 fits')


RETRY_EVIDENCE = ('kernel.py', 'render_record.json', 'platform.json', 'platform_log.json',
                  'receipt.json', 'job_log.txt', 'reconciliation.json')


def attempt_dir(root: Path, mode: str, phase: str | None, experiment_id: str,
                version: int) -> Path:
    """experiments/model1/<EXP>/v<N>, only for the one experiment the mode may render and only
    when the committed ledger and the re-derived reconciliation of version N-1 allow version N
    (round-7 H-03)."""
    from verify_kaggle_run import ledger_entry, dumps, read_ledger, reconcile
    try:
        job.check_experiment(mode, phase, experiment_id)
    except job.JobRejected as error:
        raise SystemExit(str(error)) from None
    experiment = root / 'experiments' / 'model1' / experiment_id
    ledger_path = experiment / 'attempts.jsonl'
    ledger, rederived = [], None
    if version > 1:
        if not committed_clean(root, ledger_path.relative_to(root).as_posix()):
            raise SystemExit('the attempt ledger must be committed and unmodified')
        ledger = read_ledger(ledger_path)
        previous = experiment / f'v{version - 1}'
        missing = [n for n in RETRY_EVIDENCE if not (previous / n).is_file()]
        if missing:
            raise SystemExit(f'version {version - 1} lacks the retry evidence {missing}')
        files = [p.relative_to(root).as_posix() for p in previous.rglob('*') if p.is_file()]
        if not committed_clean(root, *files):
            raise SystemExit(f'the files of version {version - 1} must be committed')
        outcome = reconcile(previous, version - 1)
        stored = (previous / 'reconciliation.json').read_bytes()
        if dumps(outcome) != stored or not ledger or ledger[-1] != ledger_entry(outcome, stored):
            raise SystemExit(f'the reconciliation of version {version - 1} differs from its files '
                             'or from the ledger')
        if outcome['mode'] != mode or outcome['experiment_id'] != experiment_id:
            raise SystemExit('the previous version is another mode or experiment')
        rederived = (outcome['retry_allowed'], outcome['reason'])
    elif ledger_path.exists():
        raise SystemExit('version 1 exists already; render the next version')
    try:
        job.check_attempt(ledger, version, rederived, mode, experiment_id)
    except job.JobRejected as error:
        raise SystemExit(str(error)) from None
    target = experiment / f'v{version}'
    if target.exists():
        raise SystemExit(f'{target} exists; an attempt is never re-rendered')
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('probe', 'capacity', 'train', 'predict'),
                        required=True)
    parser.add_argument('--phase', choices=('valid', 'test'))
    parser.add_argument('--checkpoint-sha256')
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--experiment-id', required=True)
    parser.add_argument('--attempt', type=int, required=True,
                        help='Kaggle version number of this kernel; 1 for a new kernel')
    args = parser.parse_args()
    root = authorized_root()
    legacy = Path(json.loads((root / 'configs/root_mapping.json').read_text(encoding='utf-8'))
                  ['legacy_corpus'])
    declared = args.manifest.with_suffix('.csv.sha256').read_text(encoding='ascii').split()[0]
    if sha(args.manifest) != declared:
        raise SystemExit('manifest differs from its sidecar')
    if args.mode != 'probe':
        manifest_rel = args.manifest.resolve().relative_to(root.resolve()).as_posix()
        if not committed_clean(root, manifest_rel, manifest_rel + '.sha256'):
            raise SystemExit('the manifest must be committed and unmodified')
        job.check_bindings(manifest_rel, declared, sha(root / 'src/evaluation/train_model1.py'),
                           sha(root / 'src/evaluation/kaggle_job.py'),
                           approved(root, args.mode, args.checkpoint_sha256))
    out_dir = attempt_dir(root, args.mode, args.phase, args.experiment_id, args.attempt)
    rows = list(csv.DictReader(open(args.manifest, encoding='utf-8')))
    phase = {'train': ('train', 'valid'), 'capacity': ('train', 'valid'),
             'predict': (args.phase,)}.get(args.mode)
    config_path = root / ('configs/evaluation_frozen.json' if args.phase == 'test'
                          else 'configs/evaluation.json')
    if args.mode == 'predict':
        if not args.phase or not args.checkpoint_sha256:
            raise SystemExit('predict needs --phase and --checkpoint-sha256')
        config = json.loads(config_path.read_text(encoding='utf-8'))
        if config.get('checkpoint_sha256') != args.checkpoint_sha256:
            raise SystemExit('the config names another checkpoint than the sealed one')
        # TASK-05 round-3 NEW-HIGH-03: before EXP-V01 and EXP-R02, the config is bound to the
        # committed EXP-R01 selection record by hash and training kernel version.
        from src.evaluation import evaluate
        config_rel = config_path.relative_to(root).as_posix()
        if not committed_clean(root, config_rel):
            raise SystemExit(f'{config_rel} must be committed and unmodified')
        try:
            evaluate.approved_inference(root)  # the reviewed snapshot (TASK-05 round 5)
            evaluate.bound_selection(config)
            if args.phase == 'test':
                if not committed_clean(root, config_rel + '.sha256'):
                    raise SystemExit('the frozen config sidecar must be committed')
                evaluate.sealed_config(config_path, args.manifest)
        except evaluate.RunRejected as error:
            raise SystemExit(f'the {args.phase} phase cannot render: {error}') from None

    lines, forbidden = [], []
    for r in rows:
        repo_path = r['path'].split('/', 1)[1]
        label = legacy / r['label']
        if sha(legacy / r['path']) != r['sha256'] or sha(label) != r['label_sha256']:
            raise SystemExit(f"local bytes differ from the manifest: {r['image_id']}")
        line = (repo_path, r['sha256'], hashlib.sha256(job.lf(label.read_bytes())).hexdigest())
        if args.mode == 'probe' or r['proposed_split'] in phase:
            lines.append(line)
        else:
            forbidden += [repo_path, Path(repo_path).name, r['sha256']]
    paths = sorted(r['path'].split('/', 1)[1] for r in rows)
    payload = {'mode': args.mode, 'repo': REPO, 'commit': COMMIT, 'ultralytics': '8.4.52',
               'paths_digest': hashlib.sha256(''.join(p + '\n' for p in paths).encode()).hexdigest(),
               'files_digest': job.digest(lines), 'base': BASE,
               'manifest_sha256': declared, 'experiment_id': args.experiment_id}
    if args.mode == 'predict':
        payload.update({'phase': args.phase, 'checkpoint_sha256': args.checkpoint_sha256,
                        'split': job.rle(''.join('p' if s == args.phase else 'x' for s in (
                            r['proposed_split'] for r in sorted(
                                rows, key=lambda r: r['path'].split('/', 1)[1])))),
                        'inference': {k: config[k] for k in
                                      ('min_score', 'nms_iou', 'max_det', 'imgsz')},
                        'config_sha256': sha(config_path)})
    if args.mode in ('train', 'capacity'):
        trainer = root / 'src/evaluation/train_model1.py'
        payload.update({
            'split': job.rle(job.split_string(rows)), 'integrations_off': list(ULTRALYTICS_OFF),
            'font_url': 'https://github.com/ultralytics/assets/releases/download/v0.0.0/Arial.ttf',
            'trainer_sha256': sha(trainer),
            'config': {**FROZEN, 'workers': 2, 'device': '0', 'venue': 'kaggle',
                       **({'epochs': CAPACITY_EPOCHS} if args.mode == 'capacity' else {}),
                       'experiment_id': args.experiment_id,
                       'amendments': ['PROTOCOL-AMENDMENT-008']}})
    script = job.render(payload, forbidden=forbidden, trainer_source=(
        (root / 'src/evaluation/train_model1.py').read_text(encoding='utf-8')
        if args.mode in ('train', 'capacity') else None))
    out = check_output(root, out_dir, allow_directory=True)
    out.mkdir(parents=True, exist_ok=False)
    kernel = check_output(root, out / 'kernel.py')
    kernel.write_text(script, encoding='utf-8', newline='\n')
    record = {'kernel_sha256': sha(kernel), 'kernel_source_sha256': job.source_sha256(script),
              'manifest': args.manifest.as_posix(), 'manifest_sha256': declared,
              'payload_sha256': hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()).hexdigest(), 'selected_files': len(lines),
        'excluded_files': len(rows) - len(lines), 'mode': args.mode,
        'experiment_id': args.experiment_id, 'attempt': args.attempt}
    check_output(root, out / 'render_record.json').write_text(json.dumps(record, indent=2) + '\n',
                                                               encoding='utf-8')
    print(json.dumps(record, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
