# TASK-05 independent methodological review — round 12

Date: 2026-09-28  
Reviewed repository state: `f03ad316aa167ae47a8d8e494359a9324bd3075b`  
Scope: prospective inference-approval review of the changes after `b259999b5b48673802b6f51190975a8ed3933769`. No research inference, Kaggle/network write, product-code fix, repository commit, push, or `.docx` access was performed. Mutable probes ran only in disposable exact-HEAD repositories and full environment copies under `C:\tmp`. The only worktree write made by this review is this report.

## Verdict

**DO NOT APPROVE inference for the proposed snapshot.**

The specific round-11 defect is closed. A copied `_distutils_hack` startup cache whose `RECORD` line remained `path,,`, whose genuine 16-byte header was retained, and whose body changed `csv.DictReader` was refused by the full environment gate. All requested round-7 through round-11 replays are now refused: checkout `PYTHONPATH`/`sitecustomize.py`, committed `{}` as the frozen config, the literal wrapper contract, lowercase and uppercase sourceless bytecode including metadata-spoofing variants, forged checkout `__pycache__`, both Git index flags for approval and an imported helper, embedded `csv` and `ultralytics` repositories/packages, and the recorded-empty-digest `_distutils_hack` cache.

The genuine approved `.venv` passes the new complete file/cache and loaded-module checks with unchanged runtime identity `f1a06a70e5af9e606618b4db5321f001ad4e905b3777f528d5b4d37465f9a2c2`. All 15 unique proposed snapshot files equal both their declared SHA256 and the committed `HEAD` blob. The named M1 verifier, threshold, snapshot, and Git-index closures remain closed. The clean frozen-command chain remains interface-compatible.

However, **NEW-HIGH-05 remains PARTIALLY CLOSED / OPEN** because a different local startup-path mechanism still accepts substituted code. An unrecorded `.venv\Scripts\python._pth` can replace the literal command's normal `sys.path` with an explicit list containing an external directory. The current runtime scan ignores the file because its suffix is `._pth`, and `check_startup` does not compare `sys.path` with the allowed checkout/base/venv roots or reject Windows `_pth` mode. An external `csv.py` was then loaded before `authority.py`, wrapped `DictReader` so `Costras` became `Saludable`, restored mutable `sys.base_prefix` to the recorded trusted interpreter path, and claimed the trusted stdlib `csv.py` as its origin, loader path, and `__file__`. The unchanged full gate passed, retained the approved runtime identity, and the substitution remained active after the gate.

This is within the stated trust model. The committed repository and recorded interpreter remain trusted. The counterexample does not require a custodian, signature, platform attestation, altered commit, rewritten checker, or code that disables the checker after it runs. It presents a local startup-configuration file and substituted module before inference; both remain present and are not refused.

**Open count: HIGH = 1; MEDIUM = 0.**

## Binding authority and review basis

Reviewed before implementation evidence:

- immutable `provenance/protocol_freeze.json` and `.md`;
- SPEC §§6, 7, 11, and 12;
- frozen plan TASK-05, including its literal commands;
- PROTOCOL-AMENDMENT-008 §§4 and 5.1;
- TASK-05 independent reviews rounds 6 through 11.

Amendment 008 §4 explicitly declares no independent custodian. This review therefore treats committed Git bytes and the recorded base interpreter as the root of trust. It asks whether present local untracked, modified, or substituted files can change the approved commands without refusal. It does not ask the controls to prove that a trusted committer could fabricate repository evidence.

## Post-round-11 delta and scope

`git log b259999..HEAD` contains two commits:

- `9909b6f feat(task05): toda caché del .venv, registrada o no (ronda 11)`;
- `f03ad31 docs(amendment-008): 5.1 responde a la ronda 11 e instantánea regenerada`.

The delta contains six files. Of the proposed snapshot files, only `src/evaluation/authority.py` changed. The following changed files are outside both `inference_approval.m1` and `.m2`: the amendment sidecar writer, Amendment 008 JSON/Markdown, the round-11 report, and `tests/test_authority_runtime.py`. No changed file is a `.docx`.

The authority change does three relevant things:

1. every current-interpreter `__pycache__` file under the whole `.venv` is compared with its source whether `RECORD` omits it, hashes it, or lists it with an empty digest;
2. every other code file must have a non-empty `RECORD` digest;
3. `check_loaded` checks both mutable `spec.cached` and the cache derived from the module source path.

Those changes close the round-11 cache route. They do not validate Windows `_pth` path configuration or the complete allowed `sys.path`.

## Fresh required verification

Because the managed process is owned by a different Windows identity from the linked worktree, the required modules ran in an owner-matched, LF-exact bundle clone at `f03ad316`, with `core.autocrlf=false` set before checkout and a junction to the unchanged approved `.venv`. Each module ran in its own interpreter process using the requested command form.

| Command | Fresh result |
|---|---:|
| `.\.venv\Scripts\python.exe -m unittest tests.test_evaluation` | 58 passed; exit 0; 138.186 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_intervals` | 32 passed; exit 0; 48.242 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_predict_model2` | 9 passed; exit 0; 12.175 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_authority_runtime` | 25 passed; exit 0; 19.971 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_kaggle_job` | 44 passed; exit 0; 0.596 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_verify_kaggle_run` | 14 passed; exit 0; 7.321 s |
| **Total** | **182 passed; 0 failures/errors; 226.491 s** |

A non-stubbed complete `check_environment`, followed by real torch/Ultralytics imports and `check_imported`, also passed in the exact-HEAD clone:

- runtime identity: `f1a06a70e5af9e606618b4db5321f001ad4e905b3777f528d5b4d37465f9a2c2`;
- torch: `.venv/Lib/site-packages/torch/__init__.py`;
- Ultralytics: `.venv/Lib/site-packages/ultralytics/__init__.py`;
- fresh bytecode: under `provenance/runtime_state/pycache/run-*`;
- fresh-bytecode children after normal exit: zero;
- elapsed time: 503.122 s.

This proves that the strengthened full-cache control accepts the unchanged approved environment. It does not cure the `_pth` path-injection route described below.

## Proposed snapshot against the real committed repository

For every path in Amendment 008 `inference_approval.m1` and `.m2`, the proposed SHA256 equals both the real worktree bytes and `git show HEAD:<path>` bytes. Every path is tracked and clean.

| Scope | Declared entries | Proposed = filesystem = `HEAD` | Result |
|---|---:|---:|---:|
| M1 | 12 | 12/12 | PASS |
| M2 | 7 | 7/7 | PASS |
| Unique paths | 15 | 15/15 | PASS |

Additional identity checks:

- `src/evaluation/authority.py`: `c5403b901bcbb253d72fb82350eb1df66770db318ec4d430f8b51a5ae626cc80`;
- `provenance/environment/inference_runtime.txt`: `f1a06a70e5af9e606618b4db5321f001ad4e905b3777f528d5b4d37465f9a2c2`;
- Amendment Markdown: declared and actual SHA256 `ce41988c378e527e8c1e31e8fc7d994a66f501fb1692d69bfa1b1b6f9de23f56`;
- immutable protocol-freeze JSON: `6d5aa3ff47cba97f8ecd0dd15683bb96f0d53146f3af1ce1e95bf24cec7cbc8b`.

## Requested round-7 through round-11 replay

Fifteen focused negative regressions ran verbosely in the disposable exact-HEAD clone and all passed in 21.245 s. The exact Git-index and full-environment variants were also replayed manually.

| Counterexample | Round-12 result | Fresh evidence |
|---|---:|---|
| Checkout `PYTHONPATH` plus untracked `sitecustomize.py` | REFUSED | Literal child regression reported the startup override/hook. |
| Committed `{}` at `configs/evaluation_frozen.json` | REFUSED | Producer regression stopped before run-directory creation or any test-byte read. |
| Literal M2 wrapper with actual `false` / `PROPOSED` amendment | REFUSED | Exit 2; concise `REJECTED:` message; no traceback; `EXP-R03` absent before and after. |
| Lowercase `csv.pyc` | REFUSED | Checkout-source and loaded sourceless-module regressions passed. |
| Lowercase spec-erasing `csv.pyc` | REFUSED | Literal substitute executed; loaded-module validation rejected no verified origin. |
| Uppercase `csv.PYC` | REFUSED | Case-normalized checkout scan rejected it. |
| Uppercase origin-spoofing `csv.PYC` | REFUSED | Loader-path cross-check exposed the actual checkout file. |
| Forged tracked-source `__pycache__` retaining the genuine header | REFUSED | Checkout scan and loaded-module validation both rejected a code object not compiled from its source; clearing `spec.cached` did not help. |
| Approval locally switched and hidden by `assume-unchanged` | REFUSED | `git status --short` was empty, working/HEAD blob IDs differed, and `approved_inference` rejected uncommitted authorities. |
| Approval locally switched and hidden by `skip-worktree` | REFUSED | Same result. |
| Imported `duplicate_structure` helper changed and hidden by `assume-unchanged` | REFUSED | The changed function returned `{'round12_substituted': True}`; source and complete environment gates reported both `flagged` and `modified`. |
| Same helper hidden by `skip-worktree` | REFUSED | Same result. |
| Embedded `csv/.git/` plus `csv/__init__.py` wrapper | REFUSED | Literal regression observed the altered row, then rejected `csv/__init__.py`. |
| Embedded `ultralytics/.git/` plus origin-spoofing package | REFUSED | `YOLO='checkout-substitute'` loaded and claimed the installed origin; source and environment gates rejected `ultralytics/__init__.py`. |
| Round-11 `_distutils_hack` cache listed as `path,,` | REFUSED | Exact full copied-`.venv` replay below. |

### Exact round-11 cache replay

A full 1,283,425,675-byte copy of the approved `.venv` was placed in a disposable exact-HEAD clone. Only `_distutils_hack/__pycache__/__init__.cpython-312.pyc` was changed:

- its `RECORD` line remained `_distutils_hack/__pycache__/__init__.cpython-312.pyc,,`;
- its genuine 16-byte header remained unchanged;
- its source remained unchanged;
- the committed runtime table remained unchanged;
- its body wrapped `csv.DictReader`, changing `Costras` to `Saludable` at interpreter startup.

Fresh-process evidence before the gate was `CACHE_EXECUTED=True` and `ROW_BEFORE_GATE={'class_name': 'Saludable'}`. The full gate then refused:

```text
installed files differ from their RECORD: ['...\\_distutils_hack\\__pycache__\\__init__.cpython-312.pyc']
```

The replay exited as expected after 496.631 s. This closes the specific round-11 route and proves that a `path,,` line no longer bypasses source-compilation validation.

## NEW-HIGH-05 disposition: PARTIALLY CLOSED, still OPEN

### Closed portions

- Every required round-7 through round-11 counterexample above is now refused.
- All 9,018 approved `.venv` caches are checked without using empty-digest `RECORD` membership as verification.
- Empty-digest non-cache code is refused.
- A loaded module cannot hide a forged ordinary derived cache merely by clearing `spec.cached`.
- The clean approved `.venv` passes with the unchanged committed runtime identity.

### Surviving Windows `_pth` startup-path route

**Severity:** HIGH  
**Location:** `src/evaluation/authority.py:46-53,145-160,271-304,330-368,443-455`; consumers at `src/evaluation/evaluate.py:15,660`, `src/evaluation/predict_model2.py:11,107`, `src/statistics/intervals.py:12,433`, and `provenance/commands/task04/verify_kaggle_run.py:21,213`.

In a full disposable copy whose 9,018 ordinary caches were restored byte-for-byte from the approved `.venv`:

1. An unrecorded `.venv\Scripts\python._pth` listed the normal trusted paths plus one external directory first, then `import site`.
2. Windows honored that file for the unchanged literal `.venv\Scripts\python.exe` command. The external directory appeared in `sys.path`.
3. The external directory contained `csv.py`, based on the trusted stdlib implementation. It wrapped only `DictReader`, changing `class_name=Costras` to `Saludable`.
4. The module set `sys.base_prefix`/`sys.base_exec_prefix` to the known recorded base-interpreter root and claimed the trusted stdlib `csv.py` as `__spec__.origin`, loader path, and `__file__`. It did not alter an authority function, snapshot, Git state, `RECORD`, or runtime table.
5. `check_startup` did not reject `_pth` mode or the extra path. `verify_installed` ignored `python._pth` because `Path('python._pth').suffix.lower()` is `._pth`, not `.pth` and not in `CODE_SUFFIXES`. `check_loaded` trusted mutable `sys.base_prefix` and the spoofed module metadata.
6. The complete unchanged `check_environment` passed in 226.540 s with runtime identity `f1a06a70e5af9e606618b4db5321f001ad4e905b3777f528d5b4d37465f9a2c2`.
7. The altered row was still `{'class_name': 'Saludable'}` after the gate.

Observed result:

```text
ORDINARY_CACHES=9018
ORIGINAL_BASE_PREFIX='...\\.venv\\Scripts'
CLAIMED_BASE_PREFIX='C:\\Users\\junio\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python'
MAL_ON_PATH=True
ROW_BEFORE_GATE={'class_name': 'Saludable'}
PTH_CSV_EXECUTED=True
ENVIRONMENT_PASSED
RUNTIME_IDENTITY=f1a06a70e5af9e606618b4db5321f001ad4e905b3777f528d5b4d37465f9a2c2
ROW_AFTER_GATE={'class_name': 'Saludable'}
```

**sys.path location/mechanism:** Windows `python._pth` path initialization beside the `.venv` launcher adds an external directory before the trusted base library. The substituted `csv.py` is outside the checkout, recorded base library, `.venv` root, and site-packages; the unrecorded path-config file that makes it reachable is inside `.venv\Scripts` but is not classified or refused.

**Consequence:** every frozen command imports `csv`; the accepted wrapper can alter manifest rows, attempt/selection records, truth labels, group IDs, prediction rows, and interval inputs while all reviewed repository hashes, installed-file hashes, and runtime identity remain approved. The demonstrated label substitution survives the gate and can change EXP-V01, the operating-point freeze, EXP-R02, M1 intervals, EXP-R03, primary M2 intervals, and M2 sensitivity.

**Resolution criterion:** before any test read or output creation, reject any unapproved Windows `*._pth`/`python._pth` path-configuration file associated with the `.venv` launcher, validate the resolved `sys.path` roots and order against the literal-command allowlist, and anchor the trusted base-library root to recorded interpreter evidence rather than mutable `sys.base_prefix`. Add a literal child-process negative with `.venv\Scripts\python._pth` plus an external origin-spoofing `csv.py`; it must exit 2 before scientific input reads or output creation. Re-run the full approved-`.venv` gate and independent snapshot review. No custodian, signature, or platform attestation is required.

This is new round-12 evidence for the same unresolved NEW-HIGH-05 root cause—present substituted runtime code is accepted—so it is not double-counted as a second HIGH ID.

## M1 closures and real EXP-R01 evidence

The named M1 closures still hold on their stated causes:

| Finding | Round-12 status | Fresh evidence |
|---|---:|---|
| HIGH-04 — attempt root used an unrooted verifier | CLOSED | `verify_kaggle_run.py` remains in the exact M1 snapshot; real reconciliation re-derived byte-for-byte. |
| NEW-HIGH-01 — threshold authentication depended on HIGH-04 | CLOSED | The freezer still reaches validation through the definitive reconciled attempt; the ordered frozen-command regression passed. |
| NEW-HIGH-03 — approval not bound to reviewed authorities | CLOSED | All 12 M1 entries equal proposed, filesystem, and committed `HEAD` bytes. |
| NEW-HIGH-06 — EXP-R03 could run before approval | CLOSED | Literal actual-state wrapper exits 2 and creates no run directory. |
| NEW-HIGH-07 — index flags hid local approval/helper changes | CLOSED | Exact `assume-unchanged` and `skip-worktree` replays for approval and the imported helper were refused while Git status was empty. |

Read-only pure recomputation on the real repository confirmed:

- `reconciliation.json` equals the recomputation byte-for-byte;
- the sole `attempts.jsonl` entry equals the recomputed definitive entry;
- `selection_record.json` equals the recomputed seal byte-for-byte;
- 552 train/validation files verify;
- selected epoch `91`;
- fitness `0.760868639693682`;
- selected checkpoint SHA256 `0648da3f3641e3cdb5a1908a092ba892548942836a249bb3b39667f9ae8e8125`;
- selection-record SHA256 `4a67bdca43a1c6a782dc6bb172702fcb36ebfcbe9caaa4c73f01808bcb98706c`;
- manifest SHA256 `dd9431dd7bbc00c6117baf6a0f6cf49eff8bc55f144016b4a98dbdea049ecf5f`;
- kernel version `1`.

These facts keep the named M1 defects closed. They do not make M1 inference approvable while the shared startup/runtime gate accepts the `_pth` substitution.

## Frozen command-sequence compatibility

The real amendment remains `inference_approved=false` and `inference_approval.state=PROPOSED`. No approval commit, real scientific inference, or Kaggle write was authorized or performed.

Conditional clean-path compatibility was confirmed in committed disposable fixtures using the real current code and the same approved `.venv`. A focused five-test chain passed in 65.679 s:

- EXP-V01 scoring, operating-point freeze, EXP-R02 scoring, and M1 intervals ran in order through the literal plan interfaces;
- the M2 dispatcher selected the canonical M2 manifest, ART-002, committed frozen config, and `EXP-R03` path;
- the prescribed committed EXP-R03 bundle, approved producer, and M2 snapshot were authenticated;
- primary M2 intervals selected the image-weighted path;
- M2 sensitivity wrote its JSON/CSV, confusion, shared-draw, and report outputs.

The full intervals module separately passed the seed-42, 2,000-shared-draw determinism and paired-scheme checks. The genuine approved `.venv` passed the complete strengthened runtime gate. Since only `authority.py` changed among snapshot sources after round 11, no new clean-path parser, path, output-order, promotion, or bootstrap incompatibility was observed.

Therefore, if a legitimate later commit changes only `inference_approved` and `inference_approval.state` to approved for these exact snapshot bytes, the clean frozen sequence remains runnable in order:

`EXP-V01 → operating-point freeze → EXP-R02 → M1 intervals → EXP-R03 → three-file promotion → primary M2 intervals → M2 sensitivity`.

That compatibility result is not approval. The same environment gate accepts the `_pth` counterexample, so the clean path cannot establish provenance exclusivity.

## Approval decision by step

| Step | Decision | Reason |
|---|---:|---|
| EXP-V01 | **NO** | External `csv.py` admitted through `python._pth` can alter validation manifests and reconstructed predictions. |
| Operating-point freeze | **NO** | Altered validation rows can change F2 inputs and the selected threshold. |
| EXP-R02 | **NO** | The same accepted parser can alter test reconstruction and scoring. |
| M1 intervals | **NO** | Prediction/group CSV inputs are consumed through the accepted wrapper. |
| EXP-R03 | **NO** | M2 manifest truth and records can be changed while runtime identity remains approved. |
| Primary M2 intervals | **NO** | Promoted predictions and manifest groups are parsed in the accepted substituted process. |
| M2 sensitivity | **NO** | Class labels, hashes, groups, clusters, and prediction rows can be changed without a refused file. |

## Final findings

| ID | Severity | Status | Blocks |
|---|---:|---|---|
| HIGH-04 | HIGH | CLOSED | — |
| NEW-HIGH-01 | HIGH | CLOSED | — |
| NEW-HIGH-03 | HIGH | CLOSED | — |
| NEW-HIGH-05 | HIGH | **PARTIALLY CLOSED (OPEN)** | All M1/M2 inference and interval commands; combined approval |
| NEW-HIGH-06 | HIGH | CLOSED | — |
| NEW-HIGH-07 | HIGH | CLOSED | — |
| NEW-LOW-01 | LOW | CLOSED | — |
| NEW-LOW-02 | LOW | CLOSED | — |

**Open count: HIGH = 1; MEDIUM = 0. Overall verdict: DO NOT APPROVE inference for the proposed snapshot.**
