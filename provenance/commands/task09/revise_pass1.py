"""TASK-09 pass 1: edits that do not depend on the retraining results.

Sources of every change: reports/editorial_claim_audit.csv (ED-xx), reports/citation_links.csv
and reports/bibliography_audit.csv (TASK-08), docs/research/claim_evidence_matrix.csv
(CLAIM-039: the FastAPI service runs M1 only) and the TASK-02 audit. Text that depends on
EXP-R01/R02/R03 or TASK-06 is left as [PENDIENTE: ...] and filled in pass 2 from artifacts.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
from docx_edit import cell_text, delete_paragraph, replace, set_paragraph, sha  # noqa: E402

DOCX = ROOT / 'manuscript/source/Articulo_Mango_ALBUS_revision.docx'


def main() -> int:
    before = sha(DOCX)
    d = docx.Document(DOCX)

    # Title, abstract (ED-01, ED-02, ED-03, ED-15; REVIEW-10)
    replace(d, 'DETECCIÓN Y CLASIFICACIÓN EFICIENTE DE', 'DETECCIÓN Y CLASIFICACIÓN AUTOMATIZADA DE')
    replace(d, 'Este proyecto busca diseñar un sistema de detección temprana de enfermedades en frutos '
               'de mango, con el fin de documentar su rendimiento, limitaciones y la calidad del corpus '
               'utilizado.',
            'Este trabajo diseña un sistema de detección visual automatizada de signos de enfermedad en '
            'frutos de mango y documenta su rendimiento, sus limitaciones y la calidad de los corpus '
            'utilizados.')
    replace(d, 'La cascada propuesta provee un balance favorable entre precisión y costo computacional '
               'para diagnóstico fitopatológico en mango, además el protocolo de auditoría de fuga '
               'publicado es reutilizable sobre otros conjuntos agrícolas.',
            'Una auditoría de fuga de datos mostró que el test publicado del detector compartía origen '
            'con su entrenamiento; el detector se reentrenó con una partición por grupos de origen y se '
            'evaluó una sola vez sobre su nuevo test [PENDIENTE: resultados de EXP-R02 con intervalos]. '
            'Se publican el protocolo de auditoría y su código.')

    # Introduction (TASK-08: DANE retired and replaced, Savary, pathogens, Van der Heijden blocked)
    set_paragraph(d, 'La agricultura representa aproximadamente',
                  'En 2023, la agricultura, la ganadería, la caza, la silvicultura y la pesca ocuparon '
                  'al 14,4 % de la población ocupada en Colombia (DANE, 2024).')
    replace(d, 'el Cancro Bacteriano (Xanthomonas campestris), la Cenicilla (Oidium mangiferae), las '
               'Costras y la Podredumbre del Extremo del Tallo (Dofuor et al., 2023; Iqbal et al., 2024).',
            'el Cancro Bacteriano, las Costras y la Podredumbre del Extremo del Tallo (Dofuor et al., '
            '2023), además de la Cenicilla (Pseudoidium anacardii, antes Oidium mangiferae; Iqbal et '
            'al., 2024).')
    set_paragraph(d, 'Estimaciones globales sobre el impacto',
                  'En cinco cultivos básicos, las pérdidas por plagas y patógenos se estiman entre el '
                  '17 % y el 30 % de la producción, según el cultivo (Savary et al., 2019).')
    replace(d, 'en contextos agrícolas (Van der Heijden et al., 2022). Se ha documentado que los modelos '
               'basados en redes neuronales convolucionales (CNN) superan consistentemente a los '
               'enfoques clásicos en clasificación de imágenes foliares, y trabajos posteriores han '
               'confirmado que las arquitecturas ligeras de detección de objetos en tiempo real, en '
               'particular la familia YOLO (You Only Look Once), son apropiadas para inferencia en '
               'dispositivos de campo con restricciones de cómputo (Liu & Wang, 2021).',
            'en contextos agrícolas. En la detección de enfermedades y plagas, los modelos de '
            'aprendizaje profundo superan a los métodos tradicionales, y los detectores de una sola '
            'pasada como YOLO (You Only Look Once) permiten inferencia en tiempo real (Liu & Wang, '
            '2021).')
    replace(d, 'La sección Sección 2 revisa los trabajos relacionados. La sección Sección 3 describe los '
               'materiales y métodos. La sección Sección 4 presenta los resultados experimentales. La '
               'sección Sección 5 discute los hallazgos. La sección Sección 6 resume las limitaciones y '
               'el trabajo futuro. La sección Sección 7 concluye.',
            'La Sección 2 revisa los trabajos relacionados; la Sección 3 describe los materiales y '
            'métodos; la Sección 4 presenta los resultados; la Sección 5 los discute; la Sección 6 '
            'resume las limitaciones y el trabajo futuro, y la Sección 7 concluye.')

    # Related work (TASK-08 support judgements)
    set_paragraph(d, 'Paulus (Paulus, 2019)',
                  'Paulus (2019) revisó el uso de la geometría tridimensional para medir rasgos de '
                  'plantas, como la longitud y el ancho de las hojas o el volumen.')
    set_paragraph(d, 'En el articulo Jin et al. (2021)',
                  'Jin et al. (2021) revisaron las plataformas terrestres y aéreas de fenotipado de alto '
                  'rendimiento para estimar rasgos de cultivos.')
    delete_paragraph(d, 'De igual manera en el paper Van der Heijden et al. (2022)')
    replace(d, 'Sus características distintivas —detección en una única pasada y arquitectura '
               'unificada— la hacen particularmente apropiada para inferencia en hardware de recursos '
               'limitados (Redmon et al., 2016).',
            'Su detección en una única pasada, con una arquitectura unificada, permite inferencia en '
            'tiempo real (Redmon et al., 2016).')
    delete_paragraph(d, 'En Hati y Singh (2023) se destaca')
    replace(d, 'documentan aplicaciones exitosas de YOLO en detección de patologías foliares en cultivos '
               'de tomate, papa, manzana y banano, pero los reportes',
            'documentan aplicaciones de YOLO a la detección de enfermedades en cultivos como el tomate '
            'y la manzana, pero los reportes')
    set_paragraph(d, 'La tendencia actual hacia edge computing',
                  'Ejecutar la inferencia en el propio dispositivo evita depender de conectividad a la '
                  'nube, un requisito relevante en zonas rurales con cobertura limitada.')
    set_paragraph(d, 'Plataformas como Raspberry Pi 4',
                  'Plataformas como Raspberry Pi 4 o Jetson Nano son candidatas para ese despliegue; en '
                  'este trabajo no se midió el rendimiento en ellas. Esa motivación orientó la elección de '
                  'la variante nano de YOLO, la de menor tamaño de la familia.')
    replace(d, 'la calidad del particionamiento (train/valid/test) no siempre es auditada. La fuga de '
               'datos por presencia de imágenes casi-duplicadas entre particiones es un problema '
               'recurrente que sobreestima sistemáticamente las métricas reportadas (Kapoor & Narayanan, '
               '2023).',
            'la calidad del particionamiento en entrenamiento, validación y prueba no siempre se audita. '
            'Los duplicados repartidos entre particiones son una de las formas de fuga de datos que '
            'inflan las métricas reportadas (Kapoor & Narayanan, 2023).')
    set_paragraph(d, 'Las técnicas de perceptual hashing',
                  'Las funciones de hash perceptual permiten detectar imágenes perceptualmente similares; '
                  'Zauner (2010) evaluó varias de ellas, entre ellas el hash DCT de 64 bits de la '
                  'librería pHash.')

    # Data (ED-06, provenance, MangoDHDS record)
    set_paragraph(d, 'La mayor representación de la clase Saludable',
                  'El corpus está desbalanceado hacia la clase Saludable (Tabla 1). No se aplicó ninguna '
                  'corrección específica del desbalance: la aumentación es la configuración por defecto de '
                  'Ultralytics, igual para ambas clases.')
    set_paragraph(d, 'Procedencia de las imágenes.',
                  'Procedencia de las imágenes. La fuente no publica la procedencia de cada imagen. Según '
                  'los nombres de archivo, 432 de las 669 imágenes pertenecen a un contenedor nombrado como '
                  'vídeo (sakit_mp4); la auditoría visual de una muestra mostró que contiene fotografías '
                  'de escenas distintas, no una grabación continua (Sección 3.3). El conjunto se distribuye '
                  'bajo licencia CC BY 4.0; los derechos de cada imagen de origen no son verificables desde '
                  'el registro público.')
    replace(d, 'Se utilizó el conjunto MangoDHDS (Barhate et al., 2025), publicado en IEEE Dataport bajo '
               'licencia CC BY 4.0.',
            'Se utilizó el conjunto MangoDHDS (Barhate et al., 2025), en su versión 1 de Mendeley Data, '
            'bajo licencia CC BY 4.0.')

    # MangoDHDS audit (TASK-02: 41 byte-identical + 19 re-encodings; Zauner does not calibrate 5)
    replace(d, 'se identificaron 76 pares de imágenes casi-duplicadas distribuidas entre los splits con '
               'distancia de Hamming inferior a 5. La distribución detallada se presenta en la Sección '
               'Sección 4, Tabla 6.',
            'se identificaron 76 pares de imágenes casi duplicadas repartidas entre particiones con '
            'distancia de Hamming inferior a 5 (Tabla 6, Sección 4).')
    replace(d, 'El umbral τ=5 se adoptó como criterio conservador siguiendo los benchmarks reportados por '
               'Zauner sobre phash de 64 bits, donde distancias inferiores a 5 corresponden con alta '
               'probabilidad a contenido perceptualmente idéntico bajo transformaciones leves (recortes, '
               'recompresión, ajustes de color). Los 76 pares detectados fueron además inspeccionados '
               'visualmente por los autores para confirmar su condición de duplicados o casi-duplicados '
               'antes de ejecutar la regeneración. El conjunto resultante',
            'El umbral τ = 5 es una elección operativa; no procede de una calibración publicada para '
            'esta implementación. Una reejecución independiente reproduce exactamente los 76 pares: 41 '
            'son idénticos byte a byte y 19 más son recodificaciones a distancia 0. El conjunto resultante')
    replace(d, 'se valida re-ejecutando el detector de duplicados y obteniendo cero pares cross-split.',
            'se comprobó reejecutando el detector de duplicados: no se detectan pares repartidos entre '
            'particiones bajo el umbral.')

    # Model 1 provenance (REVIEW-09)
    replace(d, 'distribuida públicamente como parte del framework Ultralytics (Jocher et al., 2023) bajo '
               'el alias yolo26n.pt.',
            'distribuida por Ultralytics (Jocher et al., 2026). El reentrenamiento parte del checkpoint '
            'oficial yolo26n.pt de la release v8.4.0 (SHA-256 9b09cc8b…4fef, verificado contra el digest '
            'publicado) y usa Ultralytics 8.4.52; el run histórico registra la versión 8.4.39.')

    # Service and cascade (CLAIM-039, ED-16)
    set_paragraph(d, 'Sobre la arquitectura en cascada se implementó',
                  'El repositorio contiene dos prototipos separados. Un servicio web FastAPI ejecuta sólo '
                  'el Modelo 1 (detector binario). La cascada completa se ejecuta con el script de línea '
                  'de comandos del repositorio, que aplica el Modelo 2 a cada caja detectada por el Modelo '
                  '1, sea cual sea su clase, y marca como «Desconocido» un diagnóstico con confianza '
                  'inferior a 0,4. La integración de la cascada en el servicio web no está implementada.')
    set_paragraph(d, 'Figura 2. Arquitectura del servicio web.',
                  'Figura 2. Arquitectura prevista del servicio web. La versión implementada ejecuta sólo '
                  'el Modelo 1; la cascada completa se ejecuta por línea de comandos (Sección 3.6). Fuente: '
                  'elaboración propia.')
    set_paragraph(d, 'El servicio FastAPI se instrumentó',
                  'El servicio FastAPI implementado recibe una imagen, ejecuta el Modelo 1 y devuelve las '
                  'detecciones binarias. La cascada con el Modelo 2 se ejecuta desde la línea de comandos '
                  'sobre imagen, carpeta, vídeo o cámara. Ninguno de los dos prototipos se evaluó con '
                  'usuarios.')

    # Model 2 (REVIEW-14, ED-09; effective n)
    replace(d, 'La configuración detallada figura en la Tabla III.',
            'La configuración detallada figura en la Tabla 3.')
    replace(d, 'La evaluación se realizó sobre las 219 imágenes del split de test (libre de fuga con el '
               'entrenamiento).',
            'La evaluación se realizó sobre las 219 imágenes de la partición de prueba, en la que no se '
            'detecta contaminación entre particiones bajo el protocolo especificado (SHA-256 y pHash con '
            'Hamming < 5); esas 219 imágenes forman 203 grupos de similitud, que son la unidad de los '
            'intervalos [PENDIENTE: EXP-R03 e intervalos].')
    replace(d, 'ambas patologías presentan lesiones oscuras e irregulares en estadios tempranos,',
            'ambas patologías presentan lesiones oscuras e irregulares,')
    replace(d, 'patologías con síntomas visualmente similares en estadios tempranos.',
            'patologías con síntomas visualmente similares.')
    replace(d, 'tras la deduplicación. En el contexto agrícola',
            'tras la deduplicación. En el contexto agrícola')

    # Discussion and future work (ED-10, ED-11; Paulus does not support precocity)
    replace(d, 'La motivación para integrar profundidad en versiones futuras se sostiene en la evidencia '
               'previa revisada en la Sección Sección 2 de que el fenotipado 3D permite capturar '
               'deformaciones morfológicas tempranas (cambios de volumen, abolladuras, deformaciones del '
               'pedúnculo) anteriores a la aparición de síntomas cromáticos.',
            'La profundidad podría aportar rasgos geométricos (volumen, abolladuras, forma del '
            'pedúnculo) complementarios al color; que permita detectar la enfermedad antes que el RGB es '
            'una hipótesis por comprobar, no un resultado.')
    replace(d, 'El análisis tridimensional permitiría detectar deformaciones morfológicas tempranas previas '
               'a la aparición de síntomas visibles, complementando la información cromática RGB.',
            'El análisis tridimensional podría aportar información geométrica complementaria a la '
            'cromática.')
    replace(d, 'Como se discutió en la Sección Sección 4, estas patologías comparten manifestaciones '
               'visuales en estadios tempranos',
            'Como se discutió en la Sección 4, estas patologías comparten manifestaciones visuales')
    replace(d, 'Las dos limitaciones restantes son operativas: la saturación bajo iluminación ambiental '
               'intensa, y la latencia que se eleva por encima de los 5 segundos en hardware edge si se '
               'opera sin cuantización.',
            'Quedan dos limitaciones operativas: la saturación bajo iluminación ambiental intensa y la '
            'ausencia de mediciones en hardware de borde; la latencia en Raspberry Pi 4 no se midió.')
    replace(d, 'La publicación del protocolo de regeneración (perceptual hashing + union-find + '
               'estratificación) y los scripts asociados proporciona una herramienta reutilizable para '
               'auditar otros conjuntos de datos agrícolas similares.',
            'El protocolo de regeneración (hash perceptual, union-find y estratificación) y su código se '
            'publican para que pueda aplicarse a otros conjuntos.')
    replace(d, 'Primero, valida la práctica creciente de auditar la calidad del particionamiento antes de '
               'utilizar conjuntos públicos.',
            'Primero, muestra por qué conviene auditar el particionamiento antes de utilizar un conjunto '
            'público.')

    # Data availability and acknowledgements (TASK-08)
    replace(d, 'El procedimiento de deduplicación que genera MangoDHDS_clean se describe en la Sección '
               'Sección 3 y es reproducible con semilla fija.',
            'El procedimiento de deduplicación que genera MangoDHDS_clean se describe en la Sección 3 y '
            'es reproducible con semilla fija.')
    replace(d, 'el conjunto Mango Disease (Villa Bastidas, 2026)', 'el conjunto Mango Disease (DANNs '
            'Workspace, 2026)')
    replace(d, 'a Barhate et al. por publicar MangoDHDS bajo licencia CC BY 4.0 en IEEE Dataport',
            'a Barhate et al. por publicar MangoDHDS bajo licencia CC BY 4.0 en Mendeley Data')

    # Table 8: the Pi latency row (REVIEW-08)
    table = d.tables[7]
    for row in range(len(table.rows)):
        if table.cell(row, 0).text.startswith('Inferencia sin cuantización'):
            cell_text(d, 7, row, 0, 'Sin medición en hardware de borde')
            cell_text(d, 7, row, 1, 'Latencia en Raspberry Pi 4 desconocida')
            cell_text(d, 7, row, 2, 'Medir con el protocolo de TASK-06 cuando haya acceso al equipo')
    d.save(DOCX)
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8')) if log.is_file() else []
    entries.append({'pass': 1, 'script': 'provenance/commands/task09/revise_pass1.py',
                    'before_sha256': before, 'after_sha256': sha(DOCX)})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(entries[-1], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
