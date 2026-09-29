# Gate review before EXP-R01

**Review date:** 2026-09-25  
**Scope:** research-methodology gate review of PROTOCOL-AMENDMENT-008 v6, the TASK-03 data freeze, and TASK-05 evaluation code.  
**Overall result:** **DO NOT START EXP-R01.** The M1/M2 data freeze is acceptable, but the venue amendment still has an open HIGH and two open MEDIUM findings. Inference also remains blocked independently by TASK-05 findings.

No repository file was changed during the review other than this report. Pre-existing unrelated worktree changes were left untouched. No Kaggle or other network write was made.

## Binding authority and review standard

I read `provenance/protocol_freeze.json` and `.md` before reviewing implementation evidence. Their embedded SPEC and plan bytes agree with the current files:

- SPEC SHA256: `76ef27520460abb7c4c6eee76061adad59e9c6f34f203c1a941f41125d60ec8b` (`docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md`)
- plan SHA256: `cd547e9e1c0fc6c2ecc3dccb12c6d3062dbc000296e8778341eadc9b32610b43` (`docs/superpowers/plans/2026-09-17-albus26-major-revision.md`)

The controlling requirements are frozen SPEC §§5, 6, 7, 11 and 12 and plan TASK-02 through TASK-05. Gate E requires zero open HIGH and MEDIUM findings. The withdrawn PROTOCOL-AMENDMENT-009 has no authority and cannot replace the conservative grouping rule.

The frozen protocol is explicit about per-byte manifest identity, group-atomic splitting, adjudication, environment capture, retained failures, one-time test use, and identifiable code/configuration/artifacts. It is silent about all of the following: an independent custodian or signing key; Kaggle kernel slug/version semantics; an exact numerical retry limit; the exact platform control-plane files that must be retained; and the fact that an Ultralytics callback after epoch 3 represents `final_eval`. That silence does not waive the explicit hash, environment, failure-preservation, or single-test-use requirements. SPEC §5 requires blind A/B packets to be exported, but is silent on whether their rendered PNG bytes must remain committed after hashes and decisions have been retained.

## Verification performed

- Recomputed the frozen hashes and checked the tracked/clean status of the amendment, freeze, implementation, and capacity-probe evidence.
- Replayed the round-5 `SRC-009688` split-substitution attack entirely in memory.
- Replayed M1 split construction from the recorded frozen inputs with the frozen algorithm and compared exact CSV bytes.
- Ran `validate_split` against the image/label hashes and atomicity constraints.
- Replayed M2 freeze construction and compared exact CSV bytes.
- Inspected all supplementary A/B decisions, third-pass resolutions, controls, final relations, and blinding log.
- Ran the required command:

  `.\.venv\Scripts\python.exe -m unittest tests.test_evaluation tests.test_intervals tests.test_predict_model2 tests.test_kaggle_job -v`

  Result: **111 tests passed**, 0 failures/errors, 16.852 s reported test time.

- Ran `.\.venv\Scripts\python.exe -B -m unittest tests.test_run_contract tests.test_split -v`.

  Result: **37 tests passed**, 0 failures/errors.

- Constructed two no-file, in-memory counterexamples against the current TASK-05 functions. Both were accepted; details are in Part C.

---

## Part A — PROTOCOL-AMENDMENT-008 version 6

### Verdict A

**DO NOT APPROVE for EXP-R01 training.** H-02 and M-01 are now closed, and the capacity result itself is sound. Approval is nevertheless barred by H-03 (HIGH, partially closed), N-06 (MEDIUM, open), and N-07 (MEDIUM, partially closed). The v6 Markdown/JSON retry contradiction also reopens prior LOW N-05.

### Round-5 finding disposition

| Prior finding | Status in v6 | Evidence |
|---|---|---|
| H-02 — phase input/test-byte integrity | **CLOSED** | The committed freeze record fixes manifest SHA256 `dd9431dd7bbc00c6117baf6a0f6cf49eff8bc55f144016b4a98dbdea049ecf5f`; amendment JSON fixes trainer SHA256 `9dd613910d4d1cbcb2a4326fad74f9cf9a8abed733d7e3dc8b7be45b1c309f84` and job SHA256 `dc6f0a3341b7248eaf2b30d2c8956e3013086c26965d5b140a46988ad872ba7c`. `check_bindings` rejects a changed manifest before rendering; `verify_receipt` binds payload, exact file set, and executed-source hash after execution. The successful receipt's executed-source hash equals the render record: `8fe32e2a292eaf2669322448e0c73ceae9c9c4f31d36a9d003b79e000386c259`. |
| H-03 — one-way attempt/retry discipline | **PARTIALLY CLOSED** | Markdown §4 now gives a substantially precise EXP-V01/EXP-R02 predicate and §6 prevents choosing between completed training runs. Remaining contradictions and training-failure ambiguity are detailed below. |
| M-01 — schedulable capacity | **CLOSED** | The model-bearing probe measured setup, callback intervals, memory, output size, and disk. The projection rule was present before measurement and was not changed after measurement. The measured projection is 1,590.58 s versus the 43,200 s limit. |
| M-02 — prediction transfer | **CLOSED for the EXP-R01-only scope** | v6 still blocks inference pending TASK-05 review. This finding does not authorize EXP-V01 or EXP-R02. |
| N-04 — venue rationale and decision chain | **CLOSED** | The amendment continues to distinguish viable local CPU execution from the user's selected Kaggle venue and cites the decision chain. |
| N-05 — Markdown/JSON agreement | **OPEN (LOW)** | The Markdown permits later kernel versions under defined retries, while JSON `test_discipline.controls` still says “single kernel ..., single version.” |
| N-06 — environment evidence | **OPEN (MEDIUM)** | Both capacity receipts record `pip check` exit code 1; the job records but does not reject it. The hashed evidence files, raw platform status/log, and Docker digest claimed by the amendment are absent from the retained directory. |
| N-07 — partial/error-run record | **PARTIALLY CLOSED (MEDIUM)** | Ordinary Python exceptions produce a receipt through `finally`, and epoch records are flushed. Hard platform termination and complete partial-artifact reconciliation remain unhandled and untested. |

### H-02 adversarial replay and trust root

The round-5 substitution was repeated against the v6 trust root. Changing `SRC-009688` from test to train and regenerating a self-consistent sidecar produced manifest SHA256 `3e8585...5c30`. `src/evaluation/kaggle_job.py:111-123` rejected it with “manifest ... is not the frozen, recorded manifest.” A self-consistent substitute therefore no longer passes merely by updating its sidecar.

The post-run side is also materially improved. `verify_receipt` at `src/evaluation/kaggle_job.py:145-161` checks the rendered payload, the complete phase-specific file mapping, and—when supplied—the source hash computed inside the kernel. The current successful render, receipt, and verification agree on source SHA256 `8fe32e2a...c259`, payload SHA256 `48a82379...4608`, and 552 train/valid files. The amendment's approved trainer/job hashes match the current bytes. This closes H-02 for the declared training route.

### Capacity probe, projection rule, and fourth interval

`capacity_verdict` is at `src/evaluation/kaggle_job.py:212-223`. Git chronology shows the rule was committed before capacity attempt 1 and before the successful measurement. Later probe-source changes corrected data-string rendering and the Ultralytics settings/font location; they did not alter the projection formula after seeing the timing.

The successful receipt records:

- setup: 32.4497 s;
- intervals: 46.5575, 7.1973, 6.9792, and 7.6945 s;
- projected 150-epoch time with factor 1.35: 1,590.5770 s;
- limit: 43,200 s;
- peak GPU allocated/reserved: 2.576/3.332 GB;
- run directory: 16,971,336 bytes; free disk: 1,100,140,138,496 bytes.

The amendment's statement about the fourth interval is correct. Ultralytics 8.4.52 calls `final_eval()` at `.venv/Lib/site-packages/ultralytics/engine/trainer.py:577`; `final_eval` is defined at line 843 and invokes the fit-epoch-end callback after validation of the selected best checkpoint. The fourth callback-to-callback duration is therefore final evaluation, not epoch 4. Because 7.6945 s exceeds the two steady training intervals, using it as the maximum makes this particular projection more conservative. The 27-fold margin to the session limit is large enough that this implementation detail does not threaten the capacity conclusion. M-01 is closed.

### Attempt 1 and retry-policy assessment

Attempt 1 has `status=FAILED`, `stage=download`, no `epoch_records.jsonl`, no model, and no predictions. Its executed-source SHA256 (`393a4e5e...fdad`) differs from the locally rendered v1 source (`f8fafb25...7d9`), and its payload likewise differs (`fc794516...7c54` executed versus `06b576fc...a86e` rendered). This correctly exposed the hand-transcribed split-string error. The successful v2 source does match its render record. In substantive stage/result terms, attempt 1 meets the §6 pre-training retry predicate.

It does not fully meet the evidence precondition. The retained `attempt1/attempt.json` is a repository-authored summary of platform status, not the downloaded raw platform status/log required before retry. There is no retained platform log against which a “metric line” predicate can be checked.

Markdown §4 is now specific about stage, absence of prediction bytes, platform-log content, preservation before retry, and the definitive transition at `predictions_written`. However:

- amendment JSON still says “single version” (`PROTOCOL-AMENDMENT-008-kaggle-compute.json:77`);
- “the platform log contains no metric line” has no defined grammar or verifier;
- §6 allows a new attempt after any failure “during training” if the payload is unchanged, without defining eligible terminal causes, excluding operator cancellation, or bounding attempts;
- no code authenticates an append-only attempt ledger, previous attempt evidence, or first-COMPLETE status before another render;
- rendering into a reused directory can replace the current `kernel.py`/`render_record.json` unless the operator separately archives it.

The frozen protocol does not specify a Kaggle retry count, so a protocol amendment may define one. It is not silent about preserving failures or avoiding post-result optionality. The current training-failure clause leaves an operator-visible partial run eligible for cancellation/retry, which is a scientific optional-stopping route even when the payload is unchanged.

### Open Part A findings

#### H-03 — HIGH — Attempt/retry discipline remains contradictory and non-enforced

- **Location:** amendment Markdown §4 (`:66`) and §6 (`:93`); amendment JSON `test_discipline.controls` (`:77`); `provenance/commands/task04/render_kaggle_job.py` output handling.
- **Consequence:** the repository cannot determine from preserved evidence whether a later EXP-R01 or inference version was an allowed exogenous retry, an operator-cancelled partial result, or an unauthorized post-result rerun. The Markdown and JSON give different version rules.
- **Resolution criterion:** make Markdown and JSON identical; define eligible training-failure terminal states and explicitly make operator cancellation/non-evidenced termination ineligible; define a deterministic metric/log predicate; preserve an append-only per-version ledger plus raw platform status/log/output before a retry; make the renderer reject a later version unless the previous version and predicate are authenticated; retain “first COMPLETE is definitive.”

#### N-06 — MEDIUM — The demonstrated environment fails an explicit gate and its raw evidence is missing

- **Location:** `src/evaluation/kaggle_job.py:293-300`; both capacity receipts; amendment §3 (`:57-58`); frozen environment contract/Gate E.
- **Consequence:** both attempts report `pip_check.exit_code=1`, but execution continues. Only hashes of `pip_check`, install report, pip configuration/debug, freeze, and NVIDIA outputs are retained; the actual files are absent from `experiments/model1/KAGGLE-CAPACITY-001/`. A reviewer cannot identify the package conflict, validate the claimed install origins, verify redaction, or reproduce the environment claim. The promised Docker digest and raw platform evidence are also absent.
- **Resolution criterion:** make a nonzero `pip check` a pre-training rejection unless an approved, recorded exception demonstrates that the conflict is irrelevant; retain the hashed evidence bytes, raw platform status/log, notebook image/digest metadata, command exit codes, and redacted configuration for every attempt; verify every retained byte against the receipt before EXP-R01 authorization.

#### N-07 — MEDIUM — Failure preservation is not durable across the relevant failure modes

- **Location:** `src/evaluation/kaggle_job.py:225-238,508-515`; `src/evaluation/train_model1.py:89-95`; current tests in `tests/test_kaggle_job.py` and `tests/test_run_contract.py`.
- **Consequence:** `finally` records ordinary exceptions and epoch JSONL is flushed, but SIGKILL/session cutoff cannot execute `finally`. Evidence hashes are populated only at the success end, and no top-level receipt reconciles whatever weights, logs, epoch records, and environment files survived a hard cutoff. A partial run can therefore expose metrics without producing the evidence needed to classify a retry under H-03.
- **Resolution criterion:** checkpoint the receipt and evidence/artifact hash inventory durably by stage; reconcile a downloaded failed session into an immutable failure record; retain partial weights/logs/epoch records with hashes; and add a controlled mid-training termination plus a simulated missing-finally/platform-cutoff reconciliation test.

#### N-05 — LOW — Markdown/JSON version-policy mismatch

- **Location:** amendment Markdown §4/§6 versus `PROTOCOL-AMENDMENT-008-kaggle-compute.json:77`.
- **Consequence:** machine and human reviewers can apply incompatible retry rules.
- **Resolution criterion:** encode the exact retry state machine in JSON, including permitted later versions, and test parity with the Markdown-declared policy.

### Part A conclusion

The v6 trust root and capacity measurement are credible, but Gate E is not satisfied. **PROTOCOL-AMENDMENT-008 must remain unapproved, and EXP-R01 must not start.**

---

## Part B — TASK-03 M1 partition freeze and M2 freeze

### Verdict B

**ACCEPTABLE as the data input of EXP-R01.** Exact replay reproduces the M1 manifest bytes and passes all frozen split/atomicity/block rules. The supplementary adjudication follows SPEC §5, no pending relation remains, and its candidate selection is independent of split assignment. The M2 freeze also reproduces exactly. There are no open HIGH or MEDIUM findings in Part B.

### Exact M1 replay

All input hashes in `data/manifests/model1_clean_manifest.freeze.json` match current bytes. Running the recorded construction in memory with seed 42, ratios 0.70/0.15/0.15, the frozen descending-group algorithm, and the recorded ordinary plus supplementary relations produced byte-for-byte the committed CSV:

- SHA256: `dd9431dd7bbc00c6117baf6a0f6cf49eff8bc55f144016b4a98dbdea049ecf5f`;
- 669 images, 199 atomic groups;
- train: 439 images / 8 groups;
- valid: 113 images / 93 groups;
- test: 117 images / 98 groups.

`validate_split` passed exact image/label hashes, required schema, unique IDs, and group atomicity. There are no block reasons. Validation has 9 groups containing Enfermo and 84 containing Saludable; test has 15 and 84 respectively, so neither class is absent and the minimum-two-independent-groups rule is satisfied.

The 432 `sakit_mp4` frames form one group, `SRC-009701`, and every member is in train. This is the frozen conservative Option A rule. PROTOCOL-AMENDMENT-009 was withdrawn by DECISION-032 and does not authorize splitting the montage.

### Supplementary adjudication against SPEC §5

The evidence supports compliance:

- Candidate generation reads the complete 7 rotation candidates and the predeclared top 40 ART-004 embedding candidates. It does not filter or rank by `proposed_split`; the code explicitly reviews every pair irrespective of split (`supplementary_candidates.py:1-10,36-45`). Split fields are descriptive only.
- A and B received separate opaque-ID packets. The retained questions expose neither SRC-ID, filename, class, nor split. Reviewer identities differ, and the log records the filesystem-access limitation instead of claiming access-control blinding.
- There are 53 reviewed units: 47 scientific candidates plus 6 calibration controls. Both reviewers classified all 53. Both scored all three positive controls related and all three negative controls unrelated.
- The original A/B table is preserved in `supplementary_adjudications.csv`: 15 agreements and 38 disagreements. Disagreements remain `PENDING_SEPARATE_ADJUDICATION` there rather than being overwritten.
- A fresh reviewer C, recorded as having no access to A or B, resolved exactly those 38 disagreements in `supplementary_resolution.csv`, with separate evidence/rationale fields.
- `supplementary_relations.csv` maps all 47 scientific candidates to final relations and contains no pending decision. The split input therefore contains no unresolved visual relation.

This satisfies the substantive two-pass, separate-third-pass, preserved-original-decision, and no-pending requirements. The protocol is silent on permanent repository retention of the rendered A/B PNGs. Their individual hashes, question manifests, answers, key, and blinding log are retained, but the PNG bytes themselves are not.

### Withdrawn Amendment 009 finding disposition

Every finding from `reports/amendments/amendment-009-independent-review.md` is **CLOSED by withdrawal**, not by validating Option B:

| Finding | Status | Evidence |
|---|---|---|
| HIGH-01 — montage evidence did not establish a smaller independence unit | **CLOSED by withdrawal** | The final freeze uses one conservative montage group. |
| HIGH-02 — outcome-conditioned protocol selection | **CLOSED by withdrawal** | DECISION-032 restores the previously frozen Option A; no Option-B result is selected. |
| HIGH-03 — residual merge rule violated adjudication | **CLOSED by withdrawal** | The residual rule is not used; final relations come from SPEC-compliant adjudication. |
| HIGH-04 — `k=5`/embedding/controls lacked error calibration | **CLOSED by withdrawal** | No calibrated residual auto-merge is used. The embedding candidates receive visual adjudication. |
| HIGH-05 — design did not close over final partition/pending candidates | **CLOSED by withdrawal** | All 47 supplementary candidates are resolved before replay; no pending relation enters the split. |
| MEDIUM-01 — Option-A consequence not reproducible | **CLOSED by withdrawal/current replay** | Exact current Option-A CSV bytes were reproduced from retained inputs. |
| MEDIUM-02 — residual cache not bound to ART-004 | **CLOSED by withdrawal** | The cache is not used as an automatic grouping authority. |
| MEDIUM-03 — residual application reported success on blocked split | **CLOSED by withdrawal** | `apply_residual.py` is not in the accepted freeze path; current `validate_split` and block checks pass. |
| MEDIUM-04 — Amendment 009/audit narrative overstated evidence | **CLOSED by withdrawal** | Amendment 009 is explicitly withdrawn. A separate stale-report LOW remains below. |
| LOW-01 — globally scoped Option-B switch | **CLOSED by withdrawal** | Option B is not enabled. |
| LOW-02 — missing amendment-critical end-to-end tests | **CLOSED by withdrawal** | The amendment path is not used; the accepted Option-A path was replayed directly and its split tests pass. |

“Closed by withdrawal” means the rejected method supplies no authority or evidence to the accepted freeze; it does not mean its scientific claims were rehabilitated.

### M2 freeze

The M2 replay produced byte-for-byte `data/manifests/model2_frozen_manifest.csv`:

- SHA256: `cd4f0d0e428fc3015268b7df541bf705261893c4b5cba0a7ef274e17d0680d92`;
- 1,500 rows and complete 1,500/1,500 DATA-004↔DATA-005 membership;
- train 1,064, valid 217, test 219;
- no frozen group crosses a split.

This is an acceptable frozen input. The frozen §7 estimand remains image-weighted over all 219 test images, with exact-SHA-deduplicated and cluster-weighted analyses secondary. The stale claim elsewhere that 203 clusters are the sole “honest denominator” does not override the frozen protocol.

### Open LOW Part B findings

#### B-L01 — LOW — Superseded status/narrative remains in execution reports

- **Location:** `reports/model1_split_proposal.md:27`; `reports/execution/task-02-audit-report.md:10,53-65,142`; freeze record status field.
- **Consequence:** the proposal still says `PROPUESTA`, the audit report says supplementary adjudication is in progress, and it presents 203 pHash clusters as the required M2 denominator. A later operator could mistake stale narrative for the final evidence or the frozen §7 estimand.
- **Resolution criterion:** after this review is accepted, update the governance status and audit narrative to cite the final supplementary counts/hash and state the frozen primary/secondary M2 estimands without altering the manifest bytes.

#### B-L02 — LOW — Exact blind-packet raster bytes are not retained

- **Location:** `data/audits/model1/supplementary_blinding_log.json` lists hashes for A/B PNGs, while the repository retains only the consolidated supplementary files.
- **Consequence:** the decisions, questions, source mapping, and packet hashes are auditable, but a reviewer cannot byte-verify the exact rendered panels shown to A/B from the repository alone. This is a provenance limitation, not evidence of split-conditioned adjudication.
- **Resolution criterion:** retain the A/B packet bytes or a deterministic render bundle with exact dependencies and verify each file against the existing packet hash list. The frozen protocol does not explicitly require committed long-term raster retention, so this is LOW.

### Part B conclusion

The low documentation/provenance limitations do not change membership or violate a frozen blocking rule. **TASK-03 is methodologically acceptable as the EXP-R01 input.** Its acceptance does not override Part A's venue block.

---

## Part C — TASK-05 evaluation code, round 3

### Verdict C

**DO NOT APPROVE inference after EXP-R01 in the current code state.** The required tests pass, but executable counterexamples show that the prediction-provenance and M2-manifest trust chains remain incomplete. In addition, the frozen evaluator/selection authority is not sealed as Amendment 008 §4 declares, and the prescribed non-sensitivity M2 interval command still routes to the M1 path.

### Prior-finding disposition

| Prior finding | Current status | Evidence |
|---|---|---|
| HIGH-01 — M1 execution not authorized/frozen | **CLOSED** | `authorize` requires amendment `APPROVED` for training and `APPROVED` plus `inference_approved=true` for prediction; prediction also requires the checkpoint in the committed EXP-R01 selection record. The renderer checks committed authority files. |
| HIGH-02 — inconsistent threshold schema | **CLOSED** | `threshold` remains canonical; grid results remain separate. |
| HIGH-03 — EXP-R03 class names | **CLOSED** | The predictor writes model-index class names and interval loading now requires a consistent declaration on every record. |
| HIGH-04 — M1 predictions not bound to kernel/checkpoint/config | **PARTIALLY CLOSED** | `verify_prediction_run` now checks executed source, payload, config/manifest hashes, phase, checkpoint, status, inference, and runtime flags, and the builder carries them. Downstream `verified_provenance`, however, accepts a self-authored provenance record without the kernel/payload/raw-prediction identities and without authenticating that the builder produced it. |
| MEDIUM-01 — evaluator/M2 inputs not anchored | **PARTIALLY CLOSED** | M1 fixed config values are enforced and M2 inference itself fixes the canonical manifest. `authenticate_m2` still accepts a different manifest if sidecars and `run_record.json` are internally consistent. |
| MEDIUM-02 — two AP paths | **CLOSED** | Saved detections remain the single AP source. |
| MEDIUM-03 — float32 IoU parity | **CLOSED** | The float32/epsilon implementation and tests remain in place. |
| MEDIUM-04 — effective inference mode/input contract | **PARTIALLY CLOSED** | Receipt verification now requires exact false `agnostic_nms`/`single_cls`, boolean `end2end`, input contract, and effective suppression. Downstream scoring/freezing does not require the two flags and only requires the other fields to be truthy. |
| LOW-01 — M2 exact tie order | **CLOSED** | Exact ties still select the first model index. |
| LOW-02 — Wilson argument contract | **CLOSED** | Invalid integer/Bernoulli inputs remain rejected. |
| NEW-HIGH-01 — unauthenticated validation predictions can select threshold | **PARTIALLY CLOSED** | The freezer now calls `verified_provenance`, but that record is self-authored/unsealed and can omit the executed-kernel chain. Synthetic predictions plus a matching sidecar/provenance can still satisfy this gate. |
| NEW-HIGH-02 — prescribed M1 interval command cannot run / accepts unsealed threshold | **CLOSED for M1** | The command derives the canonical frozen config, requires its sidecar, validates grid threshold/manifest/checkpoint, and verifies test prediction provenance. |
| NEW-LOW-01 — M2 class names not required per record | **CLOSED** | Current loading requires the same ordered declaration on every record. |

### In-memory counterexamples

The counterexamples used the current functions directly and wrote no files.

1. **Alternative M2 manifest accepted.** A one-row manifest with group `ALT-G`, a digest different from canonical `cd4f0d...0d92`, matching sidecars, a self-authored `run_record.json`, and matching `truth` was passed to `authenticate_m2`. It returned successfully. This confirms that `src/statistics/intervals.py:594-617` checks internal consistency but not the canonical M2 path/digest or the complete run contract.
2. **Incomplete M1 provenance accepted.** A prediction sidecar and `prediction_provenance.json` with the expected prediction/checkpoint/config/manifest/phase/inference fields and truthy `end2end`, input-contract, and effective-suppression values was passed to `verified_provenance`. The record deliberately omitted `agnostic_nms`, `single_cls`, `kernel_source_sha256`, `payload_sha256`, and `predictions_raw_sha256`. `src/evaluation/evaluate.py:397-425` accepted it. This counterexample applies both to test scoring and, with phase `valid`, to operating-point freezing.

These are not failures of the 111-test suite; they are missing negative contracts.

### Open and new Part C findings

#### HIGH-04 — HIGH — The executed-kernel prediction chain is not authenticated at its consumers

- **Location:** `provenance/commands/task05/build_predictions.py:42-94`; `src/evaluation/kaggle_job.py:164-210`; `src/evaluation/evaluate.py:397-425`.
- **Consequence:** the builder verifies the real receipt/render chain, but the scorer and freezer accept a replacement provenance JSON that merely repeats expected local identities and the prediction digest. Kernel source, payload, raw predictions, and builder origin can disappear or be fabricated while metric production still succeeds.
- **Resolution criterion:** seal/hash `prediction_provenance.json` as an output of the verified builder, or make every consumer reverify the retained receipt, kernel, render record, raw prediction hash, and builder output; require exact kernel/payload/raw identities and negative tests for deletion/substitution of each field.

#### NEW-HIGH-01 — HIGH — Validation prediction authentication is still forgeable

- **Location:** `src/evaluation/evaluate.py:397-454`.
- **Consequence:** arbitrary validation detections covering the frozen IDs can be paired with a self-consistent sidecar and locally authored provenance, select the F2 operating point, and then be embedded into the apparently frozen config. This changes the threshold later used once on test.
- **Resolution criterion:** close HIGH-04's provenance root and make `freeze_operating_point` require a builder-sealed EXP-V01 artifact whose receipt/render/config/manifest/checkpoint/kernel identities are independently reverified. Add a synthetic-validation-predictions negative test, not only wrong-field tests.

#### NEW-HIGH-03 — HIGH — The frozen operating-point artifact does not seal the evaluator and training-selection authority declared by the venue protocol

- **Location:** amendment §4 (`PROTOCOL-AMENDMENT-008-kaggle-compute.md:65`); `configs/evaluation.json`; `src/evaluation/evaluate.py:436-454`; inference rendering/verification code.
- **Consequence:** the current freezer records prediction, manifest, source-config, and checkpoint hashes but neither requires nor produces the evaluator SHA256 or EXP-R01 kernel version. The test selection is represented only indirectly by the whole-manifest hash, without the declared selection digest field. Evaluator bytes can therefore change between validation freeze, test inference, and local scoring without invalidating the frozen config. The checkpoint hash also lacks the amendment-declared training-kernel-version linkage inside that artifact.
- **Resolution criterion:** include and require the evaluator SHA256, an explicitly defined test-selection digest, EXP-R01 selection-record hash and kernel version in `evaluation_frozen.json`; verify those bytes/identities before EXP-V01, EXP-R02, local scoring, and interval computation; bind them into prediction provenance; add byte-mutation and wrong-selection/kernel-version tests.

#### MEDIUM-01 — MEDIUM — M2 post-processing accepts a noncanonical grouping manifest

- **Location:** `src/statistics/intervals.py:594-617`; compare canonical enforcement in `src/evaluation/predict_model2.py:20-25,63-66`.
- **Consequence:** the M2 predictor uses the frozen manifest, but intervals/sensitivity can silently replace group/cluster membership and truth with another self-consistent manifest, changing the bootstrap dependence and estimand under the same EXP-R03 label.
- **Resolution criterion:** require the canonical path and SHA256 `cd4f0d...0d92`, a mandatory sidecar, complete expected image IDs, and all immutable `run_record.json` fields (experiment ID, weights, manifest, preprocessing/input contract, model/class order); reject the demonstrated `ALT-G` substitute.

#### MEDIUM-04 — MEDIUM — Downstream runtime-mode evidence remains weaker than receipt verification

- **Location:** `src/evaluation/kaggle_job.py:164-210`; `src/evaluation/evaluate.py:397-425`.
- **Consequence:** the venue verifier proves `agnostic_nms=false` and `single_cls=false`, but scorer/freezer accept their absence and accept any truthy effective-suppression/input-contract objects. Runtime evidence can be weakened after building without failing metrics.
- **Resolution criterion:** require exact false values for both flags, exact expected `end2end`/effective-suppression semantics and the complete input contract at every consumer; seal the provenance record; add the accepted omission counterexample as a negative test.

#### NEW-MEDIUM-01 — MEDIUM — The prescribed primary M2 interval command runs the M1 path

- **Location:** frozen plan TASK-05 M2 interval commands; `src/statistics/intervals.py:658,676-681`.
- **Consequence:** `_run_m2` is selected only when `--m2-sensitivity` is present. The frozen primary command without that flag falls through to `_run_m1`, where M2 inputs are treated as M1 and rejected or misinterpreted. The required `model2_intervals.json` cannot be produced by its approved command even though the sensitivity command has an M2 path.
- **Resolution criterion:** implement deterministic M2 mode selection for the frozen primary command (or approve a protocol amendment consolidating the primary and sensitivity artifacts), authenticate it through the same M2 manifest/run record, and add an end-to-end test of both exact frozen commands and output filenames.

### Part C conclusion

Passing unit tests establish considerable local behavior, but the accepted counterexamples cross the scientific trust boundaries those tests are meant to enforce. **Even after EXP-R01 and its committed selection record exist, EXP-V01, the operating-point freeze, EXP-R02, and EXP-R03 must not be approved with the current code.**

## Final gate summary

| Part | Verdict | Open HIGH | Open MEDIUM |
|---|---|---:|---:|
| A — PROTOCOL-AMENDMENT-008 v6 / EXP-R01 venue | **DO NOT APPROVE; DO NOT START EXP-R01** | **1** | **2** |
| B — TASK-03 M1 partition and M2 freeze | **ACCEPTABLE as EXP-R01 data input** | **0** | **0** |
| C — TASK-05 inference/evaluation | **DO NOT APPROVE inference after EXP-R01** | **3** | **3** |
