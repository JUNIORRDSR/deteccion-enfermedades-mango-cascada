# TASK-02 — Auditoría reproducible de fuga, M1 y M2

Ejecución fresca con los parámetros congelados por la SPEC §5: Pillow 12.2.0, ImageHash 4.3.2, `imagehash.phash(image.convert("RGB"), hash_size=8, highfreq_factor=4)`, sin orientación EXIF ni recorte automático, Hamming `<5` como umbral operacional y banda 5–10 inspeccionada para estudiar el fallo del criterio.

Comparación cuadrática completa. Cada par no ordenado se compara una vez. Union-find con representante mínimo, reimplementado desde `legacy_corpus:Mango-vision/src/data_prep/dedup_and_resplit.py` sin sus efectos secundarios, con atribución.

**Estado (2026-09-25):**

- Completos los resultados algorítmicos, la adjudicación ciega A/B y la tercera pasada de los 35 candidatos originales.
- Cerrada la adjudicación suplementaria de los 47 candidatos (§4 ter, DECISION-034 y DECISION-035). La partición de TASK-03 está congelada y la revisión de puerta de la ronda 6 (`reports/amendments/gate-review-exp-r01.md`, parte B) la aceptó como entrada de EXP-R01.
- Las relaciones que se describen aquí son juicios operativos de revisores agente, no verdad biológica.

## 1. El resultado que valida el manuscrito

La partición original de MangoDHDS (DATA-003) reproduce **exactamente** lo que afirma el artículo:

| cantidad | manuscrito | esta auditoría |
|---|---|---|
| pares near-duplicate cruzando splits | 76 | **76** |
| de ellos a Hamming 0 | 60 | **60** |
| train ↔ valid | 55 | **55** |
| test ↔ train | 18 | **18** |
| test ↔ valid | 3 | **3** |
| clusters tras deduplicar | 1.337 | **1.337** |

Esto pasa de `PARTIALLY_SUPPORTED` a **`REPRODUCED`**: una ejecución independiente, desde las imágenes, con parámetros declarados, recupera las cifras publicadas. El análisis de deduplicación del artículo es correcto y reproducible, y conviene decirlo con esa claridad en la respuesta al revisor.

### Un matiz que el manuscrito no hace y debería

De los 76 pares cruzados, **41 son idénticos byte a byte** (SHA256 igual) y **19 más son perceptualmente idénticos pero binariamente distintos** — típico de un reencodeo. Los 16 restantes están a distancia 2 o 4.

«Hamming 0» y «mismo archivo» no son lo mismo, y el artículo los trata como equivalentes. Con estos números la corrección es concreta: 41 duplicados exactos y 19 casi-duplicados a distancia 0.

## 2. La deduplicación funcionó, verificado

| dataset | imágenes | SHA únicos | clusters | clusters cruzando splits |
|---|---|---|---|---|
| DATA-003, partición original | 1.500 | 1.400 | 1.337 | **65** |
| DATA-004, partición limpia | 1.500 | 1.400 | 1.337 | **0** |

De los 65 clusters cruzados originales, **18 tocaban el test** (15 test–train, 2 test–train–valid, 1 test–valid). Tras el re-split, cero. La estructura interna es idéntica porque son las mismas 1.500 imágenes reparticionadas: distribución de tamaños {1: 1.189, 2: 137, 3: 7, 4: 4}, sin clases discordantes por SHA.

**Lo que esto NO autoriza:** los archivos redundantes intra-split siguen ahí. La SPEC es explícita en que «duplicados intra-split por sí solos NO autorizan reentrenamiento». M2 **no se reentrena**; su sensibilidad se cuantifica en TASK-05 sobre predicciones guardadas.

### 2.1 El n efectivo del test de M2 es menor de lo que yo mismo había estimado

Una revisión adversarial independiente recomputó la estructura por split y encontró más redundancia de la que yo había contado, porque yo sólo había mirado igualdad de bytes. Verificado después por mi cuenta sobre `data/audits/model2/clusters.csv`:

| split | archivos | SHA únicos | clusters pHash | redundancia |
|---|---|---|---|---|
| train | 1.064 | 986 | **935** | 129 |
| valid | 217 | 206 | **199** | 18 |
| **test** | **219** | 208 | **203** | **16** |

El estimando principal congelado de M2 (SPEC §7) sigue siendo la exactitud por imagen sobre las 219 imágenes de prueba. Los 208 SHA únicos y los 203 clusters pHash se informan como análisis secundarios de sensibilidad, sobre los mismos remuestreos por grupo. El entrenamiento operó sobre 935 unidades distintas, no 1.064: un 12 % de redundancia.

Efecto sobre la cifra publicada, con Wilson 95 %:

| denominador | estimación | intervalo | ancho |
|---|---|---|---|
| 219 archivos, como se publica | 0,9087 | [0,863 – 0,940] | 0,077 |
| 208 SHA únicos | 0,9087 | [0,862 – 0,941] | 0,079 |
| **203 clusters pHash** | **0,9064** | **[0,859 – 0,939]** | 0,081 |

La estimación puntual se mueve poco, unas tres décimas, y el intervalo se ensancha ligeramente. El cambio material no es el número: **la unidad de análisis hay que declararla**. TASK-05 informa la cifra principal por imagen y las dos alternativas como sensibilidad; los intervalos remuestrean grupos, no imágenes.

## 3. M1: el criterio del propio artículo no habría bastado

| medida | valor |
|---|---|
| imágenes | 669 |
| SHA256 únicos | 669 (**cero duplicados binarios**) |
| pares con Hamming < 5 | 12 |
| clusters cruzando splits | 6, **todos train ↔ valid** |
| candidatos en banda 5–10 | 42 |
| tamaño máximo de cluster | 2 |

Leído sólo así, no habría contaminación del test. **Pero ese resultado es un artefacto del criterio.**

### 3.1 Las siete familias documentales: la adjudicación refuta lo que yo había sugerido

Las siete bases de nombre que aparecen en dos splits están todas a distancia pHash > 10. En la primera versión de este informe presenté eso como un punto ciego del criterio del artículo. **La adjudicación ciega lo refuta**: ambos revisores, de forma independiente, juzgaron las siete familias como **UNRELATED**, incluida `freshMango-29-`, la que cruzaba test ↔ valid. El nombre base compartido es una coincidencia de numeración, y pHash acertaba al situarlas lejos.

**Retirado:** «el criterio del artículo no habría visto las siete familias». No era un punto ciego.

### 3.1 bis El punto ciego real está en la banda 5–10

El que sí existe está donde la SPEC mandaba mirar: en la banda de sensibilidad. De los 16 pares de la banda 5–10 que cruzan splits, **15 fueron juzgados relacionados por ambos revisores** (sólo discrepan en si es la misma fotografía o el mismo fruto y escena, que para particionar significa lo mismo).

**Seis de ellos cruzan hacia el test**, a distancias 6, 8, 8, 10, 10 y 10, y **los seis** son relacionados para ambos revisores. Cuatro son imágenes que no son del vídeo. Con Hamming < 5, el criterio del artículo, esos seis pares no se habrían detectado. La afirmación, en los términos que la evidencia sostiene, es que con el umbral del artículo seis pares que la adjudicación operativa juzga relacionados habrían quedado repartidos entre entrenamiento y test.

### 3.2 `sakit_mp4` no es un vídeo continuo: es un montaje de fotografías distintas

De 234 grupos conservadores, cuatro cruzan splits. El decisivo:

```
sakit_mp4    train 329    valid 85    test 18    total 432
```

Un único grupo nominal de fotogramas de vídeo abarca **los tres conjuntos**, y son 432 de las 669 imágenes, el 64,6 %. La SPEC manda agrupar conservadoramente cuando el origen no es verificable, y lo es: la fuente del dataset no publica descripción ni procedencia, así que no consta si `sakit_mp4` es un vídeo o varios.

Con esa unidad de independencia, **la partición actual no es atómica por grupo**: el test de 33 imágenes contiene 18 fotogramas del mismo grupo nominal que 329 imágenes de entrenamiento.

Su estado sigue siendo `POSSIBLE_SEQUENCE_RELATION`, no confirmado.

**La adjudicación ciega matiza qué es ese grupo.** Ambos revisores vieron los mismos 16 fotogramas, muestreados sistemáticamente (el 3,7 % de 432) y en orden temporal, y contaron **15 escenas distintas**: suelo con raíces, hojarasca, grava, césped, copa de árbol, papel de periódico en interior. Los dos pares de numeración consecutiva que yo había puesto como controles «positivos», suponiendo que serían el mismo plano, fueron juzgados UNRELATED por ambos. Inspeccionados después, son dos fotografías distintas; una muestra un botón de cámara de móvil, es decir, una captura. No eran controles válidos: la suposición era mía y sin verdad de referencia, así que su fallo no calibra la sensibilidad de los revisores.

Lo que esa evidencia sostiene: `sakit_mp4` es un contenedor heterogéneo, probablemente un montaje de fotografías, y no una grabación continua de una sola escena. No sostiene que sus 432 imágenes sean mayormente independientes. La muestra no estima con qué frecuencia se repiten frutos, escenas o sesiones, y ambos revisores encontraron el mismo fruto en dos fotografías distintas (paneles 7 y 8), una relación que ningún hash detecta.

Consecuencia: se mantiene la regla congelada de la SPEC §5, que agrupa el contenedor entero. Una enmienda que lo dividía por identidad visual (PROTOCOL-AMENDMENT-009) se retiró tras revisión independiente (DECISION-032).

## 4. Veredicto

| decisión | estado |
|---|---|
| M1 requiere repartición (TASK-03) | **SÍ**, con el montaje como un único grupo (regla congelada). Adjudicación hecha: 5 pares cercanos train↔valid y 6 pares relacionados de la banda 5–10 que cruzan al test. Congelación pendiente de §4 ter |
| M1 requiere reentrenamiento (TASK-04) | **SÍ**, si la repartición cambia la membresía |
| M2 requiere reentrenamiento | **NO**. Su partición limpia está verificada sin cruces; los duplicados intra-split no lo autorizan |
| M2 métricas reutilizables | Sí, con el n efectivo declarado y la sensibilidad de TASK-05 |

El motivo de la repartición de M1 **no** es el número de pares pHash, que es pequeño. Es que la unidad de independencia defendible para este corpus es el grupo de adquisición, y bajo esa unidad el test no es independiente.

## 4 bis. Adjudicación visual ciega A/B

Dos revisores independientes, instancias de agente de familias de modelo distintas, con carpetas, ids y orden de preguntas propios, sin acceso a split, clase, nombre de archivo ni métricas. 35 candidatos más 5 controles indistinguibles.

| categoría | resultado |
|---|---|
| 6 pares cruzados bajo umbral | 5 acuerdo NEAR_DUPLICATE, 1 desacuerdo de subtipo |
| 16 pares cruzados de banda 5–10 | 15 relacionados para ambos (13 difieren sólo en el subtipo), 1 acuerdo UNRELATED |
| 7 familias documentales | **7 acuerdo UNRELATED** |
| secuencia `sakit_mp4` | ambos: 15 escenas distintas en 16 paneles |
| 3 controles negativos | 3/3 correctos para ambos |
| 2 controles «positivos» | 0/2 para ambos; **el control era erróneo**, ver §3.2 |

Los 14 desacuerdos son todos del mismo tipo: A dice `POSSIBLE_SEQUENCE_RELATION`, B dice `NEAR_DUPLICATE`. **Ambos juzgan el par relacionado**; sólo discrepan en si es la misma foto o el mismo fruto. Para particionar, las dos etiquetas obligan a lo mismo: agrupar. Una tercera pasada independiente (revisor C, otra familia de modelo, paquete propio, sin ver A ni B) resolvió los 14: 11 misma fotografía, 3 mismo fruto y escena, **cero disidencias sobre si el par está relacionado**.

El acuerdo entre agentes es evidencia operativa para decidir el agrupamiento. **No es una etiqueta biológica ni ground truth** (SPEC §5). Excepciones de cegamiento, calibración y hashes de los paquetes en `data/audits/model1/blinding_log.json`.

## 4 ter. Adjudicación suplementaria de 47 candidatos (DECISION-034)

Dos generadores adicionales dejaron 47 pares en `PENDING_ADJUDICATION`: 7 por pHash invariante a rotación (distancia ≤ 10) y 40 por similitud de embedding ImageNet (ART-004), con el horizonte de 40 fijado antes de ver resultados. Se adjudican todos, crucen o no la partición, bajo el mismo contrato de §5, con 6 controles de consistencia contra decisiones ya adjudicadas. **Resultado.** Dos pasadas ciegas y tercera adjudicación separada de los 38 desacuerdos. De los 47 pares, 37 quedan relacionados (26 `POSSIBLE_SEQUENCE_RELATION` y 11 `NEAR_DUPLICATE`) y 10 no relacionados; ninguno queda pendiente. `supplementary_relations.csv` lleva además la relación previa SRC-010049–SRC-010072 de `extra_relations.csv`, de ahí sus 48 filas. Los controles salieron 6/6 para ambos revisores. Los 110 archivos de los paquetes ciegos (láminas, preguntas y respuestas) se conservan en `data/audits/model1/supplementary_packets/`, comprobados contra `packet_sha256` de `supplementary_blinding_log.json`.

Límite: los pares por debajo de esos horizontes no se revisan. El par conocido de mismo fruto en dos fotografías ocupaba el puesto 765 del ranking de embedding, así que no se puede afirmar recall para esa relación. Con la regla congelada, las relaciones dentro del montaje no afectan a la partición; las que unen imágenes de fuera del montaje sí, y siguen siendo riesgo residual declarado.

## 5. Límites declarados

- Cero pares detectados **no** probaría independencia biológica. Aquí se detectaron pares, así que la cuestión es cuántos y de qué tipo, pero el límite se mantiene para las 645 imágenes en clusters de tamaño 1.
- Un recuento de clusters **no** es un recuento de unidades independientes. La interpretación se publica dentro de `duplicate_structure.json` para que no pueda leerse sin ella.
- La banda 5–10 se inspecciona para estudiar el fallo del criterio. **No se convierte automáticamente en equivalencia** y no se ha usado para seleccionar nada.
- El agrupamiento conservador de `sakit_mp4` puede ser demasiado grueso si en realidad son varios vídeos. Esa posibilidad no se resuelve dividiéndolo para mejorar los números: si el grupo impide un test informativo, se registra bloqueo por unidades insuficientes.

## 6. Artefactos

`data/audits/model1/`, `data/audits/model2_original/`, `data/audits/model2/`, cada uno con `candidate_pairs.csv`, `clusters.csv`, `cross_split_summary.csv`, `duplicate_structure.json`, `cluster_size_distribution.csv` y `audit_parameters.json` con versiones, parámetros, hash del manifiesto y límites.

RED en `provenance/commands/task02/red.log`, GREEN en `green.log`, 36 tests de método.

## 7. Estado de cierre de TASK-02

| punto | estado |
|---|---|
| Adjudicación A/B de los 6 clusters cruzados, las 7 familias documentales y los 16 pares cruzados de la banda 5–10 | **Completa**, con tercera pasada (§4 bis) |
| Membresía DATA-004 ↔ DATA-005 y alias `valid` → `val` | **Completa**: 1.500/1.500 (`data/audits/model2/membership_clean_vs_cls.json`); congelada en `data/manifests/model2_frozen_manifest.csv` |
| `data.yaml` del dataset limpio apunta al contaminado | Detectado; consecuencia: el YAML histórico no sirve como procedencia del run M2 |
| Origen de `sakit_mp4` y `freshMango` | La fuente no lo publica; se registra como bloqueo documental y se aplica la regla conservadora |
| Adjudicación suplementaria de 47 candidatos | **En curso** (§4 ter) |
