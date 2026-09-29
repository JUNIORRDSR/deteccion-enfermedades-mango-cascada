"""TASK-09 pass 1d: swap in Figures 1 and 2 redrawn with label offsets (figures.py).

Same media paths and pixel sizes as pass 1b, so the DOCX extents stay valid.
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
from docx_edit import sha  # noqa: E402
from revise_pass1b import DOCX, FIGURES, replace_media  # noqa: E402


def main() -> int:
    before = sha(DOCX)
    replace_media(DOCX)
    docx.Document(DOCX)  # still opens after the media swap
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8'))
    entries.append({'pass': '1d', 'script': 'provenance/commands/task09/revise_pass1d.py',
                    'before_sha256': before, 'after_sha256': sha(DOCX),
                    'figures': {k: hashlib.sha256(v.read_bytes()).hexdigest()
                                for k, v in FIGURES.items()}})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(entries[-1], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
