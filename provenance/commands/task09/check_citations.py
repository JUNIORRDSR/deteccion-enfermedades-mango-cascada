"""Two-way check of the DOCX: every author-year citation in the text has a reference-list entry
and every entry is cited. Keys are (first surname or corporate author, year[letter]).

Corporate authors cited by acronym are mapped in ALIASES. Prints the gaps; exit 1 when any.
"""

import re
import sys
import unicodedata
from pathlib import Path

import docx

ROOT = Path(__file__).resolve().parents[3]
DOCX = ROOT / 'manuscript/source/Articulo_Mango_ALBUS_revision.docx'
ALIASES = {'dane': 'departamento', 'intelcorporation': 'intel'}
YEAR = r'(?:19|20)\d{2}[a-z]?'


def key(author: str, year: str) -> tuple[str, str]:
    text = unicodedata.normalize('NFKD', author).encode('ascii', 'ignore').decode().casefold()
    words = re.findall(r'[a-z]+', text.replace('et al', ''))
    stop = {'van', 'der', 'de', 'la', 'del', 'y', 'e', 'the'}
    first = next((w for w in words if w not in stop), '') if len(words) > 1 else ''.join(words)
    first = ''.join(words[:2]) if ''.join(words[:2]) in ALIASES else first
    return ALIASES.get(first, first), year


def cited(text: str, known: set) -> set:
    found = set()
    for group in re.findall(r'\(([^()]*?' + YEAR + r'[^()]*)\)', text):
        for part in group.split(';'):
            m = re.search(r'([^,;]*?),?\s*(' + YEAR + r')', part)
            if m and re.search(r'[A-Za-zÀ-ÿ]', m.group(1)):
                found.add(key(m.group(1), m.group(2)))
    # Narrative «Autor (año)»: one or two capitalised words (Jairos Workspace) or two authors
    # joined by y/& (Kapoor y Narayanan); the key is the first word when that one is listed.
    word = r'[A-ZÀ-Ý][\w\-À-ÿ]+'
    for m in re.finditer(rf'(?:({word})\s+(?:(?:y|&)\s+)?)?({word}(?:\s+et al\.)?)\s+\(({YEAR})\)', text):
        one = key(m.group(2), m.group(3))
        two = key(f'{m.group(1)} {m.group(2)}', m.group(3)) if m.group(1) else one
        found.add(two if two in known and one not in known else one)
    return found


def listed(paragraphs) -> set:
    out = set()
    for p in paragraphs:
        m = re.match(r'(.+?)\((' + YEAR + r')', p.text)
        if m:
            out.add(key(m.group(1).split(',')[0].split('.')[0], m.group(2)))
    return out


def main() -> int:
    d = docx.Document(DOCX)
    refs = [p for p in d.paragraphs if p.style.name == 'ALBUS_7.1_References']
    body = '\n'.join(p.text for p in d.paragraphs if p.style.name != 'ALBUS_7.1_References')
    body += '\n' + '\n'.join(c.text for t in d.tables for r in t.rows for c in r.cells)
    in_list = listed(refs)
    in_text = cited(body, in_list)
    missing, uncited = sorted(in_text - in_list), sorted(in_list - in_text)
    print(f'{len(refs)} entries, {len(in_text)} cited keys')
    print('cited without entry:', missing)
    print('entry never cited:', uncited)
    return 1 if missing or uncited else 0


def self_check() -> None:
    known = {('kapoor', '2023'), ('jairos', '2026'), ('barhate', '2025'), ('departamento', '2024')}
    text = ('según Kapoor y Narayanan (2023) y Barhate et al. (2025); datos de Jairos Workspace '
            '(2026) (Kapoor & Narayanan, 2023; DANE, 2024) y (Nadie, 2019).')
    assert cited(text, known) == known | {('nadie', '2019')}, cited(text, known)


if __name__ == '__main__':
    if '--self-check' in sys.argv:
        self_check()
        print('self-check ok')
        sys.exit(0)
    sys.exit(main())
