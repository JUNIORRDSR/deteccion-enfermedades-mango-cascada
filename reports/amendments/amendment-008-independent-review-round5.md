# Fifth-round independent methodological review — PROTOCOL-AMENDMENT-008 version 5

- **Requested remediation snapshot:** `ce8cae0..5b5158a` (version 4 to version 5, including the unrounded-fitness correction in `5b5158a`).
- **Review posture:** remediation statements were treated as claims to falsify. I did not upload or attach data, call a Kaggle write operation, launch a kernel, train a model, or perform inference.
- **Scope note:** `HEAD` was `5b5158a` when this review began, exactly matching the user's description. While the review was running, another process advanced the shared worktree through `3d8af8c`, `253ed2b` and `faddb37`. Those later commits are not part of this round-5 snapshot and are not credited as remediation here. They require a fresh review if proposed for closure.

## Verdict

**DO NOT APPROVE. PROTOCOL-AMENDMENT-008 version 5 may not move from `PROPOSED_V5` to `APPROVED`, including for the EXP-R01-only training scope.**

Version 5 removes the v4 attachment surface and its reproduced path/symlink/schema bypasses. With the intended manifest and the checked-in job, the GitHub tree, raw blobs, LF-normalised labels, selected-file digest, and base-checkpoint digest form a strong byte-integrity chain. That chain nevertheless has no trusted root: the renderer accepts any caller-supplied manifest plus an adjacent self-authored sidecar, derives its test-forbidden list from that same input, and embeds a trainer whose hash is supplied by the same payload. The run receipt also does not bind the platform-executed kernel bytes to the checked-in kernel. I reproduced an in-memory manifest substitution that changed a frozen test row to train; the renderer accepted it and selected 556 rather than 555 files.

The probe demonstrates that a GPU kernel can execute, download the corpus and base checkpoint, and return an output. It does not demonstrate that 150 epochs fit the session: it ran for 30.38 seconds and built no model. The official Kaggle documentation supports the 12-hour CPU/GPU session limit, but the claim that EXP-R01 fits “with ample margin” remains an unmeasured projection.

Open findings across the amendment are **HIGH 2, MEDIUM 3**:

- HIGH: H-02 and H-03.
- MEDIUM: M-01, N-06, and N-07.

H-03 applies to the still-blocked inference scope, not directly to EXP-R01. The direct EXP-R01 blockers are therefore **HIGH 1, MEDIUM 3**. M-02's inference block is legitimate and is closed for the training-only approval scope, but it does not authorize inference.

## Prior-finding disposition

| Finding | Prior severity | Round-5 status | Disposition |
|---|---:|---|---|
| H-02 — phase input/test-byte integrity | HIGH | **OPEN** | Per-byte verification works, but the authoritative manifest, trainer and actually executed kernel are not independently bound. |
| H-03 — one-way test discipline | HIGH | **PARTIALLY CLOSED** | Removing the custodian is consistent with the frozen text, which never required one; the future single-version and retry rules remain contradictory and non-exhaustive. |
| M-01 — schedulable capacity | MEDIUM | **PARTIALLY CLOSED** | Platform execution and output retrieval are demonstrated; full-run time/memory/storage capacity is not. |
| M-02 — prediction transfer | MEDIUM | **CLOSED for EXP-R01 scope** | Inference is explicitly blocked pending the evaluator, tests and independent review; the proposed per-image list shape removes the v4 duplicate/no-detection contradiction. |
| N-04 — venue rationale and decision chain | LOW | **CLOSED** | v5 states that local CPU is viable and plan-authorized, and cites the user's later Kaggle decision. |
| N-05 — Markdown/JSON agreement | LOW | **CLOSED at `5b5158a`** | Version, timestamp, state, scope, prior review and recorded hashes agree at the requested snapshot. |

## Checks performed

### Frozen authority and immutability

The current frozen files have the required SHA-256 values and no diff from their committed bytes:

- `provenance/protocol_freeze.json`: `6d5aa3ff47cba97f8ecd0dd15683bb96f0d53146f3af1ce1e95bf24cec7cbc8b`.
- `provenance/protocol_freeze.md`: `1a41b1aa684e26e5853aae31369c5200b29ae25a70bc383e3f0bd3ef136058be`.

The spec and plan hashes recorded inside the freeze also match their current files:

- SPEC: `76ef27520460abb7c4c6eee76061adad59e9c6f34f203c1a941f41125d60ec8b`.
- Plan: `cd547e9e1c0fc6c2ecc3dccb12c6d3062dbc000296e8778341eadc9b32610b43`.

The binding requirements relevant here are:

- SPEC §6: test must be inaccessible to architecture, checkpoint, epoch, augmentation and threshold selection; all access/contamination is logged.
- SPEC §7 and TASK-04: train from the identified base, select only by unrounded validation fitness with last exact tie, retain byte identity, and do not evaluate test during training.
- TASK-05: freeze the validation-selected operating point before the single test evaluation and retain per-image predictions.
- SPEC §4.3 and §11: preserve environment/provenance and failures; an experimental block stops only its dependent branch.

The frozen protocol is **silent** on an independent test custodian, signing key, Kaggle kernel slug/version semantics, Kaggle control-plane retention, the platform's session-duration limit, and the exact JSONL envelope before TASK-05 implements it. It is not silent on authoritative manifest identity, train/test separation, environment provenance, failure retention, a single test evaluation, or test-access logging.

### Prescribed and related tests

With bytecode writes disabled, I ran:

```powershell
& .\.venv\Scripts\python.exe -m unittest tests.test_kaggle_job tests.test_run_contract -v
```

At the requested `5b5158a` snapshot, **25 tests ran and passed**: 13 Kaggle-job tests and 12 run-contract tests. The unrounded-fitness fixture passes, and local Ultralytics 8.4.52 source confirms that `validator.py:267` rounds the dictionary returned to the trainer to five decimals while `trainer.validator.metrics` retains the underlying `DetMetrics`. The callback occurs after native save. The `5b5158a` change therefore correctly records the unrounded validation fitness and retains the native rounded value separately.

Passing tests do not close H-02 because no test gives the renderer a different but self-consistently sidecar-hashed manifest.

### Independent Git-object and line-ending verification

I used read-only `git cat-file --batch` against `C:\Users\junio\Downloads\mango-vision\SemilleroTI-Mangos` at commit `98614804dd967e19a77af9fc58c27364d2e43bc9`, with `GIT_OPTIONAL_LOCKS=0` and a command-local `safe.directory` override. Every blob object ID was recomputed from its bytes.

Results for the 669-row manifest used by the probe (`model1_clean_manifest_A_draft.csv`, SHA-256 `aabb435227ab432c3a4b8b4fd45a474de2ac2e8114d49da858acc8dcacd283e2`):

- local image bytes matching both manifest and commit: **669/669**;
- labels exactly matching the commit: **465/669**;
- labels differing only because local CRLF becomes commit LF: **204/669**;
- any other label-content difference: **0**;
- `paths_digest`: `56a5280554e48e9472e0e235b2b136ae314ee22f3ad52e16d69513cfb002c6a1`, matching the probe payload;
- all-file digest: `4470a1c67823118d36add2eeaa28629807a37d117050ee0e1c018371ea59786d`, matching payload and receipt;
- proposed split counts: train 445, valid 110, test 114;
- selected train+valid digest: `f0873e402264431c7c553a2532782f23edb265e649ba4e51f7b200334cc17ac8` over 555 files;
- basename collisions within the generated train/valid view: **0**.

The LF-normalisation claim is therefore verified. The tree response's `truncated=false` requirement, the sorted 669-path digest, Git-blob SHA-1 check and independent selected-file SHA-256 digest mean that, **given the intended manifest-derived payload**, neither a different GitHub tree nor different raw content can silently pass.

### Probe evidence and declaration

The checked-in probe record and receipt are internally consistent:

- local kernel SHA-256 equals `render_record.json`: `608bbec74b6e6e01fa0c237ee8db31e68e4a7c84fe3d936abe5b411e0e19ffd1`;
- payload SHA-256 equals both render record and receipt: `caa93579e187273a0e2aec97a51c68830227a7ae622e1a1daac03d5ec9919102`;
- receipt contains 669 `split=all` entries and recomputes to the payload file digest;
- base SHA-256 is `9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef`;
- environment reports Python 3.12.13, Ultralytics 8.4.52, torch 2.10.0+cu128, CUDA 12.8 and two Tesla T4 devices;
- receipt has no model result and says `test_evaluated=false`;
- duration was 30.376 seconds.

`TEST-ACCESS-003` accurately records that the probe read all test bytes only for hashing, with no inference or selection. The amendment also accurately says it ran before approval, against the v4 zero-execution text, at the user's explicit request. This is an adequately declared procedural deviation and not a hidden scientific test observation.

It is not, however, proof that the exact checked-in kernel ran: the receipt contains the payload digest but no kernel digest, kernel ID, version, session ID or slug. `render_record.json` proves what was rendered locally, not what the platform executed. In addition, the checked-in probe kernel is not an exact rerender from the v5 `kaggle_job.py` at `5b5158a`; the latter has later pre-import/offline/font changes. This limitation is material to H-02's executable chain but does not turn the declared no-model probe into a scientific result.

## Prior findings

### H-02 — HIGH — OPEN

**Evidence checked:** amendment §§2–3 and §7; `src/evaluation/kaggle_job.py`; `provenance/commands/task04/render_kaggle_job.py`; all 13 supplied tests; the full 1,338-blob `git cat-file` comparison; probe kernel/render record/receipt; amendment hashes; and an independent in-memory substitution.

The v5 byte-level design is sound after a trusted payload exists:

1. `image_paths` requires a non-truncated tree and derives an exact sorted corpus list.
2. `paths_digest` fixes all 669 image paths.
3. Git blob SHA-1 fixes each raw response against the returned tree.
4. `files_digest` independently fixes every selected image SHA-256 and LF-normalised label SHA-256.
5. The training view and `data.yaml` include only the payload's `t` and `v` entries and no test/download key.
6. `/kaggle/input` top-level entries cause rejection.

The missing control is the authoritative root of that chain:

- `render_kaggle_job.py:39,46-49` accepts any `--manifest` and trusts the `.sha256` file beside it. It does not require the final `data/manifests/model1_clean_manifest.csv`, its independently approved hash, or a reviewed TASK-03 record.
- The forbidden path/name/hash list at `render_kaggle_job.py:51-61` is derived from that same manifest. A substituted row is therefore reclassified before the forbidden list exists.
- `manifest_sha256` is placed in the payload but the Kaggle job never compares it with an independently fixed expected value.
- The trainer hash is also self-consistent rather than authoritative: the renderer embeds the current source and its current hash, and the job compares the embedded source only with that embedded hash. The v5 JSON records job/renderer/test hashes but not the `5b5158a` trainer hash `dd78a7a5d72fa70d82f027c1b20aaa1132db8ca1100faaa670a75d9e8ba5350d`.
- The receipt binds only the payload, not the outer kernel source actually executed on Kaggle.

**Counterexample:** in memory, I copied the real 669 rows, changed frozen test row `SRC-009688` from `test` to `train`, recomputed the sidecar-derived split and selected-file digest, and generated the forbidden list from the altered rows. `job.render(...)` returned a valid script. Its split code for that true test path was `t`; it selected 556 files instead of 555; and the true test path, filename and image hash were absent from the resulting forbidden list. No data byte was altered, so all runtime tree/blob/file-digest checks would pass and the job could report success after training on a test image.

**Scientific consequence:** EXP-R01 can obtain a test byte while every byte-level check is internally consistent, or execute a different trainer/kernel while producing the same payload digest. The result would violate frozen SPEC §6, TASK-04's no-test rule and Gate E.

**Resolution criterion:** after TASK-03 produces the final reviewed manifest, bind the renderer to its exact path and independently recorded hash; derive and compare an expected per-file receipt map outside the kernel; record the exact trainer hash in the amendment and make it an approved constant rather than a payload self-hash; preserve or retrieve the platform version's source and compare its full kernel SHA-256 with the reviewed render before accepting outputs; add negative tests for an alternate validly sidecar-hashed manifest, a changed trainer with matching self-hash, an extra/mis-split receipt file, and a platform-source/kernel-hash mismatch. A fresh independent review must rerun the `SRC-009688` substitution.

### H-03 — HIGH — PARTIALLY CLOSED

**Evidence checked:** frozen SPEC §§6, 7 and 11; TASK-04/05; amendment §4; JSON `test_discipline`; and the EXP-R01-only scope.

The v5 argument is correct on one important point: the frozen protocol does **not** require a custodian, signing key or adversarially immutable execution broker for the local venue. Removing the unavailable v4 custodian does not itself weaken a named frozen control. Both venues ultimately rely on an honest operator plus reviewable code, artifacts and access logs; Kaggle's version timestamps add evidence but do not prove absence of deleted or unrecorded attempts.

The proposed pre-test seal is substantially better specified than v4: it names the checkpoint hash, validation-selected threshold, evaluator hash, test-selection digest and source training-kernel version. That is sufficient content if those bytes and the exact commit are independently verified before inference.

The execution rule is not yet precise enough:

- amendment §4 item 3 says any second version or second kernel is a Gate-E failure;
- item 4 permits a retry after platform `ERROR` or byte-verification failure without metrics;
- a retry necessarily needs another execution/version, but the text does not define the exception, required identifier, preservation of the first attempt, or how “no metrics” is proved from logs and partial outputs;
- before/after account lists remain operator-captured and non-exhaustive. This is also true of local process logs, so it does not justify reintroducing a custodian, but it does not support the stronger implication that platform evidence prevents shadow attempts.

**Scientific consequence:** if later inference is unblocked, two implementers can treat the same second version as either the only permitted retry or an automatic Gate-E failure. Partial metric exposure can be misclassified as “no result,” allowing an additional test execution.

**Resolution criterion:** before EXP-V01/EXP-R02 approval, define one initial platform attempt ID and an explicit retry exception; require preservation of the failed version, platform status, stdout/stderr, outputs and access-log row before any retry; define “no metric” to include logs and partial prediction/metric files; state how the retry version is numbered and why it does not violate the single-version rule. Do not claim the account list is exhaustive. No custodian is required unless the amendment chooses to claim prevention of intentional operator omission.

### M-01 — MEDIUM — PARTIALLY CLOSED

**Evidence checked:** probe receipt, render record, amendment §6, JSON probe record, `provenance/environment/kaggle_capability.json`, DECISION-033, official Kaggle notebook specifications, and the absence of a model timing/memory probe.

Capacity is now demonstrated in part rather than merely declared: the probe output is consistent with a private GPU kernel, two visible T4s, internet access, installation of Ultralytics 8.4.52, corpus/base retrieval and output recovery. The stored quota evidence records 108,000 weekly GPU seconds with zero used at observation time.

The 12-hour CPU/GPU session limit is supported by Kaggle's official notebook documentation: <https://www.kaggle.com/docs/notebooks>. It is not established by the 30-second probe or the weekly-quota record, and v5 does not preserve a dated documentation snapshot.

The statement that 150 epochs on one T4 fit “with ample margin” is an assumption. The probe built no model, measured no epoch, AMP memory, validation/checkpoint overhead, output storage or one-T4 runtime. The CPU measurement cannot establish a GPU runtime. The repository also preserves no authenticated control-plane response for the stated kernel status/output-list/dataset-info calls; those values are transcribed into the amendment/decision records.

**Scientific consequence:** TASK-04 can start its one allowed scientific run without evidence that the frozen 150-epoch configuration completes within the platform session. A timeout then intersects N-07's incomplete failure record and creates pressure for an unplanned retry or configuration change.

**Resolution criterion:** before EXP-R01, execute an explicitly authorized non-scientific capacity probe using only train/valid (or equivalent synthetic workload) that builds the model and records fixed warm-up/excluded epochs, per-epoch train+validation time, peak allocated/reserved GPU memory, storage usage, projected 150-epoch duration under a predeclared conservative rule, and platform identifiers/status/output evidence. Discard its weights and metrics and forbid their use for selection. If no such probe is authorized, state that full-run schedulability is unproven rather than “with ample margin.”

### M-02 — MEDIUM — CLOSED for EXP-R01 scope

**Evidence checked:** amendment §5, JSON `approval_scope`, frozen §7/TASK-05 prediction requirements, and the requested snapshot in which the evaluator was not an approved reviewed artifact.

The scoping is legitimate under SPEC §11: a blocked evaluation branch need not block independent training. V5 explicitly authorizes only EXP-R01 and keeps EXP-V01/EXP-R02 blocked until `src/evaluation/evaluate.py` exists, has tests and passes independent review. This removes the v4 failure mode in which an incoherent future schema was treated as an executable approval gate.

The proposed detector record is structurally coherent: one line per image, a possibly empty detections list, one file hash in an external sidecar, and no repeated top-level `image_id`. It includes image, label and group identities and original-image post-NMS boxes.

It is not yet the complete frozen TASK-05 contract: the prose omits an explicit `split` field and transformation/preprocessing version required by frozen §7. That omission does not reopen M-02 for EXP-R01 because inference remains blocked and the evaluator/schema still requires independent review. Those fields, exact ordering/number semantics, completeness checks, local recomputation fixtures and hashes must be fixed before either inference session is approved.

### N-04 — LOW — CLOSED

Amendment §1 now states that CPU training is viable, plan-authorized and approximately 15 hours (approximately 20 hours with the prior safety factor). It cites DECISION-030 and explains that Kaggle is the user's selected/required venue under DECISION-033, not the only scientifically valid method. This resolves the prior overstatement while preserving the current user decision.

### N-05 — LOW — CLOSED at `5b5158a`

The Markdown and JSON agree on version 5, `2026-09-23T04:10:00+00:00`, `PROPOSED_V5`, probe-only execution before approval, EXP-R01-only approval scope, freeze identity, prior review counts and pending round 5. At the requested snapshot the recorded hashes match:

- job `9ae97d41044570903859740ee3ffb7500e24dea107b9f79c25f62012913dad75`;
- renderer `3f65428c5ca004acad02e495a63527616b8dbcd613bfa02b62f8fea3155e1515`;
- tests `aafbfab79ae6d1f87326a6f0be7030bca9c4d43c16e5373733a104e07513a2ca`;
- amendment Markdown `19ed18855f5643fbea314ec7f3b114e60775e7bcf43b816a0bb0cc52719f29c3`;
- round-4 report `b4b0fe70e3fa90c5cbbcac30f4401bc961956190f35d6fdc664f24318df13a6b`;
- probe receipt `f075fcb4fbaab2331ab88d363d7e0bd900a9d75445de5b2c0858029ff50b2e6b`.

The omission of the trainer hash is a missing binding under H-02, not a direct Markdown/JSON contradiction.

## New findings

### N-06 — MEDIUM — Kaggle environment evidence is weaker than the frozen environment contract

**Location:** frozen SPEC §4.3; `src/evaluation/kaggle_job.py:101-113,121,127-131,166-188`; amendment §§2–3.

**Finding:** the job records Python/platform, package versions through `pip freeze`, torch/CUDA/GPU information and `nvidia-smi` stdout. It does not record `pip check`, pip configuration/effective indexes, `pip install --report`, package/wheel origin and hashes or an explicit reason they are unavailable, platform tags, relevant environment variables, or exit/stderr for the environment probes. The installation is version-pinned but not artifact-hash-pinned. The data view, checkpoint, trainer and Ultralytics configuration/cache live under `/tmp`, while only `/kaggle/working` is retained; the amendment does not define the Kaggle replacement for the frozen workspace-containment/evidence rule.

The torch 2.10.0+cu128 versus local torch 2.12.0+cpu, CUDA 12.8, automatic mixed precision, one selected T4 despite two visible T4s, and historical `0,1` versus new `0` differences are honestly declared. They are acceptable for a **de novo** EXP-R01 and do not support a historical numerical-reproduction claim. The finding is about missing provenance, not the fact that the environment differs.

**Scientific consequence:** a completed run can identify top-level versions but cannot establish that the installed environment was internally consistent or reconstruct its package sources/builds to the degree required by frozen §4.3 and Gate E. The remote venue therefore weakens a frozen control instead of replacing it with an equivalent record.

**Resolution criterion:** retain `pip install --report`, `pip check` and exit code, effective pip configuration/index hosts with secrets redacted, full freeze, platform tags, relevant environment whitelist, package artifact hashes when reasonably obtainable (or explicit unavailability), and stdout/stderr/exit codes for probes. Define the Kaggle workspace/cache mapping and preserve the required evidence under `/kaggle/working` in the output receipt.

### N-07 — MEDIUM — Partial/error runs do not retain the promised scientific record

**Location:** amendment §6 last paragraph and §7; `src/evaluation/kaggle_job.py:121-204`; `src/evaluation/train_model1.py:104-134`; frozen TASK-04 steps/expected results.

**Finding:** `receipt.json` is written on successful completion and on one final `files_digest` mismatch. Attached-input, pip/environment, tree, individual blob, base, trainer, import and training failures bypass that write. More importantly, `epoch_records.jsonl` is held in memory and written only after `model.train(...)` returns. A 12-hour cutoff or training exception can leave candidate weight files but lose their epoch/fitness/metric linkage, selected-checkpoint reconciliation, final receipt and output hashes. The amendment's statement that a cut run is preserved and declared is therefore not implemented as a complete scientific failure record.

**Scientific consequence:** the most relevant capacity failure can produce unverifiable partial artifacts. Investigators cannot determine the last valid validation state or distinguish a permissible no-result failure from a run that exposed actionable metrics, undermining TASK-04's failure-preservation rule and H-03's retry predicate.

**Resolution criterion:** append and flush each epoch record durably from the callback; write a top-level receipt through exception/finalization handling with status, exception, completed stage, partial-output hashes and process/platform evidence; preserve stdout/stderr and exit status; and prove with a controlled mid-training exception fixture that the partial record remains reconciliable and cannot be treated as a clean retry after metrics were observed.

No new LOW finding is required. The bad `§4.4` cross-reference in amendment §6 should be corrected when H-03 is clarified, but it does not independently change the scientific decision.

## Environment judgment

The venue differences are acceptable in principle for a new run:

- Ultralytics remains 8.4.52 as frozen.
- torch/CUDA/backend, AMP and device-count differences are declared before EXP-R01.
- only device `0` is requested, so the run does not claim to reproduce the historical two-device setting.
- historical numerical agreement is expressly disallowed as evidence.

Acceptance of those declared differences does not waive N-06's provenance requirements. EXP-R01 should be described as a de novo retraining under the amended Kaggle environment, never an exact historical reproduction.

## Final decision and counts

PROTOCOL-AMENDMENT-008 version 5 **may not move to `APPROVED` for EXP-R01 training** at the reviewed snapshot.

- Open HIGH findings: **2** — H-02 and H-03.
- Open MEDIUM findings: **3** — M-01, N-06 and N-07.
- Direct EXP-R01 blockers: **HIGH 1** (H-02), **MEDIUM 3** (M-01, N-06, N-07).
- Inference-only open HIGH: **H-03**; EXP-V01 and EXP-R02 remain blocked independently.
- Closed prior MEDIUM for the training scope: **M-02**.
- Closed prior LOW findings: **N-04 and N-05**.

Even after this amendment is remediated, EXP-R01 remains separately subject to the frozen TASK-03 precondition: the final `model1_clean_manifest.csv` and its review must exist. At the requested snapshot only draft-A/draft-B manifests existed.
