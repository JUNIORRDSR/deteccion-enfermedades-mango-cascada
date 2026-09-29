"""Administrative corrections to proposed documents; does not run scientific code."""
from pathlib import Path
import csv, re

ROOT = Path(__file__).resolve().parents[2]
spec_path = ROOT / 'docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md'
plan_path = ROOT / 'docs/superpowers/plans/2026-09-17-albus26-major-revision.md'
s = spec_path.read_text(encoding='utf-8')
p = plan_path.read_text(encoding='utf-8')

def replace_once(text, old, new):
    assert old in text, old[:120]
    return text.replace(old, new)

s = replace_once(s, 'Recuperar Ultralytics8.4.39 y hash de base; si no es técnicamente compatible con hardware disponible, documentar entorno nuevo y no llamarlo reproducción exacta.', 'Usar Ultralytics 8.4.52 en el entorno reconstruido común propuesto por TASK-01, previa comprobación de compatibilidad y recuperación del hash de la base. La metadata del M1 histórico identifica 8.4.39; conservar ese dato sin reemplazarlo por la versión nueva. Se elige 8.4.52 porque está documentada localmente para M2 y permite un único entorno de reevaluación, reduciendo variación operativa. Esta elección NO reproduce exactamente el runtime M1 histórico. Un fallo de compatibilidad exige enmienda explícita del entorno antes del run.')
s = replace_once(s, 'Seleccionar un solo checkpoint por máximo mAP50–95 de validation; desempate primera época.', 'Seleccionar un solo checkpoint por máximo mAP50–95 de validación, usando fitness sin redondear. Adoptar el desempate nativo de Ultralytics 8.4.52: última época que iguala el máximo. Verificar en el código instalado que el fitness del detector coincide con esta métrica; si no coincide, detener y enmendar el protocolo. Un callback posterior al guardado registra época (base 1), fitness y métricas sin redondear, así como el SHA256 del best.pt realmente escrito. Conservar una copia del último best nativo antes del stripping final y registrar el hash del artefacto final después de cualquier transformación. No reconstruir la selección desde results.csv de seis cifras significativas. Si faltan pesos o el vínculo entre época y hash, el run no pasa el gate de procedencia.')
s = replace_once(s, 'No usar hardlinks para archivos que un proceso pueda modificar; comprobar hashes legacy al terminar.', 'No usar hardlinks para archivos que un proceso pueda modificar; comprobar hashes legacy al terminar. Antes de instalar o importar dependencias, redirigir configuración, cachés y temporales al workspace según TASK-01, incluyendo YOLO_CONFIG_DIR, PIP_CACHE_DIR, TORCH_HOME, XDG_CACHE_HOME, MPLCONFIGDIR, TEMP y TMP. Desactivar bytecode fuera del workspace y las integraciones remotas opcionales. Un proceso hijo comprueba las rutas efectivas del runtime antes de permitir una ejecución científica; si aparece una ruta de escritura externa, detener y corregirla.')
s = replace_once(s, 'asignar cada grupo al split que minimice suma de desviaciones cuadráticas normalizadas respecto a tamaños/clases objetivo.', 'asignar cada grupo al split que minimice el coste global posterior a esa asignación: suma, sobre los tres splits y las dimensiones tamaño/instancias por clase, de ((conteo_actual − objetivo) / max(objetivo, 1))². Cada dimensión tiene peso 1; evaluar los tres destinos sin cambiar los grupos ya asignados.')
s = replace_once(s, 'Pool predefinido: hasta32 imágenes de validation, elegidas por orden SHA256 sin mirar latencia y cubriendo presencia/ausencia de Enfermo si existe;', 'Pool predefinido: hasta 32 imágenes de validación. Ordenar por (SHA256, image_id); elegir primero la primera imagen de cada estrato disponible (con Enfermo / sin Enfermo), completar hasta 32 con las restantes en ese orden y ejecutar en orden (SHA256, image_id), sin mirar latencia;')

env = '''$WorkspaceRoot = (Get-Location).Path
$StateRoot = Join-Path $WorkspaceRoot 'provenance/runtime_state'
New-Item -ItemType Directory -Force -Path $StateRoot | Out-Null
@{
    YOLO_CONFIG_DIR='ultralytics'; PIP_CACHE_DIR='pip'; TORCH_HOME='torch';
    XDG_CACHE_HOME='cache'; MPLCONFIGDIR='matplotlib'; TEMP='tmp'; TMP='tmp';
    HF_HOME='huggingface'; NUMBA_CACHE_DIR='numba'; PYTHONUSERBASE='python_user'
}.GetEnumerator() | ForEach-Object {
    $StatePath = Join-Path $StateRoot $_.Value
    New-Item -ItemType Directory -Force -Path $StatePath | Out-Null
    [Environment]::SetEnvironmentVariable($_.Key, $StatePath, 'Process')
}
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONNOUSERSITE='1'
$env:WANDB_DISABLED='true'
$env:WANDB_MODE='disabled'
$env:COMET_MODE='DISABLED'
'''
p = replace_once(p, '& $AuditPython -m venv .venv', env + '& $AuditPython -m venv .venv')
p = replace_once(p, '- [ ] Preparar entorno con comandos anteriores y capturar Python/platform,versiones,pip freeze,hardware real. Recuperar paquetes históricos sólo si hay fuente verificable; no sustituir registro8.4.39 del checkpoint por8.4.52.', '- [ ] Preparar el entorno con los comandos anteriores. Capturar Python, plataforma, versiones, pip freeze, hardware real y todas las variables de aislamiento. Conservar 8.4.39 como dato del M1 histórico y 8.4.52 como versión reconstruida elegida, conforme a la SPEC. Antes de importar YOLO, verificar en un proceso hijo que las variables están fijadas; después de importarlo, comprobar que los directorios efectivos de configuración, caché, pesos, datasets y runs quedan dentro del workspace. Configurar explícitamente los settings de Ultralytics para esas rutas y desactivar integraciones remotas. Probar que omitir YOLO_CONFIG_DIR falla antes de importar y que una ruta externa falla por su causa concreta. Revisar otros escritores del runtime instalado; si alguno usa una ruta externa, detener y corregirla antes de entrenar/evaluar. Guardar stdout, stderr, exit code y el informe de rutas.')
p = replace_once(p, '`select_epoch(rows:list[dict])->int` maximiza mAP50–95; en empate elige la primera época.', '`select_checkpoint(records:list[dict])->dict` selecciona el máximo fitness sin redondear y la última época en empate, usando registros del guardado nativo. Cada registro contiene epoch, fitness, métricas, checkpoint_path y SHA256. El resultado debe corresponder a los bytes conservados, no sólo a un número de época.')
start = p.index('```python\nfrom src.evaluation.train_model1 import select_epoch')
end = p.index('```', start + 4) + 3
p = p[:start] + '''El test usa tres archivos de pesos ficticios con hashes distintos y registros de guardado: épocas 95 (.80005), 137 (.80478) y 138 (.80478). Debe seleccionar la ruta y hash de 138. Otro caso usa .8047801 y .8047802, que colapsan al mismo texto con seis cifras significativas: selecciona el mayor sin redondear, incluso si es de una época anterior. Un hash cambiado o un artefacto ausente debe fallar. Estas pruebas usan bytes ficticios y no cargan ni entrenan modelos.''' + p[end:]
p = replace_once(p, '- [ ] Ejecutar una vez y conservar fallos. Aplicar systematic-debugging; no reintentar para mejorar el resultado. Comprobar la selección del checkpoint contra el historial. No evaluar test aquí.', '- [ ] Verificar el fitness efectivo en el código de la versión instalada. Registrar con callback on_model_save, después del guardado nativo, la época base 1, fitness y métricas sin redondear, y el hash de best.pt cuando se escribe. Conservar una copia de ese best antes del stripping final; registrar separadamente el hash final si se transforma. Configurar save=True; no seleccionar desde el CSV redondeado. Comprobar con fixtures la correspondencia entre pesos, hash y última época máxima.\n- [ ] Ejecutar una vez y conservar fallos. Aplicar systematic-debugging; no reintentar para mejorar el resultado. Reconciliar el registro de guardado, los hashes y el checkpoint final. Un guardado omitido por NaN/Inf o un vínculo ambiguo impide validar el run. No evaluar test aquí.')
p = replace_once(p, 'from src.leakage_audit.split import validate_split, assign_groups', 'from src.leakage_audit.split import validate_group_atomicity, assign_groups')
p = replace_once(p, 'try: validate_split(rows)\nexcept ValueError: pass', "try: validate_group_atomicity(rows)\nexcept ValueError as exc: assert str(exc) == 'GROUP_CROSSES_SPLIT:g'")
p = replace_once(p, '`validate_split(rows:list[dict])->None`;', '`validate_group_atomicity(rows:list[dict])->None` comprueba sólo los campos de agrupamiento; `validate_split(rows:list[dict])->None` añade rutas, hashes, clases y esquema completo;')
p = replace_once(p, 'Un reloj falso incrementa 1 ms por lectura; dos etapas medidas suman 2 ms.', 'Un reloj falso incrementa 1 ms por lectura; cada etapa con dos lecturas dura 1 ms y dos etapas suman 2 ms. El tiempo exterior se calcula con sus propias lecturas y puede ser mayor: no igualarlo automáticamente a la suma ni contabilizarlo dos veces.')
p = replace_once(p, '- [ ] Congelarpoolhasta32validation por SHA y presenciaEnfermo; guardarselecciónantesdeverlatencias. Guardar frutospredichos/llamadasM2 yfallos. No descartarlosporserlentos.', '- [ ] Congelar el pool de hasta 32 imágenes de validación mediante el algoritmo por estratos y orden (SHA256, image_id) de la SPEC. Guardar la selección antes de observar latencias. Conservar el número de frutos predichos, llamadas M2 y fallos; no descartar ejecuciones por ser lentas.')

# Editorial repairs affect prose only; commands and fenced Python are preserved.
fixes = {
'para669':'para 669', 'No presentar11/13':'No presentar 11/13', 'aLaTeX':'a LaTeX',
'época137':'época 137','época95':'época 95','mejor12':'mejor 12','CSV150':'CSV de 150',
'Ryzen5':'Ryzen 5','Python3.':'Python 3.','Ultralytics8.':'Ultralytics 8.','torch2.':'torch 2.',
'seed42':'seed 42','seed0':'seed 0','objetivo70/15/15':'objetivo 70/15/15','150épocas':'150 épocas',
'distancia exactamente5':'distancia exactamente 5','Distancia exactamente5':'Distancia exactamente 5','banda5–10':'banda 5–10',
'YOLO26n,640,batch16,150 épocas,patience100,seed 0':'YOLO26n, tamaño 640, batch 16, 150 épocas, patience 100 y seed 0',
'Ultralytics 8.4.52,torch 2.12.0,torchvision0.27.0,NumPy2.4.4,Pillow12.2.0,ImageHash4.3.2,scikit-learn1.8.0':'Ultralytics 8.4.52, torch 2.12.0, torchvision 0.27.0, NumPy 2.4.4, Pillow 12.2.0, ImageHash 4.3.2 y scikit-learn 1.8.0',
'Tabla5':'Tabla 5','Fig4':'Fig. 4','macroF1':'macro F1','1.500membresías':'1.500 membresías',
'hashes imagen/label/clase y aliasvalid→val, yauditar YAML aoriginal':'hashes de imagen, etiqueta y clase (la clasificación usa la clase de carpeta, sin label de cajas); comprobar el alias valid→val y el YAML que apunta al dataset original',
'frente a76pares':'frente a los 76 pares','splitnuevo':'split nuevo','conlimitaciones':'con limitaciones',
'M2contaminado':'M2 contaminado','dereentrenamientoM2':'de reentrenamiento M2',
'CSVUTF8':'CSV UTF-8',' yhash':' y hash',' deworkspace':' del workspace','no sepuedeseparar':'no se puede separar',
'fallaantesdeescribir':'falla antes de escribir','ejecucionesidénticas':'ejecuciones idénticas',
'no timestampsenCSV':'sin timestamps en el CSV','gruposdemasiadograndes yclaseausente→bloqueoconcreto, sinajustarseed':'grupos demasiado grandes y clase ausente: bloqueo concreto, sin ajustar la seed',
'splitfreeze y hash,config históricaEXP-001,checkpointbase con hash recuperado; entornoTASK-01':'split congelado y hash, configuración histórica EXP-001 y checkpoint base con hash recuperado; entorno TASK-01',
'validando0≤hash<2**64':'validando 0 ≤ hash < 2**64','frontera4/5':'frontera 4/5',
'baseM1':'base M1','CLIevaluate':'CLI evaluate','CLIintervals':'CLI intervals',
'desdeconteosfullprecision; Wilsonstd; matchingdeterminista':'desde conteos sin redondear; Wilson con stdlib; matching determinista',
'F2validationrejilla .05..95,paso.05,empate menor,registrar threshold porreglaprefijada':'Seleccionar F2 en validación con rejilla .05..95, paso .05 y empate a menor umbral; registrar la regla y el umbral',
'P/RdelpicoF1testcomo thresholddeproducción':'P/R del pico F1 en test como umbral de producción',
'protocoloSPEC':'protocolo de la SPEC','figuras/tablas,claimmatrix':'figuras, tablas y matriz CLAIM',
'md`,changelog yartifactregistry':'md`, changelog y registro de artefactos',
'únicoeditablecanónico,renderfinal,rastreoCLAIM→ART/EXP→ubicación, respuesta fielpor18IDs. Copiarfuentecompletasólounavez con hash; usarhabilidad documents/docx yPDFantesdeeditar/renderizar.':'Un único editable canónico, render final, relación CLAIM→ART/EXP→ubicación y respuesta fiel a los 18 IDs. Copiar la fuente completa una vez con hash; usar las habilidades de documentos y PDF antes de editar o renderizar.',
'md`,README; no editarlegacy':'md` y README; no editar legacy',
'tareasprevias documentadas; nofindingscríticosocultos; revisorindependientedisponible':'tareas previas documentadas, sin hallazgos críticos ocultos y con revisor independiente disponible',
'fresca,revisión':'fresca, revisión','max_det300':'max_det 300','rejilla0.05':'rejilla 0.05',
'ART-002,224px,top1':'ART-002, 224 px, top1','bootstrap2000':'bootstrap con 2000',
'percentiles2.5/97.5':'percentiles 2.5/97.5','Batch1':'Batch 1','M2=224,FP32,10':'M2=224, FP32, 10',
'imagen,100':'imagen, 100','imagen,una':'imagen, una','simultánea,threads1':'simultánea, threads 1',
'completaM1':'completa de M1','RaspberryPi4':'Raspberry Pi 4','deM2':'de M2',
'SiM1 sano evitaM2 sobre enfermoGT':'Si M1 predice sano y evita M2 sobre un fruto enfermo según GT',
'Fig1':'Fig. 1','Fig2':'Fig. 2','Fig5/7':'Fig. 5/7','cascadaCLI':'cascada CLI',
'las23 referencias delPDF':'las 23 referencias del PDF','VanDerHeijden2022/106698':'Van der Heijden 2022 / 106698',
'DANE,Savary,Zauner yRealSense':'DANE, Savary, Zauner y RealSense','fiel,interpretación,respuesta concreta,evidencia,ubicación final yestado':'fiel, interpretación, respuesta concreta, evidencia, ubicación final y estado',
'esperada,GREEN mínimo yrefactor':'esperada, GREEN mínimo y refactor','tarea,revisión independiente deSPEC ycalidad,secuencial':'tarea, revisión independiente de SPEC y calidad, secuencial',
'inventario,genealogía,reviewer matrix,experiment registry':'inventario, genealogía, reviewer matrix y experiment registry',
'SPEC,self-review':'SPEC, self-review','completas,revisión deconsistencia':'completas, revisión de consistencia',
'manifests,auditoría,tests deatomicidad,hash':'manifests, auditoría, tests de atomicidad y hash',
'absoluta defuga':'absoluta de fuga','entorno,config,comando,logs,pesos,predicciones,métricas y testfinal':'entorno, configuración, comando, logs, pesos, predicciones, métricas y test final',
'ningunoUNVERIFIED':'ninguno UNVERIFIED','render/build,tablas,figuras,bibliografía':'render/build, tablas, figuras, bibliografía',
'conresultados':'con resultados','yverificación':'y verificación','deGT/hardware yclaims':'de GT/hardware y claims',
'históricoM1':'histórico M1','hardwarePi':'hardware Pi','oclaim':'o claim',
}
for path, text in [(spec_path, s), (plan_path, p)]:
    chunks = re.split(r'(```[\s\S]*?```)', text)
    for i in range(0, len(chunks), 2):
        for old, new in fixes.items(): chunks[i] = chunks[i].replace(old, new)
    path.write_text(''.join(chunks), encoding='utf-8')

claim_path = ROOT/'docs/research/claim_evidence_matrix.csv'
with claim_path.open(encoding='utf-8-sig', newline='') as f:
    reader=csv.DictReader(f); fields=reader.fieldnames; rows=list(reader)
for row in rows:
    if row['claim_id'] in {'CLAIM-004','CLAIM-005','CLAIM-009'}:
        row['evidence_id'] += ';DER-001;DER-002'
        row['notes'] += ' Conteos soportados para el snapshot local: manifiesto DER-001 y agregados DER-002; no prueban membresía histórica exacta de entrenamiento.'
    if row['claim_id']=='CLAIM-031':
        row['status']='PARTIALLY_SUPPORTED'
        row['evidence_id'] += ';DER-001;DER-002'
        row['notes'] += ' Se observan cajas full-frame en DATA-003/004 derivadas; DATA-002 no aporta labels YOLO originales. Procedencia original de esas cajas: UNVERIFIED.'
        row['revision_action']='Reformular: cajas full-frame en la representación YOLO derivada; no atribuirlas al dataset original sin evidencia. TASK-09.'
with claim_path.open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)

for path in [ROOT/'docs/research/reviewer_matrix.md',ROOT/'reports/reviewer_matrix.csv']:
    text=path.read_text(encoding='utf-8-sig')
    text=text.replace('un conjunto propio binario no prueba patologías','el conjunto propio tiene una clase de localización mango y no prueba patologías')
    text=text.replace('Versiones exactas Ultralytics/Python/PyTorch/CUDA, GPU y checkpoint base.', 'Ultralytics 8.4.39 recuperada de ART-001; faltan Python/PyTorch/CUDA, GPU exacta y checkpoint base históricos.')
    path.write_text(text,encoding='utf-8')
print('Corrected SPEC, plan, claim matrix and reviewer descriptions. No scientific execution.')
