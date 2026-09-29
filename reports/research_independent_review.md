# Revisión independiente documental y de diseño — ALBUS26-116

Fecha: 2026-09-17. Alcance: primera fase, SPEC y plan propuestos. No es la revisión científica adversarial final ni acredita cumplimiento de los gates experimentales.

Se leyeron la solicitud original, el dictamen extraído, el texto del PDF sometido, genealogía, matriz REVIEW, matriz CLAIM, arqueología de datasets, registros EXP/ART, comprobaciones aritméticas guardadas y código instalado relevante de Ultralytics. La identidad del PDF sometido se acepta según confirmación expresa del usuario. No se ejecutaron modelos, pHash, splits, entrenamiento, benchmarks ni builds; no se modificaron los documentos revisados.

Raíz de las rutas siguientes: `C:/Users/junio/Downloads/mango-vision/`. Abreviaturas: **S** = `ALBUS26_major_revision/docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md`; **P** = `ALBUS26_major_revision/docs/superpowers/plans/2026-09-17-albus26-major-revision.md`.

Snapshot revisado: SHA256 S `c012fdc3af3204cd8e4032c1cc93aa758f2cc4ea73c4561f9c22a25807d439c4`; SHA256 P `2d71f1e0c17c094c366f2c4a72696912c51658829d058786fa58b0061f19fcf8`. Los localizadores corresponden a ese contenido.

## Hallazgos accionables

### RIR-01 — HIGH — La época seleccionada puede no tener un checkpoint conservado

**Evidencia:** S:75 y P:179–198 exigen máximo mAP50–95 y primera época en empate. El test propuesto sólo verifica el entero 137. En el runtime propuesto, `SemilleroTI-Mangos/.venv/Lib/site-packages/ultralytics/engine/trainer.py:684–687` sobrescribe `best.pt` cuando `best_fitness == fitness`; `ultralytics/cfg/default.yaml:18` fija `save_period: -1`. Por tanto, un empate posterior reemplaza los pesos de la primera época y no deja necesariamente una copia recuperable. Además, `trainer.py:824–832` escribe el CSV con `%.6g`: seleccionar desde ese CSV puede confundir métricas distintas que se redondean igual.

**Impacto:** el registro podría declarar una época y evaluar pesos de otra; afecta REVIEW-03/09 y la comparación validación/test del mismo modelo.

**Criterio de corrección:** definir una política compatible con los checkpoints realmente retenidos. La opción mínima es adoptar y documentar el desempate nativo; si se conserva la primera época, guardar explícitamente su checkpoint. La selección debe usar fitness sin redondear y registrar época/hash. Añadir una prueba con empate y otra con valores que colapsen a seis cifras, comprobando el artefacto seleccionado, no sólo el número de época.

### RIR-02 — HIGH — El aislamiento de escrituras omite efectos de importación del runtime

**Evidencia:** S:43 y P:14/21 prohíben caches y salidas fuera del workspace. P:28–40/79–81 prepara el entorno sin configurar sus directorios de estado. En `SemilleroTI-Mangos/.venv/Lib/site-packages/ultralytics/utils/__init__.py:910–924`, Windows usa por defecto `AppData/Roaming/Ultralytics`; líneas 957, 1380–1384 y 1463–1464 inicializan/validan settings y cache durante la importación. El `check_output` del wrapper no intercepta esos efectos. La instalación con pip también deja sin fijar su cache.

**Impacto:** ejecutar el plan tal como está puede escribir fuera del espacio autorizado, aunque todos los argumentos `--out` sean correctos.

**Criterio de corrección:** fijar directorios de configuración/cache dentro del workspace antes de instalar/importar dependencias, al menos `YOLO_CONFIG_DIR` y la política de cache de pip; revisar los demás escritores del runtime elegido. Registrar esas variables y comprobar aislamiento en un proceso hijo. No usar como demostración una importación que ya haya escrito en el perfil global.

### RIR-03 — MEDIUM — SPEC y plan eligen versiones distintas para el nuevo entrenamiento M1

**Evidencia:** S:73 pide recuperar Ultralytics 8.4.39 y cambiar de entorno sólo ante incompatibilidad documentada. P:33–40 instala únicamente 8.4.52; TASK-04 consume el entorno TASK-01 (P:177) y no introduce otro entorno ni el punto de decisión requerido. La etiqueta «entorno reconstruido» evita afirmar reproducción exacta, pero no resuelve la contradicción operativa.

**Criterio de corrección:** acordar una única versión explícita para el futuro M1, con justificación, o separar los entornos M1/M2 y añadir la comprobación de compatibilidad antes del run. Configuración, comando y SPEC deben coincidir. Actualizar también `reviewer_matrix.md:184`: 8.4.39 ya fue recuperada del checkpoint; no sigue totalmente ausente como Python/PyTorch/CUDA.

### RIR-04 — MEDIUM — Varios enlaces de evidencia no sustentan los conteos marcados SUPPORTED

**Evidencia:** `ALBUS26_major_revision/docs/research/claim_evidence_matrix.csv:5–6,10` enlaza CLAIM-004/005/009 únicamente a SRC-009684 o SRC-000463. Se comprobaron ambos YAML: contienen rutas, nombres de clases y, en M1, metadata Roboflow; no contienen 502/134/33, conteos de instancias ni 300 imágenes por clase. Esos conteos sí tienen soporte en `data/manifests/legacy_dataset_inventory.csv` y `reports/datasets/counts_by_split_class.csv`, explicados en `dataset_archaeology.md`.

**Impacto:** los IDs existen, pero seguir el enlace de la matriz no lleva a la evidencia numérica exigida. Tampoco los conteos actuales prueban por sí solos la membresía de EXP-001/004 histórica.

**Criterio de corrección:** añadir referencias o IDs registrados de los manifiestos/conteos derivados y su relación con las fuentes. Mantener SUPPORTED únicamente para el snapshot local explícito; conservar por separado la incertidumbre sobre entradas históricas de los runs.

### RIR-05 — MEDIUM — CLAIM-031 respalda una procedencia que la arqueología no demuestra

**Evidencia:** `claim_evidence_matrix.csv:32` marca SUPPORTED «cajas originales cubren imagen completa». `reports/submitted_candidate_text.txt:214` confirma que ésa es la afirmación del paper; sin embargo, `reports/datasets/dataset_archaeology.md:20–21,47` distingue DATA-002 por carpetas/Labels.csv, sin labels YOLO, de DATA-003/004 con cajas full-frame. El propio `revision_action` dice «cajas derivadas», incompatible con respaldar sin reserva su carácter original. Asimismo, `reviewer_matrix.md:221` llama «binario» al conjunto propio, cuando DATA-006 tiene una sola clase `mango`, sin etiquetas Enfermo/Saludable.

**Criterio de corrección:** separar la observación de cajas full-frame presentes de la procedencia original no acreditada; ajustar estado/texto de CLAIM-031 y enlazar la evidencia correspondiente. Describir DATA-006 como localización de una sola clase. No atribuir anotaciones diagnósticas ausentes.

### RIR-06 — MEDIUM — Texto pegado impide una lectura fiable del plan para aprobación

**Evidencia:** P:119–120 incluye «1.500membresías», «yauditar YAML aoriginal», «M2contaminado exige enmienda dereentrenamientoM2». El problema se vuelve sistemático en TASK-03–10, por ejemplo P:160–167, 235–240 y 347–353. S también contiene casos como «para669», «No presentar11/13» y «aLaTeX».

**Impacto:** no es sólo estilo: oculta negaciones, límites y precondiciones en documentos que el usuario debe aprobar y que implementadores nuevos deben ejecutar.

**Criterio de corrección:** restaurar espacios y redacción normal en toda la prosa, preservando comandos, identificadores, fórmulas y valores. Hacer una lectura completa del plan corregido; una sustitución puntual no cubre el patrón.

## Comprobaciones y límites

- El dictamen sustantivo está representado por los 18 REVIEW-ID. No se detectó una omisión mayor de sus peticiones en la cobertura propuesta.
- La comprobación CSV encontró 50 CLAIM-ID y nueve EXP-ID, sin IDs duplicados ni referencias SRC numéricas inexistentes en las claims. La validez de un ID no demuestra que su contenido sustente el claim; RIR-04 aborda ese problema semántico.
- Los registros distinguen observación de reproducción, mantienen `reproduced=NO` y bloquean la cascada sin GT. Los documentos revisados no aportan evidencia de ejecución experimental nueva en esta primera fase; esta lectura no sustituye la comparación final de hashes legacy.
- La ausencia de GT conjunto, hardware Pi y entorno histórico M1 se comunica explícitamente. No se exige inventar esas dependencias para corregir los hallazgos documentales.

Antes de presentar SPEC/plan como listos para aprobación, corregir RIR-01–06 y revisar los cambios. Este informe no autoriza ejecutar el plan ni declara terminada la revisión científica.
