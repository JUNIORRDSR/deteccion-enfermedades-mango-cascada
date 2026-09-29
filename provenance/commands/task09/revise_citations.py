"""TASK-09, REVIEW-16: cite the Intel D400 datasheet where the text states the D435's stereo
RGB-D capability. Its only citation went with CLAIM-007 in pass 1, leaving the entry uncited;
check_citations.py must then report no gap in either direction.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
from docx_edit import replace, sha  # noqa: E402

DOCX = ROOT / 'manuscript/source/Articulo_Mango_ALBUS_revision.docx'


def main() -> int:
    before, original = sha(DOCX), DOCX.read_bytes()
    d = docx.Document(DOCX)
    replace(d, 'Intel RealSense D435 con capacidad RGB-D estéreo,',
            'Intel RealSense D435 con capacidad RGB-D estéreo (Intel Corporation, 2022),')
    d.save(DOCX)
    check = subprocess.run([sys.executable, str(ROOT / 'provenance/commands/task09/check_citations.py')],
                           capture_output=True, text=True)
    print(check.stdout)
    if check.returncode:
        DOCX.write_bytes(original)
        raise SystemExit('citation gaps remain; DOCX restored')
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8'))
    entries.append({'pass': 'citations', 'script': 'provenance/commands/task09/revise_citations.py',
                    'before_sha256': before, 'after_sha256': sha(DOCX),
                    'check': check.stdout.strip().splitlines()})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
