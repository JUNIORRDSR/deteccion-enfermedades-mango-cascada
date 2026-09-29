"""TASK-09 pass 1b: the cascade as implemented (ED-16) and the redrawn Figures 1 and 2.

The command-line cascade crops EVERY M1 box and labels it with M2's class, or «Desconocido»
below 0.4 (src/cascade/runtime.py, from infer_cascade.py at e7e59d1). The FastAPI service
runs M1 only (CLAIM-039). Figures 1-2 are replaced by provenance/commands/task09/figures.py
output with the same pixel size. REVIEW-12/13: the cascade metric is defined and BLOCKED.
"""

import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
from docx_edit import replace, set_paragraph, sha  # noqa: E402

DOCX = ROOT / 'manuscript/source/Articulo_Mango_ALBUS_revision.docx'
FIGURES = {'word/media/image1.png': ROOT / 'manuscript/figures/fig1_cascada.png',
           'word/media/image2.png': ROOT / 'manuscript/figures/fig2_prototipos.png'}


def replace_media(path: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / 'out.docx'
        with zipfile.ZipFile(path) as src, zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as dst:
            for item in src.infolist():
                data = FIGURES[item.filename].read_bytes() if item.filename in FIGURES \
                    else src.read(item.filename)
                dst.writestr(item, data)
        shutil.copyfile(out, path)


def main() -> int:
    before = sha(DOCX)
    d = docx.Document(DOCX)
    set_paragraph(d, 'El sistema se estructura como una arquitectura en cascada',
                  'El sistema se estructura como una arquitectura en cascada (Figura 1) compuesta por '
                  'dos modelos YOLO especializados. El detector localiza los mangos y asigna a cada caja '
                  'la clase Enfermo o Saludable. En la implementación evaluada, cada caja se recorta, se '
                  'redimensiona a 224 × 224 píxeles y se entrega al clasificador, sea cual sea su clase; '
                  'la etiqueta final del fruto es la del clasificador (cuatro enfermedades o Saludable), '
                  'o «Desconocido» si su confianza es menor que 0,4. Enviar al clasificador sólo las cajas '
                  'Enfermo es una variante de diseño que ahorraría cómputo, pero no está implementada.')
    set_paragraph(d, 'Figura 1. Arquitectura en cascada',
                  'Figura 1. Cascada implementada. El Modelo 1 (YOLO26n) localiza los frutos; el Modelo 2 '
                  '(YOLO11n-cls) clasifica el recorte de cada caja en cuatro enfermedades o Saludable. '
                  'Fuente: elaboración propia con datos de Jairos Workspace (2026) y Barhate et al. (2025).')
    replace(d, 'Tercero, el costo computacional del clasificador solo se incurre sobre los recortes que el '
               'detector marca como enfermos, optimizando el rendimiento.',
            'Tercero, la cascada permitiría ejecutar el clasificador sólo sobre los recortes marcados como '
            'enfermos; la implementación evaluada no lo hace todavía y clasifica todos los recortes.')
    set_paragraph(d, 'Figura 2. Arquitectura prevista del servicio web.',
                  'Figura 2. Prototipos implementados: el servicio web FastAPI ejecuta sólo el Modelo 1; '
                  'la cascada completa se ejecuta por línea de comandos. Fuente: elaboración propia.')
    set_paragraph(d, 'La Figura 7 ilustra la cascada completa',
                  'La Figura 7 ilustra la cascada completa sobre nueve escenas del conjunto de prueba del '
                  'detector. El Modelo 2 se ejecuta sobre cada caja detectada, así que el costo crece con '
                  'el número de frutos de la escena. La latencia medida con el protocolo de la Sección 4.1.5 '
                  'es [PENDIENTE: TASK-06]. La figura es ilustrativa: no hay verdad de terreno de enfermedad '
                  'específica para esas escenas y no evidencia diagnósticos correctos.')
    replace(d, 'Cada bbox marcada como Enfermo por el Modelo 1 recibe el diagnóstico fino del Modelo 2 '
               '(Antracnosis, Cancro Bacteriano, Costras o Podredumbre del Extremo del Tallo). Las cajas '
               'verdes corresponden a frutos clasificados como Saludable y se omite el paso al Modelo 2 '
               'para optimizar latencia.',
            'Cada caja detectada por el Modelo 1 recibe la clase del Modelo 2 (Antracnosis, Cancro '
            'Bacteriano, Costras, Podredumbre del Extremo del Tallo o Saludable). Las etiquetas no están '
            'verificadas con verdad de terreno de enfermedad.')
    replace(d, 'El costo es la propagación de errores: un falso negativo del Modelo 1 hace inalcanzable el '
               'diagnóstico fino sobre ese fruto, lo cual refuerza la prioridad de la sensibilidad del '
               'detector.',
            'El costo es la propagación de errores: un fruto enfermo que el Modelo 1 no detecta nunca '
            'recibe diagnóstico, así que el desempeño de la cascada no es el producto de los desempeños '
            'de cada modelo. La métrica que lo mide es la proporción de frutos enfermos que reciben a la '
            'vez una detección emparejada (IoU ≥ 0,5) y la enfermedad correcta, sobre todos los frutos '
            'enfermos, detectados o no. Calcularla exige verdad de terreno conjunta, con caja y '
            'diagnóstico adjudicados para los mismos frutos, que ninguno de los dos conjuntos tiene. La '
            'métrica y su evaluador quedan definidos, pero su valor no se informa.')
    d.save(DOCX)
    replace_media(DOCX)
    docx.Document(DOCX)  # still opens after the media swap
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8'))
    entries.append({'pass': '1b', 'script': 'provenance/commands/task09/revise_pass1b.py',
                    'before_sha256': before, 'after_sha256': sha(DOCX),
                    'figures': {k: sha(v) for k, v in FIGURES.items()}})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(entries[-1], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
