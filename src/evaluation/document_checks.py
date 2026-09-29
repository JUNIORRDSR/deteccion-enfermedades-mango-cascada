"""Document checks for the manuscript: bibliography (TASK-08) and consistency (TASK-09).

Citation mode: --references --citations --out.
Consistency mode: --docx --claims --editorial --numbers [--metrics] --out; every registered
number (source given as a repository path) is re-derived from its artifact and must appear,
formatted, in the paragraph that holds
its anchor; editorial claims follow claim_language_issues; each lexical hit in the DOCX must be
covered by a reviewed editorial row (a lexical match alone never shows validity).
Exit codes: 0 no gaps or issues, 1 listed, 2 invalid input.
"""

import argparse
import csv
import json
import math
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from src.evaluation.provenance import InvalidInput, authorized_root, check_output, sanitize_text

ACCEPTED = {'VERIFIED', 'CORRECTED'}
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
EDITORIAL_FIELDS = ('location', 'claim', 'text', 'quote_status', 'evidence', 'decision')
EFFICIENCY = re.compile(r'eficien', re.IGNORECASE)
TEMPORAL = re.compile(r'tempran|precoz|presintom', re.IGNORECASE)
ABSOLUTE_LEAK = re.compile(r'libre de fuga|sin fuga|sin duplicados|independencia demostrada|'
                           r'\blimpi[oa]s?\b', re.IGNORECASE)
LANGUAGE = re.compile('|'.join(p.pattern for p in (EFFICIENCY, TEMPORAL, ABSOLUTE_LEAK)),
                      re.IGNORECASE)
REVIEWED = ('KEEP_ATTRIBUTED', 'MODERATE')


def citation_gaps(cited: set[str], references: set[str]) -> dict:
    return {'missing': sorted(cited - references), 'uncited': sorted(references - cited)}


def _norm(value: str) -> str:
    return re.sub(r'[^0-9a-z]+', '', (value or '').casefold())


def _doi(value: str) -> str:
    return re.sub(r'^(https?://)?(dx\.)?doi\.org/', '', (value or '').strip().casefold())


def identity_status(cited: dict, primary: dict) -> str:
    """MATCH only when DOI and title both agree; anything else needs a human decision."""
    if _doi(cited.get('doi')) == _doi(primary.get('doi')) and _norm(cited.get('title')) == _norm(primary.get('title')):
        return 'MATCH'
    return 'METADATA_CONFLICT'


def load_references(path: Path) -> set[str]:
    try:
        entries = json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise InvalidInput(f'references are not valid UTF-8 JSON: {error}') from error
    if not isinstance(entries, list):
        raise InvalidInput('references must be a JSON list')
    ids = set()
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get('id') or entry['id'] in ids:
            raise InvalidInput(f'reference without a unique id: {entry!r}')
        if entry.get('status') not in ACCEPTED:
            raise InvalidInput(f'{entry["id"]}: status {entry.get("status")!r} is not VERIFIED/CORRECTED')
        if not entry.get('evidence_url'):
            raise InvalidInput(f'{entry["id"]}: no evidence_url')
        ids.add(entry['id'])
    return ids


def load_citations(path: Path) -> set[str]:
    with path.open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    if not rows or 'ref_id' not in rows[0] or any(not row['ref_id'] for row in rows):
        raise InvalidInput('citations need a ref_id column with a value in every row')
    return {row['ref_id'] for row in rows}


def docx_paragraphs(path: Path) -> list[str]:
    """Text of every paragraph, table cells included, from word/document.xml (stdlib only)."""
    try:
        with zipfile.ZipFile(path) as package:
            body = ET.fromstring(package.read('word/document.xml'))
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as error:
        raise InvalidInput(f'not a readable DOCX: {error}') from error
    return [''.join(t.text or '' for t in p.iter(W + 't')) for p in body.iter(W + 'p')]


def fmt(value: float, digits: int, decimal: str = ',') -> str:
    return f'{value:.{digits}f}'.replace('.', decimal)


def number_issues(paragraphs: list[str], rows: list[dict], root: Path) -> list[dict]:
    """Each row {id, source, path, digits, anchor[, scale, decimal]} re-derives one printed
    number from its artifact; the anchor must name exactly one paragraph, which must show it."""
    issues = []
    for row in rows:
        where = {'id': row.get('id'), 'anchor': row.get('anchor')}
        try:
            value = json.loads((root / row['source']).read_text(encoding='utf-8'))
            for key in row['path']:
                value = value[key]
        except (OSError, KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            issues.append({**where, 'issue': f'value not found in its artifact: {error!r}'})
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            issues.append({**where, 'issue': f'artifact value is not a finite number: {value!r}'})
            continue
        expected = fmt(value * row.get('scale', 1), row['digits'], row.get('decimal', ','))
        hits = [p for p in paragraphs if row['anchor'] in p]
        if len(hits) != 1:
            issues.append({**where, 'issue': f'anchor found in {len(hits)} paragraphs'})
        elif not re.search(r'(?<![\d.,])' + re.escape(expected) + r'(?!\d)', hits[0]):
            issues.append({**where, 'issue': f'paragraph does not show {expected}',
                           'expected': expected})
    return issues


def claim_language_issues(rows: list[dict], criterion: str | None = None) -> list[dict]:
    """Own claims kept as written: efficiency needs a prior operational criterion cited in the
    evidence (the freeze defines none, so criterion is None and a descriptive benchmark never
    suffices); temporality and absolute leakage phrases are never kept. Attributed rows may be
    kept but are not own evidence."""
    issues = []
    for row in rows:
        where = {'location': row.get('location'), 'claim': row.get('claim')}
        missing = [f for f in EDITORIAL_FIELDS if not (row.get(f) or '').strip()]
        if missing:
            issues.append({**where, 'issue': f'missing fields {missing}'})
            continue
        if row['quote_status'].strip().upper() != 'OWN' or \
                not row['decision'].strip().upper().startswith('KEEP'):
            continue
        said = f"{row['claim']} {row['text']}"
        if EFFICIENCY.search(said) and not (criterion and criterion in row['evidence']):
            issues.append({**where, 'issue': 'efficiency kept without a prior operational criterion'})
        if TEMPORAL.search(said):
            issues.append({**where, 'issue': 'temporality kept without temporal evidence'})
        if ABSOLUTE_LEAK.search(said):
            issues.append({**where, 'issue': 'absolute leakage phrase kept as an own claim'})
    return issues


def language_hits(paragraphs: list[str], editorial: list[dict]) -> list[dict]:
    """Every lexical hit, marked reviewed only when a KEEP_ATTRIBUTED or MODERATE row quotes
    text found in the same paragraph."""
    kept = [r['text'] for r in editorial
            if (r.get('decision') or '').strip().upper().startswith(REVIEWED) and r.get('text')]
    hits = []
    for index, paragraph in enumerate(paragraphs):
        for match in LANGUAGE.finditer(paragraph):
            hits.append({'paragraph': index, 'match': match.group(0),
                         'context': paragraph[max(0, match.start() - 60):match.end() + 60],
                         'reviewed': any(text in paragraph for text in kept)})
    return hits


def critical_claim_issues(rows: list[dict]) -> list[dict]:
    return [{'claim_id': r.get('claim_id'), 'issue': f"{r.get('status')} without a revision action"}
            for r in rows if r.get('status') in {'UNVERIFIED', 'UNSUPPORTED'}
            and not (r.get('revision_action') or '').strip()]


def _csv(path: Path) -> list[dict]:
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def consistency(args, root: Path) -> dict:
    paragraphs = docx_paragraphs(args.docx)
    editorial = _csv(args.editorial)
    try:
        numbers = json.loads(args.numbers.read_text(encoding='utf-8'))
    except json.JSONDecodeError as error:
        raise InvalidInput(f'numbers registry is not JSON: {error}') from error
    if not isinstance(numbers, list):
        raise InvalidInput('numbers registry must be a JSON list')
    hits = language_hits(paragraphs, editorial)
    if args.metrics and not args.metrics.is_dir():
        raise InvalidInput(f'--metrics is not a directory: {args.metrics}')
    return {'metrics_dir': str(args.metrics) if args.metrics else None,
            'numbers': number_issues(paragraphs, numbers, root),
            'editorial': claim_language_issues(editorial),
            'claims': critical_claim_issues(_csv(args.claims)),
            'language_unreviewed': [h for h in hits if not h['reviewed']],
            'language_reviewed': [h for h in hits if h['reviewed']],
            'checked_numbers': len(numbers)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--references', type=Path)
    parser.add_argument('--citations', type=Path)
    parser.add_argument('--docx', type=Path)
    parser.add_argument('--claims', type=Path)
    parser.add_argument('--editorial', type=Path, default=Path('reports/editorial_claim_audit.csv'))
    parser.add_argument('--numbers', type=Path, default=Path('manuscript/numbers.json'))
    parser.add_argument('--metrics', type=Path,
                        help='metrics directory, recorded; number sources are repository paths')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    root = authorized_root()
    destination = check_output(root, args.out)
    if args.docx:
        if not args.claims:
            parser.error('--docx needs --claims')
        report = consistency(args, root)
        failed = any(report[k] for k in ('numbers', 'editorial', 'claims', 'language_unreviewed'))
    else:
        if not (args.references and args.citations):
            parser.error('citation mode needs --references and --citations')
        report = citation_gaps(load_citations(args.citations), load_references(args.references))
        failed = bool(report['missing'] or report['uncited'])
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    return 1 if failed else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (InvalidInput, OSError, csv.Error) as error:
        print(sanitize_text(str(error)), file=sys.stderr)
        sys.exit(2)
