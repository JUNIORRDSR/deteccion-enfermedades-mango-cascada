"""Reconcile one downloaded Kaggle attempt into an immutable record (PROTOCOL-AMENDMENT-008 v8).

Layout: experiments/model1/<EXP>/v<N>/ holds what the renderer wrote (kernel.py,
render_record.json), what the platform gave (platform.json with status, Docker image and the
outputs list; platform_log.json) and EVERY output the platform lists, downloaded (round-7
N-07). Every downloaded file is hashed; a file the receipt inventory names must match it
("attested"); anything else, such as partial weights written after the last receipt update
of a hard-cut session, is recorded as unattested. A platform output that was not downloaded,
or a downloaded file the platform does not list, stops the reconciliation. When a receipt
exists the job log must exist too. A missing receipt is recorded, not an error: it is the
signature of a hard cut and makes the attempt non-retriable.

Writes, each atomically and in this order: v<N>/reconciliation.json, the seal of a COMPLETE
run (capacity: v<N>/verification.json; EXP-R01: <EXP>/selection_record.json, checkpoint
recomputed from epoch_records.jsonl: maximum UNROUNDED fitness, last epoch on a tie, and the
bytes of selected.pt), and last the ledger <EXP>/attempts.jsonl. Rerunning after an
interruption resumes: bytes already written must equal the recomputation (round-7 NEW-M-01).
"""

import argparse
import csv
import hashlib
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.evaluation import kaggle_job as job  # noqa: E402
from src.evaluation.evaluate import RunRejected, executed_source  # noqa: E402
from src.evaluation.provenance import authorized_root, check_output  # noqa: E402

VIEW = {'train': 'train', 'valid': 'val'}
REQUIRED = {'train': ('run/epoch_records.jsonl', 'run/weights/selected.pt'),
            'capacity': (), 'predict': ('predictions_raw.jsonl',)}
# Written locally, never by the platform.
LOCAL = ('kernel.py', 'render_record.json', 'platform.json', 'platform_log.json',
         'reconciliation.json', 'verification.json')


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else None


def dumps(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode('utf-8')


def atomic_write(path: Path, data: bytes) -> None:
    """Temporary file, fsync, replace: a reader sees the old bytes or the new ones."""
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def reconcile(run: Path, version: int) -> dict:
    """Pure over the files of one attempt directory."""
    kernel = (run / 'kernel.py').read_text(encoding='utf-8')
    record = json.loads((run / 'render_record.json').read_text(encoding='utf-8'))
    platform = json.loads((run / 'platform.json').read_text(encoding='utf-8'))
    if not (run / 'platform_log.json').is_file():
        raise SystemExit('platform_log.json is required for every attempt')
    if record['kernel_sha256'] != sha(run / 'kernel.py') \
            or record['kernel_source_sha256'] != job.source_sha256(kernel):
        raise SystemExit('kernel.py differs from its render record')
    if platform.get('version') != version:
        raise SystemExit(f"platform.json is version {platform.get('version')}, not {version}")
    downloaded = {p.relative_to(run).as_posix(): sha(p) for p in sorted(run.rglob('*'))
                  if p.is_file() and p.relative_to(run).as_posix() not in LOCAL
                  and not p.name.endswith('.tmp')}
    outputs = set(platform.get('outputs', []))
    if outputs - set(downloaded):
        raise SystemExit(f'platform outputs not downloaded: {sorted(outputs - set(downloaded))[:5]}')
    if set(downloaded) - outputs:
        raise SystemExit(f'files the platform does not list: {sorted(set(downloaded) - outputs)[:5]}')
    receipt = read_json(run / 'receipt.json')
    inventory = {}
    if receipt is not None:
        if receipt.get('payload_sha256') != record['payload_sha256']:
            raise SystemExit('the receipt comes from another payload')
        try:
            executed_source(kernel, receipt.get('kernel_source_sha256'))
        except RunRejected as error:
            raise SystemExit(str(error)) from None
        if 'job_log.txt' not in downloaded:
            raise SystemExit('an attempt with a receipt must retain job_log.txt')
        inventory = receipt.get('inventory', {})
        for name, digest in inventory.items():
            if name in downloaded and downloaded[name] != digest:
                raise SystemExit(f'{name} differs from the receipt inventory')
            if name.startswith('evidence/') and name not in downloaded:
                raise SystemExit(f'evidence file not retained: {name}')
    files = {name: {'sha256': digest, 'attested': inventory.get(name) == digest}
             for name, digest in downloaded.items()}
    status = receipt.get('status') if receipt else 'NO_RECEIPT'
    if status == 'COMPLETE':
        missing = [n for n in REQUIRED[record['mode']] if not files.get(n, {}).get('attested')]
        if missing:
            raise SystemExit(f'a COMPLETE {record["mode"]} run must retain {missing}')
    definitive = status == 'COMPLETE' or (
        record['mode'] == 'predict' and receipt is not None
        and receipt.get('stage') in job.PREDICTIONS_DEFINITIVE
        and files.get('predictions_raw.jsonl', {}).get('sha256') == receipt.get('predictions_raw_sha256'))
    allowed = (False, 'definitive') if definitive else job.retry_allowed(
        record['mode'], receipt, platform.get('status'), sorted(outputs),
        [(run / n).read_text(encoding='utf-8') for n in ('platform_log.json', 'job_log.txt')
         if (run / n).is_file()])
    return {'version': version, 'mode': record['mode'], 'phase': (receipt or {}).get('phase'),
            'experiment_id': record.get('experiment_id'), 'status': status,
            'stage': receipt.get('stage') if receipt else None,
            'error': receipt.get('error') if receipt else None, 'definitive': definitive,
            'platform_status': platform.get('status'), 'docker_image': platform.get('docker_image'),
            'receipt_sha256': downloaded.get('receipt.json'),
            'render_record_sha256': sha(run / 'render_record.json'),
            'platform_sha256': sha(run / 'platform.json'),
            'platform_log_sha256': sha(run / 'platform_log.json'),
            'kernel_source_sha256': record['kernel_source_sha256'],
            'payload_sha256': record['payload_sha256'], 'files': files,
            'unattested': sorted(n for n, f in files.items() if not f['attested']),
            'inventory_not_downloaded': sorted(set(inventory) - set(downloaded)),
            'retry_allowed': allowed[0], 'reason': allowed[1]}


def ledger_entry(outcome: dict, reconciliation: bytes) -> dict:
    return {**{k: outcome[k] for k in ('version', 'mode', 'phase', 'experiment_id', 'status',
                                       'stage', 'definitive', 'platform_status', 'retry_allowed',
                                       'reason', 'receipt_sha256')},
            'reconciliation_sha256': hashlib.sha256(reconciliation).hexdigest()}


def read_ledger(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()] \
        if path.is_file() else []


def finalize(run: Path, version: int, outcome: dict, sealed: tuple[Path, dict] | None,
             write=atomic_write) -> dict:
    """Reconciliation, then the seal, then the ledger, each atomic. A version already in the
    ledger, or bytes already on disk, must equal the recomputation: that makes a rerun after
    any interruption either a no-op or the completion of the missing steps."""
    ledger_path = run.parent / 'attempts.jsonl'
    ledger = read_ledger(ledger_path)
    reconciliation = dumps(outcome)
    entry = ledger_entry(outcome, reconciliation)
    earlier = [e for e in ledger if e['version'] < version]
    if [e['version'] for e in earlier] != list(range(1, version)) \
            or [e['version'] for e in ledger] not in (list(range(1, version)),
                                                        list(range(1, version + 1))):
        raise SystemExit(f'the ledger must hold versions 1..{version - 1} before version {version}')
    targets = [(run / 'reconciliation.json', reconciliation)]
    if sealed is not None:
        targets.append((sealed[0], dumps(sealed[1])))
    for path, data in targets:
        if path.exists():
            if path.read_bytes() != data:
                raise SystemExit(f'{path.name} exists with other bytes than the recomputation')
        else:
            write(path, data)
    if len(ledger) == version:
        if ledger[-1] != entry:
            raise SystemExit(f'the ledger line of version {version} differs from the recomputation')
    else:
        write(ledger_path, b''.join(dumps_line(e) for e in ledger + [entry]))
    return entry


def dumps_line(entry: dict) -> bytes:
    return (json.dumps(entry, sort_keys=True) + '\n').encode('utf-8')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', type=Path, required=True, help='experiments/model1/<EXP>/v<N>')
    parser.add_argument('--manifest', type=Path, required=True)
    args = parser.parse_args()
    root = authorized_root()
    run = args.run_dir.resolve()
    check_output(root, run, allow_directory=True)
    if not run.name.startswith('v') or not run.name[1:].isdigit():
        raise SystemExit('the run dir must be <EXP>/v<N>')
    version = int(run.name[1:])
    outcome = reconcile(run, version)
    render = json.loads((run / 'render_record.json').read_text(encoding='utf-8'))
    if render['manifest_sha256'] != sha(args.manifest):
        raise SystemExit('the manifest is not the one the kernel was rendered from')
    if render.get('experiment_id') != run.parent.name:
        raise SystemExit('the attempt directory is not the experiment it was rendered for')
    sealed = None
    if outcome['status'] == 'COMPLETE' and outcome['mode'] != 'predict':
        sealed = seal(root, run, version, args.manifest, render, outcome)
    entry = finalize(run, version, outcome, sealed)
    print(json.dumps(entry, indent=2))
    if sealed is not None:
        print(json.dumps({k: v for k, v in sealed[1].items() if k != 'environment'}, indent=2))
    return 0


def seal(root: Path, run: Path, version: int, manifest: Path, render: dict, outcome: dict):
    """A COMPLETE capacity or training run: the receipt against the frozen manifest, and for
    training the checkpoint selection recomputed locally."""
    legacy = Path(json.loads((root / 'configs/root_mapping.json').read_text(encoding='utf-8'))
                  ['legacy_corpus'])
    receipt = json.loads((run / 'receipt.json').read_text(encoding='utf-8'))
    kernel = (run / 'kernel.py').read_text(encoding='utf-8')
    expected = {}
    for r in csv.DictReader(open(manifest, encoding='utf-8')):
        if r['proposed_split'] in VIEW:
            label = (legacy / r['label']).read_bytes()
            expected[r['path'].split('/', 1)[1]] = (VIEW[r['proposed_split']], r['sha256'],
                                                    hashlib.sha256(job.lf(label)).hexdigest())
    job.verify_receipt(receipt, expected, render['payload_sha256'], kernel_source=kernel)
    out = {'mode': receipt['mode'], 'kernel_version': version,
           'receipt_sha256': sha(run / 'receipt.json'), 'payload_sha256': receipt['payload_sha256'],
           'kernel_source_sha256': receipt['kernel_source_sha256'],
           'kernel_source_method': receipt.get('kernel_source_method'),
           'docker_image': outcome['docker_image'], 'files_verified': len(expected),
           'pip_check_verdict': receipt['environment'].get('pip_check_verdict'),
           'environment': {k: receipt['environment'][k] for k in
                           ('python', 'torch', 'cuda', 'cudnn', 'ultralytics', 'gpus')}}
    if receipt['mode'] == 'capacity':
        out['capacity'] = receipt['capacity']
        target = run / 'verification.json'
    else:
        epochs = [json.loads(line) for line in
                  (run / 'run' / 'epoch_records.jsonl').read_text(encoding='utf-8').splitlines()]
        if not epochs or not all(math.isfinite(e['fitness']) for e in epochs):
            raise SystemExit('epoch records are missing or non-finite')
        best = max(epochs, key=lambda e: (e['fitness'], e['epoch']))
        result = receipt['result']
        selected = run / 'run' / 'weights' / 'selected.pt'
        if (best['epoch'] != result['selected_epoch']
                or repr(best['fitness']) != result['selected_fitness_repr']
                or sha(selected) != result['selected_sha256']):
            raise SystemExit('the local recomputation disagrees with the selected checkpoint')
        out.update({'experiment_id': receipt.get('experiment_id'),
                    'attempt_dir': run.relative_to(root.resolve()).as_posix(),
                    'selected_epoch': best['epoch'], 'selected_fitness_repr': repr(best['fitness']),
                    'selected_sha256': result['selected_sha256'], 'epochs_recorded': len(epochs),
                    'epoch_records_sha256': sha(run / 'run' / 'epoch_records.jsonl'),
                    'rule': 'maximum unrounded validation mAP50-95 fitness; last epoch on a tie'})
        target = run.parent / 'selection_record.json'
    return check_output(root, target), out


if __name__ == '__main__':
    raise SystemExit(main())
