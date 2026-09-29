# TASK-05 independent methodological review — round 7

Date: 2026-09-27  
Reviewed repository state: `4f90c9fef20b429c421d12aa7fad557843a5eccb`  
Scope: prospective inference-approval review after `d7ef6ec`, `4b3edde`, `ff1293c`, `98a6d0b`, and `672d45e`. No research inference, Kaggle call, network write, product-code fix, commit, push, or `.docx` access was performed. All mutable probes used disposable repositories outside the worktree. The only worktree write made by this review is this report.

## Verdict

**DO NOT APPROVE the combined inference snapshot yet.** The three M1 findings closed in round 6 remain closed, and all 17 declared scope entries (14 unique files) equal both the proposed SHA256 and the committed `HEAD` blob. The ordinary replays requested for M2 now reject an in-checkout `ultralytics` package, a foreign interpreter, and a false/PROPOSED approval before producing predictions.

However, **NEW-HIGH-05 remains PARTIALLY CLOSED / OPEN**. The environment gate authenticates the interpreter path and the list of 43 distribution names/versions, not the code actually imported. A literal M2 command run in the approved `.venv` accepted an untracked checkout `sitecustomize.py` loaded through an allowed checkout `PYTHONPATH`; that startup hook supplied a deterministic Ultralytics substitute while declaring an origin under the `.venv`. EXP-R03 completed 219 predictions and recorded `ultralytics=8.4.52`, `dependencies_outside_checkout=true`, and the approved environment-record hash. The same run also used a committed `{}` as `configs/evaluation_frozen.json`: the producer checks only canonical path and Git cleanliness, not that the file is an operating-point freeze with a valid sidecar and sealed M1 provenance.

This does not require a custodian, signatures, platform attestation, or protection against a trusted committer fabricating the repository. The committed Git repository remains the root of trust. The missing checks are local and deterministic: authenticate the actual imported distribution files/import state, and validate that the committed canonical config is a real M1 freeze before reading M2 test bytes.

**Open count: HIGH = 1; MEDIUM = 0.**

## Binding authority and trust model

Read before review:

- immutable `provenance/protocol_freeze.json` and `.md`;
- SPEC §§6, 7, 11, and 12;
- frozen plan TASK-05 and its literal commands;
- PROTOCOL-AMENDMENT-008 §§4 and 5.1;
- `reports/execution/task-05-independent-review-round6.md`.

Amendment 008 §4 declares no independent custodian. Accordingly, this review treats committed Git identities as authoritative and does not demand signatures or external attestation. It asks only whether the code ensures that the local runtime/config actually used are the committed identities the review approved.

The out-of-scope manuscript, response, TASK-09 scripts, editorial audit, state report, `configs/class_names.json`, document checks, and provenance isolation-test edits are not entries in either inference snapshot. They were not opened beyond the name/stat comparison; the `.docx` was not opened.

## Fresh verification

Each requested module ran in its own fresh Python process with `PYTHONDONTWRITEBYTECODE=1`. The last three processes ran concurrently but remained separate processes.

| Command | Fresh result |
|---|---:|
| `.\.venv\Scripts\python.exe -m unittest tests.test_evaluation` | 57 passed; exit 0; 155.084 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_intervals` | 31 passed; exit 0; 35.410 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_predict_model2` | 8 passed; exit 0; 0.358 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_kaggle_job` | 44 passed; exit 0; 0.187 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_verify_kaggle_run` | 14 passed; exit 0; 7.442 s |
| **Total** | **154 passed; 0 failures/errors** |

The worktree was clean before and after these commands.

## Round-6 finding disposition and counterexample replay

### NEW-HIGH-05 — PARTIALLY CLOSED / OPEN

**What closed:**

1. **Ordinary in-checkout substitute.** In a disposable Git copy with only the two approval-state fields changed and a committed canonical config, an untracked `ultralytics/__init__.py` advertising 8.4.52 was selected by the literal M2 command. The producer refused it at `predict_model2.py:121-123`. No prediction file was written. The current wrapper returned 1 and left an empty EXP-R03 directory; the separate exit-code defect is NEW-LOW-01 below.
2. **Foreign interpreter.** The literal command under `C:\Python314\python.exe`, carrying the stub through the disposable checkout, was refused with `inference runs only in <checkout>\.venv, not C:\Python314`; no run directory was created.
3. **Declared package set.** On the real repository, `authority.check_environment` passed with identical resolved prefix paths, exactly 43 installed distributions, and environment-record SHA256 `64086b292d15a63b9418dfba1523b6343c60db2a8ba9a69ca0a17b7f5a345d4b`.
4. **Downstream fields.** `authenticate_m2` now checks Ultralytics version, config path/hash, `dependencies_outside_checkout`, environment path/hash, producer hash, committed promotion bundle, and the approved M2 snapshot.

**What remains open:**

- **Actual runtime code is not authenticated.** `authority.environment_lines` (`authority.py:49-53`) records distribution metadata only. `check_environment` (`authority.py:56-61`) compares that text and the prefix. `verify_environment` (`provenance.py:247-266`) allows `sys.path` entries inside the checkout and does not reject `PYTHONPATH`, `sitecustomize`, `usercustomize`, or a nonstandard `sys.meta_path`. Finally, `outside_checkout` (`predict_model2.py:38-42`) trusts the imported module's mutable `__file__` attribute.
- **Literal counterexample:** with the approved `.venv`, exact 43-package record, `PYTHONPATH=<disposable checkout>`, and an untracked `sitecustomize.py`, the literal frozen M2 command exited 0 and wrote all 219 predictions. The hook supplied a deterministic module while declaring `__file__` under `.venv/Lib/site-packages`. The run record claimed `ultralytics=8.4.52`, `dependencies_outside_checkout=true`, and the approved environment SHA. Thus package names/versions and a claimed origin do not bind the probabilities to the installed Ultralytics distribution.
- **The canonical config is not validated as a freeze.** `predict_model2.run` (`predict_model2.py:92-94`) only requires the path `configs/evaluation_frozen.json` and `committed_clean`; it does not parse the file, require its sidecar, or call the M1 `sealed_config` validator. `authenticate_m2` (`intervals.py:634-642`) repeats only cleanliness and current hash equality. A committed file containing `{}` (SHA256 `ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356`) passed this gate and was recorded by the successful 219-image counterexample. This does not prove EXP-V01 or the operating-point freeze occurred.
- **Promotion does not cure either route.** In the ordered disposable replay, a deterministic substitute bundle carrying the approved version/environment/config fields was committed using the prescribed three-file promotion. Both the primary and sensitivity interval commands accepted it. That behavior is expected from the current consumer: it authenticates recorded fields, not the runtime code that produced them.

**Consequence:** EXP-R03 probabilities, point estimates, and intervals can be attributed to the approved producer/environment/config fields even though the imported inference implementation was untracked and the supposed frozen config was arbitrary. This is the same scientific-provenance consequence as round 6 and still blocks EXP-R03 and both M2 interval commands.

**Resolution criterion:** before any M2 test byte or run-directory creation, (1) validate `configs/evaluation_frozen.json` with its sidecar and the existing M1 `sealed_config`/selection/test-digest contracts, not only its path and Git status; (2) reject startup import overrides such as `PYTHONPATH`/`sitecustomize` and nonstandard import finders for scientific runs; (3) require the imported Ultralytics and torch origins to be real files belonging to the expected `.venv` distributions and verify their installed files against committed hashes or their wheel `RECORD` hashes; and (4) record and recheck those concrete identities in `run_record.json`. A negative literal-command test must reproduce the startup-hook and `{}`-config probes and refuse both. No independent custodian or external attestation is required.

### NEW-HIGH-06 — CLOSED

`predict_model2.run` now calls `authority.approved_inference(root, 'm2')` at lines 87-91, before config inspection, output creation, manifest/image reads, or scientific imports. With the real amendment left `inference_approved=false` and `inference_approval.state=PROPOSED`, the literal M2 command was refused, no EXP-R03 directory was created, and the unit regression confirmed `csv.DictReader` was never called. The core round-6 consequence—M2 test observation before approval—is closed.

The wrapper returned exit 1 with a traceback rather than the requested controlled exit 2 because `evaluate.py` catches its own `RunRejected`, not `predict_model2.RunRejected`. That does not allow inference or test access, so it is split out as NEW-LOW-01 rather than keeping the HIGH open.

## M1 closure and real-repository checks

The M1-relevant changes since round 6 add the shared environment record/check; they do not weaken the approved verifier, attempt root, selection binding, or exact authority snapshot.

| Round-6 M1 finding | Round-7 status | Fresh evidence |
|---|---|---|
| HIGH-04 — unrooted verifier | **CLOSED** | `verify_kaggle_run.py` remains in the M1 snapshot. `tests.test_evaluation` passed the altered-verifier rejection, and real EXP-R01 reconciliation re-derived byte-for-byte. |
| NEW-HIGH-01 — threshold authentication depended on HIGH-04 | **CLOSED** | The freezer still reaches validation only through the committed definitive attempt and approved verifier. The ordered replay froze only after EXP-V01 reconciliation/promotion. |
| NEW-HIGH-03 — approval not bound to reviewed authorities | **CLOSED** | The committed-replacement-chain test passed; every current M1 authority equals the proposed and `HEAD` SHA256. |

Read-only real EXP-R01 reconciliation at current `HEAD` confirmed:

- `reconciliation.json` equals the pure recomputation byte-for-byte;
- the sole ledger line equals the recomputed definitive entry;
- `selection_record.json` equals the recomputed seal byte-for-byte;
- 552 train/validation files verify;
- selected epoch is 91, fitness is `0.760868639693682`, and selected checkpoint SHA256 is `0648da3f3641e3cdb5a1908a092ba892548942836a249bb3b39667f9ae8e8125`.

These statements close the named M1 findings. They do not negate the shared local-runtime weakness described under NEW-HIGH-05 where local scientific packages are imported.

## Proposed snapshot against committed bytes

For every path in Amendment 008 `inference_approval.m1` and `.m2`, the proposed SHA256 equals both the real worktree bytes and `git show HEAD:<path>`; every path is tracked and clean.

| Scope | Declared entries | Proposed = filesystem = `HEAD` | Result |
|---|---:|---:|---|
| M1 | 11 | 11/11 | PASS |
| M2 | 6 | 6/6 | PASS |
| Unique paths | 14 | 14/14 | PASS |

Key new identities are: environment record `64086b29…345d4b`, `authority.py` `f6fb5942…450f60`, `predict_model2.py` `3606a55b…1fd0b`, and `intervals.py` `d2058fde…41a70`. The amendment itself is committed and clean; only its two state fields were changed in disposable approval replays, as designed.

## Frozen command-sequence replay

A fresh disposable Git copy of the real `4f90c9f` tree was used. Before generated artifacts were added, the only repository change was:

- `inference_approved: false → true`;
- `inference_approval.state: PROPOSED → APPROVED`.

No Kaggle call or research inference was made. Deterministic synthetic Kaggle receipts exercised the real M1 reconciliation/evaluation code over the real frozen manifest, and a deterministic M2 backend exercised the real approved producer, ART-002 hash check, 219 real manifest/image hashes, promotion, and consumers. The resulting metrics are interface evidence only and are not scientific observations.

| Ordered step | Result |
|---|---|
| Create/reconcile/commit synthetic EXP-V01 definitive attempt | PASS; 113 validation images |
| Literal EXP-V01 command | PASS; exit 0 |
| Literal operating-point freeze | PASS; deterministic threshold 0.05 |
| Try EXP-R03 before committing the frozen config | REFUSED; no run directory, proving the current Git-cleanliness order check is active |
| Commit genuine frozen config and sidecar | PASS |
| Create/reconcile/commit synthetic EXP-R02 definitive attempt | PASS; 117 test images |
| Literal EXP-R02 command | PASS; exit 0; threshold 0.05 |
| Literal M1 intervals, seed 42 / 2,000 draws | PASS; exit 0; 10 reported metrics |
| M2 producer with deterministic non-scientific backend | PASS; 219 rows; genuine frozen-config SHA256 `341f39c7b3fc8c93268465f0b41fd981fa1198a13a58828351a59437062029bc` |
| Commit prescribed EXP-R03 three-file promotion | PASS |
| Literal primary M2 intervals, seed 42 / 2,000 draws | PASS; exit 0 |
| Literal M2 sensitivity, seed 42 / 2,000 draws | PASS; exit 0; all three schemes and 2,000 shared draws |

Thus the intended ordered sequence has no new path/parser/output-order rejection. The pre-commit refusal confirms the producer waits for a committed file at the frozen-config path. The committed `{}` counterexample separately proves that this is only a filename/Git-order check, not yet proof of an operating-point freeze.

## New defect

### NEW-LOW-01 — LOW — M2 rejections through the frozen wrapper exit 1 with a traceback

- **Location:** `src/evaluation/evaluate.py:768-776,804-810`; `src/evaluation/predict_model2.py:45,89-94,121-123`.
- **Evidence:** the false-approval, uncommitted-config, in-checkout-module, and foreign-interpreter literal commands all raised `src.evaluation.predict_model2.RunRejected`. The `evaluate.py` module catches only its distinct local `RunRejected` plus `InvalidInput`, so the process emitted a traceback and exit 1. The direct producer CLI does catch its own exception, and the current wrapper test mocks only success.
- **Consequence:** automation cannot rely on the documented invalid-input exit 2 or concise `REJECTED:` message. Scientific gates still refuse before inference, so this is not HIGH or MEDIUM.
- **Resolution criterion:** translate `predict_model2.RunRejected` to `evaluate.RunRejected` at the dispatcher boundary, or catch both in `evaluate.py`; add a literal wrapper test asserting exit 2, no traceback, no model call, and no run directory for false approval.

## Approval decision by step

| Step | Decision | Reason |
|---|---:|---|
| EXP-V01 | **M1 closures remain approvable in isolation** | Verifier, attempt root, checkpoint/config/manifest, and exact M1 snapshot remain enforced. |
| Operating-point freeze | **M1 closures remain approvable in isolation** | Validation provenance and replacement-chain protections remain intact. |
| EXP-R02 | **M1 closures remain approvable in isolation** | Frozen-config and definitive-attempt contracts passed the ordered replay. |
| M1 interval command | **Not sufficient to approve the combined snapshot** | Its named M1 closures hold, but the proposed approval is shared and the local environment control has an open provenance bypass. |
| EXP-R03 | **NO** | Arbitrary committed config and untracked imported runtime can produce an apparently approved run record. |
| Primary M2 interval command | **NO** | It accepts the promoted record fields produced through that open route. |
| M2 sensitivity command | **NO** | Same unauthenticated EXP-R03 runtime/config source. |

## Final findings

| ID | Severity | Status | Blocks |
|---|---:|---|---|
| HIGH-04 | HIGH | CLOSED | — |
| NEW-HIGH-01 | HIGH | CLOSED | — |
| NEW-HIGH-03 | HIGH | CLOSED | — |
| NEW-HIGH-05 | HIGH | PARTIALLY CLOSED / OPEN | EXP-R03, primary M2 intervals, M2 sensitivity; combined approval |
| NEW-HIGH-06 | HIGH | CLOSED | — |
| NEW-LOW-01 | LOW | OPEN | Controlled CLI error contract only |

**Open count: HIGH = 1; MEDIUM = 0. Overall verdict: DO NOT APPROVE the proposed combined inference snapshot.**
