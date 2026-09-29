"""Self-contained Kaggle job for M1 (PROTOCOL-AMENDMENT-008). Standard library only.

Nothing is uploaded. The corpus is read from the public commit that holds DATA-001; the
job receives a closed payload fixed locally from the FROZEN manifest:
- the digest of the sorted image-path list, so the commit is the expected corpus;
- one character per image (t train, v valid, p predict, x not in this phase), so test
  images are never requested in a training session;
- the digest of every selected (path, image SHA256, label SHA256 with LF line endings);
- the official digest of the base checkpoint and the exact trainer source.
Every downloaded file is also checked against the git blob SHA-1 of the commit tree.

The kernel cannot know the manifest, so the root of trust is local and checked twice:
check_bindings (before rendering: the frozen manifest and the approved code hashes) and
verify_receipt (after the run: exactly the phase's files, the rendered payload and the
executed source). `render` writes this file with PAYLOAD filled in.
"""

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import traceback
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PAYLOAD = json.loads('{"base": {"sha256": "9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef", "size": 5544453, "url": "https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26n.pt"}, "checkpoint_sha256": "0648da3f3641e3cdb5a1908a092ba892548942836a249bb3b39667f9ae8e8125", "commit": "98614804dd967e19a77af9fc58c27364d2e43bc9", "config_sha256": "b06081e926d01753cd276d2a3535b2f1e8a5975e7de1db031dc8e786c714e228", "experiment_id": "EXP-R02", "files_digest": "e6cc21ac348c3890f9c73b80d0c3975302bdb9b48d9d11e577ec66b433766ddc", "inference": {"imgsz": 640, "max_det": 300, "min_score": 0.001, "nms_iou": 0.6}, "manifest_sha256": "dd9431dd7bbc00c6117baf6a0f6cf49eff8bc55f144016b4a98dbdea049ecf5f", "mode": "predict", "paths_digest": "56a5280554e48e9472e0e235b2b136ae314ee22f3ad52e16d69513cfb002c6a1", "phase": "test", "repo": "DANN-MAGE/SemilleroTI-Mangos", "split": "p3x6p1x1p3x20p1x1p1x1p4x1p1x1p3x1p4x3p3x2p1x5p1x1p2x3p1x2p3x1p1x1p4x3p3x1p2x1p1x2p1x2p1x1p1x3p1x3p2x4p2x4p1x1p6x1p1x3p5x4p1x2p1x2p3x1p1x1p2x1p2x3p2x1p2x2p2x1p4x1p4x3p1x1p1x1p3x3p2x3p1x330p3x3p2x6p1x1p1x1p3x2p1x2p2x2p1x1p1x3p3x3p1x2p1x2p1x85", "ultralytics": "8.4.52"}')
PREFIX = 'docs/MangosDataset/'
SPLIT_DIRS = ('train', 'valid', 'test')
CODES = {'t': 'train', 'v': 'val', 'p': 'predict', 'x': None}
# Environment variables worth keeping; everything else (tokens included) is never read.
ENV_WHITELIST = ('CUDA_VERSION', 'CUDA_VISIBLE_DEVICES', 'CUBLAS_WORKSPACE_CONFIG',
                 'KAGGLE_KERNEL_RUN_TYPE', 'NVIDIA_DRIVER_CAPABILITIES', 'NVIDIA_VISIBLE_DEVICES',
                 'OMP_NUM_THREADS', 'PYTHONHASHSEED', 'YOLO_CONFIG_DIR', 'YOLO_OFFLINE')
# Round-6 N-06: a pip-check conflict blocks only when its dependent package is one the pipeline
# imports, i.e. in the dependency closure of these roots; an unparsed line blocks too.
PIP_CHECK_ROOTS = ('ultralytics', 'torch', 'torchvision')
PIP_CHECK_LINE = re.compile(r'^(\S+) \S+ (requires \S+, which is not installed\.'
                            r'|has requirement .+, but you have .+\.)$')
# Round-6 H-03/N-05/N-07: the attempt state machine. The amendment JSON is written from this
# dict, so the machine-readable policy and the code cannot drift apart.
RETRY_POLICY = {
    'max_versions': 3,
    'retry_stages': {'capacity': ['start', 'environment', 'download', 'base'],
                     'train': ['start', 'environment', 'download', 'base'],
                     'predict': ['start', 'environment', 'download', 'predict']},
    'retry_requires': ['the previous version is in the committed ledger with its receipt, '
                       'platform status, platform log and outputs list',
                       'receipt status FAILED and platform status ERROR',
                       'the failed stage is a retry stage of its mode',
                       'no model output: no .pt, epoch_records.jsonl or predictions_raw.jsonl',
                       'no line of the platform or job log matches metric_pattern'],
    'never_retried': ['operator cancellation or any platform status other than ERROR',
                      'termination without a FAILED receipt (hard cut, timeout)',
                      'a failure after the model is built or training started',
                      'any version after a COMPLETE one'],
    'definitive': ('the first COMPLETE version; for predict, the first version that reaches '
                   'predictions_written, whatever happens next'),
    'metric_pattern': r'mAP50|fitness|metrics/',
}
MODEL_OUTPUTS = ('.pt', 'epoch_records.jsonl', 'predictions_raw.jsonl')
# Round-7 H-03: each scientific mode has exactly one experiment; the capacity probes share a
# prefix. The renderer and every ledger line are bound to this mapping.
EXPERIMENT_OF = {'train': 'EXP-R01', 'valid': 'EXP-V01', 'test': 'EXP-R02'}
CAPACITY_PREFIX = 'KAGGLE-CAPACITY-'
PIP_CHECK_OK = 'No broken requirements found.'
# TASK-05 round-4 MEDIUM-04 / NEW-MEDIUM-03: YOLO26n is end-to-end and M1 names are ordered
# (checked on a YOLO26n checkpoint under Ultralytics 8.4.52); a run claiming otherwise is refused.
M1_END2END = True
M1_MODEL_NAMES = {'0': 'Enfermo', '1': 'Saludable'}
# A predict attempt is definitive once its raw predictions are hashed in a durable receipt.
PREDICTIONS_DEFINITIVE = ('predictions_written', 'done')
# TASK-05 round-3 MEDIUM-04: the runtime evidence is compared as exact values, never truthiness.
INPUT_CONTRACT = ('file path given to Ultralytics predict: the loader reads BGR and '
                  'preprocessing converts to RGB; rect letterbox at imgsz')


def experiment_for(mode: str, phase: str | None) -> str | None:
    return EXPERIMENT_OF.get(phase if mode == 'predict' else mode)


def check_experiment(mode: str, phase: str | None, experiment_id: str) -> None:
    """The only experiment a mode may render (round-7 H-03)."""
    if mode == 'capacity':
        if not experiment_id.startswith(CAPACITY_PREFIX):
            raise JobRejected(f'a capacity probe must be {CAPACITY_PREFIX}NNN')
    elif experiment_for(mode, phase) != experiment_id:
        raise JobRejected(f'{mode} {phase or ""} renders only {experiment_for(mode, phase)}')


def predict_args(inference: dict) -> dict:
    """The exact call _predict makes for the frozen inference settings."""
    return {'conf': inference['min_score'], 'iou': inference['nms_iou'],
            'max_det': inference['max_det'], 'imgsz': inference['imgsz'], 'device': '0',
            'half': False, 'batch': 1}


def suppression(end2end: bool, nms_iou: float) -> str:
    return ('end-to-end one-to-one head: no NMS, the iou argument is inert' if end2end
            else f'class-aware NMS at IoU {nms_iou}')


class JobRejected(Exception):
    """An input that must stop the job rather than be worked around."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def lf(data: bytes) -> bytes:
    return data.replace(b'\r\n', b'\n')


def source_sha256(text: str) -> str:
    """Hash of a source text with only line endings and trailing newlines normalised."""
    return sha256((text.replace('\r\n', '\n').rstrip('\n') + '\n').encode('utf-8'))


def image_paths(tree: dict) -> list[str]:
    if tree.get('truncated') is not False:
        raise JobRejected('the commit tree listing is truncated or malformed')
    return sorted(e['path'] for e in tree['tree'] if e['type'] == 'blob'
                  and any(e['path'].startswith(f'{PREFIX}{s}/images/') for s in SPLIT_DIRS))


def label_path(image: str) -> str:
    return image.replace('/images/', '/labels/', 1).rsplit('.', 1)[0] + '.txt'


def rle(codes: str) -> str:
    """Run-length form of a split string ('tttvx' -> 't3v1x1'), short enough to transcribe;
    the capacity probe failed once on a hand-copied run of 376 't' (KAGGLE-CAPACITY-001 v1)."""
    out, i = [], 0
    while i < len(codes):
        j = i
        while j < len(codes) and codes[j] == codes[i]:
            j += 1
        out.append(f'{codes[i]}{j - i}')
        i = j
    return ''.join(out)


def unrle(text: str) -> str:
    import re
    if not re.fullmatch(r'([a-z][1-9][0-9]*)+', text):
        raise JobRejected('the split encoding is malformed')
    return ''.join(code * int(n) for code, n in re.findall(r'([a-z])([0-9]+)', text))


def select(paths: list[str], split: str) -> dict[str, str]:
    if len(split) != len(paths) or set(split) - set(CODES):
        raise JobRejected('the split string does not cover the corpus image by image')
    return {p: CODES[c] for p, c in zip(paths, split) if CODES[c]}


def digest(lines: list[tuple[str, str, str]]) -> str:
    return sha256(''.join('\t'.join(line) + '\n' for line in sorted(lines)).encode())


def check_blob(path: str, data: bytes, expected_sha1: str) -> None:
    if hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() != expected_sha1:
        raise JobRejected(f'bytes of {path} differ from the commit tree')


def split_string(rows: list[dict]) -> str:
    """Local side: one code per image, in sorted repository-path order."""
    code = {'train': 't', 'valid': 'v', 'test': 'x'}
    ordered = sorted((r['path'].split('/', 1)[1], r['proposed_split']) for r in rows)
    return ''.join(code[s] for _, s in ordered)


def check_bindings(manifest_path: str, manifest_sha: str, trainer_sha: str, job_sha: str,
                   approved: dict) -> None:
    """Local side, before rendering: only the frozen manifest and the approved code."""
    if (manifest_path != approved['manifest_path']
            or manifest_sha != approved['manifest_sha256']):
        raise JobRejected(f'manifest {manifest_path} is not the frozen, recorded manifest')
    if trainer_sha != approved['trainer_sha256']:
        raise JobRejected('trainer source differs from the approved hash')
    if job_sha != approved['job_sha256']:
        raise JobRejected('job source differs from the approved hash')


def authorize(mode: str, amendment: dict, selection: dict | None = None,
              checkpoint: str | None = None) -> None:
    """Local side, before rendering (TASK-05 review round 2 HIGH-01): what the venue amendment
    permits. capacity: non-scientific, allowed while proposed. train: the amendment approved.
    predict: approved, inference explicitly approved, and the checkpoint the one the committed
    EXP-R01 selection record sealed."""
    approved = amendment.get('state') == 'APPROVED'
    if mode == 'capacity':
        if not approved and amendment.get('execution_permitted') != 'non_scientific_probes_only':
            raise JobRejected('the amendment does not permit a non-scientific probe')
    elif mode == 'train':
        if not approved:
            raise JobRejected('training needs the venue amendment APPROVED')
    elif mode == 'predict':
        if not approved or amendment.get('inference_approved') is not True:
            raise JobRejected('inference needs the amendment APPROVED with inference_approved')
        if not selection or not checkpoint or selection.get('selected_sha256') != checkpoint:
            raise JobRejected('the checkpoint is not the one the EXP-R01 selection record sealed')
    else:
        raise JobRejected(f'unknown mode {mode!r}')


def verify_receipt(receipt: dict, expected: dict[str, tuple[str, str, str]],
                   payload_sha256: str, kernel_source: str | None = None) -> None:
    """Local side, after the run. `expected` maps repository path -> (view split, image
    SHA256, LF label SHA256) for the phase's rows of the frozen manifest; `kernel_source`
    is the locally rendered kernel, compared with the source hash taken inside the run."""
    if receipt.get('payload_sha256') != payload_sha256:
        raise JobRejected('the receipt comes from another payload than the rendered one')
    if kernel_source is not None and (
            receipt.get('kernel_source_sha256') != source_sha256(kernel_source)):
        raise JobRejected('the executed kernel source differs from the rendered kernel')
    got = {f['path']: (f['split'], f['image_sha256'], f['label_lf_sha256'])
           for f in receipt['files']}
    if len(got) != len(receipt['files']) or got != expected:
        extra, missing = sorted(set(got) - set(expected)), sorted(set(expected) - set(got))
        changed = sorted(p for p in set(got) & set(expected) if got[p] != expected[p])
        raise JobRejected(f'receipt files differ from the manifest: extra {extra[:3]}, '
                          f'missing {missing[:3]}, changed {changed[:3]}')


def payload_of(kernel_text: str) -> dict:
    """The PAYLOAD embedded in a rendered kernel."""
    import ast
    head = 'PAYLOAD = json.loads('
    for line in kernel_text.splitlines():
        if line.startswith(head) and line.endswith(')'):
            return json.loads(ast.literal_eval(line[len(head):-1]))
    raise JobRejected('the kernel text carries no PAYLOAD')


def verify_prediction_run(receipt: dict, kernel_text: str, config: dict, phase: str,
                          expected: dict[str, tuple[str, str, str]], config_sha256: str,
                          manifest_sha256: str) -> dict:
    """Local side (TASK-05 review HIGH-04): the receipt, the executed source, the embedded
    payload, the sealed checkpoint, the config and manifest by hash, the phase, the frozen
    settings and the runtime suppression evidence must all agree."""
    payload = payload_of(kernel_text)
    if payload.get('config_sha256') != config_sha256:
        raise JobRejected('the run embedded another config than the one given')
    if payload.get('manifest_sha256') != manifest_sha256:
        raise JobRejected('the run embedded another manifest than the one given')
    if payload.get('experiment_id') != EXPERIMENT_OF.get(phase) \
            or receipt.get('experiment_id') != EXPERIMENT_OF.get(phase):
        raise JobRejected(f'the run is not {EXPERIMENT_OF.get(phase)}')
    inference = payload.get('inference', {})
    names = {str(k): v for k, v in (receipt.get('model_names') or {}).items()}
    if receipt.get('end2end') is not M1_END2END or receipt.get('input_contract') != INPUT_CONTRACT \
            or receipt.get('agnostic_nms') is not False or receipt.get('single_cls') is not False \
            or receipt.get('effective_suppression') != suppression(M1_END2END, inference.get('nms_iou')) \
            or names != M1_MODEL_NAMES or receipt.get('predict_args') != predict_args(inference):
        raise JobRejected('the receipt lacks the exact runtime evidence of the frozen M1 call')
    verify_receipt(receipt, expected, sha256(json.dumps(payload, sort_keys=True).encode()),
                   kernel_source=kernel_text)
    if receipt.get('mode') != 'predict' or not receipt.get('predictions_raw_sha256') \
            or not (receipt.get('status') == 'COMPLETE'
                    or receipt.get('stage') in PREDICTIONS_DEFINITIVE):
        raise JobRejected('only a predict run that wrote and hashed its predictions supplies them')
    if payload.get('phase') != phase or receipt.get('phase') != phase:
        raise JobRejected(f'the run is not the {phase} phase')
    checkpoint = config.get('checkpoint_sha256')
    if not checkpoint or {receipt.get('checkpoint_sha256'), payload.get('checkpoint_sha256')} != {checkpoint}:
        raise JobRejected('the run used another checkpoint than the config seals')
    for key in ('min_score', 'nms_iou', 'max_det', 'imgsz'):
        if payload['inference'].get(key) != config.get(key):
            raise JobRejected(f'inference setting {key} differs from the frozen config')
    return {'checkpoint_sha256': checkpoint, 'phase': phase,
            'payload_sha256': receipt['payload_sha256'],
            'kernel_source_sha256': receipt['kernel_source_sha256'],
            'predictions_raw_sha256': receipt.get('predictions_raw_sha256'),
            'inference': payload['inference'], 'config_sha256': config_sha256,
            'manifest_sha256': manifest_sha256, 'end2end': receipt['end2end'],
            'agnostic_nms': False, 'single_cls': False,
            'effective_suppression': receipt['effective_suppression'],
            'input_contract': receipt['input_contract'], 'model_names': names,
            'predict_args': receipt['predict_args'], 'experiment_id': payload['experiment_id'],
            'receipt_status': receipt['status'], 'receipt_stage': receipt['stage'],
            'receipt_error': receipt.get('error')}


def capacity_verdict(epoch_seconds: list[float], setup_seconds: float, epochs: int,
                     safety: float, limit_seconds: float) -> dict:
    """Rule fixed before measuring: the first epoch is warm-up and excluded; the slowest
    remaining epoch is projected over every frozen epoch with the safety factor."""
    per_epoch = max(epoch_seconds[1:])
    projected = setup_seconds + per_epoch * epochs * safety
    return {'rule': 'setup + max(epochs 2..n) * epochs * safety <= limit',
            'epoch_seconds': epoch_seconds, 'per_epoch_seconds': per_epoch,
            'setup_seconds': setup_seconds, 'epochs': epochs, 'safety': safety,
            'projected_seconds': projected, 'limit_seconds': limit_seconds,
            'fits': projected <= limit_seconds}


def canonical(name: str) -> str:
    return re.sub(r'[-_.]+', '-', name).lower()


def dependency_closure(roots, requires) -> set[str]:
    """Installed packages reachable from `roots`; requires(name) gives requirement strings or
    None when the package is absent. Extras are not followed."""
    seen, todo = set(), [canonical(r) for r in roots]
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        for requirement in requires(name) or ():
            if 'extra' in requirement.partition(';')[2]:
                continue
            match = re.match(r'[A-Za-z0-9][A-Za-z0-9._-]*', requirement)
            if match:
                todo.append(canonical(match.group(0)))
    return seen


def pip_check_verdict(exit_code: int, stdout: str, closure: set[str]) -> dict:
    lines = [line for line in stdout.splitlines() if line.strip()]
    blocking = []
    if exit_code == 0:
        blocking = [line for line in lines if line.strip() != PIP_CHECK_OK]
    else:
        for line in lines:
            match = PIP_CHECK_LINE.match(line)
            if not match or canonical(match.group(1)) in closure:
                blocking.append(line)
        if not lines:
            blocking.append(f'pip check exited {exit_code} without output')
    return {'rule': ('exit 0: only empty output or the pip success line; otherwise a line '
                     'blocks if unparsed or if its dependent package is in the closure'),
            'roots': list(PIP_CHECK_ROOTS), 'closure': sorted(closure), 'lines': lines,
            'blocking': blocking}


def retry_allowed(mode: str, receipt: dict | None, platform_status: str,
                  outputs: list[str], logs: list[str]) -> tuple[bool, str]:
    """Whether a failed version may be followed by another one (RETRY_POLICY)."""
    if receipt is None:
        return False, 'no receipt: a termination without a recorded failure is never retried'
    if platform_status != 'ERROR':
        return False, f'platform status {platform_status}: only a platform ERROR is retried'
    if receipt.get('status') != 'FAILED':
        return False, f"receipt status {receipt.get('status')}: only a FAILED receipt is retried"
    if receipt.get('stage') not in RETRY_POLICY['retry_stages'].get(mode, ()):
        return False, f"failed at stage {receipt.get('stage')}, after the model was built"
    produced = [o for o in outputs if o.endswith(MODEL_OUTPUTS)]
    if produced or receipt.get('predictions_raw_sha256'):
        return False, f'model outputs exist: {produced[:3]}'
    if any(re.search(RETRY_POLICY['metric_pattern'], text) for text in logs):
        return False, 'a log line carries metrics'
    return True, 'failed before any model output'


def check_attempt(ledger: list[dict], version: int,
                  previous: tuple[bool, str] | None = None, mode: str | None = None,
                  experiment_id: str | None = None) -> None:
    """Local side, before rendering version `version`: the committed ledger lists every earlier
    version of this same mode and experiment, none is COMPLETE, and the previous one,
    re-derived from its retained files (`previous`), may be retried."""
    if any(entry.get('mode') != mode or entry.get('experiment_id') != experiment_id
           for entry in ledger):
        raise JobRejected('the ledger holds another mode or experiment')
    if not 1 <= version <= RETRY_POLICY['max_versions']:
        raise JobRejected(f"version {version} is outside 1..{RETRY_POLICY['max_versions']}")
    if [entry.get('version') for entry in ledger] != list(range(1, version)):
        raise JobRejected(f'the ledger must list exactly versions 1..{version - 1}')
    if any(entry.get('status') == 'COMPLETE' for entry in ledger):
        raise JobRejected('a COMPLETE version exists; it is definitive')
    if version > 1 and not (ledger[-1].get('retry_allowed') and previous and previous[0]):
        raise JobRejected(f'version {version - 1} may not be retried: '
                          f"{previous[1] if previous else ledger[-1].get('reason')}")


def inventory(out: Path) -> dict[str, str]:
    """SHA256 of every output file except the receipt itself and the live job log."""
    out = Path(out)
    return {p.relative_to(out).as_posix(): sha256(p.read_bytes())
            for p in sorted(out.rglob('*')) if p.is_file()
            and p.name not in ('receipt.json', 'receipt.json.tmp', 'job_log.txt')}


def write_receipt(receipt: dict, out: Path) -> None:
    """Atomic: a cut session leaves the previous complete receipt, never half of one."""
    target = Path(out) / 'receipt.json'
    temporary = target.with_name('receipt.json.tmp')
    temporary.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    os.replace(temporary, target)


def set_stage(receipt: dict, out: Path, stage: str) -> None:
    """Durable at every stage (round-6 N-07): a hard cut leaves status RUNNING at the last
    stage reached, with the inventory of what existed then."""
    receipt.update({'stage': stage, 'status': 'RUNNING', 'inventory': inventory(out)})
    write_receipt(receipt, out)


def run_recorded(receipt: dict, out: Path, body) -> None:
    """Run body(receipt); the receipt is written at the start, at every stage and whatever
    happens at the end, with status, stage, error and the output inventory."""
    set_stage(receipt, out, receipt.get('stage', 'start'))
    try:
        body(receipt)
        receipt['status'] = 'COMPLETE'
    except BaseException as error:
        receipt['status'] = 'FAILED'
        receipt['error'] = ''.join(traceback.format_exception_only(type(error), error)).strip()
        raise
    finally:
        receipt['finished_unix'] = time.time()
        receipt['inventory'] = inventory(out)
        write_receipt(receipt, out)


def render(payload: dict, forbidden: list[str] = (), trainer_source: str | None = None) -> str:
    """The kernel: this file with PAYLOAD filled in and, for training, the trainer as a raw
    string (plain text, so the kernel can be sent to Kaggle without escaping errors; its
    SHA256 travels in the payload and is checked before import)."""
    text = json.dumps(payload, sort_keys=True)
    for item in forbidden:
        if item in text:
            raise JobRejected(f'the payload would carry a path outside its phase: {item}')
    source = Path(__file__).read_text(encoding='utf-8')
    source = source.replace('\nPAYLOAD = None\n', f'\nPAYLOAD = json.loads({text!r})\n', 1)
    if trainer_source is not None:
        if "'''" in trainer_source or '\r' in trainer_source \
                or trainer_source.rstrip('\n').endswith('\\'):
            raise JobRejected('the trainer source cannot be embedded as a raw string')
        source += f"\n\nTRAINER_SOURCE = r'''{trainer_source}'''\n"
    return source + "\n\nif __name__ == '__main__':\n    main(PAYLOAD)\n"


# ---- everything below runs on Kaggle ----

def _own_source() -> tuple[str | None, str]:
    """Kaggle runs a script kernel as one notebook cell; its text is the executed source."""
    try:
        from IPython import get_ipython
        cells = get_ipython().user_ns.get('In') or []
        if cells and 'PAYLOAD = json.loads(' in cells[-1]:
            return cells[-1], 'ipython_cell'
    except Exception:  # noqa: BLE001 - absence is recorded, not fatal
        pass
    main_file = getattr(sys.modules.get('__main__'), '__file__', None)
    if main_file and Path(main_file).is_file():
        return Path(main_file).read_text(encoding='utf-8'), 'main_file'
    return None, 'unavailable'


def _get(url: str, tries: int = 5) -> bytes:
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                return response.read()
        except OSError:
            if attempt == tries - 1:
                raise
            time.sleep(2 ** attempt)


def _run(command: list[str], evidence: Path, name: str) -> dict:
    done = subprocess.run(command, capture_output=True, text=True)
    (evidence / f'{name}.stdout.txt').write_text(done.stdout, encoding='utf-8')
    (evidence / f'{name}.stderr.txt').write_text(done.stderr, encoding='utf-8')
    return {'command': command, 'exit_code': done.returncode,
            'stdout_sha256': sha256(done.stdout.encode()), 'stderr_sha256': sha256(done.stderr.encode())}


def _environment(evidence: Path) -> dict:
    from importlib.metadata import version

    import torch
    probes = {
        'pip_freeze': _run([sys.executable, '-m', 'pip', 'freeze'], evidence, 'pip_freeze'),
        'pip_check': _run([sys.executable, '-m', 'pip', 'check'], evidence, 'pip_check'),
        'pip_config': _run([sys.executable, '-m', 'pip', 'config', 'list'], evidence, 'pip_config'),
        'pip_debug': _run([sys.executable, '-m', 'pip', 'debug', '--verbose'], evidence, 'pip_debug'),
        'nvidia_smi': _run(['nvidia-smi', '--query-gpu=name,driver_version,memory.total',
                            '--format=csv,noheader'], evidence, 'nvidia_smi'),
    }
    from importlib.metadata import PackageNotFoundError, requires

    def installed_requires(name):
        try:
            return requires(name)
        except PackageNotFoundError:
            return None
    verdict = pip_check_verdict(
        probes['pip_check']['exit_code'],
        (evidence / 'pip_check.stdout.txt').read_text(encoding='utf-8'),
        dependency_closure(PIP_CHECK_ROOTS, installed_requires))
    return {'python': sys.version, 'platform': platform.platform(), 'cpu_count': os.cpu_count(),
            'ultralytics': version('ultralytics'), 'torch': torch.__version__,
            'cuda': torch.version.cuda, 'cudnn': torch.backends.cudnn.version(),
            'cuda_available': torch.cuda.is_available(),
            'gpus': [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
            'env': {k: os.environ[k] for k in ENV_WHITELIST if k in os.environ},
            'probes': probes, 'pip_check_verdict': verdict}


def _predict(payload: dict, checkpoint: Path, view: Path, out: Path, receipt: dict) -> None:
    """Raw detections at the frozen settings; the ONLY source of M1 metrics, computed later
    from these bytes (TASK-05 review MEDIUM-02: no second AP from model.val). No threshold
    is applied here. The effective suppression mode is recorded: YOLO26 is end-to-end, so
    the NMS IoU argument is inert when end2end is true (review MEDIUM-04)."""
    from ultralytics import YOLO
    settings = payload['inference']
    model = YOLO(str(checkpoint))
    receipt['model_names'] = {int(k): v for k, v in model.names.items()}
    receipt['end2end'] = bool(getattr(model.model, 'end2end', False))
    receipt['agnostic_nms'] = False
    receipt['single_cls'] = False
    receipt['effective_suppression'] = suppression(receipt['end2end'], settings['nms_iou'])
    receipt['input_contract'] = INPUT_CONTRACT
    receipt['predict_args'] = predict_args(settings)
    lines = []
    for image in sorted((view / 'images' / 'predict').iterdir()):
        result = model.predict(str(image), **receipt['predict_args'], agnostic_nms=False,
                               verbose=False)[0]
        boxes = result.boxes
        lines.append(json.dumps({
            'file': image.name, 'height': int(result.orig_shape[0]),
            'width': int(result.orig_shape[1]),
            'detections': [{'class_id': int(c), 'score': float(s), 'xyxy': [float(v) for v in b]}
                           for b, s, c in zip(boxes.xyxy.tolist(), boxes.conf.tolist(),
                                              boxes.cls.tolist())]}, sort_keys=True))
    raw = out / 'predictions_raw.jsonl'
    raw.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    receipt['predictions_raw_sha256'] = sha256(raw.read_bytes())
    set_stage(receipt, out, 'predictions_written')  # definitive from here (RETRY_POLICY)


def _train(payload: dict, base: Path, view: Path, out: Path, work: Path, receipt: dict) -> None:
    trainer = work / 'train_model1.py'
    trainer.write_bytes(globals()['TRAINER_SOURCE'].encode('utf-8'))
    if sha256(trainer.read_bytes()) != payload['trainer_sha256']:
        raise JobRejected('trainer source differs from the committed file')
    sys.path.insert(0, str(work))
    os.chdir(work)  # the AMP check resolves the base name here, never downloads it
    from ultralytics import settings
    settings.update({name: False for name in payload['integrations_off']})
    import train_model1
    capacity = payload['mode'] == 'capacity'
    config = {**payload['config'], 'base_checkpoint': str(base)}
    for key, value in train_model1.FROZEN.items():
        if config[key] != value and not (capacity and key == 'epochs'):
            raise JobRejected(f'{key} differs from the frozen protocol')
    if receipt['base_sha256'] == train_model1.TRAINED_M1_SHA256:
        raise JobRejected('the base is the trained M1 weight')
    data_yaml = view / 'data.yaml'
    data_yaml.write_text(f"path: {view.as_posix()}\ntrain: images/train\nval: images/val\n"
                         f"nc: 2\nnames: ['Enfermo', 'Saludable']\n", encoding='utf-8')
    evidence = out / 'evidence'
    shutil.copyfile(data_yaml, evidence / 'data.yaml')
    set_stage(receipt, out, 'training')
    if capacity:
        _capacity(train_model1, config, data_yaml, out, receipt)
        return
    receipt['result'] = train_model1.run_training(config, data_yaml, out / 'run', device='0')


def _capacity(train_model1, config: dict, data_yaml: Path, out: Path, receipt: dict) -> None:
    """Non-scientific: time and memory of a few epochs. Validation output is silenced and
    the weights are deleted; nothing measured here may inform any selection."""
    import logging

    import torch
    logging.getLogger('ultralytics').setLevel(logging.ERROR)
    from ultralytics import YOLO
    marks = []
    model = YOLO(config['base_checkpoint'])
    model.add_callback('on_fit_epoch_end', lambda trainer: marks.append(time.time()))
    begun = time.time()
    model.train(data=str(data_yaml), epochs=config['epochs'], patience=config['patience'],
                batch=config['batch'], imgsz=config['imgsz'], seed=config['seed'],
                optimizer=config['optimizer'], device='0', deterministic=True,
                project='/tmp/capacity', name='probe', exist_ok=False, save=True, plots=True,
                workers=config.get('workers', 2), verbose=False)
    seconds = [b - a for a, b in zip([begun] + marks, marks)]
    usage = shutil.disk_usage('/tmp/capacity')
    receipt['capacity'] = {
        **capacity_verdict(seconds, receipt['setup_seconds'], train_model1.FROZEN['epochs'],
                           1.35, 43200),
        'peak_allocated_bytes': torch.cuda.max_memory_allocated(0),
        'peak_reserved_bytes': torch.cuda.max_memory_reserved(0),
        'run_dir_bytes': sum(p.stat().st_size for p in Path('/tmp/capacity').rglob('*')
                             if p.is_file()),
        'disk_free_bytes': usage.free}
    shutil.rmtree('/tmp/capacity')  # weights and metrics discarded


def main(payload: dict) -> None:
    out = Path('/kaggle/working')
    evidence = out / 'evidence'
    evidence.mkdir(parents=True, exist_ok=True)
    # Everything the job and its libraries print goes to job_log.txt, flushed line by line, so a
    # cut session keeps it and the platform log stays short (round-6 N-06/N-07).
    platform_out = sys.stdout
    log = open(out / 'job_log.txt', 'a', encoding='utf-8', buffering=1)
    sys.stdout = sys.stderr = log
    # Ultralytics is imported only after every download, with its config in /tmp/ultralytics_cfg
    # (copied into the evidence) and the same offline switch the local runner sets.
    os.environ['YOLO_CONFIG_DIR'] = '/tmp/ultralytics_cfg'
    source, how = _own_source()
    receipt = {'payload_sha256': sha256(json.dumps(payload, sort_keys=True).encode()),
               'mode': payload['mode'], 'phase': payload.get('phase'),
               'experiment_id': payload.get('experiment_id'), 'started_unix': time.time(),
               'kernel_source_sha256': source_sha256(source) if source else None,
               'kernel_source_method': how, 'stage': 'start',
               'test_evaluated': payload.get('phase') == 'test'}

    def body(receipt):
        attached = sorted(os.listdir('/kaggle/input')) if os.path.isdir('/kaggle/input') else []
        checkpoint = None
        if payload['mode'] != 'predict' and attached:
            raise JobRejected(f'unexpected attached inputs: {attached}')
        if payload['mode'] == 'predict':
            # Only the output of the training kernel may be attached; its checkpoint is the
            # one whose bytes were sealed locally.
            found = sorted(Path('/kaggle/input').rglob('selected.pt'))
            if len(attached) != 1 or len(found) != 1:
                raise JobRejected(f'expected one attached training output, got {attached} {found}')
            checkpoint = found[0]
            receipt['checkpoint_sha256'] = sha256(checkpoint.read_bytes())
            if receipt['checkpoint_sha256'] != payload['checkpoint_sha256']:
                raise JobRejected('attached checkpoint differs from the sealed hash')
        set_stage(receipt, out, 'environment')
        receipt['pip_install'] = _run(
            [sys.executable, '-m', 'pip', 'install', '-q', '--report',
             str(evidence / 'pip_install_report.json'), f"ultralytics=={payload['ultralytics']}"],
            evidence, 'pip_install')
        if receipt['pip_install']['exit_code'] != 0:
            raise JobRejected('pip install failed')
        receipt['environment'] = _environment(evidence)
        if receipt['environment']['ultralytics'] != payload['ultralytics']:
            raise JobRejected('installed Ultralytics differs from the frozen version')
        if receipt['environment']['pip_check_verdict']['blocking']:
            raise JobRejected('pip check conflicts in the pipeline packages: '
                              f"{receipt['environment']['pip_check_verdict']['blocking']}")

        set_stage(receipt, out, 'download')
        repo, commit = payload['repo'], payload['commit']
        tree = json.loads(_get(f'https://api.github.com/repos/{repo}/git/trees/{commit}?recursive=1'))
        blobs = {e['path']: e['sha'] for e in tree['tree'] if e['type'] == 'blob'}
        paths = image_paths(tree)
        if sha256(''.join(p + '\n' for p in paths).encode()) != payload['paths_digest']:
            raise JobRejected('the commit image list differs from the frozen corpus')
        chosen = ({p: 'all' for p in paths} if payload['mode'] == 'probe'
                  else select(paths, unrle(payload['split'])))
        view = Path('/tmp/view')

        def fetch(path):
            raw = f'https://raw.githubusercontent.com/{repo}/{commit}/'
            image, label = _get(raw + path), _get(raw + label_path(path))
            check_blob(path, image, blobs[path])
            check_blob(label_path(path), label, blobs[label_path(path)])
            if payload['mode'] != 'probe':
                for kind, data, name in (('images', image, Path(path).name),
                                         ('labels', lf(label), Path(label_path(path)).name)):
                    target = view / kind / chosen[path] / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
            return path, sha256(image), sha256(lf(label))

        with ThreadPoolExecutor(16) as pool:
            lines = list(pool.map(fetch, sorted(chosen)))
        receipt['files'] = [dict(zip(('path', 'image_sha256', 'label_lf_sha256', 'split'),
                                     (*line, chosen[line[0]]))) for line in lines]
        receipt['files_digest'] = digest(lines)
        if receipt['files_digest'] != payload['files_digest']:
            raise JobRejected('downloaded files differ from the frozen manifest')

        work = Path('/tmp/work')
        work.mkdir(parents=True, exist_ok=True)
        if payload['mode'] == 'predict':
            set_stage(receipt, out, 'predict')
            os.environ['YOLO_OFFLINE'] = 'true'
            _predict(payload, checkpoint, view, out, receipt)
        else:
            set_stage(receipt, out, 'base')
            base = work / Path(payload['base']['url']).name
            base.write_bytes(_get(payload['base']['url']))
            receipt['base_sha256'] = sha256(base.read_bytes())
            if receipt['base_sha256'] != payload['base']['sha256']:
                raise JobRejected('base checkpoint differs from the official digest')
            if payload['mode'] in ('train', 'capacity'):
                # Ultralytics reads YOLO_CONFIG_DIR/Ultralytics (utils.get_user_config_dir).
                font = Path(os.environ['YOLO_CONFIG_DIR']) / 'Ultralytics' / 'Arial.ttf'
                font.parent.mkdir(parents=True, exist_ok=True)
                font.write_bytes(_get(payload['font_url']))
                receipt['font_sha256'] = sha256(font.read_bytes())
                os.environ['YOLO_OFFLINE'] = 'true'
                receipt['setup_seconds'] = time.time() - receipt['started_unix']
                _train(payload, base, view, out, work, receipt)
        settings = Path(os.environ['YOLO_CONFIG_DIR']) / 'Ultralytics' / 'settings.json'
        if settings.is_file():
            shutil.copyfile(settings, evidence / 'ultralytics_settings.json')
        receipt['stage'] = 'done'

    try:
        run_recorded(receipt, out, body)
    finally:
        sys.stdout = sys.stderr = platform_out
        log.close()
        print(json.dumps({k: receipt.get(k) for k in ('experiment_id', 'mode', 'phase', 'status',
                                                      'stage', 'error')}), file=platform_out)


if __name__ == '__main__':
    main(PAYLOAD)
