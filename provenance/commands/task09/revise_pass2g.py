"""TASK-09 pass 2g: final text cleanup and AI/human attribution (reports/final_text_cleanup_audit.md,
TC-01 to TC-30) on the manuscript after pass 2f and on the response letter.

The visual adjudication of the Model 1 audit was first done with Claude agents (data/audits/model1/
blinding logs); afterwards a team member reviewed the candidates manually, as the authors declared on
2026-09-29 (docs/research/decision_log.md, DECISION-040). No case-by-case record of that manual review
exists, so the text states only that it happened; the groups come from the recorded adjudication.
The rest is wording: classification instead of diagnosis for the system output, two overclaims, a
stale sentence in 2.4 and plainer prose. No number changes; each edit names the exact text it expects.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
import revise_pass2c  # noqa: E402
from docx_edit import EditFailed, cell_text, replace, sha  # noqa: E402
from revise_letter import LETTER, apply  # noqa: E402

ROOT = revise_pass2c.ROOT
DOCX = revise_pass2c.DOCX
MANUAL = 'Posteriormente, una integrante del equipo revisó manualmente los candidatos.'

EDITS = [
    # TC-01 and TC-02
    ('y revisión visual de cada candidato por dos agentes de IA en instancias separadas (Claude Opus y '
     'Claude Sonnet), con un tercero (Claude Haiku) en caso de desacuerdo, sin acceso a la partición, la '
     'clase ni el nombre de archivo; ese ciego se impuso por instrucción, no por control de acceso, y '
     'ninguna de estas decisiones la revisó una persona.',
     'y revisión visual de cada candidato. La primera adjudicación se hizo con apoyo de agentes de IA: dos '
     'instancias separadas (Claude Opus y Claude Sonnet) juzgaron cada candidato sin ver la partición, la '
     'clase ni el nombre de archivo, y una tercera (Claude Haiku) resolvió los desacuerdos; ese ciego se '
     'impuso por instrucción, no por control de acceso.'),
    ('La fiabilidad de esta adjudicación es limitada. En la primera ronda ninguno de los dos agentes '
     'reconoció los 2 controles positivos,',
     'Los agentes mostraron una fiabilidad limitada: en la primera ronda ninguno reconoció los 2 controles '
     'positivos,'),
    ('Como esas decisiones definen los grupos, la partición y los intervalos heredan su error.',
     f'{MANUAL} Los grupos de la partición proceden de las decisiones registradas de la adjudicación, de '
     'modo que la partición y los intervalos dependen de ellas.'),
    # TC-03
    ('Las etiquetas de ambos conjuntos son las publicadas por terceros,',
     'La agrupación del corpus del detector depende de una adjudicación visual apoyada inicialmente en '
     'agentes de IA de fiabilidad limitada y revisada después por una integrante del equipo (Sección '
     '3.3.1). Las etiquetas de ambos conjuntos son las publicadas por terceros,'),
    # TC-15 to TC-18
    ('marca como «Desconocido» un diagnóstico con confianza inferior a 0,4.',
     'marca como «Desconocido» una clasificación con confianza inferior a 0,4.'),
    ('y no evidencia diagnósticos correctos.', 'y no demuestra que las clases asignadas sean correctas.'),
    ('El diagnóstico fino proviene del Modelo 2,', 'La clase de enfermedad la asigna el Modelo 2,'),
    ('La separación entre detección binaria y clasificación multiclase resulta justificada por la '
     'naturaleza de los datos disponibles. Un único modelo entrenado directamente sobre los cinco '
     'diagnósticos (cuatro enfermedades y Saludable) habría requerido un corpus con anotaciones '
     'simultáneas de caja y diagnóstico,',
     'La separación entre detección binaria y clasificación multiclase responde a la naturaleza de los '
     'datos disponibles. Un único modelo entrenado directamente sobre las cinco clases (cuatro '
     'enfermedades y Saludable) habría requerido un corpus con anotaciones simultáneas de caja y '
     'enfermedad,'),
    ('La cascada permite explotar el conjunto de detección', 'La cascada permite usar el conjunto de detección'),
    ('nunca recibe diagnóstico,', 'nunca recibe una clase de enfermedad,'),
    ('con caja y diagnóstico adjudicados para los mismos frutos,',
     'con caja y enfermedad adjudicadas para los mismos frutos,'),
    # TC-19 to TC-21
    ('el corpus que permite entrenar localización fiable en campo abierto no contiene',
     'el corpus con cajas en escenas de campo abierto no contiene'),
    ('consolidar primero la cascada RGB con métricas estables y luego incorporar',
     'consolidar primero la cascada RGB y después incorporar'),
    ('y su diagnóstico convencional depende de la inspección visual o del laboratorio, costosos o poco '
     'accesibles para el productor rural colombiano.',
     'y su diagnóstico convencional depende de la inspección visual o de técnicas de laboratorio que '
     'requieren equipos y personal especializados.'),
    # TC-22
    ('son una de las formas de fuga de datos que inflan las métricas reportadas (Kapoor & Narayanan, 2023).',
     'son una de las formas de fuga de datos que inflan las métricas reportadas (Kapoor & Narayanan, 2023). '
     'Este trabajo documenta y mitiga casos de ese tipo en los dos corpus públicos de mango que utiliza.'),
    ('La metodología estándar de evaluación de detección de objetos sigue las recomendaciones revisadas por '
     'Padilla et al. (2020). El presente trabajo documenta y mitiga uno de tales casos sobre un corpus '
     'público de mango.',
     'Las métricas de detección de objetos de este trabajo (Sección 3.7) son las que revisan Padilla et al. '
     '(2020).'),
    # TC-23 and TC-24
    ('corpus de clasificación reveló una anomalía significativa. Aplicando el hashing perceptual '
     'imagehash.phash (Zauner, 2010) sobre las 1500 imágenes (1125 de entrenamiento, 300 de validación y 75 '
     'de prueba), se identificaron 76 pares',
     'corpus de clasificación, con el hash perceptual imagehash.phash (Zauner, 2010) sobre las 1500 '
     'imágenes (1125 de entrenamiento, 300 de validación y 75 de prueba), identificó 76 pares'),
    ('Una reejecución independiente reproduce exactamente los 76 pares',
     'Una nueva ejecución del detector de duplicados en esta revisión reproduce exactamente los 76 pares'),
    # TC-25 to TC-27
    ('La visión por computador y, en particular, el aprendizaje profundo, han emergido en la última década '
     'como herramientas con alto potencial diagnóstico en contextos agrícolas.',
     'En la última década, la visión por computador y, en particular, el aprendizaje profundo se han '
     'aplicado a la detección de enfermedades en cultivos.'),
    ('Adicionalmente, en Kapoor y Narayanan (2023) se documenta la fuga de datos no auditada como una causa '
     'frecuente de irreproducibilidad en aprendizaje automático aplicado.',
     'Kapoor y Narayanan (2023) documentan la fuga de datos no auditada como una causa frecuente de '
     'irreproducibilidad en el aprendizaje automático aplicado.'),
    ('La razón de emplear la modalidad clasificación —y no detección— se justifica por la naturaleza del '
     'corpus:',
     'Se usa la modalidad de clasificación, y no la de detección, por la naturaleza del corpus:'),
    ('Será la métrica honesta de desempeño en producción.',
     'Con ese conjunto podrá medirse el desempeño en condiciones de producción.'),
]
TABLE_CELLS = [(7, 2, 0, 'Cajas sintéticas en MangoDHDS', 'Etiquetas de imagen completa en MangoDHDS')]  # TC-28
FIGURES = {'word/media/image1.png': 'manuscript/figures/fig1_cascada.png'}  # TC-30: arrow «clase», figures.py

LETTER_EDITS = {
    '# Respuesta al dictamen': [('tras la pasada 2f', 'tras la pasada 2g')],
    '## REVIEW-01': [
        # TC-04
        ('3. Revisión visual de cada candidato por dos agentes de IA en instancias separadas (Claude Opus y '
         'Claude Sonnet), con un tercero (Claude Haiku) cuando discreparon. El ciego se impuso por '
         'instrucción, no por control de acceso, y ninguna decisión la revisó una persona.',
         '3. Revisión visual de cada candidato, primero con apoyo de agentes de IA: dos instancias separadas '
         '(Claude Opus y Claude Sonnet) y una tercera (Claude Haiku) para los desacuerdos, con un ciego '
         f'impuesto por instrucción y no por control de acceso. {MANUAL}'),
        # TC-05
        ('La adjudicación visual la hicieron agentes de IA, sin revisión humana: la Sección 3.3.1 lo declara, '
         'con los controles fallidos y los desacuerdos, y la re-adjudicación por personas queda como trabajo '
         'futuro.',
         'La adjudicación visual se apoyó primero en agentes de IA de fiabilidad limitada (controles '
         'positivos fallidos y desacuerdos frecuentes) y después la revisó manualmente una integrante del '
         'equipo; los grupos de la partición proceden de las decisiones registradas de la adjudicación. La '
         'Sección 3.3.1 lo declara.'),
        # TC-06
        ('**Estado.** RESUELTO PARCIALMENTE: la auditoría existe, pero su adjudicación visual la hicieron '
         'agentes de IA, sin revisión humana.',
         '**Estado.** RESUELTO, con los límites declarados.')],
}


def main() -> int:
    from revise_pass2b import replace_media
    before = sha(DOCX)
    d = docx.Document(DOCX)
    for old, new in EDITS:
        replace(d, old, new)
    for table, row, col, expected, new in TABLE_CELLS:
        found = d.tables[table].cell(row, col).text
        if found != expected:
            raise EditFailed(f'table {table} cell ({row}, {col}) is {found!r}, not {expected!r}')
        cell_text(d, table, row, col, new)
    d.save(DOCX)
    for name, source in FIGURES.items():
        replace_media(DOCX, name, ROOT / source)
    docx.Document(DOCX)
    raw = LETTER.read_bytes()
    newline = '\r\n' if b'\r\n' in raw else '\n'
    LETTER.write_bytes(apply(raw.decode('utf-8').replace('\r\n', '\n'), LETTER_EDITS)
                       .replace('\n', newline).encode('utf-8'))
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8'))
    entries.append({'pass': '2g', 'script': 'provenance/commands/task09/revise_pass2g.py',
                    'responds_to': 'reports/final_text_cleanup_audit.md TC-01 to TC-30; DECISION-040',
                    'before_sha256': before, 'after_sha256': sha(DOCX),
                    'figures': {k: sha(ROOT / f) for k, f in FIGURES.items()}})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(entries[-1], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
