# TASK-05 independent methodological review — round 4

Date: 2026-09-25  
Scope: pre-inference review of TASK-05 evaluation, statistics, and provenance after commit `2bff016`. No model inference, validation selection on research data, test evaluation, Kaggle/network access, code fix, commit, or push was performed.

## Verdict

**DO NOT APPROVE the M1 inference chain (`EXP-V01` → operating-point freeze → `EXP-R02` → M1 intervals) with this code, even after `EXP-R01` and its selection record exist and are committed. Do not approve the overall inference package, including `EXP-R03`, under the frozen TASK-05 commands.**

The patch closes the canonical M2-manifest defect and the no-flag M2 routing defect, and it materially improves the M1 checks. It does not establish an external/committed trust root for the M1 run evidence: a completely synthetic raw prediction file plus a correspondingly rewritten receipt and derived artifacts is accepted and can select a different threshold. The frozen M1/M2 inference commands also do not match the implemented CLIs. A prediction attempt that reaches `predictions_written` and then fails is definitive under Amendment 008 but is unconditionally rejected by the evaluator.

Counting `PARTIALLY CLOSED` findings as open, this review has **4 open HIGH** and **3 open MEDIUM** findings.

## Binding authority and limits

Reviewed before implementation evidence:

- immutable `provenance/protocol_freeze.json` and `provenance/protocol_freeze.md`;
- SPEC sections 6, 7, 11, and 12;
- frozen plan TASK-05, including the exact commands at plan lines 284–291;
- PROTOCOL-AMENDMENT-008 sections 4 and 5;
- prior gate review Part C and its counterexamples;
- `git show --stat 2bff016` (`10 files changed, 998 insertions, 711 deletions`).

The frozen protocol requires validation-only threshold selection, a byte-sealed config, one derivation through `evaluate.rebuild_predictions`, committed selection authority, fixed evaluator bytes, saved per-image predictions, and grouped uncertainty. Amendment 008 section 5 expressly says a separately authored provenance record is never sufficient.

The authority is **silent** on cryptographic signatures, an independent custodian, and a mandatory platform attestation format; Amendment 008 section 4 explicitly declares that no independent custodian exists. The findings below therefore do not require a new custodian or signature. They require the existing committed/platform/reconciliation evidence to be checked, or another frozen non-self-authenticating root to be defined. The authority is also silent on the exact fields that constitute `test_selection_digest`; the implementation's `image_id + image SHA256 + label SHA256` definition is not faulted because the whole manifest is separately hashed. It does not define probability-normalization tolerances, so no finding is raised about their absence.

Current-state note, not counted as a code finding: Amendment 008 is still `PROPOSED_V7`, `execution_permitted = non_scientific_probes_only`, and has no `inference_approved = true`; `configs/evaluation.json` still has null checkpoint/manifest/selection identities. The verdict below is the requested prospective verdict after those ordinary preconditions are populated.

## Verification performed

Each required test module ran in its own process with bytecode writes disabled:

| Command | Result |
|---|---|
| `.\.venv\Scripts\python.exe -m unittest tests.test_evaluation -v` | 49 tests, pass, exit 0, 10.075 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_intervals -v` | 30 tests, pass, exit 0, 1.768 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_predict_model2 -v` | 6 tests, pass, exit 0, 0.024 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_kaggle_job -v` | 40 tests, pass, exit 0, 0.164 s |

Total: **125 passed, 0 failed**. Passing tests do not close the findings because the new negative tests mostly mutate one artifact while leaving a stale dependent hash; they do not replace the chain with a fully rehashed alternative.

Two frozen commands were also invoked only far enough to exercise argument parsing:

- The exact validation command (`evaluate --model-id model1 ... --run-dir experiments/model1/EXP-V01`) exited before work because current `evaluate.main` requires `--freeze-operating-point|--score`, `--predictions`, `--manifest`, and `--out`.
- The exact freeze command exited before work because it omits the now-required `--manifest`.

No repository fixture was written for the adversarial checks; isolated temporary fixtures were removed after execution.

## Counterexample replay and new falsification cases

| Case | Observed result | Interpretation |
|---|---|---|
| Prior ALT-G M2 manifest passed directly to `authenticate_m2` | **REJECTED**: `only the committed frozen M2 manifest is accepted` | Prior M2 manifest substitution is closed. |
| Prior incomplete self-authored M1 provenance, missing `kernel_source_sha256`, passed to `verified_provenance` and `freeze_operating_point` | **REJECTED** by both: provenance differs from rebuilt identities | The narrow prior counterexample is closed. |
| Synthetic validation raw predictions; receipt `predictions_raw_sha256`, final JSONL, sidecar, and provenance all recomputed | **ACCEPTED** by `verified_provenance` and `freeze_operating_point`; selected threshold became **0.05** | A complete self-consistent substitute remains accepted; the validation-selection authority is not authenticated. |
| Kernel re-rendered from a payload naming `OTHER-EXP`, with render record and receipt recomputed | **ACCEPTED** | `experiment_id` and the phase-specific EXP identity are not enforced by `verify_prediction_run`. |
| Receipt changed from `end2end=true` to `false`, with `effective_suppression` recomputed consistently | **ACCEPTED** | The receipt supplies both the asserted runtime mode and the expected string; there is no independent expected `end2end` value. |
| Receipt `agnostic_nms=true`, `single_cls=true`, or alternative input contract | **REJECTED** by existing tests | These exact-value parts of MEDIUM-04 are fixed. |
| Receipt `model_names` reversed, or `predict_args` replaced with different conf/IoU/max-det/imgsz/device/half/batch | **ACCEPTED** | `_predict` writes both fields, but neither verifier nor rebuilt provenance checks/carries them. |
| Labels, image hashes, manifest, config, checkpoint digest, selection record, kernel version, payload, render record, and receipt replaced together and rehashed | **ACCEPTED**; checkpoint `dddddddd…`, kernel version `9`, and a new test-selection digest were sealed | The new hashes are self-seals unless the consumers also enforce the committed authority used by the renderer. |
| Evaluator byte mutation | Static result: a stale frozen hash is rejected, but changed evaluator bytes can be accepted if a new config/sidecar is generated because `code_hashes()` hashes the current worktree and `freeze_operating_point` does not require reviewed/committed evaluator bytes | The byte check is useful after a trustworthy freeze; the freeze producer itself is not rooted. No source file was modified for this check. |
| Frozen primary M2 interval command without `--m2-sensitivity` | **ACCEPTED in the CLI integration test** and dispatched to `_run_m2_intervals` | NEW-MEDIUM-01 is closed. |
| M2 prediction label that does not equal top-1 of its probabilities | **REJECTED** in `tests.test_intervals.Cli` | The top-1/no-rejection rule and exact-tie order are enforced. |
| Real-style receipt with `status=FAILED`, `stage=predictions_written`, and retained raw-prediction digest | **REJECTED**: `only a COMPLETE predict run can supply predictions` | This conflicts with the amendment's definitive-after-predictions rule unless the intended outcome is a permanently blocked Gate E with no metrics. |

The key distinction is that `tests.test_evaluation.make_run` itself creates a synthetic local kernel, render record, receipt, and raw predictions without platform evidence, and `test_the_intact_chain_passes` proves that this synthetic chain is accepted. Rebuilding a self-authored chain is not independent authentication of its execution.

## Prior-finding disposition

| Prior finding | Status | Evidence |
|---|---|---|
| **HIGH-04 — executed-kernel prediction chain not authenticated at consumers** | **PARTIALLY CLOSED** | `verified_provenance` now reruns `rebuild_predictions` and rejects a missing/altered provenance field. However, `rebuild_predictions` checks only mutually consistent local kernel/render/receipt/raw bytes. It does not require the phase's committed attempt/reconciliation/platform evidence, a committed receipt hash, or the expected EXP identity. A completely regenerated synthetic chain passed. |
| **NEW-HIGH-01 — validation predictions can select the threshold without authentication** | **PARTIALLY CLOSED** | Replacing only final predictions/sidecar/provenance is rejected. Replacing raw predictions and recomputing the receipt plus derived artifacts is accepted and changed the chosen threshold to 0.05. |
| **NEW-HIGH-03 — operating-point artifact does not seal evaluator/training-selection authority** | **PARTIALLY CLOSED** | The freezer now emits and `sealed_config` checks evaluator hashes, test-selection digest, selection-record hash, checkpoint, and training kernel version. One-field mutations fail. But the freezer hashes current worktree bytes and current selection bytes without verifying that evaluator/config/selection authorities are committed and reviewed; the fully rehashed alternative authority chain passed. |
| **MEDIUM-01 — M2 post-processing accepts noncanonical grouping manifest** | **CLOSED** | `authenticate_m2` requires canonical resolved paths/digests and sidecars, fixed contract fields, exact test coverage, manifest truth, one class order per record, and top-1 re-derivation. ALT-G and the mismatching-label case are rejected. |
| **MEDIUM-04 — downstream runtime-mode evidence weaker than receipt verification** | **PARTIALLY CLOSED** | Exact false `agnostic_nms`/`single_cls` and exact `INPUT_CONTRACT` are now required. A paired alternative `end2end`/suppression assertion is still accepted, and `_predict`'s `predict_args` and `model_names` are ignored. |
| **NEW-MEDIUM-01 — frozen primary M2 interval command routes to M1** | **CLOSED** | Canonical M2 manifest path selects M2 before the sensitivity flag; without the flag, `_run_m2_intervals` writes the primary image-weighted output. The integration test covers this no-flag route. |

## Open and new findings

### HIGH-04 — HIGH — Rebuilding an internally consistent local run is not execution authentication

- **Location:** `tests/test_evaluation.py:106-142,372-399,540-557`; `src/evaluation/evaluate.py:442-528`; `src/evaluation/kaggle_job.py:200-247`.
- **Consequence:** a local author can create or replace kernel/payload/render/receipt/raw-prediction evidence, recompute every dependent digest, and obtain accepted predictions and provenance without the recorded platform attempt. Metrics can be attributed to an execution that did not occur. The accepted `OTHER-EXP` payload shows that even the required EXP identity is not checked.
- **Resolution criterion:** make every consumer verify a non-self-authored retained root for the selected attempt: at minimum the committed attempt/reconciliation record, expected `EXP-V01`/`EXP-R02` identity and attempt, retained platform/output identifiers, and committed hashes of kernel, render record, receipt, and raw predictions. A cryptographic custodian is not required. Add an end-to-end negative test that regenerates all local hashes, not a one-file stale-hash test.

### NEW-HIGH-01 — HIGH — A fully rehashed synthetic validation run still selects the operating point

- **Location:** `src/evaluation/evaluate.py:512-562`; `tests/test_evaluation.py:546-557`.
- **Consequence:** the added synthetic-prediction test changes only the final derived file while leaving raw predictions untouched. The stronger case changed the raw detections, updated the receipt digest, rebuilt final artifacts, and was accepted; the threshold changed from the fixture's 0.35 to 0.05. Test inference can therefore be governed by a non-executed validation result.
- **Resolution criterion:** close HIGH-04's attempt root before F2 selection, require the exact authorized `EXP-V01` attempt identity, and retain a negative test in which raw predictions, receipt, derived JSONL, sidecar, and provenance are all mutually consistent but lack that root.

### NEW-HIGH-03 — HIGH — The new operating-point hashes are self-sealing at freeze creation

- **Location:** `src/evaluation/evaluate.py:389-428,542-562`; `provenance/commands/task04/render_kaggle_job.py:165-178`.
- **Consequence:** `sealed_config` detects later byte drift, and the test renderer checks committed cleanliness. But `freeze_operating_point` can create the seal from uncommitted/replaced evaluator, manifest, selection, checkpoint, and kernel-version claims. A fully consistent alternative checkpoint/selection/kernel-version chain was accepted. This fails Amendment 008 section 4's premise that the selection record is committed and evaluator code is versioned before the seal becomes authority.
- **Resolution criterion:** before producing the frozen config, require canonical paths plus committed-clean reviewed bytes for `evaluation.json`, the M1 manifest/sidecar/freeze record, selection record, and all three sealed code files; bind the approved amendment/job identity. Test a fully rehashed alternative, including selection record and code hash, rather than only a stale hash.

### NEW-HIGH-04 — HIGH — A definitive post-prediction failure has no compliant evaluation path

- **Location:** Amendment 008 section 4 line 67; `src/evaluation/kaggle_job.py:357-371,460-492`; `src/evaluation/kaggle_job.py:229-230`; `src/evaluation/evaluate.py:483-488`.
- **Consequence:** `_predict` writes and hashes `predictions_raw.jsonl`, then durably sets `stage=predictions_written`. Any later exception makes the final receipt `FAILED`. The amendment makes that attempt definitive and forbids replacement, but `verify_prediction_run` accepts only `COMPLETE`; the preserved one-time observation can neither be rebuilt nor retried. This is especially consequential for `EXP-R02`.
- **Resolution criterion:** define and implement the amendment's intended disposition. Either (a) accept an explicitly reconciled `FAILED` receipt that reached `predictions_written`, while preserving Gate E failure and the later error, or (b) amend section 4 to state that such an attempt yields no metrics and permanently blocks the dependent result. Add a real `_predict` → later-failure test.

### MEDIUM-04 — MEDIUM — Effective runtime evidence is still partly asserted by the receipt itself

- **Location:** `src/evaluation/kaggle_job.py:221-247,468-476`; `src/evaluation/evaluate.py:483-509`.
- **Consequence:** exact false agnostic/single-class flags and the input-contract string are enforced, but either boolean `end2end` is accepted if the receipt also supplies the corresponding suppression description. `predict_args` is ignored. A re-authored receipt can therefore change the claimed effective suppression mode without rejection.
- **Resolution criterion:** derive the expected end-to-end mode from the sealed checkpoint/runtime evidence (or verify it through the retained non-self-authored run root), compare every `predict_args` field exactly with payload and frozen settings, and carry those checked fields into prediction provenance.

### NEW-MEDIUM-02 — MEDIUM — The frozen inference/freezer commands do not invoke the implemented interfaces

- **Location:** frozen plan TASK-05 lines 284-287 and protocol-freeze lines 497-500; `src/evaluation/evaluate.py:599-609`; `src/evaluation/predict_model2.py:57-66`; `provenance/commands/task04/render_kaggle_job.py:96-126`; `provenance/commands/task05/build_predictions.py:23-43`.
- **Consequence:** the frozen M1/M2 inference commands use `evaluate --model-id ... --run-dir ...`, but `evaluate.main` supports only `--freeze-operating-point` or `--score` over existing predictions. The exact freeze command omits mandatory `--manifest`. Real M1 predict attempts live under `EXP-V01/vN` and `EXP-R02/vN`, while the frozen follow-on paths name the parent directories. Amendment 008 section 5 describes the new transfer design but is silent on replacement exact commands and attempt promotion. Reproduction therefore requires undocumented operator choices after the freeze.
- **Resolution criterion:** either restore compatible CLI handling for the exact frozen commands or approve an explicit protocol amendment containing the complete renderer/acquisition/reconciliation/builder/freezer/scorer commands and their `vN` paths. Exercise those literal commands end to end with synthetic artifacts before inference.

### NEW-MEDIUM-03 — MEDIUM — M1 class-name order and recorded predict arguments are not consumed

- **Location:** `src/evaluation/kaggle_job.py:468-476`; `src/evaluation/kaggle_job.py:210-247`; `src/evaluation/evaluate.py:483-509`.
- **Consequence:** `_predict` records the actual `model.names` and full effective call arguments, but `verify_prediction_run` neither validates nor returns them. Reversing `model_names` or replacing `predict_args` was accepted. A name/order mismatch would cause saved numeric class IDs to be interpreted as the fixed config order, corrupting Enfermo/Saludable metrics and F2 threshold selection.
- **Resolution criterion:** require `model_names` to equal the frozen ordered M1 names by index, require the complete `predict_args` object to equal the approved call, return both in verified identities, and reject their omission or self-consistent substitution in builder/freezer/scorer/interval paths.

## Per-step approval decision

| Step | May it be approved with this code after EXP-R01 selection is committed? | Reason |
|---|---:|---|
| `EXP-V01` | **NO** | Frozen command mismatch; complete synthetic run evidence is accepted; EXP identity and runtime fields are incomplete. |
| Operating-point freeze | **NO** | A rehashed synthetic raw run selected threshold 0.05; evaluator/selection authorities are self-sealed rather than committed-clean at creation. |
| `EXP-R02` | **NO** | Depends on the invalid freeze; the same run-authentication gap remains; a definitive post-prediction failure has no compliant path. |
| `EXP-R03` | **NO under the frozen execution protocol** | Its predictor/post-processing contract is materially improved, but the frozen inference command invokes the unsupported `evaluate --model-id model2` interface and no amendment supplies a literal replacement command. |
| M1 interval command | **NO end to end** | Its internal canonical-config/provenance checks are improved, but it depends on unapproved M1 artifacts and the frozen parent path does not match `vN` attempts. |
| Primary M2 interval command | **Conditionally code-correct** | The no-flag command now routes to authenticated canonical M2 processing; it can run only after a protocol-compliant EXP-R03 producer command exists. |
| M2 sensitivity command | **Conditionally code-correct** | Canonical manifest/run/truth/class/top-1 checks pass; same upstream command condition as primary M2. |

## Final finding table

| ID | Severity | Status | Blocks |
|---|---|---|---|
| HIGH-04 | HIGH | PARTIALLY CLOSED / OPEN | M1 validation, freeze, test, M1 intervals |
| NEW-HIGH-01 | HIGH | PARTIALLY CLOSED / OPEN | Operating-point freeze and downstream M1 |
| NEW-HIGH-03 | HIGH | PARTIALLY CLOSED / OPEN | Freeze authority, test scoring, intervals |
| MEDIUM-01 | MEDIUM | CLOSED | — |
| MEDIUM-04 | MEDIUM | PARTIALLY CLOSED / OPEN | M1 provenance interpretation |
| NEW-MEDIUM-01 | MEDIUM | CLOSED | — |
| NEW-HIGH-04 | HIGH | OPEN | Definitive EXP-V01/EXP-R02 post-output failure |
| NEW-MEDIUM-02 | MEDIUM | OPEN | Frozen execution/reproduction commands |
| NEW-MEDIUM-03 | MEDIUM | OPEN | M1 class/runtime interpretation |

**Open count: HIGH 4; MEDIUM 3. Overall verdict: DO NOT APPROVE inference.**
