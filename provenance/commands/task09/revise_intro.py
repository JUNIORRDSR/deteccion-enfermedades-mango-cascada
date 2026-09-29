"""TASK-09, ED-16 in the introduction: the cascade classifies EVERY M1 box, not only those
labelled Enfermo (src/cascade/runtime.py; pass 1b corrected section 3.1 and Figure 1 but left
this sentence).
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
from docx_edit import replace, sha  # noqa: E402

DOCX = ROOT / 'manuscript/source/Articulo_Mango_ALBUS_revision.docx'


def main() -> int:
    before = sha(DOCX)
    d = docx.Document(DOCX)
    replace(d, 'emite una clasificación binaria (sano/enfermo), y un segundo clasificador que, para '
               'cada recorte etiquetado como enfermo, determina el tipo específico de patología.',
            'emite una clasificación binaria (Enfermo/Saludable), y un segundo clasificador que '
            'asigna a cada fruto detectado, sea cual sea su clase binaria, una de cinco clases: '
            'cuatro patologías o Saludable.')
    d.save(DOCX)
    docx.Document(DOCX)
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8'))
    entries.append({'pass': 'intro', 'script': 'provenance/commands/task09/revise_intro.py',
                    'before_sha256': before, 'after_sha256': sha(DOCX)})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(entries[-1], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
