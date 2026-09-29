# TASK-05 independent methodological review

Date: 2026-09-23  
Scope: pre-inference review of the TASK-05 detection/classification evaluation and interval code. No inference, validation selection, test evaluation, network service, code fix, commit, or push was performed.

## Verdict

**DO NOT RUN EXP-V01, the operating-point freeze, EXP-R02, or EXP-R03 with the present package.** There are **4 open HIGH** and **4 open MEDIUM** findings. The metric formulae and bootstrap core are substantially correct, but the first test observation must wait until the cross-file contracts and provenance gates below are corrected and independently re-reviewed.

| Step | May run? | Reason |
|---|---:|---|
| EXP-V01 (M1 validation inference) | **NO** | PROTOCOL-AMENDMENT-008 v6 still permits only non-scientific probes; the final M1 manifest/freeze record and checkpoint binding are absent; the inference/evaluator trust chain is incomplete. |
| Operating-point freeze | **NO** | `evaluation.json` has no checkpoint hash, and the producer writes `frozen_threshold` while both downstream M1 consumers require `threshold`. |
| EXP-R02 (M1 test) | **NO** | Depends on EXP-V01/freeze; the test renderer cannot accept the config produced by the freezer, and final predictions are not proven to come from the checkpoint/config named in the reported metrics. |
| EXP-R03 (M2 test) | **NO** | The prediction path itself applies ART-002, 224 px and top-1 without rejection, but its output cannot be consumed by the frozen-plan M2 interval command because it does not declare `class_names`. This must be resolved before the single test inference, not after observing it. |

## Open findings

### HIGH-01 — M1 scientific execution is not currently authorized or fully frozen

- **Location:** `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.json:6-7,15,23`; `configs/evaluation.json:11`; absent `data/manifests/model1_clean_manifest.csv` and `data/manifests/model1_clean_manifest.freeze.json` (only A/B drafts exist).
- **Evidence:** amendment v6 is `PROPOSED_V6` with `execution_permitted = non_scientific_probes_only`; the renderer's authority record does not exist; `checkpoint_sha256` is null.
- **Consequence:** EXP-V01/EXP-R02 are outside the current authorization and cannot be bound to final membership/checkpoint bytes. `render_kaggle_job.approved()` cannot succeed without the missing freeze record, and `freeze_operating_point()` rejects the current config.
- **Resolution criterion:** approve the effective amendment through its independent-review gate, create and commit the final manifest plus freeze record/sidecars, select and seal the checkpoint, and populate a committed validation config whose identities match those authority records.

### HIGH-02 — The frozen-threshold schema is internally inconsistent

- **Location:** `src/evaluation/evaluate.py:380` writes `frozen_threshold`; `provenance/commands/task04/render_kaggle_job.py:101-105` requires `threshold`; `src/evaluation/evaluate.py:316-318` (`interval_metrics`) also requires `threshold`. `tests/test_evaluation.py:393` hides the incompatibility by constructing a synthetic config with `threshold` instead of using the freezer's output.
- **Consequence:** the config produced by the approved freeze path cannot render EXP-R02 and cannot compute M1 bootstrap intervals. Manually adding a second field after freezing would create two possible operating points and alter the sealed file outside the producing command.
- **Resolution criterion:** define one canonical field and use it in the freezer, renderer, scorer, and intervals hook; add an integration test that passes the actual freezer output unchanged through test-render validation and interval point-estimate calculation.

### HIGH-03 — EXP-R03 predictions cannot drive the prescribed M2 sensitivity command

- **Location:** `src/evaluation/predict_model2.py:41-43` omits `class_names`; `src/statistics/intervals.py:440-454` requires either per-record `class_names` or `--class-names`; the frozen TASK-05 command supplies neither. Existing CLI tests add `--class-names A,B` manually (`tests/test_intervals.py:339-342,347`).
- **Consequence:** after the one permitted M2 test inference, the required sensitivity estimates and CIs fail before computation. Supplying names manually would bypass the plan's requirement to obtain the fixed class names/order from `model.names` and would introduce a new post-test input.
- **Resolution criterion:** persist the actual ordered `model.names` in the prediction contract and make the documented command consume and verify it without an extra operator choice; cover predictor output -> `--m2-sensitivity` in one integration test.

### HIGH-04 — M1 final prediction records are not bound to the executed kernel and sealed checkpoint/config

- **Location:** `src/evaluation/kaggle_job.py:103-115` can verify executed source when `kernel_source` is supplied, but `provenance/commands/task05/build_predictions.py:50` omits it. `build_predictions.py:50-75` does not compare `receipt.checkpoint_sha256` or the inference config identity with local sealed values. `src/evaluation/evaluate.py:452-465` reports the checkpoint from the config, not from the prediction receipt, and does not verify `predictions.jsonl.sha256`.
- **Consequence:** the local metric artifact can attribute predictions to the configured checkpoint even though the accepted receipt/final JSONL has not locally proven that linkage. This breaks the twice-checked trust chain required by PROTOCOL-AMENDMENT-008 and can make otherwise reproducible numbers scientifically misattributed.
- **Resolution criterion:** verify the preserved rendered kernel against `kernel_source_sha256`; require COMPLETE or explicitly adjudicated `predictions_written` status; compare receipt checkpoint, config digest, phase and frozen settings to local sealed values; verify the final prediction sidecar; carry those verified identities into the metric artifact; add a negative end-to-end test for each mismatch.

### MEDIUM-01 — Evaluator and M2 manifest/config inputs are not anchored to their frozen authorities

- **Location:** `src/evaluation/evaluate.py:342-384` accepts any structurally valid config/manifest; `read_config()` validates neither `.001/.6/300/640` nor the threshold-grid declaration. `src/evaluation/predict_model2.py:58-60` and `src/statistics/intervals.py:427-437` accept any manifest accompanied by a matching adjacent sidecar, without checking the committed canonical identity.
- **Consequence:** accidental use of a self-consistent but wrong manifest/config can run under the fixed EXP identifiers. In the M1 freezer, a manifest whose split labels have drifted could turn non-validation records into the selection input; in M2 it could change membership or truth while retaining the label EXP-R03.
- **Resolution criterion:** bind canonical paths/digests to committed freeze records, reject drift, and enforce the frozen numeric settings and grid before prediction/freezing/scoring. Tests must reject a rehashed alternative manifest and altered frozen inference setting.

### MEDIUM-02 — The saved-prediction AP calculation is faithful only conditional on identical detections; the `model.val` cross-check is not guaranteed equivalent

- **Location:** `src/evaluation/kaggle_job.py:224-245` obtains saved boxes through one-image-at-a-time `model.predict()` and separately obtains cross-check metrics through batched `model.val()`. Ultralytics 8.4.52 uses prediction `rect=True` (`engine/model.py:524`) and validation rectangular batches (`engine/model.py:611-612`), so actual tensor shapes can differ by batch composition. No comparison or tolerance gate follows `model.val()`.
- **Consequence:** local AP from the saved boxes can legitimately differ from `receipt.ultralytics_val`, despite the amendment requiring coincidence to tolerance. The code currently records both and continues, leaving two candidate AP values.
- **Resolution criterion:** obtain the saved detections/statistics from the same inference/preprocessing pass as the authoritative AP, or prove identical preprocessing and enforce the predeclared numerical comparison with a single authoritative outcome and explicit failure record.

### MEDIUM-03 — Operational matching and AP matching differ at the IoU boundary

- **Location:** `src/evaluation/evaluate.py:181-198` computes operational IoU with Python binary64. AP calls Ultralytics `box_iou` at `evaluate.py:273-275`; 8.4.52 `utils/metrics.py:96-102` explicitly casts both tensors to float32, so the supplied float64 dtype does not make AP float64.
- **Evidence:** for boxes `[0,0,1,1]` and `[1/3,0,4/3,1]`, the operational path gives `0.5000000000000001`, while Ultralytics gives `0.49999991059303284`; the former matches at 0.5 and the latter does not.
- **Consequence:** a geometrically boundary-level pair can be TP in the frozen-point confusion/P/R/F1/F2 and FP+FN in AP@0.5. The difference is rare but can change an unrounded count and therefore a reported metric.
- **Resolution criterion:** freeze one explicit numeric/coordinate-space policy for the 0.5 match and apply it consistently where comparability is claimed, or predeclare the difference and prove that no evaluated candidate lies within a justified tolerance of an IoU threshold.

### MEDIUM-04 — Effective YOLO26 inference mode and the M1 input contract are not recorded in the run receipt

- **Location:** `src/evaluation/kaggle_job.py:216-247`; 8.4.52 `models/yolo/detect/val.py:117-126`; `utils/nms.py:66-70`; pinned `cfg/models/26/yolo26.yaml:9` sets `end2end: True`. M2 records `input_contract = Ultralytics file-path loader` (`predict_model2.py:88-94`), but M1 records neither that contract nor `model.end2end`/effective NMS mode.
- **Consequence:** `.001`, `max_det=300`, and `imgsz=640` are passed in the current M1 code, and `.6` is passed as `iou`; however, for an end-to-end checkpoint the NMS helper returns before using the IoU threshold. A report could therefore describe NMS IoU 0.6 as effective when suppression was NMS-free, contrary to SPEC section 7's requirement to register the effective mode. The correct file-path colour contract is also implicit rather than recorded for M1.
- **Resolution criterion:** record the runtime `end2end`, effective NMS/agnostic/single-class settings, actual tensor/preprocessing contract and all frozen arguments in the receipt, and reconcile the report language with what the pinned runtime actually executed.

### LOW-01 — M2 exact-tie top-1 does not follow model-index order

- **Location:** `src/evaluation/predict_model2.py:39-43` sorts class names lexicographically before `max`; Ultralytics `probs.top1`/array argmax resolves an exact tie by the first model index.
- **Consequence:** an exact probability tie can select a different class from the model's native top-1, although this is unlikely for ordinary logits.
- **Resolution criterion:** derive top-1 from model-index order (or the runtime's `top1`) and test an exact tie.

### LOW-02 — `wilson()` does not enforce its integer Bernoulli contract

- **Location:** `src/statistics/intervals.py:46-54` annotates `k` and `n` as integers but accepts finite/infinite floats and arbitrary `z` values if the inequalities happen to pass.
- **Consequence:** a future caller could report a Wilson interval for weighted/non-binomial counts even though the SPEC permits it only for justified independent Bernoulli trials. Current TASK-05 calls do not exercise this misuse.
- **Resolution criterion:** reject non-integer/bool counts and non-positive/non-finite `z`, with a small contract test.

## Confirmed methodological behavior

1. **Formulae:** classification and detection P/R/F1 use unrounded float counts. F2 is exactly `5PR/(4P+R)`. Zero denominators remain `None`; a class with GT support but no correct prediction can have F1 = 0. Macro-F1 covers every fixed real class and becomes undefined if any class F1 is undefined. Detection background is only the last confusion row/column, never a real class or true negative, and detection accuracy is not reported.
2. **Operating point:** the grid is exactly 0.05 through 0.95 by 0.05; strict improvement while traversing ascending values gives the lower threshold on ties. The direct selection API rejects records marked `test`, and the CLI freezer loads only manifest split `valid`. This validation-only rule still needs the frozen-manifest anchoring in MEDIUM-01.
3. **One-to-one confusion matching:** candidates are globally ordered by descending IoU then stable list indices, with each GT and prediction consumed once. Matching is class-agnostic; a wrong-class overlap becomes an off-diagonal error. Unmatched GT/predictions become background FN/FP.
4. **AP implementation:** on the same saved detections, the code uses the same 8.4.52 `box_iou`, `BaseValidator.match_predictions`, IoU vector 0.50:0.05:0.95, confidence ranking, and `ap_per_class` slices as `DetectionValidator`/`DetMetrics`. The implementer's perfect-ranking result is **confirmed**: 8.4.52's 101-point interpolation has a zero endpoint at recall 1 and integrates to **0.995**, not 1.0. AP means are deliberately made undefined when a fixed class has no GT; actual Ultralytics `Metric.map` averages its AP rows, so this is stricter than `model.val` on an absent-class split but consistent with the frozen undefined-value policy.
5. **Bootstrap:** unique sorted `group_id` values are sampled with replacement; all records of a selected group stay together; draw position is the occurrence ID; SHA deduplication and cluster masses are occurrence-scoped. All estimands/metrics/deltas share the same saved draws and digest. `>5%` undefined blocks while exactly 5% passes, `<2` groups or `<2` supporting groups per required class blocks, and defined draws use the linear inclusive 2.5/97.5 percentiles (equivalent to NumPy's default linear percentile). M1 detection records derive per-group support from GT `gt_classes`, once per group.
6. **M2 estimands:** independent arithmetic on the plan fixture reproduced:

   | estimand | confusion (rows truth A/B) | accuracy | F1 A | F1 B | macro-F1 | accuracy delta |
   |---|---|---:|---:|---:|---:|---:|
   | image-weighted | `[[1,2],[0,1]]` | 1/2 | 1/2 | 1/2 | 1/2 | — |
   | exact-SHA-dedup | `[[1,1],[0,1]]` | 2/3 | 2/3 | 2/3 | 2/3 | 1/6 |
   | cluster-weighted | `[[1/3,2/3],[0,1]]` | 2/3 | 1/2 | 3/4 | 5/8 | 1/6 |

   The code chooses the lexicographically minimum `image_id`, rejects conflicting GT within an exact SHA set, and reports prediction conflicts for investigation.
7. **Frozen M2 manifest:** SHA256 is `cd4f0d0e428fc3015268b7df541bf705261893c4b5cba0a7ef274e17d0680d92`, matching its sidecar. It contains 1,500 unique IDs (1,064 train, 217 val, 219 test). Test has 208 unique SHA values, 203 clusters/groups, no SHA/cluster cross-group or cross-split, no GT conflict among equal SHA copies, and per-class group support of 37/45/43/42/36; the static `<2` support gate is therefore satisfiable for every class (draw-level undefined fractions remain outcome-dependent).
8. **Prediction-before-metrics discipline:** M1 writes and hashes `predictions_raw.jsonl` and marks `predictions_written` before calling `model.val`; M2 writes and hashes `predictions.jsonl` before printing its non-metric image/hash receipt. Neither test inference path contains threshold/checkpoint selection. The M1 test renderer is intended to require a committed frozen config, but HIGH-01/02/04 prevent relying on that path now.
9. **BGR/RGB and resize contract:** the new M1 and M2 inference calls pass file paths. In 8.4.52, the path loader reads BGR and predictor preprocessing converts BGR -> RGB. The legacy gallery first converts BGR -> RGB and then passes a NumPy array; NumPy inputs are treated as already OpenCV/BGR and predictor preprocessing reverses them again, so the legacy path feeds channel-swapped BGR to the tensor. They are **not equivalent**. Using the file-path loader is the acceptable API-conformant choice and avoids copying the legacy error; comparisons to legacy gallery output must declare the input-pipeline difference. M2 does declare it; M1 needs the run-record evidence in MEDIUM-04.

## Verification performed

- Installed package inspected directly: Ultralytics **8.4.52**.
- Exact requested command:

  `& .\.venv\Scripts\python.exe -m unittest tests.test_evaluation tests.test_intervals tests.test_predict_model2 -v`

- Result: **65 tests run, all passed, exit code 0, 10.400 s**.
- Independent fixture arithmetic and the IoU boundary calculation were run without importing the implementation under review for the arithmetic result.

Passing unit tests do not close the findings because the principal blockers are cross-file producer/consumer and provenance contracts that the current tests do not exercise.
