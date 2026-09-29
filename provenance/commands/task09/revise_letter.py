"""TASK-09: fill the result markers of docs/response_to_reviewers.md from the frozen artifacts.

Every number comes from the same facts() and values() that pass 2c prints in the manuscript;
none is typed here. Each marker is replaced inside its own REVIEW section and must be found
exactly once there, so a rerun or an edited letter stops instead of writing twice. REVIEW-10 and
REVIEW-15 wait for the review of the final render.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import revise_pass2c  # noqa: E402
from results_tables import es  # noqa: E402

LETTER = ROOT / 'docs/response_to_reviewers.md'
SENSITIVITY = 'artifacts/metrics/model2_sensitivity.json'


def edits(f: dict) -> dict[str, list[tuple[str, str]]]:
    v = revise_pass2c.values(f)
    deltas = json.loads((ROOT / SENSITIVITY).read_text(encoding='utf-8'))['deltas']
    pp = {scheme: es(abs(d['accuracy']['percentage_points']), 2) for scheme, d in deltas.items()}
    return {
        '## REVIEW-03': [
            ('`[PENDIENTE: resultados de EXP-V01 y EXP-R02]`',
             f"En validación (EXP-V01, {f['val']['counts']['images']} imágenes) el mAP@0,5 es "
             f"{v['map50_val']}, y el umbral fijado es {v['t']}, con F2 de Enfermo "
             f"{es(f['threshold_f2'])}. La prueba (EXP-R02, {v['n_test']} imágenes en "
             f"{v['groups_test']} grupos) se evaluó una sola vez: el mAP@0,5 es {v['map50_test']} y "
             f"la sensibilidad para Enfermo {v['recall_Enfermo_test']}, frente a "
             f"{v['recall_Enfermo_val']} en validación. Es un resultado peor que el publicado, y el "
             'manuscrito lo presenta como la principal limitación del detector (Secciones 4.1.2, '
             '5.1 y 6.1).'),
            ('Es un entrenamiento nuevo, no una reproducción del histórico.',
             'Es un entrenamiento nuevo, no una reproducción del histórico. La inferencia de '
             'validación y la de prueba también se ejecutaron en Kaggle, sobre el mismo checkpoint '
             'verificado por hash. El primer intento de validación se detuvo antes de leer datos '
             'porque la plataforma no montó el checkpoint, y se repitió según la política de '
             'reintentos congelada (DECISION-038 y DECISION-039).'),
            ('**Estado.** `[PENDIENTE]`', '**Estado.** RESUELTO.')],
        '## REVIEW-05': [
            ('más de un 5 % de remuestras indefinidas `[PENDIENTE]`.',
             'más de un 5 % de remuestras indefinidas. Ningún intervalo del Modelo 1 quedó '
             'bloqueado; el de la sensibilidad para Enfermo, '
             f"{v['recall_Enfermo_test']}, es ancho porque esa clase aparece solo en "
             f"{v['groups_E_test']} de los {v['groups_test']} grupos de la prueba."),
            ('ponderación por cluster `[PENDIENTE: EXP-R03]`.',
             f"ponderación por cluster. La exactitud es {v['m2_acc']} y el macro-F1 "
             f"{v['m2_macro_f1']}; la deduplicación por SHA-256 baja la exactitud "
             f"{pp['exact_sha_dedup']} puntos porcentuales y la ponderación por cluster "
             f"{pp['cluster_weighted']} (`reports/model2_duplicate_sensitivity.md`)."),
            ('**Estado.** `[PENDIENTE]`', '**Estado.** RESUELTO.')],
        '## REVIEW-07': [
            (' `[PENDIENTE: TASK-06]`:', ':'),
            ('- Entrada de 640 px, batch 1, FP32 y un hilo.',
             '- Modelo 1 a 640 px y Modelo 2 a 224 px, batch 1, FP32, un proceso y un hilo.'),
            ('- Se informan media, mediana, desviación, p95, mínimo y máximo, por etapa y de '
             'extremo a extremo.',
             '- Se informan media, mediana, desviación, p95, mínimo y máximo, por etapa y de '
             'extremo a extremo.\n\n'
             f"Sobre {f['benchmark']['n']} repeticiones medidas, la mediana de extremo a extremo, "
             f"de la lectura del archivo a la imagen anotada, es {v['lat_e2e']} ms (p95 "
             f"{v['lat_e2e_p95']} ms); la llamada al Modelo 1 toma {v['lat_m1']} ms y la cascada "
             f"{v['lat_cascade']} ms (`reports/benchmark_report.md`)."),
            ('**Estado.** `[PENDIENTE]`',
             '**Estado.** RESUELTO en CPU; la Raspberry Pi 4 sigue bloqueada (REVIEW-08).')],
    }


def apply(text: str, plan: dict[str, list[tuple[str, str]]]) -> str:
    for heading, replacements in plan.items():
        start = text.index(heading)
        end = text.find('\n## ', start + len(heading))
        end = len(text) if end < 0 else end
        section = text[start:end]
        for old, new in replacements:
            if section.count(old) != 1:
                raise SystemExit(f'{heading}: expected one {old!r}, found {section.count(old)}')
            section = section.replace(old, new)
        text = text[:start] + section + text[end:]
    return text


def main() -> int:
    raw = LETTER.read_bytes()
    newline = '\r\n' if b'\r\n' in raw else '\n'
    text = raw.decode('utf-8').replace('\r\n', '\n')
    text = apply(text, edits(revise_pass2c.facts()))
    LETTER.write_bytes(text.replace('\n', newline).encode('utf-8'))
    print('filled REVIEW-03, REVIEW-05 and REVIEW-07')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
