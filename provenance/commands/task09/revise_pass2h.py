"""TASK-09 pass 2h: cite release v1.0.1 of the public repository.

The authors published release v1.0.0 on 2026-09-29 from the pass 2f state, whose manuscript still said
that no person reviewed the visual adjudication. Pass 2g changed that text, so the manuscript must cite the
release that matches it. Release v1.0.1 is a child of the published main, so v1.0.0 is not rewritten.
Only the reference entry and the letter header change.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
import revise_pass2c  # noqa: E402
from docx_edit import replace, sha  # noqa: E402
from revise_letter import LETTER, apply  # noqa: E402

ROOT = revise_pass2c.ROOT
DOCX = revise_pass2c.DOCX
REPO = 'https://github.com/JUNIORRDSR/deteccion-enfermedades-mango-cascada'

EDITS = [(f'revisión (Versión 1.0.0) [Software]. GitHub. {REPO}/releases/tag/v1.0.0',
          f'revisión (Versión 1.0.1) [Software]. GitHub. {REPO}/releases/tag/v1.0.1')]
LETTER_EDITS = {'# Respuesta al dictamen': [('tras la pasada 2g', 'tras la pasada 2h'),
                                            (f'{REPO} (versión 1.0.0)', f'{REPO} (versión 1.0.1)')]}


def main() -> int:
    before = sha(DOCX)
    d = docx.Document(DOCX)
    for old, new in EDITS:
        replace(d, old, new)
    d.save(DOCX)
    docx.Document(DOCX)
    raw = LETTER.read_bytes()
    newline = '\r\n' if b'\r\n' in raw else '\n'
    LETTER.write_bytes(apply(raw.decode('utf-8').replace('\r\n', '\n'), LETTER_EDITS)
                       .replace('\n', newline).encode('utf-8'))
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8'))
    entries.append({'pass': '2h', 'script': 'provenance/commands/task09/revise_pass2h.py',
                    'responds_to': 'release v1.0.0 published from the pass 2f state; cite v1.0.1',
                    'before_sha256': before, 'after_sha256': sha(DOCX)})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(entries[-1], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
