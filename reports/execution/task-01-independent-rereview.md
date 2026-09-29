# TASK-01 independent adversarial re-review

**Remediation diff reviewed:** `675c49c..3367672`  
**Authorities:** frozen TASK-01 brief; design specification sections 4 and 11; immutable `provenance/protocol_freeze.json`  
**Posture:** `reports/execution/task-01-review-response.md` and commit `3367672` were treated as claims to falsify, not evidence.

## Executive result

**REJECT. TASK-01 may not pass its independent-review gate.** The remediation improves the checked-in sidecar and closes the operational-error classification defect, but all three prior HIGH findings remain unresolved (two partially closed, one open), six prior MEDIUM findings remain unresolved, and two new MEDIUM defects were introduced or exposed by the remediation.

The immutable freeze was not changed by the remediation diff. Fresh hashes are:

- `provenance/protocol_freeze.json`: `6d5aa3ff47cba97f8ecd0dd15683bb96f0d53146f3af1ce1e95bf24cec7cbc8b`
- `provenance/protocol_freeze.md`: `1a41b1aa684e26e5853aae31369c5200b29ae25a70bc383e3f0bd3ef136058be`

A fresh in-memory run over the real 11,137-row sidecar completed in 71.129 seconds with zero hash discrepancies, zero duplicate Windows `(st_dev, st_ino)` file identities, and the original manifest unchanged (`sha256 b72041a4f84034dcb5c77dee547805a3d8f0c3f9a86a9851a4979c5a5996a781`). This establishes that the present dataset happens to be clean under a stronger file-ID scan. It does not establish that the delivered validator enforces the claimed contracts.

The filesystem-writing `unittest` suite was not rerun because this review was expressly forbidden to write anywhere except this report; its checked-in `green.log` was inspected but was not treated as fresh verification. All hostile probes described below were fresh and read-only. Three real CLI malformed-input probes were also run; none reached its `--out` path.

## Prior findings

### 1. HIGH — canonical uniqueness: PARTIALLY CLOSED

**Relevant code:** `src/evaluation/provenance.py:79-81,233-281`; `reports/source_verification.json:4`; `tests/test_provenance_hardening.py:29-85`.

What is closed: dot segments, slash spelling, case spelling on this Windows host, and two logical roots mapped to the same resolved pathname are now compared through `normcase(realpath(...))`. A real redirected AppData path and its package-cache view canonicalized to the same path, showing that `realpath` resolves at least that available reparse/virtualization case. The current 11,137 rows also contain no duplicate Windows file IDs.

What is not closed: pathname canonicalization is not physical-file identity. A fresh probe used the existing Windows hardlinks

- `C:\Windows\System32\kernel32.dll`
- `C:\Windows\WinSxS\amd64_microsoft-windows-kernel32_31bf3856ad364e35_10.0.26100.9444_none_2f8379ba064efb69\kernel32.dll`

`os.path.samefile` returned true and both paths had the same device/inode pair, but `canonical()` returned two different strings. `validate_locations` accepted them as two SRC IDs and `verify_sources` returned `[]`. Thus `reports/source_verification.json` and response line 33 claim more than the method proves.

No SUBST drive or network-mapped drive was available on this host, and the 8.3-volume query was access-denied. Those cases therefore remain unproved, not implicitly passing. Python's non-strict `realpath` also stops resolving on several access, network, unsupported-reparse, and missing-path errors; a missing file is normally caught later, but the comparison and hashing remain separate TOCTOU observations. Root mappings that resolve through supported junctions are improved, but hardlinks alone are a decisive bypass.

**Resolution criterion:** use a stable file identity for existing sources (on Windows, volume/file ID or an equivalent `samefile` grouping) in addition to the portable resolved path; explicitly test hardlinks, symlinks, junction roots, 8.3 aliases, SUBST/mapped/UNC aliases when available, missing-at-check-time behavior, and revalidation immediately before hashing/reporting. Narrow the report claim to the method actually proved.

### 2. HIGH — write authorization: OPEN

**Relevant code:** `src/evaluation/provenance.py:45-55,84-118,121-136`; `provenance/commands/task01/install_reconstructed.py:18-21,28-35,59-85,125-137`; `tests/test_provenance_hardening.py:92-149`.

The freeze hashes are intact and exact protected spellings such as `provenance/protocol_freeze.json`, ordinary `NUL`, and trailing-dot/space spellings are rejected. Running from a nested directory under this checkout correctly found the checkout ancestor.

The authorization boundary remains caller-controlled:

- `check_output(Path('C:/Windows'), Path('C:/Windows/Temp/out.json'))` was accepted. `check_output` never authenticates `root`; `create_run(root, path)` merely delegates to it, so any caller-selected writable root remains authorized.
- `authorized_root` authenticates only the existence of any ancestor file named `provenance/protocol_freeze.json`; it does not verify the Git checkout, expected freeze hash, or canonical authorized root. The test deliberately creates an arbitrary temporary tree containing `{}` and calls it authorized.
- `check_output` accepted the existing tracked input `src/evaluation/provenance.py` and the existing report `reports/source_verification.json`. The eight-entry `PROTECTED_RELATIVE` tuple is not an approved output policy and does not satisfy the frozen rule against modifying inputs.
- `check_output` accepted `NUL:$DATA` and `provenance/protocol_freeze.json:evil`. The device test compares `NUL:$DATA`, not its base device name, and protected-path comparison does not reject NTFS alternate data streams/colon forms.
- A hardlink to a protected file bypasses the pathname comparison for the same reason as finding 1. Existing symlinks/junctions that `realpath` resolves are caught, but the declared junction TOCTOU remains.
- `install_reconstructed.py` still defines `ROOT = Path.cwd()` and writes numerous files directly under `OUT` without `authorized_root` or `check_output`. Invoking that script elsewhere remains an external-write path.

Consequently, the junction race is not the only residual declared at response line 47. The core public helpers still authorize arbitrary roots and arbitrary in-checkout overwrites.

**Resolution criterion:** bind all writers to one authenticated checkout identity; make `check_output`, `create_run`, environment capture, and runtime helpers enforce that identity internally; use explicit output subtrees and reject existing inputs; reject all colon/device/ADS and drive-relative forms; compare protected targets by file identity; and close or explicitly block the reparse-point check/use race.

### 3. HIGH — external runtime write: PARTIALLY CLOSED

**Relevant code:** `provenance/commands/task01/verify_runtime_paths.py:30-38,40-97,100-126,129-181`; `provenance/environment/runtime_path_report.json:24-141`; `provenance/incidents/INCIDENT-001.json:1-62`.

The remediation no longer imports the unguarded child into the real profile. It creates the profile fixture and its AppData/config parents before import, and the sandboxed child genuinely exercises Ultralytics' fallback behavior. The three recorded external paths remain present. Their sizes, mtimes, and SHA256 values match `INCIDENT-001`; all three preserved copies also match. The two AppData spellings canonicalize to the same redirected physical file, as the response itself describes as a real path and its redirected view. Targeted checks found no contemporaneous new matplotlib, torch, or numba cache outside the checkout; the existing `~/.matplotlib/fontlist-v390.json` predates this incident. The incident record is materially honest about the known writes and pending owner disposition.

The containment proof is still incomplete:

- The guarded child calls `lock_ultralytics` only after `from ultralytics import ...`; the committed report records `ultralytics_online_probe_at_import: true`. Integration settings are therefore not a pre-import network guard.
- Guarded mode checks only Ultralytics datasets, weights, runs, settings, and user-config path strings. It does not query or monitor effective torch, matplotlib, numba, pip, user-profile, or actual temp writes. `USERPROFILE`, `APPDATA`, and `LOCALAPPDATA` remain real in guarded mode. Environment-variable intent is not proof that no import-time writer used another sink.
- The parent first calls `configure_environment`, and children inherit its non-path isolation variables. The child does call `configure_environment` for path variables, but the fresh-start proof is partly launcher inheritance. On this venv `site.ENABLE_USER_SITE` was false even with `PYTHONNOUSERSITE` absent and `sys.flags.no_user_site == 0`.
- The unguarded sandbox report itself has `escaped.datasets_dir` pointing outside the checkout (`...\.worktrees\datasets`), yet lines 157-171 ignore `payload['escaped']` in that mode and the overall report is `PASS`. This directly contradicts the script docstring's “Any resolved path outside the workspace is a FAILURE in every mode” and response lines 23/101 (“PASS ... sin escapes”). See new finding N1.

The sandboxed unguarded mode remains a useful test of Ultralytics, not merely of a pre-populated fixture, but it is a hazard observation rather than containment proof. The missing and external guarded-entry tests do reject before scientific import.

**Resolution criterion:** keep the controlled profile negative test, but separate its expected hazard result from the containment gate; fail any unexplained escaped path; disable or explicitly authorize import-time network behavior before import; verify effective locations for every named runtime writer and temp facility; and use an OS-enforced/audited write boundary or before/after evidence capable of detecting paths beyond the hand-selected settings keys.

### 4. MEDIUM — operational error classification: CLOSED

**Relevant code:** `src/evaluation/provenance.py:63-68,189-204,368-376`; `tests/test_provenance_hardening.py:152-181`.

`InvalidInput` is now distinct from operational exceptions. `verify_sources` no longer catches `OSError`; a fresh `Path.stat -> PermissionError('ACL denied')` probe propagated rather than becoming a discrepancy, consistent with the stored `sha256 -> PermissionError` test. Output-write and other unexpected exceptions reach the traceback/exit-1 handler. Missing files and malformed row keys remain deliberately collected as source/input discrepancies. The `KeyError` arm encloses more code than ideal, but no current production helper inside that block raises `KeyError` except row lookup.

### 5. MEDIUM — total exit-2 contract for malformed input: PARTIALLY CLOSED

**Relevant code:** `src/evaluation/provenance.py:221-230,334-376`.

Fixed branches: a top-level JSON list used as `--root-mapping` now exits 2, and malformed JSON is translated to `InvalidInput`. `utf-8-sig` is appropriate for a BOM.

Fresh counterexamples:

- A non-UTF-8 executable used as `--source-manifest` raised `UnicodeDecodeError` with traceback and exit 1.
- `provenance/experiment_registry.csv` used as a manifest (missing `source_id`/`sha256` columns) raised uncaught `KeyError: 'source_id'` and exited 1.
- `csv.DictReader` silently collapsed a duplicate `logical_root` header; the resulting row passed schema, coverage, and verification with zero issues.
- A row whose header includes `local_absolute_path` but whose data line omits that final cell yields `None`. `require_schema` evaluates `str(None) == 'None'`, accepts it as nonblank, `validate_locations` skips the falsey declared value, and verification returned zero issues.

The claim that exit 2 is total is false.

**Resolution criterion:** validate both CSV header sequences before constructing rows (required, unique, exact policy), reject `None` cells and surplus cells, validate manifest and sidecar schemas separately, and translate decoding/CSV-format errors to `InvalidInput`/exit 2 while retaining operational read failures as exit 1.

### 6. MEDIUM — durable secret sanitization: PARTIALLY CLOSED

**Relevant code:** `src/evaluation/provenance.py:59-60,284-317`; `provenance/commands/task01/install_reconstructed.py:28-45,53-75,126-137`; `tests/test_provenance_hardening.py:215-237`.

Key-aware recursion, HTTP URL removal of userinfo/query, common Authorization/Bearer/Basic forms, and scheme-less proxy userinfo are real improvements. The checked-in pip download URLs have no userinfo/query, so no current credential leak was established.

Fresh probes show realistic unhandled shapes remain unchanged: `private_key`, `access_key_id`, `auth`, `Cookie: session=...`, and a structured pair `{'name': 'Authorization', 'value': 'Bearer abc'}`. AWS `Signature=...`, generic session/cookie values, generic private/access keys, and short bearer/basic values have the same gap. `run()` persists sanitized plain text, so split name/value structures and unrecognized keys can reach durable logs.

**Resolution criterion:** define a conservative key/header policy covering private/access/signing keys, auth/cookie/session values, split header records, and common cloud/pip proxy forms; test every durable writer, then scan exact generated artifacts with tests that report locations without echoing secret values.

### 7. MEDIUM — isolation and integrations: PARTIALLY CLOSED

**Relevant code:** `src/evaluation/provenance.py:27-43,121-161,320-331`; `provenance/commands/task01/verify_runtime_paths.py:64-96,129-177`; `tests/test_provenance_hardening.py:240-258`.

The five non-path variables are now compared, all ten listed Ultralytics settings are false after `lock_ultralytics`, and the current venv reports user-site disabled.

The process is still certifiable with an external import path. A fresh child launched with `PYTHONPATH=C:\Windows` retained `C:\Windows` in `sys.path`; `configure_environment` plus `verify_environment` returned success and `site.ENABLE_USER_SITE == False`. Neither `PYTHONPATH`/`sys.path` nor already injected modules are validated. On this venv the site check is false even without `PYTHONNOUSERSITE`, so it does not demonstrate that the late environment assignment caused startup isolation. Likewise, assigning `PYTHONDONTWRITEBYTECODE` after startup does not change the interpreter flag. Finally, the online probe occurs before settings are locked, and effective paths for the other named runtimes are not measured.

**Resolution criterion:** launch with startup flags/environment already fixed, validate `sys.path`, interpreter flags, and absence of pre-import scientific modules, and verify the other runtime directories. Apply any Ultralytics network policy before importing code that probes the network, or document and authorize that probe rather than describing the process as offline/fully disabled.

### 8. MEDIUM — sidecar schema enforcement: PARTIALLY CLOSED

**Relevant code:** `src/evaluation/provenance.py:57,207-218,233-281,344-360`; `tests/test_provenance_hardening.py:184-212`.

Dictionary keys, non-empty ordinary strings, lowercase SHA syntax, and ordinary `local_absolute_path` mismatches are now checked on the main CLI path. The current sidecar satisfies those checks.

The CSV representation is not validated. The fresh missing-final-cell probe above produced `local_absolute_path=None` and passed because line 215 stringifies `None`; duplicate and extra headers/columns are not rejected. The test removes the key entirely and therefore passes for the wrong reason relative to a real short CSV row. `validate_locations` itself also does not call `require_schema`, so standalone coverage calls can still omit the schema unless every caller remembers the precondition.

**Resolution criterion:** validate raw headers and row widths, require actual strings rather than `str(value)`, reject `None` and surplus fields, and make the coverage API enforce its own schema precondition.

### 9. MEDIUM — method tests and RED evidence: PARTIALLY CLOSED

**Relevant files:** `tests/test_provenance_hardening.py:1-262`; `provenance/commands/task01/red-hardening.log:1-20`; `provenance/commands/task01/green.log:1-34`.

The remediation adds 21 focused tests and the stored log records 28/28 passing. `red-hardening.log` is a genuine pre-implementation import failure for the new module surface, and the response correctly downgrades the unpreserved uniqueness RED rather than fabricating it.

Coverage is still materially short of the prior resolution criterion. There is no hardlink, symlink, junction-root, 8.3, SUBST/UNC, ADS/colon device, arbitrary caller root, arbitrary existing input overwrite, CSV header/row-width, non-UTF-8, real CLI exit, hostile `PYTHONPATH`, import-time writer, output-write failure, manifest-immutability, nonzero pip-check, or full runtime-containment test. The fake-checkout test positively codifies “any directory with a freeze-named file is authorized.” The missing-column test does not model `DictReader`'s `None` value. The suite therefore remains green with the reproduced defects above.

**Resolution criterion:** add the smallest Windows-host tests for each demonstrated bypass, exercise malformed inputs through the real CLI, preserve exact RED/GREEN evidence for new behavior, and avoid tests whose fixture bypasses the parser/OS behavior under test.

### 10. MEDIUM — required artifacts and registry linkage: PARTIALLY CLOSED

**Relevant files:** `provenance/environment/pip_config_redacted.txt`; `provenance/commands/task01/command.txt:1-19`; `provenance/artifact_registry.csv:102-106`.

The two named files now exist and ART-101..105 rows were added. ART-101, ART-102, ART-104, and ART-105 currently match their registered size and SHA256.

The registration is not consistent with the existing registry: every prior row has a nonblank `source_id`, `experiment_ids`, and `reproduced`, while all five new rows leave all three fields blank. No experiment registry link was added. `command.txt` omits `install_reconstructed.py`/environment creation and therefore cannot reproduce all TASK-01 artifacts despite calling itself self-contained. ART-103 is also factually stale; see N2.

**Resolution criterion:** use the registry's established nonblank semantics (or formally define a TASK-level replacement), link each artifact to its producing execution/command, regenerate hashes from exact committed bytes, validate the whole registry, and include the environment-capture command and required working-directory/startup isolation in the self-contained command record.

### 11. LOW — publication policy for machine identifiers: OPEN

**Relevant claim:** `reports/execution/task-01-review-response.md:81-85`.

The response states an intent to retain raw evidence privately and generate a projection in TASK-10, but no durable policy, classification, deterministic projection, or test was added in this diff. The raw evidence still contains the account name, package identifier, profile paths, and Ultralytics UUID. Deferring execution can be reasonable; calling the finding accepted is not closure.

**Resolution criterion:** record the private/public evidence policy in a durable authority, define exact retained/redacted fields, and test a deterministic publishable projection before publication.

## New findings

### N1. MEDIUM — runtime verifier reports PASS while its own result contains an escaped path

**Location:** `provenance/commands/task01/verify_runtime_paths.py:157-171`; `provenance/environment/runtime_path_report.json:101-141`; response lines 23 and 101.

**Failure scenario:** the sandboxed unguarded import resolves `datasets_dir` to `...\.worktrees\datasets`, outside the checkout. The child records this in `escaped`, but the parent only checks that settings/user-config follow the fixture and that selected strings do not start with three forbidden sinks. It ignores the recorded escape and emits `failures: []`, `status: PASS`. The docstring and response say every escape fails / there are no escapes.

**Resolution criterion:** classify the negative-mode escape as an explicit expected hazard separate from the containment result, or fail it; never describe the combined report as “no escapes.” Guarded containment must have its own complete writer evidence.

### N2. MEDIUM — ART-103's registered identity is false

**Location:** `provenance/artifact_registry.csv:104`.

**Failure scenario:** ART-103 records `size_bytes=902` and SHA256 `0c4a1a64f7adae96dc4edbd6d83f1e894f69fba4f6bc671e28733f6bf266b4d4`. The exact file in commit `3367672` and the clean worktree is 900 bytes with SHA256 `36d746868b58efb6596d84e21fc814f7153e6e4a21613208d415188f28dbdc71`. A consumer following the registry must reject the artifact.

**Resolution criterion:** regenerate the row from exact committed bytes and add a registry-wide verification check that rejects stale sizes/hashes and missing required linkage fields.

## Claims falsified

Commit `3367672` says the adversarial findings are closed, malformed-input exit 2 is total, every escape fails, and the 11,137-row report proves canonical uniqueness/full schema. The fresh hardlink, caller-root, ADS/device, malformed CSV/encoding, external `PYTHONPATH`, and registry-hash probes falsify those claims. The present sidecar's clean outcome is real but narrower: current bytes and current rows verified; the validator and evidence gate remain incomplete.

## Verdicts

**Frozen-brief compliance: FAIL / NOT COMPLIANT.** The immutable freeze is intact, and the present source set hashes cleanly, but canonical uniqueness, authenticated write containment, complete runtime-writer containment, total malformed-input handling, exact schema enforcement, and registry linkage/identity are not satisfied.

**Engineering quality: REJECT.** The remediation is directionally useful and honestly records the known incident, but its tests and reports certify properties the implementation does not enforce. The false ART-103 identity is itself a provenance failure.

**Open counts:** unresolved prior findings = **3 HIGH, 6 MEDIUM, 1 LOW**; new findings = **2 MEDIUM**. Gate-total findings listed here = **3 HIGH, 8 MEDIUM, 1 LOW**.

**TASK-01 may not pass its independent-review gate.**
