"""TASK-09 pass 1c: restore run formatting lost by whole-paragraph rewrites in passes 1/1b.

Bold lead-ins (figure labels, «Procedencia de las imágenes.») and the italic class names
Enfermo/Saludable used elsewhere in the text. Text is unchanged except for formatting.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
from docx_edit import set_runs, sha  # noqa: E402

DOCX = ROOT / 'manuscript/source/Articulo_Mango_ALBUS_revision.docx'


def split_on(text: str, lead: str | None = None, italic: tuple[str, ...] = ()) -> list:
    """Segments: an optional bold lead, then the text with the given words in italics."""
    segments = []
    if lead:
        if not text.startswith(lead):
            raise SystemExit(f'{text[:40]!r} does not start with {lead!r}')
        segments.append((lead, 'b'))
        text = text[len(lead):]
    pieces = [(text, '')]
    for word in italic:
        out = []
        for piece, flags in pieces:
            if flags:
                out.append((piece, flags))
                continue
            parts = piece.split(word)
            for i, part in enumerate(parts):
                if part:
                    out.append((part, ''))
                if i < len(parts) - 1:
                    out.append((word, 'i'))
        pieces = out
    return segments + pieces


def main() -> int:
    before = sha(DOCX)
    d = docx.Document(DOCX)
    by_start = {p.text[:40]: p.text for p in d.paragraphs}

    def fix(start: str, lead: str | None = None, italic: tuple[str, ...] = ()) -> None:
        text = next(t for s, t in by_start.items() if t.startswith(start))
        set_runs(d, start, split_on(text, lead, italic))

    fix('Figura 1. Cascada implementada.', lead='Figura 1. ')
    fix('Figura 2. Prototipos implementados', lead='Figura 2. ')
    fix('Procedencia de las imágenes.', lead='Procedencia de las imágenes.')
    fix('El sistema se estructura como una arquitectura en cascada', italic=('Enfermo', 'Saludable'))
    fix('El corpus está desbalanceado hacia la clase Saludable', italic=('Saludable',))
    d.save(DOCX)
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8'))
    entries.append({'pass': '1c', 'script': 'provenance/commands/task09/revise_pass1c.py',
                    'before_sha256': before, 'after_sha256': sha(DOCX)})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(entries[-1], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
