"""TASK-09 pass 2f: the corrections of the final adversarial review (reports/final_adversarial_review.md)
on the manuscript after pass 2e and on the response letter, with the authors' decisions of 2026-09-28:
declare the AI adjudication now (H-01), keep the title (H-03), publish the repository with the final
weights under AGPL-3.0 (H-06, CLAIM-042).

H-01 the visual adjudication of the Model 1 audit was done by Claude agents, which failed the first
positive controls and disagreed often; H-02 the split rule was frozen before building the groups, not
before seeing the data; H-03 the labels are third-party visual labels; H-05 the classifier crosses a
domain shift; H-06 the repository is cited; M-02 and M-03 the Model 2 label conflict and the training
and validation duplicates; M-04 the two validation evaluators; M-05 the intervals are conditional;
M-06 the 0.4 rejection threshold is not validated; M-07 the latency spread and pool composition;
M-08 two literature claims are narrowed; L-01 Ultralytics is cited by its release tag. Render
review: no table breaks across a page.
Result numbers come from the artifacts; each edit names the exact text it expects.
"""

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
import revise_pass2c  # noqa: E402
from docx_edit import EditFailed, insert_after, replace, sha  # noqa: E402
from results_tables import es  # noqa: E402
from revise_letter import LETTER, apply  # noqa: E402

ROOT = revise_pass2c.ROOT
DOCX = revise_pass2c.DOCX
REPO = 'https://github.com/JUNIORRDSR/deteccion-enfermedades-mango-cascada'
RELEASE = f'{REPO}/releases/tag/v1.0.0'
CITE = '(Villa Bastidas et al., 2026)'
REFERENCE = ('Villa Bastidas, D., Solano Romero, J., & Molina-Cárdenas, M. (2026). Detección y '
             'clasificación automatizada de enfermedades en mango: código, pesos y evidencia de la '
             f'revisión (Versión 1.0.0) [Software]. GitHub. {RELEASE}')


def facts() -> dict:
    """Every count the new sentences print, read from its artifact."""
    blind = json.loads((ROOT / 'data/audits/model1/blinding_log.json').read_text(encoding='utf-8'))
    supp = list(csv.DictReader(open(ROOT / 'data/audits/model1/supplementary_adjudications.csv',
                                    encoding='utf-8')))
    pairs = [r for r in supp if not r['category'].startswith('control')]
    split = [r for r in pairs if r['agreement'] == 'DISAGREE'
             and 'UNRELATED' in (r['decision_a'], r['decision_b'])]
    m2 = list(csv.DictReader(open(ROOT / 'data/manifests/model2_frozen_manifest.csv', encoding='utf-8')))
    by = {s: [r for r in m2 if r['split'] == s] for s in ('train', 'val')}
    labels = {}
    for r in m2:
        labels.setdefault((r['split'], r['cluster_id']), set()).add(r['class_name'])
    conflicts = [k for k, v in labels.items() if len(v) > 1]
    pool = list(csv.DictReader(open(ROOT / 'artifacts/metrics/benchmark_raw_pool.csv', encoding='utf-8')))
    manifest = {r['image_id']: r for r in csv.DictReader(
        open(ROOT / 'data/manifests/model1_clean_manifest.csv', encoding='utf-8'))}
    fruits = {}
    for r in csv.DictReader(open(ROOT / 'artifacts/metrics/benchmark_raw.csv', encoding='utf-8')):
        if r['n_predicted_fruits'] != '':
            fruits[r['image_id']] = int(r['n_predicted_fruits'])
    e2e = json.loads((ROOT / 'artifacts/metrics/benchmark_summary.json').read_text(
        encoding='utf-8'))['stages']['end_to_end']
    v01 = json.loads((ROOT / 'experiments/model1/EXP-V01/metrics_frozen.json').read_text(encoding='utf-8'))
    log = list(csv.DictReader(open(ROOT / 'experiments/model1/EXP-R01/v1/run/train/results.csv',
                                   encoding='utf-8')))
    epoch = json.loads((ROOT / 'experiments/model1/EXP-R01/selection_record.json').read_text(
        encoding='utf-8'))['selected_epoch']
    row = {k.strip(): v for k, v in next(r for r in log if int(r['epoch'].strip()) == epoch).items()}
    if len(conflicts) != 1 or conflicts[0][0] != 'train':
        raise EditFailed(f'expected one mixed-label training cluster, found {conflicts}')
    if any(blind['calibration'][k]['positive_controls_called_related'] for k in 'ab'):
        raise EditFailed('the text says neither agent recognised a positive control')
    return {
        'units': blind['counts']['candidates'], 'disagree': blind['counts']['disagree'],
        'pos': blind['controls']['positive'],
        'pos_called': {k: blind['calibration'][k]['positive_controls_called_related'] for k in 'ab'},
        'pairs': len(pairs), 'pairs_disagree': sum(r['agreement'] == 'DISAGREE' for r in pairs),
        'pairs_existence': len(split),
        'train_n': len(by['train']), 'train_sha': len({r['sha256'] for r in by['train']}),
        'val_n': len(by['val']), 'val_sha': len({r['sha256'] for r in by['val']}),
        'pool_n': len(pool), 'pool_groups': len({manifest[r['image_id']]['group_id'] for r in pool}),
        'pool_enfermo': sum(r['with_enfermo'] == 'True' for r in pool),
        'fruits_min': min(fruits.values()), 'fruits_max': max(fruits.values()),
        'mean': es(e2e['mean'], 1), 'std': es(e2e['std'], 1), 'min': es(e2e['min'], 1),
        'max': es(e2e['max'], 1),
        'log_map50': es(float(row['metrics/mAP50(B)']), 3), 'log_map': es(float(row['metrics/mAP50-95(B)']), 3),
        'v01_map50': es(v01['average_precision']['map50'], 3),
        'v01_map': es(v01['average_precision']['map50_95'], 3),
    }


def edits(f: dict) -> list[tuple[str, str]]:
    return [
        # H-01
        ('y revisión visual ciega de cada candidato por dos revisores independientes, con un tercero en '
         'caso de desacuerdo.',
         'y revisión visual de cada candidato por dos agentes de IA en instancias separadas (Claude Opus y '
         'Claude Sonnet), con un tercero (Claude Haiku) en caso de desacuerdo, sin acceso a la partición, '
         'la clase ni el nombre de archivo; ese ciego se impuso por instrucción, no por control de acceso, '
         'y ninguna de estas decisiones la revisó una persona.'),
        ('propusieron 47 pares más, adjudicados con el mismo protocolo: 37 resultaron relacionados y 10 no.',
         'propusieron 47 pares más, adjudicados con el mismo protocolo (el tercer agente fue otra instancia '
         'de Claude Opus): 37 resultaron relacionados y 10 no. La fiabilidad de esta adjudicación es '
         f"limitada. En la primera ronda ninguno de los dos agentes reconoció los {f['pos']} controles "
         f"positivos, y discreparon en {f['disagree']} de las {f['units']} unidades, siempre sobre el "
         'tipo de relación (casi duplicado o secuencia) y no sobre si existía; en la ronda suplementaria '
         f"discreparon en {f['pairs_disagree']} de los {f['pairs']} pares, {f['pairs_existence']} de ellos "
         'sobre si existía relación. Como esas decisiones definen los grupos, la partición y los '
         'intervalos heredan su error.'),
        # H-02
        ('La asignación de grupos a particiones es un algoritmo único fijado antes de ver los datos '
         '(semilla 42, objetivo 70/15/15), sin búsqueda de semillas.',
         'La asignación de grupos a particiones es un algoritmo único (semilla 42, objetivo 70/15/15), sin '
         'búsqueda de semillas, fijado en el protocolo congelado el 20 de septiembre de 2026, antes de '
         'construir los grupos y de ejecutar la asignación. No se fijó antes de ver los datos: para entonces '
         'ya se conocían las imágenes y los resultados históricos de su prueba.'),
        # M-06
        ('o «Desconocido» si su confianza es menor que 0,4. Enviar',
         'o «Desconocido» si su confianza es menor que 0,4. Ese umbral es el del prototipo original: no se '
         'calibró ni se validó, y las métricas del Modelo 2 de la Sección 4.2.3 se calculan sin ese '
         'rechazo. Enviar'),
        # H-06, Section 3.6: the prototypes are those of the original project
        ('El repositorio contiene dos prototipos separados.', 'El proyecto original tiene dos prototipos '
         'separados.'),
        ('La cascada completa se ejecuta con el script de línea de comandos del repositorio,',
         'La cascada completa se ejecuta con su script de línea de comandos,'),
        ('La integración de la cascada en el servicio web no está implementada.',
         'La integración de la cascada en el servicio web no está implementada. El repositorio del trabajo '
         f'{CITE} incluye una copia de esa cascada, que usan la Figura 7 y la medición de latencia.'),
        # M-05
        ('que remuestrean grupos de origen y no imágenes.',
         'que remuestrean grupos de origen y no imágenes. Son intervalos condicionales: mantienen fijos el '
         'modelo entrenado, la partición, el umbral y la definición de los grupos, así que no recogen la '
         'variabilidad del entrenamiento, de la partición, del etiquetado ni de la agrupación.'),
        # M-04
        ('las métricas de validación del evaluador del artículo, con el umbral operativo, se dan en la '
         'Tabla 4.',
         'las métricas de validación del evaluador del artículo, con el umbral operativo, se dan en la '
         f"Tabla 4. Las dos evaluaciones del mismo checkpoint difieren (mAP@0,5 de {f['log_map50']} frente "
         f"a {f['v01_map50']}, y mAP@0,5:0,95 de {f['log_map']} frente a {f['v01_map']}): durante el "
         'entrenamiento, el validador de Ultralytics agrupa las imágenes en lotes rectangulares y calcula en '
         'media precisión (FP16), mientras que el evaluador del artículo predice cada imagen por separado '
         'en FP32. Este trabajo no aisló la contribución de cada diferencia ni comprobó si el evaluador del '
         'artículo ordenaría igual los checkpoints candidatos; la regla de selección, fijada en el '
         'protocolo, usa el registro de entrenamiento.'),
        # M-07
        ('la llamada al Modelo 1 toma 203,8 ms y la cascada completa 233,9 ms.',
         f"la llamada al Modelo 1 toma 203,8 ms y la cascada completa 233,9 ms. La media es {f['mean']} ms "
         f"(desviación típica {f['std']} ms), con un mínimo de {f['min']} ms y un máximo de {f['max']} ms. "
         f"Las repeticiones miden {f['pool_n']} imágenes de {f['pool_groups']} grupos de origen, "
         f"{f['pool_enfermo']} con frutos Enfermo, en las que el Modelo 1 detecta entre {f['fruits_min']} "
         f"y {f['fruits_max']} frutos, así que la medición no cubre escenas con muchos frutos."),
        # M-02 and M-03
        ('la partición de prueba tiene entre 42 y 46 imágenes por clase.',
         'la partición de prueba tiene entre 42 y 46 imágenes por clase. Un cluster de entrenamiento une '
         'dos imágenes casi idénticas (distancia de Hamming 2) con etiquetas distintas, Cancro bacteriano '
         'y Costras; se conservaron las dos etiquetas sin adjudicarlas. Entrenamiento y validación también '
         f"repiten archivos: {f['train_sha']} SHA-256 distintos en {f['train_n']} imágenes de entrenamiento "
         f"y {f['val_sha']} en {f['val_n']} de validación. El checkpoint del Modelo 2 se eligió con la "
         'exactitud de validación ponderada por imagen, y el análisis de sensibilidad a duplicados de la '
         'Sección 4.2.3 sólo cubre la prueba.'),
        # H-05
        ('La métrica y su evaluador quedan definidos, pero su valor no se informa.',
         'La métrica y su evaluador quedan definidos, pero su valor no se informa. Además, el clasificador '
         'se entrenó con imágenes de frutos individuales centrados, tomadas en condiciones controladas, y '
         'en la cascada recibe recortes de escenas de campo del detector; el efecto de ese cambio de '
         'dominio no se ha medido.'),
        # H-06, CLAIM-042
        ('Se publican el protocolo de auditoría y su código.',
         f'El código, los pesos de los dos modelos y la evidencia de la auditoría están en un repositorio '
         f'público {CITE}.'),
        ('y su código se publican para que pueda aplicarse a otros conjuntos.',
         f'y su código están en el repositorio del trabajo {CITE} para que puedan aplicarse a otros '
         'conjuntos.'),
        ('dicho conjunto no interviene en los modelos ni en los resultados aquí reportados y queda '
         'disponible para trabajos futuros.',
         'dicho conjunto no interviene en los modelos ni en los resultados aquí reportados y queda '
         'disponible para trabajos futuros. El código, los manifiestos congelados, los pesos de los dos '
         'modelos, las predicciones guardadas y los registros de ejecución están en un repositorio público '
         f'bajo licencia AGPL-3.0 {CITE}.'),
        # H-03
        ('Finalmente, el sistema aún carece',
         'Las etiquetas de ambos conjuntos son las publicadas por terceros, sin criterios diagnósticos, '
         'confirmación de laboratorio ni acuerdo entre anotadores documentados, así que los resultados '
         'miden la concordancia con esas etiquetas visuales y no la validez fitopatológica del diagnóstico. '
         'Finalmente, el sistema aún carece'),
        # M-08
        ('Para el productor rural promedio, las técnicas de laboratorio son costosas, lentas y requieren '
         'infraestructura especializada raramente disponible en zonas rurales (Venbrux et al., 2023). La '
         'consecuencia agronómica es una dependencia excesiva de la aplicación preventiva masiva de '
         'agroquímicos, con los costos económicos y ambientales que ello implica (Ciofini et al., 2022).',
         'Las técnicas de laboratorio requieren equipos y personal especializados, lo que limita su uso '
         'rutinario en campo (Venbrux et al., 2023). En la antracnosis poscosecha, el control sigue '
         'apoyándose sobre todo en fungicidas sintéticos, con sus costos económicos y ambientales (Ciofini '
         'et al., 2022).'),
        ('Revisiones recientes (Liu & Wang, 2021) documentan aplicaciones de YOLO a la detección de '
         'enfermedades en cultivos como el tomate y la manzana, pero los reportes específicos sobre mango '
         'son escasos y, hasta donde los autores conocen, ninguno ha publicado un análisis sistemático de '
         'fuga de datos sobre conjuntos públicos de mango.',
         'Una revisión (Liu & Wang, 2021) documenta aplicaciones de YOLO a la detección de enfermedades en '
         'cultivos como el tomate y la manzana. Este trabajo no hizo una búsqueda sistemática de la '
         'literatura sobre mango, así que no afirma ser el primero en auditar la fuga de datos de sus '
         'conjuntos públicos.'),
        # L-01
        ('[Software]. GitHub. https://github.com/ultralytics/ultralytics',
         '[Software]. GitHub. https://github.com/ultralytics/ultralytics/releases/tag/v8.4.52'),
    ]


def letter_edits(f: dict) -> dict[str, list[tuple[str, str]]]:
    return {
        '# Respuesta al dictamen': [
            ('tras la pasada 2e', 'tras la pasada 2f'),
            ('La única acción pendiente de los autores es CLAIM-042: el resumen y la Sección 5.3 dicen que '
             'el protocolo de auditoría y su código se publican, lo que exige publicar el repositorio y '
             'citarlo antes del envío, o suavizar ambas frases.',
             f'El código, los pesos y la evidencia están en {REPO} (versión 1.0.0), citado en el manuscrito '
             f'{CITE}; no queda ninguna acción pendiente de los autores.')],
        '## REVIEW-01': [
            ('3. Revisión visual ciega de cada candidato por dos revisores independientes, con un tercero '
             'cuando discreparon.',
             '3. Revisión visual de cada candidato por dos agentes de IA en instancias separadas (Claude Opus '
             'y Claude Sonnet), con un tercero (Claude Haiku) cuando discreparon. El ciego se impuso por '
             'instrucción, no por control de acceso, y ninguna decisión la revisó una persona.'),
            ('y los revisores confirmaron cinco', 'y los agentes confirmaron cinco'),
            ('lo son para ambos revisores', 'lo son para ambos agentes'),
            ('Sus 47 pares se adjudicaron con el mismo protocolo ciego: dos pasadas independientes y una '
             'tercera adjudicación separada para los 38 desacuerdos.',
             'Sus 47 pares se adjudicaron con el mismo protocolo: dos agentes en instancias separadas y un '
             'tercero, otra instancia de Claude Opus, para los 38 desacuerdos.'),
            ('Los seis controles de consistencia salieron bien para ambos revisores.',
             'Los seis controles de consistencia, que comparan con decisiones anteriores y no con una verdad '
             'biológica, salieron bien para ambos agentes. En la primera ronda, en cambio, ninguno de los '
             f"dos reconoció los {f['pos']} controles positivos, y discreparon en {f['disagree']} de "
             f"{f['units']} unidades, siempre sobre el tipo de relación."),
            ('pueden seguir existiendo.',
             'pueden seguir existiendo. La adjudicación visual la hicieron agentes de IA, sin revisión '
             'humana: la Sección 3.3.1 lo declara, con los controles fallidos y los desacuerdos, y la '
             're-adjudicación por personas queda como trabajo futuro.'),
            ('**Estado.** RESUELTO.', '**Estado.** RESUELTO PARCIALMENTE: la auditoría existe, pero su '
             'adjudicación visual la hicieron agentes de IA, sin revisión humana.')],
        '## REVIEW-02': [
            ('La asignación de grupos es un algoritmo único, fijado antes de ver los datos (semilla 42, '
             'objetivo 70/15/15 y coste cuadrático normalizado sobre imágenes e instancias por clase), sin '
             'barrido de semillas.',
             'La asignación de grupos es un algoritmo único (semilla 42, objetivo 70/15/15 y coste '
             'cuadrático normalizado sobre imágenes e instancias por clase), sin barrido de semillas, fijado '
             'en el protocolo congelado del 20 de septiembre de 2026, antes de construir los grupos y de '
             'ejecutar la asignación, aunque después de conocer las imágenes y los resultados históricos de '
             'su prueba.'),
            ('la retiramos tras una revisión metodológica independiente.',
             'la retiramos tras una revisión metodológica hecha por un agente de IA distinto del que '
             'ejecutó el trabajo.'),
            ('Una revisión metodológica independiente reprodujo byte a byte',
             'Esa misma revisión automatizada reprodujo byte a byte')],
        '## REVIEW-05': [
            ('se apoya en una independencia que las 13 instancias no tienen.',
             'se apoya en una independencia que las 13 instancias no tienen. Todos los intervalos son '
             'condicionales: mantienen fijos el modelo, la partición, el umbral y la definición de los '
             'grupos (Sección 3.7).')],
        '## REVIEW-07': [
            ('y la cascada 233,9 ms (`reports/benchmark_report.md`).',
             f"y la cascada 233,9 ms. La media es {f['mean']} ms (desviación típica {f['std']} ms), con un "
             f"mínimo de {f['min']} ms y un máximo de {f['max']} ms. Las repeticiones miden {f['pool_n']} "
             f"imágenes de {f['pool_groups']} grupos, {f['pool_enfermo']} con frutos Enfermo y entre "
             f"{f['fruits_min']} y {f['fruits_max']} frutos detectados, así que no cubren escenas densas "
             '(Sección 4.1.5 y `reports/benchmark_report.md`).')],
        '## REVIEW-09': [
            ('El entorno local de evaluación queda en `provenance/environment/inference_environment.txt`.',
             'El entorno local de evaluación queda en `provenance/environment/inference_environment.txt`. '
             'Los pesos del checkpoint seleccionado del Modelo 1 y los del Modelo 2 se publican, con sus '
             f'SHA-256, en el repositorio del trabajo {CITE}.')],
        '## REVIEW-12 y REVIEW-13': [
            ('No publicamos un número que no podemos medir,',
             'Además, el clasificador recibe en la cascada recortes de escenas de campo, distintos de las '
             'imágenes controladas con que se entrenó, y ese cambio de dominio tampoco se ha medido '
             '(Sección 5.2). No publicamos un número que no podemos medir,')],
        '## REVIEW-16, REVIEW-17 y REVIEW-18': [
            ('Añadimos Ultralytics 8.4.52, la versión usada. La lista final tiene 21 entradas',
             'Añadimos Ultralytics 8.4.52, la versión usada, citada por su etiqueta de versión, y el '
             'repositorio del trabajo. Suavizamos además dos afirmaciones que sus citas no sostenían: la '
             'dependencia de los agroquímicos (Ciofini et al., 2022) y la novedad de la auditoría de fuga, '
             'porque no hicimos una búsqueda sistemática. La lista final tiene 22 entradas')],
    }


def keep_tables_together(document) -> None:
    """Render review: the caption and every row keep with the next, so no table breaks across a
    page or leaves its caption behind."""
    for table in document.tables:
        caption = table._element.getprevious()
        if caption is not None and caption.tag.endswith('}p'):
            docx.text.paragraph.Paragraph(caption, table._parent).paragraph_format.keep_with_next = True
        for row in table.rows[:-1]:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.keep_with_next = True


def main() -> int:
    before = sha(DOCX)
    f = facts()
    d = docx.Document(DOCX)
    for old, new in edits(f):
        replace(d, old, new)
    insert_after(d, 'Venbrux, M., Crauwels, S., & Rediers, H. (2023).', REFERENCE)
    keep_tables_together(d)
    d.save(DOCX)
    docx.Document(DOCX)
    raw = LETTER.read_bytes()
    newline = '\r\n' if b'\r\n' in raw else '\n'
    LETTER.write_bytes(apply(raw.decode('utf-8').replace('\r\n', '\n'), letter_edits(f))
                       .replace('\n', newline).encode('utf-8'))
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8'))
    entries.append({'pass': '2f', 'script': 'provenance/commands/task09/revise_pass2f.py',
                    'responds_to': 'reports/final_adversarial_review.md H-01 to H-06, M-02 to M-08, L-01',
                    'before_sha256': before, 'after_sha256': sha(DOCX), 'facts': f})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(entries[-1], indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
