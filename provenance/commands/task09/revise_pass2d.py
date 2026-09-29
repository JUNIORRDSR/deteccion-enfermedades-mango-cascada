"""TASK-09 pass 2d: the corrections of the independent audit B (reports/execution/task-09-results-audit.md)
and of the page-by-page render review, on the manuscript after pass 2c.

B-01 the temporal premise of the introduction goes; B-02 the M2 leakage paragraph keeps only what
the audit shows; B-03/B-04 the Cancro-Costras explanation, the 320 px mitigation and the light
saturation become untested hypotheses; B-05 both tests are called internal retrospective
evaluations (protocol_freeze.md, test section); B-06 the unseen-montage sentence states only the
documented group separation; B-07 the M2 duplicate sensitivity joins the principal estimate.
Render review: the detector leak in 5.3 and the conclusion, the web-service scope, the running
header, the disease-name capitals, the table typography and the figure plural. Claim matrix:
five diagnoses in 5.2 (CLAIM-041) and image-level labels in 3.5 (CLAIM-031). Figures 1 and 2 at
300 dpi (B-13) and Figure 3 with decimal commas (B-12) replace their embedded media.

Every result number comes from the artifacts through revise_pass2c.facts()/values() or the
sensitivity JSON; each edit names the exact text it expects and fails if it is not there once.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
import revise_pass2c  # noqa: E402
from docx_edit import EditFailed, cell_text, insert_after, replace, set_paragraph, sha  # noqa: E402
from results_tables import es  # noqa: E402

DOCX = revise_pass2c.DOCX
SENSITIVITY = 'artifacts/metrics/model2_sensitivity.json'
HEADER_OLD = 'Author | short title'
HEADER_NEW = 'Villa Bastidas et al. | Detección y clasificación de enfermedades en mango'


def pp_ci(delta: dict, interval: dict) -> str:
    """A difference in percentage points with its paired 95 % interval."""
    low, high = interval['ci95']
    return f"{es(delta['percentage_points'], 2)} [{es(low * 100, 2)}; {es(high * 100, 2)}]"


def sensitivity_paragraph() -> str:
    s = json.loads((ROOT / SENSITIVITY).read_text(encoding='utf-8'))
    st, est, iv = s['structure'], s['estimands'], s['bootstrap']['intervals']
    dl, di = s['deltas'], s['bootstrap']['delta_intervals']

    def value(scheme, key):
        return f"{es(est[scheme]['metrics'][key])} [{es(iv[scheme][key]['ci95'][0])}; " \
               f"{es(iv[scheme][key]['ci95'][1])}]"
    return (f"La prueba tiene {st['n_images']} imágenes pero {st['n_unique_sha']} SHA-256 distintos: "
            f"{st['n_images'] - st['n_unique_sha']} imágenes repiten exactamente a otra de la misma "
            'partición. Los dos análisis de sensibilidad fijados en el protocolo usan las mismas '
            f"predicciones y las mismas {s['inputs']['resamples']} remuestras de grupos (semilla "
            f"{s['inputs']['seed']}). Con una imagen por SHA-256, la exactitud es "
            f"{value('exact_sha_dedup', 'accuracy')} y el macro-F1 {value('exact_sha_dedup', 'macro_f1')}; "
            f"con peso 1 por cluster, {value('cluster_weighted', 'accuracy')} y "
            f"{value('cluster_weighted', 'macro_f1')}. Frente al análisis principal, la exactitud cambia "
            f"{pp_ci(dl['exact_sha_dedup']['accuracy'], di['exact_sha_dedup']['accuracy'])} y "
            f"{pp_ci(dl['cluster_weighted']['accuracy'], di['cluster_weighted']['accuracy'])} puntos "
            'porcentuales, y el macro-F1 '
            f"{pp_ci(dl['exact_sha_dedup']['macro_f1'], di['exact_sha_dedup']['macro_f1'])} y "
            f"{pp_ci(dl['cluster_weighted']['macro_f1'], di['cluster_weighted']['macro_f1'])}, con el "
            'intervalo pareado del 95 % entre corchetes.')


def edits(v: dict) -> list[tuple[str, str]]:
    n, g, m2n = v['n_test'], v['groups_test'], v['m2_n']
    return [
        # B-01
        ('Ambas alternativas presentan limitaciones estructurales para el productor rural promedio: '
         'la inspección visual es tardía por naturaleza, ya que cuando los síntomas son perceptibles '
         'a simple vista, el patógeno ya ha comprometido una fracción significativa del tejido. '
         'Mientras que las técnicas de laboratorio son costosas',
         'Para el productor rural promedio, las técnicas de laboratorio son costosas'),
        # B-03
        ('Ambas patologías presentan lesiones oscuras e irregulares, y distinguirlas suele requerir '
         'detalles finos, como la textura local o el exudado bacteriano, que un clasificador a 224 px '
         'apenas captura.',
         'Este trabajo no analizó la causa de esa confusión; la similitud visual de las lesiones, la '
         'resolución de entrada y el número de ejemplos por clase son hipótesis por comprobar.'),
        ('estas patologías comparten manifestaciones visuales y separarlas requeriría más datos, mayor '
         'resolución de entrada o módulos de atención local.',
         'comprobar si más datos, mayor resolución de entrada o módulos de atención local la reducen '
         'queda como trabajo futuro.'),
        ('la saturación bajo iluminación ambiental intensa y la ausencia',
         'una posible saturación del sensor bajo luz intensa, que este trabajo no midió, y la ausencia'),
        # B-05
        (f'antes de evaluar una sola vez la prueba ({n} imágenes, {g} grupos). En prueba, el detector',
         f'antes de evaluar una sola vez la prueba ({n} imágenes, {g} grupos), una evaluación interna '
         'retrospectiva sobre imágenes ya publicadas. En ella, el detector'),
        (f'El clasificador, evaluado sobre la partición limpia de MangoDHDS ({m2n} imágenes)',
         f'El clasificador, evaluado también de forma retrospectiva sobre la partición limpia de '
         f'MangoDHDS ({m2n} imágenes)'),
        ('se fijaron antes de tocar la prueba, que se evaluó una sola vez (EXP-R02).',
         'se fijaron antes de evaluar la prueba una sola vez (EXP-R02). Es una evaluación interna '
         'retrospectiva, no una prueba prospectiva: sus imágenes eran públicas y parte de ellas estaba '
         'en el entrenamiento histórico (Sección 3.3.1).'),
        ('distribuidos según la Tabla 7.',
         'distribuidos según la Tabla 7. Como en el Modelo 1, es una evaluación interna retrospectiva: '
         'la versión anterior del manuscrito ya informó resultados sobre esta partición.'),
        (f'evaluado una sola vez sobre {n} imágenes de prueba de {g} grupos',
         f'evaluado una sola vez, de forma retrospectiva, sobre {n} imágenes de prueba de {g} grupos'),
        ('El clasificador YOLO11n-cls, evaluado sobre la partición limpia de MangoDHDS',
         'El clasificador YOLO11n-cls, evaluado de forma retrospectiva sobre la partición limpia de '
         'MangoDHDS'),
        # B-06
        ('El umbral se eligió en validación, lo que vuelve optimistas las cifras de esa partición, y '
         'la partición por grupos de origen hace que la prueba contenga montajes que el modelo no vio '
         'al entrenar.',
         'El umbral se eligió en validación, lo que vuelve optimistas las cifras de esa partición. '
         'Validación y prueba son disjuntas de entrenamiento por grupo de origen, y este trabajo no '
         'identificó la causa de la diferencia entre ambas.'),
        # Render review
        ('El prototipo se integra en una arquitectura de servicio basada en FastAPI con persistencia '
         'SQLite, diseñada para operar localmente sin conectividad permanente a internet, accesible '
         'desde un navegador web tras su despliegue en red local.',
         'El detector también se ofrece como servicio web local basado en FastAPI con persistencia '
         'SQLite, pensado para operar sin conectividad permanente a internet; la cascada completa se '
         'ejecuta por línea de comandos (Sección 3.6).'),
        ('las reproducidas en las Figura 5 y Figura 7', 'las reproducidas en las Figuras 5 y 7'),
        ('el Cancro Bacteriano, las Costras y la Podredumbre del Extremo del Tallo',
         'el Cancro bacteriano, las Costras y la Podredumbre del extremo del tallo'),
        ('Bacterial Canker (Cancro Bacteriano)', 'Bacterial Canker (Cancro bacteriano)'),
        ('Stem End Rot (Podredumbre del Extremo del Tallo)',
         'Stem End Rot (Podredumbre del extremo del tallo)'),
        # Claim matrix: CLAIM-041 and CLAIM-031
        ('Un único modelo multiclase entrenado directamente sobre los seis posibles diagnósticos (5 '
         'enfermedades + sano) habría requerido un corpus único con anotaciones simultáneas de '
         'detección y diagnóstico, corpus que no existe para mango.',
         'Un único modelo entrenado directamente sobre los cinco diagnósticos (cuatro enfermedades y '
         'Saludable) habría requerido un corpus con anotaciones simultáneas de caja y diagnóstico, que '
         'no se encontró entre los conjuntos públicos de mango revisados.'),
        ('la naturaleza del corpus: las anotaciones originales son cajas de imagen completa (cls 0.5 '
         '0.5 1.0 1.0), de modo que',
         'la naturaleza del corpus: sus etiquetas son de imagen completa (en formato YOLO, cajas cls '
         '0.5 0.5 1.0 1.0), de modo que'),
    ]


PARAGRAPHS = [
    # B-02
    ('Entrenar y evaluar sobre esa partición',
     'Con imágenes casi idénticas repartidas entre particiones, las métricas de validación y de '
     'prueba no miden sólo la generalización a frutos no vistos y pueden sobreestimarla (Kapoor & '
     'Narayanan, 2023); este trabajo no cuantificó ese efecto en el corpus de clasificación.'),
]
REPLACE_SPANS_5_3 = [
    ('El hallazgo de 76 pares casi-duplicados en el particionamiento original del corpus público es '
     'relevante por dos motivos. Primero, muestra por qué conviene auditar el particionamiento antes '
     'de utilizar un conjunto público. Segundo, sugiere que las métricas reportadas en trabajos '
     'previos que hayan usado la partición original podrían estar sesgadas al alza',
     'Las dos auditorías de fuga son relevantes por dos motivos. En el corpus del detector, casi '
     'todas las instancias Enfermo de la prueba publicada procedían de un montaje cuyas demás '
     'imágenes estaban en entrenamiento (Sección 3.3.1), y en el de clasificación había pares casi '
     'duplicados repartidos entre particiones (Sección 3.3.2). Primero, muestran por qué conviene '
     'auditar el particionamiento antes de utilizar un conjunto público. Segundo, sugieren que las '
     'métricas reportadas en trabajos previos que hayan usado las particiones originales podrían '
     'estar sesgadas al alza'),
    ('Como contribución metodológica colateral, se identificó y mitigó una fuga de datos en el '
     'particionamiento original del corpus público de mango (76 pares casi duplicados entre '
     'particiones), publicando un procedimiento reproducible basado en hash perceptual y union-find '
     'que regenera el conjunto con estratificación por clase,',
     'Como contribución metodológica, se identificaron y mitigaron fugas de datos en las particiones '
     'publicadas de los dos corpus: en el del detector, un mismo montaje fotográfico repartido entre '
     'entrenamiento y prueba, sustituido por una partición por grupos de origen; en el del '
     'clasificador, pares casi duplicados entre particiones, eliminados con un procedimiento '
     'reproducible basado en hash perceptual y union-find que regenera el conjunto con '
     'estratificación por clase,'),
    ('para investigadores futuros que utilicen el mismo corpus y,',
     'para investigadores futuros que utilicen los mismos corpus y,'),
]
TABLE_CELLS = [  # (table, row, column, expected, new)
    (1, 10, 1, '5·10^-4', '5·10⁻⁴'),
    (7, 1, 0, 'Detector limitado a 669 imgs', 'Detector limitado a 669 imágenes'),
    (7, 3, 2, 'Más datos, resolución 320 px, atención local',
     'Evaluar más datos, mayor resolución o atención local'),
    (7, 6, 1, 'Saturación del sensor', 'Posible saturación del sensor (no medida)'),
    (7, 6, 2, 'Parasol + normalización', 'Evaluar parasol y normalización'),
]


def header(document) -> int:
    changed = 0
    for section in document.sections:
        for part in (section.header, section.first_page_header, section.even_page_header):
            if part.is_linked_to_previous and section is not document.sections[0]:
                continue
            for paragraph in part.paragraphs:
                for run in paragraph.runs:
                    if HEADER_OLD in run.text:
                        run.text = run.text.replace(HEADER_OLD, HEADER_NEW)
                        changed += 1
    return changed


def apply(document, v: dict) -> None:
    for old, new in edits(v) + REPLACE_SPANS_5_3:
        replace(document, old, new)
    for start, text in PARAGRAPHS:
        set_paragraph(document, start, text)
    insert_after(document, 'La evaluación se realizó sobre las', sensitivity_paragraph())
    for table, row, col, expected, new in TABLE_CELLS:
        found = document.tables[table].cell(row, col).text
        if found != expected:
            raise EditFailed(f'table {table} cell ({row}, {col}) is {found!r}, not {expected!r}')
        cell_text(document, table, row, col, new)
    if header(document) == 0:
        raise EditFailed('the running header placeholder was not found')


FIGURES = {  # regenerated by figures.py (300 dpi, B-13) and figure3_training.py (decimal comma, B-12)
    'word/media/image1.png': 'manuscript/figures/fig1_cascada.png',
    'word/media/image2.png': 'manuscript/figures/fig2_prototipos.png',
    'word/media/image3.png': 'manuscript/figures/fig3_entrenamiento.png',
}


def main() -> int:
    from revise_pass2b import replace_media
    before = sha(DOCX)
    v = revise_pass2c.values(revise_pass2c.facts())
    d = docx.Document(DOCX)
    apply(d, v)
    d.save(DOCX)
    for name, source in FIGURES.items():
        replace_media(DOCX, name, ROOT / source)
    docx.Document(DOCX)
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8'))
    entries.append({'pass': '2d', 'script': 'provenance/commands/task09/revise_pass2d.py',
                    'responds_to': 'reports/execution/task-09-results-audit.md B-01 to B-07; render review',
                    'before_sha256': before, 'after_sha256': sha(DOCX),
                    'figures': {k: sha(ROOT / f) for k, f in FIGURES.items()}})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(entries[-1], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
