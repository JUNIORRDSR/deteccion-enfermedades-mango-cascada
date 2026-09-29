"""TASK-09: close docs/response_to_reviewers.md against the manuscript after pass 2d (audit B, B-05, B-10
and B-12). The header stops calling the letter a draft; REVIEW-03 states the retrospective status of
the test; REVIEW-05 uses decimal commas and adds the macro-F1 changes; REVIEW-10 and REVIEW-15 get
their final locations (reports/execution/render_review.md). Numbers come from the artifacts, and
each replacement must be found exactly once in its section (revise_letter.apply).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from results_tables import es  # noqa: E402
from revise_letter import LETTER, ROOT, SENSITIVITY, apply  # noqa: E402

sys.path.insert(0, str(ROOT))
from src.statistics.intervals import wilson  # noqa: E402

WILSON = wilson(11, 13)  # the published 11 of 13 Enfermo instances that REVIEW-04 and REVIEW-05 quote


def edits() -> dict[str, list[tuple[str, str]]]:
    deltas = json.loads((ROOT / SENSITIVITY).read_text(encoding='utf-8'))['deltas']
    pp = {(s, m): es(abs(deltas[s][m]['percentage_points']), 2)
          for s in ('exact_sha_dedup', 'cluster_weighted') for m in ('accuracy', 'macro_f1')}
    return {
        '# Respuesta al dictamen': [
            ('**Estado del documento: BORRADOR.** Las cifras marcadas `[PENDIENTE: …]` salen de '
             'artefactos que todavía no existen y se completarán desde ellos, sin copiarlas a mano.',
             '**Estado del documento.** Las cifras de resultados se escriben desde los artefactos '
             'congelados con `provenance/commands/task09/revise_letter.py` y '
             '`revise_letter_final.py`, sin copiarlas a mano, y las ubicaciones remiten al manuscrito '
             'tras la pasada 2d (`reports/execution/render_review.md`).')],
        '## REVIEW-03': [
            ('El test se evaluó una sola vez, después de fijar ambos.',
             'La prueba se evaluó una sola vez, después de fijar ambos. Es una evaluación interna '
             'retrospectiva, no una prueba prospectiva: sus imágenes eran públicas y parte de ellas '
             'estaba en el entrenamiento histórico.')],
        '## REVIEW-05': [
            (f"baja la exactitud {pp['exact_sha_dedup', 'accuracy']} puntos porcentuales y la "
             f"ponderación por cluster {pp['cluster_weighted', 'accuracy']} "
             '(`reports/model2_duplicate_sensitivity.md`).',
             f"baja la exactitud {pp['exact_sha_dedup', 'accuracy']} puntos porcentuales y el "
             f"macro-F1 {pp['exact_sha_dedup', 'macro_f1']}, y la ponderación por cluster "
             f"{pp['cluster_weighted', 'accuracy']} y {pp['cluster_weighted', 'macro_f1']}. La Sección "
             '4.2.3 del manuscrito da las tres estimaciones con sus intervalos '
             '(`reports/model2_duplicate_sensitivity.md`).'),
            ('[0.578, 0.957]', f'[{es(WILSON[0])}; {es(WILSON[1])}]')],
        '## REVIEW-10': [
            ('**Estado.** RESUELTO en el texto `[PENDIENTE: ubicación]`.',
             '**Estado.** RESUELTO en el texto: título, resumen, Sección 1 (cuarto párrafo, sin la '
             'premisa de que la inspección visual es tardía), 5.4, 6.2 y Sección 7. Esa premisa la '
             'retiró una revisión semántica posterior a la búsqueda por palabras '
             '(`reports/editorial_audit.md`).')],
        '## REVIEW-14 y REVIEW-15': [
            ('aparecen una sola vez, en la Sección 3.1,', 'aparecen una sola vez, en la Sección 3.2.2,'),
            (' `[PENDIENTE: secciones de resultados y revisión sobre el render final]`.',
             '. Las secciones de resultados siguen la misma terminología, con los nombres de las '
             'patologías en minúscula tras la primera palabra, y la coma decimal en texto, tablas y '
             'figuras; la Figura 3 se regeneró con coma decimal. El render final se revisó página a '
             'página (`reports/execution/render_review.md`).'),
            ('**Estado.** `[PENDIENTE]`', '**Estado.** RESUELTO.')],
    }


def main() -> int:
    raw = LETTER.read_bytes()
    newline = '\r\n' if b'\r\n' in raw else '\n'
    text = apply(raw.decode('utf-8').replace('\r\n', '\n'), edits())
    if '[PENDIENTE' in text:
        raise SystemExit('a placeholder is left in the letter')
    LETTER.write_bytes(text.replace('\n', newline).encode('utf-8'))
    print('letter closed: no placeholder left')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
