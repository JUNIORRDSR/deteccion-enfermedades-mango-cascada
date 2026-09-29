"""TASK-09 pass 2e: the corrections of audit B round 2 (reports/execution/task-09-results-audit-round2.md)
on the manuscript after pass 2d and on the response letter.

R2-01 the nano variant is no longer justified by an untested speed/memory/edge balance; R2-02 the
RGB-D and Raspberry Pi extensions are future work without an impact forecast; R2-03 Section 3.7 and
REVIEW-04 call the tests internal retrospective evaluations; R2-06 «limpio/limpia» gives way to the
dataset name and the protocol-bounded wording; R2-07 the letter header names CLAIM-042 as the one
pending author action; R2-08 Figure 5 keeps every label inside its image; R2-09 the document
author metadata lists the manuscript authors. From the render review of this pass: headings keep
with the next paragraph, and 6.1 describes the full-image labels as 3.5 does (CLAIM-031). No result
number changes.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
import revise_pass2c  # noqa: E402
from docx_edit import EditFailed, replace, sha  # noqa: E402
from revise_letter import LETTER, apply  # noqa: E402

ROOT = revise_pass2c.ROOT
DOCX = revise_pass2c.DOCX

EDITS = [
    # R2-01
    ('La variante nano fue seleccionada por su equilibrio entre velocidad de inferencia, precisión '
     'sobre objetos medianos y huella de memoria compatible con despliegue en hardware de borde.',
     'La variante nano es la del run histórico; este trabajo no comparó variantes de otro tamaño.'),
    # R2-02
    ('La incorporación futura de información tridimensional (RGB-D) mediante la cámara Intel '
     'RealSense D435 y el despliegue edge sobre Raspberry Pi 4 con cuantización INT8 son las '
     'extensiones naturales que consolidarían el enfoque dentro del paradigma de Agricultura 4.0 como '
     'motor de sostenibilidad alimentaria en Colombia.',
     'La incorporación de información tridimensional (RGB-D) con la cámara Intel RealSense D435 y el '
     'despliegue sobre Raspberry Pi 4 con cuantización INT8 quedan como trabajo futuro; este estudio '
     'no evaluó ninguno de los dos.'),
    # R2-03
    ('la prueba se evaluó una sola vez, con ambos fijados.',
     'la prueba se evaluó una sola vez, con ambos fijados. Las pruebas de los dos modelos son '
     'evaluaciones internas retrospectivas sobre imágenes ya publicadas (Secciones 4.1.2 y 4.2.3).'),
    # R2-06
    ('sobre la partición limpia de MangoDHDS (',
     'sobre la partición de prueba de MangoDHDS_clean, regenerada sin casi duplicados detectados entre '
     'particiones ('),
    ('evaluado de forma retrospectiva sobre la partición limpia de MangoDHDS,',
     'evaluado de forma retrospectiva sobre la partición de prueba de MangoDHDS_clean,'),
    ('El conjunto limpio tiene', 'MangoDHDS_clean tiene'),
    # CLAIM-031 in 6.1, as in 3.5: the full-image boxes are derived, not annotations of the corpus
    ('La segunda limitación corresponde a la naturaleza de las anotaciones del corpus público '
     'utilizado para el clasificador: las cajas envuelven la imagen completa,',
     'La segunda limitación es que el corpus público utilizado para el clasificador sólo tiene '
     'etiquetas de imagen completa,'),
]
LETTER_EDITS = {
    '# Respuesta al dictamen': [
        ('tras la pasada 2d', 'tras la pasada 2e'),
        ('Ninguna acción pendiente se describe como hecha.',
         'La única acción pendiente de los autores es CLAIM-042: el resumen y la Sección 5.3 dicen que '
         'el protocolo de auditoría y su código se publican, lo que exige publicar el repositorio y '
         'citarlo antes del envío, o suavizar ambas frases.')],
    '## REVIEW-04': [
        ('El test nuevo tiene', 'La nueva partición interna de prueba, evaluada de forma retrospectiva, '
                                'tiene')],
}
FIGURES = {'word/media/image5.png': 'manuscript/figures/fig5_detecciones.png'}  # R2-08


def authors(document) -> str:
    lines = [p.text for p in document.paragraphs if p.style.name == 'ALBUS_1.3_authornames']
    if len(lines) != 1 or not lines[0].strip():
        raise EditFailed(f'expected one author line, found {lines!r}')
    return lines[0].strip()


def main() -> int:
    from revise_pass2b import replace_media
    before = sha(DOCX)
    d = docx.Document(DOCX)
    for old, new in EDITS:
        replace(d, old, new)
    after_heading = False  # render review: no heading left alone at the foot of a page
    for p in d.paragraphs:
        heading = 'heading' in p.style.name.lower()
        if heading or (after_heading and not p.text.strip()):  # and the spacer that follows it
            p.paragraph_format.keep_with_next = True
        after_heading = heading
    d.core_properties.author = authors(d)  # R2-09
    d.save(DOCX)
    for name, source in FIGURES.items():
        replace_media(DOCX, name, ROOT / source)
    docx.Document(DOCX)
    raw = LETTER.read_bytes()
    newline = '\r\n' if b'\r\n' in raw else '\n'
    LETTER.write_bytes(apply(raw.decode('utf-8').replace('\r\n', '\n'), LETTER_EDITS)
                       .replace('\n', newline).encode('utf-8'))
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8'))
    entries.append({'pass': '2e', 'script': 'provenance/commands/task09/revise_pass2e.py',
                    'responds_to': 'reports/execution/task-09-results-audit-round2.md R2-01 to R2-09',
                    'before_sha256': before, 'after_sha256': sha(DOCX),
                    'figures': {k: sha(ROOT / f) for k, f in FIGURES.items()}})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(entries[-1], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
