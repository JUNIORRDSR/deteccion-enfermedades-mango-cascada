# Independent review of PROTOCOL-AMENDMENT-008 v7 — round 7

**Review date:** 2026-09-25  
**Scope:** Part A only, Kaggle venue controls for the EXP-R01 training run.  
**Verdict:** **DO NOT APPROVE PROTOCOL-AMENDMENT-008 v7 for EXP-R01.** One HIGH and two MEDIUM findings remain open. The TASK-03 freeze accepted in round 6 was not re-reviewed. TASK-05 inference code and the predict path are out of scope and remain blocked independently by amendment §5.

No Kaggle or other network service was called. No repository file was changed by this review other than this report. Pre-existing unrelated untracked files were left untouched.

## Binding authority and limits of this review

I read `provenance/protocol_freeze.json` and `provenance/protocol_freeze.md` before judging v7. I also read the current SPEC §§5, 6, 7, 11 and 12 and plan TASK-04. Their bytes still match the identities embedded in the freeze:

- SPEC SHA256: `76ef27520460abb7c4c6eee76061adad59e9c6f34f203c1a941f41125d60ec8b`.
- plan SHA256: `cd547e9e1c0fc6c2ecc3dccb12c6d3062dbc000296e8778341eadc9b32610b43`.

The frozen authority requires a single scientifically interpretable training run, preservation of failures, identifiable environment/configuration/code/artifacts, validation-only checkpoint selection, and no test access during training. It explicitly allows a failed run to remain a recorded failure and requires blocked branches to remain blocked.

The frozen authority is silent on Kaggle kernel slug/version semantics, an exact numerical retry limit, the exact platform-log grammar, and the transaction used to reconcile a downloaded Kaggle run. It is also silent on an independent Kaggle custodian. V7 may define those details, but that silence does not waive the frozen requirements to preserve failures, remove post-result optionality, and make EXP-R01 identifiable. The absence of a custodian is therefore treated as the declared limitation it is, not as a new finding.

Commit `2bff016` changes only the out-of-scope predict branch of the renderer, amendment §5/sidecar hashes, and TASK-05 inference files. The training state machine reviewed here is the one introduced by `788dca4`; `73daf37` adds the retained v7 capacity probe.

## Verification performed

- Compared the amendment Markdown, JSON `retry_policy`, and `src/evaluation/kaggle_job.py:RETRY_POLICY`. The JSON object equals the code object byte-for-structure, and the Markdown states the same maximum of three versions, permitted pre-model stages, output/metric exclusions, non-retryable terminations, and first-`COMPLETE` rule.
- Confirmed the current trainer/job/renderer/verifier/test SHA256 values equal the values recorded in the v7 JSON. In particular, the approved job hash is `d4891ff6b0f454b6e803d72d227bbc2309cc16796aa21360586e8316fb2bbc9f`.
- Ran the requested modules in three fresh Python processes with bytecode disabled:

  - `tests.test_kaggle_job`: **40 passed**.
  - `tests.test_verify_kaggle_run`: **6 passed**.
  - `tests.test_run_contract`: **12 passed**.

  Total: **58 passed, 0 failures/errors**.

- Replayed cancellation, hard-cut, post-training-stage, metric-log, clean pre-model failure, ledger-gap, after-`COMPLETE`, and rerender cases. The direct predicates reject all prohibited cases and accept only the clean pre-model case.
- Constructed additional temporary, no-repository-write counterexamples against the composed renderer/verifier path. Those counterexamples expose H-03 and N-07 gaps below.
- Recomputed the retained KAGGLE-CAPACITY-002 v1 reconciliation. The fresh result exactly equals the committed `reconciliation.json`; all 15 receipt-inventoried files are present and match; `hash_only` is empty; 552 manifest files verify; and the computed, render-record, receipt, and verification source hashes all equal `30ba388913a7ca519e6b3541c9c3d885b876dbb2d089608e5785c01a6033ce1b`.
- Executed `render_kaggle_job.capacity_retained` read-only against KAGGLE-CAPACITY-001. It passed: the required files are committed/clean, every evidence byte named by the receipt matches, and the retained verification says the projection fits.

## Round-6 finding disposition

### H-03 — PARTIALLY CLOSED (HIGH remains open)

The core predicates are materially improved. `retry_allowed` rejects cancellation, a `RUNNING` hard-cut receipt, a training-stage failure, any `.pt`/epoch/prediction output, a metric-bearing log, and any non-`ERROR` platform state. `check_attempt` rejects gaps, duplicate version 1, version 4, re-derived refusal, ledger refusal, and any version after `COMPLETE`. `attempt_dir` rejects an existing target directory. A hard cut during training leaves a durable `RUNNING` receipt and is never retryable.

The composed authorization boundary is nevertheless not one-way:

1. **The experiment identity is caller-controlled and the ledger is per caller-supplied directory.** `render_kaggle_job.py:136` accepts arbitrary `--experiment-id`; `:153` passes it directly to `attempt_dir`; and `attempt_dir` at `:96-126` consults only `experiments/model1/<supplied-id>/attempts.jsonl`. With a canonical `EXP-R01/v1` already recorded `COMPLETE`, the actual function still returned a fresh authorized target for `EXP-R01-copy/v1`. The renderer also does not bind mode to experiment ID or require that all ledger entries use the current mode. Once the amendment state becomes `APPROVED`, the same frozen training payload can therefore be rendered as multiple version-1 training namespaces, defeating “the first COMPLETE training is definitive.”
2. **Required retry evidence can fail open at render time.** V7 says both platform and job logs are retained and inspected. The verifier requires `platform_log.json`, but `logs_of` and `attempt_dir` read `job_log.txt` only if it exists (`verify_kaggle_run.py:45-47`; `render_kaggle_job.py:113-117`). `attempt_dir` does not require or authenticate `reconciliation.json` against the ledger's `reconciliation_sha256`. A committed ledger row marked retryable plus a `FAILED` pre-model receipt and `ERROR` platform record was accepted for v2 even when both logs and the reconciliation were absent. The counterexample returned `experiments/model1/EXP-R01/v2`.

**Location:** `provenance/commands/task04/render_kaggle_job.py:96-126,136,153`; `src/evaluation/kaggle_job.py:299-331`; `provenance/commands/task04/verify_kaggle_run.py:45-47,84-99`.

**Consequence:** the repository can authorize more than one completed EXP-R01-equivalent training under different names, or authorize a retry without the full log evidence the declared predicate requires. This restores operator optionality over completed scientific trainings despite the per-directory state machine.

**Resolution criterion:** enforce an exact mode-to-experiment mapping (`train` → `EXP-R01`) before rendering; bind the expected mode and experiment ID in every ledger entry and reject mode changes; require `platform.json`, `platform_log.json`, `job_log.txt`, `reconciliation.json`, receipt, and outputs list for a retry; recompute and compare the reconciliation hash and ledger fields; and add negative tests for alternate experiment IDs, mode switching, missing logs/reconciliation, and a second namespace after canonical `COMPLETE`.

### N-06 — CLOSED

The original environment-evidence defect is closed for the reviewed training scope:

- `_environment` computes the installed dependency closure of `ultralytics`, `torch`, and `torchvision`; a nonzero `pip check` blocks on an unparsed conflict or when the dependent package is in that closure, before data download.
- KAGGLE-CAPACITY-002 exercised this rule on the platform. Its six conflicts concern `bigframes`, `google-adk`, `google-colab`, `dopamine-rl`, and `moviepy`, all outside the recorded closure; `blocking` is empty. The closure contains the detector pipeline's declared runtime dependencies, including torch, torchvision, numpy, OpenCV, Pillow, PyYAML, SciPy, requests, matplotlib, and Ultralytics THOP.
- KAGGLE-CAPACITY-002 retains the install report, stdout/stderr and exit code for every probe, data YAML, Ultralytics settings, job log, platform status/log, Docker digest, receipt, reconciliation, and verification. Fresh byte checks and source checks pass.
- KAGGLE-CAPACITY-001 now retains and byte-checks the evidence that existed for the accepted capacity result. `capacity_retained` is a mandatory pre-render check for training and passed against the committed bytes.

The dependency traversal over-approximates unevaluated environment markers, which can cause conservative false blocks but not acceptance of a broken in-closure dependency. A separate parser completeness defect is recorded as NEW-L-01; it does not negate the demonstrated treatment and retention of the actual nonzero `pip check` evidence that formed N-06.

### N-07 — PARTIALLY CLOSED (MEDIUM remains open)

V7 closes the retry aspect of a hard cut: `set_stage` atomically replaces the receipt at each transition, a cut after `stage=training` leaves `status=RUNNING`, and `retry_allowed` refuses it. Ordinary exceptions receive a final `FAILED` receipt and final inventory. `job_log.txt` is line-buffered, and epoch records are flushed and fsynced.

It does not yet close partial-artifact preservation. `set_stage` inventories only files that exist at the stage transition. If training then creates `run/epoch_records.jsonl` or partial `.pt` files and the session is hard-cut, the stale `RUNNING` receipt cannot list them. `reconcile` checks only names already in `receipt.inventory`; it neither enumerates all retained files nor hashes all names in `platform.outputs`. In the controlled hard-cut counterexample, both a partial epoch record and `last.pt` existed and the attempt was correctly non-retryable, but neither appeared in `retained` nor `hash_only` in the reconciliation. `job_log.txt` is separately hashed only when present.

**Location:** `src/evaluation/kaggle_job.py:334-354`; `provenance/commands/task04/verify_kaggle_run.py:50-99`; `tests/test_kaggle_job.py:395-413`; `tests/test_verify_kaggle_run.py:62-69`.

**Consequence:** a post-training-start hard cut is definitive and non-retryable, but the reconciliation does not authenticate the partial weights and epoch evidence that survived it. A reviewer cannot determine from the immutable record exactly which metric-bearing/model artifacts were retained, which is the unresolved part of the round-6 preservation criterion.

**Resolution criterion:** reconciliation must enumerate the platform outputs and every downloaded file, hash every surviving partial artifact, distinguish receipt-attested from post-receipt/unattested bytes, require the job log, and fail on unexplained omissions. Add a hard-cut test that creates an epoch record and partial weight after the last receipt update and asserts both hashes are recorded.

### N-05 — CLOSED

The former “single version” contradiction is gone. Markdown §6 permits later versions only under the state machine; JSON `test_discipline.controls` says the same; JSON `retry_policy` equals `RETRY_POLICY`; and the code enforces the declared maximum/stages/status/output/metric rules within a ledger namespace. The remaining H-03 problem is missing scope/evidence enforcement, not Markdown/JSON disagreement.

## Other required evidence checks

### KAGGLE-CAPACITY-002

The retained probe is internally consistent:

- receipt/render/verification payload and source identities agree;
- executed-source SHA256 equals the rendered source SHA256 (`30ba3889…ce1b`);
- 552 train/validation files verify against the frozen manifest;
- all 15 receipt inventory files are present and byte-identical;
- platform status is `COMPLETE`, and the Docker image digest is retained;
- the job log has no `mAP50`, `fitness`, or `metrics/` line;
- fresh reconciliation equals the committed reconciliation exactly.

The platform log contains the job's final status JSON followed by Kaggle/nbconvert messages. This does not change the receipt's `COMPLETE` state, and no post-training error is present in this probe.

### KAGGLE-CAPACITY-001 deviation

The deviation is honestly declared. Amendment §6 states that attempt 1 failed during `download`, that its executed-source hash differed from the rendered source, that the retry rule was written only afterward, that raw platform status/log were not retained before the retry, and that `attempts.jsonl` was reconstructed. Each ledger line carries `"reconstructed": true`. The amendment does not present attempt 1 as contemporaneously compliant evidence.

## New findings

### NEW-M-01 — MEDIUM — Reconciliation is not atomic or restartable after a completed training

`verify_kaggle_run.main` computes the seal, writes `reconciliation.json`, appends the current version to `attempts.jsonl`, and only then writes `selection_record.json` (`verify_kaggle_run.py:117-134`). These are ordinary non-atomic writes. If the process is interrupted during the ledger append or after the append but before the selection record is durable, rerunning the verifier is rejected at `:113-116` because the ledger now contains the current version rather than only earlier versions. A partial `selection_record.json` also cannot be replaced because `seal` rejects an existing target at `:181-184`.

**Consequence:** EXP-R01 may finish successfully and become definitive, yet a local interruption in the small post-download sealing window can leave no valid selection record and no supported way to resume reconciliation. Because post-training rerun is forbidden, this can wedge TASK-04 after the expensive scientific run without creating scientific optionality.

**Resolution criterion:** make reconciliation/sealing idempotent and transactional: write and fsync temporary reconciliation/selection files, atomically replace them, append/fsync the ledger last, and allow an exact recomputation to resume when existing bytes/hashes agree. Add fault-injection tests after each write boundary, including a partial ledger line and a partial/missing selection record.

### NEW-L-01 — LOW — A healthy `pip check` success line is treated as a conflict

`pip_check_verdict` parses every nonempty stdout line as a conflict regardless of exit code (`src/evaluation/kaggle_job.py:285-296`). The normal success output `No broken requirements found.` with exit code 0 is unparsed and therefore placed in `blocking`; the job then aborts at `:599-601`.

**Consequence:** if the Kaggle image becomes conflict-free, an otherwise healthy environment is rejected before training. This is fail-safe for scientific integrity and the currently demonstrated image follows the nonzero-conflict branch, so severity is LOW, but the parser is not complete.

**Resolution criterion:** handle exit code 0 explicitly, accepting only empty output or the exact pip success sentinel and rejecting contradictory output; parse conflicts only for nonzero exit status. Add both exit-0 cases to `tests/test_kaggle_job.py`.

## Verdict

**PROTOCOL-AMENDMENT-008 v7 may not move to `APPROVED` for EXP-R01 training.** The per-attempt predicate is much stronger, N-05 and N-06 are closed, KAGGLE-CAPACITY-002 is valid retained evidence, and hard cuts are correctly non-retryable. However, H-03 remains HIGH because a second completed training can be authorized through another caller-supplied experiment namespace, and N-07 plus NEW-M-01 leave definitive failure/completion evidence incompletely reconciled or non-restartable.

Inference remains blocked by amendment §5 and was not adjudicated here.

| Finding | Severity | Round-7 status | Gate effect |
|---|---:|---|---|
| H-03 — one-way attempt/retry discipline | HIGH | **PARTIALLY CLOSED / OPEN** | Blocks approval: experiment ID/mode are not globally bound; required retry evidence can fail open |
| N-06 — environment evidence | MEDIUM | **CLOSED** | No open gate effect |
| N-07 — partial/error-run record | MEDIUM | **PARTIALLY CLOSED / OPEN** | Blocks approval: hard-cut partial artifacts are not all hashed in reconciliation |
| N-05 — Markdown/JSON agreement | LOW | **CLOSED** | No open gate effect |
| NEW-M-01 — non-atomic, non-restartable sealing | MEDIUM | **OPEN** | Blocks approval: a completed EXP-R01 can be left without a recoverable selection seal |
| NEW-L-01 — healthy pip-check output rejected | LOW | **OPEN** | Does not alone block scientific validity; may cause a pre-training false block |

**Open counts: HIGH = 1; MEDIUM = 2.**
