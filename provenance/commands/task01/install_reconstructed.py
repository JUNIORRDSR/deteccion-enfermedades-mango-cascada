"""Capture a reconstructed environment; never persist unsanitized pip output."""

import csv
import ctypes
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from src.evaluation.provenance import (authorized_root, check_output,
                                       configure_environment, redact_url,
                                       sanitize_obj, sanitize_text)


# Finding 2 round 2: this script trusted the current directory and wrote under it
# without any containment check, so running it elsewhere was an external-write path.
ROOT = authorized_root()
OUT = check_output(ROOT, ROOT / 'provenance/environment')
OUT.mkdir(parents=True, exist_ok=True)
WHITELIST = configure_environment(ROOT)
PINS = ('ultralytics==8.4.52', 'torch==2.12.0', 'torchvision==0.27.0',
        'numpy==2.4.4', 'Pillow==12.2.0', 'ImageHash==4.3.2',
        'scikit-learn==1.8.0')
COMMANDS = []


def run(label, args):
    completed = subprocess.run(args, cwd=ROOT, text=True, encoding='utf-8',
                               errors='replace', stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, check=False)
    output = sanitize_text(completed.stdout)
    (OUT / f'{label}.txt').write_text(output + f'\nexit_code={completed.returncode}\n', encoding='utf-8')
    COMMANDS.append({'label': label, 'command': sanitize_text(' '.join(map(str, args))),
                     'exit_code': completed.returncode, 'log': f'{label}.txt'})
    return completed.returncode, output


def scrub(value):
    if isinstance(value, dict):
        return {key: scrub(item) for key, item in value.items()}
    if isinstance(value, list):
        return [scrub(item) for item in value]
    if isinstance(value, str):
        return sanitize_text(value)
    return value


code, python_version = run('python_version', [sys.executable, '--version'])
code, pip_version = run('pip_version', [sys.executable, '-m', 'pip', '--version'])
run('pip_config_debug_redacted', [sys.executable, '-m', 'pip', 'config', 'debug'])
run('pip_config_list_redacted', [sys.executable, '-m', 'pip', 'config', 'list'])
indices = {}
for name in ('PIP_INDEX_URL', 'PIP_EXTRA_INDEX_URL', 'PIP_FIND_LINKS', 'PIP_NO_INDEX'):
    value = os.environ.get(name)
    if value:
        indices[name] = sanitize_text(value)

raw_report = None
try:
    with tempfile.NamedTemporaryFile(prefix='pip-report-', suffix='.json',
                                     dir=ROOT / 'provenance/runtime_state/tmp',
                                     delete=False) as stream:
        raw_report = Path(stream.name)
    install_code, _ = run('pip_install_redacted', [sys.executable, '-m', 'pip', 'install',
                                '--report', str(raw_report), *PINS])
    if raw_report.exists() and raw_report.stat().st_size:
        report = sanitize_obj(json.loads(raw_report.read_text(encoding='utf-8')))
        (OUT / 'install_report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    else:
        report = {'install': [], 'status': 'UNAVAILABLE', 'reason': f'pip install exit {install_code}'}
        (OUT / 'install_report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
finally:
    if raw_report is not None:
        raw_report.unlink(missing_ok=True)

pip_check_code, _ = run('pip_check', [sys.executable, '-m', 'pip', 'check'])
code, packages_text = run('pip_list', [sys.executable, '-m', 'pip', 'list', '--format=json'])
packages = json.loads(packages_text) if code == 0 else []
(OUT / 'packages.json').write_text(json.dumps(packages, indent=2) + '\n', encoding='utf-8')
code, freeze = run('pip_freeze', [sys.executable, '-m', 'pip', 'freeze', '--all'])
(OUT / 'reconstructed_freeze.txt').write_text(freeze, encoding='utf-8')

installed = {item['metadata']['name'].lower().replace('_', '-'): item for item in report.get('install', [])}
with (OUT / 'package_artifacts.csv').open('w', encoding='utf-8', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=['distribution', 'version', 'filename', 'build',
                                                  'origin_redacted', 'sha256', 'status', 'reason'])
    writer.writeheader()
    for package in packages:
        name = package['name']
        item = installed.get(name.lower().replace('_', '-'), {})
        info = item.get('download_info', {})
        url = info.get('url', '')
        filename = Path(urlsplit(url).path).name if url else ''
        hashes = info.get('archive_info', {}).get('hashes', {})
        digest = hashes.get('sha256', '')
        writer.writerow({'distribution': name, 'version': package['version'],
                         'filename': filename or 'UNRECOVERED', 'build': 'UNRECOVERED',
                         'origin_redacted': redact_url(url) if url else 'UNRECOVERED',
                         'sha256': digest or 'UNRECOVERED',
                         'status': 'ARCHIVE_SHA256_RECORDED' if digest else 'BINARY_IDENTITY_UNRECOVERED',
                         'reason': '' if digest else ('already installed / no pip download record' if not item
                                                    else 'pip report lacks archive SHA256')})

class MEMORYSTATUS(ctypes.Structure):
    _fields_ = [('length', ctypes.c_uint32), ('memory_load', ctypes.c_uint32),
                ('total_physical', ctypes.c_uint64), ('available_physical', ctypes.c_uint64),
                ('total_page', ctypes.c_uint64), ('available_page', ctypes.c_uint64),
                ('total_virtual', ctypes.c_uint64), ('available_virtual', ctypes.c_uint64),
                ('available_extended_virtual', ctypes.c_uint64)]


memory = MEMORYSTATUS()
memory.length = ctypes.sizeof(MEMORYSTATUS)
ram = memory.total_physical if os.name == 'nt' and ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)) else None
gpu_code, gpu = run('gpu_inventory', ['powershell', '-NoProfile', '-Command',
    'Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion | ConvertTo-Json -Compress'])
cuda_code, cuda = run('nvidia_smi', ['nvidia-smi', '--query-gpu=name,driver_version,compute_cap', '--format=csv,noheader']) if __import__('shutil').which('nvidia-smi') else (127, 'nvidia-smi unavailable')
hardware = {'os': platform.platform(), 'os_build': platform.version(),
            'cpu': platform.processor(), 'cpu_count': os.cpu_count(), 'ram_bytes': ram,
            'gpu_inventory': gpu.strip() if gpu_code == 0 else 'UNAVAILABLE',
            'gpu_inventory_exit_code': gpu_code,
            'nvidia_gpu_driver': cuda.strip() if cuda_code == 0 else 'NVIDIA GPU/driver unavailable',
            'cuda_runtime': 'NOT_PROBED_WITH_TORCH', 'nvidia_smi_exit_code': cuda_code}
(OUT / 'hardware.json').write_text(json.dumps(hardware, indent=2) + '\n', encoding='utf-8')
relevant = sanitize_obj({name: value for name, value in os.environ.items()
            if name in WHITELIST or name.startswith(('CUDA_', 'OMP_', 'MKL_', 'OPENBLAS_', 'PIP_'))
            or name in ('PYTHONDONTWRITEBYTECODE', 'PYTHONNOUSERSITE', 'WANDB_DISABLED',
                        'WANDB_MODE', 'COMET_MODE')})
(OUT / 'environment_whitelist.json').write_text(json.dumps(relevant, indent=2) + '\n', encoding='utf-8')
identity = {'kind': 'RECONSTRUCTED', 'python_version': python_version.strip(),
            'python_executable': sys.executable, 'pip_version': pip_version.strip(),
            'requested_pins': PINS, 'historical_model1_ultralytics': '8.4.39',
            'reconstructed_ultralytics': '8.4.52', 'effective_index_environment': indices,
            'pip_cli_index_options': [], 'commands': COMMANDS,
            'pip_check_exit_code': pip_check_code, 'scientific_use_allowed': install_code == 0 and pip_check_code == 0}
(OUT / 'identity.json').write_text(json.dumps(identity, indent=2) + '\n', encoding='utf-8')
print(f'install_exit={install_code} pip_check_exit={pip_check_code} packages={len(packages)}')
if install_code or pip_check_code:
    raise SystemExit(2)
