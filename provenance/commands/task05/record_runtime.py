"""TASK-05 rounds 11-12: write the two records of the approved .venv, both authorities of the
inference snapshots:

- provenance/environment/inference_runtime.txt, the table of RECORD SHA256 per installed
  distribution (authority.runtime_table), computed after every installed file, cache and
  unrecorded code file of the .venv has been verified; check_runtime compares it on every run;
- provenance/environment/inference_interpreter.json, the base interpreter the .venv was made
  from (its root and sys.version), read from the .venv's pyvenv.cfg and this clean process;
  check_interpreter compares sys.base_prefix, pyvenv.cfg and sys.path with it on every run.

Run in a fresh process of the approved .venv with no startup override.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.evaluation import authority  # noqa: E402

if __name__ == '__main__':
    authority.check_startup()
    config = (ROOT / '.venv' / 'pyvenv.cfg').read_text(encoding='utf-8').splitlines()
    home = [line.split('=', 1)[1].strip() for line in config if line.split('=', 1)[0].strip() == 'home']
    if [authority._key(h) for h in home] != [authority._key(sys.base_prefix)]:
        raise SystemExit(f'pyvenv.cfg home {home} is not sys.base_prefix {sys.base_prefix}')
    interpreter = {'base_prefix': home[0], 'version': sys.version}
    (ROOT / authority.INTERPRETER_RECORD).write_text(json.dumps(interpreter, indent=2) + '\n',
                                                     encoding='utf-8', newline='\n')
    table = authority.runtime_table()
    (ROOT / authority.RUNTIME_RECORD).write_text(table, encoding='utf-8', newline='\n')
    print(len(table.splitlines()), 'distributions; runtime identity', authority.runtime_identity())
    print(json.dumps(interpreter))
