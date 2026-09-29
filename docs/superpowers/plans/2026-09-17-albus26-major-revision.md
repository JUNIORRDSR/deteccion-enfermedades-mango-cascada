# ALBUS26-116 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Aprobación conceptual recibida; no iniciar TASK-01 hasta revisión independiente fresca del delta sin HIGH/MEDIUM abiertos, registro de autorización satisfecha y protocol freeze. Esta edición no satisface por sí sola GATE B/C.

**Goal:** Producir una revisión científicamente trazable, corrigiendo el método y el alcance de las afirmaciones según evidencia.

**Architecture:** Archivos de procedencia y scripts CLI pequeños dentro del workspace. Legacy sólo lectura; los resultados finales alimentan tablas, figuras, DOCX y respuesta. No agregar servicios, frameworks de experimentación ni otra base de datos.

**Tech Stack:** Python, stdlib `unittest`, Ultralytics/PyTorch en entorno nuevo congelado, Pillow/ImageHash, NumPy/SciPy ya utilizados por el proyecto; DOCX ALBUS y render PDF. No ejecutar scripts legacy con salidas fijas.

## Global Constraints

- Autoridad: `docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md`.
- Git canónico: `C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision`; raíz lógica `revision` = checkout/worktree activo. Outputs relativos se resuelven allí. Legacy se resuelve mediante root mapping, nunca por el padre del worktree; sólo lectura.
- AMENDMENT-01 autoriza nuevo Git exclusivo, baseline documental `3990fa7c79b77224675449b9bb676e650c47bbaf`, exclusiones `c0463636d2288ba3370d34914c27e47b11a5e30f`, rama `revision/execute-approved-plan`, worktree `.worktrees/execution` y commits LOCALES pequeños por tarea. No push/merge externo/publicación ni cambios legacy o su `.git`. No versionar datasets/pesos/entornos grandes; manifests/hashes bastan, sin LFS innecesario.
- Sólo train/validation orientan selección; test se ejecuta al final con decisiones congeladas y su historia retrospectiva declarada.
- Conservar runs y fallos; directorio de run debe ser nuevo. No borrar datasets ni sustituir métricas desfavorables.
- Ningún test exige mAP/F1/accuracy mínima. Los tests comprueban método.
- `REPRODUCED` requiere ejecución fresca y evidencia; lectura de CSV no basta.
- Ground truth conjunto, Raspberry Pi y reproducción histórica M1 exacta ausentes bloquean sólo sus resultados dependientes; continuar partes independientes y retirar/moderar claims. Gates D/E bloqueados conservan su estado real.
- Toda función que consuma rutas/output rechaza escritura fuera del checkout/repositorio autorizado y modificación de entrada. Comandos Git de lectura en legacy usan `GIT_OPTIONAL_LOCKS=0` y se comparan con estado inicial; nunca limpiar cambios previos. El `.git` administrativo del nuevo worktree puede apuntar al nuevo repo autorizado, nunca a legacy.
- Interfaz CLI común propuesta: argumentos explícitos; código 0=éxito,2=entrada inválida o dependencia científica ausente; errores de ejecución conservan traceback y exit code. Estas CLIs son entregables futuros, no herramientas ya implementadas.

## Preflight documental y freeze — antes de TASK-01

- [ ] Preservar autorización del usuario; generar diff exacto de SPEC/plan contra baseline aprobado y registrar SHA256 del diff. Actualizar decision_log, self-reviews y correspondencia AMENDMENT↔REVIEW↔TASK.
- [ ] Revisor independiente fresco inspecciona únicamente delta y sus efectos sobre diseño completo, sin self-review persuasivo. Resolver HIGH/MEDIUM y volver a revisar lo afectado. No convertir aprobación conceptual en gate satisfecho antes de este resultado.
- [ ] Verificar baseline e integridad legacy con estado inicial. El preflight documental fresco se conserva en `reports/amendments/pre_execution_integrity.json`; no es una nueva auditoría científica ni sustituye comprobaciones posteriores.
- [ ] Registrar que la condición de autorización se cumplió, con hash de delta y reporte del reviewer; commitear SPEC/plan y decisiones localmente. Obtener commit de cada documento y SHA256 de sus bytes, cotejando `git show <commit>:<path>` con archivo actual.
- [ ] Crear con exclusividad `provenance/protocol_freeze.{md,json}` según SPEC §4.2, con reglas completas de auditoría/pHash/agrupamiento/split/seeds/estimandos/selección/bootstrap/benchmark/test. Registrar `test_observed_before_freeze=true` y evidencia histórica ya leída en `provenance/test_access_log.csv`; no afirmar preregistro prospectivo.
- [ ] Verificar snapshot JSON parseable, todos los campos, correspondencia de commits/hashes, ausencia de nuevas observaciones y escritura sin sobrescritura; commitear snapshot, registrar hash/commit en ledger. GATE B/C=SATISFIED sólo con evidencia de revisión y freeze. Iniciar TASK-01 sin nueva aprobación.

El freeze es append-only. Cambios posteriores usan `provenance/protocol_amendments/PROTOCOL-AMENDMENT-XXX.{md,json}` con timestamp, protocolo anterior, modificación, evidencia, test observado, impacto, decisión y reviewer. Bugs con efecto científico exigen también deviation/amendment, además de TDD. Rigen exclusivamente las cinco condiciones de parada global de SPEC §11; una enmienda material tras test observado o que altere interpretación primaria exige decisión del usuario. Bloqueos conocidos no detienen tareas independientes.

## Entorno de comandos y dependencias

El bloque de instalación establece la raíz del checkout activo en su propia invocación. Para cada comando de TASK-01 a TASK-10, fijar `workdir` de `exec_command` a esa raíz (o anteponer `Set-Location -LiteralPath` en la misma invocación). Cada llamada es un proceso independiente y no conserva variables anteriores. Cada invocación científica debe aplicar/verificar la inicialización antes de importar runtimes; reutilizar `configure_environment(root)` de TASK-01 en entradas CLI. Cada command.txt debe bastar en proceso nuevo con raíz y ejecutable explícitos. Los ejemplos por tarea invocan `.\.venv\Scripts\python.exe` desde esa raíz.

TASK-01 creará `.venv` dentro del workspace usando el runtime disponible Python 3.12.14. Es un entorno **reconstruido**, distinto de Python 3.13.13 del entrenamiento M2 y del Python desconocido del M1. Propuesta fijada: Ultralytics 8.4.52, torch 2.12.0, torchvision 0.27.0, NumPy 2.4.4, Pillow 12.2.0, ImageHash 4.3.2 y scikit-learn 1.8.0; versiones observadas en metadata local, no asumidas compatibles antes de comprobarlas. Registrar resolución exacta de dependencias transitivas. Si la instalación/carga no es compatible, aplicar systematic-debugging y documentar una enmienda de entorno; no actualizar silenciosamente ni escribir en `.venv` legacy. La reproducción histórica exacta M1 sigue bloqueada sin su entorno original; la reevaluación reconstruida se identifica como tal.

```powershell
Set-Location -LiteralPath 'C:\Users\junio\Downloads\mango-vision\ALBUS26_major_revision\.worktrees\execution'
# Otro checkout autorizado puede sustituir esta ubicación; no inferir legacy desde '..'.
$env:GIT_OPTIONAL_LOCKS='0'
$AuditPython = 'C:\Users\junio\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$WorkspaceRoot = (Get-Location).Path
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
& $AuditPython -m venv .venv
$Python = Join-Path (Get-Location) '.venv\Scripts\python.exe'
New-Item -ItemType Directory -Force -Path provenance/environment | Out-Null
& $Python --version
& $Python -c "import sys; print(sys.executable)"
& $Python -m pip --version
# Registrar pip config y los índices efectivos mediante salida redactada según TASK-01.
& $Python -m pip install --report provenance/environment/install_report.json ultralytics==8.4.52 torch==2.12.0 torchvision==0.27.0 numpy==2.4.4 Pillow==12.2.0 ImageHash==4.3.2 scikit-learn==1.8.0
& $Python -m pip check
& $Python -m pip list --format=json > provenance/environment/packages.json
& $Python -m pip freeze --all > provenance/environment/reconstructed_freeze.txt
```

No se ha ejecutado ninguna de esas órdenes en la primera fase. Si no hay capacidad para entrenar, TASK-04 produce bloqueo con evidencia de capacidad y mantiene pendiente el resultado; no inventar hardware Kaggle.

## Orden y revisión

Secuencia: TASK-01→02→03→04(condicional)→05→06→07→08→09→10. Bibliografía puede investigarse en paralelo en sólo lectura; implementadores no escriben archivos compartidos simultáneamente. Un implementador fresco por tarea; entrega cambios, comando RED/GREEN, evidencia y self-review. Un revisor fresco comprueba SPEC y calidad sin recibir conclusiones persuasivas. Hallazgos HIGH/MEDIUM se resuelven antes de continuar la rama afectada; verificar ausencia de nuevas contradicciones. El implementador crea commits candidatos locales tras self-review/tests para revisión independiente del diff BASE..HEAD; fixes se añaden como commits posteriores y se revisan de nuevo. Sólo marcar tarea completa/ledger tras aprobar cumplimiento y calidad, con commits, tests y artefactos. No push ni merge implícitos. Si no hay agentes disponibles, registrar revisión independiente BLOCKED y no afirmar ese gate satisfecho.

## TASK-01 — Congelar fuentes, entorno y contratos

**FILES:** crear `src/evaluation/provenance.py`, `tests/__init__.py`, `tests/test_provenance.py`, `configs/inputs.json`, `configs/root_mapping.json`, `provenance/source_locations.csv`, `provenance/environment/{reconstructed_freeze.txt,identity.json,pip_config_redacted.txt,install_report.json,packages.json,package_artifacts.csv,hardware.json,environment_whitelist.json,pip_check.txt}`; actualizar registries, preservando manifests originales. Leer manifest inicial, freeze y ambos registries.

**CONSUMES:** `provenance/source_manifest.csv`; ART-001 detector y ART-002 clasificador; DATA-001/004/005; metadata estática de checkpoints.

**PRODUCES:** `configure_environment(root:Path)->dict[str,str]` inicializa/verifica whitelist de rutas y aislamiento antes de imports científicos en cada proceso CLI, sin depender de shell previa; `sha256(path: Path)->str`, `verify_sources(rows: list[dict])->list[dict]` con discrepancias; `create_run(path: Path)->None` con `mkdir(exist_ok=False)`; `check_output(root: Path,path: Path)->Path` que valida containment. `configs/inputs.json` contiene referencias `SRC-ID,logical_root,logical_path,local_absolute_path,sha256`, versión reconstruida y fuente histórica separadas. `resolve_source(row:dict,roots:dict[str,str])->Path` valida path relativo y containment con resolve, resuelve root explícito y comprueba identidad por hash; `verify_sources` acepta filas del sidecar reconciliado con el manifest original por SRC-ID. No mutar el original para arreglar rutas. CLI añade `--root-mapping configs/root_mapping.json --source-locations provenance/source_locations.csv`; requiere cobertura total y única de SRC originales y falla por mapeos ambiguos. `package_artifacts.csv` tiene distribution,version,filename,build,origin_redacted,sha256,status,reason; valores no recuperados son explícitos. `identity.json` incluye comandos/versiones/ejecutable y `hardware.json` OS/build, CPU,RAM,GPU,driver,CUDA o ausencia documentada.

**PRECONDITIONS:** B/C satisfechos mediante revisión fresca y freeze; snapshot inicial disponible; nuevo Git/worktree autorizado por AMENDMENT-01. Freeze verificado y ninguna TASK-01 ejecutada antes de él.

**STEPS:**

- [ ] Escribir test antes del módulo, con archivo temporal `abc`, hash esperado y rechazo de `../outside`. Guardar salida RED:

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from src.evaluation.provenance import sha256, check_output, create_run
with TemporaryDirectory() as d:
    root = Path(d); p = root / 'input'; p.write_bytes(b'abc')
    assert sha256(p) == 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
    assert check_output(root, root / 'output') == (root / 'output').resolve()
    try: check_output(root, root / '..' / 'outside')
    except ValueError: pass
    else: raise AssertionError('escaped output accepted')
    create_run(root / 'run')
    try: create_run(root / 'run')
    except FileExistsError: pass
    else: raise AssertionError('existing run accepted')
```

- [ ] Implementar hashlib streaming y containment con `Path.resolve().is_relative_to`; no confiar en prefijos string. Añadir fixtures: archivo modificado produce discrepancia, inexistente produce error con SRC-ID; cero discrepancias no se confunde con manifest vacío.
- [ ] Crear root mapping `legacy_corpus=C:/Users/junio/Downloads/mango-vision`, `external_mail=C:/Users/junio/Downloads`, `revision=raíz del checkout`; separar referencias portables de evidencia absoluta. Test RED con dos roots temporales que contienen los mismos bytes y SRC: ambas resoluciones tienen igual SHA y logical_path; root ausente, path absoluto/escape, SRC duplicado/ausente, archivo faltante y hash diferente deben fallar antes de inferencia. Los bytes del manifest original permanecen idénticos tras resolver. El cwd de worktree no permite resolver una fuente por `../`.
- [ ] Preparar el entorno con los comandos anteriores. Capturar `python --version`, ejecutable, `pip --version`, `pip config debug/list` redactado, índices efectivos (incluidos configuración/env/CLI), install report, pip check y exit code, paquetes JSON, freeze, wheel/build/metadatos y hashes disponibles. Conservar causa para hashes no obtenibles; pins no equivalen a identidad binaria. Capturar OS/build, CPU, RAM, GPU/driver/CUDA o ausencia comprobada; variables en whitelist de aislamiento, índices, dispositivo y threads. Redactar userinfo/tokens/queries sensibles y otros secretos antes de persistir/publicar registros; mantener host e información no secreta. Si pip produce report con secretos, generar el archivo duradero mediante captura/sanitización y no commitear el raw. Test: URL con credenciales/token preserva host y elimina secretos; pip check no cero bloquea uso científico de ese entorno. Conservar 8.4.39 como dato del M1 histórico y 8.4.52 como versión reconstruida elegida, conforme a la SPEC. Antes de importar YOLO, verificar en un proceso hijo que las variables están fijadas; después de importarlo, comprobar que los directorios efectivos de configuración, caché, pesos, datasets y runs quedan dentro del workspace. Configurar explícitamente los settings de Ultralytics para esas rutas y desactivar integraciones remotas. Probar que omitir YOLO_CONFIG_DIR falla antes de importar y que una ruta externa falla por su causa concreta. Revisar otros escritores del runtime instalado; si alguno usa una ruta externa, bloquear ese proceso y corregirla antes de entrenar/evaluar; aplicar las cinco condiciones de parada global si corresponde. Repetir la comprobación en un proceso nuevo sin variables heredadas para verificar que el entrypoint inicializa y valida antes de importar; cada CLI científica de tareas posteriores reutiliza este helper. Guardar stdout, stderr, exit code y el informe de rutas.
- [ ] Guardar `configs/inputs.json` desde SRC/ART; comprobar hashes de los cuatro pesos sin inferencia. Entrada base M1 ausente queda `BLOCKED_MISSING_BASE_CHECKPOINT`; no usar best entrenado como base para split nuevo.
- [ ] Ejecutar GREEN y revisión independiente de procedencia.

**TESTS / VERIFICATION COMMANDS:** `& .\.venv\Scripts\python.exe -m unittest tests.test_provenance -v`; `& .\.venv\Scripts\python.exe -m src.evaluation.provenance --source-manifest provenance/source_manifest.csv --source-locations provenance/source_locations.csv --root-mapping configs/root_mapping.json --out reports/source_verification.json`.

**EXPECTED RESULTS:** tests correctos, cero diferencias de fuentes elegibles o fallo explícito; salida nunca altera baseline. Entorno congelado identificado como reconstruido.

**ARTIFACTS:** logs RED/GREEN en `provenance/commands/task01/`; `reports/source_verification.json`; configs, source_locations y registros detallados del entorno; constancia de freeze verificado y referencias a commits; originales intactos.

**REVIEW-IDs SATISFIED:** REVIEW-09 (procedencia recuperada y límites); habilita01/03/07.

## TASK-02 — Auditoría reproducible M1 y comprobación M2

**FILES:** crear `src/leakage_audit/audit.py`, `tests/test_leakage.py`; outputs `data/audits/model1/` y `data/audits/model2/`. Reutilizar algoritmo union-find entendido de `legacy_corpus:Mango-vision/src/data_prep/dedup_and_resplit.py`, quitando efectos legacy y manteniendo atribución.

**CONSUMES:** `data/manifests/legacy_dataset_inventory.csv`, `configs/inputs.json`; DATA-001 y003/004/005; pares históricos `legacy_corpus:Articulo/reports/leakage_pairs.csv`.

**PRODUCES:** `hamming(a:int,b:int)->int`; `components(ids:list[str],edges:list[tuple[str,str]])->dict[str,str]` con ID mínimo como representante; `cross_split(rows:list[dict])->list[dict]`; CLI `--dataset-id --manifest --phash-bits 64 --hamming-lt 5 --candidate-max 10 --out`. Pares incluyen IDs,hashes,distancia,splits,relation,evidence,review_decision; clusters incluyen todas las imágenes, aun aisladas. pHash fijado: Pillow 12.2.0/ImageHash 4.3.2, `imagehash.phash(image.convert("RGB"),hash_size=8,highfreq_factor=4)`, sin normalización EXIF/recorte. Implementar `validate_adjudications(rows:list[dict])->None` conforme a SPEC §5: A/B independientes, IDs opacos, decisiones originales, agreement, final, evidence/rationale y resolución separada. Exportar `blind_packets/{a,b}/`, clave separada, `adjudications.csv`, `adjudication_resolution.csv`, `blinding_log.json`, `duplicate_structure.json` y `cluster_size_distribution.csv` por dataset. Esquema por par o grupo con `unit_type,member_ids` y cobertura verificable; grande=≥10 imágenes.

**PRECONDITIONS:** TASK-01; fuentes íntegras; acceso sólo lectura; revisión visual de candidatos es investigación de calidad de datos, nunca optimización de métricas.

**STEPS:**

- [ ] Test RED de Hamming, frontera 4/5, transitividad, singleton y orden de entrada:

```python
from src.leakage_audit.audit import hamming, components
assert hamming(0, 15) == 4
assert hamming(0, 31) == 5
assert (hamming(0, 15) < 5) and not (hamming(0, 31) < 5)
expected = {'a':'a','b':'a','c':'a','d':'d'}
assert components(['d','b','a','c'], [('a','b'),('b','c')]) == expected
assert components(['a','b','c','d'], [('c','b'),('b','a')]) == expected
```

- [ ] Implementar `hamming=(a^b).bit_count()`, validando 0 ≤ hash < 2**64; union-find determinista. Reusar SRC IDs; comparar pares sólo una vez; SHA exacto no se identifica con pHash0.
- [ ] Agregar caso sintético dos copias exactas entre splits, near pair dentro del split, imagen corrupta y etiquetas contradictorias. Error de decodificación aborta audit con lista; no omitir imagen. Clases en conflicto se remiten a adjudicación, no mayoría automática.
- [ ] RED adicional: candidato visual relevante sin B falla; A=B como identidad del reviewer falla; desacuerdo sin adjudicación separada falla; cluster de 10 miembros activa revisión grande y uno de 9 no por ese criterio, pero los demás motivos siguen activos. Paquete ciego no incluye split/rutas/filenames/clases ni resultados/métricas/consecuencias y no contiene la decisión A en B. Relaciones probadas documentalmente conservan prioridad. Comprobar registro por cluster con miembros completos sin exigir N² filas.
- [ ] Ejecutar auditoría M1; dos reviewers frescos reciben paquetes visuales separados sin acceso recíproco para cross-split, ≥10 imágenes, conflictos, posibles secuencias y banda 5–10 usada en sensibilidad cuando haga falta juicio visual. Cegar split siempre posible y añadirlo sólo al análisis posterior. Guardar excepciones de cegamiento, evidencia y juicio A/B; disagreement exige resolución separada. Resolver origen de `sakit_mp4` y freshMango; sin fuente verificable, mantener relación posible y grupo conservador. Una nueva evidencia añade adjudicación, nunca modifica raw ni reemplaza silenciosamente decisiones previas.
- [ ] Ejecutar comprobación M2 completa; verificar 1.500 membresías clean→cls con hashes de imagen, etiqueta y clase (la clasificación usa la clase de carpeta, sin label de cajas); comprobar el alias valid→val y el YAML que apunta al dataset original. Conservar informe de diferencias frente a los 76 pares históricos.
- [ ] Exportar estructura M2 por dataset/split: n imágenes, n SHA únicos, n clusters, n group_id, distribución completa de tamaños, mínimo/mediana/máximo y clases discordantes por SHA. Fixture cuatro imágenes, tres SHA, dos clusters de tamaños 3/1 produce exactamente esos counts; no se etiqueta n clusters como n biológicamente independiente. Sensibilidad de métricas se ejecuta en TASK-05, sin reentrenar por multiplicidad intra-split.
- [ ] Emitir verdict: contaminación/grupos cruzados→TASK-03 split nuevo; ausencia de relaciones detectadas→preservación condicional, con limitaciones; unidades insuficientes→BLOCKED. M2 contaminado exige enmienda de reentrenamiento M2, no ejecución implícita.

**TESTS / VERIFICATION COMMANDS:** `& .\.venv\Scripts\python.exe -m unittest tests.test_leakage -v`.

```powershell
& .\.venv\Scripts\python.exe -m src.leakage_audit.audit --dataset-id DATA-001 --manifest data/manifests/legacy_dataset_inventory.csv --phash-bits 64 --hamming-lt 5 --candidate-max 10 --out data/audits/model1
& .\.venv\Scripts\python.exe -m src.leakage_audit.audit --dataset-id DATA-004 --manifest data/manifests/legacy_dataset_inventory.csv --phash-bits 64 --hamming-lt 5 --candidate-max 10 --out data/audits/model2
```

**EXPECTED RESULTS:** El número de pares es una observación, sin valor mínimo exigido. Los conteos cubren todos los archivos; parámetros, versiones, hashes y decisiones quedan conservados. Cero pares no demuestra independencia biológica.

**ARTIFACTS:** Outputs M1/M2, versiones/hashes, paquetes y adjudicaciones A/B, resoluciones y registro de cegamiento, duplicate_structure/cluster_size_distribution y logs RED/GREEN. Reporte enumera forma de fuga, algoritmo/parámetros, evidencia de origen/secuencia, límites y relaciones no excluidas; no declara ausencia universal de fuga.

**REVIEW-IDs SATISFIED:** REVIEW-01, REVIEW-02; decide REVIEW-03 y apoya REVIEW-04/09.

## TASK-03 — Proponer y congelar partición

**FILES:** crear `src/leakage_audit/split.py`, `tests/test_split.py`; `data/manifests/model1_clean_manifest.csv`, su `.sha256`, `data/manifests/model2_frozen_manifest.csv`, su `.sha256`, `configs/model1_data.yaml`, `reports/model1_split_proposal.md`.

**CONSUMES:** Auditoría y adjudicación de TASK-02, SRC de imagen y etiqueta, root mapping/source_locations de TASK-01, grupos confirmados y conservadores.

**PRODUCES:** `validate_group_atomicity(rows:list[dict])->None` comprueba sólo los campos de agrupamiento; `validate_split(rows:list[dict])->None` añade rutas, hashes, clases y esquema completo; `assign_groups(groups:list[dict],seed:int=42)->dict[str,str]`; CSV UTF-8 ordenado por image_id y hash; YAML sólo dentro del workspace.

**PRECONDITIONS:** Dictamen de auditoría documentado. Una clase o grupo ambiguo sin resolver bloquea la congelación. Generar el manifiesto no inicia el entrenamiento.

**STEPS:**

- [ ] RED: filas con mismo group_id en train/test deben fallar, igual image_id repetido debe fallar; secuencia confirmada no se puede separar aunque clusters difieran. Fixture mínimo:

```python
from src.leakage_audit.split import validate_group_atomicity, assign_groups
rows = [dict(image_id='a', group_id='g', cluster_id='c1', sequence_id='s', proposed_split='train'),
        dict(image_id='b', group_id='g', cluster_id='c2', sequence_id='s', proposed_split='test')]
try: validate_group_atomicity(rows)
except ValueError as exc: assert str(exc) == 'GROUP_CROSSES_SPLIT:g'
else: raise AssertionError('group crosses split')
groups=[{'id':str(i),'size':1,'class_counts':[1,1]} for i in range(20)]
assert assign_groups(groups,42) == assign_groups(list(reversed(groups)),42)
```

- [ ] Implementar el algoritmo único de la SPEC: ordenar IDs, shuffle con seed 42, ordenar estable por tamaño y asignar minimizando la desviación cuadrática normalizada. Operar vectores de instancias; no usar sólo la primera clase de una imagen. Conservar archivos duplicados como miembros distintos del mismo grupo.
- [ ] Fixture rutas/hashes/labels inválidos falla antes de escribir; dos ejecuciones idénticas producen bytes/hash idénticos; sin timestamps en el CSV. Añadir grupos demasiado grandes y clase ausente: bloqueo concreto, sin ajustar la seed.
- [ ] Si se conserva el split, congelar la membresía actual con el mismo esquema y justificación. Si se reasigna, generar la vista en data/derived con etiquetas propias y sin caches en legacy.
- [ ] Si la auditoría M2 permite reutilizar sus pesos, congelar su membresía actual en `model2_frozen_manifest.csv`, con image_id de DATA-005, logical_root/logical_path/local_absolute_path, SHA256, nombre de clase, split, cluster_id y group_id; clasificación usa la etiqueta de carpeta. Mapear cada miembro DATA-004 a DATA-005 por nombre, hash, clase y split (valid→val), conservando multiplicidad y SRC de ambos. Exigir correspondencia total y única; no unir sólo por hash porque hay duplicados. Transferir el grupo auditado a cada image_id DATA-005 y guardar sidecar SHA256. No reasignar M2 con esta tarea; una discrepancia bloquea su evaluación y exige la enmienda prevista.
- [ ] Guardar propuesta con conteos, unidades, conflictos, proporciones reales, hash y flags `requires_retraining` y `test_history`. Revisar la congelación antes de TASK-04.

**TESTS / VERIFICATION COMMANDS:** `& .\.venv\Scripts\python.exe -m unittest tests.test_split -v`; `& .\.venv\Scripts\python.exe -m src.leakage_audit.split --audit data/audits/model1 --seed 42 --ratios 0.70 0.15 0.15 --out data/manifests/model1_clean_manifest.csv --proposal reports/model1_split_proposal.md`; `Get-FileHash -Algorithm SHA256 -LiteralPath data/manifests/model1_clean_manifest.csv`.

Congelación M2 sin cambiar miembros: `& .\.venv\Scripts\python.exe -m src.leakage_audit.split --audit data/audits/model2 --preserve-membership --dataset-id DATA-005 --out data/manifests/model2_frozen_manifest.csv`. El modo verifica clases y grupos, produce el sidecar y falla si la auditoría no permite reutilización.

**EXPECTED RESULTS:** Atomicidad y validez pasan o la congelación queda bloqueada. El hash coincide con el sidecar. La configuración apunta sólo a la membresía congelada.

**ARTIFACTS:** CSV, sidecar, YAML, propuesta, logs y registro de datos actualizado.

**REVIEW-IDs SATISFIED:** REVIEW-02, REVIEW-03; prepara REVIEW-04/05.

## TASK-04 — Run M1 condicionado a auditoría

**FILES:** crear `src/evaluation/train_model1.py`, `tests/test_run_contract.py`, `configs/model1_train.json`; outputs `experiments/model1/EXP-R01/`. Si no procede entrenar, producir `reports/model1_retraining_decision.md` sin run ficticio.

**CONSUMES:** split congelado y hash, configuración histórica EXP-001 y checkpoint base con hash recuperado; entorno TASK-01.

**PRODUCES:** `prepare_run(config:dict,manifest:Path,run_dir:Path)->dict` con command/env/hashes; Entrenamiento desde la base y registro completo. `select_checkpoint(records:list[dict])->dict` selecciona el máximo fitness sin redondear y la última época en empate, usando registros del guardado nativo. Cada registro contiene epoch, fitness, métricas, checkpoint_path y SHA256. El resultado debe corresponder a los bytes conservados, no sólo a un número de época.

**PRECONDITIONS:** TASK-03, `requires_retraining=true`, base YOLO26n identificada y capacidad real disponible. Si falta base, entorno o hardware, queda BLOCKED. Si se conserva el split y la auditoría permite usar pesos históricos, documentar que no se reentrena y seguir a TASK-05.

**STEPS:**

- [ ] RED: Un manifiesto distinto del hash registrado se rechaza antes de importar YOLO. Un run existente se rechaza. La configuración impide usar un checkpoint entrenado como base de una partición cambiada. Test de selección:

El test usa tres archivos de pesos ficticios con hashes distintos y registros de guardado: épocas 95 (.80005), 137 (.80478) y 138 (.80478). Debe seleccionar la ruta y hash de 138. Otro caso usa .8047801 y .8047802, que colapsan al mismo texto con seis cifras significativas: selecciona el mayor sin redondear, incluso si es de una época anterior. Un hash cambiado o un artefacto ausente debe fallar. Estas pruebas usan bytes ficticios y no cargan ni entrenan modelos.

- [ ] Implementar un wrapper que comprueba entradas, crea un run nuevo, contiene salidas y caches, guarda comando y entorno y captura stdout/stderr. Configuración: epochs=150, patience=100, batch=16, imgsz=640, seed=0 y optimizer=auto con el optimizador resuelto registrado. Proponer CPU si es el único dispositivo disponible. Si se usa GPU, registrar antes del run la diferencia de configuración; no afirmar una réplica de 2×T4.
- [ ] Obtener la base oficial y su hash sólo tras aprobación. No emplear el peso M1 entrenado para una partición nueva. Conservar origen y licencia.
- [ ] Verificar el fitness efectivo en el código de la versión instalada. Registrar con callback on_model_save, después del guardado nativo, la época base 1, fitness y métricas sin redondear, y el hash de best.pt cuando se escribe. Conservar una copia de ese best antes del stripping final; registrar separadamente el hash final si se transforma. Configurar save=True; no seleccionar desde el CSV redondeado. Comprobar con fixtures la correspondencia entre pesos, hash y última época máxima.
- [ ] Ejecutar una vez y conservar fallos. Aplicar systematic-debugging; no reintentar para mejorar el resultado. Reconciliar el registro de guardado, los hashes y el checkpoint final. Un guardado omitido por NaN/Inf o un vínculo ambiguo impide validar el run. No evaluar test aquí.
- [ ] Un revisor independiente comprueba entradas, hashes, configuración, seeds, selección y ausencia de acceso al test.

**TESTS / VERIFICATION COMMANDS:** `& .\.venv\Scripts\python.exe -m unittest tests.test_run_contract -v`; `& .\.venv\Scripts\python.exe -m src.evaluation.train_model1 --config configs/model1_train.json --manifest data/manifests/model1_clean_manifest.csv --run-dir experiments/model1/EXP-R01`.

**EXPECTED RESULTS:** Run completo o fallo registrado con exit code, sin umbral de éxito científico. Hash de entradas idéntico antes y después; checkpoint seleccionado sólo por validación.

**ARTIFACTS:** config.yaml, command.txt, environment.txt, dataset_manifest.sha256, results.csv, logs/, weights/, plots/, metrics.json y README.md; registro EXP-R01.

**REVIEW-IDs SATISFIED:** REVIEW-03 y REVIEW-09 si el entrenamiento requerido se completa; si se bloquea, quedan pendientes.

## TASK-05 — Evaluación coherente e incertidumbre

**FILES:** crear `src/evaluation/evaluate.py`, `src/statistics/intervals.py`, `tests/test_evaluation.py`, `tests/test_intervals.py`; `configs/evaluation.json`, `configs/evaluation_frozen.json` y su `.sha256`; outputs `experiments/model1/EXP-V01/` (validación), `experiments/model1/EXP-R02/`, `experiments/model2/EXP-R03/` y `artifacts/metrics/`.

**CONSUMES:** Pesos congelados de TASK-04 o ART-001 admitido por la auditoría, ART-002 para M2, manifiestos M1 y M2 comprobados y decisiones operativas fijadas en validación.

**PRODUCES:** `classification_metrics(cm:list[list[float]])->dict`; `match(gt:list[dict],pred:list[dict],iou_threshold:float)->dict`; `wilson(k:int,n:int,z:float=1.959963984540054)->tuple[float,float]`; `bootstrap_groups(records:list[dict],metric,seed:int=42,n_resamples:int=2000)->dict`. CLI evaluate con `--model-id --config --split --run-dir`; CLI intervals con `--predictions --groups --seed --resamples --out`. `m2_sensitivity(records:list[dict],class_names:list[str])->dict` devuelve estimandos image-weighted/exact-SHA-dedup/cluster-weighted, matrices float, métricas, deltas y motivos de indefinición; `bootstrap_groups` conserva draws compartidos e IDs de ocurrencia para intervalos pareados. Añadir modo `--m2-sensitivity` a intervals; produce `artifacts/metrics/model2_sensitivity.{json,csv}`, `model2_sensitivity_confusions.json`, `model2_bootstrap_draws.json` y `reports/model2_duplicate_sensitivity.md`. No usar otra inferencia ni reentrenamiento para esta sensibilidad.

**PRECONDITIONS:** Auditoría y congelación completas, pesos y entorno fijos, auditoría M2 válida o enmienda aprobada. No optimizar en test.

**STEPS:**

- [ ] RED: La matriz fixture [[8,2],[1,9]] debe producir accuracy=17/20 y macro F1=media(16/19,18/21). La matriz extendida de detección no admite tratar el fondo como clase real para accuracy. Un GT con dos predicciones coincidentes produce TP=1 y FP=1; un GT sin predicción produce FN=1. Probar desempate IoU estable y mapa de nombres de clase desordenado.

```python
from src.evaluation.evaluate import classification_metrics
m=classification_metrics([[8,2],[1,9]])
assert abs(m['accuracy'] - 17/20) < 1e-12
assert abs(m['macro_f1'] - (16/19+18/21)/2) < 1e-12
from src.statistics.intervals import wilson
lo,hi=wilson(0,10)
assert abs(lo)<1e-12 and .277<hi<.278
try: wilson(0,0)
except ValueError: pass
else: raise AssertionError('undefined proportion accepted')
```

- [ ] RED M2: cuatro filas de dos clases en fixture de función (producción usa las cinco fijas): `a1,a2` mismo SHA/GT=A/pred=B, `a3` SHA distinto/GT=A/pred=A y `b1` GT=B/pred=B; cluster(a1,a2,a3)=c1, cluster(b1)=c2. Principal accuracy=1/2; exact-dedup escoge a1 y accuracy=2/3; cluster-weighted pesos 1/3,1/3,1/3,1 y accuracy=2/3. Deltas de ambas accuracy=1/6. MacroF1 principal=1/2*(2/4+2/4)=1/2, exact-dedup=2/3, cluster-weighted=1/2*(1/2+3/4)=5/8. Verificar invariancia de orden, representante mínimo, discrepancia de GT por SHA rechazada y coverage de IDs. Clase GT ausente vuelve indefinida su F1 y macroF1; precision sin predicciones es indefinida, F1 con GT positivo es cero. No promediar sólo clases presentes.
- [ ] Implementar principal peso1; exact-SHA-dedup representante mínimo por hash con etiqueta consistente; cluster-weighted peso1/tamaño del cluster en test. Confusión y P/R/F1 por clase/accuracy/macroF1 desde conteos float según SPEC §7; conservar clases por nombre y orden fijado. Exportar denominadores, counts/estructura de TASK-02, estimaciones y diferencias secundaria−principal en unidades y puntos porcentuales. No seleccionar el estimando que mejore resultados.
- [ ] RED bootstrap pareado: group_id de adquisición puede contener dos clusters y debe remuestrearlos juntos. Dos ocurrencias del mismo grupo conservan dos masas de cluster y dos representantes SHA, sin deduplicación global. Los tres esquemas/deltas comparten exactamente los mismos draws seed42/2000. Un SHA o cluster en dos group_id falla. Fixture con >5% draws indefinidos bloquea CI; exactamente5% admite CI percentil de draws definidos con count explícito si hay ≥2 grupos por clase; <2 grupos bloquea CI correspondiente. La proporción indefinida del delta se calcula cuando cualquiera de sus dos métricas es indefinida. Guardar draws hasheados.
- [ ] Implementar métricas desde conteos sin redondear; Wilson con stdlib; matching determinista por IoU descendente. Seleccionar F2 en validación con rejilla 0.05..0.95, paso 0.05 y empate a menor umbral; registrar la regla y el umbral. No usar P/R del pico F1 en test como umbral de producción.
- [ ] El test de bootstrap con un grupo repetido y seed fija comprueba atomicidad, tamaños y determinismo. Las remuestras con clase ausente incrementan `undefined_count`; no se les asigna cero. Dos copias bootstrap del mismo grupo reciben IDs de ocurrencia distintos.
- [ ] Comprobar equivalencia BGR/RGB y resize entre evaluación y CLI: la galería legacy convierte BGR a RGB antes de YOLO. No copiar esa transformación sin comprobar el contrato de entrada. Congelar un tratamiento acorde con la API y registrar el cambio, sin elegirlo por resultados de test.
- [ ] Preparar configuración final de validación, hashes, nombres de clases y score mínimo. Evaluar test una vez después de congelar decisiones; conservar predicciones suficientes para AP y métricas operativas. Calcular intervalos desde predicciones guardadas, sin repetir inferencia.
- [ ] Ejecutar primero validación M1 y guardar sus predicciones. El modo `--freeze-operating-point` consume únicamente esas predicciones y la configuración previa, aplica la rejilla F2 de la SPEC y escribe una configuración nueva con umbral, regla, hashes de pesos/manifiestos y hash de las predicciones de validación. Rechazar entradas marcadas test. El modo test exige esta configuración congelada y su sidecar, sin opciones de selección; M2 conserva top1 sin rechazo. Probar el rechazo de predicciones de test y de un hash alterado.
- [ ] Remuestrear grupos de adquisición cuando se conozcan; usar imagen sólo con independencia justificada. Publicar estimación, CI, número de imágenes, instancias y grupos, y fracción definida. Aplicar el bloqueo de CI de la SPEC: menos de dos grupos o más del 5% de remuestras indefinidas.
- [ ] Comparar resultados nuevos e históricos explicando umbral, checkpoint y split. No exigir igualdad con entradas diferentes. Corregir doble redondeo sólo en artefactos de revisión; preservar legacy.

**TESTS / VERIFICATION COMMANDS:** `& .\.venv\Scripts\python.exe -m unittest tests.test_evaluation tests.test_intervals -v`.

```powershell
& .\.venv\Scripts\python.exe -m src.evaluation.evaluate --model-id model1 --config configs/evaluation.json --split val --run-dir experiments/model1/EXP-V01
& .\.venv\Scripts\python.exe -m src.evaluation.evaluate --freeze-operating-point --predictions experiments/model1/EXP-V01/predictions.jsonl --config configs/evaluation.json --out configs/evaluation_frozen.json
& .\.venv\Scripts\python.exe -m src.evaluation.evaluate --model-id model1 --config configs/evaluation_frozen.json --split test --run-dir experiments/model1/EXP-R02
& .\.venv\Scripts\python.exe -m src.evaluation.evaluate --model-id model2 --config configs/evaluation_frozen.json --split test --run-dir experiments/model2/EXP-R03
& .\.venv\Scripts\python.exe -m src.statistics.intervals --predictions experiments/model1/EXP-R02/predictions.jsonl --groups data/manifests/model1_clean_manifest.csv --seed 42 --resamples 2000 --out artifacts/metrics/model1_intervals.json
```

Los intervalos M2 usan `experiments/model2/EXP-R03/predictions.jsonl` y `data/manifests/model2_frozen_manifest.csv` con la misma CLI y salida `artifacts/metrics/model2_intervals.json`. Ejecutar también `& .\.venv\Scripts\python.exe -m src.statistics.intervals --m2-sensitivity --predictions experiments/model2/EXP-R03/predictions.jsonl --groups data/manifests/model2_frozen_manifest.csv --seed 42 --resamples 2000 --out artifacts/metrics/model2_sensitivity.json`; el modo emite las tablas, confusiones, draws y reporte hermanos especificados. Remuestrear group_id de máxima dependencia conocida, cluster sólo si es la unidad conservadora disponible; no anunciar independencia biológica ni tamaño efectivo demostrado. Exigir una correspondencia total y única entre image_id de cada predicción y grupo del manifiesto; un ID ausente, repetido o de DATA-004 en lugar de DATA-005 aborta. Probar el fallo con copias de igual hash pero SRC distintos.

**EXPECTED RESULTS:** Métodos correctos, valores observados, conteos reconciliados e intervalos o indefinición explícita. Conservar el registro de acceso al test y hashes. No usar métricas redondeadas como entrada a otros cálculos.

**ARTIFACTS:** Predicciones JSONL, métricas JSON, matrices CSV, intervalos, tabla de diferencias y figuras finales vinculadas al run.

**REVIEW-IDs SATISFIED:** REVIEW-03,04,05,09; apoya REVIEW-12/15.

## TASK-06 — Benchmark verificable

**FILES:** crear `src/benchmarks/run.py`, `tests/test_benchmark.py`, `configs/benchmark.json`; `artifacts/metrics/benchmark_raw.csv`, `reports/benchmark_report.md`.

**CONSUMES:** Pesos y configuración congelados, pool de validación fijado y cascada CLI copiada con atribución a `src/cascade/runtime.py` sólo con cambios necesarios de salidas y temporizador. No integrar la API.

**PRODUCES:** `summarize(times_ns:list[int])->dict`; `measure(stages:list[tuple[str,callable]],clock)->dict`; Tiempos por imagen, repetición y etapa, con fronteras de la SPEC; `.speed` interno se etiqueta por separado.

**PRECONDITIONS:** Entorno y hardware identificados. No importar código legacy que escriba fuera. Raspberry Pi bloqueada si no se aporta acceso real.

**STEPS:**

- [ ] RED: Un reloj falso incrementa 1 ms por lectura; cada etapa con dos lecturas dura 1 ms y dos etapas suman 2 ms. El tiempo exterior se calcula con sus propias lecturas y puede ser mayor: no igualarlo automáticamente a la suma ni contabilizarlo dos veces. Los warmups no aparecen en el registro medido. La anotación se incluye en end-to-end y se excluye de cascade. `summarize([1,2,3,4])` mediana=2.5, media=2.5, mínimo=1 y máximo=4; rechazar n=0 y tiempos negativos.
- [ ] Implementar perf_counter_ns y fronteras wall sin sumar dos veces los tiempos internos. Registrar threads=1, batch=1, FP32, entradas 640/224, diez warmups y cien iteraciones por imagen. Probar con mock la sincronización condicional de CUDA.
- [ ] Congelar el pool de hasta 32 imágenes de validación mediante el algoritmo por estratos y orden (SHA256, image_id) de la SPEC. Guardar la selección antes de observar latencias. Conservar el número de frutos predichos, llamadas M2 y fallos; no descartar ejecuciones por ser lentas.
- [ ] Ejecutar el benchmark en CPU real. Reportar media, mediana, desviación estándar, p95, mínimo y máximo, con la definición del percentil versionada. Mostrar distribución total y por imagen o carga de trabajo.
- [ ] Si falta Raspberry Pi, escribir `BLOCKED_BY_HARDWARE` y el protocolo; no crear filas de medición para Pi. Los resultados CPU no sustituyen Pi. Retirar claims cuantitativos sin sustento en TASK-09.

**TESTS / VERIFICATION COMMANDS:** `& .\.venv\Scripts\python.exe -m unittest tests.test_benchmark -v`; `& .\.venv\Scripts\python.exe -m src.benchmarks.run --config configs/benchmark.json --out artifacts/metrics/benchmark_raw.csv --report reports/benchmark_report.md`.

**EXPECTED RESULTS:** El registro contiene cien iteraciones por imagen y protocolo, con warmups separados. Número de fallos y fronteras claros; no forzar objetivos de 145 ms o 5 s.

**ARTIFACTS:** Tiempos crudos, resumen, hardware, OS, runtime, manifiesto de entradas y protocolo Pi o bloqueo.

**REVIEW-IDs SATISFIED:** REVIEW-07; REVIEW-08 medido sólo con Pi real o respuesta razonada por bloqueo.

## TASK-07 — Ground truth y contrato end-to-end

**FILES:** crear `src/evaluation/cascade.py`, `tests/test_cascade.py`, `data/manifests/cascade_annotation_schema.json`, `reports/cascade_ground_truth_assessment.md`, `reports/cascade_protocol.md`.

**CONSUMES:** Esquemas DATA-001/005/006, cascada y posible GT independiente suministrado. Nunca predicciones como etiquetas.

**PRODUCES:** `validate_ground_truth(rows:list[dict])->None`; `score_cascade(gt:list[dict],pred:list[dict],iou_threshold:float=.5)->dict`; esquema y protocolo de la SPEC. CLI `--annotations --predictions --out`; modo `--check-availability --out` genera assessment sin métricas.

**PRECONDITIONS:** Métodos y protocolo fijos. La rama experimental sólo continúa con GT independiente real. Estado inicial: BLOCKED_BY_GROUND_TRUTH.

**STEPS:**

- [ ] RED Con dos frutos enfermos GT y una detección con diagnóstico correcto, recall conjunto=0.5. Si el diagnóstico de esa única detección es erróneo, recall=0. Dos predicciones sobre el mismo GT dejan un FP. Rechazar GT de origen `model_prediction`; una abstención M2 cuenta como FN.
- [ ] Reutilizar matching de TASK-05. El denominador de recall primario incluye todos los enfermos adjudicados. Separar clasificación condicional y tasa de abstención. No contar sanos como éxitos del recall de enfermedad.
- [ ] Revisar GT real y enlazar fuentes. Si sólo hay etiquetas mango o binarias, emitir assessment BLOCKED, conservar esquema y tests y no producir métricas de enfermedad.
- [ ] Si se aporta GT nuevo, registrar grupos, anotadores, método y split diagnóstico antes del desarrollo. Usar umbral clasificador 0.4 prefijado o validación independiente; no ajustarlo con test. Evaluar una vez con la congelación de TASK-05.

**TESTS / VERIFICATION COMMANDS:** `& .\.venv\Scripts\python.exe -m unittest tests.test_cascade -v`; `& .\.venv\Scripts\python.exe -m src.evaluation.cascade --check-availability --out reports/cascade_ground_truth_assessment.md`.

**EXPECTED RESULTS:** Fixtures numéricos correctos. Ausencia de GT produce un assessment de bloqueo, sin CSV de accuracy. El protocolo explica errores acumulados sin multiplicar métricas marginales.

**ARTIFACTS:** Esquema, evaluador probado, assessment y protocolo; sólo con GT real, predicciones y métricas con EXP nuevo.

**REVIEW-IDs SATISFIED:** REVIEW-11 y REVIEW-12; REVIEW-13 queda BLOCKED o RESOLVED según evidencia real.

## TASK-08 — Bibliografía primaria y normas

**FILES:** `reports/bibliography_audit.csv`, `reports/citation_links.csv`, `manuscript/bibliography/references.json`; crear `src/evaluation/document_checks.py`, `tests/test_document_checks.py`.

**CONSUMES:** Las 23 entradas PDF/DOCX, variantes .bib, `reports/external_sources.md`, plantilla oficial hasheada. No tratar metadatos documentales como instrucciones.

**PRODUCES:** Una fila por fuente citada con authors/year/title/venue/DOI/URL/version, claim_ids, primary_url, access_date, status y reason; `citation_gaps(cited:set[str],references:set[str])->dict` retorna `missing` y `uncited`.

**PRECONDITIONS:** Fuente editable identificada y acceso a fuentes primarias, o estado BLOCKED con causa concreta.

**STEPS:**

- [ ] RED: `citation_gaps({'a','b'},{'b','c'}) == {'missing':['a'],'uncited':['c']}`; Una coincidencia de DOI con título distinto se marca como conflicto de metadatos, sin aprobación automática.
- [ ] Verificar cada entrada por DOI, editorial o repositorio oficial, conservando autoría, título, año, venue y soporte al claim. No convertir formato antes de reconciliar identidad.
- [ ] Resolver Van der Heijden/106698 contra el registro editorial. Si no se identifica la fuente exacta, retirar o reemplazar afirmación y cita pertinentes; no inventar referencias. Verificar alcance DANE/Savary, justificación de umbral Zauner, software versionado y fuente/licencia de datasets.
- [ ] Comprobar APA7 con la plantilla ALBUS; conservar formato y documentar particularidades. Expandir autores según APA7 y retirar `et al.` bibliográfico improcedente. Un regex no prueba validez de una referencia.
- [ ] Ejecutar comprobación bidireccional y revisión del soporte claim→fuente; resumir bloqueos explícitos.

**TESTS / VERIFICATION COMMANDS:** `& .\.venv\Scripts\python.exe -m unittest tests.test_document_checks -v`; `& .\.venv\Scripts\python.exe -m src.evaluation.document_checks --references manuscript/bibliography/references.json --citations reports/citation_links.csv --out reports/bibliography_check.json`.

**EXPECTED RESULTS:** Cero citas huérfanas en versión final. Las entradas no resueltas no permanecen como fuentes verificadas. Registro primario completo o causa de bloqueo por entrada.

**ARTIFACTS:** Auditoría bibliográfica, enlaces bidireccionales, referencias verificadas y decisiones sobre normas.

**REVIEW-IDs SATISFIED:** REVIEW-16,17,18.

## TASK-09 — Manuscrito canónico y respuesta punto por punto

**FILES:** crear `manuscript/source/Articulo_Mango_ALBUS_revision.docx`, `manuscript/output/Articulo_Mango_ALBUS_revision.pdf`, `configs/class_names.json`, `reports/editorial_audit.md`, `reports/editorial_claim_audit.csv`; extender `src/evaluation/document_checks.py` y `tests/test_document_checks.py`; actualizar figuras, tablas y matriz CLAIM, `docs/response_to_reviewers.md`, changelog y registro de artefactos.

**CONSUMES:** Fuente DOCX confirmada, métricas finales sin redondeo o retirada de claims, bibliografía, bloqueos y matriz REVIEW.

**PRODUCES:** Un único editable canónico, render final, relación CLAIM→ART/EXP→ubicación y respuesta fiel a los 18 IDs. Copiar la fuente completa una vez con hash; usar las habilidades de documentos y PDF antes de editar o renderizar.

**PRECONDITIONS:** Gates D/E aplicables completos, o resultados bloqueados retirados del alcance sin afirmar su validación. Decisiones científicas fijas. No redactar como realizadas acciones pendientes de revisión.

**STEPS:**

- [ ] Copiar el DOCX ALBUS exacto y registrar hashes de origen/destino antes de editar. Enlazar la relación GENE con el PDF. Conservar legacy intacto.
- [ ] Preparar tablas desde metrics JSON sin redondeo intermedio. Un test agrega un CLAIM ficticio con valor obsoleto y document_checks debe rechazarlo. Comprobar .9094733437→'.909', .8314606742→'.831'; No usar CSV de cuatro decimales como fuente final.
- [ ] Auditar «DETECCIÓN TEMPRANA» y «EFICIENTE» y sus variantes en título, resumen, contribuciones y conclusión. Registrar ubicación/frase original, evidencia y decisión por claim. No hay criterio operacional de eficiencia comparativa en el freeze propuesto: sustituir por descripción neutral «automatizada», «visual» o «mediante una arquitectura en cascada». Sólo conservar «eficiente» con criterio operacional previo verificable o comparador adecuado; nunca diseñar benchmark después de ver latencia para justificarlo. Retirar temporalidad no probada, describir signos visuales; mantener campo objetivo, API binaria separada y métricas coherentes.
- [ ] Normalizar lenguaje de fuga en manuscrito/respuesta/matriz CLAIM: forma evaluada, algoritmo/parámetros, origen/secuencia, límites y relaciones no excluibles. Usar «sin contaminación cross-split detectada bajo el protocolo especificado» cuando corresponda. Prohibidas afirmaciones propias «sin duplicados» para clean, «libre de fuga» e «independencia demostrada»; citas históricas se identifican y no se presentan como conclusiones. Reportar duplicación intra-split y sensibilidad M2 manteniendo interpretación primaria aprobada.
- [ ] Extender document_checks con `claim_language_issues(rows:list[dict])->list[dict]`: filas incluyen location,claim,text,quote_status,evidence,decision; fixture eficiente sin criterio previo se rechaza en cada una de las cuatro ubicaciones; benchmark único descriptivo no satisface eficiencia comparativa. Frase absoluta de fuga propia falla; cita histórica claramente atribuida puede conservarse pero no cuenta como evidencia propia. Un match léxico demanda revisión contextual, no demuestra por sí solo validez. Guardar `reports/editorial_claim_audit.csv` además del reporte. Respetar plantilla en resumen.
- [ ] Corregir texto embebido en figuras: Fig. 1 reconoce terceros y cuatro patologías+Saludable; Fig. 2 muestra la ruta API real. Revisar nomenclatura, captions y referencias internas. Cada figura experimental debe derivar del run final; las cualitativas explicitan parámetros y ausencia de GT.
- [ ] Revisar cada REVIEW-ID: Comment, Interpretation, Response, Evidence, Changes in Manuscript con página/párrafo final y Status. Para Pi o GT bloqueados, explicar causa y alcance limitado con artefactos; no decir «corregido».
- [ ] Renderizar DOCX a PDF con una herramienta disponible y documentada; guardar comando, versión y exit code. Si Word/LibreOffice no está disponible, comprobar el runtime de documents. Si no hay render funcional, GATE-G queda BLOCKED; no afirmar build exitoso.
- [ ] Inspeccionar todas las páginas: tablas sin cortes, captions legibles, nomenclatura, bibliografía y referencias internas. Extraer texto final y comparar claims y métricas contra artefactos; los cambios de formato no pueden ocultar resultados.

**TESTS / VERIFICATION COMMANDS:** `& .\.venv\Scripts\python.exe -m unittest tests.test_document_checks -v`; `& .\.venv\Scripts\python.exe -m src.evaluation.document_checks --docx manuscript/source/Articulo_Mango_ALBUS_revision.docx --metrics artifacts/metrics --claims docs/research/claim_evidence_matrix.csv --out reports/manuscript_consistency.json`; `pdftoppm -scale-to 1600 -png manuscript/output/Articulo_Mango_ALBUS_revision.pdf manuscript/output/page`.

**EXPECTED RESULTS:** Ningún claim crítico UNVERIFIED oculto; retiradas documentadas; cifras, tablas y figuras coincidentes; render revisado visualmente. Esto no equivale a aceptación editorial.

**ARTIFACTS:** DOCX/PDF, nuevos ART, auditoría editorial, respuesta y detalle de cambios.

**REVIEW-IDs SATISFIED:** REVIEW-04,06,10,11,12,14,15,16,17,18; Todas las demás observaciones se reflejan en sus respuestas con estado verdadero.

## TASK-10 — Verificación fresca, revisión adversarial y entrega

**FILES:** `reports/final_adversarial_review.md`, `reports/reproduction_check.md`, `reports/protocol_compliance.json`, `reports/portability_check.json`, `docs/final_validation_report.md` y README; extender `tests/test_provenance.py` y `tests/test_document_checks.py` sólo para contratos nuevos de verificación; no editar legacy ni el freeze.

**CONSUMES:** SPEC, plan, artefactos finales, tests, evidencia y registros. El revisor no recibe conclusiones persuasivas.

**PRODUCES:** Comandos desde entorno limpio, exit codes, hashes, matriz de gates y hallazgos finales.

**PRECONDITIONS:** tareas previas documentadas, sin hallazgos críticos ocultos y con revisor independiente disponible.

**STEPS:**

- [ ] Verificar freeze/hash/commit, historia append-only de amendments/deviations, registro de acceso a test y reglas efectivas de cada run. RED de contrato: alterar un byte de copia de SPEC congelada o referir una enmienda inexistente falla; no tocar snapshot real. Confirmar que cada cambio científico posterior enlaza evidencia, estado test, decisión y reviewer; ningún bug con efecto en resultados se esconde como detalle técnico.
- [ ] Verificar portabilidad con un mapping alterno sobre copias mínimas sintéticas/de lectura: mismo SRC/logical_path/SHA se resuelve independientemente del prefijo absoluto; root faltante o escape falla. Registrar en `reports/portability_check.json`; guía de reproducción documenta roots y evidencia absoluta de la máquina sólo como dato local.
- [ ] Verificar AMENDMENT↔REVIEW↔TASK, adjudicación A/B y desacuerdos resueltos en decisiones usadas, sensibilidad M2 y sus CI/indefiniciones, cobertura ambiental incluida pip check, auditoría eficiente/temprana y lenguaje de fuga. `reports/protocol_compliance.json` lista estado real/evidencia por enmienda, sin elevar BLOCKED a validado.
- [ ] Ejecutar toda la suite y una comparación fresca de legacy. Comprobar que las salidas estén contenidas en el workspace. Los cambios previos de Semillero siguen atribuidos al estado inicial.
- [ ] En un entorno limpio dentro del workspace, reconstruir un run de evaluación desde entradas congeladas sin seleccionar parámetros nuevos. Usar tolerancia 1e-6 para métricas derivadas de las mismas predicciones; explicar diferencias de backend en predicciones. Una nueva inferencia de test es auditoría del resultado final y no permite volver a seleccionar parámetros.
- [ ] Dar a un revisor fresco: «Intenta encontrar razones técnicamente justificables para rechazar este manuscrito». Inspeccionar fuga, contaminación de test, selección retrospectiva, sesgo de selección, muestras pequeñas, intervalos, replicabilidad, claims, OOD, YOLO, benchmark, GT, citas, figuras y tablas obsoletas. Registrar hallazgos, incluidos los que obliguen a reabrir gates.
- [ ] Resolver hallazgos HIGH/MEDIUM por su causa raíz y repetir las verificaciones afectadas. Si exige enmienda material tras test observado o cambia interpretación primaria, aplicar parada global y decisión del usuario conforme a SPEC §11; no corregir silenciosamente para pasar revisión. No sustituir revisión independiente por self-review. Si falta el revisor, GATE-I queda BLOCKED.
- [ ] Actualizar respuesta e informe final: cada REVIEW resuelto o justificadamente bloqueado, cada CLAIM crítico soportado, moderado o retirado y reproducción con rutas y comandos completos. Aplicar finishing-a-development-branch a la rama local autorizada sólo con validación completa; conservar commits/ledger y no ejecutar push, merge externo ni publicación. Si esos pasos fueran necesarios, rige la condición de parada del usuario.

**TESTS / VERIFICATION COMMANDS:** `& .\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -v`; `& .\.venv\Scripts\python.exe -m src.evaluation.provenance --source-manifest provenance/source_manifest.csv --source-locations provenance/source_locations.csv --root-mapping configs/root_mapping.json --out reports/legacy_final_verification.json`; ejecutar comprobación documental final de TASK-09; `$env:GIT_OPTIONAL_LOCKS="0"`; `git -C C:/Users/junio/Downloads/mango-vision/Mango-vision status --short`; `git -C C:/Users/junio/Downloads/mango-vision/SemilleroTI-Mangos status --short` (resolver estas ubicaciones desde `legacy_corpus` para otra máquina). Comparar también HEAD, diff index/worktree y estado untracked con baseline inicial, no sólo status.

**EXPECTED RESULTS:** sin fallos de método; fuentes hasheadas intactas; cero hallazgos HIGH/MEDIUM abiertos; limitaciones científicas explícitas. Si falta un requisito, no declarar revisión DONE.

**ARTIFACTS:** reporte de validación fresca, revisión adversarial, guía de reproducción y respuesta final.

**REVIEW-IDs SATISFIED:** comprobación integral de los 18; no cambia estado BLOCKED sin evidencia.

## Cobertura y salida de esta planificación

|Review|Tasks|Resultado exigido|
|---|---|---|
|01|01,02|Auditoría M1 reproducible|
|02|02,03|Grupos y freeze|
|03|03,04,05|Decisión de reentrenamiento y evaluación válida|
|04|05,09|Denominadores y limitación|
|05|05|CI apropiados o insuficiencia explícita|
|06|09|Prevalencia retirada sin fuente|
|07|01,06|Benchmark con tiempos crudos|
|08|06,09|Pi real o resultado retirado/bloqueado|
|09|01,04,05|Versiones, hashes y procedencia|
|10|09|Alcance visual sin temporalidad no demostrada|
|11|07,09|Campo objetivo separado de validación|
|12|07,09|Propagación y denominadores conjuntos|
|13|07|Evaluador+GT o BLOCKED_BY_GROUND_TRUTH|
|14|09|Auditoría editorial y render|
|15|05,09|Taxonomía y nombres coherentes|
|16|08,09|APA7 compatible con plantilla|
|17|08|Software/datasets identificados|
|18|08,09|Citas bidireccionales y fuentes pertinentes|

La ejecución elegida por el usuario en su solicitud es subagent-driven-development secuencial. No se pide de nuevo elegir método. Próximo gate: revisión independiente fresca del delta sin HIGH/MEDIUM abiertos y freeze; cumplidas las condiciones de la autorización ya recibida, registrar B/C=SATISFIED y comenzar TASK-01 automáticamente. No volver a pedir aprobación entre tareas ordinarias; detener globalmente sólo en las cinco condiciones de SPEC §11.

## Correspondencia de enmiendas, REVIEW y entregables

|Enmienda|REVIEW vinculados|TASK / preflight|Contrato y evidencia|
|---|---|---|---|
|AMENDMENT-01|09; todos por trazabilidad|Preflight,01,10|Git exclusivo, baseline exacto, worktree/commits candidatos locales, revisión BASE..HEAD y ledger; legacy read-only y hashes/status iguales al inicial|
|AMENDMENT-02|01,02,03,05,07,09|Preflight,01,10|Freeze antes de nuevas observaciones, commit+SHA, reglas completas, test histórico observado y amendments append-only; protocolo verificado por run|
|AMENDMENT-03|01,02|02,03,10|Dos pasadas A/B ciegas, grande≥10, cobertura relevante, acuerdo explícito y resolución separada; procedencia documental prioritaria|
|AMENDMENT-04|02,04,05,09|02,05,09,10|Counts/distribución, principal image-weighted, exact-SHA y cluster-weighted, deltas/CI pareados, indefinición y límites de independencia|
|AMENDMENT-05|09,17|01,10|Identidad completa entorno, índices/config sin secretos, report/check/JSON/build/hashes, root mapping/SRC/path y verificación portable|
|AMENDMENT-06|07,08,10,14|06,09,10|Detección temprana y eficiente en cuatro ubicaciones; criterio previo o neutralización, sin benchmark retrospectivo para salvar claim|
|AMENDMENT-07|01,02,04,14|02,03,09,10|Lenguaje de contaminación detectada con algoritmo/parámetros/evidencia/límites; no independencia universal ni clean sin duplicados|
