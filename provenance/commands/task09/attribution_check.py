"""Write reports/ai_human_attribution_check.md: every final occurrence of the AI/human attribution terms
in the manuscript and the current documents, with file, section, sentence and justification; historical
records are listed by file and count, since they are kept as they happened (DECISION-040)."""

import csv
import re
import subprocess
from pathlib import Path

import docx

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'reports/ai_human_attribution_check.md'
TERMS = re.compile(r'\bIA\b|inteligencia artificial|Claude|\bagentes?\b|\bhuman[oa]s?\b|revisi[oó]n manual|'
                   r'manualmente|revisi[oó]n visual|adjudica\w*|\bAI\b|\bhuman\b', re.IGNORECASE)
CURRENT = ['docs/response_to_reviewers.md', 'README.md', 'docs/final_validation_report.md',
           'reports/execution/STATE.md', 'reports/editorial_audit.md', 'reports/execution/render_review.md',
           'reports/protocol_compliance.json', 'docs/research/claim_evidence_matrix.csv',
           'reports/editorial_claim_audit.csv']
HISTORICAL = ['data/audits/model1/', 'reports/execution/task-02-audit-report.md', 'reports/final_adversarial_review.md',
              'reports/execution/task-09-results-audit.md', 'reports/execution/task-09-results-audit-round2.md',
              'reports/amendments/', 'docs/research/decision_log.md', 'manuscript/source/edit_log.json',
              'provenance/commands/task09/revise_pass2f.py', 'provenance/commands/task02/', 'docs/superpowers/']
RULES = [  # first match wins
    (r'integrante del equipo|manualmente|team member|manual review|revisión manual|caso a caso|case-by-case',
     'Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así '
     'que no se le atribuyen resultados ni protocolo.'),
    (r'^#+ Uso de IA$', 'Título de la sección del README que declara el uso de IA.'),
    (r'revisión metodológica', 'Revisión metodológica hecha por un modelo de IA distinto del que ejecutó el '
     'trabajo, y así se declara.'),
    (r'Claude|agentes? de IA|agentes|reviewer-[abc]|not human reviewers|AI-assisted',
     'Uso real de IA en la adjudicación inicial: `data/audits/model1/blinding_log.json` y '
     '`supplementary_blinding_log.json` nombran a los agentes.'),
    (r'inspección visual humana', 'Diagnóstico convencional por personas; no se refiere a esta auditoría.'),
    (r'asistentes de IA', 'Declaración general del uso de asistentes de IA en la ejecución de la revisión.'),
    (r'modelos de IA|revisiones? independientes?',
     'Las revisiones independientes de la rama las hicieron modelos de IA, y así se declara.'),
    (r'revisión visual', 'Nombra el criterio de la auditoría; su autoría está en la misma frase o en la siguiente.'),
    (r'adjudica', 'Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01.'),
    (r'humana|human', 'Se refiere a una revisión humana todavía pendiente (re-adjudicación externa), no a la ya hecha.'),
]


def justify(sentence: str, section: str = '') -> str:
    if section == 'ED-21':
        return 'Registro de la decisión de la pasada 2f; ED-25 la sustituye y se conserva como historia.'
    if section == 'ED-25' and 'revisó una persona' in sentence:
        return 'Cita el texto antiguo que la decisión ED-25 sustituye.'
    for pattern, text in RULES:
        if re.search(pattern, sentence, re.IGNORECASE):
            return text
    return 'REVISAR'


def sentences(text: str):
    for s in re.split(r'(?<=[.;:])\s+', text):
        if TERMS.search(s):
            yield s.strip()


def docx_rows():
    document = docx.Document(ROOT / 'manuscript/source/Articulo_Mango_ALBUS_revision.docx')
    section = 'Título'
    for p in document.paragraphs:
        if 'heading' in p.style.name.lower() and p.text.strip():
            section = p.text.replace('\t', ' ').strip()
        elif p.style.name.startswith('ALBUS_1.7'):
            section = 'Resumen'
        for s in sentences(p.text):
            yield 'manuscrito (DOCX)', section, s
    for ti, table in enumerate(document.tables, start=1):
        for row in table.rows:
            for s in sentences(' | '.join(c.text for c in row.cells)):
                yield 'manuscrito (DOCX)', f'Tabla {ti}', s


def text_rows(rel):
    section = '—'
    path = ROOT / rel
    if rel.endswith('.csv'):
        for row in csv.DictReader(open(path, encoding='utf-8')):
            key = row.get('claim_id', '')
            for s in sentences(' '.join(v for v in row.values() if v)):
                yield rel, key, s
        return
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('#'):
            section = line.lstrip('# ').strip()
        match = re.search(r'"id": "([^"]+)"', line)
        if match:
            section = match.group(1)
        for s in sentences(line):
            yield rel, section, s


def cell(text: str) -> str:
    return text.replace('|', '\\|').replace('\n', ' ')


def main() -> int:
    rows = list(docx_rows())
    for rel in CURRENT:
        rows += list(text_rows(rel))
    historical = []
    for rel in HISTORICAL:
        files = subprocess.run(['git', 'ls-files', rel], cwd=ROOT, capture_output=True, text=True).stdout.split()
        for f in files:
            try:
                n = len(TERMS.findall((ROOT / f).read_text(encoding='utf-8', errors='ignore')))
            except OSError:
                continue
            if n:
                historical.append((f, n))
    unreviewed = sum(justify(s, sec) == 'REVISAR' for _, sec, s in rows)
    lines = ['# Control de atribución IA/humano', '',
             '**Generado por:** `provenance/commands/task09/attribution_check.py` sobre el manuscrito tras la pasada 2g '
             'y los documentos que describen el estado actual.',
             '',
             '**Términos buscados:** IA, inteligencia artificial, Claude, agente/agentes, humano/humana, revisión manual '
             'o «manualmente», revisión visual y adjudicación. En los documentos en inglés también se buscan AI y human.',
             '',
             f'**Apariciones en documentos actuales:** {len(rows)}. **Sin justificación:** {unreviewed}.', '',
             '## Apariciones en el manuscrito y en los documentos actuales', '',
             '| Archivo | Sección | Frase | Justificación |', '|---|---|---|---|']
    lines += [f'| {cell(f)} | {cell(sec)} | {cell(s)} | {justify(s, sec)} |' for f, sec, s in rows]
    lines += ['', '## Registros históricos (no se modifican)', '',
              'Estos archivos registran lo que ocurrió en cada fecha: quién adjudicó, qué decía el texto en cada pasada '
              'y qué señalaron las revisiones. Corregirlos para que coincidan con la descripción actual falsearía la '
              'historia. La descripción actual está en el manuscrito, la carta y DECISION-040.', '',
              '| Archivo | Apariciones |', '|---|---:|']
    lines += [f'| `{f}` | {n} |' for f, n in historical]
    OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print(len(rows), 'current occurrences;', unreviewed, 'without justification;', len(historical), 'historical files')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
