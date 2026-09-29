# Decisiones metodológicas — enmiendas antes del freeze

SPEC y plan cuentan con aprobación conceptual condicional del usuario del 18-09-2026. El gate efectivo requiere revisión independiente fresca sin HIGH/MEDIUM abiertos y freeze anterior a TASK-01. Esta edición no ejecuta experimentos ni afirma ese gate satisfecho.

|Decisión|Regla concreta|Justificación y límite|Tarea|
|---|---|---|---|
|Unidad de independencia|Fruto, escena o secuencia documentada; grupo conservador si el origen sólo es probable|pHash y filename no demuestran identidad biológica|02–03|
|Similitud|SHA256 y pHash64 Hamming <5; banda 5–10 revisada sin consultar rendimiento|Conservar relaciones exactas, cercanas, posibles y confirmadas separadas|02|
|Split M1|Mantener sólo si auditado; cambio obliga a reentrenar desde base|Grupos atómicos, seed 42, objetivo 70/15/15; algoritmo y bloqueos definidos en SPEC §6|03–04|
|M2 principal y sensibilidad|Principal image-weighted; exact-SHA-dedup menor image_id por SHA con GT consistente; cluster-weighted peso1/tamaño del cluster. Confusión float y macroF1 sobre las cinco clases fijas|Counts imágenes/SHA/clusters/distribución no son independencia biológica. Diferencias secundaria−principal, sin reentrenamiento automático por duplicación intra-split|02,05|
|Entorno nuevo|Python 3.12.14 y Ultralytics 8.4.52 propuestos; compatibilidad pendiente|Reconstruido, no idéntico al M1 histórico 8.4.39; todas las cachés y temporales contenidos|01|
|Checkpoint|Fitness sin redondear, último empate máximo según guardado nativo|Registrar época y hash de pesos conservados antes/después del stripping; nunca elegir desde CSV redondeado|04|
|Punto operativo|F2 de Enfermo en validación, rejilla .05:.05:.95, empate menor umbral|Regla prefijada que prioriza recall; AP con score mínimo .001 separado de confusión|05|
|Incertidumbre|95%, bootstrap2000 seed42 por group_id de máxima dependencia; draws compartidos para principal/sensibilidades M2/deltas, con ocurrencias separadas y dedup dentro de ocurrencia; Wilson sólo con independencia justificada|<2 grupos por clase o >5% indefinidas bloquea CI respectivo; no eliminar clases ausentes del macroF1 ni ocultar draws indefinidos. Intervalos no corrigen sesgo|05|
|Latencia|Equipo real, batch 1, FP32, 10 warmups y 100 repeticiones por imagen|Pool ≤32 de validación fijado por hashes y estratos; separar tiempos internos, wall, cascada y archivo→JPEG|06|
|GT conjunto|Cajas y enfermedad específica por fruto, adjudicación independiente|No usar predicciones como verdad ni multiplicar recalls de datasets distintos|07|
|Fuente editorial|Copiar DOCX ALBUS después de autorización; render final|Texto normalizado coincide con PDF enviado; conservar originales y registrar cambios|09|

Los contratos completos, incluyendo fórmulas, casos de error y rutas, están en `docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md` y en las tareas correspondientes del plan. DECISION-001–025 conserva razones e historial. Una incompatibilidad material requiere enmienda documentada y, después de observar test o si afecta interpretación primaria, decisión del usuario según las cinco condiciones de SPEC §11; no sustitución silenciosa.

|Enmienda|Regla congelable|Control y salida|Tareas|
|---|---|---|---|
|AMENDMENT-01|Git nuevo sólo revisión, baseline exacto y commits locales por tarea; legacy read-only incluido .git|Ledger/hash/diff y comparación fresca con estado inicial; GIT_OPTIONAL_LOCKS=0 al leer legacy. No push/merge externo/publicación ni grandes innecesarios|Preflight,01,10|
|AMENDMENT-02|Snapshot de SPEC/plan con commit+SHA y protocolo completo antes de TASK-01; test histórico ya observado registrado true|Freeze append-only; PROTOCOL-AMENDMENT-XXX con evidencia, impacto y reviewer para cambios materiales, también bugs con efectos científicos. Gate del usuario si cambia materialmente protocolo tras test o interpretación primaria|Preflight,01,10|
|AMENDMENT-03|A/B ciegos independientes; grande≥10; cross-split/conflictos/posibles secuencias/banda5–10 relevantes reciben dos juicios cuando visuales|Sin métricas/modelos/consecuencias/primera pasada; split/rutas/clases cegados cuando posible. Decisiones originales, agreement, adjudicación separada si desacuerdo, evidencia y rationale. Procedencia prevalece y no exige N² por video|02,03,10|
|AMENDMENT-04|Mantener interpretación principal M2 y reportar tres estimandos/denominadores/deltas/CI agrupado si calculable|SHA con GT conflictivo bloquea dedup; groups conservan todos sus clusters; no dedup entre ocurrencias bootstrap; formas de ponderación y undefined en SPEC §7|02,05,09,10|
|AMENDMENT-05|Identidad del entorno/artefactos de instalación y referencias reconstruibles por root mapping|legacy_corpus→corpus; external_mail→Downloads; revision→checkout. SRC/logical_path separados de ruta absoluta; originales intactos y hash cotejado. Índices/env sólo pertinentes, credenciales redactadas|01,10|
|AMENDMENT-06|Eficiencia requiere definición previa y criterio verificable o comparador; benchmark actual descriptivo implica descripción neutral|Revisar eficiente y detección temprana en título/resumen/contribuciones/conclusión; no benchmark retrospectivo salvador|06,09,10|
|AMENDMENT-07|Conclusiones de contaminación detectada acotadas al protocolo, no garantía biológica universal|Cada conclusión informa forma/algoritmo/parámetros/origen/secuencia/límites/relaciones no excluidas; citas históricas separadas de claims propios|02,03,09,10|

Continuidad: los bloqueos previstos Pi, GT conjunto y M1 histórico exacto conservan estado experimental BLOCKED; no se presentan como gates D/E satisfechos, pero permiten desarrollar/validar las ramas independientes. Las únicas paradas globales son acción destructiva/externa requerida; push/merge/publicación; falta de evidencia que vuelva especulativas todas las alternativas; cambio material del protocolo tras test observado; enmienda que afecte interpretación primaria.
