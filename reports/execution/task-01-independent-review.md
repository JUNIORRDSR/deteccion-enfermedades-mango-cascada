# TASK-01 independent adversarial review

**Diff reviewed:** `bead360..675c49c`  
**Authorities:** frozen TASK-01 brief; design specification sections 4 and 11; immutable `provenance/protocol_freeze.json`  
**Review posture:** implementation-report statements were treated as claims to falsify. Later commits `4b198bd` and `6ab97f7` are outside the reviewed diff.

The reviewed diff does not change `provenance/protocol_freeze.json` or the original `provenance/source_manifest.csv`. An independent read-only scan of the committed sidecar found 11,137 populated rows, no duplicate raw `(logical_root, logical_path)` pairs, no duplicate resolved targets, and no mismatch between the resolved path and `local_absolute_path`. The committed `install_report.json` contains 41 download URLs and none contains userinfo, a query string, or a local machine path. These are observations about the present artifacts, not proof that the implemented validators enforce the contracts below.

## Open findings

### 1. HIGH — uniqueness is checked on raw CSV spelling, not on the resolved file

**Location:** `src/evaluation/provenance.py:74-95,130-141`; `tests/test_provenance.py:61-65`; `reports/execution/task-01-implementation.md:14-16,31`

**Concrete failure scenario:** Inputs are a two-row manifest with distinct `SRC-1`/`SRC-2` and the same expected hash, plus sidecar rows `(legacy_corpus, d/a.bin)` and `(legacy_corpus, d/./a.bin)`. `validate_locations` compares the raw strings and accepts both; `_relative_path` normalizes both to the same path; `resolve_source` hashes the same physical file twice; the CLI can report `discrepancies=0`. The same bypass is available on Windows with `/` versus `\`, case variants, trailing dot/space aliases, an 8.3 short name versus its long name, or two logical-root names mapped to the same directory. A fresh in-memory probe confirmed that `d/a.bin` and `d/./a.bin` are accepted while normalizing to the same path.

**Wrong behaviour:** `reports/execution/task-01-implementation.md:31` says the zero-discrepancy run proves unique `SRC -> file` correspondence, but the active check proves only uniqueness of raw CSV pairs. The present sidecar happens to be unique under an independent canonical scan; the program does not establish that fact.

**Resolution criterion:** Resolve every sidecar row through the supplied root mapping first, canonicalize with Windows case/alias semantics, and reject two source IDs that identify the same resolved file. Cover slash, dot-segment, case, trailing-dot/space, 8.3, junction/symlink, and aliased-root cases with RED/GREEN evidence. The verification report must identify the canonical uniqueness method it actually ran.

### 2. HIGH — write authorization and immutable-input protection are caller-controlled

**Location:** `src/evaluation/provenance.py:31-57,162-183`; `src/evaluation/provenance.py:38-39` (`create_run`)

**Concrete failure scenarios:**

- With otherwise valid TASK-01 inputs, pass `--out provenance/protocol_freeze.json` (or `provenance/source_manifest.csv`). `check_output` accepts the path because it is below the current directory, and `write_text` overwrites the frozen protocol or original input before returning success.
- Invoke the module from `C:\Temp` using the script's absolute path and absolute input arguments. `main` treats the arbitrary current directory as the authorized root; `configure_environment` creates `C:\Temp\provenance\runtime_state`, and an ordinary relative `--out` is written outside the approved checkout.
- Call `create_run(Path('C:/outside/run'))`; it creates that directory without any containment check.
- On this Windows host, a fresh probe showed that `check_output(checkout, checkout / 'NUL')` accepts the reserved device. Using `--out NUL` can discard the durable report while the CLI prints success. Trailing-dot/space and 8.3 aliases can likewise name a different existing sink than the spelling that was checked. Because `resolve(strict=False)` checks a non-existent path before `mkdir`/`write_text`, replacing an intermediate directory with a junction after the check also creates a check/use race.

**Wrong behaviour:** The global frozen rule requires every path/output consumer to reject writes outside the authorized checkout and modification of inputs. The current code establishes only “relative to a caller-selected root” and does not protect the freeze, manifests, source/config files, or durable-output semantics. Although the reviewed diff itself leaves the freeze unchanged, running the delivered CLI can destroy it.

**Resolution criterion:** Authenticate the root as the active authorized checkout, restrict each writer to an approved output subtree, reject all input/protected paths and aliases, make `create_run` take and enforce an authorized root, reject Windows device/drive-relative/trailing-dot/space forms, and close the junction/symlink check-use gap with an atomic/no-follow strategy or an immediately revalidated opened handle. Add tests for protected-file collision and Windows aliases.

### 3. HIGH — the runtime-path verifier performs the forbidden external write and calls it PASS

**Location:** `provenance/commands/task01/verify_runtime_paths.py:40-49,67-80,92-105`; `provenance/environment/runtime_path_report.json:55-87`; `reports/execution/task-01-implementation.md:53-62`

**Concrete failure scenario:** Run the committed verifier. Its `import_unguarded` child deliberately imports Ultralytics with `YOLO_CONFIG_DIR` stripped and then unconditionally calls `SETTINGS.update`. Ultralytics selects `%APPDATA%\Ultralytics\settings.json`. Lines 97-99 add a failure only when the escape *does not* occur, so the observed external write produces `failures: []`, status `PASS`, and exit 0.

**Wrong behaviour:** The committed report records the escaped settings file at `C:\Users\junio\AppData\Roaming\Ultralytics\settings.json` (resolved by the sandbox to the APPDATA package cache). Read-only inspection confirmed that the file already exists outside the workspace and contains the workspace paths and an Ultralytics machine UUID. Thus TASK-01 itself caused/updated exactly the external state that the frozen brief says must block the process and be corrected before scientific use. Documenting the hazard is not containment, and future-CLI discipline is not programmatic enforcement.

**Resolution criterion:** The verifier must never import into an uncontrolled profile. It must either prove the pre-import guard without executing an unsafe import or redirect the entire child profile into a controlled workspace fixture. Any detected external writer must make the gate fail. Preserve evidence of, and obtain an owner-approved disposition for, the already-created APPDATA file; then demonstrate in a new process that all effective runtime writers remain inside the checkout and that an unguarded entrypoint is rejected before import.

### 4. MEDIUM — unexpected I/O failures are converted into source discrepancies and invalid-input exit 2

**Location:** `src/evaluation/provenance.py:98-112,188-193`

**Concrete failure scenario:** A source exists and has the expected row, but hashing raises `PermissionError` because of an ACL, sharing violation, disconnected volume, or storage fault. `verify_sources` catches every `OSError` and returns `{'source_id': ..., 'error': ...}`. A fresh mock probe confirmed that a simulated `PermissionError('I/O denial')` is returned as a discrepancy. At the outer level, every `OSError`, including output disk-full or permission failures, is printed without traceback and mapped to exit 2.

**Wrong behaviour:** Operational failures are reported as invalid scientific input/source mismatch. This loses the traceback and violates the frozen CLI distinction: 2 is for invalid input or a missing scientific dependency, while execution failures retain traceback and their real exit status.

**Resolution criterion:** Define a narrow validation exception hierarchy. Catch only expected invalid-input cases (with an explicit policy for a genuinely missing source), let unexpected I/O/runtime errors propagate with traceback/non-2 status, and add tests for permission/read failure and output-write failure.

### 5. MEDIUM — the CLI exit-code contract is not total for malformed input

**Location:** `src/evaluation/provenance.py:175-176,188-193`

**Concrete failure scenario:** Supply a valid JSON file whose top level is a list as `--root-mapping` (the existing `provenance/environment/packages.json` suffices). `roots['revision'] = ...` raises uncaught `TypeError`. A fresh non-writing invocation observed a traceback and exit 1.

**Wrong behaviour:** This is malformed input, but it does not produce the required exit 2. Similar wrong JSON types can take the same uncaught path.

**Resolution criterion:** Validate the complete JSON/CSV schema and value types before use, translate every invalid-input branch to one documented input exception/exit 2, and exercise each branch through the real CLI in tests.

### 6. MEDIUM — redaction is input-contingent rather than contract-enforcing

**Location:** `src/evaluation/provenance.py:144-159`; `provenance/commands/task01/install_reconstructed.py:38-45,52-56,125-136`; `tests/test_provenance.py:67-71`

**Concrete failure scenario:** Set `PIP_PROXY=alice:secret@proxy.example:8080`, or pass text containing `Authorization: Bearer topsecret` or JSON `{"password":"hunter2"}`. `install_reconstructed.py` persists all `PIP_*` variables after calling `sanitize_text`; fresh probes showed all three strings remain unchanged. The recursive `scrub` also loses dictionary-key context, so a secret stored under a key such as `password` is sanitized only as an unlabelled scalar value.

**Wrong behaviour:** Credentials can be committed to `environment_whitelist.json`, pip logs, or a future install report even though `reports/execution/task-01-implementation.md:35` claims credentials and tokens are eliminated. The single test exercises only an HTTP URL through `redact_url`; it does not test `sanitize_text` or structured secret fields. No credential was found in the currently committed `install_report.json`, but that clean result is accidental with respect to these inputs.

**Resolution criterion:** Use key-aware structured scrubbing plus explicit handling for authorization headers, bearer/basic credentials, proxy/userinfo forms with and without a scheme, sensitive query parameters, and common token/key names. Keep the allowed host information. Add adversarial tests and a final secret scan of every durable environment artifact.

### 7. MEDIUM — environment verification does not enforce the claimed isolation or disable all integrations

**Location:** `src/evaluation/provenance.py:42-71`; `provenance/commands/task01/verify_runtime_paths.py:40-62,92-101`; `reports/execution/task-01-implementation.md:35,59-62`

**Concrete failure scenarios:**

- Start a future CLI in a Python configuration where a user-site or injected path is already enabled. `configure_environment` sets `PYTHONNOUSERSITE` and `PYTHONDONTWRITEBYTECODE` only after interpreter startup; those environment assignments do not retroactively remove an existing user site from `sys.path` or change Python's startup flags. `verify_environment` checks only the ten path variables and still passes.
- After configuration, change `WANDB_MODE`, `COMET_MODE`, `PYTHONNOUSERSITE`, or another non-path isolation variable. `verify_environment` does not inspect it and still passes.
- In the guarded Ultralytics child, `SETTINGS.update` disables only `sync`/API key and moves three directories. The effective settings observed on disk still have `clearml`, `comet`, `dvc`, `hub`, `mlflow`, `neptune`, and `raytune` enabled; the committed verifier asserts only `sync is False`.

**Wrong behaviour:** A process can be labelled isolated while imports or integrations remain externally influenced. This does not meet the frozen requirement to initialize/verify isolation before scientific imports and explicitly disable remote integrations.

**Resolution criterion:** Enforce startup isolation in the launcher or explicitly validate/repair `sys.path`, `site.ENABLE_USER_SITE`, and relevant interpreter flags before scientific imports; verify exact values for every isolation/device/thread variable; explicitly disable all applicable Ultralytics integrations; and test the behaviour in a genuinely fresh process with hostile inherited settings.

### 8. MEDIUM — sidecar coverage does not validate the required reference schema

**Location:** `src/evaluation/provenance.py:98-141`; `reports/execution/task-01-implementation.md:14,31`

**Concrete failure scenario:** Give `validate_locations` one manifest row and a matching sidecar row containing `source_id`, `logical_root`, `logical_path`, and `sha256`, but omit `local_absolute_path`. With roots supplied, `verify_sources` never reads that field. A fresh read-only probe passed validation and returned `[]` discrepancies.

**Wrong behaviour:** The CLI can report complete, zero-discrepancy coverage even though a field required for every new reference by the frozen brief is absent or false. `local_absolute_path` is neither required nor checked against the resolved target. Rows with a missing/blank `logical_path` are *not* a zero-discrepancy CLI loophole—the later resolver records a `KeyError`/invalid path and returns 2—but `validate_locations` itself silently skips them, so its standalone uniqueness claim is incomplete.

**Resolution criterion:** Validate an exact required sidecar schema, non-empty values, hash syntax, allowed logical roots, and consistency of `local_absolute_path` with the resolved target before coverage/uniqueness is declared. Test missing, blank, extra, and inconsistent fields through the CLI.

### 9. MEDIUM — the passing suite does not test the required methods, and the claimed uniqueness RED is not preserved

**Location:** `tests/test_provenance.py:18-103`; `provenance/commands/task01/red.log`; `provenance/commands/task01/red-environment.log`; `provenance/commands/task01/green-initial.log`; `reports/execution/task-01-implementation.md:10,21-31`

**Concrete failure scenario:** Keep the discovered defects: raw-string uniqueness, missing `local_absolute_path`, invalid mapping exit 1, broad `OSError` swallowing, `NUL` output, and incomplete sanitization. All seven committed unit tests can still pass because none exercises those branches. The modified-file assertion checks only `len(...) == 1`, no successful non-empty verification proves that zero discrepancies is distinct from an empty manifest, no test covers a non-zero `pip check`, no test preserves manifest bytes across resolution, and no CLI test covers exit codes.

**Wrong behaviour:** GREEN is compatible with failure of several frozen methods. The stored `red.log` is a module import failure, `red-environment.log` is the TEMP-policy RED, and `green-initial.log` fails an `SRC-9` expectation; none records the claimed `test_two_ids_cannot_map_one_logical_file` / `ValueError not raised` RED from implementation-report line 10. The final GREEN proves only the final seven examples, not the narrated RED/GREEN history for the resumed check.

**Resolution criterion:** Add method-level tests for every frozen negative and positive case, including canonical Windows aliases, protected outputs, schema completeness, successful non-empty verification, manifest immutability, sanitizer adversaries, pip-check blocking, runtime containment, and real CLI exits. Preserve the exact uniqueness RED and subsequent GREEN command/stdout/stderr/exit evidence; otherwise downgrade the TDD claim to unverified history.

### 10. MEDIUM — mandated provenance deliverables and registry linkage are incomplete

**Location:** diff file list for `bead360..675c49c`; `provenance/environment/identity.json:16-75`; `provenance/commands/task01/`; `reports/execution/task-01-implementation.md:37-41`

**Concrete failure scenario:** A new researcher checks out `675c49c` and follows the frozen TASK-01 artifact names and registry links. There is no `provenance/environment/pip_config_redacted.txt`, no self-contained `command.txt` under `provenance/commands/task01/`, and neither `provenance/experiment_registry.csv` nor `provenance/artifact_registry.csv` changed in the reviewed diff. `identity.json` records subprocess argument strings but not the top-level capture/verification commands with their required working directory, and the new environment/source-verification artifacts are not linked from a registry.

**Wrong behaviour:** The explicit TASK-01 file/update contract and section 4.3 linkage contract are not met. The split debug/list pip files are useful, but they do not make the required stable artifact path exist; prose in the implementation report is not a registry or a self-contained execution record.

**Resolution criterion:** Produce the exact mandated artifact (or an approved frozen-protocol amendment defining its replacement), preserve self-contained top-level commands with absolute executable/workdir plus stdout/stderr/exit status, and update the designated registries to link the reconstructed environment and verification artifacts without rewriting original manifests.

### 11. LOW — tracked environment evidence exposes machine identifiers without a publication policy

**Location:** `provenance/environment/identity.json:4-5,18-72`; `provenance/environment/environment_whitelist.json:2-11`; `provenance/environment/runtime_path_report.json:2-3,58,69-72`

**Concrete failure scenario:** Publish `provenance/environment/` as journal supplementary material. The files disclose the Windows account name `junio`, the full workstation layout, and the sandbox application package identifier `Claude_pzs8sxrjxfjjc` embedded in the resolved APPDATA path.

**Wrong behaviour:** These are not credentials, and some absolute-path/executable evidence is explicitly required by the frozen protocol, but the current redaction functions do not distinguish required reproducibility metadata from unnecessary machine/application identifiers. The repository has no stated public/private projection for this evidence.

**Resolution criterion:** Define and test a publication policy: retain hash-linked raw evidence privately when required, while generating a deterministic publishable projection that replaces account/application-specific path components without removing OS/build, executable version, host/index, or other scientifically necessary fields.

## Explicit verdicts

**Frozen-brief compliance verdict: FAIL / NOT COMPLIANT.** TASK-01 must not pass its independent-review gate. The source-identity proof is not canonical, protected inputs and authorized-root writes are not enforced, the runtime verifier performs an acknowledged outside-workspace write while reporting PASS, and multiple frozen test/evidence deliverables are absent.

**Engineering and scientific-quality verdict: REJECT IN CURRENT FORM.** The present 11,137-row sidecar and install report show useful observed state, but the software can certify the wrong source mapping, misclassify runtime failures, leak future secrets, and call a containment violation successful. Those defects make the current “complete and green” and “scientific use allowed” states unsafe as gate evidence.

**Open finding count: 3 HIGH, 7 MEDIUM, 1 LOW.** All 3 HIGH and all 7 MEDIUM findings remain open.
