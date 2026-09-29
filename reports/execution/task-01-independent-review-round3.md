# TASK-01 third-round independent adversarial review

**Remediation diff reviewed:** `3367672..194efe1`  
**Authorities read first:** `.superpowers/sdd/2026-09-17-albus26-major-revision/task-1-brief.md`; design specification sections 4 and 11; immutable `provenance/protocol_freeze.json`  
**Prior claims treated as claims to falsify:** both prior reviews, both author responses, `reports/source_verification.json`, `provenance/environment/runtime_path_report.json`, and commit `194efe1`  
**Review constraint:** no product, test, configuration, provenance, or documentation file was modified. The filesystem-writing unit suite was not rerun because the instruction permits only this report to be written. The checked-in GREEN log was inspected but is not fresh evidence. All fresh probes below were read-only or in-memory.

## Executive result

**REJECT. TASK-01 may not pass its independent-review gate.** The present 11,137-source corpus is clean under the current host's NTFS file IDs and hashes, the freeze is unchanged, ART-103 is repaired, and several malformed-input and redaction cases are genuinely improved. The delivered controls still do not authenticate the active checkout, do not prevent overwriting all inputs, do not route all writers through the output guard, do not prove runtime-wide containment, and still certify malformed CSV, external import paths, incomplete schemas, and incomplete registry integrity.

Using the same counting convention as round 2, newly exposed remediation defects are counted separately even when they also reinforce an older umbrella finding. **Prior nonclosed findings: 3 HIGH and 8 MEDIUM. New findings: 0 HIGH and 4 MEDIUM. Gate total: 3 HIGH and 12 MEDIUM open.** The prior LOW is closed.

## Fresh evidence and scope checks

- `git diff 3367672..194efe1 -- provenance/protocol_freeze.json` is empty. The current freeze SHA256 is `6d5aa3ff47cba97f8ecd0dd15683bb96f0d53146f3af1ce1e95bf24cec7cbc8b`.
- A fresh read-only run of `read_rows`, `validate_locations`, `file_identity`, and `verify_sources` over the real corpus found 11,137 manifest rows, 11,137 sidecar rows, zero discrepancies, zero missing paths, zero directories, zero pathname fallbacks, zero `st_dev == 0`, zero `st_ino == 0`, and zero duplicate identity groups. The source-manifest SHA256 was `b72041a4f84034dcb5c77dee547805a3d8f0c3f9a86a9851a4979c5a5996a781` both before and after. This proves the current local corpus, not the race/cross-filesystem contracts.
- Output-policy probes rejected `reports-evil/x.json` and `data/derived-x/x.json`, and Windows case variants resolved to the existing canonical spelling. The same guard accepted the binding design document as an output and accepted the directories `reports/` and `provenance/environment/` where a file destination was expected.
- The Python-writer inventory found 22 non-test writer modules. Eighteen contain direct writes and no `check_output` reference. Three are current TASK-01 writers: `build_inputs.py`, `probe_cpu_topology.py`, and `write_amendment_sidecar.py`.
- The artifact registry has 107 rows, zero duplicate artifact IDs, and zero duplicate path strings. ART-101..105 and ART-107 resolve locally and match their registered bytes. ART-005 is unchanged by the remediation diff. Only 6/107 registry rows resolve from this checkout; the current integrity test silently skips the other 101, including ART-106.
- The credential-shaped scan covered all 161 files under `provenance/environment/`, `provenance/incidents/`, and `reports/`, including binary bytes for recognizable ASCII token formats. No live credential-shaped candidate was found in environment or incident evidence. Credential-like example literals occur at `reports/execution/task-01-independent-review.md:70`, `reports/execution/task-01-independent-rereview.md:104`, and `reports/execution/task-01-review-response-round2.md:64`; these are review examples, not live credentials. Values are intentionally not reproduced here.
- During the review, an unrelated untracked `reports/amendments/amendment-008-independent-review-round3.md` appeared after the initially clean status check. After this report was written, a concurrent process advanced HEAD from `194efe1` to `3564091` and committed both round-3 reports. This reviewer did not stage, commit, reset, or push anything. The concurrent commit is outside the requested `3367672..194efe1` review range.

## Prior-finding disposition

### 1. HIGH — source/file uniqueness: PARTIALLY CLOSED

**Checked:** `src/evaluation/provenance.py:104-120,363-425`; `tests/test_provenance_round2.py:30-57`; `reports/source_verification.json:4-5`; the fresh 11,137-row scan above.

The hardlink bypass from round 2 is closed on this NTFS host: existing paths are grouped by `(st_dev, st_ino)`, the hardlink test uses a real `os.link`, and the present corpus has no duplicate or zero file IDs. Dot, slash, case, and aliased-root spellings are also grouped.

The full uniqueness contract is not closed. `validate_locations` observes identity at lines 412-420, while `verify_sources` later reopens/rechecks only pathname and hash at lines 279-293. If a distinct target is deleted and replaced by a hardlink or same-byte replacement between those phases, both hashes can pass even though the reported identity relation is no longer the one validated. A stable deletion alone does fail with one discrepancy; a stable directory also yields one discrepancy, although both are accepted by the earlier identity/schema phase. A probe with one existing target and one missing target confirmed `validate_locations` accepts and final verification reports one issue.

`file_identity` also catches every `OSError` and falls back to pathname, not only `FileNotFoundError`. It unconditionally trusts nonzero `st_dev/st_ino`; no capability or stability check exists for non-NTFS, network, synthetic-inode, or inode-reuse behavior. The committed report names unexercised mapped drives, 8.3 aliases, SUBST, and reparse points, but omits the identity/hash TOCTOU, the any-`OSError` fallback, and non-NTFS file-ID reliability. Its `uniqueness_method` describes the successful local method; its `uniqueness_limits` do not exactly describe what the code proves.

**Resolution criterion:** couple file identity and hashing in one stable/open-handle observation, revalidate identity immediately before reporting, distinguish missing from operational stat failures, detect unsupported/zero/unstable file IDs and fall back to a documented platform primitive without claiming physical identity, and publish all residual limits in the report.

### 2. HIGH — authenticated root and write/output policy: OPEN

**Checked:** `src/evaluation/provenance.py:46-75,123-214`; `tests/test_provenance_hardening.py:97-158`; `tests/test_provenance_round2.py:60-95`; every Python write site.

The fixed freeze digest is not checkout authentication. Any directory containing copied freeze bytes, or a symlink/hardlink to the real freeze, satisfies `is_file()` plus SHA256. A nested tree wins because `authorized_root` returns the first matching ancestor. More directly, the public `expected_freeze` argument on `authenticate_root`, `check_output`, `create_run`, and `configure_environment` lets a caller choose the digest of an arbitrary fixture; the committed tests intentionally do this. No Git worktree identity, expected `.git` administrative target, baseline, or canonical active-root check exists.

The subtree prefix checks themselves correctly reject `reports-evil` and `data/derived-x`, and Windows case spelling resolves correctly. The allowlist is still not an input-protection policy. A fresh probe showed `check_output` accepts `docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md`, even though it is binding input, because all `docs/` are writable outputs. It likewise allows arbitrary existing files below `configs/`, `reports/`, and the other allowed trees unless they are one of eight `PROTECTED_RELATIVE` names. A hardlink placed in an allowed tree to any other tracked/input file also bypasses the eight-file identity loop. Passing a directory where the CLI expects a report file is accepted and becomes an execution error only at `write_text`.

The remediation also did not route every writer through the guard. Current TASK-01 counterexamples are:

- `provenance/commands/task01/build_inputs.py:9-14,31-34,66` trusts `cwd` and writes protected configs/sidecar directly;
- `provenance/commands/task01/probe_cpu_topology.py:44-45` writes a relative path directly;
- `provenance/commands/task01/write_amendment_sidecar.py:133-134` writes a relative amendment path directly.

Other unguarded writer modules are `provenance/commands/{capture_sources,close_first_phase,finalize_delivery,polish_plan_prose,read_official_template,resolve_design_review,verify_first_phase,write_claims,write_research_indexes}.py`, `reports/datasets/inventory_legacy.py`, `reports/experiments/{build_registries,inspect_existing_evidence}.py`, and `reports/genealogy/{collect_genealogy,compare_genealogy,verify_relationships}.py`. `install_reconstructed.py` validates the parent directory once, then performs all child writes directly, so the declared reparse-point check/use race also remains.

**Resolution criterion:** bind root identity internally to the active authorized Git worktree and expected administrative repository, remove caller-selected production authentication, reject copied/link-only freezes, classify every immutable/input path rather than eight names, distinguish file and directory destinations, route every production writer through the same guard at the final target, and close or block the reparse-point TOCTOU.

### 3. HIGH — runtime containment and prior external write: PARTIALLY CLOSED

**Checked:** `provenance/commands/task01/verify_runtime_paths.py:30-205`; `provenance/environment/runtime_path_report.json`; pinned Ultralytics `utils/__init__.py:808-821,944-946`.

The known unsafe profile import is now sandboxed, guarded Ultralytics settings resolve inside the checkout, all ten listed integrations are false, and known INCIDENT-001 files remain honestly documented. `YOLO_OFFLINE=true` is assigned before import. The pinned `is_online()` returns false immediately for that exact environment value, and the report measures `ONLINE=false` in guarded mode versus `true` in its unguarded negative mode. The offline result is therefore supported, not merely incidental to unavailable networking.

The containment claim remains incomplete. Guarded mode uses the real `USERPROFILE`, `APPDATA`, and `LOCALAPPDATA`; it reports only Ultralytics datasets/weights/runs/settings/user-config strings. It does not query or audit effective torch, matplotlib, numba, pip, Python user, or `tempfile.gettempdir()` locations, nor does it take an OS-level or before/after write inventory. Importing `torch` and checking CUDA is not proof of torch-cache containment. The report therefore cannot detect an import-time writer outside the five hand-selected settings keys.

`EXPECTED_HAZARD_KEYS` is also key-only. Any new unsafe destination under `datasets_dir`, `weights_dir`, or `runs_dir` remains “expected,” and disappearance of an expected hazard is not a failure because equality with the expected set is never required. A genuine unguarded regression under those keys can be absorbed; a guarded escape among the five observed keys still fails. The larger guarded risk is that unobserved writers never enter `payload['escaped']` at all.

**Resolution criterion:** preserve the controlled negative test but compare exact expected keys and destination classes, isolate guarded profile variables too, record effective paths for every named runtime/temp facility, and use an OS-enforced or complete before/after write audit that can detect writers beyond Ultralytics settings.

### 4. MEDIUM — operational I/O error classification: CLOSED

**Checked:** `src/evaluation/provenance.py:89-101,263-293,520-531`; `tests/test_provenance_hardening.py:161-190`.

`verify_sources` catches only expected validation/missing/key cases; a `PermissionError` from hashing propagates. Unexpected output and runtime exceptions retain traceback and exit 1, while `InvalidInput` maps to 2. A mocked `Path.stat -> PermissionError` also propagated from final source verification rather than becoming a clean result. The broader `file_identity` fallback remains a uniqueness-limit problem under finding 1, but it does not by itself suppress the later source-verification failure.

### 5. MEDIUM — total malformed-input/exit-2 contract: PARTIALLY CLOSED

**Checked:** `src/evaluation/provenance.py:318-349,482-531`; in-memory parser probes.

Duplicate/missing headers, ordinary short/surplus rows, invalid UTF-8, and header-only files are now invalid input. The contract is still not total: a NUL in a logical path reaches `stat` and raises raw `ValueError` (CLI exit 1), an unmatched quote in the final field is accepted, and an enormous field raises raw `_csv.Error` from `read_rows` iteration (the module-level CLI happens to map it to 2). See N3.

### 6. MEDIUM — durable secret sanitization: PARTIALLY CLOSED

**Checked:** `src/evaluation/provenance.py:80-85,428-466`; `install_reconstructed.py:31-49,62-85,129-140`; in-memory sanitizer probes; durable-artifact scan above.

Snake/kebab-case secret keys, split name/value headers, common authorization/cookie/signature text, HTTP URL userinfo/query, and scheme-less proxy userinfo are improved. Realistic shapes remain unchanged: camelCase `accessKeyId`, `secretAccessKey`, `clientSecret`, and `sasToken`; PEM private-key blocks; unlabeled provider-token formats; and connection strings using `AccountKey`. The present durable environment/incident artifacts did not expose a live credential-shaped candidate, so this is a policy-enforcement defect rather than a demonstrated current leak.

**Resolution criterion:** add conservative camelCase/key-normalization, PEM and common provider-token handling, connection-string parsing, and tests at every durable writer; retain location-only post-generation scanning.

### 7. MEDIUM — startup isolation and integrations: PARTIALLY CLOSED

**Checked:** `src/evaluation/provenance.py:30-44,86,217-251`; `provenance/commands/task01/command.txt`; in-memory hostile `sys.path` and preimport probes.

Path variables, five isolation values, user-site state, and the ten Ultralytics settings are checked. The new `sys.path` check is defeatable because line 242 uses string `startswith`: an external path equal to the checkout string plus `-evil` was certified with `sys.path_external_entries=0`. The preimport test also certified injected `matplotlib` and `numba`, because neither is in `SCIENTIFIC_MODULES`. See N4.

The launcher is not isolated before Python startup (`-I` is absent), so `sitecustomize` can import/write before this late check. Listed modules may be detected afterward, but side effects have already occurred; unlisted scientific modules are not detected. The fact that the CLI itself imports no scientific package makes the clean result expected, not proof that startup hooks were unable to do so.

### 8. MEDIUM — sidecar schema enforcement: PARTIALLY CLOSED

**Checked:** `src/evaluation/provenance.py:296-349,363-425`; direct calls with and without roots.

The main CLI path enforces five nonblank string fields, lowercase hash syntax, local-path consistency, unique headers, and ordinary row width. `validate_locations` does **not** enforce the sidecar schema on every coverage path: line 369 requires both `enforce_schema` and `roots is not None`. A manifest plus sidecar containing only `source_id` and `sha256` passed `validate_locations(manifest, locations)` in a fresh probe. `build_inputs.py:30` uses exactly that no-roots path before writing the sidecar. Extra named header columns are also accepted. See N3 for representation-level holes.

**Resolution criterion:** make schema enforcement unconditional whenever coverage is declared, give any intentionally reduced API a different name, enforce an explicit header policy, and validate the parsed CSV semantics before coverage/uniqueness.

### 9. MEDIUM — method tests and RED/GREEN evidence: PARTIALLY CLOSED

**Checked:** all three test modules; `green.log`; `red-round2.log`; `command.txt`.

The 19 new tests target genuine round-2 bypasses, and `red-round2.log` preserves a real failing state. The suite still lacks the clone/link-freeze root attack, arbitrary allowed-input overwrite, file/directory destination typing, identity/hash race, prefix-sibling `sys.path`, matplotlib/numba/sitecustomize, multiline/strict/NUL CSV, exact expected runtime hazards, complete writer audit, and registry missing/linkage cases. Several existing tests positively authenticate temporary trees solely by caller-supplied digest.

The stored log says 47 tests passed, but the recorded self-contained command runs only `tests.test_provenance` and `tests.test_provenance_hardening`; it omits `tests.test_provenance_round2`, whose 19 cases occupy `green.log:29-47`. See N6.

### 10. MEDIUM — required artifacts and registry linkage: PARTIALLY CLOSED

**Checked:** `provenance/artifact_registry.csv`; `provenance/experiment_registry.csv`; `register_artifacts.py`; `command.txt`; exact byte hashes.

The named files exist, ART-101..105/107 match their current bytes, ART-103 is repaired, and no pre-existing row or ART-005 changed. The new rows place `TASK-01` in `experiment_ids`, but the experiment registry contains only EXP-001..EXP-009; there is no TASK-01 producing execution. `register_artifacts.py` does not replace nonblank existing relations, so several rows retain descriptive relations rather than links to the producing command despite the response claim.

The integrity loop and test skip every missing path and every blank hash and do not validate duplicate IDs, schema, linkage, or sentinel policy. Only 6/107 rows are checked. `command.txt` is also not self-contained from a clean environment. See N5 and N6.

### 11. LOW — publication policy for machine identifiers: CLOSED

**Checked:** `docs/research/evidence_publication_policy.md:1-39`.

A durable policy now classifies private versus publishable fields, specifies deterministic placeholders and hash linkage, requires fail-closed testing, and forbids publication until the TASK-10 projection and test exist. The projection is not yet implemented, but the present disclosure risk is controlled by an explicit no-publication rule; implementation remains a TASK-10 acceptance condition rather than an open TASK-01 policy defect.

### N1. MEDIUM — PASS with an escaped negative-mode path: PARTIALLY CLOSED

**Checked:** `verify_runtime_paths.py:167-196`; `runtime_path_report.json:4-12,109-157`.

The report now explicitly separates guarded escapes from unguarded expected hazards and states that global PASS does not mean no path escaped. That closes the false prose claim. It remains partial because the key-only allowlist accepts arbitrary changed destinations under three names, does not require expected hazards to be present, and shares one overall PASS with an incomplete guarded-writer proof.

### N2. MEDIUM — ART-103 false registered identity: PARTIALLY CLOSED

**Checked:** `artifact_registry.csv:102-108`; `register_artifacts.py:36-90`; `test_provenance_round2.py:200-220`.

ART-103 now exactly matches 900 bytes and SHA256 `36d746868b58efb6596d84e21fc814f7153e6e4a21613208d415188f28dbdc71`; the other locally resolvable TASK-01 rows also match and there are no current duplicate IDs. The required registry-wide protection is not closed because missing/blank rows, duplicates, schema, and experiment linkage are not tested. See N5.

## New findings

### N3. MEDIUM — `read_rows` changes CSV data and accepts malformed records

**Location:** `src/evaluation/provenance.py:318-349`; absent coverage in `tests/test_provenance_round2.py:97-151`.

**Failure scenario:** `text.splitlines()` removes record terminators before `csv.reader` sees them. A quoted logical path `src/evaluation/provenance.<LF>py` or the lone-CR equivalent becomes `src/evaluation/provenance.py`. A fresh probe fed that CSV through `read_rows`, `validate_locations`, and `verify_sources` against the real file; the full gate returned zero issues for bytes whose CSV meaning contained a newline. A final unmatched quote is accepted because the reader is not strict. NUL and mid-file BOM characters are accepted; the NUL later raises raw `ValueError`. A field above the CSV limit raises raw `_csv.Error` during iteration because only reader construction/header fetch are in the `try`. Leading/trailing header whitespace is rejected, which is correct.

**Resolution criterion:** pass a newline-preserving text stream to `csv.reader`, use strict parsing or explicitly reject malformed quoting, reject NUL and disallowed BOM placement, catch `csv.Error` across iteration as `InvalidInput`, enforce exact allowed headers, and add full-gate tests for LF, CR, NUL, oversized fields, BOM placement, unmatched quotes, and whitespace headers.

### N4. MEDIUM — import isolation uses string-prefix containment and an incomplete module set

**Location:** `src/evaluation/provenance.py:86,236-250`.

**Failure scenario:** with every environment value otherwise correct, `sys.path=[<checkout>-evil]` passes because `canonical(entry).startswith(canonical(checkout))`. Injecting `matplotlib` and `numba` into `sys.modules` also passes and reports `preimported_scientific_modules=0`. A startup `sitecustomize` can therefore execute from a prefix-confusable path or preload unlisted runtimes before the verifier runs.

**Resolution criterion:** compare path components with `Path.is_relative_to`/`commonpath` after canonicalization, validate empty/current-directory entries explicitly, cover every named scientific/runtime writer including matplotlib and numba, and launch through a startup-isolated wrapper that sanitizes environment before interpreter/site initialization.

### N5. MEDIUM — the “whole registry” check skips 101 rows and ART-106 is not a schema-valid artifact

**Location:** `tests/test_provenance_round2.py:200-220`; `provenance/commands/task01/register_artifacts.py:44-88`; `provenance/artifact_registry.csv:107`; `PROTOCOL-AMENDMENT-008-kaggle-compute.md:123-127`.

**Failure scenario:** both integrity loops execute `continue` when a path does not resolve or the hash is blank. A registry row can drift to a missing path, lose its hash, duplicate an ID, or reference a nonexistent experiment and still pass. Fresh counts were 107 rows but only 6 checked. ART-106 currently has sentinel path `RESERVED_NOT_YET_ACQUIRED`, blank hash/size, `source_id=RESERVED`, and `experiment_ids=TASK-04`, which is not an experiment-registry ID. The amendment specifies acquisition in a separately recorded step with URL, version, license, size, and SHA256; the current row is a reservation, not that artifact. Current IDs are unique and ART-005 is untouched, but the reservation has no formal status field/schema exception.

**Resolution criterion:** validate unique IDs/paths and all required columns first; resolve each row through its declared source/root semantics; fail missing/blank identities for real artifacts; validate every experiment link; keep reservations in a separate registry or add an explicit validated `RESERVED` state that cannot be consumed as an artifact and must be atomically completed on acquisition.

### N6. MEDIUM — the self-contained command record cannot reproduce its own GREEN evidence or environment

**Location:** `provenance/commands/task01/command.txt:1-34`; `green.log:29-52`; `install_reconstructed.py:19-24`.

**Failure scenario:** the recorded unit-test command omits `tests.test_provenance_round2`, yet `green.log` includes those 19 tests and reports 47 total. The environment step says it creates `.venv` but invokes `.venv\Scripts\python.exe` to run a script that only installs into the already-running interpreter; it cannot bootstrap a clean checkout. Lines 32-34 also claim every entrypoint calls both environment helpers, while `install_reconstructed.py` calls only `configure_environment` and the CPU/registry scripts call neither.

**Resolution criterion:** record the exact command that generated each log, include all three test modules, bootstrap the venv from an explicitly recorded external interpreter before invoking its Python, accurately state which entrypoints initialize/verify isolation, and regenerate/hash the command artifact after the reproducible sequence passes.

## Claim audit

- **Supported:** the remediation does not modify the immutable freeze; the current corpus has 11,137 clean source hashes and unique local NTFS file IDs; ART-103 and the other six local TASK-01 registry files match; ART IDs are currently unique; ART-005 and rows 1-100 are untouched; `YOLO_OFFLINE=true` is set before guarded import and the pinned code makes the measured false result causal.
- **Unsupported/overstated:** response line 17 and `source_verification.json:5` say the limits match what is proved; response lines 25-30 and the commit describe digest matching as root authentication and a real input policy; response line 46 says unexplained runtime escapes fail although changes under expected keys are whitelisted; response line 52 says the whole registry is protected and every artifact is command-linked; response line 60 says `read_rows` translates CSV format failures and `validate_locations` enforces its schema itself; response line 66 implies the listed secret shapes close the policy; response line 72 says external `sys.path` and scientific preimports are excluded; response lines 78/84 and the commit say 47 tests and full containment/schema/registry integrity are reproducible from the recorded evidence. The concrete counterexamples above falsify those broader statements.
- **Narrowly honest:** `runtime_path_report.json:11` now says PASS does not mean no path anywhere escaped. That wording is accurate, but its stronger phrase that the guarded entrypoint “is contained” is not supported for unobserved runtime/temp writers.

## Verdicts

**Frozen-brief compliance: FAIL / NOT COMPLIANT.** The freeze and present source bytes are intact, but the active checkout is not authenticated, input/output protection is incomplete, multiple writers bypass the guard, runtime-wide containment is unproved, and malformed/schema/registry gates remain defeatable.

**Engineering quality: REJECT.** The remediation fixes real examples but repeatedly turns those examples into narrow allowlists or tests while retaining the broader defect. Several generated claims and the self-contained command record exceed the evidence.

**Open counts:** prior nonclosed = **3 HIGH, 8 MEDIUM**; new = **0 HIGH, 4 MEDIUM**; gate total = **3 HIGH, 12 MEDIUM**.

**TASK-01 may not pass its independent-review gate.**
