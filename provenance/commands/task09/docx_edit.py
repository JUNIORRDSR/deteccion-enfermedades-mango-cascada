"""Paragraph-level edits of the canonical DOCX that keep the template styles.

Each edit names the exact text it expects, so an edit that no longer matches fails instead
of silently rewriting the wrong paragraph. Inline formatting inside the replaced span takes
the formatting of the run where the span starts; text outside the span keeps its runs.
"""

import copy
import hashlib
from pathlib import Path

import docx


class EditFailed(Exception):
    pass


def _find(document, old: str):
    hits = [p for p in document.paragraphs if old in p.text]
    if len(hits) != 1:
        raise EditFailed(f'{len(hits)} paragraphs contain {old[:70]!r}')
    return hits[0]


def replace(document, old: str, new: str) -> None:
    """Replace one exact span; the span may cross runs."""
    p = _find(document, old)
    start = p.text.index(old)
    end = start + len(old)
    pos, first = 0, None
    for run in list(p.runs):
        text = run.text
        a, b = pos, pos + len(text)
        pos = b
        if b <= start or a >= end:
            continue
        keep_before = text[:max(0, start - a)]
        keep_after = text[max(0, end - a):] if b > end else ''
        if first is None:
            run.text = keep_before + new + keep_after
            first = run
        else:
            run.text = keep_after
    if first is None:
        raise EditFailed(f'span not found in runs: {old[:70]!r}')


def set_paragraph(document, old_start: str, new: str) -> None:
    """Replace a whole paragraph identified by its opening text, keeping its first run style."""
    p = _find(document, old_start)
    if not p.text.startswith(old_start):
        raise EditFailed(f'paragraph does not start with {old_start[:70]!r}')
    runs = p.runs
    runs[0].text = new
    for run in runs[1:]:
        run._element.getparent().remove(run._element)


def set_runs(document, old_start: str, segments: list[tuple[str, str]]) -> None:
    """Rewrite a paragraph as segments (text, flags), flags a subset of 'bi' (bold, italic).

    Every run copies the character properties of the paragraph's first NON-bold run (the
    body style), then sets bold/italic explicitly, so a bold lead-in does not spread.
    """
    p = _find(document, old_start)
    if not p.text.startswith(old_start):
        raise EditFailed(f'paragraph does not start with {old_start[:70]!r}')
    runs = p.runs
    base = next((r for r in runs if not r.bold), runs[0])
    rpr = copy.deepcopy(base._element.rPr) if base._element.rPr is not None else None
    for run in runs:
        run._element.getparent().remove(run._element)
    for text, flags in segments:
        run = p.add_run(text)
        if rpr is not None:
            run._element.insert(0, copy.deepcopy(rpr))
        run.bold = 'b' in flags
        run.italic = 'i' in flags


def delete_paragraph(document, old_start: str) -> None:
    p = _find(document, old_start)
    if not p.text.startswith(old_start):
        raise EditFailed(f'paragraph does not start with {old_start[:70]!r}')
    p._element.getparent().remove(p._element)


def insert_after(document, anchor_start: str, text: str, like: str | None = None) -> None:
    """New paragraph after the anchor, copying the paragraph properties of `like` (or the anchor)."""
    anchor = _find(document, anchor_start)
    model = _find(document, like) if like else anchor
    element = copy.deepcopy(model._element)
    for child in list(element):
        if child.tag.endswith('}r') or child.tag.endswith('}hyperlink'):
            element.remove(child)
    anchor._element.addnext(element)
    new = docx.text.paragraph.Paragraph(element, anchor._parent)
    run = new.add_run(text)
    if model.runs and model.runs[0]._element.rPr is not None:
        run._element.insert(0, copy.deepcopy(model.runs[0]._element.rPr))


def cell_text(document, table: int, row: int, col: int, new: str) -> None:
    cell = document.tables[table].cell(row, col)
    paragraph = cell.paragraphs[0]
    runs = paragraph.runs
    if runs:
        runs[0].text = new
        for run in runs[1:]:
            run._element.getparent().remove(run._element)
    else:
        paragraph.add_run(new)


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
