"""TASK-09 (audit B, B-09): the final disposition of every claim of the submitted manuscript.

Adds final_status, final_location and final_evidence to docs/research/claim_evidence_matrix.csv
without touching the 50 original rows or their audit columns (verify_first_phase.py counts them).
final_status: SUPPORTED (kept, with its evidence), CORRECTED (kept with a corrected value),
REPLACED (the old result gave way to a new, traced one), REFORMULATED (kept as a narrower or
hypothetical statement), QUALIFIED (kept with its stated limit), RETIRED (removed from the text),
PENDING_AUTHOR (depends on a decision of the authors). Locations refer to the manuscript after
pass 2f; evidence names committed repository paths. Rerunning rewrites the three final columns.
"""

import csv
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MATRIX = ROOT / 'docs/research/claim_evidence_matrix.csv'
NEW = ('final_status', 'final_location', 'final_evidence')
R01, V01, R02, R03 = ('experiments/model1/EXP-R01/selection_record.json',
                      'experiments/model1/EXP-V01/metrics_frozen.json',
                      'experiments/model1/EXP-R02/metrics.json;artifacts/metrics/model1_intervals.json',
                      'artifacts/metrics/model2_intervals.json;experiments/model2/EXP-R03/run_record.json')
FINAL = {
    'CLAIM-001': ('RETIRED', 'Título;Resumen;3.4', 'reports/editorial_claim_audit.csv (eficiencia retirada; REVIEW-10); 3.4 dice sólo que la variante nano es la del run histórico, sin comparar variantes (pasada 2e, R2-01)'),
    'CLAIM-002': ('RETIRED', 'Título;Resumen;1;7', 'Título y resumen hablan de detección visual automatizada; premisa temporal de la introducción retirada en la pasada 2d (auditoría B, B-01)'),
    'CLAIM-003': ('SUPPORTED', '3.1;3.6;Figura 1;Figura 2', 'src/cascade/runtime.py; la cascada se ejecuta por línea de comandos y el servicio FastAPI sólo ejecuta el Modelo 1'),
    'CLAIM-004': ('REPLACED', '3.2.1;Tabla 1', 'data/manifests/model1_clean_manifest.csv (partición por grupos: 439/113/117)'),
    'CLAIM-005': ('REPLACED', '3.2.1;Tabla 1', 'data/manifests/model1_clean_manifest.csv (Enfermo 526/30/26; Saludable 937/169/166)'),
    'CLAIM-006': ('RETIRED', '3.2.1', 'REVIEW-06; el texto describe el desbalance sin relacionarlo con la prevalencia'),
    'CLAIM-007': ('REFORMULATED', '3.2.1 (Procedencia de las imágenes)', 'Sólo se conserva lo observable: 432 nombres de archivo del contenedor sakit_mp4; el resto del desglose se retiró'),
    'CLAIM-008': ('QUALIFIED', '3.2.1;Disponibilidad de datos', 'El texto dice que los derechos de cada imagen de origen no son verificables desde el registro público'),
    'CLAIM-009': ('SUPPORTED', '3.2.2', 'manuscript/bibliography/references.json (MangoDHDS, Mendeley Data v1)'),
    'CLAIM-010': ('CORRECTED', '3.2.2;Referencias', 'manuscript/bibliography/references.json (Mendeley Data v1, DOI 10.17632/b4nrw5hyyc.1)'),
    'CLAIM-011': ('SUPPORTED', '3.3.2;Tabla 6', 'Reejecución independiente del detector de duplicados (76 pares) registrada en TASK-02'),
    'CLAIM-012': ('SUPPORTED', '3.3.2;4.2.1', '41 pares idénticos byte a byte y 19 recodificaciones a distancia 0; Hamming 0 no se presenta como igualdad binaria'),
    'CLAIM-013': ('REFORMULATED', '3.3.2', 'El umbral τ = 5 se declara elección operativa, sin calibración publicada'),
    'CLAIM-014': ('QUALIFIED', 'Resumen;3.3.1;3.3.2;4.2.1;4.2.3;7', 'Cero pares entre particiones bajo el protocolo especificado; no se afirma ausencia absoluta de fuga; MangoDHDS_clean es sólo el nombre del conjunto y «limpio» ya no se usa como veredicto (pasada 2e, R2-06)'),
    'CLAIM-015': ('SUPPORTED', '4.2.1', 'data/manifests/model2_frozen_manifest.csv (1064/217/219 y 1337 cluster_id distintos)'),
    'CLAIM-016': ('REPLACED', '3.4;Tabla 2', f'{R01}; experiments/model1/EXP-R01/v1/receipt.json (Ultralytics 8.4.52, 1×T4, 18,7 min)'),
    'CLAIM-017': ('REPLACED', '4.1.1;Tabla 4', f'{V01} (métricas del checkpoint elegido, no máximos por época)'),
    'CLAIM-018': ('REPLACED', 'Tabla 4', V01),
    'CLAIM-019': ('RETIRED', 'Tabla 4', 'Los máximos retrospectivos por época ya no se informan'),
    'CLAIM-020': ('RETIRED', 'Tabla 4', 'Se informa sólo el checkpoint seleccionado (época 91)'),
    'CLAIM-021': ('REPLACED', '4.1.1;Figura 3', 'experiments/model1/EXP-R01/v1/run/train/results.csv; sin afirmación de ausencia de sobreajuste'),
    'CLAIM-022': ('REPLACED', '4.1.2;Tabla 5', R02),
    'CLAIM-023': ('REPLACED', 'Tabla 5', R02),
    'CLAIM-024': ('REPLACED', 'Tabla 5', R02),
    'CLAIM-025': ('REPLACED', '4.1.3;Figura 4', 'experiments/model1/EXP-R02/metrics.json (detection_confusion)'),
    'CLAIM-026': ('QUALIFIED', '3.7;4.1.2;Resumen;7', 'configs/evaluation_frozen.json sellado antes de EXP-R02; provenance/test_access_log.csv; la prueba se declara evaluación interna retrospectiva (pasada 2d, B-05), también en 3.7 (pasada 2e, R2-03)'),
    'CLAIM-027': ('REPLACED', '4.1.5', 'reports/benchmark_report.md; artifacts/metrics/benchmark_raw.csv'),
    'CLAIM-028': ('RETIRED', '4.1.5;6.1;Tabla 8', 'Raspberry Pi 4 BLOCKED_BY_HARDWARE; sólo se declara que no se midió'),
    'CLAIM-029': ('RETIRED', '6.1;Tabla 8', 'Ídem CLAIM-028'),
    'CLAIM-030': ('REPLACED', '4.1.5', 'reports/benchmark_report.md (cascada y extremo a extremo con límites definidos)'),
    'CLAIM-031': ('QUALIFIED', '3.5;6.1', 'Las etiquetas del corpus son de imagen completa (en formato YOLO, cajas cls 0.5 0.5 1.0 1.0) sin atribuirlas a anotaciones originales (pasada 2d; 6.1 en la pasada 2e); el Modelo 2 se describe como clasificador'),
    'CLAIM-032': ('SUPPORTED', '3.5;Tabla 3;4.2.2', 'Registro de entrenamiento de ART-002 (train_args); entrenamiento histórico, no repetido'),
    'CLAIM-033': ('SUPPORTED', '4.2.3;Tabla 7;Resumen;7', R03),
    'CLAIM-034': ('CORRECTED', '4.2.3;Tabla 7;Resumen;7', f'{R03} (macro-F1 0,909, redondeo directo)'),
    'CLAIM-035': ('CORRECTED', 'Tabla 7', f'{R03} (F1 de Cancro bacteriano 0,832 corregido a 0,831)'),
    'CLAIM-036': ('SUPPORTED', 'Tabla 7', R03),
    'CLAIM-037': ('REFORMULATED', '4.2.3;6.1;Tabla 8', 'experiments/model2/EXP-R03/predictions.jsonl (6 + 6 errores cruzados); la causa se declara hipótesis no ensayada (pasada 2d, B-03)'),
    'CLAIM-038': ('REFORMULATED', '4.1.4;4.2.4;Figuras 5 y 7', 'Muestras al azar con semilla 42, no elegidas por su resultado; Figura 7 ilustrativa, sin verdad de terreno de enfermedad'),
    'CLAIM-039': ('RETIRED', '3.6;4.3;7', 'El servicio FastAPI sólo ejecuta el Modelo 1; la conclusión se corrigió en la pasada 2d'),
    'CLAIM-040': ('QUALIFIED', '4.3', 'Implementación observada en el código; ninguno de los prototipos se evaluó con usuarios'),
    'CLAIM-041': ('CORRECTED', '5.2', 'Cinco diagnósticos (cuatro enfermedades y Saludable) y ausencia de corpus limitada a los conjuntos revisados (pasada 2d)'),
    'CLAIM-042': ('SUPPORTED', 'Resumen;3.6;5.3;Disponibilidad de datos', 'Repositorio público https://github.com/JUNIORRDSR/deteccion-enfermedades-mango-cascada (versión 1.0.0, AGPL-3.0) con el código, los manifiestos, los pesos de los dos modelos y la evidencia, citado como Villa Bastidas et al. (2026) (pasada 2f)'),
    'CLAIM-043': ('REFORMULATED', '5.4;6.2;7', 'Detectar antes que el RGB se declara hipótesis por comprobar; la conclusión deja RGB-D y Raspberry Pi 4 como trabajo futuro no evaluado, sin efecto de consolidación ni de sostenibilidad (pasada 2e, R2-02)'),
    'CLAIM-044': ('SUPPORTED', '6.1;7', 'Ninguna imagen del detector procede de los cultivos objetivo'),
    'CLAIM-045': ('REFORMULATED', '7', 'El servicio web local se describe como diseño («pensado para»), sin afirmar funcionamiento sin conexión probado'),
    'CLAIM-046': ('QUALIFIED', 'Disponibilidad de datos', 'manuscript/bibliography/references.json (villabastidas2026, CORRECTED); el conjunto no interviene en ningún resultado'),
    'CLAIM-047': ('CORRECTED', '1', 'DANE (2024): 14,4 % de la población ocupada (reports/bibliography_audit.csv)'),
    'CLAIM-048': ('CORRECTED', '1', 'Savary et al. (2019): 17 % a 30 % según el cultivo (reports/bibliography_audit.csv)'),
    'CLAIM-049': ('REFORMULATED', '1', 'La tardanza de la inspección visual se retiró (pasada 2d, B-01); la ventaja del aprendizaje profundo se conserva atribuida a Liu & Wang (2021), sin «consistentemente»'),
    'CLAIM-050': ('REPLACED', '4.1.2;5.1', f'{V01}; {R02} (misma selección de checkpoint en validación y prueba)'),
}


def main() -> int:
    raw = MATRIX.read_bytes()
    newline = '\r\n' if b'\r\n' in raw else '\n'
    rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8'))))
    fields = [f for f in rows[0] if f not in NEW]
    if [r['claim_id'] for r in rows] != sorted(FINAL):
        raise SystemExit('the dispositions do not cover exactly the claims of the matrix')
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=fields + list(NEW), lineterminator=newline)
    writer.writeheader()
    for row in rows:
        writer.writerow({**row, **dict(zip(NEW, FINAL[row['claim_id']]))})
    MATRIX.write_bytes(out.getvalue().encode('utf-8'))
    counts = {}
    for status, _, _ in FINAL.values():
        counts[status] = counts.get(status, 0) + 1
    print(counts)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
