"""Self-contained Kaggle job for M1 (PROTOCOL-AMENDMENT-008 v5). Standard library only.

Nothing is uploaded. The corpus is read from the public commit that holds DATA-001; the
job receives a closed payload fixed locally from the frozen manifest:
- the digest of the sorted image-path list, so the commit is the expected corpus;
- one character per image (t train, v valid, x not in this phase), so test images are
  never requested in a training session;
- the digest of every selected (path, image SHA256, label SHA256 with LF line endings);
- the official digest of the base checkpoint and the exact trainer source.
Every downloaded file is also checked against the git blob SHA-1 of the commit tree.
Any mismatch stops the job before a model is built.

`render` writes the script uploaded as the Kaggle kernel: this file with PAYLOAD filled in.
"""

import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PAYLOAD = json.loads('{"base": {"sha256": "9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef", "size": 5544453, "url": "https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26n.pt"}, "commit": "98614804dd967e19a77af9fc58c27364d2e43bc9", "experiment_id": "KAGGLE-PROBE-001", "files_digest": "4470a1c67823118d36add2eeaa28629807a37d117050ee0e1c018371ea59786d", "manifest_sha256": "aabb435227ab432c3a4b8b4fd45a474de2ac2e8114d49da858acc8dcacd283e2", "mode": "probe", "paths_digest": "56a5280554e48e9472e0e235b2b136ae314ee22f3ad52e16d69513cfb002c6a1", "repo": "DANN-MAGE/SemilleroTI-Mangos", "ultralytics": "8.4.52"}')
PREFIX = 'docs/MangosDataset/'
SPLIT_DIRS = ('train', 'valid', 'test')
CODES = {'t': 'train', 'v': 'val', 'x': None}


class JobRejected(Exception):
    """An input that must stop the job rather than be worked around."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def lf(data: bytes) -> bytes:
    return data.replace(b'\r\n', b'\n')


def image_paths(tree: dict) -> list[str]:
    if tree.get('truncated') is not False:
        raise JobRejected('the commit tree listing is truncated or malformed')
    return sorted(e['path'] for e in tree['tree'] if e['type'] == 'blob'
                  and any(e['path'].startswith(f'{PREFIX}{s}/images/') for s in SPLIT_DIRS))


def label_path(image: str) -> str:
    return image.replace('/images/', '/labels/', 1).rsplit('.', 1)[0] + '.txt'


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


def render(payload: dict, forbidden: list[str] = ()) -> str:
    text = json.dumps(payload, sort_keys=True)
    for item in forbidden:
        if item in text:
            raise JobRejected(f'the payload would carry a path outside its phase: {item}')
    source = Path(__file__).read_text(encoding='utf-8')
    source = source.replace('\nPAYLOAD = None\n', f'\nPAYLOAD = json.loads({text!r})\n', 1)
    return source + "\n\nif __name__ == '__main__':\n    main(PAYLOAD)\n"


# ---- everything below runs on Kaggle ----

def _get(url: str, tries: int = 5) -> bytes:
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                return response.read()
        except OSError:
            if attempt == tries - 1:
                raise
            time.sleep(2 ** attempt)


def _environment() -> dict:
    import torch
    import ultralytics
    freeze = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True).stdout
    smi = subprocess.run(['nvidia-smi', '--query-gpu=name,driver_version,memory.total',
                          '--format=csv,noheader'], capture_output=True, text=True).stdout
    return {'python': sys.version, 'platform': platform.platform(), 'cpu_count': os.cpu_count(),
            'ultralytics': ultralytics.__version__, 'torch': torch.__version__,
            'cuda': torch.version.cuda, 'cuda_available': torch.cuda.is_available(),
            'gpus': [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
            'nvidia_smi': smi.strip(), 'pip_freeze_sha256': sha256(freeze.encode()),
            'pip_freeze': freeze}


def main(payload: dict) -> None:
    started = time.time()
    out = Path('/kaggle/working')
    receipt = {'payload_sha256': sha256(json.dumps(payload, sort_keys=True).encode()),
               'mode': payload['mode'], 'started_unix': started}
    attached = sorted(os.listdir('/kaggle/input')) if os.path.isdir('/kaggle/input') else []
    if attached:
        raise JobRejected(f'unexpected attached inputs: {attached}')
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q',
                    f"ultralytics=={payload['ultralytics']}"], check=True)
    receipt['environment'] = _environment()
    if receipt['environment']['ultralytics'] != payload['ultralytics']:
        raise JobRejected('installed Ultralytics differs from the frozen version')

    repo, commit = payload['repo'], payload['commit']
    tree = json.loads(_get(f'https://api.github.com/repos/{repo}/git/trees/{commit}?recursive=1'))
    blobs = {e['path']: e['sha'] for e in tree['tree'] if e['type'] == 'blob'}
    paths = image_paths(tree)
    if sha256(''.join(p + '\n' for p in paths).encode()) != payload['paths_digest']:
        raise JobRejected('the commit image list differs from the frozen corpus')
    chosen = ({p: 'all' for p in paths} if payload['mode'] == 'probe'
              else select(paths, payload['split']))

    view = Path('/tmp/view')

    def fetch(path):
        raw = f'https://raw.githubusercontent.com/{repo}/{commit}/'
        image, label = _get(raw + path), _get(raw + label_path(path))
        check_blob(path, image, blobs[path])
        check_blob(label_path(path), label, blobs[label_path(path)])
        if payload['mode'] == 'train':
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
        (out / 'receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
        raise JobRejected('downloaded files differ from the frozen manifest; see receipt.json')

    work = Path('/tmp/work')
    work.mkdir(parents=True, exist_ok=True)
    base = work / Path(payload['base']['url']).name
    base.write_bytes(_get(payload['base']['url']))
    receipt['base_sha256'] = sha256(base.read_bytes())
    if receipt['base_sha256'] != payload['base']['sha256']:
        raise JobRejected('base checkpoint differs from the official digest')

    if payload['mode'] == 'train':
        trainer = work / 'train_model1.py'
        trainer.write_bytes(payload['trainer_source'].encode('utf-8'))
        if sha256(trainer.read_bytes()) != payload['trainer_sha256']:
            raise JobRejected('trainer source differs from the committed file')
        sys.path.insert(0, str(work))
        os.chdir(work)  # the AMP check resolves the base name here, never downloads it
        from ultralytics import settings
        settings.update({name: False for name in payload['integrations_off']})
        import train_model1
        config = {**payload['config'], 'base_checkpoint': str(base)}
        for key, value in train_model1.FROZEN.items():
            if config[key] != value:
                raise JobRejected(f'{key} differs from the frozen protocol')
        if receipt['base_sha256'] == train_model1.TRAINED_M1_SHA256:
            raise JobRejected('the base is the trained M1 weight')
        (view / 'data.yaml').write_text(
            f"path: {view.as_posix()}\ntrain: images/train\nval: images/val\n"
            f"nc: 2\nnames: ['Enfermo', 'Saludable']\n", encoding='utf-8')
        receipt['result'] = train_model1.run_training(config, view / 'data.yaml',
                                                      out / 'run', device='0')
        receipt['outputs'] = {str(p.relative_to(out)): sha256(p.read_bytes())
                              for p in sorted((out / 'run').rglob('*')) if p.is_file()}
    receipt['test_evaluated'] = False
    receipt['seconds'] = time.time() - started
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in receipt.items() if k not in ('files', 'environment')}, indent=2))


if __name__ == '__main__':
    main(PAYLOAD)
