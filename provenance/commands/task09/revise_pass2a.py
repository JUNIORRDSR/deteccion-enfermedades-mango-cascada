"""TASK-09 pass 2a: what no longer depends on results (REVIEW-01, REVIEW-02, REVIEW-04).

The frozen M1 partition goes into Table 1 with its groups (reports/model1_split_proposal.md,
accepted by reports/amendments/gate-review-exp-r01.md part B); section 3.3 becomes the leakage
audit of both corpora, with the new M1 audit as 3.3.1 and the MangoDHDS text as 3.3.2, so no
later heading or cross-reference is renumbered; and the paragraph split inherited from the
original copy ("El conjunto resultante" / "(MangoDHDS_clean) ...") is joined.
Counts come from the committed manifest, never typed by hand.
"""

import copy
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx_edit import (  # noqa: E402
    cell_text, delete_paragraph, insert_after, replace, set_runs, sha,
)

DOCX = ROOT / 'manuscript/source/Articulo_Mango_ALBUS_revision.docx'
MANIFEST = ROOT / 'data/manifests/model1_clean_manifest.csv'
LEGACY = Path(json.loads((ROOT / 'configs/root_mapping.json').read_text(encoding='utf-8'))
              ['legacy_corpus'])
SPLITS = (('train', 'Entrenamiento'), ('valid', 'Validación'), ('test', 'Prueba'))


def counts() -> dict:
    """Images, groups and label instances per split, and groups holding Enfermo (class 0)."""
    rows = list(csv.DictReader(open(MANIFEST, encoding='utf-8')))
    out = {}
    for split, _ in SPLITS:
        chosen = [r for r in rows if r['proposed_split'] == split]
        classes, enfermo_groups = Counter(), set()
        for r in chosen:
            for line in (LEGACY / r['label']).read_text(encoding='utf-8').splitlines():
                if line.strip():
                    cls = int(line.split()[0])
                    classes[cls] += 1
                    if cls == 0:
                        enfermo_groups.add(r['group_id'])
        out[split] = {'images': len(chosen), 'groups': len({r['group_id'] for r in chosen}),
                      'enfermo': classes[0], 'saludable': classes[1],
                      'enfermo_groups': len(enfermo_groups)}
    out['total'] = {k: sum(out[s][k] for s, _ in SPLITS)
                    for k in ('images', 'groups', 'enfermo', 'saludable')}
    return out


def add_last_column(table, texts: list[str]) -> None:
    """Copy the last column (grid and cell formatting) and fill it."""
    grid = table._tbl.tblGrid
    grid.append(copy.deepcopy(grid.findall(qn('w:gridCol'))[-1]))
    for row, text in zip(table.rows, texts):
        tc = copy.deepcopy(row._tr.findall(qn('w:tc'))[-1])
        row._tr.append(tc)
    for i, text in enumerate(texts):
        cell_text_last(table, i, text)


def cell_text_last(table, row: int, text: str) -> None:
    cells = table.rows[row]._tr.findall(qn('w:tc'))
    paragraph = docx.table._Cell(cells[-1], table).paragraphs[0]
    runs = paragraph.runs
    runs[0].text = text
    for run in runs[1:]:
        run._element.getparent().remove(run._element)


def main() -> int:
    before = sha(DOCX)
    c = counts()
    expected = {'train': (439, 8), 'valid': (113, 93), 'test': (117, 98)}
    if any((c[s]['images'], c[s]['groups']) != v for s, v in expected.items()):
        raise SystemExit(f'manifest counts differ from the frozen proposal: {c}')
    d = docx.Document(DOCX)
    table = d.tables[0]
    if [cell.text for cell in table.rows[0].cells] != ['Partición', 'Imágenes', 'Enfermo',
                                                       'Saludable']:
        raise SystemExit('Table 1 is not the expected table')
    header = ['Partición', 'Imágenes', 'Instancias Enfermo', 'Instancias Saludable']
    for col, text in enumerate(header):
        cell_text(d, 0, 0, col, text)
    for i, (split, name) in enumerate(SPLITS, start=1):
        for col, value in enumerate((name, c[split]['images'], c[split]['enfermo'],
                                     c[split]['saludable'])):
            cell_text(d, 0, i, col, str(value))
    for col, value in enumerate(('Total', c['total']['images'], c['total']['enfermo'],
                                 c['total']['saludable'])):
        cell_text(d, 0, 4, col, str(value))
    add_last_column(table, ['Grupos'] + [str(c[s]['groups']) for s, _ in SPLITS]
                    + [str(c['total']['groups'])])

    set_runs(d, 'Tabla 1. Distribución del conjunto del detector binario', [
        ('Tabla 1. ', 'b'),
        ('Conjunto del detector binario tras la partición por grupos de origen: imágenes, '
         'instancias por clase y grupos de cada partición.', '')])
    replace(d, 'con dos clases: Enfermo y Saludable. La distribución se presenta en la Tabla 1.',
            'con dos clases: Enfermo y Saludable. La partición publicada por la fuente se '
            'sustituyó por una partición por grupos de origen (Sección 3.3.1), cuya distribución '
            'se presenta en la Tabla 1.')
    replace(d, 'No se aplicó ninguna corrección específica del desbalance: la aumentación es la '
               'configuración por defecto de Ultralytics, igual para ambas clases.',
            'No se aplicó ninguna corrección específica del desbalance: la aumentación es la '
            'configuración por defecto de Ultralytics, igual para ambas clases. Todas las '
            'instancias Enfermo de entrenamiento proceden de un único grupo de origen, el '
            f"montaje descrito en la Sección 3.3.1; la prueba tiene {c['test']['enfermo']} "
            f"instancias Enfermo repartidas en {c['test']['enfermo_groups']} grupos.")

    set_runs(d, '3.3\tAnálisis y mitigación de fuga de datos en MangoDHDS',
             [('3.3', 'i'), ('\tAnálisis y mitigación de fuga de datos', '')])
    replace(d, 'no una grabación continua (Sección 3.3).',
            'no una grabación continua (Sección 3.3.1).')
    heading3 = '3.2.2\tClasificador de enfermedad (Modelo 2)'
    anchor = '3.3\tAnálisis y mitigación de fuga de datos'
    paragraphs = [
        ('3.3.1\tDetector binario (Modelo 1)', heading3),
        ('La fuente publica una partición en entrenamiento, validación y prueba, pero no la '
         'procedencia de cada imagen. Se auditaron las 669 imágenes con tres criterios: '
         'identidad de bytes por SHA-256; hash perceptual pHash de 64 bits (ImageHash 4.3.2, '
         'Pillow 12.2.0) con umbral de Hamming menor que 5 y una banda de sensibilidad de 5 a '
         '10; y revisión visual ciega de cada candidato por dos revisores independientes, con '
         'un tercero en caso de desacuerdo. Dos generadores adicionales, pHash invariante a la '
         'rotación y similitud de embedding ImageNet con un horizonte fijado antes de ver los '
         'resultados, propusieron 47 pares más, adjudicados con el mismo protocolo: 37 '
         'resultaron relacionados y 10 no.', 'Se utilizó el conjunto MangoDHDS'),
        ('Las 669 imágenes tienen SHA-256 distintos, pero la partición publicada no era '
         'independiente. De los doce pares bajo el umbral, seis cruzan de entrenamiento a '
         'validación. En la banda de 5 a 10, 15 de los 16 pares que cruzan particiones '
         'resultaron relacionados, así que ese umbral deja pasar contaminación. Las 432 imágenes '
         'nombradas como un vídeo forman un montaje de fotografías distintas en el que el mismo '
         'fruto aparece en fotografías diferentes, algo que ningún hash detecta. Doce de las '
         'trece instancias Enfermo del test publicado procedían de ese montaje, cuyas otras '
         '329 imágenes estaban en entrenamiento.', 'Entrenar y evaluar sobre tal split'),
        ('Por ello la partición publicada se sustituyó por una partición por grupos atómicos de '
         'origen. Cada grupo une duplicados, casi duplicados y relaciones adjudicadas, y el '
         'montaje completo forma un único grupo, porque ninguna fuente verificable permite '
         'separar sus fotografías. La asignación de grupos a particiones es un algoritmo único '
         'fijado antes de ver los datos (semilla 42, objetivo 70/15/15), sin búsqueda de '
         f"semillas. El resultado (Tabla 1) tiene {c['total']['groups']} grupos: "
         f"{c['train']['groups']} en entrenamiento, {c['valid']['groups']} en validación y "
         f"{c['test']['groups']} en prueba, y {c['test']['enfermo_groups']} de los de prueba "
         'contienen instancias Enfermo. Todas las instancias Enfermo de entrenamiento proceden '
         'del montaje, de modo que la prueba mide la generalización desde ese origen hacia '
         'imágenes de otros orígenes. Como 89 de las 117 imágenes de la nueva prueba estaban '
         'en el entrenamiento histórico, los pesos publicados no pueden evaluarse sobre ella y '
         'el detector se reentrenó (Sección 3.4). Con estos criterios no se detecta '
         'contaminación entre particiones. No se afirma que el conjunto esté libre de fuga: '
         'pueden quedar relaciones de mismo fruto que ningún generador propone.',
         'Entrenar y evaluar sobre tal split'),
        ('3.3.2\tClasificador de enfermedad (MangoDHDS)', heading3),
    ]
    for text, like in paragraphs:
        insert_after(d, anchor, text, like=like)
        anchor = text[:60]
    delete_paragraph(d, '(MangoDHDS_clean) se comprobó reejecutando')
    replace(d, 'El conjunto resultante',
            'El conjunto resultante (MangoDHDS_clean) se comprobó reejecutando el detector de '
            'duplicados: no se detectan pares repartidos entre particiones bajo el umbral.')
    d.save(DOCX)
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8'))
    entries.append({'pass': '2a', 'script': 'provenance/commands/task09/revise_pass2a.py',
                    'before_sha256': before, 'after_sha256': sha(DOCX),
                    'manifest_sha256': sha(MANIFEST), 'counts': c})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(entries[-1], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
