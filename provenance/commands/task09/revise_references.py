"""TASK-09: rebuild the reference list from the verified TASK-08 entries (APA 7).

Kept: every entry of manuscript/bibliography/references.json that the revised text cites.
Dropped: Van der Heijden 2022 (BLOCKED, unidentifiable), DANE 2023 (retired) and Hati & Singh
2023 (its only citation did not support the claim and was removed in pass 1).
Added: DANE 2024 GEIH bulletin (verified in TASK-08) and Ultralytics 8.4.52, the version
actually used (PyPI upload 2026-05-20). The list is alphabetical, as APA 7 requires.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
from docx_edit import sha  # noqa: E402

DOCX = ROOT / 'manuscript/source/Articulo_Mango_ALBUS_revision.docx'
DROP = {'hati2023', 'jocher_ultralytics'}
EXTRA = {
    'dane2024': ('Departamento Administrativo Nacional de Estadística. (2024). Boletín técnico: '
                 'Principales indicadores del mercado laboral. Diciembre de 2023 (Gran Encuesta '
                 'Integrada de Hogares, GEIH). https://www.dane.gov.co/files/operaciones/GEIH/'
                 'bol-GEIH-dic2023.pdf'),
    'jocher_ultralytics_8452': ('Jocher, G., Qiu, J., & Chaurasia, A. (2026). Ultralytics YOLO '
                                '(Versión 8.4.52) [Software]. GitHub. '
                                'https://github.com/ultralytics/ultralytics'),
}


def main() -> int:
    refs = json.loads((ROOT / 'manuscript/bibliography/references.json').read_text(encoding='utf-8'))
    items = refs if isinstance(refs, list) else refs.get('references', [])
    entries = {r.get('ref_id') or r.get('id'): r.get('apa7') or r.get('apa') for r in items}
    entries = {k: v for k, v in entries.items() if k not in DROP}
    entries.update(EXTRA)
    texts = sorted(entries.values(), key=lambda t: t.casefold())
    before = sha(DOCX)
    d = docx.Document(DOCX)
    old = [p for p in d.paragraphs if p.style.name == 'ALBUS_7.1_References']
    if not old or len(texts) > len(old):
        raise SystemExit(f'{len(texts)} references for {len(old)} template paragraphs')
    for p, text in zip(old, texts):
        runs = p.runs
        runs[0].text = text
        for run in runs[1:]:
            run._element.getparent().remove(run._element)
    for p in old[len(texts):]:
        p._element.getparent().remove(p._element)
    d.save(DOCX)
    log = ROOT / 'manuscript/source/edit_log.json'
    entries_log = json.loads(log.read_text(encoding='utf-8'))
    entries_log.append({'pass': '1-references', 'script': 'provenance/commands/task09/revise_references.py',
                        'before_sha256': before, 'after_sha256': sha(DOCX), 'references': len(texts)})
    log.write_text(json.dumps(entries_log, indent=2) + '\n', encoding='utf-8')
    print(len(texts), 'references')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
