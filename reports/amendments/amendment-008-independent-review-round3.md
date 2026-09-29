# Third-round independent adversarial review — PROTOCOL-AMENDMENT-008 version 3

- **Remediation range:** `f70bb2a..0a34e4b`, plus relevant later changes through `194efe1` (`HEAD`)
- **Primary artifacts:** `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.{md,json}`
- **Prior findings tested:** H-01–H-06, M-01–M-03, N-01, and N-02
- **Posture:** every remediation statement was treated as a claim to falsify. This review did not upload data, attach a Kaggle resource, run a Kaggle kernel, train a model, or perform inference.

## Verdict

**DO NOT APPROVE. PROTOCOL-AMENDMENT-008 may not move from `PROPOSED_V3` to `APPROVED`.** Version 3 closes the historical-venue overreach, earned-state wording, checkpoint/artifact identity, egress/privacy, and historical-run identity findings. It does not yet turn the load-bearing input-isolation and one-way custody rules into auditable mechanisms, and the capacity and prediction contracts remain promises to choose exact gates later. The new CPU probe also reports `PASS` despite a failed power-plan query.

`PARTIALLY CLOSED` counts as open for approval. Unique open blockers: **HIGH 2, MEDIUM 3**. New finding N-03 is the concrete defect that keeps M-03 open and is counted once, not twice.

| Finding | Severity | Round-3 status |
|---|---:|---|
| H-01 formal amendment record | HIGH | **CLOSED** |
| H-02 test-inaccessible training input | HIGH | **PARTIALLY CLOSED** |
| H-03 one-way test discipline | HIGH | **PARTIALLY CLOSED** |
| H-04 checkpoint, network, environment, artifact ID | HIGH | **CLOSED** |
| H-05 permission, privacy, and egress | HIGH | **CLOSED** |
| H-06 historical-run identity | HIGH | **CLOSED** |
| M-01 schedulable capacity | MEDIUM | **PARTIALLY CLOSED** |
| M-02 prediction transfer | MEDIUM | **PARTIALLY CLOSED** |
| M-03 CPU identity and benchmark context | MEDIUM | **PARTIALLY CLOSED** |
| N-01 historical Kaggle venue overreach | HIGH | **CLOSED** |
| N-02 author-declared closure before review | MEDIUM | **CLOSED** |

## Controlling checks

### Frozen authority

The current freeze is byte-identical to commit `7d0f9985cce73740cfa2ae26154971b55282ad52`. The current and frozen Git blob IDs match for both files:

- `provenance/protocol_freeze.json`: blob `0d86606b0620b5c2533664848305895ef90a2b7f`; SHA-256 `6d5aa3ff47cba97f8ecd0dd15683bb96f0d53146f3af1ce1e95bf24cec7cbc8b`.
- `provenance/protocol_freeze.md`: blob `ee957639a8dc1563d08d882b299b9a8380dd2612`; SHA-256 `1a41b1aa684e26e5853aae31369c5200b29ae25a70bc383e3f0bd3ef136058be`.

The freeze still requires complete and truthful experiment provenance, validation-only selection, one final test evaluation, preservation of failures, and no approval while a HIGH or MEDIUM review finding remains open (`provenance/protocol_freeze.md:185-210`; source SPEC §§11–12; TASK-04–06 in the frozen plan).

### Remediation scope through HEAD

Commit `0a34e4b` contains version 3, the response correction, DECISION-029, the CPU probe, and its sidecar generator. The only later change relevant to this amendment is the ART-106/ART-107 registry update in `194efe1`; the amendment Markdown, JSON, response, decision log, and CPU probe are unchanged after `0a34e4b`.

### Markdown/JSON identity and agreement

The Markdown hashes to `d530243372a4d50e9c8aa5824e494e6c036cef2749df80480f87ed27071d63e7`, exactly the value in the JSON sidecar (`PROTOCOL-AMENDMENT-008-kaggle-compute.json:160-164`). The V1 review, V2 review, and authorization hashes in the sidecar also match their current files.

No contradictory shared field was found. Both artifacts say version 3, `PROPOSED_V3`, `execution_permitted=false`, the same freeze identities, prior test exposure with no new access, DECISION-028, ART-106, historical paths `CIRCUMSTANTIAL`, historical venue `UNVERIFIED`, and claimed remediation pending independent review. The JSON summarizes rather than serializes the detailed H-02/H-03/M-01/M-02 controls; that is not a direct Markdown/JSON contradiction, but it does not supply the missing executable schemas discussed below.

### Historical venue and active-document search

The active amendment classifies the saved Kaggle-shaped paths as `CIRCUMSTANTIAL`, the historical venue as `UNVERIFIED`, and explicitly removes venue from the justification (`PROTOCOL-AMENDMENT-008-kaggle-compute.md:39-54`; JSON lines 112-130). EXP-001 still separates saved `device=0,1` metadata from the PDF-only `2 x NVIDIA T4 / Kaggle` claim and missing hardware log.

The response retains its false V2 sentence at line 17 as history, then appends an unmistakable correction: the assertion is an overreach, is withdrawn, and the governing status is circumstantial/unverified (`amendment-008-review-response.md:89-99`). The decision log likewise preserves DECISION-028 and immediately follows it with DECISION-029, titled as a correction, which expressly supersedes the venue conclusion and removes it from the rationale (`docs/research/decision_log.md:60-76`). The log's introduction says later decisions may explicitly supersede earlier ones. A reader following either append-only record reaches the corrected conclusion. Historical manuscript and genealogy transcriptions remain evidence of what was claimed, not active adoption of that claim.

### No Amendment-008 Kaggle execution or upload

There is still **zero repository evidence of an upload or execution under this amendment**. Tracked Kaggle-named artifacts are limited to the authorization, capability probe, and amendment Markdown/JSON. There is no `experiments/` directory, no `EXP-R01`, `EXP-V01`, `EXP-R02`, or `EXP-R03` output, no frozen operating-point config, no Kaggle dataset-version/upload receipt, no kernel/run/output identifier, no acquired ART-106 bytes, no prediction file, and no GPU run log. `kaggle_capability.json` remains an account quota observation, not an Amendment-008 run.

## Prior findings

### H-01 — HIGH — CLOSED

**Evidence checked:** amendment Markdown lines 7-31; complete JSON sidecar lines 1-80; `provenance/test_access_log.csv`; current freeze, authorization, V1 review, V2 review, and amendment hashes.

Version 3 records the exact protocol identity, material effect, inherited test exposure, zero new accesses, user decision, both completed independent reviews with their actual verdicts/counts, and the current `PROPOSED_V3`/non-executable state. The sidecar carries the exact V2 review hash and leaves the V3 review entry `PENDING`. The earlier premature-closure field is gone.

The current review cannot be cited before it exists. Adding this report's path/hash and the actual verdict is a mechanical prerequisite to any later state transition, not a residual defect in the version-3 procedure. If the record were changed to `APPROVED` without that insertion, H-01 would reopen.

### H-02 — HIGH — PARTIALLY CLOSED

**Evidence checked:** amendment §§4.1–4.2 (`:68-90`); JSON H-02 summary (`:83`); pinned Ultralytics 8.4.52 resolver at `.venv/Lib/site-packages/ultralytics/data/utils.py:453-544`; official KaggleHub cache/attachment behavior.

Version 3 correctly requires a clean kernel, versioned phase-specific inputs, effective-resource reconciliation, generated YAML without `test`, explicit rejection of `download`, `autodownload=False`, canonical containment, path-bearing indirections, and preservation of positive and negative validator results. These requirements close the obvious YAML and renamed-file bypasses.

The operative schema and validator still do not exist and are not specified precisely enough here to audit an implementation:

- No schema path, schema version, field types/cardinalities, validator path, invocation, output schema, or expected fixture results are fixed. Section 4.1 says those artifacts will be frozen later.
- The allegedly exhaustive roots include descriptions rather than resolved locations: “the platform resource cache,” “the kagglehub cache,” and environment-dependent roots. It does not define expansion/unset behavior or include all override locations such as `KAGGLEHUB_CACHE`, `XDG_CACHE_HOME`, `PIP_CACHE_DIR`, and temporary roots. An operator can therefore inspect a chosen interpretation of the list and still call it exhaustive.
- “Any file containing paths” is not a finite parsing contract. The text names `.txt` and sidecars but does not enumerate accepted path-bearing formats, recursive depth, encoding, or rejection of an unknown format. A validator cannot prove that an omitted indirection was omitted unless the accepted grammar is closed.
- Effective attached-resource reconciliation does not name the platform API/receipt or define failure when the platform reports no version. KaggleHub's resolver obtains `versionNumber` with a nullable lookup and mounts resources from a shared cache; the amendment does not state that a missing effective version is fatal.
- Symlinks/reparse points are rejected, but hard links, device nodes, code/notebook-embedded payloads, and mount identity are not covered. The code bundle/notebook itself is hashed later under H-03 but is not part of the per-file test-hash/group exclusion described here.

Official KaggleHub documentation confirms automatic attachment and shared-cache service, and its resolver returns the effective version only when the platform response includes it: <https://github.com/Kaggle/kagglehub>, <https://github.com/Kaggle/kagglehub/blob/main/src/kagglehub/kaggle_cache_resolver.py>.

**What an operator can still do:** choose concrete meanings for the descriptive cache roots, omit an unrecognized path-bearing format, accept a null/unverifiable resource version, or implement a validator whose output cannot be compared to a frozen expected schema. The prose would be violated in spirit, but no fixed artifact makes that objectively detectable before upload.

**Resolution criterion:** before approval, add and hash the concrete inventory schema, validator, command, output schema, and positive/negative fixtures. Resolve every root from a closed environment-variable contract; abort on unset/unknown/extra roots and null resource versions; include the code/notebook bundle and all allowed file types; define link/mount handling and a closed grammar for path-bearing indirections. The independent review must run the validator against bypass fixtures, not merely review a promise to create it later.

### H-03 — HIGH — PARTIALLY CLOSED

**Evidence checked:** amendment §4.3 (`:92-103`); JSON H-03 summary (`:84`); repository-wide search for a custodian identity/signing key; current Git signing configuration; official Kaggle CLI kernel commands.

Version 3 improves the retry taxonomy, makes a separate custodian mandatory, requires a signature before test attachment, and makes a missing/deleted platform attempt a Gate-E failure. Those are sound fail-closed intentions.

The custody mechanism is not yet operational or independently enforceable:

- No custodian is identified, no availability is established, and no trusted signing key/fingerprint or verifier is recorded. The only custodian references are the amendment and its generator. The current repository has no configured Git signing key. The rule therefore presupposes a second person or independent role that may not exist. If none exists, it safely blocks test, but it is not a workable approved procedure.
- “An annotated and signed Git object” is not an immutable storage primitive. Presumably this means a signed annotated tag, but no object/tag type or command is named. Git content hashes and signatures make mutation detectable; refs and objects can still be deleted, replaced, or pruned. The extra “read-only copy” has no location, independent owner, retention policy, or access-control evidence.
- The official Kaggle CLI documents kernel listing, push/pull, output retrieval, and the status of the **latest** run; it does not document an account audit export guaranteed to enumerate every attempt, cancellation, deletion, and output. The required reconciliation source is therefore unspecified and may not exist in the public interface: <https://github.com/Kaggle/kaggle-api#kernels>.
- The taxonomy names “platform infrastructure failure” but does not require independent platform evidence for that classification, byte-identical reuse of the sealed bundle, or sealing all partial outputs before a retry. “Quota exhausted” also remains retryable even though M-01 is supposed to reject a run that cannot fit.

**What an operator can still do:** self-designate a nominal custodian/key, preserve only the platform history visible through a non-exhaustive interface, classify a failure under the broad infrastructure category, and rerun without a specified proof that the sealed bundle and every exposed partial output were unchanged.

**Resolution criterion:** designate the custodian and trusted key/fingerprint or declare custodian unavailability as an explicit blocking prerequisite; specify the signed Git object/tag command, verification command, independent retention location/owner, and missing-object failure. Name and test an account-history source that actually exposes the required events, or narrow the claim and add an independently retained launch/access log that cannot be altered by the operator. Every allowed retry must carry external evidence, reuse the identical sealed bundle, and seal any partial output before relaunch.

### H-04 — HIGH — CLOSED

**Evidence checked:** amendment §7.1 (`:125-129`); JSON artifact/environment fields; all 107 rows of `provenance/artifact_registry.csv`; later registry change in `194efe1`.

ART-106 is now a reservation row for the official YOLO26n base checkpoint (`artifact_registry.csv:107`), with blank hash/size until acquisition and instructions to record URL, publisher, licence, and SHA-256. There are no duplicate artifact IDs. ART-005 retains its historical `args.yaml` identity. The amendment still requires separate logged acquisition, immutable version-pinned input, network disabled during training/inference, `YOLO_OFFLINE=true`, complete environment capture, and pre-run review of substitutions. The Markdown, JSON, and registry agree.

### H-05 — HIGH — CLOSED

**Evidence checked:** authorization; amendment §5 (`:105-118`), H-02 per-file identity fields, and M-02 prediction identity fields; CLAIM-008/010; dataset archaeology; frozen TASK-02/TASK-05 contracts.

The upload block is unambiguous: **nothing may be uploaded** while DATA-001 licence coverage remains `PARTIALLY_SUPPORTED` or DATA-004/005 identity remains unresolved. Both conditions are still unresolved, so the present amendment authorizes no upload.

The post-resolution privacy rule now matches the prior closure criterion: opaque filenames; local-only original-name mapping; sanitized archive members and text sidecars; explicit EXIF/IPTC/XMP removal or a field-by-field allowlist; visible-personal-data review where applicable; minimum phase payloads; private dataset settings; and a byte-for-byte receipt reconciled to the sanitized allowlist. An extra file fails the gate.

Opaque filenames do not by themselves break TASK-02 or reproducibility. TASK-02 remains local. The original-to-opaque mapping remains local, while H-02 requires each uploaded opaque file to retain `image_id`, `group_id`, split, byte hash, and label hash in the sanitized inventory, and M-02 requires those identities in predictions. That preserves group/sequence reasoning and permits local reconciliation without disclosing original filenames. The mapping and inventory must, as the amendment already requires, be frozen and retained; they need not be uploaded together with original names.

### H-06 — HIGH — CLOSED

**Evidence checked:** EXP-001 registry fields; amendment §§1.1 and 6; JSON historical venue/accelerator objects; response correction; DECISION-028/029; claim matrix and archival genealogy files.

Version 3 no longer presents EXP-R01 as a reproduction, no longer treats historical accelerator or venue as observed, and no longer uses venue continuity as rationale. EXP-R01 is a de novo reconstructed run whose actual accelerator must be reported after execution. Active records separate `device=0,1` saved metadata from the unverified PDF claim. N-01 is therefore closed as the residual cause of H-06.

### M-01 — MEDIUM — PARTIALLY CLOSED

**Evidence checked:** amendment §7.2 (`:131-136`); JSON M-01 summary (`:88`); frozen TASK-04 configuration and one-run rule.

The amendment now says capacity is conditional and requires an explicit pass/fail rule tied to 150 epochs, batch 16, 640 px, measured session limits, storage, and quota. That is better than treating a quota balance as capacity.

It can still be satisfied trivially. The measurement is only an example (“a reduced number of epochs”), and no minimum sample, warm-up treatment, validation/checkpoint overhead, estimator, uncertainty bound, numerical safety margin, session-limit equation, quota reserve, or failure code is fixed. “Fits with margin” leaves the margin to the same operator. A short favorable sample and linear extrapolation can be declared a pass without violating any serialized rule. A reduced-epoch training probe also creates an extra training attempt not reconciled with TASK-04's one-run discipline.

**Resolution criterion:** freeze the capacity plan now: exact non-test workload, number of measured steps/epochs, warm-up exclusion, included validation/checkpoint overhead, estimator and upper bound, numeric safety factor, session and total-quota inequalities, handling of variance/preemption, output schema, and pass/fail exit codes. State whether the probe is a non-scientific throughput run and forbid retention/use of its model or metrics.

### M-02 — MEDIUM — PARTIALLY CLOSED

**Evidence checked:** amendment §7.3 (`:138-142`); JSON M-02 summary (`:89`); frozen TASK-05 requirements.

Version 3 enumerates the right dimensions and requires one authoritative evaluator, a validator fixture, byte identity across transfer, no re-inference, and Gate-E failure for unreconciled discrepancies.

The “exact schema” is still prose and the evaluator is still to be chosen. There is no schema file/version/hash, field names, JSONL object shape, required/optional rules, cardinalities, detector-versus-classifier record forms, probability-vector order/length, coordinate convention, dtype encoding, non-finite rejection rule, evaluator path/commit/hash, or numerical comparison tolerance. Choosing and freezing them later before inference avoids test-driven selection, but it leaves a material contract to the operator after amendment approval with no required independent review of the resulting artifacts.

**Resolution criterion:** serialize and review the prediction schema and authoritative evaluator before approval. Include exact field/type/cardinality rules for M1 and M2, coordinate units, pre/post-NMS authority, score/probability semantics, class order, uniqueness/completeness failures, non-finite handling, deterministic ordering, serialization, evaluator identity, tolerances, and an executable positive/negative fixture with expected metrics.

### M-03 — MEDIUM — PARTIALLY CLOSED

**Evidence checked:** `provenance/environment/cpu_topology_probe.json`; its generator; ART-107 registry row/hash; fresh execution of every recorded command where permissions allowed.

The processor-name registry command reproduces `AMD Ryzen 5 7520U with Radeon Graphics`; the environment and registry commands reproduce eight logical processors. The preserved original CIM output records four physical and eight logical cores. ART-107's registry SHA-256 exactly matches the current probe file. This closes the original unsupported four-core assertion substantially.

The artifact is not a clean PASS. Its power-plan entry has empty stdout and an access/Terminal Services error in stderr (`cpu_topology_probe.json:29-33`) but records `exit_code: 0`; the file then reports `failed_probes: []` and `status: PASS` (`:48-49`). A fresh run reproduced the failure mode: the parenthesized PowerShell power-plan expression emitted an access-denied error while the `powershell.exe` process returned 0. Fresh CIM topology/OS/clock probes were also denied in the current review context, so their privilege/context prerequisite is not documented by the artifact.

The generator only treats nonzero process exit as failure and ignores nonempty stderr or empty required stdout (`probe_cpu_topology.py:36-43`). It always exits 0 (`:47`). The actual active power plan was not measured, and the top-level PASS is false. New finding N-03 below is the concrete residual and is counted here once.

### N-01 — HIGH — CLOSED

**Evidence checked:** every active location named by the prior review plus repository-wide Kaggle/T4/venue searches.

The amendment and sidecar use `CIRCUMSTANTIAL`/`UNVERIFIED`; the response has an explicit appended withdrawal; DECISION-029 expressly corrects DECISION-028; the experiment registry keeps the hardware log unverified; and no other active document was found using the historical venue as support for Amendment-008. The append-only correction is adequate because the records label the old conclusion as wrong and state the governing replacement, rather than merely adding an ambiguous later note.

### N-02 — MEDIUM — CLOSED

**Evidence checked:** amendment headings and introductory warning; JSON `closure_authority`, `claimed_remediation_pending_independent_review`, V3 review entry, state, and execution flag.

The author no longer claims independent closure. Headings say “responde a,” the sidecar explicitly labels the entries claimed remediation pending review, V3 review is `PENDING`, state is `PROPOSED_V3`, and execution remains false.

## New finding

### N-03 — MEDIUM — CPU context probe converts a failed power-plan query into `PASS`

**Location:** `provenance/environment/cpu_topology_probe.json:29-33,48-49`; `provenance/commands/task01/probe_cpu_topology.py:36-47`; amendment `:37,145`; JSON M-03 claim `:90`.

**Problem:** the PowerShell expression emits an error but returns process status 0. The generator checks only the process status, so it records no failed probe and labels the whole artifact `PASS` even though power-plan stdout is empty. The amendment accurately says the raw output is preserved, but the artifact's success classification and the M-03 claimed-remediation summary overstate what was obtained.

**Scientific consequence:** TASK-06 can be described as having a preserved power-plan context when the active plan is unknown. CPU frequency and latency depend on power policy; a false PASS can hide a benchmark-context gap and weaken reproducibility of the Ryzen result.

**Resolution criterion:** run PowerShell with terminating errors (`-ErrorAction Stop` or equivalent), fail a required probe on nonempty stderr or empty/malformed stdout, return nonzero/`PARTIAL` when any required probe fails, and record the actual active plan or an honest `UNAVAILABLE` state. Document the privilege/context needed to reproduce CIM probes and repeat them in the TASK-06 run record. N-03 is the reason M-03 remains open and is not an additional count.

## Final decision and counts

PROTOCOL-AMENDMENT-008 **may not** move from `PROPOSED_V3` to `APPROVED`.

- Open HIGH findings: **2** — H-02 and H-03.
- Open MEDIUM findings: **3** — M-01, M-02, and M-03/N-03.
- Closed HIGH findings: H-01, H-04, H-05, H-06, and N-01.
- Closed MEDIUM finding: N-02.

Until the open findings are resolved and independently re-reviewed: **zero Kaggle uploads and zero Kaggle executions remain the correct state.**
