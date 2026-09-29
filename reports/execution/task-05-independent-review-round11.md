# TASK-05 independent methodological review — round 11

Date: 2026-09-28  
Reviewed repository state: `b259999b5b48673802b6f51190975a8ed3933769`  
Scope: prospective inference-approval review of the changes after `4c87de866c082565fa124ec813b6079d92255f7a`. No research inference, Kaggle call, network write, product-code fix, commit, push, or `.docx` access was performed. Mutable probes ran only in disposable repositories and environment copies under the process temporary directory. The only persistent worktree write made by this review is this report.

## Verdict

**DO NOT APPROVE inference for the proposed snapshot.** The round-11 checkout walk closes the round-10 embedded-repository route. The requested round-7 through round-10 counterexamples are now refused: checkout `PYTHONPATH`/`sitecustomize.py`, committed `{}` as the frozen config, lowercase and uppercase sourceless bytecode including metadata-spoofing variants, forged checkout `__pycache__`, both Git index flags, the modified tracked helper, the embedded `csv` package, and the embedded `ultralytics` package. The literal M2 wrapper also refuses the still-unapproved amendment with exit 2 and creates no run directory.

**NEW-HIGH-05 is PARTIALLY CLOSED and remains OPEN.** The new whole-`.venv` verification does not inspect a cache if it is already listed in a distribution `RECORD` with an empty digest. The approved environment contains 9,018 `__pycache__` files; 9,010 are listed in `RECORD` as `path,,`. Those 9,010 caches bypass the new source-compilation comparison. In a full disposable copy of the approved `.venv`, I replaced the body of the recorded `_distutils_hack/__pycache__/__init__.cpython-312.pyc`, retained its genuine 16-byte header, and left its source and `RECORD` unchanged. Python loaded that cache automatically through the recorded `distutils-precedence.pth`. It wrapped `csv.DictReader`, changed `Costras` to `Saludable`, and passed the complete `check_environment()` and `check_loaded()` gates with the approved runtime identity `f1a06a70…f9a2c2`.

The counterexample did not change or disable an authority function. It is a present substituted package cache which the controls claim to compare with its source but do not. Its only metadata change was to report the recorded source as `spec.cached`, analogous to the origin/loader/file spoofing exercised in earlier rounds. The scientific substitution remained active after the gate.

**Open count: HIGH = 1; MEDIUM = 0.**

## Binding authority and trust model

Reviewed before implementation evidence:

- immutable `provenance/protocol_freeze.json` and `.md`;
- SPEC §§6, 7, 11, and 12;
- frozen plan TASK-05 and its literal commands;
- PROTOCOL-AMENDMENT-008 §§4 and 5.1;
- TASK-05 independent reviews rounds 6 through 10.

Amendment 008 §4 declares that there is no independent custodian. This review treats the committed Git repository and recorded base interpreter as the root of trust. It does not require signatures, platform attestation, or resistance to code that deliberately rewrites the checker. The surviving route is narrower: a local `.venv` code file is present before inference, is not byte-equal to its source, and is not refused by the file-presence/runtime-origin controls that are intended to authenticate it.

## Post-round-10 delta and proposed snapshot

`git log 4c87de8..HEAD` contains seven commits:

- `ad8d410 feat(task05): el checkout se recorre en disco (ronda 10)`;
- `19491c8 feat(task05): todo el .venv sin código sin registrar`;
- `e7ed1cb docs(amendment-008): 5.1 responde a la ronda 10 e instantánea regenerada`;
- `d3ca4b2 feat(task05): tabla de RECORD comprometida y cachés del .venv`;
- `8384b22 docs(amendment-008): instantánea con inference_runtime.txt`;
- `935c247 fix(task05): el .venv puede ser una unión; sys.prefix lo fija`;
- `b259999 docs(amendment-008): instantánea regenerada`.

The delta has 11 files. Of paths already present in the round-10 inference snapshots, only `src/evaluation/authority.py` changed. The new `provenance/environment/inference_runtime.txt` was added to both scopes. The other changed implementation, test, report, writer, and amendment files are not entries in `inference_approval.m1` or `.m2`; the amendment JSON is separately required to be committed and unmodified. No changed file is a `.docx`.

Every proposed SHA256 equals the real worktree SHA256, and each working Git blob equals `HEAD:<path>`:

| Scope | Declared entries | Proposed = filesystem = `HEAD` | Result |
|---|---:|---:|---:|
| M1 | 12 | 12/12 | PASS |
| M2 | 7 | 7/7 | PASS |
| Unique paths | 15 | 15/15 | PASS |

Key identities:

- `src/evaluation/authority.py`: `a46aee13f07e367e0c0241bdb08e15ff3bc92a2f096270d750df92720e158146`;
- `provenance/environment/inference_runtime.txt`: `f1a06a70e5af9e606618b4db5321f001ad4e905b3777f528d5b4d37465f9a2c2`;
- protocol freeze JSON: `6d5aa3ff47cba97f8ecd0dd15683bb96f0d53146f3af1ce1e95bf24cec7cbc8b`.

## Fresh verification

### Required isolated modules

The managed process runs under a different Windows identity from the linked-worktree owner. I therefore created an owner-matched, LF-exact bundle clone at `b259999`, with `core.autocrlf=false` applied before checkout and a junction to the approved `.venv`. The clone was clean, and its protocol-freeze hash was `6d5aa3ff…cbc8b`. Each required module ran in its own Python process:

| Command | Fresh result |
|---|---:|
| `.\.venv\Scripts\python.exe -m unittest tests.test_evaluation` | 58 passed; exit 0; 178.228 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_intervals` | 32 passed; exit 0; 43.655 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_predict_model2` | 9 passed; exit 0; 12.124 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_authority_runtime` | 24 passed; exit 0; 25.065 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_kaggle_job` | 44 passed; exit 0; 0.124 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_verify_kaggle_run` | 14 passed; exit 0; 7.441 s |
| **Total** | **181 passed; 0 failures/errors** |

The approved `.venv` also passed a non-stubbed complete environment check and post-import check in 376.146 s:

- runtime identity `f1a06a70e5af9e606618b4db5321f001ad4e905b3777f528d5b4d37465f9a2c2`;
- torch from `Lib/site-packages/torch/__init__.py`;
- Ultralytics from `Lib/site-packages/ultralytics/__init__.py`;
- fresh bytecode under `provenance/runtime_state/pycache/run-*`;
- zero children under the bytecode parent after normal process exit.

This clean pass establishes compatibility with the approved environment. It does not distinguish that environment from the substituted-cache copy described below, which produced the same identity and also passed.

### Requested round-7 through round-10 counterexample replay

| Counterexample | Result | Fresh evidence |
|---|---:|---|
| Checkout `PYTHONPATH` plus untracked `sitecustomize.py` preloading Ultralytics | REFUSED | The literal child regression passed; `check_startup` reported the startup override and hook. |
| Committed `{}` at `configs/evaluation_frozen.json` | REFUSED | The producer regression rejected it as not being the frozen M1 operating point before any test-byte read. |
| Literal M2 wrapper with real amendment `false` / `PROPOSED` | REFUSED | Exit 2, `REJECTED: inference needs PROTOCOL-AMENDMENT-008 APPROVED with an approved inference snapshot`, no traceback, and `EXP-R03` absent before and after. |
| Lowercase checkout `csv.pyc` | REFUSED | Source-presence and actually-loaded sourceless-module regressions passed. |
| Lowercase spec-erasing `csv.pyc` | REFUSED | The literal substitute executed, but `check_loaded` rejected `csv: no verified origin`. |
| Uppercase checkout `csv.PYC` | REFUSED | Case-insensitive source classification rejected it. |
| Uppercase origin-spoofing `csv.PYC` | REFUSED | The literal substitute executed, but its loader path exposed the file actually read; `check_loaded` rejected it. |
| Forged tracked-source `__pycache__` retaining the genuine header | REFUSED | Both checkout source scanning and loaded-module validation rejected a code object not compiled from its source. |
| Approval fields switched locally and hidden with `assume-unchanged` | REFUSED | `git status --short` was empty; `approved_inference(..., 'm2')` rejected the amendment/authorities as not committed and unmodified. |
| Same approval switch hidden with `skip-worktree` | REFUSED | Same result. |
| Imported `duplicate_structure` helper changed and hidden with `assume-unchanged` | REFUSED | The changed function returned `{'round11_substituted': True}`, while both `check_sources` and full `check_environment` rejected `flagged` and `modified src/leakage_audit/audit.py`. |
| Same helper change hidden with `skip-worktree` | REFUSED | Same result. |
| Embedded `csv/.git/` plus `csv/__init__.py` wrapper | REFUSED | The wrapper changed `Costras` to `Saludable` before the check, but the literal regression rejected `csv/__init__.py`. |
| Directory junction in the checkout | REFUSED | The focused junction regression rejected `link csv`; the `.venv` junction exception remained accepted as intended. |
| Embedded `ultralytics/.git/` plus origin-spoofing `ultralytics/__init__.py` | REFUSED | The substitute loaded and exposed `YOLO='checkout-substitute'`, but `check_sources` and `check_environment` both rejected `ultralytics/__init__.py`. |

These replays close the concrete checkout and Git-index routes from rounds 7 through 10. They do not close NEW-HIGH-05's broader requirement that every present substituted runtime code file be refused.

## NEW-HIGH-05 disposition: PARTIALLY CLOSED, still OPEN

### Surviving recorded-empty-digest cache route

**Severity:** HIGH  
**Location:** `src/evaluation/authority.py:271-289` and `343-353`; the current negative at `tests/test_authority_runtime.py:102-115` covers an unrecorded cache, not a cache already listed in `RECORD` with an empty digest.

`verify_installed` adds every `RECORD` path to `recorded` before inspecting its digest. An empty digest reaches `continue`. The later filesystem scan calls `_bad_cache` only when the path is absent from `recorded`:

```text
if not digest:
    continue
...
if p.suffix.lower() in CODE_SUFFIXES and _key(p) not in recorded and _bad_cache(p)
```

That condition is inverted for the environment's real caches. Pip records generated caches with no hash. Fresh enumeration of the approved `.venv` found:

```text
ACTUAL_VENV_CACHES 9018
EMPTY_DIGEST_CODE_COUNTS {'cache:.pyc': 9010}
```

One of those entries is:

```text
_distutils_hack/__pycache__/__init__.cpython-312.pyc,,
```

The recorded `distutils-precedence.pth` imports `_distutils_hack` during interpreter startup, before the authority gate.

### Disposable counterexamples

A small synthetic distribution first isolated the logic:

```text
TABLE_UNCHANGED True
CACHE_RECORD_LINE __pycache__/recorded_probe.cpython-312.pyc,,
EXECUTED_VALUE cache
SPEC_CACHED <recorded_probe.py>
VERIFY_INSTALLED_PASSED
CHECK_LOADED_PASSED
```

I then copied the complete 1,283,425,675-byte approved `.venv` into a disposable exact-HEAD checkout. Only the `_distutils_hack` cache body was replaced; its genuine header, source, `RECORD`, environment list, and committed runtime table were unchanged. The cache preserved `_distutils_hack` behavior, wrapped the genuine standard-library `csv.DictReader`, and set its own `spec.cached` claim to the recorded source. A fresh literal process produced:

```text
ROW_BEFORE_GATE {'class_name': 'Saludable'}
RUNTIME_IDENTITY f1a06a70e5af9e606618b4db5321f001ad4e905b3777f528d5b4d37465f9a2c2
ROW_AFTER_GATE {'class_name': 'Saludable'}
ENVIRONMENT_PASSED
LOADED_PASSED
EXIT=0
```

The unmodified input row was `class_name=Costras`. The full gate took 414.297 s and left zero fresh-bytecode children after exit. The same substituted cache was active before and after the gate.

**Consequence:** code from a locally replaced, recorded startup cache can change CSV-backed manifests, attempt records, ground truth, group IDs, prediction records, or other scientific inputs while the runtime table, environment identity, approved source hashes, and loaded-module checks all pass. This affects EXP-V01, the operating-point freeze, EXP-R02, EXP-R03, M1 intervals, primary M2 intervals, and M2 sensitivity.

**Resolution criterion:** validate every cache under the whole `.venv` that this interpreter would read against its source, regardless of whether the cache is absent from `RECORD`, present with a hash, or present with an empty digest. A recorded `__pycache__` path with `,,` must still pass `_loadable`/`_same_code`; `RECORD` membership must not bypass that comparison. Loaded-module validation should also bind the actual cache used rather than trusting mutable `spec.cached` alone. Add a negative whose `RECORD` already contains the cache with `,,`, preferably a literal startup path through a recorded `.pth`; after replacing the cache body while retaining a valid header, `check_environment` must refuse before test reads or output creation.

This is new round-11 evidence for the same unresolved NEW-HIGH-05 root cause, not a second HIGH ID. No separate new MEDIUM or LOW finding is opened.

## M1 closures and real EXP-R01 evidence

The named M1 closures still hold:

| Finding | Round-11 status | Fresh evidence |
|---|---:|---|
| HIGH-04 — attempt root used an unrooted verifier | CLOSED | `verify_kaggle_run.py` remains in the exact M1 snapshot; real reconciliation re-derived byte-for-byte. |
| NEW-HIGH-01 — threshold authentication depended on HIGH-04 | CLOSED | The freezer still reaches validation through the definitive reconciled attempt; the ordered frozen-command regression passed. |
| NEW-HIGH-03 — approval not bound to reviewed authorities | CLOSED | All 12 M1 entries equal the proposed SHA256 and committed `HEAD` bytes. |
| NEW-HIGH-07 — index flags hid local approval/helper changes | CLOSED | Exact `assume-unchanged` and `skip-worktree` replays for both approval and imported-helper changes were refused while `git status` was empty. |

Read-only pure recomputation on the real repository confirmed:

- `reconciliation.json` equals the recomputation byte-for-byte;
- the sole ledger entry equals the recomputed definitive entry;
- `selection_record.json` equals the recomputed seal byte-for-byte;
- 552 train/validation files verify;
- selected epoch `91`;
- fitness `0.760868639693682`;
- selected checkpoint SHA256 `0648da3f3641e3cdb5a1908a092ba892548942836a249bb3b39667f9ae8e8125`;
- selection-record SHA256 `4a67bdca43a1c6a782dc6bb172702fcb36ebfcbe9caaa4c73f01808bcb98706c`;
- manifest SHA256 `dd9431dd7bbc00c6117baf6a0f6cf49eff8bc55f144016b4a98dbdea049ecf5f`;
- kernel version `1`.

These facts keep the named M1 defects closed. They do not make M1 inference approvable while the shared local runtime gate accepts the substituted startup cache.

## Frozen command-sequence compatibility

The real amendment remains `inference_approved=false` and `inference_approval.state=PROPOSED`; no real scientific inference or Kaggle write was authorized or performed.

Conditional clean-path compatibility was confirmed in committed disposable fixtures. A focused five-test sequence passed in 60.666 s:

- EXP-V01 scoring, operating-point freeze, EXP-R02 scoring, and M1 intervals ran in order through the literal plan interfaces;
- the M2 dispatcher selected the canonical manifest, ART-002, frozen config, and `EXP-R03` path;
- the promoted EXP-R03 bundle, approved producer, runtime identity, and M2 snapshot were authenticated;
- primary M2 intervals selected the image-weighted path;
- M2 sensitivity wrote the JSON/CSV, confusion, shared-draw, and report outputs;
- the full intervals module separately exercised seed 42 with 2,000 deterministic shared draws.

The non-stubbed approved `.venv` passed the clean runtime gate, so no new parser, path, output-order, promotion, or clean-environment incompatibility was observed if a legitimate commit changes only the two amendment approval fields for this exact snapshot. This is compatibility evidence, not approval: the full disposable-cache replay shows that the same runtime checks also accept substituted code.

## Approval decision by step

| Step | Decision | Reason |
|---|---:|---|
| EXP-V01 | NO | The accepted startup cache can change CSV-backed validation inputs and reconstructed predictions. |
| Operating-point freeze | NO | Altered validation rows can change the F2-selected threshold. |
| EXP-R02 | NO | The same startup substitution persists into test reconstruction and scoring. |
| M1 intervals | NO | Manifest/group/prediction parsing can be changed before the gate completes. |
| EXP-R03 | NO | Startup code can substitute parsing or scientific runtime behavior while retaining the approved runtime identity. |
| Primary M2 intervals | NO | Promoted predictions and group truth are consumed in the accepted substituted process. |
| M2 sensitivity | NO | Class labels, hashes, groups, clusters, and prediction rows can be changed without a refused file. |

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
