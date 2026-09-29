# TASK-05 independent methodological review — round 5

Date: 2026-09-27  
Scope: prospective pre-inference review of TASK-05 evaluation, statistics, and provenance after commits `e421ce2`, `5ecdeb2`, and `656148d`. No model inference on research data, Kaggle/network call, product-code fix, repository commit, push, or change under `experiments/` was performed.

## Verdict

**DO NOT APPROVE inference yet.** After EXP-R01 and its selection record are committed, the literal TASK-05 commands are now callable in the intended order and the prior runtime-field and post-prediction-failure defects are closed. The M1 chain is nevertheless not ready for approval because the code that re-derives the attempt reconciliation is not itself a committed/reviewed authority, and the inference approval is not bound to the evaluator/config/selection blobs it reviewed. A post-approval committed alternative evaluator/checkpoint/selection chain was accepted.

There is also a new independent blocker for EXP-R03: the interval consumers accept a fully synthetic, self-consistent M2 predictions/sidecar/run-record bundle without evidence that `predict_model2.run` produced it. This is a provenance defect, not a request for an independent custodian or signatures.

Counting `PARTIALLY CLOSED` as open, the final count is **HIGH 4; MEDIUM 0**.

## Binding authority, scope, and protocol silence

Read before judging the implementation:

- immutable `provenance/protocol_freeze.json` and `provenance/protocol_freeze.md`;
- SPEC §§6, 7, 11, and 12;
- frozen plan TASK-05, including every literal command;
- PROTOCOL-AMENDMENT-008 §§4, 5, and proposed §5.1;
- `reports/execution/task-05-independent-review-round4.md`;
- the training-only approval in `reports/amendments/amendment-008-independent-review-round8.md`.

The training scope approved in amendment round 8 was not reopened. `verify_kaggle_run.py` was considered only where `evaluate.attempt_root` relies on it.

The frozen protocol and Amendment 008 explicitly allow the absence of an independent custodian. They are silent on signatures, and this review does **not** require either. The committed Git repository is the declared root of trust. The defect in the accepted alternative-authority replay is therefore not “a committer could commit”: it is that `inference_approved` is not bound to the particular reviewed blobs, so a later commit can replace them without invalidating that approval.

The authority is also silent on the exact schema of that approval-to-blob binding and on an exact local attempt-ledger format for M2. It is not silent on fresh independent review, identifiable Gate-E inputs/code/predictions, one-time test evaluation, or preserving the authority of saved predictions. Section 5.1 may choose a minimal Git-based mechanism for those requirements. The frozen authority remains silent on the exact fields of `test_selection_digest` and on a probability-normalization tolerance; neither is raised as a finding.

Current-state note, not counted as a defect: EXP-R01 has no committed `selection_record.json` yet, `configs/evaluation.json` still has null selection identities, no frozen config exists, and Amendment 008 has `inference_approved=false`. The verdict below is the requested prospective verdict once those ordinary preconditions exist.

## Reviewed implementation

- `src/evaluation/evaluate.py`: `committed_clean`, `attempt_root`, `rebuild_predictions`, `rebuilt`, `write_predictions`, `verified_provenance`, `approved_inference`, `bound_selection`, `sealed_config`, `freeze_operating_point`, `frozen_threshold`, `_score_split`, and `main`.
- `src/evaluation/kaggle_job.py`: the named prediction constants/helpers, `verify_prediction_run`, and `_predict`.
- `src/statistics/intervals.py`: `_run_m1`, M2 authentication/routing used by `main`, and `main`.
- `src/evaluation/predict_model2.py`: `M2_CONTRACT` and `run`.
- `provenance/commands/task05/build_predictions.py` and the predict block of `provenance/commands/task04/render_kaggle_job.py`.
- `configs/evaluation.json`, Amendment 008 §5.1, and the requested test classes/modules.

The current amendment Markdown hash equals the `document.sha256` recorded in its JSON. The current `kaggle_job.py` hash is `9aecd22da3e733c82b4504f1c435b935d18ac90815bbdc6b3751854121d22574`, equal to `approved_code.job_sha256`.

## Fresh verification

Each required module ran in its own Python process with bytecode writes disabled:

| Command | Result |
|---|---|
| `.\.venv\Scripts\python.exe -m unittest tests.test_evaluation -v` | 54 passed, exit 0 |
| `.\.venv\Scripts\python.exe -m unittest tests.test_intervals -v` | 30 passed, exit 0 |
| `.\.venv\Scripts\python.exe -m unittest tests.test_predict_model2 -v` | 6 passed, exit 0 |
| `.\.venv\Scripts\python.exe -m unittest tests.test_kaggle_job -v` | 44 passed, exit 0 |
| **Total** | **134 passed, 0 failures/errors** |

Passing tests do not close the remaining findings because neither post-approval authority replacement nor the M2 producer-bypass case is covered.

## Counterexample replay

All mutable replays used disposable temporary repositories/directories, never `experiments/` in this worktree.

| Round-4 or new case | Observed result | Interpretation |
|---|---|---|
| Fully rehashed synthetic M1 raw run whose candidate threshold is 0.05 | **REJECTED** by `freeze_operating_point`: the altered attempt/ledger/reconciliation were not committed-clean. The rebuilt candidate independently selected **0.05**. | The ordinary round-4 substitution is now stopped by the Git attempt root. |
| `OTHER-EXP` in payload and receipt with hashes recomputed | **REJECTED**: `the run is not EXP-V01`. | Phase-specific experiment identity is closed. |
| `end2end=false` plus its matching suppression description | **REJECTED**. | The expected runtime mode is no longer supplied by the receipt itself. |
| Reversed `model_names` | **REJECTED**. | Numeric class IDs cannot be silently reinterpreted. |
| Altered complete `predict_args` (`half=true`) | **REJECTED**. | The frozen M1 call is compared exactly and carried into provenance. |
| Fully rehashed post-approval alternative selection record/checkpoint/kernel version/evaluator bytes, all committed in the disposable repository | **ACCEPTED**; checkpoint `dddd…`, kernel version 9, and alternative evaluator SHA256 `3c4f…f73` were sealed. | Committed cleanliness alone does not link the inference approval to the blobs that were independently reviewed. |
| Committed changed M1 attempt evaluated through an untracked altered reconciliation module | **ACCEPTED** by `attempt_root`; the verifier itself reported `tracked=false`. | The attempt root trusts the output of a verifier that is absent from `_authorities` and the seal. |
| `FAILED` receipt at `predictions_written` with retained raw digest and later error | **ACCEPTED**; provenance preserved `receipt_status=FAILED`, `receipt_stage=predictions_written`, and the error. | The amendment's definitive-after-predictions rule is now implemented. |
| Literal M1 validation → freeze → test → M1 interval commands | **PASSED** end to end in `FrozenCommands` against a committed synthetic repository; rerunning the test scorer was refused as non-overwriting. | The prior interface/path mismatch is closed. The real repository was not run because its scientific preconditions do not yet exist. |
| Literal M2 command dispatch | **PASSED** the `FrozenCommands` wiring test and resolves the canonical manifest, ART-002 path, run directory, and config. The real ART-002 hash and all 219 test paths were also checked read-only. | No remaining literal-command/parser blocker was found; actual M2 inference was correctly not performed before approval. |
| New: fully synthetic M2 predictions, matching sidecar, and matching `run_record.json`, without calling `predict_model2.run` | **ACCEPTED** by the primary M2 interval CLI and reported accuracy 1.0. | M2 post-processing authenticates assertions inside a self-authored bundle, not the producer/run root. |

## Prior-finding disposition

| Prior finding | Round-5 status | Evidence |
|---|---|---|
| **HIGH-04 — executed-kernel prediction chain not authenticated at consumers** | **PARTIALLY CLOSED / OPEN** | `attempt_root` now enforces the canonical EXP, one definitive ledger entry, byte-identical re-reconciliation, and committed-clean attempt files. However, `_verifier()` dynamically loads `verify_kaggle_run.py`, while `_authorities()` does not require or seal that file. An untracked altered verifier admitted a changed committed attempt. |
| **NEW-HIGH-01 — validation predictions can select the threshold without authentication** | **PARTIALLY CLOSED / OPEN** | The exact rehashed 0.05 substitute is rejected by the committed attempt root. Because HIGH-04's verifier is not rooted, the same changed raw/receipt bytes can still get past `attempt_root` under an unchecked verifier and reach threshold selection. |
| **NEW-HIGH-03 — operating-point artifact does not seal evaluator/training-selection authority** | **PARTIALLY CLOSED / OPEN** | Canonical paths and committed cleanliness are enforced, and later drift is detected. A later committed replacement of evaluator, selection record, checkpoint, kernel version, config, kernel, receipt, and reconciliation was nevertheless accepted under the earlier `inference_approved=true`. |
| **MEDIUM-01 — M2 post-processing accepts noncanonical grouping manifest** | **CLOSED** | Canonical M2 manifest path/hash/sidecar, one-to-one IDs, manifest truth, class order, and top-1 derivation remain enforced. |
| **MEDIUM-04 — downstream runtime-mode evidence weaker than receipt verification** | **CLOSED** | Exact `end2end=true`, suppression, class names, input contract, flags, and full `predict_args` are enforced and returned in provenance. |
| **NEW-MEDIUM-01 — frozen primary M2 interval command routes to M1** | **CLOSED** | The canonical M2 manifest routes the no-flag command to `_run_m2_intervals`. |
| **NEW-HIGH-04 — definitive post-prediction failure has no compliant evaluation path** | **CLOSED** | `predictions_written`/`done` are definitive; FAILED/RUNNING receipts with the retained raw digest are usable, and status/stage/error travel into provenance. |
| **NEW-MEDIUM-02 — frozen inference/freezer commands do not invoke implemented interfaces** | **CLOSED** | `evaluate.main` implements both model IDs, the freezer defaults to the canonical M1 manifest, parent EXP directories resolve their definitive `vN`, and the literal synthetic sequence passes. |
| **NEW-MEDIUM-03 — M1 class-name order and recorded predict arguments are not consumed** | **CLOSED** | Reversed names and altered/missing call arguments are rejected, and both fields are included in rebuilt provenance. |

## Open and new findings

### HIGH-04 — HIGH — The attempt root is evaluated by an unrooted verifier

- **Location:** `src/evaluation/evaluate.py:453-455,495-533`; `provenance/commands/task04/verify_kaggle_run.py` as dynamically loaded by `_verifier`; Amendment 008 §5.1 “Raíz del intento”.
- **Evidence:** in a disposable repository, raw predictions and their receipt were changed and committed while the old committed reconciliation/ledger remained. An untracked replacement verifier returned the stored reconciliation. `attempt_root` accepted the attempt because it requires committed attempt files but never requires the verifier itself to be canonical, committed-clean, or equal to reviewed bytes.
- **Consequence:** the chain that is supposed to authenticate EXP-V01/EXP-R02 can be reinterpreted by code outside the trust root. A changed validation observation can then govern the F2 threshold, and a changed test observation can reach scoring and intervals.
- **Resolution criterion:** make the canonical verifier an inference authority: bind its exact reviewed SHA256 or approval commit in Amendment 008's inference approval, require it committed-clean in every consumer, and seal/check it before freeze, scoring, and intervals. Retain a negative test in which attempt bytes and receipt are mutually consistent but reconciliation only passes under an altered verifier. No custodian or signature is required.

### NEW-HIGH-01 — HIGH — Threshold authentication still depends on the open attempt-root defect

- **Location:** `src/evaluation/evaluate.py:638-696`, through `verified_provenance` → `rebuilt` → `attempt_root`.
- **Evidence:** the fully rehashed 0.05 run is now rejected when the real committed verifier is used, which is material progress. The altered-verifier replay nevertheless lets the changed definitive attempt through the exact gate on which `freeze_operating_point` relies.
- **Consequence:** until HIGH-04 is closed, validation-only selection is not fully authenticated by the declared Git root and downstream M1 inference remains blocked.
- **Resolution criterion:** close HIGH-04 and add an end-to-end freezer test that changes raw detections to the 0.05 case, updates receipt/final hashes, and also substitutes the verifier; the freezer must reject before threshold selection.

### NEW-HIGH-03 — HIGH — Inference approval is not bound to the reviewed authority snapshot

- **Location:** `src/evaluation/evaluate.py:418-481,671-696`; `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.json`; Amendment 008 §5.1 “Autoridades del sello”.
- **Evidence:** after an approval-bearing commit, a second disposable commit changed the selection record, checkpoint to `dddd…`, kernel version to 9, source config, evaluator bytes, and the complete prediction chain. All paths were tracked and clean, so the freezer sealed the replacement evaluator and authority chain.
- **Consequence:** independent approval of one evaluator/config/selection state survives later material changes to the exact bytes that determine the operating point and scores. Git preserves the change, but the automated gate does not distinguish “committed after approval” from “the commit that was reviewed and approved.”
- **Resolution criterion:** record the inference review/approval commit or exact SHA256s for `evaluation.json`, manifest/sidecar/freeze record, EXP-R01 selection record, every sealed code file, the verifier, and the approved amendment/job identity. `approved_inference` and `sealed_config` must require those reviewed identities, not merely current committed cleanliness. A subsequent commit changing any authority must require a new inference review/approval record.

### NEW-HIGH-05 — HIGH — EXP-R03 predictions have no authenticated producer root

- **Location:** `src/evaluation/predict_model2.py:29-33,68-119`; `src/statistics/intervals.py:599-644,699-737`; `tests/test_intervals.py:341-370`.
- **Evidence:** a temporary fixture wrote arbitrary M2 predictions, a matching sidecar, and a matching run record under a structurally equivalent temporary `M2_CONTRACT`, without invoking `predict_model2.run`. Both the route and top-1 probabilities were internally consistent, so the primary interval command accepted the bundle and published accuracy 1.0. The production checks use the same fields and add no producer or Git-root check.
- **Consequence:** EXP-R03 test outcomes can be replaced after—or instead of—the one intended inference, with all current downstream checks passing. The fixed manifest, truth, class order, and top-1 rule prevent some substitutions but do not establish that ART-002 and the reviewed producer generated the probabilities.
- **Resolution criterion:** define a minimal Git-rooted local EXP-R03 attempt/promotion record before test access; bind committed-clean `predict_model2.py`, environment/config identity, ART-002, canonical manifest, predictions, sidecar, and run record. Require the interval consumers to verify that root and specify the commit/promotion step between the literal M2 inference and interval commands. This does not require platform attestation, an external custodian, or signatures.

## Legitimate-attempt and literal-command assessment

No field mismatch was found that would reject a legitimate EXP-V01 or EXP-R02 receipt produced by the current `_predict`, reconciled by the current `verify_kaggle_run.py`, and committed under the canonical experiment. `_predict` emits the exact names, arguments, `end2end`, suppression description, phase, experiment, checkpoint, raw digest, and definitive stage that the verifier expects. COMPLETE, FAILED-after-predictions, and hard-cut RUNNING-after-predictions states are representable; later failure information is retained.

No remaining path or parser defect prevents the frozen command sequence from running in order once EXP-R01 is sealed, its config identities are populated and committed, Amendment 008 inference is validly approved, the canonical Kaggle attempts are downloaded/reconciled/committed, and the frozen config is committed before EXP-R02. The current worktree cannot run that real sequence now because those scientific prerequisites intentionally do not exist. The synthetic literal-command replay is sufficient to close the old interface defect, not to approve the provenance gaps above.

## Per-step approval decision

| Step | May it be approved after EXP-R01 selection is committed? | Reason |
|---|---:|---|
| `EXP-V01` | **NO** | Its canonical command and runtime contract are fixed, but the attempt reconciler is not itself rooted in the approved bytes. |
| Operating-point freeze | **NO** | It depends on EXP-V01 and accepts authority blobs committed after the approval snapshot without requiring renewed review. |
| `EXP-R02` | **NO** | The command and definitive-failure path work, but it inherits HIGH-04 and NEW-HIGH-03. |
| `EXP-R03` | **NO** | The literal command is wired correctly, but downstream consumers accept a synthetic self-authored run bundle with no producer root. |
| M1 interval command | **NO** | Statistical routing and frozen-config checks are sound, but the upstream M1 authority is not yet approvable. |
| Primary M2 interval command | **NO** | The estimator/routing checks pass; the saved EXP-R03 observation is not authenticated to its producer. |
| M2 sensitivity command | **NO** | The sensitivity/statistical contracts pass; it shares the same unauthenticated EXP-R03 source. |

## Final finding table

| ID | Severity | Status | Blocks |
|---|---:|---|---|
| HIGH-04 | HIGH | PARTIALLY CLOSED / OPEN | EXP-V01, freeze, EXP-R02, M1 intervals |
| NEW-HIGH-01 | HIGH | PARTIALLY CLOSED / OPEN | Operating-point freeze and downstream M1 |
| NEW-HIGH-03 | HIGH | PARTIALLY CLOSED / OPEN | Approval/authority snapshot, freeze, scoring, intervals |
| MEDIUM-01 | MEDIUM | CLOSED | — |
| MEDIUM-04 | MEDIUM | CLOSED | — |
| NEW-MEDIUM-01 | MEDIUM | CLOSED | — |
| NEW-HIGH-04 | HIGH | CLOSED | — |
| NEW-MEDIUM-02 | MEDIUM | CLOSED | — |
| NEW-MEDIUM-03 | MEDIUM | CLOSED | — |
| NEW-HIGH-05 | HIGH | OPEN | EXP-R03, primary M2 intervals, M2 sensitivity |

**Open count: HIGH = 4; MEDIUM = 0. Overall verdict: DO NOT APPROVE inference.**
