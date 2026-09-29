# Final adversarial review — ALBUS26-116 (TASK-10)

## Recommendation: REJECT

The revision is substantially more transparent than the submitted version, and I independently reproduced the headline metrics from the saved predictions. Nevertheless, I would reject the manuscript in its present form. The central contribution is an allegedly fitopathological detection–classification cascade, but the cascade has never been evaluated against joint box-and-disease ground truth; the classifier is transferred from controlled, centered-fruit images to detector crops without any validation in that domain; and the biological validity of the source labels is not established. The detector's entire diseased training signal comes from one operational origin group and its diseased-fruit sensitivity on the retrospective test is only 0.577.

There are also serious reporting/provenance defects independent of those admitted limitations. Most importantly, the manuscript describes “independent reviewers” in the leakage audit without disclosing that all reviewers and adjudicators were Claude agents, even though the two initial agents both failed the positive controls and disagreements were frequent. It also says that the final split algorithm was fixed “before seeing the data,” contrary to the frozen provenance, and says that code is published although the response letter itself records publication as pending. These are not cosmetic matters: they concern the validity and reproducibility of the revised study.

The work would require new biological ground truth, new independent field data, and a re-audited data split—not merely editorial changes or another analysis of the existing predictions. That is why I recommend rejection rather than another major revision.

## Scope and independent verification

I reviewed the canonical DOCX and all 16 pages of its rendered PDF, the response to reviewers, the frozen protocol and test-access log, data manifests and audit records, experiment receipts and saved predictions, metric artifacts, configurations, source code, command provenance, git history, and the source repositories/datasets available in the evidence package. I did not treat author-written audit summaries as proof where primary manifests, logs, predictions, code, or source records were available.

Checks that passed are important to record:

- The DOCX and PDF are mutually consistent and contain seven figures and eight tables. The images embedded in the DOCX match the final figure files by hash. I found no stale headline number or stale confusion matrix.
- An independent replay in a disposable copy reproduced the Model 1 test AP values (mAP@0.5 = 0.8071086; mAP@0.5:0.95 = 0.6625059), the fixed-threshold confusion counts, and the 0.35 validation threshold. It also reproduced the Model 2 confusion matrix, accuracy 0.9086758, macro-F1 0.9094733, and both duplicate-sensitivity analyses.
- The Model 1 test matrix underlying the prose is correct: of 26 Enfermo instances, 15 are detected as Enfermo, one as Saludable, and ten are missed; of 166 Saludable instances, 144 are correctly detected and 22 are missed; there are four unmatched Enfermo and 16 unmatched Saludable predictions.
- The Model 2 matrix and the stated 20 errors are correct, including six Cancro bacteriano→Costras and six Costras→Cancro bacteriano errors.
- The Model 1 training receipt supports YOLO26n from the official v8.4.0 base checkpoint, Ultralytics 8.4.52, one Tesla T4, torch 2.10.0/CUDA 12.8, seed 0, 150 epochs, and selection of epoch 91. The Model 2 historical log supports YOLO11n-cls, early stopping at epoch 27, best epoch 12, and the reported CPU training time. The official Ultralytics release history confirms that YOLO26 and the cited releases exist.
- The benchmark raw data reproduce the stated medians and p95. The bibliography has 21 entries, every entry is cited, and every in-text citation has an entry. The high-risk dataset metadata for MangoDHDS, the two Roboflow records, and the Ultralytics version are broadly correct.

These successful checks do not cure the findings below.

## HIGH-severity findings

### H-01 — The leakage audit conceals that the “independent reviewers” were AI agents, and their reliability evidence is poor

**Location and exact text.** Section 3.3.1 states: “Se auditaron las 669 imágenes con tres criterios: identidad de bytes por SHA-256; hash perceptual pHash de 64 bits (ImageHash 4.3.2, Pillow 12.2.0) con umbral de Hamming menor que 5 y una banda de sensibilidad de 5 a 10; y revisión visual ciega de cada candidato por dos revisores independientes, con un tercero en caso de desacuerdo.” The response to REVIEW-01 similarly says: “Revisión visual ciega de cada candidato por dos revisores independientes, con un tercero cuando discreparon.”

**Primary evidence checked.** `data/audits/model1/blinding_log.json` identifies reviewer A as `reviewer-A (claude-opus subagent)`, reviewer B as `reviewer-B (claude-sonnet subagent)`, and reviewer C as `reviewer-C (claude-haiku subagent)`. Both A and B called zero of two positive controls related and therefore failed calibration. They disagreed on 14 of 35 candidates. `data/audits/model1/supplementary_blinding_log.json` again identifies all three reviewers as Claude subagents and records 38 disagreements among 53 reviewed units; its six controls were consistency checks against prior AI adjudication, explicitly not biological ground truth. The response letter reports 38 disagreements among the 47 additional candidate pairs. The logs also admit that blinding relied on instructions rather than access control.

**Consequence.** The grouping decisions define the train/validation/test boundary and the bootstrap units. Presenting this as ordinary independent reviewer adjudication with no disclosure of machine adjudicators, failed initial controls, or very high disagreement materially overstates the credibility of the leakage remedy. “Different agent instances” is not evidence of independent human judgment or of correct same-fruit/sequence identification. Because the final split and confidence intervals inherit these decisions, this defect reaches the main results.

**Declared or undeclared?** Undeclared in both manuscript and response; the primary audit files disclose it.

**Resolution criterion.** Disclose the use, model identities, prompts/protocol, lack of access-control blinding, control failures, and agreement statistics. More importantly, have qualified human reviewers, independent of model development and blinded by enforceable access separation, re-adjudicate all consequential candidates under a pre-specified protocol. Rebuild the groups and split, then retrain and reevaluate if any membership changes. Disclosure alone is insufficient given the failed controls and disagreement rate.

### H-02 — The assertion that the split rule was fixed “before seeing the data” is false

**Location and exact text.** Section 3.3.1 states: “La asignación de grupos a particiones es un algoritmo único fijado antes de ver los datos (semilla 42, objetivo 70/15/15), sin búsqueda de semillas.” The response to REVIEW-02 repeats: “La asignación de grupos es un algoritmo único, fijado antes de ver los datos”.

**Primary evidence checked.** `provenance/protocol_freeze.md` and `.json` explicitly record `test_observed_before_freeze=true` and state: “esto es pre-registro interno de nuevas decisiones, no preregistro prospectivo del estudio ni test nunca observado.” `provenance/test_access_log.csv` records historical review of aggregate test results, matrices, and qualitative predictions before the freeze. The dataset had necessarily also been inspected to discover the montage, construct candidates, and design the conservative grouping rule. Git history shows alternative grouping/split work before the final manifest. The final rule may have been fixed before executing the final assignment or viewing its final metrics, but it was not fixed before seeing the data.

**Consequence.** This language falsely gives a prospective character to a retrospective repair and hides the opportunity for post-hoc design choices. The phrase directly conflicts with the package's own strongest provenance statement.

**Declared or undeclared?** The general retrospective nature of the tests is declared honestly elsewhere; this contradictory “before seeing the data” claim is not.

**Resolution criterion.** Replace the assertion with an exact chronology: what data, labels, groups, alternatives, and historical test outputs had been observed; when the final deterministic assignment rule was frozen; and which outputs had not yet been generated. Do not call this preregistration or pre-data specification.

### H-03 — The biological validity of the disease labels is not established

**Location and exact text.** The title claims “DETECCIÓN Y CLASIFICACIÓN AUTOMATIZADA DE ENFERMEDADES FITOPATOLÓGICAS EN MANGO”. Section 3.2.1 says only: “Se utilizó el conjunto mangoUnhealty (versión 2) (Jairos Workspace, 2026), publicado por terceros en Roboflow Universe bajo licencia CC BY 4.0, con dos clases: Enfermo y Saludable.” Section 3.2.2 lists the five MangoDHDS image labels but provides no diagnostic protocol.

**Primary evidence checked.** The mangoUnhealty public record and the source repository document the class names and annotations but do not identify plant-pathology annotators, diagnostic criteria, laboratory confirmation, inter-rater agreement, or per-image adjudication. The MangoDHDS public record says that collection occurred with expert guidance, while its distributed README merely enumerates the five folders/classes; neither source supplies per-image diagnostic method, blinding, agreement, or laboratory confirmation. The committed manifests faithfully carry the source labels but cannot validate them biologically. The audit also contains an unresolved near-duplicate pair assigned to two diseases (M-02).

**Consequence.** The experiments establish agreement with two third-party label sets, not diagnostic validity for fitopathological disease. Visual symptoms from different causes can overlap, and the manuscript's title and repeated “diagnóstico” wording are stronger than the label provenance permits. This is a construct-validity failure at the outcome level.

**Declared or undeclared?** Largely undeclared. The manuscript declares image-level labels and lack of external field validation, but not the absence of a documented biological reference standard for the labels used as truth.

**Resolution criterion.** Provide independently adjudicated disease ground truth with annotator expertise, diagnostic criteria/method, uncertainty categories, agreement, and—where needed—laboratory confirmation. Otherwise, consistently narrow the claims to prediction of the public datasets' visual labels and remove diagnostic/fitopathological validity claims.

### H-04 — Model 1 has effectively one diseased training origin and inadequate diseased-fruit performance

**Location and exact text.** Section 3.2.1 candidly states: “Todas las instancias Enfermo de entrenamiento proceden de un único grupo de origen, el montaje descrito en la Sección 3.3.1; la prueba tiene 26 instancias Enfermo repartidas en 15 grupos.” Section 6.1 also concedes: “La tercera limitación, y la de mayor peso para el uso previsto, es la baja sensibilidad del detector para Enfermo en prueba (0,577 [0,273; 0,735]), estimada con solo 26 instancias en 15 grupos de origen.”

**Primary evidence checked.** `reports/model1_split_proposal.md`, `data/manifests/model1_clean_manifest.csv`, and the label files give 439 training images in only eight groups, 526 Enfermo boxes in one group, and 937 Saludable boxes across eight groups. Test contains 26 Enfermo instances in 15 operational groups. The saved predictions confirm only 15/26 diseased instances detected as Enfermo. The group-bootstrap interval is correctly computed but does not add new acquisition diversity.

**Consequence.** The model cannot learn robust between-origin variability for the class that matters most. Its observed diseased sensitivity is unsuitable for the motivating use, and the estimate remains imprecise. A high overall mAP and strong Saludable performance do not compensate for this failure. This is a substantive reason to reject an application paper centered on disease detection.

**Declared or undeclared?** Declared honestly and prominently. Honest disclosure is commendable, but it does not make the evidence adequate.

**Resolution criterion.** Acquire multiple genuinely independent diseased-fruit groups across farms, dates, devices, cultivars, and disease presentations; reserve an external, independently diagnosed test set; retrain; and demonstrate clinically/agronomically justified sensitivity with useful precision.

### H-05 — The claimed cascade has no end-to-end evidence and crosses an unvalidated domain boundary

**Location and exact text.** Section 5.2 acknowledges: “Calcularla exige verdad de terreno conjunta, con caja y diagnóstico adjudicados para los mismos frutos, que ninguno de los dos conjuntos tiene. La métrica y su evaluador quedan definidos, pero su valor no se informa.” Figure 7 adds: “La figura es ilustrativa: no hay verdad de terreno de enfermedad específica para esas escenas y no evidencia diagnósticos correctos.” Section 3.1 nevertheless presents the work as an implemented cascade, and the title makes that cascade the organizing contribution.

**Primary evidence checked.** The Model 1 labels contain only boxes plus Enfermo/Saludable; the Model 2 labels are whole-image classes from another source. MangoDHDS images are centered individual fruits collected against a white background, whereas the cascade applies that classifier to detector crops from heterogeneous scenes. `data/manifests/cascade_annotation_schema.json` is only a schema; no populated joint ground truth exists. The cascade evaluator therefore has no valid input. The nine-panel Figure 7 contains model outputs, not labels. No comparison with a single-stage system or other end-to-end baseline is possible on the available data.

**Consequence.** Neither end-to-end recall nor disease-specific precision, abstention behavior, error propagation, or the effect of crop/domain shift is known. The two component metrics from different distributions cannot establish that the proposed cascade works. This is the central acceptance-limiting gap, even though the authors correctly refuse to multiply marginal recalls.

**Declared or undeclared?** Absence of joint truth, error propagation, lack of field/OOD validation, and the illustrative status of Figure 7 are declared honestly. The severity of the centered-white-background-to-field-crop shift is not described with comparable specificity.

**Resolution criterion.** Construct a joint dataset in the intended use domain with fruit boxes and independently adjudicated disease labels for the same fruits, including missed fruits and ambiguous diagnoses. Freeze thresholds before its test evaluation, report end-to-end disease recall/precision and abstention, and compare the cascade with appropriate baselines. No analysis of the present separate datasets can substitute for this.

### H-06 — The manuscript falsely says that code is published, while committed artifacts cannot reproduce training or inference

**Location and exact text.** The abstract says: “Se publican el protocolo de auditoría y su código.” Section 5.3 says: “El protocolo de regeneración (hash perceptual, union-find y estratificación) y su código se publican para que pueda aplicarse a otros conjuntos.” Section 3.6 repeatedly refers to “El repositorio”.

**Primary evidence checked.** The response letter itself says that CLAIM-042 remains pending and requires publishing/citing the repository or softening both statements. The manuscript contains no repository URL or archival identifier. `git ls-files '*.pt'` returns no tracked weights. The selected Model 1 and Model 2 checkpoints exist only as ignored/local or legacy files; the Model 1 kernels are described in `README.md` as private. `reports/reproduction_check.md` regenerated metrics from committed saved predictions and explicitly says “No se repitió ninguna inferencia”; it reconstructs scoring from the already committed Kaggle predictions. `provenance/artifact_registry.csv` ends with a reserved base checkpoint entry and does not register the final selected checkpoint/prediction chain as complete current artifacts.

**Consequence.** A clean recipient can replay arithmetic from predictions but cannot reproduce the exact training or inference that produced them from the committed package. The present-tense publication claim is false as the submission stands, and the availability statement is insufficient for a computational paper.

**Declared or undeclared?** Undeclared in the manuscript; explicitly admitted as pending at the top of the response letter.

**Resolution criterion.** Before submission, archive and cite a public, immutable release containing executable code, exact manifests/configurations, environment specification, licenses, final checkpoints (or durable public checkpoint identifiers), and commands that reproduce inference and metrics. If weights cannot be shared, state that limitation and do not claim full reproduction or published code.

## MEDIUM-severity findings

### M-01 — Neither reported test is an untouched confirmatory test

**Location and exact text.** The abstract correctly calls Model 1 “una evaluación interna retrospectiva sobre imágenes ya publicadas.” Section 4.2.3 says of Model 2: “Como en el Modelo 1, es una evaluación interna retrospectiva: la versión anterior del manuscrito ya informó resultados sobre esta partición.”

**Primary evidence checked.** The protocol freeze records prior inspection of historical test results and qualitative predictions. For the new Model 1 split, 89 of 117 test images belonged to the historical training split, 21 to historical validation, and seven to historical test. The final model was retrained from a base checkpoint without these test images, which prevents direct weight leakage, but architecture, configuration, data audit, and revision strategy were developed after historical exposure. Model 2 reuses the same test and checkpoint already reported in the previous manuscript. The final access log supports one new frozen inference per model, not absence of earlier study-level test knowledge.

**Consequence.** The values are legitimate retrospective internal estimates, not independent confirmation of model selection or generalization. The manuscript's caveat is accurate, but the study still lacks the independent test needed to turn the revised workflow into confirmatory evidence.

**Declared or undeclared?** Declared honestly. This is an evidential limitation, not an accusation of a hidden test run.

**Resolution criterion.** Preserve the present results as retrospective/exploratory and evaluate once on a newly acquired, independently labeled external test set that was unavailable during all design and revision decisions.

### M-02 — A near-identical Model 2 training image pair has conflicting disease labels and remains unadjudicated

**Location and exact text.** Section 3.3.2 describes “división 70 % / 15 % / 15 % estratificada por etiqueta de enfermedad” and later says that no image was discarded. The manuscript does not disclose mixed-label similarity clusters.

**Primary evidence checked.** `data/audits/model2/candidate_pairs.csv` row `PAIR-00543` links `SRC-004117` and `SRC-004662` at pHash Hamming distance 2, labels Cancro_bacteriano and Costras, decision `NEAR_DUPLICATE`, review status `PENDING_ADJUDICATION`. In `data/manifests/model2_frozen_manifest.csv`, these become `SRC-006900` (`Bc101.jpg`) and `SRC-007231` (`Sc252.jpg`) in the same training group `SRC-004117` but retain different labels. Direct inspection shows the same fruit/view with a brightness change; both are 256×256 and have small mean channel differences. The legacy split code assigns a cluster's majority class for stratification but copies every member with its original label; a two-member tie is not biological adjudication. `duplicate_structure.json` reports only exact-SHA class discordance and therefore misses this cluster-level conflict.

**Consequence.** At least one evident label conflict remains in the training truth, precisely between the two classes responsible for most test errors. The statement that the split is stratified by disease is incomplete for mixed-label clusters, and the data audit does not close label quality.

**Declared or undeclared?** Undeclared.

**Resolution criterion.** Adjudicate every cross-class exact/near-duplicate cluster with qualified disease expertise; retain ambiguity when it cannot be resolved; document the rule; regenerate the split without majority-label shortcuts; and retrain if labels or membership change.

### M-03 — Duplicate handling is analyzed for the Model 2 test but not for training/validation selection

**Location and exact text.** Section 4.2.3 carefully reports: “La prueba tiene 219 imágenes pero 208 SHA-256 distintos” and gives exact-SHA and cluster-weighted test sensitivities. It reports the selected Model 2 checkpoint from validation as “los mejores pesos de la época 12 (exactitud top-1 en validación = 0,935).”

**Primary evidence checked.** The frozen manifest has 1,500 files, 1,400 unique SHA-256 values, and 1,337 similarity clusters. Training has 1,064 files but only 986 unique hashes and 935 clusters; validation has 217 files, 206 unique hashes, and 199 clusters. The original training/early-stopping run used ordinary image-weighted training and validation. The current test analysis checks duplicate weighting only after the checkpoint had already been selected; no corresponding validation sensitivity or alternative checkpoint analysis exists.

**Consequence.** Repeated images can overweight visual cases during optimization and early stopping. The small test sensitivity deltas do not establish that duplicate weighting had no effect on model fitting or checkpoint choice.

**Declared or undeclared?** Intra-test duplication is declared; the effect on training/validation selection is not.

**Resolution criterion.** Report duplicate structure by split, train with group-aware sampling or deduplicated data, and verify checkpoint/model selection with group-weighted validation. Treat the current checkpoint as conditional on the duplicated validation distribution.

### M-04 — Two validation evaluators disagree for the same Model 1 checkpoint without reconciliation

**Location and exact text.** Section 4.1.1 says: “El checkpoint seleccionado corresponde a la época 91, con mAP@0,5:0,95 de validación 0,761 y mAP@0,5 0,905 según el registro de entrenamiento; las métricas de validación del evaluador del artículo, con el umbral operativo, se dan en la Tabla 4.” Table 4 gives AP@0.5 = 0.889 and AP@0.5:0.95 = 0.750.

**Primary evidence checked.** `experiments/model1/EXP-R01/v1/run/results.csv` supports approximately 0.9049/0.7609 at the selected epoch. Recalculation from `experiments/model1/EXP-V01/v2/predictions.jsonl` supports 0.8892/0.7500. The code and receipts identify the checkpoint and split, but the manuscript and provenance do not explain the source of the difference or show whether every candidate checkpoint would rank the same under the article evaluator.

**Consequence.** Readers cannot tell which validation pipeline defines model selection or why two nominally equivalent AP evaluations differ. This does not invalidate the independently reproduced test number, but it weakens selection reproducibility.

**Declared or undeclared?** Both values are disclosed; the discrepancy is unexplained.

**Resolution criterion.** Reconcile preprocessing, inference settings, AP implementation, and prediction set. Either select and report with one frozen evaluator or demonstrate that the chosen checkpoint is unchanged across both evaluators.

### M-05 — The confidence intervals omit important sources of uncertainty

**Location and exact text.** Section 3.7 says: “Los intervalos de confianza del 95 % son percentiles de 2000 remuestras bootstrap con semilla 42, que remuestrean grupos de origen y no imágenes.”

**Primary evidence checked.** The code correctly performs 2,000 deterministic percentile group-bootstrap draws and the published intervals match the artifact. Model 1, however, has only 15 test groups containing Enfermo, and the group definitions are operational products of the disputed visual audit. Both models are single fitted checkpoints from one split/seed. The resampling holds model training, split construction, threshold choice, and label/group adjudication fixed.

**Consequence.** These intervals describe conditional variability of the fixed prediction set under the chosen operational groups. They do not quantify training stochasticity, split-selection uncertainty, domain shift, label error, or uncertainty in grouping. Calling them simply 95% confidence intervals can invite a broader interpretation than the procedure supports; the wide Model 1 interval does not repair the limited sample.

**Declared or undeclared?** Small diseased support and group resampling are declared; the conditional scope and omitted uncertainty sources are not.

**Resolution criterion.** Label the intervals as conditional group-bootstrap intervals, justify the independence unit, report group-size/class distribution, and add repeated training/split or external-cohort evidence. For the central diseased sensitivity, obtain substantially more independent positive groups rather than relying on bootstrap precision.

### M-06 — The cascade's 0.4 “Desconocido” threshold is unvalidated

**Location and exact text.** Section 3.1 says: “la etiqueta final del fruto es la del clasificador (cuatro enfermedades o Saludable), o «Desconocido» si su confianza es menor que 0,4.” Figure 7 uses the same rule.

**Primary evidence checked.** The frozen Model 2 evaluation reports top-1 classification without rejection. No calibration curve, expected calibration error, validation optimization, coverage-risk analysis, or independent abstention set supports 0.4. The joint cascade cannot evaluate the rule because it lacks disease ground truth for detector crops.

**Consequence.** “Desconocido” is part of the implemented system but its threshold has no demonstrated meaning. Softmax confidence is not a calibrated diagnostic probability, and the reported Model 2 accuracy/F1 do not describe performance after rejection.

**Declared or undeclared?** The threshold is declared; its arbitrary/unvalidated status is not.

**Resolution criterion.** Pre-specify or tune the threshold only on independent validation data from the cascade's crop domain, assess calibration and coverage versus error, then freeze and evaluate it on joint test ground truth.

### M-07 — The latency response overstates what the manuscript reports, and the benchmark pool is too narrow for a cascade workload claim

**Location and exact text.** The response to REVIEW-07 promises: “Se informan media, mediana, desviación, p95, mínimo y máximo, por etapa y de extremo a extremo.” The manuscript instead gives only: “La mediana de extremo a extremo, de la lectura del archivo a la imagen anotada, es 239,4 ms (p95 777,7 ms); la llamada al Modelo 1 toma 203,8 ms y la cascada completa 233,9 ms.”

**Primary evidence checked.** `artifacts/metrics/benchmark_summary.json` does contain full statistics by stage. For end-to-end time it gives mean 343.4 ms, median 239.4 ms, population SD 459.9 ms, p95 777.7 ms, and a maximum of 8,605.0 ms. The manuscript omits most of these. Joining `benchmark_raw_pool.csv` to the manifest shows 32 images from 28 groups: 29 healthy-only images and only three with Enfermo. The measured predictions contain zero fruits in four images, one fruit in 26, and two fruits in two; there is no crowded-scene workload. The 3,200 rows are repeated timings of 32 images, not 3,200 independent scenes.

**Consequence.** The raw benchmark is useful and the reported medians are correct, but the response incorrectly claims complete reporting in the manuscript. The pool does not characterize scaling with crop count or representative field scenes, and the extreme right tail is hidden by the selected summary.

**Declared or undeclared?** Single-device/no-comparator status is declared. Pool composition, outliers, and incomplete manuscript reporting are not.

**Resolution criterion.** Put the full stage table in the manuscript or supplement; disclose image/group/disease and predicted-crop composition; summarize per-image as well as repeated-run variation; and benchmark a pre-specified representative range of scene densities. Retain the claim as device-specific descriptive latency.

### M-08 — Several literature claims remain unsupported despite the reference cleanup

**Location and exact text.** Section 2.2 claims: “los reportes específicos sobre mango son escasos y, hasta donde los autores conocen, ninguno ha publicado un análisis sistemático de fuga de datos sobre conjuntos públicos de mango.” Section 1 also states: “La consecuencia agronómica es una dependencia excesiva de la aplicación preventiva masiva de agroquímicos, con los costos económicos y ambientales que ello implica (Ciofini et al., 2022).”

**Primary evidence checked.** Liu and Wang (2021) is a general plant disease/pest deep-learning review and predates much of the 2022–2026 literature; the manuscript gives no search sources, query, dates, screening method, or evidence capable of supporting a universal negative through 2026. Ciofini et al. (2022) reviews post-harvest anthracnose management and synthetic fungicide use but does not establish the claimed causal chain from inaccessible diagnosis to excessive mass preventive agrochemical application. Venbrux et al. (2023) discusses pathogen-detection techniques but does not establish the manuscript's specific claim about infrastructure being rarely available to the average rural producer. I found no citation/reference pairing error for the 21 final entries, but citation existence is not claim support.

**Consequence.** The novelty and agronomic-motivation claims are stronger than their evidence. The novelty claim is particularly important because the manuscript positions the leakage analysis as a contribution.

**Declared or undeclared?** Undeclared.

**Resolution criterion.** Either conduct and report a reproducible literature search sufficient for the bounded novelty claim, or soften it to what the cited review establishes. Remove the diagnostic-access→mass-agrochemical causal statement or cite direct empirical evidence.

## LOW-severity findings

### L-01 — Software/reference and template details are not publication-ready

**Location and exact text.** The reference is: “Jocher, G., Qiu, J., & Chaurasia, A. (2026). Ultralytics YOLO (Versión 8.4.52) [Software]. GitHub. https://github.com/ultralytics/ultralytics”. Every PDF footer reads “ALBUS 2025, 3, x. https://doi.org/”.

**Evidence checked.** The software/version identity is credible, but the cited URL is the moving repository root rather than an immutable v8.4.52 tag/archive. The footer remains a template placeholder on all pages.

**Consequence.** Long-term software identification and submission polish are weakened, without changing the results.

**Resolution criterion.** Cite the exact tagged release/archive and persistent identifier if available; replace or remove the journal placeholder according to ALBUS instructions.

### L-02 — The final layout has avoidable whitespace and crowded qualitative labels

**Location and exact text.** Figures 5 and 7 are qualitative galleries; the latter caption correctly says: “Las etiquetas no están verificadas con verdad de terreno de enfermedad.”

**Evidence checked.** Page-by-page PDF inspection found no clipped table or figure, but pages 8 and 11 leave large lower blank areas because the following galleries are forced to a new page, page 16 is mostly blank, and dense panels in Figures 5/7 have crowded small overlay labels.

**Consequence.** This affects readability/presentation only.

**Resolution criterion.** Reflow the galleries and captions while preserving legibility at journal print size.

## Assessment of the response to every reviewer comment

“Answered” below means that the response accurately appears in the manuscript; it does not mean that the resulting study is scientifically sufficient.

| Review ID | Assessment of the response as the manuscript stands | Related finding |
|---|---|---|
| REVIEW-01 | **Not resolved.** A Model 1 leakage audit exists, but the letter conceals machine adjudication, failed initial controls, and frequent disagreement. | H-01 |
| REVIEW-02 | **Partly resolved.** The final manifest is grouped and atomic under its rules, but those rules inherit the unreliable adjudication and the “before seeing the data” chronology is false. | H-01, H-02 |
| REVIEW-03 | **Partly resolved.** Model 1 was retrained and the final predictions/metrics are internally correct, but the validation evaluators are unreconciled and exact inference is not reproducible from committed artifacts. | M-04, H-06 |
| REVIEW-04 | **Answered.** The new test denominators, positive support, groups, and sensitivity limitation are reported accurately. | H-04 (remaining adequacy problem) |
| REVIEW-05 | **Partly resolved.** Group-bootstrap intervals are supplied and numerically correct, but only conditional uncertainty is covered and positive support remains inadequate. | M-05 |
| REVIEW-06 | **Answered.** The unsupported field-prevalence interpretation was removed; the manuscript now describes corpus imbalance. | — |
| REVIEW-07 | **Partly resolved.** A reproducible raw CPU benchmark exists, but the manuscript does not report the full statistics promised by the response and does not characterize a representative cascade workload. | M-07 |
| REVIEW-08 | **Answered by withdrawal.** Raspberry Pi claims were removed and lack of hardware is stated; no Raspberry Pi result is implied. | — |
| REVIEW-09 | **Partly resolved.** YOLO26n version, base checkpoint, run environment, and configuration are documented correctly, but the final weights are not committed/publicly archived and inference cannot be replayed from the submission alone. | H-06 |
| REVIEW-10 | **Answered.** “Early” and comparative “efficient” claims were removed; the remaining text is framed as visible-sign detection. | — |
| REVIEW-11 | **Honest but scientifically unresolved.** Lack of rural/field/OOD validation is visible; it remains a central reason the claimed use is unsupported. | H-05, M-01 |
| REVIEW-12 | **Honest but scientifically unresolved.** Error propagation is described correctly, but it is not measured. | H-05 |
| REVIEW-13 | **Honest but scientifically unresolved.** The joint metric/evaluator is defined, but no joint ground truth or end-to-end value exists. | H-05 |
| REVIEW-14 | **Answered.** The specified repetition, numbering, accent, and major prose issues were corrected. | L-02 only |
| REVIEW-15 | **Answered.** Split terminology, class names, and four-diseases-plus-Saludable nomenclature are now consistent. | — |
| REVIEW-16 | **Largely answered.** The final 21-entry list is consistently formatted and bidirectionally linked to citations. | L-01 |
| REVIEW-17 | **Partly resolved.** Dataset and software metadata are mostly corrected, but the software citation is not immutable and the executable research objects are not archived. | H-06, L-01 |
| REVIEW-18 | **Partly resolved.** Citation-to-entry matching is complete, but several surviving citations do not support the strength of the associated claims. | M-08 |

## Final finding register

| ID | Severity | Short finding | Declared by manuscript? |
|---|---|---|---|
| H-01 | HIGH | AI adjudicators are presented only as independent reviewers despite failed controls and frequent disagreement | No |
| H-02 | HIGH | Split rule falsely described as fixed before seeing data | Contradicted by its retrospective disclosures |
| H-03 | HIGH | Biological reference standard for disease labels is not established | No |
| H-04 | HIGH | All diseased Model 1 training signal comes from one group; diseased sensitivity is low and sparse | Yes |
| H-05 | HIGH | No joint ground-truth/end-to-end cascade evaluation; classifier crop-domain transfer is unvalidated | Mostly yes; domain shift only partly |
| H-06 | HIGH | Code-publication claim is false; committed package replays metrics but not exact training/inference | No; response admits pending action |
| M-01 | MEDIUM | Both tests are retrospective and previously exposed, not untouched confirmation | Yes |
| M-02 | MEDIUM | Cross-disease near-duplicate remains unadjudicated in Model 2 training | No |
| M-03 | MEDIUM | Duplicate effects on Model 2 training/validation selection are not analyzed | Partly |
| M-04 | MEDIUM | Model 1 validation evaluators disagree without reconciliation | Values yes; explanation no |
| M-05 | MEDIUM | Bootstrap intervals are conditional and omit grouping/training/split uncertainty | Partly |
| M-06 | MEDIUM | The 0.4 abstention threshold is unvalidated and uncalibrated | Threshold yes; limitation no |
| M-07 | MEDIUM | Latency reporting is incomplete relative to the response and the pool is narrow | Partly |
| M-08 | MEDIUM | Novelty and agronomic causal claims exceed their citations | No |
| L-01 | LOW | Moving software URL and journal footer placeholder | No |
| L-02 | LOW | Excess whitespace and crowded labels in qualitative figures | No |

**Count: 6 HIGH findings; 8 MEDIUM findings.**
