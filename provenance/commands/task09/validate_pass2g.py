"""Checks of the pass 2g cleanup (reports/final_text_cleanup_report.md): every number of the manuscript
is unchanged from the pass 2f candidate, no current document still says the visual review had no human
review, and each real limitation is still stated. Prints JSON; exit 1 when a check fails.

Usage: python provenance/commands/task09/validate_pass2g.py <pass-2f commit>
"""

import io
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import docx

ROOT = Path(__file__).resolve().parents[3]
DOCX = 'manuscript/source/Articulo_Mango_ALBUS_revision.docx'
NUMBER = re.compile(r'-?\d+(?:,\d+)?')
SECTION = re.compile(r'Secci[oó]n(?:es)? \d+(?:\.\d+)*(?: y \d+(?:\.\d+)*)?')  # references, not results
CURRENT_DOCS = ['README.md', 'docs/response_to_reviewers.md', 'docs/final_validation_report.md',
                'reports/execution/STATE.md', 'reports/editorial_audit.md', 'reports/protocol_compliance.json',
                'reports/execution/render_review.md']
STALE = ['sin revisión humana', 'ninguna de estas decisiones la revisó', 'ninguna decisión la revisó',
         'revisó una persona', 're-adjudicación por personas', 'Estado.** RESUELTO PARCIALMENTE',
         'human re-adjudication is open', 'la re-adjudicación humana queda como trabajo futuro']
LIMITATIONS = {
    'M1 sensibilidad Enfermo en prueba': 'sensibilidad del detector para Enfermo en prueba (0,577 [0,273; 0,735])',
    'M1 un solo origen Enfermo en entrenamiento': 'proceden de un único grupo de origen',
    'pruebas retrospectivas': 'evaluaciones internas retrospectivas',
    'sin verdad de terreno conjunta': 'No hay verdad de terreno conjunta',
    'sin validación en campo': 'el sistema no se validó en cultivos de la región',
    'cambio de dominio del clasificador': 'el efecto de ese cambio de dominio no se ha medido',
    'umbral 0,4 sin validar': 'no se calibró ni se validó',
    'intervalos condicionales': 'Son intervalos condicionales',
    'fuga no descartada': 'No se afirma que el conjunto esté libre de fuga',
    'adjudicación asistida por IA': 'La primera adjudicación se hizo con apoyo de agentes de IA',
    'fiabilidad limitada de los agentes': 'Los agentes mostraron una fiabilidad limitada',
    'revisión manual posterior': 'una integrante del equipo revisó manualmente los candidatos',
    'grupos de la adjudicación registrada': 'Los grupos de la partición proceden de las decisiones registradas',
    'etiquetas de terceros sin confirmación': 'no la validez fitopatológica del diagnóstico',
    'cluster con dos etiquetas en M2': 'se conservaron las dos etiquetas sin adjudicarlas',
    'duplicados en entrenamiento y validación de M2': '986 SHA-256 distintos en 1064 imágenes',
    'dos evaluadores de validación': 'Este trabajo no aisló la contribución de cada diferencia',
    'latencia sin escenas densas': 'la medición no cubre escenas con muchos frutos',
    'Raspberry Pi no medida': 'la latencia en Raspberry Pi 4 no se midió',
    'sin prueba externa': 'carece de un conjunto de prueba out-of-distribution externo',
}


def text_of(document) -> str:
    parts = [p.text for p in document.paragraphs]
    parts += [cell.text for table in document.tables for row in table.rows for cell in row.cells]
    return '\n'.join(parts)


def main() -> int:
    base = sys.argv[1]
    old = text_of(docx.Document(io.BytesIO(subprocess.run(
        ['git', 'show', f'{base}:{DOCX}'], cwd=ROOT, capture_output=True, check=True).stdout)))
    new = text_of(docx.Document(ROOT / DOCX))
    old_numbers = Counter(NUMBER.findall(SECTION.sub('', old)))
    new_numbers = Counter(NUMBER.findall(SECTION.sub('', new)))
    stale = {rel: [s for s in STALE if s.lower() in (ROOT / rel).read_text(encoding='utf-8').lower()]
             for rel in CURRENT_DOCS}
    stale['manuscript'] = [s for s in STALE if s.lower() in new.lower()]
    report = {
        'numbers_unchanged': old_numbers == new_numbers,
        'numbers_only_before': dict(old_numbers - new_numbers),
        'numbers_only_after': dict(new_numbers - old_numbers),
        'stale_ai_human_wording': {k: v for k, v in stale.items() if v},
        'limitations_missing': [k for k, v in LIMITATIONS.items() if v not in new],
        'limitations_checked': len(LIMITATIONS),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if (report['numbers_unchanged'] and not report['stale_ai_human_wording']
                 and not report['limitations_missing']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
