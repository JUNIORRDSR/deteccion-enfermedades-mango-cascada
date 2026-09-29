# PROTOCOL-AMENDMENT-009 — Unidad de agrupamiento del montaje `sakit_mp4`

| campo | valor |
|---|---|
| `amendment_id` | PROTOCOL-AMENDMENT-009 |
| `version` | 1 |
| `base_protocol` | ALBUS26-116-PROTOCOL-001, commit `7d0f9985cce73740cfa2ae26154971b55282ad52`, JSON SHA256 `6d5aa3ff…c8b` |
| `modifica` | SPEC §5, regla «sin fuente verificable, todos los frames nominales de un mismo video se agrupan conservadoramente» |
| `user_decision` | DECISION-031, opción B elegida por el usuario tras recibir las dos opciones con sus consecuencias |
| `test_observed_before_freeze` | true (heredado) |
| `new_test_access` | ninguno: no hay predicciones nuevas sobre ningún test |
| `state` | **WITHDRAWN** el 2026-09-23 (§7); la partición primaria vuelve a la regla congelada |
| `execution_permitted` | false hasta cerrar ambas |

## 1. Qué cambia

La regla congelada agrupa en **un único grupo atómico** todos los fotogramas nominales de un vídeo cuando su origen no es verificable. Esta enmienda la sustituye, **sólo para `sakit_mp4`**, por agrupamiento por identidad visual: se fusionan las imágenes que son la misma fotografía o el mismo fruto, y no las que sólo comparten contenedor.

El registro de adjudicación del montaje completo como `POSSIBLE_SEQUENCE_RELATION` **se conserva como evidencia y no se usa como arista de agrupamiento**.

## 2. Por qué: evidencia, no tamaño de test

La regla se escribió suponiendo que un vídeo es una adquisición continua de una escena. La adjudicación ciega mostró que `sakit_mp4` no lo es:

- Dos revisores independientes, de familias de modelo distintas y sin acceso mutuo, contaron **15 escenas distintas en 16 paneles** muestreados en orden temporal.
- Los dos pares de fotogramas con numeración consecutiva, construidos como control positivo, fueron **UNRELATED para ambos**; inspeccionados después, son fotografías distintas, una con el botón de cámara de un móvil visible.
- Los 432 fotogramas siguen una numeración contigua, que es la convención de Roboflow al extraer fotogramas de un vídeo subido. El contenedor es un vídeo; el contenido es un **montaje de fotografías**.

Agrupar 432 fotografías mayormente independientes como una sola unidad no refleja la dependencia real, sino el formato del archivo.

## 3. Declaración obligatoria de conocimiento previo

**El coordinador conocía el tamaño del test de la opción A antes de proponer B.** La proyección con la regla congelada (test con 9 imágenes enfermas de 9 grupos) se calculó antes de que la adjudicación revelara que el vídeo es un montaje. Ese conocimiento puede sesgar hacia B. Por eso:

- B se justifica únicamente por la evidencia de §2, que es independiente de cualquier tamaño de test.
- La decisión la tomó el usuario, no el coordinador, con ambas opciones y sus consecuencias por escrito.
- No se ha visto ninguna predicción ni métrica sobre ningún test de ninguna de las dos particiones.
- B no se elige por rendimiento: el algoritmo de asignación sigue siendo el único congelado de la SPEC §6, sin barrido de semillas.

## 4. Riesgo que introduce B y cómo se controla

B separa fotografías que la regla A mantenía juntas. Si dos de ellas muestran **el mismo fruto** y acaban en splits distintos, hay fuga. Los hashes no bastan:

| mecanismo | qué detecta | evidencia |
|---|---|---|
| SHA256 | el mismo archivo | 0 duplicados binarios en M1 |
| pHash < 5 | la misma foto, recodificada | 12 pares |
| pHash banda 5–10, adjudicada | la misma foto con más cambios | 15 de 16 pares cruzados, relacionados |
| hash invariante a rotación y reflexión | la misma foto girada o espejada | 7 candidatos nuevos |
| **nada de lo anterior** | **otra fotografía del mismo fruto** | paneles 7 y 8: pHash 30, invariante 26, **mismo mango para ambos revisores** |

Para la última fila, que ningún hash cubre, se aplica una **comprobación residual ciega preregistrada**:

- Cada imagen del test de B se muestra con sus **5 vecinos más cercanos fuera del test**, según un embedding genérico de ImageNet (ART-004, verificado por hash, nunca entrenado con estas imágenes). El embedding sólo propone; decide la revisión visual.
- k = 5 porque el único positivo conocido fue el 5.º vecino de su propia imagen en la calibración; en el ranking global quedaba en el puesto 765, así que una ventana global habría fallado.
- **Regla fijada antes de ver respuestas:** un vecino marcado como el mismo fruto por **al menos uno** de los dos revisores se fusiona con el grupo de la consulta y se recalcula la partición una sola vez. La regla favorece separar y no puede inflar resultados.
- Controles: 2 positivos construidos con el par conocido de los paneles 7 y 8, y 2 negativos.

## 5. Límite residual que queda declarado

- Una relación «mismo fruto» entre una imagen de test y una de train que **no** esté entre los 5 vecinos más cercanos no se revisa.
- Las relaciones entre train y valid no se comprueban con este procedimiento; afectan a la selección de checkpoint, no a la evaluación final, y se declaran.
- El acuerdo entre agentes es evidencia operativa, no ground truth biológico.

## 6. Criterio de aprobación

`APPROVED` sólo cuando: (a) la comprobación residual esté completa y aplicada; (b) los controles positivos se detecten, porque si no se detectan la comprobación no demuestra nada; y (c) una revisión independiente fresca no deje HIGH ni MEDIUM abiertos.

## 7. Retirada — 2026-09-23

La primera revisión independiente (`reports/amendments/amendment-009-independent-review.md`) concluyó que la enmienda no es aprobable con ningún resultado de la comprobación residual: 5 HIGH y 4 MEDIUM. Se verificó lo esencial antes de aceptarla:

- La SPEC §5 congelada ya prevé este caso: «Si ese grupo impide un test informativo, registrar bloqueo por unidades insuficientes; no dividirlo para mejorar números». La opción B hace exactamente lo que esa frase prohíbe.
- 43 de los 48 grupos de test con Enfermo de B proceden del montaje en disputa (recalculado). La ganancia de B la produce la regla discutida.
- La cifra «9 imágenes enfermas de 9 grupos» de §3 no es reproducible con los artefactos finales: con la regla congelada salen 114 imágenes de test y 10 grupos con Enfermo. Procedía de un estado intermedio de relaciones que no se conservó. Queda retirada.
- La regla residual de «al menos un revisor» contradice la tercera adjudicación obligatoria de §5, y sus controles no calibran nada.

Consecuencias: la partición primaria de M1 aplica la regla congelada (opción A); la comprobación residual queda **SUPERSEDED**, incompleta (revisor A 107/107, revisor B 83/107) y **nunca aplicada**; ningún resultado suyo entra en la partición. El borrador B se conserva como artefacto, sin ejecución prevista. Registro: DECISION-032.
