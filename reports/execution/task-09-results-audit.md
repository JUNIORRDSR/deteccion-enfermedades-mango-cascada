# Independent Audit B — TASK-09 results pass and pre-submission steps

**Manuscript:** ALBUS26-116  
**Audit date:** 2026-09-28  
**Manuscript audited:** `manuscript/source/Articulo_Mango_ALBUS_revision.docx`, after pass 2c (`9e1ccfa`)  
**Audit type:** read-only research-methodology and scientific-reporting review  
**Changes made to the research package:** none; this report is the only file added

## Verdict

**No: the results sections and the response letter should not be submitted as they stand.** The numerical core is reproducible: the reported M1 and M2 point estimates and intervals, the benchmark statistics, Tables 4, 5, and 7, and Figures 4–7 agree with their artifacts at the displayed precision. I found no surviving use of the retracted detector metrics as current results.

Submission is nevertheless blocked by **4 HIGH** and **6 MEDIUM** open findings. The HIGH findings are unsupported scientific wording: a remaining temporal/early-detection premise, a causal characterization of the leaked split that was not experimentally established, a causal explanation of the Cancro bacteriano–Costras confusion, and the unsupported exact recommendation of 320 px in Table 8. The MEDIUM findings concern the required retrospective qualification of the M1 test, an unsupported statement about unseen “montajes,” omission of the required M2 duplicate-sensitivity results, incomplete numerical and claim traceability, and unfinished response-letter status/location fields.

If the findings in this report are resolved, the final document is rendered and inspected, and TASK-10 passes with zero open HIGH or MEDIUM findings, the numerical results would be suitable for submission. This audit does not itself make that later submission decision.

## Scope, authority, and method

The audit treated the following as binding: `provenance/protocol_freeze.json` and `.md`; the revision design; TASK-09 and TASK-10 in the revision plan; the reviewer comments and draft responses; and DECISION-037 through DECISION-039. I also checked the pass scripts, the current DOCX XML through `python-docx`, the source and embedded figures, the frozen metrics and interval artifacts, the M2 predictions and sensitivity report, the benchmark report and raw CSV, and the M1 selection record.

The protocol has two consequences that are important to this report:

1. The current M1 test is an **internal retrospective evaluation**, not a newly pristine prospective holdout, even though the current checkpoint and threshold were fixed before the current test run.
2. Groups are the maximum known dependence unit for inference. They are not proven biologically independent units. The manuscript does not currently make the prohibited biological-independence claim.

All comparisons below use the unrounded artifact value first and then check the manuscript's three-decimal rounding and Spanish decimal comma. Figures 4–7 embedded in the DOCX are byte-identical to their source PNGs.

## 1. Numerical reconciliation

### 1.1 Abstract and repeated headline results

All numerical statements inserted by pass 2c in the abstract reconcile:

| Manuscript statement | Artifact basis | Audit |
|---|---|---|
| 669 detector images; two detector classes; four disease classes | M1 manifest and M2 class mapping | Correct |
| M1 test: 117 images in 98 groups | `experiments/model1/EXP-R02/metrics.json` | Correct |
| M1 mAP@0.5: `0,807 [0,677; 0,887]` | 0.8071086; bootstrap [0.676994, 0.886654] | Correct rounding and comma |
| Enfermo sensitivity: `0,577 [0,273; 0,735]` | 0.5769231; bootstrap [0.272727, 0.734748] | Correct rounding and comma |
| M2 test: 219 images | M2 interval and prediction artifacts | Correct |
| M2 accuracy: `0,909 [0,869; 0,946]` | 0.9086758; [0.868772, 0.946188] | Correct rounding and comma |
| M2 macro-F1: `0,909 [0,869; 0,945]` | 0.9094733; [0.869426, 0.944677] | Correct rounding and comma |
| 95% intervals | percentile group bootstrap configuration | Correct |

The same headline values are repeated consistently in Sections 5.1, 6.1, and 7. No repetition changes a digit or interval endpoint.

### 1.2 Section 4.1.2 and Table 4 — validation

The selected checkpoint is epoch 91. Its unrounded selection fitness is 0.7608686, displayed as `0,761` where reported. The operating threshold is `0,35`, selected on validation by maximum Enfermo F2, with the frozen lower-threshold tie rule. Validation contains 113 images, 93 groups, and 199 annotated instances (30 Enfermo and 169 Saludable).

Every Table 4 entry matches `experiments/model1/EXP-V01/metrics_frozen.json`:

| Metric | Class mean | Enfermo | Saludable |
|---|---:|---:|---:|
| AP@0.5 | 0.889 | 0.861 | 0.917 |
| AP@0.5:0.95 | 0.750 | 0.672 | 0.828 |
| Precision | — | 0.963 | 0.941 |
| Sensitivity | — | 0.867 | 0.846 |
| F1 | — | 0.912 | 0.891 |
| F2 | — | 0.884 | 0.864 |

The DOCX correctly renders those values with decimal commas. The current `0,846` and `0,884` are not remnants of the retracted result: they are, respectively, the current validation sensitivity for Saludable and the current validation F2 for Enfermo.

### 1.3 Section 4.1.2 and Table 5 — test

The test counts—117 images, 98 groups, 192 instances, 26 Enfermo and 166 Saludable—match `EXP-R02/metrics.json`. The 26 Enfermo instances occur in 15 groups. Table 5 is numerically correct:

| Metric | Class mean | Enfermo | Saludable |
|---|---:|---:|---:|
| AP@0.5 | 0.807 [0.677; 0.887] | 0.711 | 0.903 |
| AP@0.5:0.95 | 0.663 [0.536; 0.745] | 0.534 | 0.791 |
| Precision | — | 0.789 [0.400; 1.000] | 0.894 [0.827; 0.955] |
| Sensitivity | — | 0.577 [0.273; 0.735] | 0.867 [0.800; 0.931] |
| F1 | — | 0.667 [0.333; 0.826] | 0.881 [0.826; 0.927] |
| F2 | — | 0.610 [0.300; 0.769] | 0.873 [0.813; 0.926] |

The displayed intervals agree with `artifacts/metrics/model1_intervals.json`; no interval was blocked. The manuscript correctly states 2,000 resamples and seed 42. Decimal commas are correct in the DOCX.

The paragraph comparing validation and test is also arithmetically correct: mAP@0.5 decreases from 0.889 to 0.807; Enfermo sensitivity decreases from 0.867 to 0.577; Saludable sensitivity changes from 0.846 to 0.867; and the upper endpoint 0.735 for Enfermo test sensitivity is below the validation estimate 0.867. Interpretive qualifications are discussed below.

### 1.4 Section 4.1.3 and Figures 4–5

The Figure 4 matrix matches the test artifact exactly:

| Ground truth / prediction | Enfermo | Saludable | No detection |
|---|---:|---:|---:|
| Enfermo | 15 | 1 | 10 |
| Saludable | 0 | 144 | 22 |
| Background | 4 | 16 | — |

The row proportions shown in the figure are consistent with these counts: 0.58/0.04/0.38 for Enfermo and 0/0.87/0.13 for Saludable. The caption's threshold `0,35` and IoU `0,5` are correct. The prose statement that the dominant ground-truth error is a missed detection is supported: 32 annotated objects are unmatched (10 Enfermo and 22 Saludable), compared with one Enfermo-to-Saludable class error.

Figure 5 uses the frozen seed-42 test sample and the frozen 0.35 threshold. Its nine source IDs are `SRC-009695`, `SRC-009762`, `SRC-009764`, `SRC-009768`, `SRC-009793`, `SRC-009798`, `SRC-009804`, `SRC-009897`, and `SRC-009919`. The displayed ground-truth and detection counts agree with the saved predictions; the sample was not selected by performance.

### 1.5 Section 4.1.5 — latency

All latency values agree with `artifacts/metrics/benchmark_raw.csv` and `reports/benchmark_report.md`:

| Stage | Manuscript median | Manuscript p95 | Recomputed from 3,200 successful rows |
|---|---:|---:|---:|
| M1 call | 203.8 ms | 681.8 ms | 203.83645 / 681.758145 ms |
| Cascade computation | 233.9 ms | 772.0 ms | 233.8815 / 772.002165 ms |
| End to end | 239.4 ms | 777.7 ms | 239.4089 / 777.73907 ms |

The stated protocol also matches the benchmark artifact: AMD Ryzen 5 7520U, Windows 11, batch 1, FP32, 640 px for M1, 224 px for M2, one process and one thread, 10 warm-ups, and 100 repetitions on each of 32 validation images. The manuscript correctly says Raspberry Pi 4 latency was not measured.

Latency is a material manuscript result with a valid CSV/report source, but it has **no JSON source and no entry in `manuscript/numbers.json`**.

### 1.6 Section 4.2, Table 7, and Figures 6–7

The M2 test has 219 images in 203 registered groups. Accuracy and macro-F1 match the interval artifact, as reported above. All Table 7 values, intervals, and supports match `artifacts/metrics/model2_intervals.json`:

| Class | Precision | Sensitivity | F1 | n |
|---|---:|---:|---:|---:|
| Antracnosis | 0.898 [0.800; 0.977] | 0.957 [0.886; 1.000] | 0.926 [0.857; 0.975] | 46 |
| Cancro bacteriano | 0.841 [0.725; 0.944] | 0.822 [0.704; 0.929] | 0.831 [0.736; 0.911] | 45 |
| Costras | 0.857 [0.744; 0.955] | 0.818 [0.700; 0.925] | 0.837 [0.743; 0.915] | 44 |
| Podredumbre del extremo del tallo | 0.976 [0.921; 1.000] | 0.976 [0.918; 1.000] | 0.976 [0.935; 1.000] | 42 |
| Saludable | 0.976 [0.923; 1.000] | 0.976 [0.919; 1.000] | 0.976 [0.937; 1.000] | 42 |
| Macro mean | — | — | 0.909 [0.869; 0.945] | 219 |

The 20 total M2 errors and the leading error counts—six Cancro bacteriano classified as Costras, six Costras classified as Cancro bacteriano, and two Costras classified as Antracnosis—recompute from `experiments/model2/EXP-R03/predictions.jsonl`. Figure 6 contains that exact matrix and row proportions.

Figure 7 uses nine seed-42 **validation**, not test, images: `SRC-009692`, `SRC-009773`, `SRC-009774`, `SRC-009781`, `SRC-009799`, `SRC-009807`, `SRC-009818`, `SRC-009916`, and `SRC-010768`. It uses the saved EXP-V01 detections at threshold 0.35 and the specified M2 display threshold 0.4. The caption explicitly says that these data have no per-fruit disease ground truth and that the panel does not establish diagnostic correctness. That is protocol-compliant.

### 1.7 Sections 5.1, 6.1, 7, and Table 8

All repeated empirical values in the discussion, limitations, and conclusion agree with the artifacts. The Table 8 rows containing 669 detector images, the Cancro/Costras F1 intervals, Enfermo sensitivity, and the absence of a Raspberry Pi 4 measurement are consistent with the corresponding evidence.

One numeric exception is material: Table 8 prescribes **“resolución 320 px.”** The value 320 is hard-coded in `revise_pass2c.py`; it is not returned by `values()`, is not evaluated in any supplied experiment, and is not justified by an ablation or cited source. This contradicts the premise that every pass-2c number comes from `values()` and is finding B-04.

### 1.8 Coverage of `manuscript/numbers.json`

`reports/manuscript_consistency.json` reports 26 registered numbers and no issues. That statement is narrowly true: each registered value occurs at its configured anchor. It does **not** show that all material manuscript numbers are registered.

The registry covers selected headline point estimates, some interval endpoints, and selected counts. Material omissions include:

- most confidence-interval endpoints in the abstract and repeated prose;
- most cells of Tables 4, 5, and 7;
- epoch 91, most test/validation counts, most confusion-matrix counts, and the Figure 4 values;
- the Figure 5 and Figure 7 sample memberships and display thresholds;
- all benchmark protocol and latency values, whose authoritative source is CSV rather than JSON;
- the M2 confusion counts and most class-level intervals;
- the unsupported 320 px in Table 8; and
- many repetitions in Sections 5.1, 6.1, and 7.

The consistency mode therefore detects mismatches only in a small allow-list; it is not evidence that every number in the document has an artifact source. This is finding B-08.

## 2. Retracted-result and leaked-split leftovers

The current manuscript contains no active-result occurrence of `0.932`, `0.845`, `0.737`, old precision `0.884`, `n=33`, or `145 ms`; no uppercase “TEST”; and no “test independiente.” It does not claim the cleaned data are “libre de fuga” or “sin duplicados.” Its one use of the former idea is a correct negation: **“No se afirma que el conjunto resultante quede libre de toda dependencia.”**

Two potentially confusing numbers are legitimate current values: `0,846` is current Saludable validation sensitivity, and `0,884` is current Enfermo validation F2. References to 13 Enfermo instances and 11/13 remain only when explicitly describing the defective published split or the reviewer's original calculation; they are not presented as current results.

No section still reports the old detector performance as the current detector performance. The principal semantic leftover is instead the temporal premise in the Introduction:

> “la inspección visual es tardía por naturaleza, ya que cuando los síntomas son perceptibles a simple vista, el patógeno ya ha comprometido una fracción significativa del tejido.”

This is an early-detection rationale in substance even though it avoids the literal words “temprana” and “precoz.” The study detects visible RGB signs and contains no temporal disease-stage or tissue-damage evidence. It also contradicts REVIEW-10's claim that the temporal wording was resolved. This is finding B-01.

The literal efficiency claim has been removed. The manuscript does not claim prospective external generalization and explicitly identifies the lack of an external out-of-distribution test.

## 3. Interpretation audit

### 3.1 Supported and proportionate interpretations

**Drop in Enfermo sensitivity and wide interval.** Supported. The drop from 0.867 to `0,577 [0,273; 0,735]` is exact. Only 26 Enfermo instances in 15 registered groups contribute, and the group-bootstrap interval is correspondingly wide. The sentence noting that the upper endpoint remains below the validation point estimate is numerically correct. It should not be read as a formal between-split hypothesis test, but the manuscript does not present it as one.

**“el detector actual deja pasar más frutos enfermos de los que marca en falso.”** Supported for this test and threshold. There are 11 missed/misclassified Enfermo ground-truth instances versus four unmatched Enfermo detections, consistent with precision 0.789 exceeding sensitivity 0.577. The safest scope is explicitly “en esta prueba,” because neither count estimates field prevalence or field cost; the surrounding paragraph mostly supplies that scope.

**“el error dominante es la falta de detección.”** Supported for the ground-truth object error modes shown in Figure 4: 32 annotated instances are not detected, versus one between-class error. The figure also shows 20 unmatched detections, so the statement should continue to refer to the annotated-object error pattern rather than all possible error accounting.

**Validation metrics at the chosen threshold are optimistic.** Supported and proportionate. The threshold was selected by maximizing validation Enfermo F2, and the checkpoint was selected on a validation metric, so the displayed validation performance is selection-conditioned. This does not prove the size of the optimism, but the manuscript does not quantify it.

**Comparison with the previous manuscript version.** Supported. The old published split mixed related montage material across partitions, while the current run uses the frozen grouped split and a newly trained checkpoint. Saying the old and current figures are not directly comparable is scientifically appropriate. The old Wilson interval in the response letter is correctly labeled as relying on an independence assumption that the 13 instances did not satisfy.

### 3.2 Interpretations requiring correction or qualification

The following sentence overstates what the supplied artifacts establish:

> “la partición por grupos de origen hace que la prueba contenga montajes que el modelo no vio al entrenar.”

The manifests support that test acquisition groups are disjoint from training under the frozen grouping rule. They do not establish that the current test specifically contains unseen “montajes,” nor that this explains the sensitivity drop. This is finding B-06. A resolution must state only the documented group separation unless montage membership is separately evidenced, and must not make the grouping a demonstrated cause of the performance change.

The leaked-split paragraph makes an unevaluated causal and magnitude claim:

> “conlleva una sobreestimación severa de las métricas de generalización: el modelo memoriza imágenes vistas durante el entrenamiento y las vuelve a observar en validación, transformando la métrica de evaluación en un indicador de memorización antes que de capacidad de generalizar a frutos no vistos.”

The audit proves cross-partition dependence and that the old test was not independent. It does not include a controlled contaminated-versus-grouped experiment that identifies the magnitude as “severa,” demonstrates model memorization, or shows the old metric measured memorization rather than a mixture of signal and dependence. This is finding B-02.

The M2 error counts are supported, but the explanatory sentence is not:

> “Ambas patologías presentan lesiones oscuras e irregulares, y distinguirlas suele requerir detalles finos, como la textura local o el exudado bacteriano, que un clasificador a 224 px apenas captura.”

The confusion matrix cannot establish lesion phenomenology, what is clinically required to distinguish the diseases, or that 224 px caused the errors. No resolution ablation, attention analysis, feature analysis, or supporting citation is provided. Section 6.1 compounds this by saying separation **“requeriría más datos, mayor resolución de entrada o módulos de atención local.”** These are hypotheses for future work, not demonstrated remedies. This is finding B-03.

The limitations also state **“la saturación bajo iluminación ambiental intensa”** and Table 8 states **“Sensibilidad a luz intensa / Saturación del sensor / Parasol + normalización.”** No supplied measurement, image audit, or operating log supports the observation or the proposed remedy. Because it is framed as a limitation rather than a demonstrated performance result, it is included in the resolution criterion for B-03 rather than counted as a separate HIGH finding: identify the evidence, qualify it as an untested operational hypothesis, or remove it.

No wording indicates that the current checkpoint or threshold was selected on the current test. The selection record and access log support the stated order for the current run. The problem is different: without the required retrospective label, “before touching test” and “evaluated once” can imply a historically pristine test set. That is finding B-05.

## 4. Figures and tables

### 4.1 Source/embedding identity and resolution

| Figure | Source pixels | Source equals embedded DOCX media | Approx. effective resolution at DOCX size | Audit |
|---|---:|---|---:|---|
| Figure 4 | 2785 × 1391 | Yes (`image4.png`) | 464 ppi | Pass |
| Figure 5 | 1821 × 1900 | Yes (`image5.png`) | 304 ppi | Pass, with label-crowding note |
| Figure 6 | 2954 × 1486 | Yes (`image6.png`) | 492 ppi | Pass |
| Figure 7 | 1922 × 2000 | Yes (`image7.png`) | 320 ppi | Pass, with label-crowding note |

These four figures clear a common 300-ppi raster threshold at their current placed sizes. Journal-specific requirements and the final PDF must still be checked. Figures 5 and 7 contain crowded or edge-truncated overlays in some lower panels; this does not change the audit values but may impair readability after PDF conversion (B-11, LOW).

### 4.2 Content checks

- **Figure 4:** counts, proportions, threshold 0.35, IoU 0.5, and background row all match M1 test predictions.
- **Figure 5:** the nine panels are the seed-42 test sample; ground truth and detections match the saved predictions at threshold 0.35.
- **Figure 6:** counts and normalized proportions match the 219 M2 predictions.
- **Figure 7:** the nine panels are the seed-42 M1 validation sample, not test; boxes come from saved predictions; the caption disclaims per-fruit disease ground truth and diagnostic proof.
- **Table 4:** all validation values pass.
- **Table 5:** all test point estimates and displayed intervals pass.
- **Table 7:** all class values, intervals, supports, and macro-F1 pass.
- **Table 8:** evidence-linked metrics pass, but the exact 320-px mitigation fails traceability (B-04), and the asserted illumination limitation/remedy needs evidence or qualification (included under B-03).

Figure 3, outside the requested Figures 4–7, still contains an English decimal point in `mAP@0.5:0.95 = 0.761`, and REVIEW-05 gives the old Wilson interval as `[0.578, 0.957]`. These are editorial decimal-comma inconsistencies (B-12, LOW).

## 5. Uncertainty and design compliance

### 5.1 M1 group bootstrap

The manuscript describes the frozen design correctly: 2,000 percentile resamples, seed 42, and acquisition group as the resampling unit. It states both blocking rules: fewer than two class-containing groups, or more than 5% undefined resamples. The interval artifact confirms 98 test groups, including 15 with Enfermo and 84 with Saludable; no interval is blocked. One Enfermo-F2 resample is undefined, well below the 5% gate.

The prose does not call groups biologically independent. It appropriately describes them as a dependence-control unit.

### 5.2 M2 duplicate sensitivity

The frozen analysis is correctly implemented in the artifacts:

- principal image-weighted analysis: 219 images, accuracy 90.87%, macro-F1 90.95%;
- exact-SHA-deduplicated analysis: 208 unique images, changes of -0.48 and -0.30 percentage points;
- cluster-weighted analysis: 203 clusters, changes of -0.72 and -0.50 percentage points; and
- paired group bootstrap: 2,000 resamples, seed 42, with no blocked comparison.

The methods mention both sensitivity analyses, and REVIEW-05 reports the accuracy changes. The manuscript's results section, however, reports only the principal 219-image/203-group result. It does not disclose the 11 within-split exact duplicates or the exact-SHA and cluster-weighted sensitivity results. The frozen reporting plan requires those intra-split duplicates and sensitivity results to accompany the primary estimate. This is finding B-07.

The manuscript does not claim that M2 groups or clusters are biologically independent. In the current manifest the registered group and similarity-cluster identifiers happen to coincide for these 203 units; the distinction should nevertheless remain explicit because the protocol assigns them different roles.

### 5.3 Retrospective status

The words “evaluación interna retrospectiva” do not appear in the manuscript or REVIEW-03. Instead, the text repeatedly emphasizes that the current test was touched once after fixing the checkpoint and threshold. That execution statement is true for the current run, but it is incomplete because the test had historical exposure in the project and in the prior manuscript. The frozen protocol specifically requires the retrospective qualification. This is B-05.

## 6. Response-to-reviewers audit

### REVIEW-03

The filled answer's configuration and results reconcile: 640 px, batch 16, 150 epochs, patience 100, seed 0, 18.7 minutes, epoch 91, selected validation metric 0.761, 113 validation images, mAP@0.5 0.889, threshold 0.35, Enfermo F2 0.884, 117 test images in 98 groups, test mAP@0.5 `0,807 [0,677; 0,887]`, and Enfermo sensitivity `0,577 [0,273; 0,735]`. The execution environment and retry account are consistent with the cited records.

The answer is not fully protocol-compliant because **“El test se evaluó una sola vez, después de fijar ambos”** lacks the required internal-retrospective qualification and can imply that the test was historically untouched. Resolve B-05 in both the manuscript and this answer.

### REVIEW-05

The M1 bootstrap design, blocking gates, group counts, and M1 interval are correct. The M2 point estimates and reported changes under exact deduplication and cluster weighting agree with `reports/model2_duplicate_sensitivity.md`. The historical 11/13 Wilson interval recomputes to [0.577654, 0.956742], so `[0.578, 0.957]` is numerically correct; only its decimal punctuation is inconsistent with the Spanish document.

The letter reports M2 accuracy deltas but not the macro-F1 deltas (-0.30 and -0.50 percentage points). This is not a false statement, but the final answer would be more complete if it stated both prespecified outcome changes, matching the manuscript's required sensitivity disclosure.

### REVIEW-07

The answer correctly replaces the historical 145 ms with the frozen benchmark protocol. Hardware, image sizes, batch/precision/thread settings, warm-up and repetition counts, selection of 32 validation images, 3,200 measurements, and the 203.8/233.9/239.4 ms medians and 777.7 ms end-to-end p95 all reconcile. The Raspberry Pi 4 remains correctly blocked rather than estimated.

### REVIEW-10 still needs

REVIEW-10 currently says:

> “**Estado.** RESUELTO en el texto `[PENDIENTE: ubicación]`.”

It needs two substantive completion checks, not just a page number:

1. remove or evidence/qualify the remaining temporal premise quoted in B-01, then repeat a semantic—not merely keyword—scan for claims of earlier diagnosis, prevention before visible symptoms, timeliness, and undefined efficiency; and
2. after the final PDF exists, replace the placeholder with exact final section/page/paragraph locations and verify that the response accurately describes the final text.

Until both are done, “RESUELTO” is inaccurate.

### REVIEW-15 still needs

The combined REVIEW-14/15 answer ends with **“[PENDIENTE: secciones de resultados y revisión sobre el render final]”** and its state is **“[PENDIENTE]”.** It still needs:

- final rendered page references for all changed results sections;
- page-by-page verification of headings, section sequence, table and figure numbering, placements, captions, and cross-references;
- a terminology and decimal-comma pass over the rendered output, including text inside figures; and
- replacement of the placeholder and state with an evidence-backed final disposition.

The letter header is also stale: **“Las cifras marcadas `[PENDIENTE: …]` salen de artefactos que todavía no existen”** is no longer true for TASK-09 result artifacts. The header and all remaining placeholders must describe the actual final state (B-10).

## 7. Required next steps before submission

The following order minimizes the chance of rendering and auditing a document that still needs substantive changes.

1. **Resolve this audit's scientific findings.**  
   **Done when:** every B-01 through B-10 resolution criterion is met; a fresh targeted review finds no unsupported temporal, causal, resolution, montage, retrospective-status, or duplicate-sensitivity statement; and this audit's HIGH/MEDIUM count is zero or every residual item has an explicit, defensible disposition.

2. **Complete the claim–evidence matrix and editorial audit.**  
   Update `reports/claim_evidence_matrix.csv` for the actual pass-2c/final claims and exact locations; resolve or disposition its existing PARTIALLY_SUPPORTED, UNVERIFIED, and UNSUPPORTED rows. Produce the required `reports/editorial_audit.md` and reconcile it with `reports/editorial_claim_audit.csv`. Expand numerical traceability or explicitly document exceptions such as the benchmark CSV.  
   **Done when:** every material current claim and number has an exact source/location and support judgment; no critical claim is UNVERIFIED or UNSUPPORTED; `reports/editorial_audit.md` exists; and the consistency check can no longer be mistaken for a comprehensive 26-number check.

3. **Render the final DOCX to PDF with a recorded command and tool version.**  
   **Done when:** the PDF is generated from the exact candidate DOCX, the command/version/exit status are recorded, the expected page count is stable, and the PDF hash is recorded.

4. **Perform a page-by-page visual inspection.**  
   Inspect every page at normal reading scale and at zoom. Check clipped text, font substitution, widows/orphans, table splits, caption attachment, image crops, overlay legibility, and blank/overflow pages. Confirm every figure's effective resolution against the journal requirement, not only its source pixel dimensions. Figures 4–7 currently meet 300 ppi at their placed sizes; Figures 5 and 7 need special attention to crowded overlays.  
   **Done when:** a page-indexed checklist covers every PDF page, every table and figure, and records zero unresolved placement/readability/resolution defect.

5. **Verify numbering, cross-references, terminology, and decimal punctuation in the final render.**  
   **Done when:** sections, tables, figures, and equations are sequential; every in-text reference resolves to the right item; captions match their callouts; terminology is consistent; no prohibited “TEST”/“test independiente”/leak-free wording survives; and Spanish decimal commas are consistent in prose, tables, figures, and the letter.

6. **Run the final bibliography and citation audit on the rendered candidate.**  
   **Done when:** the 21-entry list is alphabetized and APA-7 compliant; every in-text citation has one bibliography entry; every bibliography entry is cited; DOI/URL and source-support checks still pass; and pagination or formatting did not detach or corrupt entries.

7. **Finalize the response letter.**  
   Resolve REVIEW-10 and REVIEW-15 as described above; add exact final locations; synchronize REVIEW-03/05 with the final manuscript; remove the stale draft header and every `[PENDIENTE]`; and retain REVIEW-08 and REVIEW-12/13 as honest blocks where evidence is unavailable.  
   **Done when:** a literal placeholder search returns zero, every stated action is visible in the final PDF at the cited location, and every metric in the letter matches the artifact and manuscript.

8. **Close TASK-09 gates on the final candidate.**  
   Re-run document checks, terminology scans, numerical/claim traceability, source-versus-embedded figure checks, and render checks.  
   **Done when:** all TASK-09 commands pass against the same final DOCX/PDF pair and the evidence records identify that pair by hash.

9. **Execute TASK-10 from a clean verification environment.**  
   This must include the fresh test suite, provenance/freeze/amendment/access checks, portability checks, metric reproduction within the frozen tolerance, protocol compliance, legacy integrity, and a new adversarial review. Replace the stale pre-results `docs/final_validation_report.md` and create the required final adversarial/protocol outputs.  
   **Done when:** TASK-10's fresh verification artifacts all identify the final package, every required gate passes, and the independent final review reports **zero open HIGH and zero open MEDIUM** findings.

10. **Freeze the submission package.**  
    **Done when:** the candidate DOCX, inspected PDF, response letter, figures, bibliography, and required evidence reports are the versions verified above; their hashes and package inventory are recorded; and no file changes after verification without re-running the affected gates.

## 8. Findings register

| ID | Severity | Location and exact wording | Consequence | Resolution criterion | Status |
|---|---|---|---|---|---|
| B-01 | **HIGH** | Introduction: “la inspección visual es tardía por naturaleza, ya que cuando los síntomas son perceptibles a simple vista, el patógeno ya ha comprometido una fracción significativa del tejido.” REVIEW-10 says the temporal claim is resolved. | Reintroduces an unsupported early/temporal-detection premise and makes the reviewer response inaccurate. | Remove it or replace it with a claim directly supported by temporal-stage evidence; complete a semantic temporal-claim scan; update REVIEW-10 with an exact final location. | Open |
| B-02 | **HIGH** | Dataset/split discussion: “conlleva una sobreestimación severa… el modelo memoriza… transformando la métrica… en un indicador de memorización”. | Claims a causal mechanism and severity not identified by the duplicate audit or a controlled comparison. | Limit the claim to demonstrated cross-partition dependence/non-independence, or provide a prespecified controlled analysis establishing magnitude and mechanism. | Open |
| B-03 | **HIGH** | Section 4.2: “lesiones oscuras e irregulares… detalles finos… que un clasificador a 224 px apenas captura”; Section 6.1 says separation “requeriría” more data/resolution/attention; illumination saturation/remedy is also asserted without supplied evidence. | Converts an observed confusion into unsupported clinical, causal, and remediation claims that a reviewer could challenge. | Separate observation from hypothesis; add appropriate primary support and experimental evidence, or explicitly qualify/remove the causal and remedy assertions. Evidence or qualification is also required for the light-saturation statement. | Open |
| B-04 | **HIGH** | Table 8: “Más datos, resolución 320 px, atención local.” | Introduces an exact, unevaluated design number; it is hard-coded rather than sourced through `values()` and may look like an evidence-based recommendation. | Remove the exact value, label it as a future experimental candidate without efficacy claim, or support it with a cited/prespecified resolution study. Register its source if retained. | Open |
| B-05 | **MEDIUM** | Abstract/methods/results/conclusion and REVIEW-03 emphasize a one-time current test evaluation but never say “evaluación interna retrospectiva.” | Can imply a pristine prospective holdout despite known historical access, contrary to the frozen reporting rule. | Add the required internal-retrospective qualification wherever the test's evidentiary status is summarized, including REVIEW-03, without implying current test-based selection. | Open |
| B-06 | **MEDIUM** | Section 4.1.2: “la prueba contenga montajes que el modelo no vio al entrenar.” | The artifacts establish disjoint registered groups, not this specific montage characterization or a causal explanation for the performance drop. | State the documented group separation only, or provide exact montage membership evidence; avoid causal attribution without an analysis. | Open |
| B-07 | **MEDIUM** | Section 4.2 reports only the principal 219-image/203-group M2 analysis. | Omits protocol-required disclosure of 11 within-split exact duplicates and the exact-SHA/cluster-weighted sensitivity results, understating dependence sensitivity. | Report the principal, exact-deduplicated, and cluster-weighted estimates/deltas together, with 2,000 paired group resamples and seed 42, and identify intra-split duplicate counts. | Open |
| B-08 | **MEDIUM** | `manuscript/numbers.json` / `reports/manuscript_consistency.json`: 26 checks, “no issues.” | The result may be read as comprehensive although most table cells, intervals, confusion values, latency values, and repetitions are unregistered. It also fails to expose unsupported 320 px. | Expand the registry/checker to all material numbers or clearly document scope and exceptions; ensure every current number has an authoritative artifact, including non-JSON sources. | Open |
| B-09 | **MEDIUM** | `reports/claim_evidence_matrix.csv` is not updated to the current results; required `reports/editorial_audit.md` is absent. | TASK-09 traceability is incomplete; current causal and temporal overclaims escape the automated “no issues” result. | Map every final material claim to exact evidence/location and disposition; complete the editorial audit; leave no critical UNVERIFIED/UNSUPPORTED claim. | Open |
| B-10 | **MEDIUM** | Response letter header says pending figures come from artifacts that “todavía no existen”; REVIEW-10 has `[PENDIENTE: ubicación]`; REVIEW-15 remains `[PENDIENTE]`. | The letter is factually stale and visibly unfinished; it cannot accompany a submission. | Update the header, resolve the substantive REVIEW-10 defect, complete the final-render REVIEW-15 audit, add exact locations, and remove every placeholder. | Open |
| B-11 | LOW | Figures 5 and 7, lower-panel overlay labels. | Crowding/edge truncation may reduce readability in the PDF, although underlying samples and counts are correct. | Confirm at final PDF scale that every label is legible and inside the panel; regenerate layout if not. | Open |
| B-12 | LOW | Figure 3 uses `0.761`; REVIEW-05 uses `[0.578, 0.957]`. | Minor Spanish decimal-punctuation inconsistency. | Use decimal commas consistently in visible Spanish prose/figures/letter, subject to journal style. | Open |
| B-13 | LOW | Figures 1 and 2 are approximately 134 and 142 ppi at current DOCX placement. | They may fail a journal raster-resolution requirement even though Figures 4–7 clear 300 ppi. | Check the journal specification and final PDF; replace with adequate-resolution or vector exports if required. | Open |

## Open-finding count

| Severity | Open |
|---|---:|
| HIGH | **4** |
| MEDIUM | **6** |
| LOW | 3 |

**Submission gate:** fail until HIGH = 0 and MEDIUM = 0, the final PDF has passed page-by-page inspection, the response letter contains no pending fields, and TASK-10 independently passes on the frozen final candidate.
