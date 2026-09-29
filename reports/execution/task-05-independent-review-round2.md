# TASK-05 independent methodological review — round 2

Date: 2026-09-23  
Remediation reviewed: `3175d7e..9e3b0bc`, restricted to the TASK-05 evaluation/statistics implementation, configuration, prediction builder, Kaggle job, and their tests. The scoped files are unchanged between `9e3b0bc` and the current `HEAD` (`81b861a`).  
Scope: pre-inference research-methodology review. No model inference, validation selection, test evaluation, Kaggle/network access, code fix, commit, or push was performed.

## Verdict

**DO NOT RUN EXP-V01, the operating-point freeze, EXP-R02, or the complete EXP-R03 evaluation pipeline with this code, even after the final M1 manifest, approved venue amendment, and sealed checkpoint exist.** Counting every `OPEN` or `PARTIALLY CLOSED` finding as open, there are **4 open HIGH** and **2 open MEDIUM** findings.

The remediation correctly fixes the threshold field name, M2 class-name persistence, the duplicate AP path, float32 IoU arithmetic, the M2 exact-tie rule, and the Wilson argument contract. It does not yet enforce the full authority, prediction-provenance, frozen-config, or downstream manifest bindings required before a one-time test observation.

## Binding authority checked

- `provenance/protocol_freeze.json` and `.md`, especially the immutable test-access, checkpoint, operating-point, prediction, and grouped-bootstrap rules.
- `docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md` sections 6–7.
- `docs/superpowers/plans/2026-09-17-albus26-major-revision.md` TASK-05, including the exact M1/M2 interval commands.
- Round-1 report and the author's response.

Current-state facts were used only to exercise gates, not as the reason for the code verdict: PROTOCOL-AMENDMENT-008 remains `PROPOSED_V6` with `execution_permitted = non_scientific_probes_only`; the final M1 manifest/freeze record and frozen evaluation config are absent; `configs/evaluation.json` still has null checkpoint and manifest hashes.

## Verification performed

Required command, with bytecode writes disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -m unittest tests.test_evaluation tests.test_intervals tests.test_predict_model2 tests.test_kaggle_job -v
```

Result: **102 tests run, all passed, exit code 0, 22.177 s**.

Independent in-memory checks:

- `_iou` versus `ultralytics.utils.metrics.box_iou`: **10,005/10,005 exactly equal**, maximum absolute difference `0.0`, and zero decisions differing at IoU 0.5. Cases included the round-1 `1/3` boundary, identical/disjoint/touching boxes, large coordinates, and 10,000 deterministic random box pairs.
- M2 exact tie: probabilities tied at model indices 0 and 1 selected index 0, as required.
- The adversarial acceptances described below were reproduced without writing fixtures to the repository.

Passing tests do not close the remaining findings because the missing checks are cross-command authority and artifact-binding gates not exercised by the suite.

## Round-1 finding disposition

| Round-1 finding | Status | Evidence checked |
|---|---|---|
| **HIGH-01 — M1 execution not authorized/frozen** | **OPEN** | The final-manifest part is enforced through the committed freeze record (`render_kaggle_job.py:53-60,79-84`). However, `approved()` reads `approved_code` from any committed amendment and never checks `state`, `execution_permitted`, the v6 review verdict, or approval scope. An in-memory `PROPOSED_V6` / `non_scientific_probes_only` amendment was accepted. For validation prediction, the renderer also accepts a caller-provided checkpoint digest without proving a local checkpoint-selection/seal record (`render_kaggle_job.py:90-93,123-130`). Thus adding the currently missing files would not by itself close the gate. |
| **HIGH-02 — inconsistent threshold schema** | **CLOSED** | The freezer writes only `threshold` and places the search results in `threshold_grid_values` (`evaluate.py:416-420`). The renderer, scorer, and interval hook all read `threshold` (`render_kaggle_job.py:101-105`; `evaluate.py:322-324,423-439`). The actual freezer output feeds `interval_metrics` unchanged. The separate failure to authenticate that threshold in the interval CLI is NEW-HIGH-02 below, not a field-name inconsistency. |
| **HIGH-03 — EXP-R03 lacks class names** | **CLOSED** | Every predictor record carries the actual `model.names` index order (`predict_model2.py:42-47`), and `_class_names` consumes that declaration without the plan command adding `--class-names` (`intervals.py:444-458`). A predictor-produced record resolved to the expected ordered names in the independent check. The incomplete-per-record validation is NEW-LOW-01. |
| **HIGH-04 — M1 predictions not bound to kernel/checkpoint/config** | **PARTIALLY CLOSED** | Kernel source, payload, COMPLETE status, phase, checkpoint, four inference settings, raw prediction bytes, final JSONL sidecar, and carried provenance are now checked. But `verify_prediction_run` ignores the payload's `config_sha256` and does not return it (`kaggle_job.py:132-154`), while `build_predictions.py` writes the *current local* config hash after that incomplete verification (`build_predictions.py:84-87`). A kernel carrying deliberately wrong config and manifest digests was accepted. `verified_provenance` then checks only prediction bytes and checkpoint, accepting a provenance record naming a different phase, config, and manifest (`evaluate.py:375-390`). |
| **MEDIUM-01 — evaluator/M2 inputs not anchored** | **PARTIALLY CLOSED** | M1 freeze/scoring and M1 intervals now compare the manifest digest in the config; four inference values and the grid declaration are fixed. The M2 predictor requires the canonical path and digest, which exactly match the current manifest and sidecar (`cd4f0d0e...680d92`). Remaining gaps: `read_config` still accepts `iou_match != 0.5`, a different class order/positive class/model ID, and any non-canonical config with those fields (`evaluate.py:348-366`). The M2 interval command accepts any alternative grouping manifest; its sidecar is optional, there is no canonical digest/path check, and truth is not reconciled with manifest `class_name` (`intervals.py:30-31,376-441,621-648`). An alternative `ALT-G` group was accepted in memory. |
| **MEDIUM-02 — two non-equivalent AP paths** | **CLOSED** | `_predict` no longer calls `model.val`; the saved detections are the only AP source (`kaggle_job.py:252-276`). |
| **MEDIUM-03 — binary64 versus Ultralytics float32 IoU** | **CLOSED** | `_iou` now duplicates float32 conversion and `1e-7` denominator epsilon (`evaluate.py:184-191`). It matched `box_iou` exactly for all 10,005 independent cases, including the prior boundary counterexample (`0.49999991059303284` in both implementations). |
| **MEDIUM-04 — effective inference mode/input contract not recorded** | **PARTIALLY CLOSED** | The receipt now records `end2end`, the file-path/BGR-to-RGB contract, and explicit conf/IoU/max-det/imgsz/device/half/batch arguments (`kaggle_job.py:252-270`). It still does not explicitly record `agnostic_nms`, `single_cls`, or a resolved effective suppression mode, and `verify_prediction_run` accepts and propagates missing `end2end`/`input_contract` instead of requiring the evidence (`kaggle_job.py:149-154`). The in-memory consistent receipt with both absent was accepted. |
| **LOW-01 — M2 exact tie uses lexical order** | **CLOSED** | Top-1 now maximizes `(probability, -model_index)` and therefore uses the first model index on exact ties (`predict_model2.py:42-47`). Independent tie result: `Saludable`, the index-0 class. |
| **LOW-02 — Wilson integer/Bernoulli contract not enforced** | **CLOSED** | `wilson` rejects bool/non-integer counts and non-finite/non-positive `z` (`intervals.py:46-53`); the new negative tests pass. |

## Open residual findings

### HIGH-01 — The renderer does not authenticate venue approval or the sealed checkpoint authority

- **Location:** `provenance/commands/task04/render_kaggle_job.py:53-60,79-84,90-93,123-130`; `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.json:6-8`.
- **Consequence:** once a final manifest freeze record is added, the current committed `PROPOSED_V6` amendment is sufficient for `approved()` even though it permits only non-scientific probes. EXP-V01 rendering also needs only a caller-supplied digest, not a checked checkpoint-selection/seal authority. Scientific inference can therefore begin before the two other stated preconditions are proven.
- **Resolution criterion:** make the trusted authority record explicitly assert an approved state, permitted EXP-V01/EXP-R02 scope, completed independent review, and the approved renderer/job identities; bind the selected checkpoint digest to a committed selection/seal record and verify it before rendering either validation or test inference.

### HIGH-04 — The M1 prediction/config trust chain is still incomplete

- **Location:** `src/evaluation/kaggle_job.py:132-154`; `provenance/commands/task05/build_predictions.py:42-59,84-87`; `src/evaluation/evaluate.py:375-390,489-503`.
- **Consequence:** a receipt/kernel pair from a different config file is accepted when checkpoint and four inference values happen to match. The builder then labels it with the current local config hash, and scoring accepts provenance that names a different config, manifest, or phase. Metric artifacts can therefore claim a configuration identity that was never verified against the executed payload.
- **Resolution criterion:** pass the local config bytes/digest and manifest digest into `verify_prediction_run`; require equality with payload and render record; return those verified identities; require scoring to compare prediction provenance phase/config/manifest/inference/kernel identities with its current inputs, not merely checkpoint and prediction hash. Add one negative test per binding.

### MEDIUM-01 — Frozen configuration and M2 post-processing inputs remain only partly anchored

- **Location:** `src/evaluation/evaluate.py:348-372`; `src/statistics/intervals.py:30-31,376-458,621-648`; `src/evaluation/predict_model2.py:20-25,62-67`.
- **Consequence:** M1 can freeze/select with a non-protocol matching IoU (0.4 was accepted), another positive class/order, or an alternative otherwise-valid config. M2 inference itself uses the canonical manifest, but sensitivity/CI post-processing can replace group/cluster membership and can change `truth` because it neither authenticates the predictor artifact nor checks truth against the manifest. That changes estimands and bootstrap dependence without changing the EXP-R03 label.
- **Resolution criterion:** enforce all fixed M1 values (`model_id`, ordered names, positive class, IoU 0.5, inference settings, grid) and authenticate the canonical config; in M2 intervals require the canonical manifest path/digest and mandatory sidecar, verify `predictions.jsonl` against its sidecar and `run_record.json`, and reconcile each truth with frozen manifest `class_name`.

### MEDIUM-04 — Runtime-mode evidence is recorded but neither complete nor required

- **Location:** `src/evaluation/kaggle_job.py:149-154,252-270`.
- **Consequence:** the preserved receipt does not explicitly state the effective suppression mode or the agnostic/single-class settings, and the verifier accepts `None` for the two new evidence fields. A metrics artifact can therefore pass the trust gate without the evidence needed to state whether IoU 0.6 actually governed suppression.
- **Resolution criterion:** record explicit `agnostic_nms`, `single_cls`, model `end2end`, and resolved effective suppression mode; require exact expected values and a non-empty input contract during receipt verification; carry them unchanged into prediction and metric provenance.

## New findings

### NEW-HIGH-01 — The operating-point freezer accepts unauthenticated validation predictions

- **Location:** `src/evaluation/evaluate.py:404-420` versus the provenance check used only by scoring at `evaluate.py:375-390,489-493`.
- **Evidence:** `freeze_operating_point` checks record structure, validation split, manifest membership, and a syntactically valid checkpoint hash in the config, but never requires the prediction sidecar or `prediction_provenance.json` and never verifies that EXP-V01 used that checkpoint/config/kernel. It then hashes whatever prediction file was supplied into the frozen config.
- **Consequence:** predictions from another checkpoint—or synthetic validation predictions with matching IDs/hashes—can choose the scientific operating point and then become apparently sealed. This directly affects the one threshold later applied to test.
- **Resolution criterion:** before F2 selection, require and verify EXP-V01 prediction sidecar/provenance with phase `valid`, the executed kernel/config/manifest/checkpoint identities, and frozen inference settings; reject every mismatch. Exercise the actual EXP-V01 builder output through the freezer and add negative wrong-checkpoint/config tests.

### NEW-HIGH-02 — The prescribed M1 interval command cannot run, while the undocumented workaround accepts an unsealed/off-grid threshold

- **Location:** frozen TASK-05 command at plan line 288 / protocol-freeze line 501; `src/statistics/intervals.py:595-617,621-648`; `src/evaluation/evaluate.py:315-345,348-366`.
- **Evidence:** the frozen command supplies no `--config`, but `_run_m1` rejects unless one is added. If an operator adds the undocumented option, `_run_m1` calls `read_config` and `interval_metrics` directly rather than the sealed-config validator: no `.sha256` sidecar is required and any non-null threshold is accepted. An in-memory threshold `0.123` was accepted.
- **Consequence:** the required M1 CIs fail under the approved command. A manual workaround can compute test intervals at a post-test, non-grid threshold different from the scored point estimate.
- **Resolution criterion:** implement the frozen command deterministically (for example, derive the canonical frozen config from authenticated prediction provenance) or obtain an approved protocol amendment for the explicit option; in either case use one shared validator that requires the frozen config sidecar, manifest hash, checkpoint/provenance identities, and a grid-valid threshold before interval calculation.

### NEW-LOW-01 — M2 class-name declaration is not required on every prediction record

- **Location:** `src/statistics/intervals.py:444-458`.
- **Evidence:** `_class_names` collects only records with a truthy `class_names`; a two-record file in which only one record declared the list was accepted.
- **Consequence:** a partially malformed or concatenated prediction file can inherit its class-order contract from one row instead of proving one consistent producer contract for the whole run. The current predictor writes the field on every row, so this does not affect an intact output.
- **Resolution criterion:** require every M2 record to carry the same exact ordered class list, or move the list to an authenticated run-level record and require the prediction file to bind to that record.

## Confirmed remediation behavior

- The canonical field is now `threshold` across freezer, renderer, scorer, and interval metric construction.
- The M2 predictor preserves actual model-index order, and exact ties use the first model index.
- M2 frozen manifest digest, sidecar, and predictor constant agree: `cd4f0d0e428fc3015268b7df541bf705261893c4b5cba0a7ef274e17d0680d92`.
- The second `model.val` AP result is gone; AP is computed only from saved detections.
- Float32 operational IoU is an exact replication of the installed Ultralytics 8.4.52 `box_iou` for the checked cases.
- Wilson now enforces integer counts and a finite positive `z`.

## Final run decision after the stated external prerequisites exist

| Step | May run? | Remaining code reason |
|---|---:|---|
| EXP-V01 — M1 validation inference | **NO** | The renderer does not prove venue approval or checkpoint-seal authority, and the executed config digest is not part of the verified receipt binding. |
| Operating-point freeze | **NO** | Validation predictions are not authenticated to EXP-V01/checkpoint/config before they select and seal the threshold. |
| EXP-R02 — M1 test | **NO** | The prediction/config provenance chain remains incomplete, runtime-mode evidence is not required, and the approved M1 interval command either fails or can use an unsealed threshold. |
| EXP-R03 — M2 test | **NO for the complete EXP-R03 pipeline** | The inference producer itself now enforces ART-002, the canonical M2 manifest, 224 px, top-1, class names, and the correct tie rule. However, the required sensitivity/CI consumer can substitute an unauthenticated manifest/prediction truth contract. The single test observation should wait until that downstream path is sealed. |

**Open count: HIGH 4; MEDIUM 2.**
