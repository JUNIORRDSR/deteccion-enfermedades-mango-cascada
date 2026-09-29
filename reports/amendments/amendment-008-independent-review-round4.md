# Fourth-round independent adversarial review — PROTOCOL-AMENDMENT-008 version 4

- **Remediation range:** `0a34e4b..3564091`, plus relevant later changes through `9288371` (`HEAD`)
- **Relevant later commit:** `bb0e004` changes the CPU probe, its output, and the amendment JSON timestamp; no later commit touches the listed Amendment-008 remediation artifacts
- **Primary artifacts:** `provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.{md,json}`
- **Prior open findings tested:** H-02, H-03, M-01, M-02, and M-03/N-03
- **Posture:** all remediation statements were treated as claims to falsify. This review did not upload data, attach a Kaggle resource, run a Kaggle kernel, train a model, or perform inference.

## Verdict

**DO NOT APPROVE. PROTOCOL-AMENDMENT-008 may not move from `PROPOSED_V4` to `APPROVED`.** Version 4 creates real artifacts and closes M-03/N-03, but the input validator has reproducible fail-open bypasses, the proposed signed tag does not seal the scientific bundle, the platform reconciliation cannot detect omitted shadow attempts, and the capacity and prediction-transfer files are not yet enforceable, internally coherent gates.

`PARTIALLY CLOSED` counts as open for approval. Open approval blockers are **HIGH 2, MEDIUM 2**. Two new LOW findings concern the now-stale venue rationale/decision link and Markdown/JSON agreement.

| Finding | Severity | Round-4 status |
|---|---:|---|
| H-02 test-inaccessible phase inputs | HIGH | **PARTIALLY CLOSED** |
| H-03 one-way test discipline | HIGH | **PARTIALLY CLOSED** |
| M-01 schedulable capacity | MEDIUM | **PARTIALLY CLOSED** |
| M-02 prediction transfer | MEDIUM | **PARTIALLY CLOSED** |
| M-03/N-03 CPU identity, context, and probe truthfulness | MEDIUM | **CLOSED** |
| N-04 current venue rationale and decision chain | LOW | **OPEN** |
| N-05 Markdown/JSON agreement | LOW | **OPEN** |

## Checks performed

### Binding authority and remediation scope

The frozen plan still says to propose CPU when it is the only available device (`docs/superpowers/plans/2026-09-17-albus26-major-revision.md:221,229`). SPEC §11 still requires a fresh review with zero open HIGH/MEDIUM findings before approval and permits an experimental block to stop only its dependent branch (`docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md:151-162`).

The v3-to-v4 range was inspected in full. After `3564091`, only `bb0e004` touches the listed artifacts: it adds authorized output containment to the CPU probe, regenerates its output, and updates the amendment JSON timestamp. The later DECISION-030/031 commits do not update the Amendment-008 Markdown or JSON.

### Prescribed validator run

I ran exactly:

```powershell
& .\.venv\Scripts\python.exe -m unittest tests.test_kaggle_inputs -v
```

Result: **15 tests ran, all passed, exit 0** (`Ran 15 tests in 18.432s`, `OK`). Passing the supplied fixtures does not close H-02 because the fixtures omit several fail-open paths in the implementation.

### Independent validator attacks

I ran three temporary payloads without changing repository files. All should fail the amendment's closed-input contract; all passed with no violations:

1. A training YAML referred to an absolute file outside the allowed root in a sibling path whose name merely began with the allowed-root string (`input_evil` versus `input`). `validate_inventory` saw one allowlisted YAML and returned `violations=[]`. The cause is string-prefix containment at `src/evaluation/kaggle_inputs.py:223-228`.
2. An allowed root contained a directory symlink to external test bytes. The bytes were readable through the allowed-root path, but `os.walk(..., followlinks=False)` put the link in `directories`; the validator checks links only in `files`. It saw zero files and returned `violations=[]` (`src/evaluation/kaggle_inputs.py:175-192`).
3. A training image allowlist entry omitted `image_id`, `group_id`, `split`, and `label_sha256` while the exclusion set contained a test group. The schema declares these identity fields optional and the validator accepted the entry, so the group and phase checks never ran (`configs/kaggle_input_schema.json:26-39`; `src/evaluation/kaggle_inputs.py:67-96,205-214`).

The validator also accepts `--attached-resources` as operator-supplied JSON and does not bind it to a platform response, does not implement the schema's `extra_mounts` rule, and does not bind the allowlist's identity metadata to an independently frozen manifest (`src/evaluation/kaggle_inputs.py:165-173,232-248`; `configs/kaggle_input_schema.json:53-59`).

### CPU-probe behavior

I invoked `probe_cpu_topology.main()` against temporary output with `subprocess.run` controlled to return exit 0, empty stdout, and empty stderr:

- empty **optional** probe → probe `UNAVAILABLE`, global `PARTIAL`, function exit **1**;
- empty **required** probe → probe `UNAVAILABLE`, global `FAIL`, function exit **2**.

The checked-in real output reports the failed optional power-plan query as `UNAVAILABLE`, global `PARTIAL`, while the required topology and OS probes are measured (`provenance/environment/cpu_topology_probe.json:41-78`). This is honest behavior.

## Prior findings

### H-02 — HIGH — PARTIALLY CLOSED

**Evidence checked:** the schema, validator, all 15 supplied fixtures, the exact prescribed test command, and the three independent bypass payloads above.

Version 4 materially improves on v3: an executable validator and fixed schema now exist, null resource versions and unknown extensions are rejected in the tested cases, hashes match the amendment sidecar, and the supplied fixtures pass.

The root and indirection contracts are not actually closed. Path containment can be bypassed by string-prefix siblings; directory symlinks are not inspected; identity fields needed for split/group exclusion are optional and are not bound to an authoritative manifest; extra mounts are not checked; and effective resource identity is trusted from an arbitrary input JSON rather than captured from the platform. A training payload can therefore expose undeclared or test-related bytes while the validator reports PASS.

**Scientific consequence:** test pixels or group-related material can remain available to training or validation selection despite a passing pre-import report. Dependent M1 results would fail the frozen validation/test separation and Gate E.

**Resolution criterion:** use path ancestry rather than string prefixes; inspect and reject linked/reparse/mounted directories before traversal; implement the extra-mount rule; require the appropriate identity fields by file kind and phase; bind file metadata, exclusions, allowlist, and attached-resource identities to independently frozen/hash-verified sources; obtain effective versions from preserved platform evidence rather than an operator-authored JSON; and add negative fixtures for each reproduced bypass. An independent review must rerun those attacks.

### H-03 — HIGH — PARTIALLY CLOSED

**Evidence checked:** amendment §4.3, current Git signing configuration, pretest tags, local `git tag` syntax, ignore rules, and the frozen one-test requirements.

Declaring that no custodian/key exists and setting the TASK-05 test phase to `BLOCKED_BY_CUSTODIAN` is an **honest block, not an evasion**. It follows SPEC §11's rule that a blocked experimental branch stays blocked without falsifying a result. The narrowed retry taxonomy is also materially better: quota exhaustion is removed, platform failure needs platform evidence, validator failure is objective, and metric-driven retry remains prohibited.

The seal commands are syntactically valid but insufficient:

```powershell
git tag -a -s pretest/EXP-R02 -m "sealed pre-test bundle"
git tag -v pretest/EXP-R02
git rev-parse pretest/EXP-R02^{}
```

With no object argument, the first command signs the current `HEAD`; it does not by itself include the checkpoint, validation predictions, selected threshold, dataset versions, environment, permitted command, or a manifest of their hashes. Checkpoints are ignored by `*.pt`, so tagging a commit cannot silently bind them. The commands also do not verify an expected custodian fingerprint or name the exact committed manifest/object that must be peeled and compared. No signing key or pretest tag is currently configured, consistent with the declared block.

The platform control remains incomplete. A read-only independent launch log prevents alteration of recorded launches but does not detect a launch that the operator never entered. Because the public platform view is expressly non-exhaustive, a shadow attempt deleted or absent from that view can also be absent from the independent log and still reconcile. The custodian verifies the bundle before attachment but is not stated to control test attachment, account credentials, or every test launch.

**Scientific consequence:** once a custodian is named, the text would unblock a procedure in which the signed object need not bind the scientific bundle and omitted shadow test attempts can remain undetectable. Test feedback could still influence attempt or result selection.

**Resolution criterion:** keep `BLOCKED_BY_CUSTODIAN`; define a hash manifest covering every pretest artifact, commit that manifest or tag its exact object explicitly, verify the expected key fingerprint and every manifest byte before attachment, and retain the tag plus external bytes under independent custody. The custodian or an immutable broker must control test-resource attachment and all launch authority so every attempt is necessarily logged; cross-checking two non-exhaustive/operator-optional logs is not enough.

### M-01 — MEDIUM — PARTIALLY CLOSED

**Evidence checked:** `configs/capacity_plan.json`, repository-wide references to it and `capacity_preflight`, DECISION-030/031, and the observed `datasets.get` denial stated in the decision log.

The file fixes useful quantities: target configuration, three probe epochs with one excluded warm-up, validation/checkpoint overhead, maximum-based projection, safety factor 1.35, variance/preemption handling, and discard of probe weights/metrics. Those choices remove much of the operator discretion identified in round 3.

It is not yet a real fail-closed gate. No code consumes `capacity_plan.json`; no `capacity_preflight.json` exists; the output section is a list of field names rather than an enforceable typed schema; and status/exit code can be written independently of the stated equations. More importantly, the three pass inequalities cover session time, quota, and GPU memory only. Available storage and the required API-scope booleans are recorded facts but are not pass conditions. Thus the artifact can say PASS despite zero usable storage or a denied required read scope.

API scopes are correctly recognized **conceptually** as capacity, but not enforced as capacity. `datasets.get` is already recorded denied, and H-02 requires effective dataset identity/version reconciliation. Until that read capability or an equivalent authenticated platform receipt exists, the Kaggle path is not demonstrated usable. A missing write scope is not the only blocking case.

**Scientific consequence:** TASK-04 can be marked capacity-PASS from hand-written or incomplete values even when the account cannot create/reconcile inputs, launch the job, retrieve output, or store the run. That restores discretionary mid-run failure and retry risk.

**Resolution criterion:** implement and test a capacity-gate command that validates typed inputs, recomputes every equation, includes storage and **all** required API capabilities as mandatory booleans, emits the fixed report and exit code, and fails on missing/denied facts. Preserve authenticated scope evidence. The currently denied dataset-read capability must either be restored or replaced by an independently verifiable resource/version receipt before PASS.

### M-02 — MEDIUM — PARTIALLY CLOSED

**Evidence checked:** `configs/prediction_transfer_schema.json`, the amendment's transfer claims, the frozen TASK-05 contract, and repository-wide searches for the named evaluator and fixture.

The file fixes many previously open dimensions: original-image pixel coordinates, float64, post-NMS authority, score floor, class order, full M2 probability vector, non-finite rejection, ordering, byte hashes, and a 1e-9 recomputation tolerance.

It is not specific or coherent enough to implement and audit yet:

- the authoritative evaluator is explicitly `NOT_YET_IMPLEMENTED_TASK_05`, and both declared fixture files are still future work (`configs/prediction_transfer_schema.json:6-10,66-70`);
- detection output necessarily permits multiple boxes with the same `image_id`, but the shared completeness rule says `duplicate_image_id` is fatal (`:18-33,50-55`);
- the no-detection record requires `class_id=-1`, `score=0.0`, and a null box, while every detection record requires all four coordinates and the coordinate rule requires strict non-null inequalities (`:18-32,50-53`);
- the transfer contract omits the promised per-image `label_sha256`;
- the binding hashes have no specified envelope/header/sidecar location, and `predictions_sha256` cannot be an ordinary field inside the same bytes whose hash it defines (`:57-60`).

**Scientific consequence:** two reasonable implementers can produce incompatible files or validators, and normal multi-detection output can be rejected while a missing required binding can be interpreted differently. The authoritative metrics cannot be independently reproduced before inference.

**Resolution criterion:** resolve the record-shape contradictions; define separate detector/classifier file/envelope schemas, the no-detection union, per-image label identity, and external metadata/hash placement; then implement the authoritative evaluator and executable positive/negative fixtures. Freeze and independently review their exact hashes before any validation or test inference.

### M-03/N-03 — MEDIUM — CLOSED

**Evidence checked:** generator source, checked-in probe output, ART-107 registry hash, and controlled executions for empty optional and required probes.

The generator now treats nonzero exit, nonempty stderr, or empty stdout as unavailable. Optional failure yields `PARTIAL`/1; required failure yields `FAIL`/2. The real power-plan failure is no longer converted to PASS, while CPU name, 4 physical cores, 8 logical processors, OS/build, and clock/load hint are preserved with commands and raw outputs. Repeating the probes and recording thread/thermal context with TASK-06 remains a future run prerequisite, not a false claim that TASK-06 has already executed.

## New findings

### N-04 — LOW — Version 4 understates the measured local alternative and omits the user's current venue decision

**Location:** amendment `:55,57-65,156-164`; JSON `material_change` and `user_decision` at `:16-43`; `docs/research/decision_log.md:80-92`; `reports/execution/cpu_capacity_probe.json`.

**Problem:** DECISION-030 measured local CPU training at a conservative upper estimate of about 14.8 hours (about 20 hours with the 1.35 factor) and confirmed that the frozen plan already permits CPU. DECISION-031 then records the user's informed choice of Kaggle, with CPU retained as the valid fallback. Version 4 predates both decisions and still says its justification is no local GPU, measured Kaggle budget, and authorization; it does not say that local training is scientifically viable or link the later explicit choice.

**Consequence:** the amendment can be read as a necessity finding rather than a speed/preference choice, understating an already measured plan-compliant fallback if Kaggle rights, scopes, custody, or deadline prerequisites remain blocked. The broader decision log corrects the record, so this is LOW rather than a renewed scientific blocker.

**Resolution criterion:** update the append-only amendment record/sidecar to cite DECISION-030 and DECISION-031, state that CPU training is viable and plan-authorized, and characterize Kaggle as the user's selected faster venue subject to the listed gates—not as the only scientifically valid route.

### N-05 — LOW — Markdown and JSON do not fully agree on the version-4 formal record

**Location:** Markdown `:13,182-186`; JSON `:5,170-175`; input schema `configs/kaggle_input_schema.json:5-8`.

**Problem:** the Markdown's `recorded_at` row still gives the v2 timestamp and mentions a v3 sidecar, while the JSON gives the v4 timestamp `2026-09-22T15:50:52.179264+00:00`. The JSON's first blocking prerequisite requires a review of **version 3** with zero HIGH/MEDIUM findings, even though version 3 was rejected and the Markdown correctly requires review of version 4. The newly introduced input schema also says `minimum_version: 3` despite being a v4 remediation artifact.

**Consequence:** a reader or compliance tool cannot derive one exact version-4 timestamp and approval predicate from the pair. The wrong prerequisite fails closed rather than authorizing execution, so severity is LOW.

**Resolution criterion:** record the same v4 timestamp and v4 review prerequisite in Markdown and JSON, and correct the schema authority version. Regenerate hashes and have the next review verify the pair again.

## Integrity and execution-evidence checks

### Freeze integrity

The freeze is byte-identical to commit `7d0f9985cce73740cfa2ae26154971b55282ad52`; current and frozen Git blob IDs match, and there is no freeze diff through HEAD.

- `provenance/protocol_freeze.json`: `6d5aa3ff47cba97f8ecd0dd15683bb96f0d53146f3af1ce1e95bf24cec7cbc8b`
- `provenance/protocol_freeze.md`: `1a41b1aa684e26e5853aae31369c5200b29ae25a70bc383e3f0bd3ef136058be`

The sidecar's Markdown hash and all five frozen-mechanism hashes match the current files. Apart from N-05 and the post-v4 decision omission in N-04, the shared protocol identity, state, execution prohibition, test exposure, prior review outcomes, artifact ID, and claimed-remediation status agree.

### Kaggle upload/execution evidence

There is **zero repository evidence of an upload or execution under Amendment-008**. `experiments/` is empty; `EXP-R01`, `EXP-V01`, `EXP-R02`, and `EXP-R03` are absent; no capacity preflight or frozen operating-point config exists; ART-106 remains `RESERVED_NOT_YET_ACQUIRED`; and no dataset receipt/version, kernel/notebook run ID, prediction file, GPU log, or output ID exists. The tracked Kaggle-named files are authorization, capability observation, amendment/control artifacts, validator code, and tests.

This should not be broadened to “zero evidence that Kaggle was ever involved historically.” EXP-001 contains Kaggle-shaped saved paths, which are circumstantial configuration evidence but still do not authenticate a historical upload or execution venue.

## Final decision and counts

PROTOCOL-AMENDMENT-008 **may not** move from `PROPOSED_V4` to `APPROVED`.

- Open HIGH findings: **2** — H-02 and H-03.
- Open MEDIUM findings: **2** — M-01 and M-02.
- Closed prior MEDIUM finding: M-03/N-03.
- New LOW findings: **2** — N-04 and N-05.

Until the HIGH/MEDIUM findings are resolved and independently re-reviewed: **zero Kaggle uploads and zero Kaggle executions remain the required state.**
