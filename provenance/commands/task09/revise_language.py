"""TASK-09, REVIEW-10 / ED-04 and ED-14: language that does not depend on the new results.

ED-04: the uncited «variantes cada vez más eficientes» of section 2.2.

Redmon et al. (2016) supports only single-pass detection with a unified architecture
(reports/citation_links.csv, PARTIAL), not an evolution towards efficiency; the sentence now
states what each citation supports, and names the version used here.
ED-14: «libre de fuga» in the conclusion becomes the wording of ED-09.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
from docx_edit import replace, set_paragraph, sha  # noqa: E402

DOCX = ROOT / 'manuscript/source/Articulo_Mango_ALBUS_revision.docx'


def main() -> int:
    before = sha(DOCX)
    d = docx.Document(DOCX)
    set_paragraph(d, 'La familia YOLO ha evolucionado desde la propuesta original',
                  'YOLO detecta en una única pasada, con una arquitectura unificada, lo que permite '
                  'inferencia en tiempo real (Redmon et al., 2016). Desde entonces la familia ha '
                  'tenido numerosas versiones; este trabajo usa YOLO26 (Jocher et al., 2026).')
    # ED-14: the conclusion states what the protocol found, not an absolute absence of leakage.
    replace(d, 'que regenera el conjunto con estratificación por clase libre de fuga.',
            'que regenera el conjunto con estratificación por clase, sin contaminación entre '
            'particiones detectada bajo el protocolo especificado (SHA-256, pHash con distancia de '
            'Hamming < 5 y agrupamiento por cluster).')
    d.save(DOCX)
    docx.Document(DOCX)
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8'))
    entries.append({'pass': 'language', 'script': 'provenance/commands/task09/revise_language.py',
                    'before_sha256': before, 'after_sha256': sha(DOCX)})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(entries[-1], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
