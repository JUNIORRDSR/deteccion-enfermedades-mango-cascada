"""TASK-10: the legacy repositories' git state against provenance/repository_initial_state.md
(reports/legacy_git_final.json).

Runs, read only (GIT_OPTIONAL_LOCKS=0), every git command the initial record lists for
Mango-vision and SemilleroTI-Mangos, resolved from legacy_corpus in configs/root_mapping.json, and
compares the output byte for byte with the recorded one, as verify_first_phase.py does.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.evaluation.provenance import authorized_root, check_output  # noqa: E402

REPOS = ('Mango-vision', 'SemilleroTI-Mangos')


def main() -> int:
    root = authorized_root()
    out = check_output(root, root / 'reports/legacy_git_final.json')
    legacy = Path(json.loads((ROOT / 'configs/root_mapping.json').read_text(encoding='utf-8'))
                  ['legacy_corpus'])
    initial = (ROOT / 'provenance/repository_initial_state.md').read_text(encoding='utf-8')
    env = {**os.environ, 'GIT_OPTIONAL_LOCKS': '0'}
    checks = []
    for name in REPOS:
        section = initial.split('## ' + str(legacy / name) + '\n')[1].split('\n## ')[0]
        for command in re.findall(r'### git ([^\n]+)', section):
            body = section.split('### git ' + command + '\n')[1].split('\n### ')[0]
            recorded = re.search(r'```text\n([\s\S]*?)```', body)
            proc = subprocess.run(['git', '-C', str(legacy / name), *command.split()],
                                  capture_output=True, text=True, encoding='utf-8',
                                  errors='replace', env=env)
            checks.append({'repo': name, 'command': 'git ' + command, 'exit_code': proc.returncode,
                           'matches_initial': bool(recorded) and proc.returncode == 0
                           and proc.stdout == recorded.group(1)})
    report = {'task': 'TASK-10 legacy git state', 'checks': checks,
              'passed': bool(checks) and all(c['matches_initial'] for c in checks)}
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f"{sum(c['matches_initial'] for c in checks)}/{len(checks)} match the initial record")
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
