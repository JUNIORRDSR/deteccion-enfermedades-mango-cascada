"""Close the first-phase handoff only after a successful documentary verification."""
from pathlib import Path
import csv, datetime, hashlib, json, re

W=Path(__file__).resolve().parents[2]
r=json.loads((W/'reports/first_phase_verification.json').read_text(encoding='utf-8'))
assert r['status']=='PASS_FIRST_PHASE_DOCUMENTARY' and not r['errors'], 'Full verification must pass first'
checks=r['checks'];legacy=checks['legacy'];docs=checks['documentary']
assert not legacy['changed'] and not legacy['missing'] and not legacy['new_eligible_paths']
assert all(row['matches_initial'] for row in checks['git'])
review=(W/'reports/research_independent_rereview.md').read_text(encoding='utf-8')
assert 'no se identifican hallazgos HIGH o MEDIUM de diseño pendientes' in review
for rel in ['docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md',
            'docs/superpowers/plans/2026-09-17-albus26-major-revision.md',
            'reports/first_phase_executive_report.md']:
    digest=hashlib.sha256((W/rel).read_bytes()).hexdigest()
    assert digest in review, 'Document changed after independent review: '+rel

text=f'''# Validación de primera fase — ALBUS26-116

**Estado de entrega: READY_FOR_REVIEW.** Sólo investigación documental, SPEC y plan. La Major Revision científica completa **NO está DONE**. No se ejecutaron entrenamiento, inferencia, pHash nuevo, particiones nuevas, benchmarks ni edición científica del manuscrito.

La comprobación completa terminó con `PASS_FIRST_PHASE_DOCUMENTARY`, exit code **0**, a partir de la ejecución iniciada en `{r['checked_at_utc']}`. Evidencia legible por máquina: `reports/first_phase_verification.json`. El comando ejecutado fue:

```powershell
& 'C:/Users/junio/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/provenance/commands/verify_first_phase.py'
```

## Resultados comprobados

|Comprobación|Resultado|Límite|
|---|---|---|
|Fuentes originales|{legacy['files']:,} archivos y {legacy['bytes']:,} bytes; 0 hashes/tamaños alterados, 0 ausentes, 0 archivos elegibles añadidos|Excluye .git, .venv, node_modules, __pycache__ y el workspace nuevo; no certificación universal del disco|
|Fechas de modificación|{len(legacy['mtime_changes'])} discrepancias frente al baseline|Las fechas no prueban cuándo se hizo un experimento|
|Git|8 comandos con exit 0 y resultados idénticos al estado inicial|Semillero ya tenía cambios y untracked; no se atribuyen a esta tarea|
|Matrices y cobertura|18 REVIEW, 50 CLAIM, 9 EXP, 100 ART, 3 DER y 10 TASK; IDs únicos y referencias comprobadas|Resolución de enlaces no basta para soporte científico; revisión semántica documentada por separado|
|Reproducción histórica|Los 9 EXP y 100 ART conservan reproduced=NO|Leer CSV o metadata no reproduce un experimento|
|Inventario de imágenes|7.016 archivos enlazados a hashes SRC; M1: 669 imágenes, 1.854 cajas; test: 33 imágenes, 99 cajas, 13 Enfermo|Representaciones y copias no son observaciones independientes|
|Duplicados binarios cross-split|DATA-001: 0; DATA-003: 41 pares; DATA-004/005: 0|No prueba independencia temporal, perceptual ni biológica|
|CSV M2 existente|199/219; macro F1 0,9094733437 y Cancro 0,8314606742; redondeo directo 0,909/0,831|Sólo contraste aritmético; no cambia las métricas publicadas ni valida el test|
|Genealogía fresca|PDF 16 páginas; 33.468 caracteres normalizados idénticos al DOCX|No demuestra igualdad de maquetación ni sustituye la confirmación de envío del usuario|
|Alcance de primera fase|src, tests, experiments y manuscrito de revisión sin archivos de implementación|Comandos científicos del plan son futuros|

SHA256 del baseline preservado: `{legacy['baseline_sha256']}`. SHA256 del texto normalizado PDF/DOCX: `{checks['genealogy']['sha256']}`.

Se ejecutaron y registraron `git -C <repo> status --short`, `branch --show-current`, `rev-parse HEAD` y `worktree list --porcelain` para ambos repositorios. HEAD Mango-vision: `e7e59d1bce74a7ae12674f5b6068068681e691ce`; HEAD SemilleroTI-Mangos: `98614804dd967e19a77af9fc58c27364d2e43bc9`. Ambos siguen en main, sin worktree nuevo. La raíz contenedora no es un repositorio Git; el exit 128 inicial de esa raíz está documentado y no es un fallo de los repositorios internos.

## Revisiones realizadas y fallos conservados

Self-review de SPEC y plan: `reports/spec_self_review.md` y `reports/plan_self_review.md`. Revisión independiente inicial: `reports/research_independent_review.md`; relectura de correcciones: `reports/research_independent_rereview.md`. Los seis hallazgos iniciales y los detalles posteriores de IDs M2, rutas y redacción se resolvieron documentalmente. No quedan hallazgos HIGH/MEDIUM de diseño pendientes en esa relectura. La existencia de este informe cierra su último pendiente de entrega; los enlaces locales se comprueban en `reports/delivery_check.json`.

El primer intento del verificador falló porque suponía que ART-095–100 eran fuentes legacy; son productos derivados de arqueología. El segundo falló por interpretar una columna de nombres de fila que no existe en la matriz CSV. Se corrigieron esos supuestos en el verificador, sin cambiar el CSV, los artefactos ni las fuentes. Se preservan `reports/first_phase_verification_attempt1.json` y `reports/first_phase_verification_attempt2.json`; ambos habían verificado hashes/Git. La extracción fresca y aritmética se comprobaron luego por separado y la ejecución completa actual pasó. Las interrupciones por límite de uso tampoco son experimentos científicos fallidos.

## Gates

|Gate|Estado actual|
|---|---|
|A — repositorio entendido|SATISFIED_DOCUMENTARY: inventario, genealogía, requisitos y registros presentes; huecos explícitos|
|B — diseño aprobado|READY_FOR_REVIEW; aprobación humana pendiente|
|C — plan aprobado|READY_FOR_REVIEW; cobertura y self-review completos; aprobación humana pendiente|
|D — datos validados|NOT_EXECUTED: falta auditoría formal de similitud/origen y freeze aprobado|
|E — experimentos validados|NOT_EXECUTED: no nuevas ejecuciones; procedencia histórica incompleta|
|F — claims validados|NOT_SATISFIED: matriz inicial conserva UNVERIFIED/UNSUPPORTED explícitos|
|G — manuscrito validado|NOT_EXECUTED: sin edición ni build final de revisión|
|H — respuesta validada|NOT_SATISFIED: borrador de planificación, no carta para enviar|
|I — revisión adversarial final|NOT_EXECUTED: la revisión independiente actual es del diseño, no del manuscrito final|

Persisten las dependencias de GT conjunto independiente, hardware Pi, origen de secuencias, entorno/base M1 históricos y bibliografía completa. Las 23 referencias todavía no están auditadas en su totalidad. La compatibilidad del entorno reconstruido tampoco se ha probado. Son límites explícitos de la propuesta, no resultados favorables asumidos.

La aprobación conjunta de SPEC y plan, exigida en los apartados 41–42 de la solicitud del usuario, es el siguiente paso. Hasta recibirla no se ejecuta TASK-01.
'''
(W/'docs/final_validation_report.md').write_text(text,encoding='utf-8')
p=W/'docs/research/research_charter.md'
text=p.read_text(encoding='utf-8').replace('- [ ] verification-before-completion: evidencia fresca de artefactos y preservación de legacy.',
    '- [x] verification-before-completion: comprobación documental completa con exit 0; evidencia y límites en docs/final_validation_report.md.')
p.write_text(text,encoding='utf-8')

executive=(W/'reports/first_phase_executive_report.md').read_text(encoding='utf-8')
links=re.findall(r'\]\(<(C:/[^>]+)>\)',executive)
assert all(Path(path).exists() for path in links), 'Missing executive delivery link'
delivery={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'status':'READY_FOR_REVIEW','executive_local_links':len(links),'all_links_exist':True,
          'independently_reviewed_spec_plan_executive_hashes_unchanged':True,
          'first_phase_verification_sha256':hashlib.sha256((W/'reports/first_phase_verification.json').read_bytes()).hexdigest(),
          'final_validation_report_exists':True,'scientific_revision_done':False,'human_approval':'PENDING'}
(W/'reports/delivery_check.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf-8')
paths=sorted(set(docs['hashes'])|{'docs/final_validation_report.md','reports/research_independent_rereview.md','reports/delivery_check.json',
                              'reports/first_phase_verification.json','provenance/derived_evidence_registry.csv',
                              'provenance/experiment_registry.csv','provenance/artifact_registry.csv'})
with (W/'provenance/first_phase_delivery_manifest.csv').open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['path','sha256','size_bytes']);writer.writeheader()
    for path in paths:
        b=(W/path).read_bytes();writer.writerow(dict(path=path,sha256=hashlib.sha256(b).hexdigest(),size_bytes=len(b)))
print(json.dumps(delivery,ensure_ascii=False))
