# Independent review of PROTOCOL-AMENDMENT-008 v8 — round 8

**Review date:** 2026-09-27  
**Scope:** EXP-R01 training only. TASK-03 remains accepted from round 6 and was not reopened. TASK-05 inference, including the predict branches of the renderer and `kaggle_job.verify_prediction_run`, remains out of scope and blocked by amendment §5.  
**Verdict:** **PROTOCOL-AMENDMENT-008 v8 MAY MOVE TO `APPROVED` FOR EXP-R01 TRAINING.** All round-7 HIGH/MEDIUM findings are closed. Two new LOW reconciliation edge cases remain; neither permits another training, changes selection, or makes a failed attempt retryable.

No Kaggle or other network service was called. No repository file was changed by this review other than this report. Any pre-existing out-of-scope worktree changes observed during the review were left untouched.

## Binding authority and protocol silence

I read `provenance/protocol_freeze.json` and `.md` before judging v8, followed by SPEC §§5, 6, 7, 11 and 12 and plan TASK-04. Their current identities remain the frozen identities:

- freeze JSON: `6d5aa3ff47cba97f8ecd0dd15683bb96f0d53146f3af1ce1e95bf24cec7cbc8b`;
- freeze Markdown: `1a41b1aa684e26e5853aae31369c5200b29ae25a70bc383e3f0bd3ef136058be`;
- SPEC: `76ef27520460abb7c4c6eee76061adad59e9c6f34f203c1a941f41125d60ec8b`;
- plan: `cd547e9e1c0fc6c2ecc3dccb12c6d3062dbc000296e8778341eadc9b32610b43`.

The frozen protocol requires one identifiable training run, validation-only unrounded checkpoint selection with last-epoch tie breaking, preservation of failures and artifacts, complete environment/configuration/code identities, and no test access during training. It permits a failed run to remain a recorded failure and requires dependent branches to remain blocked.

The frozen protocol is silent on Kaggle kernel slug/version semantics, an exact numerical retry limit, exact platform-log grammar, the local reconciliation transaction, and an independent Kaggle custodian. V8 may define those mechanics. In particular, the declared absence of an independent custodian is a limitation already allowed by the frozen protocol and is not a finding.

## Reviewed delta and identities

Commit `e421ce2` is the reviewed v8 fix. The training-relevant code hashes equal the identities in the v8 JSON:

| File | SHA256 |
|---|---|
| `src/evaluation/train_model1.py` | `9dd613910d4d1cbcb2a4326fad74f9cf9a8abed733d7e3dc8b7be45b1c309f84` |
| `src/evaluation/kaggle_job.py` | `9aecd22da3e733c82b4504f1c435b935d18ac90815bbdc6b3751854121d22574` |
| `provenance/commands/task04/render_kaggle_job.py` | `897bd50259659e9805c5ad2bb75e146ee88729cd2bd8d3137735ad55377f0ed5` |
| `provenance/commands/task04/verify_kaggle_run.py` | `05c60a982349ed535efc2ccc865fe98d3ebb354874c7b2012e93c09ca735e281` |
| `tests/test_kaggle_job.py` | `fae46737562a4ae7226c7341b6def4a9a580e777814ae5ebf7ddcd2f2ac02100` |
| `tests/test_verify_kaggle_run.py` | `61ea5ce2198601276698220fd663d80abde7af2ca9f4e55cd87470a85de6a8c5` |

The amendment Markdown hash is `788390c6aff4429e231e16cdee8b0dc4b0c141e88f78e3593502fe67c18a59bf`, matching its JSON sidecar. The JSON retry policy equals `kaggle_job.RETRY_POLICY` structurally.

V8 changes no training hyperparameter, seed, data membership, trainer selection rule, or test-access rule. `train_model1.py` and `tests/test_run_contract.py` are unchanged by `e421ce2`; the training branch still renders only train/validation inputs and uses the approved trainer/job hashes. The v8 inference edits do not execute on the training path.

## Fresh verification

Each requested module ran in its own Python process with bytecode disabled:

| Command | Result |
|---|---:|
| `.\.venv\Scripts\python.exe -m unittest tests.test_kaggle_job -v` | 44 passed |
| `.\.venv\Scripts\python.exe -m unittest tests.test_verify_kaggle_run -v` | 14 passed |
| `.\.venv\Scripts\python.exe -m unittest tests.test_run_contract -v` | 12 passed |
| **Total** | **70 passed, 0 failures/errors** |

`render_kaggle_job.capacity_retained` also passed read-only against `KAGGLE-CAPACITY-001`.

### Fresh KAGGLE-CAPACITY-002 reconciliation

Calling the current `reconcile` on `experiments/model1/KAGGLE-CAPACITY-002/v1` produced bytes exactly equal to the committed `reconciliation.json`:

- fresh and committed SHA256: `4bb733f5e22bcaf10e7bd0571734aae79a98e952f062f8a123d22fe6010b1b74`;
- the re-derived ledger entry exactly equals the sole committed `attempts.jsonl` entry;
- 17 downloaded files were hashed;
- `inventory_not_downloaded` is empty;
- only `job_log.txt` and `receipt.json` are unattested, as designed because the job receipt inventory excludes the live log and itself;
- status and platform status are both `COMPLETE`;
- executed/rendered source SHA256 is `30ba388913a7ca519e6b3541c9c3d885b876dbb2d089608e5785c01a6033ce1b`.

A fresh call to `seal` also reproduced the committed `verification.json` exactly, verified 552 train/validation files, and retained `capacity.fits=true`.

## Round-7 counterexample replay and disposition

### H-03 — CLOSED

`EXPERIMENT_OF` and `check_experiment` bind training to exactly `EXP-R01`; `attempt_dir` invokes that check before allocating a directory. `check_attempt` additionally requires every ledger row to carry the current mode and experiment. Thus `EXP-R01-copy/v1` is refused even if canonical EXP-R01 has already completed, and a later canonical version is refused after any `COMPLETE` ledger row (`kaggle_job.py:69,87-93,362-379`; `render_kaggle_job.py:101-142`).

For a retry, `attempt_dir` requires `kernel.py`, `render_record.json`, `platform.json`, `platform_log.json`, `receipt.json`, `job_log.txt`, and `reconciliation.json`; requires every retained file to be committed and clean; recomputes reconciliation; compares its exact bytes with the committed record; and compares the reconstructed ledger row. The temporary-git-repository test rejected missing `job_log.txt`, missing `platform_log.json`, missing `reconciliation.json`, altered logs, uncommitted evidence, another namespace, and another mode.

**Consequence removed:** neither a second training namespace nor a retry based on incomplete/stale evidence is authorized. The first completed EXP-R01 remains definitive.

### N-07 — CLOSED

The hard-cut replay left the last receipt at `RUNNING`, stage `training`, then wrote `run/epoch_records.jsonl` and `run/train/weights/last.pt`. Fresh reconciliation hashed both platform-listed files, marked both unattested because they postdated the receipt, and kept the attempt non-retryable (`verify_kaggle_run.py:65-138`; `tests/test_verify_kaggle_run.py:84-96`). Missing platform-listed output, unlisted downloaded output, a receipt without `job_log.txt`, and missing/altered evidence all fail reconciliation.

**Consequence removed:** partial epoch/weight bytes surviving a post-training-start cut are now identifiable instead of disappearing from the immutable record. The narrower temporary-file and non-core omission cases found in this round are recorded separately as LOW findings below.

### NEW-M-01 — CLOSED

`atomic_write` writes and fsyncs a temporary file before `os.replace`. `finalize` orders reconciliation, then the capacity verification or EXP-R01 selection record, and the ledger last; existing bytes must equal exact recomputation. Fault injection before each of the three write boundaries resumed to the same bytes, and a second rerun was a no-op. Divergent existing selection bytes were rejected (`verify_kaggle_run.py:55-63,143-175`; `tests/test_verify_kaggle_run.py:139-181`).

**Consequence removed:** once a complete EXP-R01 can be sealed, interruption of the local verifier cannot leave a ledger row without a recoverable selection record.

### NEW-L-01 — CLOSED

`pip_check_verdict` now treats exit code 0 separately: empty output and exactly `No broken requirements found.` pass; contradictory or other output blocks. Nonzero exit handling remains conservative and closure-aware (`kaggle_job.py:325-340`; `tests/test_kaggle_job.py:365-373`).

**Consequence removed:** a healthy Kaggle image no longer fails before training solely because pip emitted its normal success line.

## New LOW findings

### NEW-L-02 — Platform-listed receipt temporary file cannot be reconciled

**Severity:** LOW.  
**Location:** `src/evaluation/kaggle_job.py:390-395`; `provenance/commands/task04/verify_kaggle_run.py:76-83`.  
**Evidence:** `write_receipt` uses `receipt.json.tmp`. A synthetic hard cut with the prior `receipt.json` plus a platform-listed `receipt.json.tmp` was rejected as `platform outputs not downloaded: ['receipt.json.tmp']`: `reconcile` excludes every filename ending in `.tmp` before comparing against the platform list.  
**Consequence:** a cut in the narrow receipt-replacement window is fail-safe and non-retryable, but the attempt cannot receive the formal reconciliation/ledger record even though the temporary bytes were downloaded. It cannot authorize another run or alter a selection.  
**Resolution criterion:** exclude only verifier-owned temporary paths (`reconciliation.json.tmp`, `verification.json.tmp`, selection/ledger temporaries outside the attempt) or hash a platform-listed job temporary file as unattested. Add a cut fixture containing `receipt.json.tmp` and require successful non-retryable reconciliation.

### NEW-L-03 — Non-core receipt-inventory omissions are exposed but do not stop sealing

**Severity:** LOW.  
**Location:** `provenance/commands/task04/verify_kaggle_run.py:91-102,118-127,196-197`.  
**Evidence:** a synthetic `COMPLETE` training receipt that attested `run/train/results.csv`, while the platform list/download omitted that file but retained the mandatory epoch records, selected checkpoint, evidence and log, was accepted as `definitive=true`; the omission appeared only in `inventory_not_downloaded`.  
**Consequence:** the selection-critical files, job log and environment evidence remain mandatory, so checkpoint selection and retry discipline are not weakened. However, an ancillary receipt-attested artifact can be absent while the verifier proceeds to sealing; the omission is visible but not a hard failure.  
**Resolution criterion:** before sealing, either reject any nonempty `inventory_not_downloaded`, or define an explicit optional-artifact allowlist consistent with frozen Gate E/TASK-04 and test both mandatory and optional cases.

## Verdict

**PROTOCOL-AMENDMENT-008 v8 may move to `APPROVED` for EXP-R01 training.** The exact round-7 HIGH/MEDIUM counterexamples are closed, the training code/config identities match the proposed amendment, the required tests pass, and KAGGLE-CAPACITY-002 re-reconciles byte-for-byte. The two LOW findings should be corrected or explicitly handled before claiming a later full Gate E artifact record if either condition occurs, but neither restores scientific optionality or risks an incorrect checkpoint selection.

Inference remains blocked by amendment §5 and was not approved or adjudicated here.

| Finding | Severity | Round-8 status | Gate effect |
|---|---:|---|---|
| H-03 — one-way attempt/retry discipline | HIGH | **CLOSED** | None |
| N-07 — partial/error-run record | MEDIUM | **CLOSED** | None |
| NEW-M-01 — atomic, restartable sealing | MEDIUM | **CLOSED** | None |
| NEW-L-01 — healthy pip-check output | LOW | **CLOSED** | None |
| NEW-L-02 — platform-listed receipt temporary | LOW | **OPEN** | Does not block approval; a narrow hard cut cannot be formally reconciled |
| NEW-L-03 — non-core receipt omission | LOW | **OPEN** | Does not block approval; omission is visible and selection-critical artifacts remain mandatory |

**Open counts: HIGH = 0; MEDIUM = 0.**
