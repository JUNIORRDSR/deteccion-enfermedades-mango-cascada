# Independent adversarial review — PROTOCOL-AMENDMENT-008

- **Reviewed range:** `675c49c..4b198bd`
- **Main artifact:** `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.md`
- **Review posture:** hostile reproducibility and research-integrity review. No Kaggle experiment was run as part of this review.

## Verdict

**PROTOCOL-AMENDMENT-008 may not move from `PROPOSED` to `APPROVED`.** The proposed reading of the frozen capacity clause is legitimate, the freeze itself was not modified, and the reviewed range contains no evidence of a Kaggle experimental run. Those points do not cure the open controls below.

Open findings: **HIGH 6, MEDIUM 3, LOW 0**.

## Controlling determinations

### The frozen clause does not impose a permanent Kaggle ban

The text supports the amendment's narrow legal reading. The frozen SPEC requires real hardware, time, and budget to be recorded before execution and says that absent capacity leaves training blocked (`provenance/protocol_freeze.md:136`). The frozen plan says that if capacity is unavailable TASK-04 must record a block and must not invent Kaggle hardware (`provenance/protocol_freeze.md:289`; source plan `docs/superpowers/plans/2026-09-17-albus26-major-revision.md:76`). TASK-04 itself permits GPU use if the difference is recorded and forbids claiming a 2×T4 replica (`provenance/protocol_freeze.md:434-445`; source plan `:221-232`). None of those passages forbids later use of measured, authorized external capacity.

The user authorization satisfies the stop condition for an external action (`provenance/authorizations/2026-09-21-kaggle-compute-authorization.md:5-10,22`). Therefore, using Kaggle after a valid amendment is not, by itself, motivated reasoning. The motivated step is narrower: the amendment treats a quota response as if it proves an executable GPU configuration and leans on an unverified historical T4 claim. Findings H-06 and M-01 address those overstatements.

### The freeze is intact and `PROPOSED` has been honored in the reviewed range

The reviewed commit adds only the authorization, capability record, and proposed amendment. Neither freeze file, the SPEC, nor the plan changes in `675c49c..4b198bd`. The current freeze blobs equal the blobs in freeze commit `7d0f9985cce73740cfa2ae26154971b55282ad52`; current SHA-256 values are `6d5aa3ff47cba97f8ecd0dd15683bb96f0d53146f3af1ce1e95bf24cec7cbc8b` for the JSON and `1a41b1aa684e26e5853aae31369c5200b29ae25a70bc383e3f0bd3ef136058be` for the Markdown.

The range contains no notebook, Kaggle dataset version, kernel/run identifier, `EXP-R01` output, downloaded base checkpoint, or GPU result. The quota probe is capability observation, not an experimental run. `has_ever_run=true` in `provenance/environment/kaggle_capability.json:11` is account-level history and is not evidence that this protocol ran. On the repository evidence reviewed, the `PROPOSED` state at amendment line 5 was honored.

## Findings

### H-01 — HIGH — The material-amendment record is incomplete under the freeze's own procedure

**Location:** `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.md:3-6,66-68`; `provenance/protocol_freeze.md:84-90,203,246`; `provenance/test_access_log.csv:2`.

The freeze requires an append-only amendment to record a timestamp, prior protocol hash/ID, the change, compelling evidence, whether test was observed and the applicable accesses, potential impact, decision, and independent reviewer. A material change after test exposure also requires the user decision; every run must link the freeze and applicable amendments. Amendment-008 links the protocol and authorization and describes risks, but it has no exact timestamp with timezone, no explicit `test_observed_before_freeze=true` or amendment-era access statement, no decision ID, no reviewer/report identity or hash, and no machine-readable amendment companion. The only test-access row is the pre-freeze historical entry. The absence of a reviewer is expected while the document is `PROPOSED`; it is not acceptable at approval.

**Scientific consequence:** an approved run would not have a complete, auditable chain identifying the effective protocol after known historical test exposure. A later reader could not distinguish “no new access” from an omitted access record or identify the review that authorized the change.

**Resolution criterion:** before approval, create the complete append-only amendment record required by `protocol_freeze.md:90`: exact timestamp/timezone; base protocol ID, commit, and SHA-256; explicit prior test exposure and any new accesses (or an explicit zero-new-access statement linked to the log); material-impact statement; user decision ID/link; independent reviewer and this report's hash; open-finding counts; and an `APPROVED` decision only after all HIGH/MEDIUM findings close. Add the machine-readable sidecar expected by `PROTOCOL-AMENDMENT-XXX.{md,json}` and require each Kaggle/local run record to cite both the freeze and Amendment-008.

### H-02 — HIGH — “Separate payloads plus no test IDs” does not make the training notebook test-inaccessible

**Location:** `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.md:41,44,51`; frozen test rule `provenance/protocol_freeze.md:124-132`; frozen plan `docs/superpowers/plans/2026-09-17-albus26-major-revision.md:16,251,276-277`.

The amendment does not pin Kaggle dataset handles and version numbers, enumerate every mounted input, or require a clean kernel/cache. A “separate” upload can still be one private dataset version containing train, validation, and test, or the training notebook can have both datasets attached. An `image_id` anti-join does not detect a renamed test image, an exact-content duplicate under another ID, a label leak, a group/sequence-equivalent image, or undeclared files in the read-only mount. Kaggle's official client documentation says notebook resources are attached as inputs and served from a shared resource cache, and its API accepts versioned handles; the amendment specifies neither version pinning nor cache/input closure ([Kaggle `kagglehub`](https://github.com/Kaggle/kagglehub), [`datasets.py`](https://github.com/Kaggle/kagglehub/blob/main/src/kagglehub/datasets.py)).

Ultralytics 8.4.52 also resolves `path` and each `train`, `val`, and `test` entry from the YAML, including a `../` fallback (`.venv/Lib/site-packages/ultralytics/data/utils.py:503-517`). The amendment has no generated train-only YAML, resolved-path allowlist, or assertion that all resolved paths remain inside the approved training mount.

**Scientific consequence:** test pixels, labels, or test-related duplicates can be available to training, checkpoint selection, callbacks, or manual inspection even if the declared training IDs pass. The final test is then not isolated under the frozen rule, and all dependent M1 numbers fail Gate E.

**Resolution criterion:** define immutable, version-pinned Kaggle inputs per phase. The training input may contain only M1 train/validation files, the preverified base checkpoint, and a generated YAML with no test entry; the test input must not be attached until the frozen operating-point artifact exists. At notebook start, fail closed after recording the complete `/kaggle/input`, working-directory, and relevant cache inventory; verify every allowed file by relative path, byte hash, label hash, `image_id`, `group_id`, and split; reject undeclared files, test hashes/groups, path escape, extra mounts, and stale cache/output inputs. Resolve the YAML with the installed Ultralytics code and assert every resolved path is inside the allowlisted mount before importing or training the model.

### H-03 — HIGH — The same operator can still use test feedback to alter thresholds, runs, or attempt selection

**Location:** `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.md:51,54,58`; `provenance/protocol_freeze.md:132,138-140`; frozen plan `docs/superpowers/plans/2026-09-17-albus26-major-revision.md:229-233,273,276-279`; `provenance/test_access_log.csv:2`.

“Evaluate once after freezing” is a declaration, not an enforcement mechanism. The amendment does not prevent the operator from inspecting test outputs, editing and re-running the validation-threshold step, changing a config, selecting another successful notebook version, aborting an unattractive run, or treating only a preferred attempt as the official one. Its retry rule covers quota interruption, not manual cancellation, numerical failure, a completed but unfavorable run, or a test-driven change. The project also begins with acknowledged historical test exposure, which raises rather than lowers the need for a one-way audit trail.

**Scientific consequence:** the reported operating point, checkpoint, or run can be selected with knowledge of test behavior while still appearing to follow the validation-only rule. This creates undisclosed researcher degrees of freedom and invalidates the intended validation/test separation.

**Resolution criterion:** before attaching test data, freeze and timestamp the notebook/code hash, checkpoint hash, dataset versions, validation-prediction hash, selected threshold, complete evaluation config, environment, and permitted command in a write-once local record reviewed by a different person. Run test non-interactively with no selection options. Preserve every Kaggle kernel version, attempt, cancellation, failure, stdout/stderr, exit code, and output identifier. Define technical retry criteria before launch and forbid retries based on any metric. Log every test-output access. Test outputs may update reporting only; any later selection change must trigger the frozen material-change stop rule, not a silent re-run.

### H-04 — HIGH — The base checkpoint and Kaggle environment are not closed inputs, and `ART-005` is already occupied

**Location:** `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.md:49-53`; frozen environment and TASK-04 rules `docs/superpowers/plans/2026-09-17-albus26-major-revision.md:39,217,221,229-232`; `provenance/artifact_registry.csv:6`.

The amendment enables internet during training to fetch an unspecified “official” checkpoint. It gives no exact URL, publisher record, expected hash, license, download response, or pre-run identity. Downloading inside the training session also leaves an open input channel when the test-isolation claim depends on input closure. Line 53 says that checkpoint will become `ART-005`, but `ART-005` already identifies the historical `args.yaml` in the artifact registry. The proposed record would create two incompatible identities for one artifact ID.

The environment treatment is also asymmetric: line 50 says Kaggle fixes its own torch/CUDA stack, but requires another amendment only if Ultralytics 8.4.52 cannot be installed. A different torch, torchvision, CUDA, cuDNN, base image, or wheel build is equally capable of changing optimization and inference. Recording effective versions after execution does not preauthorize a departure from the frozen environment rule.

**Scientific consequence:** the starting weights, software stack, or artifact identity could differ without a valid pre-run decision. Results would not be reconstructible and could be attached to the wrong provenance record.

**Resolution criterion:** acquire the base checkpoint before the scientific run through a separately logged step; record exact source URL, publisher/model version, license, response metadata, size, and SHA-256; assign an unused ART ID; place the verified bytes in an immutable version-pinned input; and disable network for training and inference. Freeze the Kaggle image/environment identity, Python, all direct and transitive packages, wheel/build hashes, torch/torchvision/CUDA/cuDNN, Ultralytics settings, driver, and accelerator topology. Preserve install report and `pip check`. Any incompatibility or substitution must be reviewed and approved before the run.

### H-05 — HIGH — File-level permission, attribution, privacy, and egress minimization are not established

**Location:** `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.md:41-45`; authorization `provenance/authorizations/2026-09-21-kaggle-compute-authorization.md:13-18`; `docs/research/claim_evidence_matrix.csv:9,11`; `reports/datasets/dataset_archaeology.md:28`; manifest contract `provenance/protocol_freeze.md:128` and M2 plan `docs/superpowers/plans/2026-09-17-albus26-major-revision.md:200`.

CC BY 4.0 permits reproduction and sharing of material to which the licensor validly applied the license, subject to attribution and related conditions. It does not certify that a dataset publisher owned every source image, and it does not grant third-party privacy/publicity rights. The project's own evidence says the DATA-001 license/origin claim is only partially supported and that a dataset-level license does not certify rights in source images; DATA-004/005 provenance remains unresolved between records/mirrors. The local archaeology explicitly says external licenses and origin were not verified.

The promise to put attribution “in dataset metadata” does not specify creator, copyright notice, license link, source URI, disclaimer, or modification notice required when supplied by the licensor ([CC BY 4.0 legal code, sections 2-3](https://creativecommons.org/licenses/by/4.0/legalcode)). Private status reduces public exposure but does not prove permission for the exact bytes or remove privacy obligations.

The upload boundary is also too broad. TASK-05 needs M1 phase-specific inputs and the frozen M2 test view, not every representation of DATA-004/005. The frozen manifests contain `local_absolute_path`; uploading them unchanged would disclose local path/user information despite the authorization's prohibition on personal data. No EXIF/metadata inspection or sanitized Kaggle manifest is required.

**Scientific consequence:** the project may transfer files it cannot prove are licensed for this use, fail attribution, disclose local or embedded metadata, or upload more data than the authorized computation needs. That is both an integrity problem and a breach of the stated egress boundary.

**Resolution criterion:** produce a file-level egress manifest tied to exact dataset versions and source records, with documented license coverage/rightsholder, creator/attribution party, source URL, license URL, notices, and modifications for every payload family. Resolve the DATA-001 coverage and DATA-004/005 identity gaps before upload. Upload only files required for each run: M1 train/validation for training, M1 test only for final M1 evaluation, and the frozen DATA-005 test inputs required for M2 inference; justify any DATA-004 bytes separately. Use a sanitized relative-path/hash manifest with no absolute paths or credentials, inspect/remove unnecessary EXIF and other metadata, record Kaggle privacy/version settings, and verify the final uploaded file list against the allowlist.

### H-06 — HIGH — `RECONSTRUCTED` does not cure the unsupported suggestion of a historical 2×T4 relationship

**Location:** `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.md:15,19,49`; `provenance/environment/kaggle_capability.json:20`; `provenance/experiment_registry.csv:2`; `docs/research/claim_evidence_matrix.csv:17`.

The amendment labels the historical 2×T4 statement `OBSERVED` and says the Kaggle accelerator family matches it. The registry says only `device=0,1` is supported by metadata; “2 x NVIDIA T4 / Kaggle” is a manuscript claim with no hardware log and is `UNVERIFIED`. The quota probe explicitly says it does not guarantee any accelerator shape. No new device has yet been scheduled. Even a future T4 would not establish equivalence of accelerator count, distributed-training semantics, base checkpoint, dataset membership, split, Python, torch, CUDA/cuDNN, Ultralytics, optimizer resolution, or driver.

**Scientific consequence:** readers can reasonably infer a closer replication of EXP-001 than the evidence permits and treat agreement/disagreement as a replication result rather than a new reconstructed experiment.

**Resolution criterion:** remove the current T4-match claim and change the historical row to “claimed/unverified.” Describe EXP-R01 as a de novo reconstructed run under a revised protocol, not a reproduction of the historical 2×T4 run. After execution, report the actual GPU name/count and a full historical-versus-new difference table. Do not use numerical agreement as evidence of historical reproducibility or numerical disagreement as evidence of model instability without controlling those differences.

### M-01 — MEDIUM — The quota response does not yet establish schedulable capacity for TASK-04

**Location:** `provenance/environment/kaggle_capability.json:2-20`; `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.md:14,17,54,62`.

The evidence shows an account quota balance on a date, not a timestamped allocation with GPU model/count, memory, availability, session limit, or successful environment preflight. The quota refreshes on 2026-09-26, so it is not durable capacity evidence. Comparing 30 hours with the historical 21-minute report assumes the unverified historical hardware and a comparable run; neither is established.

**Scientific consequence:** TASK-04 may be declared unblocked even though the specified model, batch, environment, or full run cannot be scheduled or completed. Mid-run failures can then create discretionary retries.

**Resolution criterion:** keep capacity status conditional until a timestamped, non-test preflight records actual GPU name/count, memory, driver/runtime, session/quota limits, available storage, and successful loading of the frozen environment and base checkpoint. Estimate resource need from the approved configuration without using test data. Re-probe quota immediately before launch and preserve the response and tool/version identity.

### M-02 — MEDIUM — GPU inference and local statistics are compatible only with a stronger prediction-transfer contract

**Location:** `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.md:26-27,36,52`; `provenance/protocol_freeze.md:140,151-153`; frozen TASK-05 `docs/superpowers/plans/2026-09-17-albus26-major-revision.md:273,276-278,284-291`.

There is no inherent scientific inconsistency in running validation/test inference on the same frozen GPU backend and calculating Wilson/bootstrap statistics locally. The predictions, not the processor used for arithmetic, are the experimental bridge. The amendment, however, only says outputs will be downloaded and hashed. It does not make approval conditional on a complete prediction schema, full-precision scores/boxes/probabilities, score-floor and NMS state, exact row coverage, deterministic tie/order handling, or a single authoritative source for AP and operating-point metrics.

**Scientific consequence:** local code could calculate statistics from rounded, filtered, reordered, or incomplete predictions and publish numbers that do not correspond to the validation threshold or final GPU test inference.

**Resolution criterion:** define and test the transfer contract before inference: prediction schema and numeric precision; pre/post-NMS status; score floor; class map; image/label/group IDs and hashes; checkpoint/config/manifest/environment hashes; total-row and per-image coverage; serialization version; and metric-code commit. Hash the GPU predictions before transfer, verify the same bytes locally, and derive all local statistics from those bytes without re-inference. Reconcile local metrics with the GPU run or explain any evaluator difference before manuscript use.

### M-03 — MEDIUM — The local CPU is in fact a Ryzen 5 7520U, but the cited hardware record does not prove it

**Location:** `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.md:35`; `provenance/environment/hardware.json:4-7`; `reports/reviewer_matrix.csv:8-9`; frozen benchmark rule `provenance/protocol_freeze.md:155-161`.

Keeping the CPU benchmark local is scientifically correct: REVIEW-07 concerns the Windows/Ryzen latency claim, while REVIEW-08 requires a physical Raspberry Pi and remains blocked. The amendment nevertheless cites `hardware.json` for the statement that the local CPU belongs to the Ryzen 5 7520U family. That file records only `AMD64 Family 23 Model 160`, eight logical CPUs, RAM, and generic Radeon graphics; it does not record the processor marketing name.

A fresh read-only registry probe during this review returned `ProcessorNameString = AMD Ryzen 5 7520U with Radeon Graphics`, so the factual identification is correct on the current host. The problem is evidentiary: the amendment presents an inference as if its cited durable artifact proves it. The current registry observation is in this report, not in the environment record tied to the future benchmark.

**Scientific consequence:** without a run-linked exact identity, a later benchmark could be attributed to the historical processor model based on an ambiguous hardware record. The result would not be reproducible even if the current machine happens to match.

**Resolution criterion:** before TASK-06, capture the exact processor name, manufacturer/model, physical and logical cores, OS/build, power plan, thread controls, thermal/power state, runtime versions, and the command/raw output with timestamp in the benchmark environment record. Report the new measurement as a fresh Ryzen 5 7520U benchmark, not as recovery of the historical 145 ms. Keep the Raspberry Pi result `BLOCKED_BY_HARDWARE` until measured on a physical Pi 4.

## Minimum package a referee would require before accepting GPU-run numbers

Approval of the amendment is not approval of future numbers. Before any GPU result enters the manuscript, the evidence package must include:

1. the closed Amendment-008 record and decision described in H-01;
2. immutable Kaggle dataset handles **with version numbers**, file manifests/hashes, attribution, privacy scan, and per-phase input allowlists;
3. the exact notebook/script bytes and commit, Kaggle kernel version/run ID, noninteractive command, network setting, mounted-input/cache inventory, and every attempt/failure;
4. an unused artifact ID and full provenance for the base checkpoint, plus a network-disabled scientific run;
5. a frozen environment and actual accelerator identity/topology captured before training, with package/build hashes and `pip check`;
6. pre-test hashes for the validation predictions, checkpoint, selected threshold, evaluation config, manifests, and code, followed by a one-way test execution and complete access log;
7. full-precision per-image predictions and the verified transfer/recalculation package in M-02;
8. a run report that calls EXP-R01 reconstructed/de novo, lists every difference from EXP-001, preserves unfavorable results, and makes no claim of exact or near historical reproduction; and
9. the exact local CPU benchmark identity and a separately blocked Raspberry Pi statement.

## Final decision

The reinterpretation of “do not invent Kaggle hardware” is textually legitimate, but the present amendment does not yet make Kaggle training or test evaluation acceptably isolated, licensed, or reproducible. **Do not approve PROTOCOL-AMENDMENT-008 and do not execute on Kaggle.** Remaining open findings: **6 HIGH and 3 MEDIUM**.
