"""Produce first-phase documentary deliverables from the existing evidence index."""
from pathlib import Path
import csv, hashlib, re

W = Path(__file__).resolve().parents[2]
R = W.parent
def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))
sources = read_csv(W/'provenance/source_manifest.csv')
by_path = {r['relative_path']:r for r in sources}
def link(relative, label=None, legacy=False):
    path=(R if legacy else W)/relative
    return f'[{label or relative}](<{path.as_posix()}>)'
def src(relative):
    row=by_path.get(relative)
    assert row, relative
    return f"{link(relative, legacy=True)} — **{row['source_id']}**, SHA256 `{row['sha256']}`"
def write(relative, content):
    (W/relative).write_text(content.strip()+'\n', encoding='utf-8')

derived = [
 ('DER-001','data/manifests/legacy_dataset_inventory.csv','Inventario de 7016 archivos de imágenes y referencias SRC de imagen/etiqueta'),
 ('DER-002','reports/datasets/counts_by_split_class.csv','Agregados del inventario por dataset/split/clase; instances es el conteo de objetos de esa clase'),
 ('DER-003','reports/datasets/dataset_archaeology.md','Interpretación documental y limitaciones de los inventarios'),
]
rows=[]
for eid,path,meaning in derived:
    rows.append(dict(evidence_id=eid,path=path,sha256=hashlib.sha256((W/path).read_bytes()).hexdigest(),
                     provenance='SRC-ID y hashes en DER-001; baseline provenance/source_manifest.csv',
                     producer='reports/datasets/inventory_legacy.py',meaning=meaning,scope='Snapshot local; no prueba identidad histórica del run'))
with (W/'provenance/derived_evidence_registry.csv').open('w',encoding='utf-8',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=rows[0]);wr.writeheader();wr.writerows(rows)

for path in [W/'docs/research/reviewer_matrix.md',W/'reports/reviewer_matrix.csv']:
    text=path.read_text(encoding='utf-8')
    text=text.replace('Python/Ultralytics/PyTorch/CUDA original, base checkpoint hash, log comando y hardware.',
                      'Ultralytics 8.4.39 identificada en ART-001; faltan Python/PyTorch/CUDA originales, hash de la base, comando y hardware exactos.')
    path.write_text(text,encoding='utf-8')

spec=W/'docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md'
text=spec.read_text(encoding='utf-8').replace('paso0.05','paso 0.05').replace('remuestras,seed','remuestras, seed').replace('recortes+llamadasM2','recortes + llamadas M2')
text=text.replace('`source_inventory.md`, `manuscript_genealogy.md`, `reviewer_matrix.md`, `claim_evidence_matrix.csv`, `experiment_registry.csv`, `artifact_registry.csv`', '`docs/research/source_inventory.md`, `docs/research/manuscript_genealogy.md`, `docs/research/reviewer_matrix.md`, `docs/research/claim_evidence_matrix.csv`, `provenance/experiment_registry.csv`, `provenance/artifact_registry.csv`')
text=text.replace('`artifact_registry.csv` enlaza', '`provenance/artifact_registry.csv` enlaza')
spec.write_text(text,encoding='utf-8')

risk=W/'docs/research/risk_register.md'
text=risk.read_text(encoding='utf-8')
fixes={'33imágenes/99instancias/13Enfermo':'33 imágenes / 99 instancias / 13 Enfermo','identifica8.4.39':'identifica 8.4.39',
'RaspberryPi':'Raspberry Pi','Tabla5 y Fig4':'Tabla 5 y Fig. 4','ymatching':'y matching','best métricasép137; mAP50máxép95; Rmáxép1 omitido':'best coincide con época 137; máximo mAP50 en época 95; máximo R en época 1 omitido',
'deun':'de un','deF1 ysumarios':'de F1 y sumarios','MacroF1matriz':'Macro F1 de matriz','usaM1':'usa M1',
'editorial106698 ajeno aVanDerHeijden':'editorial 106698 ajeno a Van der Heijden','yalcance':'y alcance',
'temporalidad,epidemiología oGT':'temporalidad, epidemiología o GT','oretirar':'o retirar','ybbox':'y bbox',
'multipunto,568bbox':'multipunto, 568 bbox','siese':'si se','ypuede':'y puede',
'make_cls_layout/log e igualdad por hash por revisar':'make_cls_layout/log y correspondencia local por hash comprobada; vínculo histórico incompleto',
'+assert':'y aserción','mismomembership':'misma membresía','deltest':'del test','100pares':'100 pares',
'porimagen yCI porcluster':'por imagen y CI por cluster','quecluster':'que cluster','yfiguras':'y figuras',
'Fig1 dice Roboflowpropio/5enfermedades':'Fig. 1 dice Roboflow propio / 5 enfermedades','defiguras yrevisar':'de figuras y revisar',
'altest':'al test','accesslogs':'logs de acceso','historiaprevia':'historia previa','ystatus':'y status','alfinal':'al final',
'delhash':'del hash','33test':'33 imágenes de test','porclase':'por clase','dereentrenar':'de reentrenar',
'alrun deforma':'al run de forma','sinoutputs':'sin outputs','yartifactregistry':'y registro de artefactos','delpasado':'del pasado'}
for old,new in fixes.items(): text=text.replace(old,new)
risk.write_text(text,encoding='utf-8')

write('docs/research/methodology_decisions.md', '''
# Decisiones metodológicas propuestas

Estas decisiones forman parte de la SPEC sometida a aprobación. No se han ejecutado experimentos nuevos.

|Decisión|Regla concreta|Justificación y límite|Tarea|
|---|---|---|---|
|Unidad de independencia|Fruto, escena o secuencia documentada; grupo conservador si el origen sólo es probable|pHash y filename no demuestran identidad biológica|02–03|
|Similitud|SHA256 y pHash64 Hamming <5; banda 5–10 revisada sin consultar rendimiento|Conservar relaciones exactas, cercanas, posibles y confirmadas separadas|02|
|Split M1|Mantener sólo si auditado; cambio obliga a reentrenar desde base|Grupos atómicos, seed 42, objetivo 70/15/15; algoritmo y bloqueos definidos en SPEC §6|03–04|
|M2|Auditar clean y cls, sin regeneración automática|Contaminación o entrada histórica no reconciliada exige enmienda antes de reentrenar|02,05|
|Entorno nuevo|Python 3.12.14 y Ultralytics 8.4.52 propuestos; compatibilidad pendiente|Reconstruido, no idéntico al M1 histórico 8.4.39; todas las cachés y temporales contenidos|01|
|Checkpoint|Fitness sin redondear, último empate máximo según guardado nativo|Registrar época y hash de pesos conservados antes/después del stripping; nunca elegir desde CSV redondeado|04|
|Punto operativo|F2 de Enfermo en validación, rejilla .05:.05:.95, empate menor umbral|Regla prefijada que prioriza recall; AP con score mínimo .001 separado de confusión|05|
|Incertidumbre|95%, bootstrap 2000, seed 42, grupos de adquisición; Wilson sólo para Bernoulli independiente|Menos de 2 grupos por clase o >5% indefinidas bloquea CI de esa clase; intervalos no corrigen sesgo|05|
|Latencia|Equipo real, batch 1, FP32, 10 warmups y 100 repeticiones por imagen|Pool ≤32 de validación fijado por hashes y estratos; separar tiempos internos, wall, cascada y archivo→JPEG|06|
|GT conjunto|Cajas y enfermedad específica por fruto, adjudicación independiente|No usar predicciones como verdad ni multiplicar recalls de datasets distintos|07|
|Fuente editorial|Copiar DOCX ALBUS después de autorización; render final|Texto normalizado coincide con PDF enviado; conservar originales y registrar cambios|09|

Los contratos completos, incluyendo fórmulas, casos de error y rutas, están en `docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md` y en las tareas correspondientes del plan. DECISION-001–017 registra la razón; una incompatibilidad material requiere una enmienda documentada, no una sustitución silenciosa.
''')

decisions=W/'docs/research/decision_log.md'
text=decisions.read_text(encoding='utf-8')
text += '''

## Decisiones tras revisión independiente

|ID|Fecha|Pregunta y evidencia|Decisión propuesta|Alternativa y riesgo|Artefactos|
|---|---|---|---|---|---|
|DECISION-015|2026-09-17|RIR-01: guardado nativo sobrescribe best en empate y CSV pierde precisión|Usar último máximo nativo con fitness sin redondear y hashes antes/después de stripping|Primera época requeriría retención distinta; se evita declarar pesos inexistentes|SPEC §7; TASK-04|
|DECISION-016|2026-09-17|RIR-02/03: versión inconsistente y cachés globales|Un entorno reconstruido 8.4.52, preservando metadata histórica 8.4.39; redirección antes de instalar/importar y prueba en hijo|Dos entornos añadirían coste sin recuperar las dependencias M1 desconocidas; compatibilidad nueva aún no probada|SPEC §4/7; TASK-01|
|DECISION-017|2026-09-17|RIR-04/05: YAML no prueba conteos ni cajas originales|Registrar DER-001/002/003, enlazar conteos locales y moderar CLAIM-031|No elevar observación de layout derivado a procedencia original|claim matrix; derived_evidence_registry|
'''
decisions.write_text(text,encoding='utf-8')

review_rows=read_csv(W/'reports/reviewer_matrix.csv')
response=['# Borrador de respuesta al revisor — primera fase\n\n**No es una carta final ni está lista para enviar.** Las acciones siguientes están propuestas, no realizadas. El comentario es un resumen fiel del dictamen SRC-MAIL. No se ha modificado el manuscrito y no se asignan páginas finales ficticias.\n']
for row in review_rows:
    response.append(f"## {row['review_id']}\n\n**Comment:** {row['reviewer_comment']}\n\n**Interpretation:** {row['technical_interpretation']}\n\n**Response propuesta:** {row['required_action']} La ejecución depende de {row['implementation_tasks']}; no se declara resuelto este punto.\n\n**Evidence disponible:** {row['current_evidence']} Evidencia todavía necesaria: {row['missing_evidence']}\n\n**Changes in Manuscript:** Pendientes. Secciones previstas: {row['manuscript_sections']}. Cambio previsto: {row['manuscript_change']}\n\n**Status:** {row['status']}. Decisión metodológica: {row['decision']}.\n")
write('docs/response_to_reviewers.md','\n'.join(response))

write('reports/spec_self_review.md', '''
# Self-review de la SPEC

Alcance: diseño documental de primera fase, no validación de datos ni modelos. Se realizó una segunda lectura como investigador externo siguiendo fuente→dato→run→claim, sin asumir que el nombre de un archivo prueba procedencia.

|Pregunta de revisión|Resultado y corrección|
|---|---|
|¿Responde a la solicitud real y al dictamen?|18 REVIEW-ID cubiertos. Se conserva el gate conjunto y la prohibición de nuevos experimentos en esta fase.|
|¿Distingue hechos e inferencias?|PDF confirmado por usuario; texto DOCX normalizado idéntico; época 137 inferida de métricas; origen exacto de entradas históricas no certificado.|
|¿Una auditoría sin pares puede llamarse limpia?|No. SHA/pHash, nombres, secuencias y dependencia biológica se distinguen; limitaciones explícitas.|
|¿La política de split es ejecutable?|Se precisó coste global normalizado, desempates, seed y condiciones de bloqueo. No se fragmentan grupos para fabricar test.|
|¿El checkpoint seleccionado existe?|RIR-01 corrigió el desempate: último máximo nativo, fitness sin redondear, registro de época y hash, conservación antes del stripping.|
|¿Hay contradicción de versiones?|RIR-03: un entorno reconstruido 8.4.52 propuesto; 8.4.39 permanece como evidencia histórica. Compatibilidad queda por comprobar antes de ejecutar.|
|¿Puede el runtime escribir en legacy/perfil global?|RIR-02 añadió redirección antes de instalar/importar y comprobación de rutas efectivas en proceso hijo. El aislamiento de diseño no equivale a una prueba de ejecución ya superada.|
|¿Los intervalos respetan dependencia y pequeños n?|Unidad grupo cuando existe; indefinición explícita; Wilson restringido; no se afirma que el CI elimine sesgo.|
|¿El benchmark promete lo que no mide?|Define archivo→JPEG con pesos residentes y etapas internas separadas; excluye red/API/SQLite, cold-start aparte. Pi exige hardware real.|
|¿La cascada puede evaluarse ahora?|No: falta GT específico por fruto. Se rechaza convertir predicciones en etiquetas; entregable futuro condicionado.|
|¿El plan puede cerrar con limitaciones?|Sí, retirando/moderando claims y respondiendo con causa, sin declarar resuelto experimentalmente lo bloqueado ni anticipar aceptación del congreso.|
|¿La fuente editable y bibliografía se eligen por comodidad?|No: genealogía y plantilla oficial respaldan DOCX; las 23 referencias necesitan auditoría completa posterior.|

RIR-04/05 corrigieron además la matriz de evidencia: conteos enlazados al manifiesto derivado y afirmación sobre cajas originales moderada. RIR-06 motivó lectura y corrección editorial completa. La revisión externa se conserva en `research_independent_review.md`; su relectura posterior debe comprobar la resolución sin reemplazar esta self-review.

Conclusión documental: diseño concreto para aprobación, con dependencias bloqueadas explícitas. La aprobación humana y todos los gates experimentales siguen pendientes.
''')
write('reports/plan_self_review.md', '''
# Self-review y coherencia del plan

Primera fase: no se han ejecutado los comandos científicos que contiene el plan. Las CLIs y tests son entregables futuros identificados como tales.

- Las diez tareas incluyen FILES, CONSUMES, PRODUCES, PRECONDITIONS, STEPS, TESTS / VERIFICATION COMMANDS, EXPECTED RESULTS, ARTIFACTS y REVIEW-IDs SATISFIED. La matriz final cubre los 18 requisitos.
- El orden fija procedencia→auditoría→split→entrenamiento condicional→evaluación antes de editar métricas. Un bloqueo no se transforma en ejecución ficticia. No hay código de modelo nuevo en `src/` ni tests científicos implementados ahora.
- Se corrigió la selección de pesos: el test verifica ruta/hash y precisión, incluidos empates y valores distintos que colapsan a seis cifras; un entero epoch no basta.
- TASK-01 redirige configuración/cachés/temporales antes de venv/pip/imports, y exige una prueba del aislamiento en proceso hijo. La versión común coincide con la SPEC; la instalación no se presenta como realizada.
- El fixture de split usa `validate_group_atomicity` y exige el error `GROUP_CROSSES_SPLIT:g`; así no pasa por una ruta/label ausente. La validación completa prueba por separado las restantes entradas.
- El algoritmo del pool del benchmark es determinista por estrato y hash. El reloj falso distingue suma de etapas y temporizador exterior, evitando exigir una igualdad falsa.
- Los números sintéticos de clasificación, matching, abstención y bootstrap verifican el método; ninguna prueba impone rendimiento mínimo al modelo.
- Se conserva el esquema de GT y una salida de bloqueo útil aunque no haya anotaciones. La revisión bibliográfica es primaria y semántica, no sólo regex.
- El plan exige render y lectura visual de todas las páginas antes de afirmar build/manuscrito final correctos. Ni DOCX ni PDF fueron editados en esta fase.
- La última tarea requiere un revisor científico fresco y reproducción desde entorno limpio. La revisión del diseño actual no sustituye esa revisión adversarial final.

Relectura editorial: se restauraron espacios, frases y nombres; se conservaron comandos y valores. La verificación administrativa revisa además campos, IDs, cobertura y hashes. Ninguna casilla de implementación queda marcada como realizada. Resultado: plan listo para revisión humana una vez comprobados sus artefactos actuales.
''')

write('reports/design_review_resolution.md', '''
# Resolución documental de revisión independiente

El snapshot original y sus hallazgos se preservan en `research_independent_review.md`. Las correcciones se limitan a documentos de propuesta y matrices; no se ejecutó el plan.

|Hallazgo|Cambio concreto|Evidencia a releer|Estado de corrección|
|---|---|---|---|
|RIR-01 HIGH|Último máximo nativo con precisión completa; callback y retención/hash antes y después de stripping; pruebas de bytes y empate|SPEC §7; TASK-04|IMPLEMENTED_IN_DESIGN; relectura independiente solicitada|
|RIR-02 HIGH|Variables antes de pip/imports, rutas efectivas comprobadas en hijo y bloqueo por escape|SPEC §4; entorno y TASK-01|IMPLEMENTED_IN_DESIGN; ejecución futura pendiente|
|RIR-03 MEDIUM|Entorno reconstruido común 8.4.52; 8.4.39 histórico conservado y REVIEW-09 actualizado|SPEC §7; TASK-01; matriz REVIEW|IMPLEMENTED_IN_DESIGN|
|RIR-04 MEDIUM|DER-001/002 enlazados desde CLAIM-004/005/009; alcance snapshot local|derived_evidence_registry.csv; claim matrix|CORRECTED_DOCUMENTARY_TRACEABILITY|
|RIR-05 MEDIUM|CLAIM-031 parcialmente soportado; no acredita cajas originales. DATA-006 es localización mango|claim matrix; REVIEW-11|CORRECTED_DOCUMENTARY_SCOPE|
|RIR-06 MEDIUM|Lectura completa y corrección de texto pegado, conservando comandos y cifras|SPEC; plan; risk register|CORRECTED_PROSE|

El estado de corrección no significa que el método esté implementado o validado en ejecución. La relectura independiente se registra por separado y no se sustituye por esta respuesta del autor del diseño.
''')

summary=f'''
# Informe ejecutivo de primera fase — ALBUS26-116

Fecha: 2026-09-17. Se ha completado investigación documental, inventarios y propuestas. No hay entrenamiento, inferencia, pHash nuevo, splits nuevos ni cambios científicos del manuscrito. Las comprobaciones aritméticas sólo contrastan artefactos existentes. Confianza HIGH/MEDIUM/LOW califica cada conclusión documental; no equivale a validez científica del resultado.

## 1. ¿Cuál fue exactamente el manuscrito sometido?

{src('Articulo_Mango_ALBUS.pdf')}. Es el PDF de 16 páginas confirmado expresamente por el usuario. **HIGH**, por confirmación y archivo identificado. El dictamen SRC-MAIL usa algunas páginas que no coinciden; se conserva esa discrepancia, sin sustituir el archivo por otra versión. La identidad no se dedujo del nombre v9. Relacionado: REVIEW-14/18, GENE-001, DECISION-002.

## 2. ¿Cuál es la fuente editable más probable?

{src('Articulo_Mango_ALBUS.docx')}. **HIGH**: texto normalizado del DOCX y PDF idéntico en 33.468 caracteres; SHA256 del texto normalizado `9f80a981be79aeab9f9e068c1adc6e1639681aaaaf09e06cdd7c7a7a4920773e`. Siete imágenes del DOCX coinciden binariamente con v9. Esto demuestra contenido normalizado, no igualdad de maquetación ni que otro archivo no se usara al exportar. Se propone copiar este DOCX como fuente canónica sólo tras aprobación. GENE-001/002; REVIEW-14/16/18.

## 3. ¿Cuál es la genealogía?

{link('docs/research/manuscript_genealogy.md')} documenta GENE-001–009 con hashes, fechas, títulos, secciones, tablas, figuras y referencias. Las carpetas v4–v6 conservan texto/bibliografía y cambian imágenes. El ZIP v8 coincide 16/16 y v9 17/17 con sus carpetas; v7 sólo 12/16 y el ZIP base 3/16, por lo que no son copias intercambiables. v9 es respaldo LaTeX próximo al DOCX, pero tiene título/formato distinto. No existe una secuencia lineal fiable inferible sólo por los números de versión. **HIGH** para comparaciones de bytes/texto; **MEDIUM** para orden causal de ediciones sin historial completo. REVIEW-14/18.

## 4. ¿Dónde está el código del Modelo 1?

- Evaluación: {src('Articulo/scripts/evaluate_detector_test.py')} — EXP-002/003.
- Servicio binario: {src('SemilleroTI-Mangos/core/vision.py')}, llamado desde {link('SemilleroTI-Mangos/api/routers/inference.py',legacy=True)}.
- Entrenamiento publicado: {src('SemilleroTI-Mangos/docs/Yolo26n-model-docs/Entrenamiento-1/args.yaml')} y {link('SemilleroTI-Mangos/docs/Yolo26n-model-docs/Entrenamiento-1/resultados/results.csv',legacy=True)} — EXP-001. **No se localizó el script/notebook ejecutado de ese entrenamiento**; el trainer genérico del otro repo no prueba ese run.

**HIGH** para rutas y comportamiento actual; **MEDIUM** para vínculo histórico parcial. REVIEW-03/09.

## 5. ¿Dónde está el código del Modelo 2?

{src('Mango-vision/src/training/train_cls.py')}. La preparación de layout está en {link('Mango-vision/src/data_prep/make_cls_layout.py',legacy=True)}; evaluación en {src('Articulo/scripts/evaluate_classifier.py')}. EXP-004/005: log {link('Articulo/reports/train_cls_log.txt',legacy=True)}, checkpoint ART-002 y matriz de 219 imágenes. **HIGH** en identificación y evidencia local; la membresía histórica exacta no quedó congelada. REVIEW-09/15.

## 6. ¿Dónde está la cascada?

{src('SemilleroTI-Mangos/core/cascade.py')}, invocada por {link('SemilleroTI-Mangos/run_cascade.py',legacy=True)} y {link('Articulo/figs/fig7_cascade_demo.py',legacy=True)} — EXP-007. La API de `api/routers/inference.py` utiliza `core/vision.py`, que ejecuta sólo M1. **HIGH**: el flujo actual no demuestra integración de cascada en la API ni diagnóstico end-to-end validado. REVIEW-07/12/13; CLAIM-039; DECISION-012.

## 7. ¿Dónde están los datasets?

|ID|Ruta absoluta|Snapshot observado|Confianza|
|---|---|---|---|
|DATA-001|{link('SemilleroTI-Mangos/docs/MangosDataset',legacy=True)}|669 imágenes: 502/134/33; 1.854 cajas, dos clases. Test: 99 cajas, 13 Enfermo|HIGH|
|DATA-002|{link('Mango-vision/MangoDHDS A Dataset of Diseased and Healthy Mangoe',legacy=True)}|1.500 imágenes sin split; 300 por cada una de cinco clases|HIGH|
|DATA-003|{link('Mango-vision/DatasetMango_YOLO',legacy=True)}|1.500: 1.125/300/75; cajas de imagen completa en layout derivado|HIGH|
|DATA-004|{link('Mango-vision/DatasetMango_YOLO_clean',legacy=True)}|1.500: 1.064/217/219; copias exactas conservadas dentro de splits|HIGH|
|DATA-005|{link('Mango-vision/DatasetMango_cls',legacy=True)}|Misma membresía, hash y clase que DATA-004, con valid→val|HIGH|
|DATA-006|{link('Mango-vision/DatasetMango_Propias',legacy=True)}|173: 121/35/17; una clase mango; 568 bbox + 965 polígonos. Sin diagnóstico específico|HIGH|
|DATA-007|{link('Mango-vision/Datasets Sucios personal/Camara VIVO Y21',legacy=True)}|174 fotografías sin GT diagnóstico; 173 nombres normalizados relacionados con exportación|HIGH para inventario; MEDIUM para relación de transformación|
|DATA-008|Ruta configurada DatasetMango_Detector|No localizada; configuración no equivale a datos presentes|HIGH para ausencia en corpus inventariado|

DER-001/002/003: {link('provenance/derived_evidence_registry.csv')}; {link('reports/datasets/dataset_archaeology.md')}. Los 7.016 archivos son representaciones y copias, no 7.016 observaciones independientes. Los campos `box_rows/polygon_rows` por clase cuentan filas de imágenes que contienen esa clase; para número de objetos por clase usar `instances`. REVIEW-01/02/04/11/13.

## 8. ¿Dónde están los checkpoints?

|ART-ID|Ruta|SHA256|
|---|---|---|
|ART-001|{link('SemilleroTI-Mangos/models/best.pt',legacy=True)}|`595fa3ea9b0670f63289529bde3333124ff1179588b52fbe16c9c454b6e488de`|
|ART-002|{link('Mango-vision/models/clasificador_enfermedad.pt',legacy=True)}|`e277717e6ca9d7f308d22697550a5a4e80613929acb68eeb790f3304ebfdb08e`|
|ART-003|{link('SemilleroTI-Mangos/models/clasificador_enfermedad.pt',legacy=True)}|Igual a ART-002|
|ART-004|{link('Mango-vision/yolo11n-cls.pt',legacy=True)}|`c62d41bf9625777760018bf914d2e6cd472420ccd01706d97a61cb6c82502bd7`|

**HIGH** para identidad actual. ART-004 presente no prueba que sus bytes fueran la base exacta del entrenamiento histórico. La base M1 `yolo26n.pt` no está identificada por hash histórico. Metadata inspeccionada estáticamente, sin cargar pickle ni modelos. REVIEW-09; {link('provenance/artifact_registry.csv')}.

## 9. ¿Qué experimentos pueden trazarse?

|EXP|Evidencia recuperada|Límite|Confianza|
|---|---|---|---|
|001 M1 train|args, 150 filas, checkpoint y métricas embebidas|Faltan comando, entorno completo, base y manifest históricos|HIGH documental, MEDIUM procedencia|
|002 M1 test AP|script, CSV global y por clase|Sin predicciones ni hash de ejecución|MEDIUM|
|003 M1 confusión|mismo script con conf .25 y matriz|Protocolo distinto de EXP-002|MEDIUM|
|004 M2 train|script, log CPU, 27 épocas y mejor 12, pesos|Sin manifest inmutable del run|HIGH documental, MEDIUM procedencia|
|005 M2 test|script, matriz y CSV, 219 casos|Sin ejecución nueva ni predicciones individuales|MEDIUM|
|006/007 galerías|scripts, figuras, seeds y umbrales|Cualitativas; no GT diagnóstico conjunto|HIGH identificación; LOW para eficacia clínica|
|008/009 latencias|Claims del PDF|Sin run recuperado ni tiempos crudos|LOW|

{link('provenance/experiment_registry.csv')}: nueve registros, todos `reproduced=NO`. {link('reports/experiments/experiment_archaeology.md')}. REVIEW-03/05/07/08/09/13.

## 10. ¿Qué métricas pueden reproducirse?

**Ninguna se ha reproducido experimentalmente en esta fase.** Hay entradas suficientes para proponer reevaluaciones M1/M2, condicionadas a auditoría de datos y compatibilidad. Sí puede comprobarse aritméticamente lo que dicen las matrices existentes: M2 tiene 199/219 aciertos (0,9086758), macro F1 0,9094733 y F1 Cancro 0,8314607. A tres decimales corresponden 0,909 y 0,831, mientras el paper usa doble redondeo para F1. Esto no prueba la validez del test ni modifica el manuscrito.

EXP-003 permite reconstruir P/R/F1 del umbral .25 desde su matriz; EXP-001 permite recuperar máximos y valores de época del CSV. AP necesita detecciones/puntuaciones individuales o una nueva inferencia; no se reconstruye desde una matriz de confusión. **HIGH** aritmética, **UNVERIFIED** reproducción experimental. REVIEW-04/05/09; {link('reports/experiments/csv_arithmetic_check.json')} y verificación fresca de primera fase.

## 11. ¿Qué métricas carecen de procedencia suficiente?

145 ms CPU, rendimiento Raspberry Pi, eficacia diagnóstica conjunta, detección temprana y generalización rural no tienen la evidencia experimental necesaria. P/R/F1 de Tabla 5 y Fig. 4 responden a umbrales/matching distintos. La validación del best.pt coincide con época 137, pero el pico mAP50 usado en la comparación histórica es de época 95; no son el mismo punto del entrenamiento. El supuesto máximo de recall omite época 1. Las inferencias de época son fuertes, pero no reemplazan el log original. **HIGH** para identificar el hueco; **LOW** para sostener los claims cuantitativos ausentes. EXP-001/002/003/007/008/009; REVIEW-03/07/08/09/10/11/13.

## 12. ¿Existe evidencia preliminar de leakage?

Sí. DATA-003 tiene 41 pares de archivos binariamente iguales entre splits (29 train-valid, 10 train-test, 2 valid-test). DATA-004/005 no tienen esos cruces exactos; los 76 pares del reporte pHash histórico están coasignados. No se recalculó pHash ni se certifica independencia biológica. En M1, 432 nombres sakit_mp4 están repartidos 329/85/18 entre splits y siete bases freshMango aparecen en más de uno: **indicios temporales**, aunque los 669 hashes sean únicos. En DATA-006 nueve ráfagas nominales cruzan train/valid y cinco también test. **HIGH** para duplicación binaria y nombres; **MEDIUM** para inferencia de secuencia compartida hasta recuperar origen. DER-001/003; REVIEW-01/02/03.

## 13. ¿Qué comentarios requieren nuevos experimentos?

REVIEW-01/02: auditoría de similitud/procedencia y partición; REVIEW-03: reentrenamiento M1 sólo si cambia el split o la auditoría lo exige, seguido de evaluación; REVIEW-05: incertidumbre desde predicciones conservadas; REVIEW-07: benchmark real. REVIEW-08 requiere Pi real para producir cifras. REVIEW-13 exige GT específico conjunto; REVIEW-11 exige datos externos independientes si se quiere reclamar validación rural. REVIEW-09 requiere una reevaluación reconstruida además de investigación de procedencia. **HIGH** sobre necesidad; resultados todavía desconocidos. TASK-01–07.

## 14. ¿Qué comentarios sólo requieren cambios editoriales?

REVIEW-06 (desbalance no implica prevalencia), REVIEW-10 (retirar temporalidad no demostrada), REVIEW-14 (redacción), REVIEW-15 (nombres y taxonomía) y REVIEW-16–18 (normas y auditoría bibliográfica) no exigen entrenamiento. REVIEW-04 admite hacer explícitos n y limitación; sus intervalos pertenecen a REVIEW-05. La limitación rural de REVIEW-11 y la explicación de propagación de REVIEW-12 pueden corregirse editorialmente, pero no convierten en validada la cascada. Fig. 1 debe corregir origen del dataset y cuatro enfermedades + Saludable; descripción API/cascada debe reflejar rutas reales. **HIGH**; TASK-08/09, con investigación primaria para referencias.

## 15. ¿Qué está bloqueado?

- REVIEW-13: **BLOCKED_BY_GROUND_TRUTH**, sin enfermedad específica por fruto en escenas de detección.
- REVIEW-08: medición **BLOCKED_BY_HARDWARE**, no hay acceso documentado a Pi en esta fase. Se puede retirar el claim y responder con limitación.
- REVIEW-09: reproducción histórica exacta M1 bloqueada por entorno/base/comando incompletos; una reevaluación reconstruida es distinta y está planificada.
- REVIEW-02: confirmación de secuencias pendiente de originales; agrupamiento conservador permite avanzar sólo si deja unidades suficientes.
- REVIEW-18: referencia Van der Heijden / artículo 106698 discrepante; requiere identificar fuente, sustituirla justificadamente o retirar el claim.

Todas las implementaciones están además pendientes de aprobación SPEC+plan. **HIGH** para los huecos observados, sin suponer que archivos externos no aportados no existan. {link('docs/research/risk_register.md')}.

## 16. ¿Qué riesgos nuevos se descubrieron?

La API actual sólo usa M1; los puntos operativos del paper difieren; el best checkpoint no coincide con el pico mAP50; el máximo de recall excluye una época; hay doble redondeo en F1; el YAML clean aún apunta al dataset original; galerías usan transformaciones BGR/RGB que deben reconciliarse; los datos propios mezclan cajas y polígonos legítimos sin diagnóstico; el test ya examinado no es prospectivo; las figuras conservan taxonomía/procedencia incorrectas y hay una referencia editorial discrepante. **HIGH** documental; impacto cuantitativo sin evaluar. RISK-01–20, CLAIM-001–050, REVIEW-01/03/05/09/11/13/14/15/18.

La revisión independiente del diseño añadió dos riesgos de implementación: elegir una época sin conservar sus pesos y dejar cachés globales fuera del workspace. Ambos se incorporaron a la SPEC/plan mediante contratos y pruebas propuestas. RIR-01/02; DECISION-015/016. No se afirma que esas pruebas futuras ya pasen.

## 17. ¿Qué hará exactamente el plan tras aprobarse?

1. Congelar entradas y preparar entorno aislado reconstruido, con prueba de rutas y hashes.
2. Auditar M1 por igualdad, similitud y origen; comprobar M2 y sus layouts.
3. Conservar o proponer un único split por grupos, con manifest/hash y bloqueo si faltan unidades.
4. Reentrenar M1 desde base sólo si corresponde; conservar el checkpoint realmente seleccionado y toda su procedencia.
5. Evaluar pesos congelados con AP y punto operativo definidos, predicciones individuales e intervalos apropiados.
6. Medir tiempos crudos sobre hardware real; Pi sólo si se dispone de ella.
7. Preparar contrato/evaluador de cascada; métricas únicamente con GT conjunto independiente.
8. Auditar las 23 referencias contra fuentes primarias y normas ALBUS/APA7.
9. Editar una copia del DOCX canónico y regenerar tablas/figuras/respuesta desde artefactos; renderizar e inspeccionar todas las páginas.
10. Verificar desde entorno limpio y someter el resultado a revisión adversarial fresca; cerrar cada requisito con evidencia o bloqueo justificado.

Cada tarea fija archivos, entradas, salidas, precondiciones, tests, comandos y criterios de revisión. **HIGH** para la definición del trabajo; no es una promesa de métricas favorables ni de aceptación editorial.

## Entrega para aprobación

{link('docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md','SPEC')} · {link('docs/superpowers/plans/2026-09-17-albus26-major-revision.md','Plan')} · {link('reports/spec_self_review.md','Self-review SPEC')} · {link('reports/plan_self_review.md','Self-review plan')} · {link('reports/research_independent_review.md','Revisión independiente inicial')} · {link('docs/final_validation_report.md','Validación de primera fase')}.

El estado READY_FOR_REVIEW se refiere exclusivamente a los documentos para aprobación. GATE A es documental; B/C esperan aprobación humana y D–I no están superados. La revisión científica completa no está DONE. Se solicita aprobación conjunta antes de ejecutar TASK-01.
'''
write('reports/first_phase_executive_report.md', summary)

write('README.md', f'''
# ALBUS26-116 — Major Revision

Workspace de reconstrucción científica. Primera fase: investigación documental y propuestas; no experimentos nuevos ni edición científica del manuscrito.

- {link('reports/first_phase_executive_report.md','Informe ejecutivo: 17 respuestas con evidencia')}.
- {link('docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md','SPEC para aprobación')} y {link('docs/superpowers/plans/2026-09-17-albus26-major-revision.md','Plan de 10 tareas')}.
- {link('docs/research/source_inventory.md','Inventario')}, {link('docs/research/manuscript_genealogy.md','genealogía')}, {link('docs/research/reviewer_matrix.md','18 requisitos')} y {link('docs/research/claim_evidence_matrix.csv','50 claims')}.
- {link('provenance/experiment_registry.csv','9 experimentos históricos')}, {link('provenance/artifact_registry.csv','100 artefactos')} y {link('provenance/source_manifest.csv','baseline de fuentes')}.
- {link('docs/final_validation_report.md','Comprobación de primera fase')} y {link('docs/response_to_reviewers.md','borrador de respuesta, no enviar')}.

Los originales están fuera de esta carpeta y son de sólo lectura. La carpeta contenedora no tiene Git; Mango-vision está en main y SemilleroTI-Mangos tenía cambios previos documentados. No se creó worktree ni se hizo commit. No ejecutar `provenance/commands/capture_sources.py` otra vez: reemplazaría el baseline. Los scripts documentales de generación son registros de esta sesión, no una canalización científica ni pasos para reconstruir el baseline.

La comprobación administrativa repetible es:

```powershell
& 'C:/Users/junio/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/provenance/commands/verify_first_phase.py'
```

`src/`, `tests/`, experimentos nuevos y manuscrito de revisión permanecen sin implementación. Todas las CLIs del plan son futuras. Aprobar SPEC y plan habilitará la ejecución por tareas; «continúa» durante esta primera fase no es esa aprobación. GT conjunto, Pi y procedencia histórica incompleta siguen siendo limitaciones explícitas.
''')
print('First-phase reports written; scientific sources not modified.')
