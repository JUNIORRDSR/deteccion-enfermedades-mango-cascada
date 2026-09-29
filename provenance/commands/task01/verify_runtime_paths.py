"""Prove Ultralytics writes only inside the workspace, without ever writing outside it.

Rewritten after finding 3 HIGH of the independent adversarial review. The first
version demonstrated the unguarded-import hazard by TRIGGERING it, so it created
`%APPDATA%/Ultralytics/settings.json` outside the authorized checkout and still
reported PASS. That escape is preserved as INCIDENT-001.

This version never imports a scientific runtime into an uncontrolled profile.
The unguarded case redirects the whole child profile (`USERPROFILE`, `HOME`,
`APPDATA`, `XDG_CONFIG_HOME`, ...) into a workspace fixture, so the documented
fallback in `ultralytics.utils.get_user_config_dir` lands inside the checkout
and is observable without touching the real user profile. Any resolved path
outside the workspace is a FAILURE in every mode, never an expectation.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.evaluation.provenance import (  # noqa: E402
    ISOLATION_VALUES, STATE_DIRS, ULTRALYTICS_OFF, check_output,
    configure_environment, verify_environment,
)

PROFILE_VARS = ('USERPROFILE', 'HOME', 'HOMEDRIVE', 'HOMEPATH', 'APPDATA',
                'LOCALAPPDATA', 'XDG_CONFIG_HOME')

# The workspace lives under the user profile, so the home directory is NOT a useful
# exclusion. What must never be touched are the real config locations and the
# ultralytics /tmp fallback.
# Without the guard, Ultralytics picks its own locations: datasets_dir lands
# OUTSIDE the checkout entirely, and weights_dir and runs_dir land inside the
# checkout but outside any declared output subtree. All three are the hazard
# being demonstrated. Naming them individually is the point: an escape that is
# not on this list fails the gate (finding N1).
EXPECTED_HAZARD_KEYS = {'datasets_dir', 'weights_dir', 'runs_dir'}

FORBIDDEN_SINKS = tuple(str(Path(value)) for value in (
    os.environ.get('APPDATA', ''), os.environ.get('LOCALAPPDATA', ''),
    'C:/tmp') if value)

CHILD = r'''
import json, os, sys
from pathlib import Path
root = Path(sys.argv[1]); mode = sys.argv[2]
sys.path.insert(0, str(root))
from src.evaluation.provenance import (configure_environment, verify_environment,
                                       check_output, lock_ultralytics, ULTRALYTICS_OFF)

if mode == 'missing':
    os.environ.pop('YOLO_CONFIG_DIR', None)
    try:
        verify_environment(root)
    except ValueError as error:
        print(json.dumps({'refused_before_import': str(error)})); sys.exit(0)
    print(json.dumps({'refused_before_import': None})); sys.exit(1)

if mode == 'external':
    os.environ['YOLO_CONFIG_DIR'] = os.environ['EXTERNAL_PROBE']
    try:
        configure_environment(root)
    except ValueError as error:
        print(json.dumps({'refused_external': str(error)})); sys.exit(0)
    print(json.dumps({'refused_external': None})); sys.exit(1)

if mode == 'guarded':
    configure_environment(root)
    verify_environment(root)
    # The import-time probe runs before settings can be locked, so the offline
    # intent has to be expressed as environment before importing anything.
    os.environ['YOLO_OFFLINE'] = 'true'
elif mode == 'unguarded_sandboxed_profile':
    os.environ.pop('YOLO_CONFIG_DIR', None)
else:
    print(json.dumps({'error': 'unknown mode ' + mode})); sys.exit(1)

assert 'ultralytics' not in sys.modules
from ultralytics import SETTINGS, __version__
from ultralytics.utils import ONLINE, USER_CONFIG_DIR
import torch

applied = lock_ultralytics(SETTINGS, root) if mode == 'guarded' else {}
paths = {key: str(SETTINGS[key]) for key in ('datasets_dir', 'weights_dir', 'runs_dir')}
paths['settings_file'] = str(SETTINGS.file)
paths['user_config_dir'] = str(USER_CONFIG_DIR)
escaped = {}
for key, value in paths.items():
    try:
        check_output(root, Path(value))
    except ValueError as error:
        escaped[key] = str(error)
print(json.dumps({
    'ultralytics': __version__, 'torch': torch.__version__,
    'torch_cuda_available': torch.cuda.is_available(),
    'torch_cuda_version': torch.version.cuda,
    'ultralytics_online_probe_at_import': bool(ONLINE),
    'effective_paths': paths, 'escaped': escaped,
    'integrations': {name: SETTINGS.get(name) for name in ULTRALYTICS_OFF},
    'lockdown_applied': applied,
    'profile_home': str(Path.home()),
}))
'''


def child(mode: str, sandbox_profile: bool) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in STATE_DIRS}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['EXTERNAL_PROBE'] = str(Path(os.environ.get('SystemRoot', 'C:/Windows')) / 'Temp')
    fixture = None
    if sandbox_profile:
        fixture = check_output(ROOT, ROOT / 'provenance' / 'runtime_state' / 'profile_fixture' / mode)
        fixture.mkdir(parents=True, exist_ok=True)
        for name in PROFILE_VARS:
            env.pop(name, None)
        env['USERPROFILE'] = str(fixture)
        env['HOME'] = str(fixture)
        env['HOMEDRIVE'] = str(fixture.drive)
        env['HOMEPATH'] = str(fixture)[len(fixture.drive):]
        env['APPDATA'] = str(fixture / 'AppData' / 'Roaming')
        env['LOCALAPPDATA'] = str(fixture / 'AppData' / 'Local')
        env['XDG_CONFIG_HOME'] = str(fixture / '.config')
        # The fallback only lands here if the parent already exists and is writeable;
        # otherwise ultralytics drops to /tmp, which is another external write.
        for relative in ('AppData/Roaming', 'AppData/Local', '.config'):
            (fixture / relative).mkdir(parents=True, exist_ok=True)
    done = subprocess.run([sys.executable, '-c', CHILD, str(ROOT), mode],
                          capture_output=True, text=True, env=env, cwd=str(ROOT))
    return {'mode': mode, 'sandboxed_profile': sandbox_profile,
            'profile_fixture': str(fixture) if fixture else None,
            'exit_code': done.returncode, 'stdout': done.stdout.strip(),
            'stderr': done.stderr.strip()[-2000:]}


def main() -> int:
    configure_environment(ROOT)
    verify_environment(ROOT)
    results = [child('missing', False), child('external', False),
               child('guarded', False), child('unguarded_sandboxed_profile', True)]
    failures: list[str] = []
    for result in results:
        if result['exit_code'] != 0:
            failures.append(f"{result['mode']}: exit {result['exit_code']}")
            continue
        payload_lines = [line for line in result['stdout'].splitlines() if line.startswith('{')]
        if not payload_lines:
            failures.append(f"{result['mode']}: no JSON payload")
            continue
        payload = json.loads(payload_lines[-1])
        result['parsed'] = payload
        if result['mode'] in ('missing', 'external'):
            if not any(payload.values()):
                failures.append(f"{result['mode']}: accepted an unsafe configuration")
            continue
        if result['mode'] == 'guarded':
            # Finding 3 HIGH: in the guarded mode nothing may leave the checkout.
            if payload['escaped']:
                failures.append(f"guarded: paths escape the workspace {payload['escaped']}")
            # Finding 7 MEDIUM: every remote integration must be off, not only sync.
            enabled = [name for name, value in payload['integrations'].items() if value]
            if enabled:
                failures.append(f"guarded: remote integrations still enabled {enabled}")
        else:
            # The unguarded case is a NEGATIVE test observed inside a profile fixture,
            # so the real user profile is never written. Escapes here are the expected
            # hazard, but every one must be named in EXPECTED_HAZARD_KEYS; an
            # unexplained escape fails the gate. The previous version silently ignored
            # payload['escaped'] in this mode and still printed PASS (finding N1).
            fixture = str(result['profile_fixture'])
            unexplained = sorted(set(payload['escaped']) - EXPECTED_HAZARD_KEYS)
            if unexplained:
                failures.append(f'unguarded: unexplained escaped paths {unexplained}; '
                                'the containment contract must be re-derived')
            result['expected_hazard_escapes'] = payload['escaped']
            for key in ('user_config_dir', 'settings_file'):
                if fixture not in payload['effective_paths'][key]:
                    failures.append(f"unguarded: {key} went to "
                                    f"{payload['effective_paths'][key]} instead of the fixture; "
                                    'an external writer is unaccounted for')
            for key, value in payload['effective_paths'].items():
                for sink in FORBIDDEN_SINKS:
                    if str(value).lower().startswith(sink.lower()):
                        failures.append(f"unguarded: {key} reached a forbidden sink {value}")
    guarded = next((r.get('parsed', {}) for r in results if r['mode'] == 'guarded'), {})
    unguarded = next((r for r in results if r['mode'] == 'unguarded_sandboxed_profile'), {})
    report = {'root': str(ROOT), 'executable': sys.executable,
              'containment_claim': {
                  'guarded_escaped_paths': guarded.get('escaped', 'NOT_RUN'),
                  'unguarded_expected_hazard_escapes': unguarded.get('expected_hazard_escapes', {}),
                  'note': ('PASS means the GUARDED entrypoint is contained and the negative test '
                           'produced only expected hazards inside the fixture. It does NOT mean '
                           'no path anywhere escaped.')},
              'isolation_values': ISOLATION_VALUES,
              'integrations_required_off': list(ULTRALYTICS_OFF),
              'supersedes': 'first version of this script, which caused INCIDENT-001',
              'results': results, 'failures': failures,
              'status': 'PASS' if not failures else 'FAIL'}
    out = check_output(ROOT, ROOT / 'provenance' / 'environment' / 'runtime_path_report.json')
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'failures': failures, 'report': str(out)}, indent=2))
    return 0 if not failures else 2


if __name__ == '__main__':
    sys.exit(main())
