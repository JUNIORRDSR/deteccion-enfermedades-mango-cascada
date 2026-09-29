"""Redraw Figures 1 and 2 so their embedded text matches what is implemented (SPEC section 10).

Fig. 1: the cascade of the command-line script. Every M1 box is cropped and classified by M2
into five classes (four diseases + Saludable); the final label is M2's, or «Desconocido»
below 0.4 confidence (src/cascade/runtime.py, copied from infer_cascade.py at e7e59d1).
Fig. 2: the two prototypes. The FastAPI service runs M1 only (CLAIM-039); the cascade runs
from the command line. Same pixel size as the originals, so the DOCX extents stay valid.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
DPI = 100  # drawing geometry: the originals' pixel size at this DPI fixes the aspect ratio
SAVE_DPI = 300  # audit B, B-13: same physical size in the DOCX, three times the pixels
NAVY, TEAL, LIGHT, ORANGE, GREY = '#1b365d', '#1d5f63', '#eaf5f7', '#fdf4ec', '#f2f2f2'


def box(ax, x, y, w, h, title, body, face, edge, title_color='black', body_color='black'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.03',
                                facecolor=face, edgecolor=edge, linewidth=1.2))
    ax.text(x + w / 2, y + h * 0.66, title, ha='center', va='center', fontsize=10.5,
            fontweight='bold', color=title_color)
    ax.text(x + w / 2, y + h * 0.33, body, ha='center', va='center', fontsize=9,
            color=body_color, linespacing=1.3)


def arrow(ax, a, b, label=None, rad=0.0, offset=(0.0, 0.025)):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=14, linewidth=1.3,
                                 color='#444444', connectionstyle=f'arc3,rad={rad}'))
    if label:
        ax.text((a[0] + b[0]) / 2 + offset[0], (a[1] + b[1]) / 2 + offset[1], label,
                ha='center', fontsize=8.5, style='italic', color='#444444')


def canvas(width_px, height_px, title):
    fig = plt.figure(figsize=(width_px / DPI, height_px / DPI), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.text(0.5, 0.95, title, ha='center', va='center', fontsize=13, fontweight='bold')
    return fig, ax


def figure1(path):
    fig, ax = canvas(806, 601, 'Cascada implementada (script de línea de comandos)')
    box(ax, 0.03, 0.70, 0.18, 0.14, 'Entrada', 'imagen RGB: archivo,\nvídeo o cámara',
        'white', NAVY)
    box(ax, 0.27, 0.70, 0.24, 0.14, 'MODELO 1', 'YOLO26n: detección de frutos\ncajas Enfermo / Saludable',
        NAVY, NAVY, 'white', 'white')
    box(ax, 0.58, 0.70, 0.36, 0.14, 'Cajas detectadas', 'confianza ≥ umbral operativo\n'
        'fijado en validación', LIGHT, TEAL, TEAL)
    box(ax, 0.58, 0.42, 0.36, 0.14, 'Recorte de cada caja', 'todas las cajas, sea cual sea\n'
        'su clase; reescalado a 224 × 224 px', ORANGE, '#c8621b', '#c8621b')
    box(ax, 0.05, 0.42, 0.44, 0.14, 'MODELO 2', 'YOLO11n-cls: 5 clases\n4 enfermedades + Saludable',
        TEAL, TEAL, 'white', 'white')
    box(ax, 0.12, 0.12, 0.76, 0.15, 'Etiqueta final por fruto',
        'Antracnosis | Cancro bacteriano | Costras | Podredumbre del extremo del tallo | Saludable\n'
        '«Desconocido» si la confianza del Modelo 2 es menor que 0,4', LIGHT, TEAL)
    arrow(ax, (0.21, 0.77), (0.27, 0.77))
    arrow(ax, (0.51, 0.77), (0.58, 0.77))
    arrow(ax, (0.76, 0.70), (0.76, 0.56))
    arrow(ax, (0.58, 0.49), (0.49, 0.49))
    arrow(ax, (0.27, 0.42), (0.40, 0.27), 'clase', offset=(-0.08, 0.0))
    ax.text(0.5, 0.045, 'Datos: detector, mangoUnhealty v2 (Jairos Workspace, 2026), 669 imágenes;\n'
            'clasificador, MangoDHDS (Barhate et al., 2025), 1500 imágenes.', ha='center',
            fontsize=8, style='italic', color='#555555')
    fig.savefig(path, dpi=SAVE_DPI)
    plt.close(fig)


def figure2(path):
    fig, ax = canvas(853, 505, 'Prototipos implementados')
    ax.text(0.26, 0.84, 'Servicio web', ha='center', fontsize=11, fontweight='bold', color=NAVY)
    box(ax, 0.02, 0.52, 0.15, 0.22, 'Cliente', 'navegador\no móvil', '#f5f0fb', '#7b4bb3',
        '#7b4bb3')
    box(ax, 0.29, 0.52, 0.20, 0.22, 'API FastAPI', 'Modelo 1 (YOLO26n)\ndetección binaria',
        NAVY, NAVY, 'white', 'white')
    box(ax, 0.10, 0.18, 0.32, 0.18, 'Respuesta', 'cajas Enfermo / Saludable\ncon su confianza',
        ORANGE, '#c8621b', '#c8621b')
    arrow(ax, (0.19, 0.63), (0.27, 0.63), 'imagen', offset=(0.0, 0.02))
    arrow(ax, (0.39, 0.52), (0.30, 0.36))
    ax.plot([0.535, 0.535], [0.12, 0.88], color='#bbbbbb', linewidth=1, linestyle='--')
    ax.text(0.77, 0.84, 'Script de línea de comandos', ha='center', fontsize=11,
            fontweight='bold', color=TEAL)
    box(ax, 0.58, 0.52, 0.17, 0.22, 'Entrada', 'imagen, carpeta,\nvídeo o cámara', 'white', NAVY)
    box(ax, 0.79, 0.52, 0.18, 0.22, 'Cascada', 'Modelo 1 → recortes\n→ Modelo 2', TEAL, TEAL,
        'white', 'white')
    box(ax, 0.64, 0.18, 0.30, 0.18, 'Salida', 'imagen anotada con\nla etiqueta del Modelo 2',
        LIGHT, TEAL, TEAL)
    arrow(ax, (0.75, 0.63), (0.79, 0.63))
    arrow(ax, (0.88, 0.52), (0.82, 0.36))
    ax.text(0.5, 0.05, 'La integración de la cascada en el servicio web no está implementada.',
            ha='center', fontsize=8.5, style='italic', color='#555555')
    fig.savefig(path, dpi=SAVE_DPI)
    plt.close(fig)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    figure1(OUT / 'fig1_cascada.png')
    figure2(OUT / 'fig2_prototipos.png')
    print('ok')
