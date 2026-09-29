"""Correct the TASK-02 audit report with the blind A/B adjudication outcome."""

from pathlib import Path

REPORT = Path('reports/execution/task-02-audit-report.md')

OLD_31 = """### 3.1 Las siete familias documentales son invisibles a pHash

Las siete bases de nombre que aparecen en dos splits están **todas a distancia > 10**: ni siquiera entran como candidatas. Incluida `freshMango-29-`, que cruza **test ↔ valid**.

Si la auditoría se hubiera hecho sólo con Hamming < 5, las siete habrían pasado sin ser vistas. Es la justificación empírica, sobre este corpus, de la regla de la SPEC de que **la procedencia documental tiene prioridad sobre la semejanza visual**.

Qué significa una distancia > 10 con el mismo nombre base: o son fotos distintas del mismo fruto o escena, y entonces hay parentesco, o la coincidencia del esquema de numeración no significa nada. **No se decide desde metadatos.** Van a adjudicación visual ciega A/B como candidatos obligatorios."""

NEW_31 = """### 3.1 Las siete familias documentales: la adjudicación refuta lo que yo había sugerido

Las siete bases de nombre que aparecen en dos splits están todas a distancia pHash > 10. En la primera versión de este informe presenté eso como un punto ciego del criterio del artículo. **La adjudicación ciega lo refuta**: ambos revisores, de forma independiente, juzgaron las siete familias como **UNRELATED**, incluida `freshMango-29-`, la que cruzaba test ↔ valid. El nombre base compartido es una coincidencia de numeración, y pHash acertaba al situarlas lejos.

**Retirado:** «el criterio del artículo no habría visto las siete familias». No era un punto ciego.

### 3.1 bis El punto ciego real está en la banda 5–10

El que sí existe está donde la SPEC mandaba mirar: en la banda de sensibilidad. De los 16 pares de la banda 5–10 que cruzan splits, **15 fueron juzgados relacionados por ambos revisores** (sólo discrepan en si es la misma fotografía o el mismo fruto y escena, que para particionar significa lo mismo).

**Seis de ellos cruzan hacia el test**, a distancias 6, 8, 8, 10, 10 y 10, y **los seis** son relacionados para ambos revisores. Cuatro son imágenes que no son del vídeo. Con Hamming < 5, el criterio del artículo, esos seis pares no se habrían detectado. Ésa es la versión correcta y adjudicada de la afirmación: **el umbral del artículo deja pasar contaminación real del test en la banda 5–10**."""

OLD_32_HEAD = "### 3.2 Bajo agrupamiento conservador, el test sí queda alcanzado"
NEW_32_HEAD = "### 3.2 `sakit_mp4` no es un vídeo continuo: es un montaje de fotografías distintas"

OLD_32_TAIL = """Su estado sigue siendo `POSSIBLE_SEQUENCE_RELATION`, no confirmado. La SPEC lo prevé: sin fuente verificable se agrupa conservadoramente para particionar, pero la relación no se promueve a confirmada."""

NEW_32_TAIL = """Su estado sigue siendo `POSSIBLE_SEQUENCE_RELATION`, no confirmado.

**Pero la adjudicación ciega cambia qué significa ese grupo.** Ambos revisores, sobre 16 fotogramas muestreados en orden temporal, contaron **15 escenas distintas**: suelo con raíces, hojarasca, grava, césped, copa de árbol, papel de periódico en interior. Y los dos controles «positivos», que yo había construido con fotogramas de numeración consecutiva suponiendo que serían el mismo plano, fueron juzgados UNRELATED por ambos. Inspeccionados después, **los revisores tenían razón**: `sakit_mp4-0075` y `-0076` son dos fotografías distintas, una de ellas con un botón de cámara de móvil visible, es decir, una captura. El control estaba mal diseñado por mí, no los revisores mal calibrados.

Conclusión con evidencia: `sakit_mp4` es un **montaje de fotografías distintas** empaquetado como vídeo, no una grabación continua de una escena. Algunas fotografías aparecen en varios fotogramas extraídos, y ésas sí son duplicados reales (las parejas a Hamming 0 cruzando train/valid son de este tipo). Pero dos fotogramas del «mismo vídeo» no son, en general, el mismo fruto.

Esto tiene una consecuencia directa: la regla de la SPEC que agrupa **todos** los fotogramas nominales de un vídeo en un solo grupo se escribió pensando en una adquisición continua. Aplicada a un montaje, es **sobre-conservadora**: mete 432 fotografías mayormente independientes en un único grupo atómico. Cambiarla es una decisión de protocolo, no mía; ver §4."""

OLD_4 = """| M1 requiere repartición (TASK-03) | **SÍ**, condicionado a la adjudicación visual |"""
NEW_4 = """| M1 requiere repartición (TASK-03) | **SÍ**. Adjudicación hecha: 5 pares cercanos train↔valid confirmados y 6 pares relacionados de la banda 5–10 que cruzan al test |"""

CALIBRATION = """

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

Los 14 desacuerdos son todos del mismo tipo: A dice `POSSIBLE_SEQUENCE_RELATION`, B dice `NEAR_DUPLICATE`. **Ambos juzgan el par relacionado**; sólo discrepan en si es la misma foto o el mismo fruto. Para particionar, las dos etiquetas obligan a lo mismo: agrupar. El subtipo queda `PENDING_SEPARATE_ADJUDICATION` para una tercera pasada independiente, como exige la SPEC.

El acuerdo entre agentes es evidencia operativa para decidir el agrupamiento. **No es una etiqueta biológica ni ground truth** (SPEC §5). Excepciones de cegamiento, calibración y hashes de los paquetes en `data/audits/model1/blinding_log.json`."""


def main() -> int:
    s = REPORT.read_text(encoding='utf-8')
    for old, new in ((OLD_31, NEW_31), (OLD_32_HEAD, NEW_32_HEAD), (OLD_32_TAIL, NEW_32_TAIL),
                     (OLD_4, NEW_4)):
        if s.count(old) != 1:
            raise SystemExit(f'anchor not found once: {old[:60]!r}')
        s = s.replace(old, new)
    s = s.replace('## 5. Límites declarados', CALIBRATION.strip() + '\n\n## 5. Límites declarados')
    s = s.replace('**Estado:** resultados algorítmicos completos; **adjudicación visual A/B pendiente**.',
                  '**Estado:** resultados algorítmicos y adjudicación visual A/B completos; subtipo de 14 pares pendiente de tercera pasada.')
    REPORT.write_text(s, encoding='utf-8')
    print('audit report corrected')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
