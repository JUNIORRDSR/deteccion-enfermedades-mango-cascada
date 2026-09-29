# Independent adversarial re-review — PROTOCOL-AMENDMENT-008 version 2

- **Reviewed remediation range:** `4b198bd..f70bb2a`
- **Reviewed HEAD:** `f70bb2ae19a51d45f2acd9cae9ef070427a2bd86`
- **Artifacts:** `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.{md,json}`
- **Prior findings under test:** H-01–H-06 and M-01–M-03 from `reports/amendments/amendment-008-independent-review.md`
- **Posture:** the author response was treated as a claim to falsify. No Kaggle upload, notebook execution, model inference, or training was performed by this review.

## Verdict

**DO NOT APPROVE. PROTOCOL-AMENDMENT-008 may not move from `PROPOSED_V2` to `APPROVED`.** Version 2 makes material progress, and H-04 is closed, but the load-bearing isolation, evidence-custody, egress, historical-venue, capacity, prediction-transfer, and CPU-topology controls are not all closed.

`PARTIALLY CLOSED` counts as open for approval. Unique remaining blockers: **HIGH 5, MEDIUM 4**. N-01 is the new evidentiary overreach that keeps H-06 open and is not counted twice.

| Finding | Severity | Re-review status |
|---|---:|---|
| H-01 formal amendment record | HIGH | **PARTIALLY CLOSED** |
| H-02 test-inaccessible training input | HIGH | **PARTIALLY CLOSED** |
| H-03 one-way test discipline | HIGH | **PARTIALLY CLOSED** |
| H-04 checkpoint, network, environment, artifact ID | HIGH | **CLOSED** |
| H-05 permission, privacy, and egress | HIGH | **PARTIALLY CLOSED** |
| H-06 historical-run identity | HIGH | **PARTIALLY CLOSED** |
| M-01 schedulable capacity | MEDIUM | **PARTIALLY CLOSED** |
| M-02 prediction transfer | MEDIUM | **PARTIALLY CLOSED** |
| M-03 CPU identity | MEDIUM | **PARTIALLY CLOSED** |

## Controlling checks

### Frozen authority remains intact

Fresh SHA-256 values are:

- `provenance/protocol_freeze.json`: `6d5aa3ff47cba97f8ecd0dd15683bb96f0d53146f3af1ce1e95bf24cec7cbc8b`
- `provenance/protocol_freeze.md`: `1a41b1aa684e26e5853aae31369c5200b29ae25a70bc383e3f0bd3ef136058be`

Both files are byte-identical to commit `7d0f9985cce73740cfa2ae26154971b55282ad52`, and neither changes in `4b198bd..f70bb2a`. The SPEC and plan still require truthful blocking, complete environment/run evidence, one test evaluation after validation decisions are frozen, and zero open HIGH/MEDIUM findings before approval.

### The EXP-001 dataset field does not prove execution venue

I independently read the EXP-001 row in `provenance/experiment_registry.csv`. Its `dataset` field is exactly:

> `mangoUnhealty v2 via Kaggle /kaggle/input/datasets/jairoall/mangodataset/data.yaml; local SemilleroTI-Mangos/docs/MangosDataset`

The Kaggle-shaped path is also embedded in the statically decoded checkpoint `train_args` (`reports/experiments/checkpoint_static_metadata.json:15060-15074`) and its pickle opcode transcript (`reports/experiments/SemilleroTI-Mangos_best_pickle_opcodes.txt:72531-72534`). Another embedded string names `/kaggle/working/runs/detect/train-2`. This is genuine evidence that the saved configuration was shaped for Kaggle. It is **not proof that training executed there**:

- EXP-001 itself says the training notebook/script, execution commit, historical manifest, exact invocation, Python, PyTorch, CUDA, and hardware log are unverified.
- `reports/experiments/experiment_archaeology.md:35` says the original notebook/script was not found.
- The same report warns at line 68 that a path stored in code does not prove the same bytes were used in a historical execution.
- A checkpoint/config dictionary can be copied, reused, or edited; no authenticated Kaggle kernel ID/version, dataset version, platform log, or host record binds these strings to an actual run.

The defensible classification is **consistent with / suggestive of Kaggle, venue unverified**, not `OBSERVED`. Version 2 therefore overreaches in the opposite direction from the original 2×T4 error.

### 2×T4 treatment

Within the amendment Markdown and JSON sidecar, the concrete `2 × NVIDIA T4` statement is now correctly marked claimed/unverified, `device=0,1` is separated as saved metadata, accelerator-family matching is withdrawn, and EXP-R01 is called de novo. `provenance/experiment_registry.csv` also says `claimed by PDF, hardware log UNVERIFIED`. Archival manuscript/genealogy transcriptions still contain the original claim by design; they are historical sources, not validated assertions. `docs/research/claim_evidence_matrix.csv:17` remains a compound `PARTIALLY_SUPPORTED` row and should not be read as verification of the T4 component.

### Markdown/JSON consistency

The sidecar's `document.sha256` is correct: the current Markdown hashes to `415106148ceae9c41d603c28bfec399031d2e245dd5038a11b81313c733472a9`. The sidecar and Markdown agree on the protocol hashes, timestamp, state, prior test exposure, no new test access, DECISION-028, prior review/hash/counts, ART-106, conditional capacity, historical-venue claim, 2×T4 status, and prohibition on execution. No substantive field contradiction was found. Cosmetic differences are the unaccented JSON title and numeric `physical_cores` in the sidecar versus a string in `hardware.json`.

This agreement does not make the shared claims correct. Both artifacts promote the historical venue to `OBSERVED`, and both claim the nine findings are closed before the required fresh review; see N-01 and N-02.

### Kaggle execution/upload evidence

There is still **zero repository evidence of an Amendment-008 Kaggle upload or execution**: the remediation range contains no notebook, immutable dataset-version record, Kaggle kernel/run/output ID, uploaded-file receipt, EXP-R01/EXP-V01/EXP-R02/EXP-R03 directory, checkpoint acquisition, predictions, GPU log, or run output. The `experiments/` directory is absent. `kaggle_capability.json` is an account quota probe; `has_ever_run=true` is account history, not evidence for this protocol.

The broader statement “zero evidence of any Kaggle execution anywhere” is too absolute. Historical saved metadata contains Kaggle-shaped input/output paths and is circumstantial evidence for EXP-001, but it is not sufficient to establish the venue as observed. There is no evidence of a new upload or run under Amendment-008.

## Re-review of prior findings

### H-01 — HIGH — PARTIALLY CLOSED

**Evidence checked:** amendment Markdown lines 5-26; complete JSON sidecar; `provenance/test_access_log.csv`; current hashes of the freeze, authorization, V1 review, and amendment Markdown.

Version 2 adds the timestamp/timezone, base protocol identity and hashes, material impact, inherited test exposure, explicit zero-new-access statement, DECISION-028, V1 reviewer/report/hash/counts, machine-readable sidecar, and mandatory run citations. All referenced hashes checked out, including the sidecar's Markdown hash. The test log really contains only TEST-ACCESS-001 and TEST-ACCESS-002.

It is not fully closed for approval because the record contains only the rejected V1 review. It does not yet identify the V2 reviewer, this re-review, its hash, or the resulting open counts. That omission is proper while the state remains `PROPOSED_V2`, but it means the current bytes are not yet a complete approval record. In addition, the sidecar field `findings_closed_in_v2` asserts closure before review (N-02).

**Closure criterion:** retain `PROPOSED_V2` until all blockers are resolved; then record the fresh V2 reviewer, report path/hash, actual finding counts, and final decision without weakening the append-only evidence chain.

### H-02 — HIGH — PARTIALLY CLOSED

**Evidence checked:** amendment Markdown lines 63-73 and 141-147; JSON closure claim; pinned Ultralytics 8.4.52 resolver at `.venv/Lib/site-packages/ultralytics/data/utils.py:503-536`; current official KaggleHub documentation.

The versioned per-phase inputs, train/validation-only payload, test attached only later, byte/label/image/group/split checks, extra-mount rejection, and generated YAML without `test` are real improvements. Kaggle supports explicit dataset handles such as `owner/slug/versions/N`; its official documentation also says notebook resources are automatically attached and served from a shared resources cache ([KaggleHub](https://github.com/Kaggle/kagglehub#readme)).

The mechanism is still not closed enough to audit:

- `relevant caches` is operator-defined. No exhaustive cache/root list, clean-kernel requirement, or immutable pre-upload allowlist schema is named, despite Kaggle's shared resource cache.
- `owner/slug + version` is prose, not a required captured attached-resource identity/receipt. An operator can record a version while attaching or reading another unless the kernel's effective inputs are independently reconciled.
- The path assertion does not specify canonical/symlink treatment or nested path-bearing files such as image-list text files.
- Calling the installed Ultralytics dataset resolver is not side-effect-free by default. The pinned code can process the YAML `download` field and execute an HTTP download, shell command, or Python snippet after path resolution if files are missing. Version 2 does not explicitly reject `download`, set `autodownload=False`, or require the containment check to occur before any such action.
- No runnable validator, expected inventory schema, or negative fixture is required before the scientific run. “Fail closed” therefore still depends on later implementation choices.

An operator can still choose which caches are “relevant,” omit a path-bearing indirection, or let the resolver act before the assertion. That is a declaration with useful detail, not yet a complete fail-closed mechanism.

**Closure criterion:** freeze a concrete input/inventory schema and validator before upload; enumerate every inspected root/cache; require a fresh kernel; capture the effective attached resource IDs and versions; canonicalize and reject symlink/nested-list escapes; reject YAML `download` and disable autodownload; and preserve passing and failing validator output before any Ultralytics import or run.

### H-03 — HIGH — PARTIALLY CLOSED

**Evidence checked:** amendment Markdown lines 75-86 and 141-147; frozen SPEC test rule; frozen TASK-05 one-test procedure; JSON `execution_permitted=false`.

Version 2 now freezes hashes/config/threshold before attaching test, requires a noninteractive test run, preserves attempts/cancellations/failures, limits retries to technical causes fixed before launch, logs output access, and forbids metric-driven retries. Those are meaningful controls.

The custody problem remains. The “write-once local record” is not defined as append-only storage, an immutable service object, or a Git object reviewed before test attachment. The same operator may select the threshold, create the purported write-once record, attach the test, decide whether a cancellation was a technical failure, and preserve the evidence. No different person is required to verify the pre-test bundle before test access, and no independently obtained Kaggle version history/account audit is required to prove that all shadow runs, cancellations, deletions, and accesses were retained. “Error de carga” is also broad enough to permit discretionary retry classification.

Thus the text reduces researcher degrees of freedom but does not make the trail one-way against the person who controls it. This directly fails the prior resolution criterion requiring pre-test review by a different person.

**Closure criterion:** require a separately identified reviewer/custodian to verify and hash the pre-test bundle before the test resource is attached; define the immutable storage primitive and exact technical retry taxonomy; reconcile all account-visible Kaggle kernel versions/attempts/output IDs against the local log; and make any missing or deleted attempt a failed Gate E.

### H-04 — HIGH — CLOSED

**Evidence checked:** all artifact IDs in `provenance/artifact_registry.csv`; range diff of that registry; amendment Markdown lines 108-121; `hardware.json`; `runtime_path_report.json`; pinned Ultralytics `is_online()` implementation.

ART-106 is genuinely free: the registry has 105 rows ending at ART-105. ART-005 remains the historical EXP-001 `args.yaml`, and its row is untouched in `4b198bd..f70bb2a`.

The base checkpoint is now acquired in a separate logged step, assigned ART-106 only on acquisition, hashed and placed in a version-pinned immutable input. Network is disabled during training and inference. That is workable with pinned Ultralytics: `is_online()` runs at import, returns immediately when `YOLO_OFFLINE=true`, catches DNS `OSError`, and ultimately returns false rather than aborting import (`ultralytics/utils/__init__.py:808-821,946`). The local runtime report proves the import-time probe exists, although it measured `ONLINE=true` in the local online environment rather than performing an offline import. The amendment describes this limitation honestly. Recording `YOLO_OFFLINE=true` in the future run would make the intent unambiguous, but it is not necessary to keep H-04 open if platform egress is actually disabled and verified.

The environment rule is now symmetric across Ultralytics, torch, torchvision, CUDA, cuDNN, image, wheel/build, driver, settings, and accelerator topology. Any substitution requires pre-run review instead of post-hoc documentation. This closes the prior asymmetry.

### H-05 — HIGH — PARTIALLY CLOSED

**Evidence checked:** amendment Markdown lines 88-96 and 137; JSON blocking prerequisites; `docs/research/claim_evidence_matrix.csv:9`; `reports/datasets/dataset_archaeology.md`; authorization egress conditions.

The prerequisite is strong, not advisory: “No se sube nada mientras eso siga abierto.” Because DATA-001 license coverage remains `PARTIALLY_SUPPORTED` and DATA-004/005 identity/provenance remains unresolved, **the current amendment does not authorize any upload yet**. That is the correct current state.

The future privacy boundary is incomplete. The sanitized manifest removes absolute paths and credentials but retains relative paths, which normally retain original filenames. Version 2 does not require filename pseudonymization or inspection for identifiers embedded in filenames. It requires removal of “unnecessary” EXIF and other embedded metadata, not a fail-closed rule for every identifying metadata field. It also does not expressly cover identifiers in archive member names, YAML/comments, labels, sidecars, or visually embedded personal information.

**Closure criterion:** keep the upload block; after rights are resolved, require a payload-wide privacy transformation/scan with opaque filenames, sanitized archive members and text sidecars, explicit EXIF/IPTC/XMP removal or justified allowlist, visual-personal-data review where applicable, and a byte-for-byte uploaded-file receipt reconciled to the sanitized allowlist.

### H-06 — HIGH — PARTIALLY CLOSED

**Evidence checked:** EXP-001 registry fields; decoded checkpoint metadata/opcodes; experiment archaeology; amendment Markdown lines 28-41 and 98-104; JSON `historical_venue` and `historical_accelerator`; active decision log and claim matrix.

The original defect is repaired: 2×T4 is claimed/unverified, accelerator matching is withdrawn, and EXP-R01 is de novo. However, V2 introduces N-01: it labels the historical Kaggle venue `OBSERVED` and says Kaggle was the original site based on a path in saved configuration. As established above, that evidence is consistent with Kaggle but cannot exclude copied/edited/reused configuration or execution elsewhere. The same overstatement appears in the author response and `docs/research/decision_log.md:64`.

**Closure criterion:** change all active statements to “Kaggle-shaped paths are embedded in saved args/checkpoint; historical execution venue remains unverified.” Promote venue to observed only with authenticated Kaggle notebook/kernel version, dataset attachment/version, execution log, or equivalent independent platform evidence.

### M-01 — MEDIUM — PARTIALLY CLOSED

**Evidence checked:** `kaggle_capability.json`; amendment Markdown lines 123-125 and 137; JSON capacity/blocking fields; repository search for the retracted comparison.

Capacity is now genuinely conditional. The quota response is explicitly non-durable; TASK-04 remains blocked pending a non-test preflight that records real GPU, memory, driver/runtime, session limit, storage, frozen-environment load, checkpoint load, and a fresh quota probe. The “30 h versus 21 min” argument is no longer used. It survives only in statements that explicitly retract it; `kaggle_capability.json` still truthfully reports the 30-hour account balance by itself.

The prior closure criterion also required a resource-need estimate from the approved configuration without test data. V2 omits that. Merely loading the environment/checkpoint and recording a session limit does not show that 150 epochs at the approved batch/image size can finish within that limit. That residual uncertainty is precisely what can create discretionary mid-run retries.

**Closure criterion:** add a predeclared, non-test resource/throughput estimate and a pass/fail capacity rule tying the approved 150-epoch configuration to the measured session/quota limits before TASK-04 is unblocked.

### M-02 — MEDIUM — PARTIALLY CLOSED

**Evidence checked:** amendment Markdown lines 127-129 and 141-143; frozen TASK-05 prediction requirements.

The amendment now names the main transfer dimensions: precision, NMS state, score floor, class map, image/label/group IDs and hashes, checkpoint/config/manifest/environment hashes, coverage, deterministic order/ties, serialization, metric-code commit, Kaggle hash, local byte verification, and no re-inference. This is substantially stronger.

It still says that a schema will be fixed later rather than specifying the schema or requiring an executable validator/test. It does not define box coordinate representation/units, numeric dtype and NaN/Inf handling, whether pre- or post-NMS predictions are authoritative, the required probability/vector content, or exact duplicate/missing-image failure behavior. Most importantly, “a single authoritative source” is not selected before inference, and evaluator differences may be “reconciled or explained” after seeing results. That leaves room to choose an evaluator after a discrepancy is observed.

**Closure criterion:** freeze the exact serialized schema and one authoritative evaluator before inference; define coordinates, dtypes, non-finite handling, score/probability content, uniqueness/completeness failures, and metric tolerances; require a validator fixture and fail Gate E on any unreconciled byte/schema/metric mismatch.

### M-03 — MEDIUM — PARTIALLY CLOSED

**Evidence checked:** `provenance/environment/hardware.json:18-27`; its remediation diff; fresh read-only registry probe; logical-processor registry entries; prior resolution criterion.

The recorded command reproduces `AMD Ryzen 5 7520U with Radeon Graphics`, and the processor-name evidence is now durable. The registry exposes eight logical processor entries, consistent with `cpu_count=8` and `logical_cores=8`. Keeping TASK-06 local and treating it as a fresh measurement is correct.

The same recorded probe reads only `ProcessorNameString`; it does not produce `physical_cores=4`. No command/raw output/source is preserved for that physical-core count. A fresh CIM topology probe in this review was unavailable due access denial, so the four-core value remains plausible and hardware-consistent, but not reproduced from the cited probe. The environment record also does not yet include the power plan, thread controls, or thermal/power state required by the prior criterion for the future benchmark.

**Closure criterion:** before TASK-06, preserve a successful topology probe and raw output for physical/logical cores, plus the run-linked OS/build, power plan, thread controls, thermal/power state, and runtime versions. Keep the measurement fresh and Raspberry Pi `BLOCKED_BY_HARDWARE`.

## New findings

### N-01 — HIGH — Historical Kaggle venue is promoted beyond the evidence

**Location:** `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.md:35,39,47`; JSON `evidence.historical_venue`; `reports/amendments/amendment-008-review-response.md:17`; `docs/research/decision_log.md:64`.

**Problem:** a saved `/kaggle/input/...` path and `/kaggle/working/...` output string are configuration provenance, not authenticated execution provenance. The repository itself records the original script, manifest, invocation, environment, and hardware log as missing. The new `OBSERVED` classification repeats the V1 epistemic error in reverse.

**Scientific consequence:** Kaggle is presented as the original venue and then used as additional rationale for the amended venue. Readers may infer stronger historical continuity and comparability than exists.

**Resolution criterion:** downgrade the venue to unverified/circumstantial everywhere active, or supply independent authenticated Kaggle execution records. This finding is the residual cause for H-06 and is counted once.

### N-02 — MEDIUM — The machine-readable record declares closure before review

**Location:** JSON `findings_closed_in_v2`; amendment headings “cierra H-01/H-02/H-03/H-04/H-05/H-06/M-01/M-02”; author-response status table.

**Problem:** the sidecar's state is correctly `PROPOSED_V2` and `execution_permitted=false`, but its machine-readable field says every finding is closed while the required independent V2 review has not accepted that state. The Markdown uses the same earned-state wording.

**Scientific consequence:** a human or automated compliance check can treat author assertions as independent closure and undercount open controls.

**Resolution criterion:** represent these entries as `claimed_remediation`/`pending_independent_review`, and record closure only from the independent outcome with report hash and counts.

## Final decision

PROTOCOL-AMENDMENT-008 **may not** move from `PROPOSED_V2` to `APPROVED`. It must remain non-executable: no Kaggle upload and no Kaggle run.

- Prior findings not fully closed: **HIGH 5** (H-01, H-02, H-03, H-05, H-06) and **MEDIUM 3** (M-01, M-02, M-03).
- New findings: **N-01 HIGH**, already counted as the H-06 residual; **N-02 MEDIUM**, additional.
- **Unique open approval blockers: HIGH 5, MEDIUM 4.**
