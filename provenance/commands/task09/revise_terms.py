"""TASK-09, REVIEW-15: one name per partition (entrenamiento / validación / prueba) and Spanish
class names, in the text that does not depend on the new results.

Paragraphs whose numbers change with EXP-R02/EXP-R03 (abstract, 4.1.2-4.1.5, 4.2, the
conclusions' results) are rewritten whole in pass 2c and are not touched here. The source
corpus's own English class names stay once, in section 3.1, next to their translation.
The MangoDHDS_clean counts come from the frozen M2 manifest, never typed by hand.
"""

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
from docx_edit import cell_text, replace, set_runs, sha  # noqa: E402

DOCX = ROOT / 'manuscript/source/Articulo_Mango_ALBUS_revision.docx'
M2_MANIFEST = ROOT / 'data/manifests/model2_frozen_manifest.csv'


def m2_counts() -> dict:
    rows = list(csv.DictReader(open(M2_MANIFEST, encoding='utf-8')))
    split = collections.Counter(r['split'] for r in rows)
    test = collections.Counter(r['class_name'] for r in rows if r['split'] == 'test')
    clusters = len({r['cluster_id'] for r in rows})
    return {'total': len(rows), 'train': split['train'], 'val': split['val'],
            'test': split['test'], 'clusters': clusters, 'consolidated': len(rows) - clusters,
            'test_min': min(test.values()), 'test_max': max(test.values())}


def main() -> int:
    before = sha(DOCX)
    c = m2_counts()
    d = docx.Document(DOCX)
    for old, new in (
        ('instancias Enfermo del test publicado', 'instancias Enfermo de la partición de prueba publicada'),
        ('(1125 train + 300 valid + 75 test)', '(1125 de entrenamiento, 300 de validación y 75 de prueba)'),
        ('Entrenar y evaluar sobre tal split', 'Entrenar y evaluar sobre esa partición'),
        ('de los tres splits originales', 'de las tres particiones originales'),
        ('Pares casi-duplicados detectados entre splits originales del corpus de clasificación, '
         'con perceptual hashing y umbral Hamming < 5.',
         'Pares casi duplicados entre las particiones originales del corpus de clasificación, '
         'detectados con hash perceptual y umbral de Hamming < 5.'),
        ('(top-1 val = 0.935)', '(exactitud top-1 en validación = 0.935)'),
        ('que hayan usado el split original', 'que hayan usado la partición original'),
        ('(76 pares casi-duplicados cross-split)', '(76 pares casi duplicados entre particiones)'),
        ('basado en perceptual hashing y union-find que regenera el dataset',
         'basado en hash perceptual y union-find que regenera el conjunto'),
        ('un conjunto de test externo anotado', 'un conjunto de prueba externo anotado'),
    ):
        replace(d, old, new)
    set_runs(d, 'El 79% de los pares (60/76)', [
        ('El 79 % de los pares (60/76) tiene distancia de Hamming exactamente 0: son imágenes '
         'perceptualmente idénticas guardadas con nombres distintos. Los pares se concentran en ', ''),
        ('Saludable', 'i'), (' (31) y ', ''), ('Antracnosis', 'i'),
        (' (25), las dos clases con más tomas repetidas. Tras aplicar el protocolo de '
         'regeneración, la verificación sobre MangoDHDS_clean no encuentra pares entre '
         f"particiones (umbral τ = 5). El conjunto limpio tiene {c['train']} imágenes de "
         f"entrenamiento, {c['val']} de validación y {c['test']} de prueba ({c['total']} en total, "
         f"sin descartar ninguna), agrupadas en {c['clusters']} clusters atómicos "
         f"({c['consolidated']} imágenes consolidadas en grupos de casi duplicados). La "
         'estratificación por clase mantiene el balance: la partición de prueba tiene entre '
         f"{c['test_min']} y {c['test_max']} imágenes por clase.", '')])
    labels = [row.cells[0].text for row in d.tables[1].rows]
    cell_text(d, 1, labels.index('Tarea'), 1, 'Detección (cajas + clasificación binaria)')
    for row, text in enumerate(('Particiones comparadas', 'entrenamiento ↔ validación',
                                'entrenamiento ↔ prueba', 'validación ↔ prueba')):
        cell_text(d, 5, row, 0, text)
    limits = [row.cells[0].text for row in d.tables[7].rows]
    row = limits.index('Sin test OOD externo')
    cell_text(d, 7, row, 0, 'Sin prueba externa fuera de distribución')
    cell_text(d, 7, row, 2, 'Conjunto de prueba externo anotado de forma independiente')
    d.save(DOCX)
    docx.Document(DOCX)
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8'))
    entries.append({'pass': 'terms', 'script': 'provenance/commands/task09/revise_terms.py',
                    'before_sha256': before, 'after_sha256': sha(DOCX), 'm2_counts': c,
                    'm2_manifest_sha256': sha(M2_MANIFEST)})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(entries[-1], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
