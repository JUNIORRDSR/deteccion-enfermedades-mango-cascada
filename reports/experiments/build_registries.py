"""Build provenance registers from inspected legacy files; no model execution."""
from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROV = ROOT / 'ALBUS26_major_revision/provenance'
with (PROV / 'source_manifest.csv').open(encoding='utf-8-sig') as f:
    sources = {r['relative_path'].replace('\\', '/'): r for r in csv.DictReader(f)}
FIELDS = 'experiment_id model purpose date source_code git_commit dataset dataset_manifest split seed base_checkpoint checkpoint config python ultralytics pytorch cuda hardware command results_csv metrics_artifacts figures published_values reproduced confidence notes status'.split()

def exp(n, **values):
    return dict(dict.fromkeys(FIELDS, 'UNVERIFIED'), experiment_id=f'EXP-{n:03}', reproduced='NO', **values)

det = 'SemilleroTI-Mangos/models/best.pt'
cls = 'Mango-vision/models/clasificador_enfermedad.pt'
cls2 = 'SemilleroTI-Mangos/models/clasificador_enfermedad.pt'
det_csv = 'SemilleroTI-Mangos/docs/Yolo26n-model-docs/Entrenamiento-1/resultados/results.csv'
det_args = 'SemilleroTI-Mangos/docs/Yolo26n-model-docs/Entrenamiento-1/args.yaml'
train_log = 'Articulo/reports/train_cls_log.txt'
det_data = 'SemilleroTI-Mangos/docs/MangosDataset'
cls_data = 'Mango-vision/DatasetMango_YOLO_cls'
manifest_note = 'UNVERIFIED historical run manifest; provenance/source_manifest.csv records current files only'
det_git = 'UNVERIFIED execution commit; artifact first tracked in e1477b53d7db3eede52f32904c07242153a65e8d (2026-04-20)'
rows = [
    exp(1, model='Modelo 1 / YOLO26n / detect', purpose='Entrenamiento binario + validación por época',
        date='2026-04-18T22:39:04.577835 (checkpoint metadata; timezone UNVERIFIED)',
        source_code='UNVERIFIED training notebook/script absent; args.yaml and checkpoint train_args retained', git_commit=det_git,
        dataset='mangoUnhealty v2 via Kaggle /kaggle/input/datasets/jairoall/mangodataset/data.yaml; local '+det_data,
        dataset_manifest=manifest_note, split='train=502; valid=134; test=33 (local source audit; training manifest UNVERIFIED)',
        seed='0', base_checkpoint='yolo26n.pt (train_args; source checkpoint/hash UNVERIFIED)', checkpoint=det,
        config=det_args+'; epochs=150, batch=16, imgsz=640, patience=100, device=0,1, optimizer=auto, deterministic=true',
        ultralytics='8.4.39 (checkpoint)', hardware='device=0,1 verified metadata; 2 x NVIDIA T4 / Kaggle claimed by PDF, hardware log UNVERIFIED',
        command='UNVERIFIED exact historical invocation', results_csv=det_csv,
        metrics_artifacts='checkpoint train_metrics and train_results (safe static extraction in reports/experiments/checkpoint_static_metadata.json)',
        figures='Articulo/figs/fig3_curvas.png; SemilleroTI-Mangos/docs/Yolo26n-model-docs/Entrenamiento-1/Evaluacion/',
        published_values='PDF Table 4: peak mAP50=.9317 ep95; peak mAP50-95=.8048 ep137; P=.9473 ep101; R=.8731 ep88 (excludes ep1 silently); last .9098/.9201/.8483',
        confidence='HIGH artifact identity/config/history; MEDIUM run provenance; no reproduction',
        notes='150 rows; 1281.61 seconds in CSV. best.pt train_metrics mAP50=.91607, mAP50-95=.80478 match ep137; peak .93174 ep95 is not best.pt validation mAP50. Checkpoint epoch=-1 after stripping; match ep137 is an inference. Python/PyTorch/CUDA and actual optimizer unresolved.', status='EXISTING_RUN_WITH_ARTIFACTS'),
    exp(2, model='Modelo 1 / YOLO26n / detect', purpose='Evaluación interna test por Ultralytics AP y P/R/F1',
        source_code='Articulo/scripts/evaluate_detector_test.py:23-86', git_commit='UNVERIFIED; Articulo is outside nested Git repositories',
        dataset=det_data, dataset_manifest=manifest_note, split='test; 33 images; 99 GT instances (13 Enfermo, 86 Saludable)',
        checkpoint=det, config='imgsz=640; split=test; conf=.001; iou=.6; plots=False; device not specified in model.val',
        command='UNVERIFIED execution log; corresponding source: python Articulo/scripts/evaluate_detector_test.py (not run in this audit)',
        metrics_artifacts='Articulo/reports/metrics_test_global.csv; Articulo/reports/metrics_test_per_class.csv',
        published_values='PDF Table 5: mAP50=.845; mAP50-95=.784; macro P=.884; R=.737; Enfermo P=.804 R=.846 F1=.825',
        confidence='HIGH correspondence CSV/published values; MEDIUM association with current weights/source',
        notes='CSV records no checkpoint hash/version/run date/predictions. Same filename in source is not proof of weight bytes at evaluation. P/R from Ultralytics results do not represent fixed deployment conf=.5/.7.', status='EXISTING_METRICS_WITH_INCOMPLETE_LINEAGE'),
    exp(3, model='Modelo 1 / YOLO26n / detect', purpose='Matriz de confusión por matching greedy de IoU y umbral fijo',
        source_code='Articulo/scripts/evaluate_detector_test.py:88-222', git_commit='UNVERIFIED; Articulo outside nested Git repositories',
        dataset=det_data, dataset_manifest=manifest_note, split='test; 33 images; 99 GT instances', checkpoint=det,
        config='predict conf=.25; iou=.6; imgsz=640; one-to-one greedy descending IoU; match IoU>=.5, class-agnostic matching',
        command='UNVERIFIED execution log; second block of evaluate_detector_test.py',
        metrics_artifacts='Articulo/reports/confusion_matrix_raw.csv; Articulo/reports/confusion_matrix_metrics.csv',
        figures='Articulo/figs/fig5_confusion_matrix.png; .pdf',
        published_values='PDF Figure 4: [[11,1,1],[3,61,22],[4,13,0]]; Enfermo correct 11/13; Saludable undetected 22/86',
        confidence='HIGH arithmetic consistency; MEDIUM experimental lineage',
        notes='Raw matrix yields Enfermo P=.611111 R=.846154 F1=.709677; Saludable P=.813333 R=.709302 F1=.757764. These differ legitimately from EXP-002 because operating threshold/protocol differ; paper must separate protocols. No per-image predictions stored.', status='EXISTING_METRICS_WITH_INCOMPLETE_LINEAGE'),
    exp(4, model='Modelo 2 / YOLO11n-cls / classify', purpose='Entrenamiento clasificación cinco clases y early stopping',
        date='2026-05-24T17:00:24.164716 (checkpoint metadata; timezone UNVERIFIED)',
        source_code='Mango-vision/src/training/train_cls.py; src/training/make_cls_layout.py; src/utils/config.py',
        git_commit='UNVERIFIED execution commit; train_cls.py tracked at e9ac0f45057fc131c00737b6c90fd3b3fa05dc06; current HEAD e7e59d1bce74a7ae12674f5b6068068681e691ce; model ignored/untracked',
        dataset=cls_data+' (copy/layout from DatasetMango_YOLO_clean)', dataset_manifest=manifest_note,
        split='train=1064; val=217; test=219 (log); five classes', seed='42',
        base_checkpoint='Mango-vision/yolo11n-cls.pt; sha256 c62d41bf9625777760018bf914d2e6cd472420ccd01706d97a61cb6c82502bd7 (present copy; runtime byte linkage UNVERIFIED)',
        checkpoint=cls+'; byte-identical copy '+cls2,
        config='epochs=50 requested; 27 completed; best ep12 per log; batch=32; imgsz=224; patience=15; optimizer=AdamW(lr=.001111,momentum=.9) per log',
        python='3.13.13 (log)', ultralytics='8.4.52 (log/checkpoint)', pytorch='2.12.0+cpu (log)', cuda='NOT_USED (device=cpu)',
        hardware='AMD Ryzen 5 7520U with Radeon Graphics; CPU (log); OS version UNVERIFIED',
        command='UNVERIFIED exact shell; source-equivalent inferred: python src/training/train_cls.py --epochs 50 --batch 32 --imgsz 224 --device cpu --name train_cls_50e',
        results_csv='UNVERIFIED original external C:/WorkSpace Vs Code/Mango-vision/runs/classify/train_cls_50e/results.csv; embedded 27-row history transcribed to reports/experiments/Mango-vision_clasificador_enfermedad_embedded_train_results.csv',
        metrics_artifacts=train_log+'; checkpoint train_metrics/train_results',
        published_values='PDF §4.2.2: 27 epochs, best12, val top1=.935, 24min CPU; all supported by log/history within rounding',
        confidence='HIGH log/checkpoint correspondence; MEDIUM dataset historical identity',
        notes='Log 0.396h; history1424.05s. Both final classifier copies sha256 e277717e6ca9d7f308d22697550a5a4e80613929acb68eeb790f3304ebfdb08e. Kaggle notebooks have no execution outputs and do not establish a GPU run.', status='EXISTING_RUN_WITH_ARTIFACTS'),
    exp(5, model='Modelo 2 / YOLO11n-cls / classify', purpose='Evaluación interna test sobre imágenes completas',
        source_code='Articulo/scripts/evaluate_classifier.py:18-144', git_commit='UNVERIFIED; Articulo outside nested Git repositories',
        dataset=cls_data, dataset_manifest=manifest_note, split='test; 219 images; supports46/45/44/42/42 in alphabetical class order',
        checkpoint='UNVERIFIED exact historical chosen path; source fallback order: runs/classify/train_cls_50e/weights/best.pt -> '+cls+' -> '+cls2,
        config='imgsz=224; device=cpu; top1; sorted class-folder names; no confidence rejection', hardware='CPU requested; actual CPU/OS UNVERIFIED',
        command='UNVERIFIED execution log; corresponding source python Articulo/scripts/evaluate_classifier.py',
        metrics_artifacts='Articulo/reports/metrics_classifier_test.csv; Articulo/reports/confusion_matrix_cls.csv',
        figures='Articulo/figs/fig6_confusion_cls.png; .pdf', published_values='PDF Table7: top1=.909; macro F1=.910; cross-confusion Cancro/Costras 6+6',
        confidence='HIGH arithmetic/CSV consistency; MEDIUM weight/input lineage',
        notes='Matrix gives 199/219=.908675799 accuracy and exact macroF1=.909473343667..., which rounds .909 at 3 decimals. Stored 4dp macroF1=.9095 rounds again to .910: double-rounding explains published .910. No model metrics reproduced; no CSV with per-image predictions.', status='EXISTING_METRICS_WITH_INCOMPLETE_LINEAGE'),
    exp(6, model='Modelo 1 / YOLO26n / detect', purpose='Galería cualitativa de 9 imágenes del test detector',
        source_code='Articulo/figs/fig4_test_inference.py', git_commit='UNVERIFIED; Articulo outside nested Git repositories',
        dataset=det_data, dataset_manifest=manifest_note, split='test sample9', seed='42', checkpoint=det,
        config='sorted jpg/png; random.sample; conf=.5; iou=.5; imgsz=640; cvtColor BGR->RGB before passing ndarray to predict',
        command='UNVERIFIED historical invocation; corresponding source python Articulo/figs/fig4_test_inference.py',
        figures='Articulo/figs/fig4_test_inference.png; .pdf', published_values='PDF Figure5 qualitative gallery',
        confidence='MEDIUM source/figure association; no per-image output provenance',
        notes='Source calls sample stratified but no class strata implemented; random sample. Input channel conversion differs from detector test/cascade scripts (BGR); pipeline parity requires explicit check in future.', status='EXISTING_QUALITATIVE_ARTIFACT'),
    exp(7, model='Modelo1 YOLO26n -> Modelo2 YOLO11n-cls', purpose='Galería cualitativa de cascada sobre 9 escenas',
        source_code='Articulo/figs/fig7_cascade_demo.py; SemilleroTI-Mangos/core/cascade.py; run_cascade.py',
        git_commit='UNVERIFIED; core/cascade.py and run_cascade.py are untracked; Articulo outside nested Git repositories',
        dataset=det_data, dataset_manifest=manifest_note, split='test sample9', seed='7', checkpoint=det+' + '+cls2,
        config='sorted jpg; shuffle; first9; conf_det=.5; conf_cls=.35 (gallery override); iou_det=.5; imgsz_det640; imgsz_cls224; CPU; classify only Enfermo',
        command='UNVERIFIED historical invocation; corresponding source python Articulo/figs/fig7_cascade_demo.py',
        figures='Articulo/figs/fig7_cascade_demo.png; .pdf; Articulo/figs/cascade_demo/*_annot.jpg (exact generation run UNVERIFIED)',
        published_values='PDF Figure7; 0.18-0.6s end-to-end claimed (§4.2.4)', confidence='MEDIUM qualitative artifacts; LOW timing claim',
        notes='No multiclass GT on detector test; qualitative predictions cannot establish disease accuracy. predict timer excludes annotate/load/save/API. Healthy detections bypass classifier. No latency CSV or repeated benchmark found. Current API does not call cascade.', status='EXISTING_QUALITATIVE_ARTIFACT_TIMING_UNVERIFIED'),
    exp(8, model='Modelo 1 / YOLO26n / detect', purpose='Afirmación de latencia media CPU 145ms (sin benchmark recuperado)',
        source_code='UNVERIFIED measurement script; PDF §4.1.5 latency paragraph',
        config='640x640 claimed; batch/threads/warmup/repetitions/scope UNVERIFIED',
        hardware='AMD Ryzen 5 7520U Windows11 claimed; inference measurement log UNVERIFIED',
        published_values='145ms promedio CPU', confidence='LOW',
        notes='CLAIM ONLY: no benchmark rows, timing distribution, image selection manifest or checkpoint hash linked to timing; not established as a recovered execution.', status='CLAIM_ONLY_UNVERIFIED'),
    exp(9, model='Modelo 1 / YOLO26n / edge', purpose='Afirmaciones de latencia RaspberryPi4 sin cuantización (sin benchmark recuperado)',
        source_code='UNVERIFIED measurement script; PDF latency paragraph and §6.1/Table8',
        config='No quantization claimed; Table8 mentions832x832; earlier latency paragraph640x640; run configs UNVERIFIED',
        hardware='RaspberryPi4 ARM Cortex-A72 claimed; hardware/runtime capture UNVERIFIED',
        published_values='PDF: <5s in latency paragraph; >5s in limitations; Table8 832x832', confidence='LOW',
        notes='CLAIM ONLY; no recovered benchmark. Different resolution/hardware protocols could explain differences but cannot be assumed. 145ms CPU and0.18-.6s cascade are also distinct scopes, not interchangeable measurements.', status='CLAIM_ONLY_CONTRADICTORY_UNVERIFIED'),
]
with (PROV / 'experiment_registry.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, FIELDS); writer.writeheader(); writer.writerows(rows)

artifacts = []
def artifact(path, kind, experiments, relation, note=''):
    absolute = ROOT / path
    source = sources.get(path, {})
    if not absolute.is_file():
        return
    digest = source.get('sha256') or hashlib.sha256(absolute.read_bytes()).hexdigest()
    artifacts.append(dict(artifact_id=f'ART-{len(artifacts)+1:03}', source_id=source.get('source_id','DERIVED_THIS_AUDIT'),
                          path=path, sha256=digest, size_bytes=absolute.stat().st_size, artifact_type=kind,
                          experiment_ids=experiments, relation=relation, notes=note, reproduced='NO'))

artifact(det,'checkpoint','EXP-001;EXP-002;EXP-003;EXP-006;EXP-007','trained detector / evaluation reference','Metadata read safely; actual evaluation bytes UNVERIFIED')
artifact(cls,'checkpoint','EXP-004;EXP-005','trained classifier / evaluation fallback','Same bytes as ART-003')
artifact(cls2,'checkpoint','EXP-004;EXP-005;EXP-007','classifier deployment copy','Untracked; same bytes as ART-002')
artifact('Mango-vision/yolo11n-cls.pt','base checkpoint','EXP-004','candidate pretrained input','ImageNet base metadata; historic byte linkage UNVERIFIED')
artifact(det_args,'config','EXP-001','saved run arguments')
artifact(det_csv,'training history','EXP-001','saved epoch metrics; source of Fig3')
artifact(train_log,'training log','EXP-004','environment/config/progress/early stop record')
for name, ex in [('metrics_test_global.csv','EXP-002'),('metrics_test_per_class.csv','EXP-002'),('confusion_matrix_raw.csv','EXP-003'),('confusion_matrix_metrics.csv','EXP-003'),('metrics_classifier_test.csv','EXP-005'),('confusion_matrix_cls.csv','EXP-005')]:
    artifact('Articulo/reports/'+name,'saved metrics',ex,'existing aggregate metric evidence; not regenerated')
for stem, ex in [('fig3_curvas','EXP-001'),('fig4_test_inference','EXP-006'),('fig5_confusion_matrix','EXP-003'),('fig6_confusion_cls','EXP-005'),('fig7_cascade_demo','EXP-007')]:
    for suffix in ['.png','.pdf','.py']:
        artifact('Articulo/figs/'+stem+suffix,'source code' if suffix=='.py' else 'figure',ex,'figure generation source' if suffix=='.py' else 'existing figure; no regeneration')
for path, ex in [('Articulo/scripts/evaluate_detector_test.py','EXP-002;EXP-003'),('Articulo/scripts/evaluate_classifier.py','EXP-005'),('Mango-vision/src/training/train_cls.py','EXP-004'),('Mango-vision/src/training/make_cls_layout.py','EXP-004'),('Mango-vision/src/utils/config.py','EXP-004'),('SemilleroTI-Mangos/core/cascade.py','EXP-007'),('SemilleroTI-Mangos/run_cascade.py','EXP-007')]:
    artifact(path,'source code',ex,'current source; no proof of historical execution commit')
for path in ['SemilleroTI-Mangos/core/vision.py','SemilleroTI-Mangos/core/config.py','SemilleroTI-Mangos/api/main.py','SemilleroTI-Mangos/api/routers/inference.py','SemilleroTI-Mangos/api/routers/history.py','SemilleroTI-Mangos/static/script.js']:
    artifact(path,'API implementation','EXP-007','counterevidence to claimed cascade integration; binary inference only')
for path in ['Mango-vision/src/training/train_det_generic.py','Mango-vision/src/inference/infer_cascade.py','Mango-vision/src/evaluation/evaluate_cls.py','Mango-vision/src/evaluation/evaluate_det.py']:
    artifact(path,'alternate pipeline source','NONE_EXECUTION_UNVERIFIED','notebook/scaffold source; different detector configuration from EXP-001')
for path in sorted((ROOT / 'Articulo/figs/cascade_demo').glob('*_annot.jpg')):
    artifact(path.relative_to(ROOT).as_posix(),'qualitative annotated image','EXP-007','existing CLI-like output; precise invocation/date UNVERIFIED')
for path in sorted((ROOT / 'SemilleroTI-Mangos/docs/Yolo26n-model-docs/Entrenamiento-1/Evaluacion').glob('*.png')):
    artifact(path.relative_to(ROOT).as_posix(),'training figure','EXP-001','existing Ultralytics figure')
for path in list((ROOT / 'Mango-vision/notebooks').glob('*.ipynb'))+[ROOT/'Articulo/notebooks/train_cls_kaggle.ipynb']:
    artifact(path.relative_to(ROOT).as_posix(),'notebook template','NONE_EXECUTION_UNVERIFIED','all code execution_count=null and outputs=[]; not a recovered experiment')
for path in ['requirements.txt','Mango-vision/requirements.txt','SemilleroTI-Mangos/requirements.txt']:
    artifact(path,'dependency requirements','EXP-001;EXP-002;EXP-003;EXP-004;EXP-005;EXP-006;EXP-007','minimum constraints, not historical exact environment')
for path in [det_data+'/data.yaml',cls_data.replace('_cls','_clean')+'/data.yaml']:
    artifact(path,'dataset config','EXP-001;EXP-004','current dataset descriptor, not run manifest')
artifact('Articulo_Mango_ALBUS.pdf','submitted candidate','EXP-001;EXP-002;EXP-003;EXP-004;EXP-005;EXP-006;EXP-007;EXP-008;EXP-009','source of published claims; submitted version identity pending editorial evidence')
for path in OUT.glob('*'):
    if path.is_file() and path.suffix in {'.json','.csv'}:
        artifact(path.relative_to(ROOT).as_posix(),'static extraction/check','EXP-001;EXP-004;EXP-005','derived in audit; transcription/arithmetic only, no model execution')
with (PROV / 'artifact_registry.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f,list(artifacts[0])); writer.writeheader(); writer.writerows(artifacts)
assert len({r['experiment_id'] for r in rows}) == len(rows)
assert all(r['reproduced'] == 'NO' and all(r[k] for k in FIELDS) for r in rows)
assert artifacts[1]['sha256'] == artifacts[2]['sha256']
print(f'{len(rows)} experiment entries; {len(artifacts)} artifact entries. All reproduced=NO.')
