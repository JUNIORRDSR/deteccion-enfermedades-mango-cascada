# TASK-05 independent methodological review — round 8

Date: 2026-09-28  
Reviewed repository state: `cf1801610b4fca6e489900b8cbb30d99782a3c06`  
Scope: prospective inference-approval review of the post-`4f90c9f` TASK-05 delta. No research inference, Kaggle/network write, product-code fix, repository commit, push, or `.docx` access was performed. Mutable counterexamples used disposable temporary directories outside the worktree. The only worktree write made by this review is this report.

## Verdict

**DO NOT APPROVE inference for the proposed snapshot.** The committed-`{}` configuration route and the round-7 wrapper exit-code defect are closed, and the ordinary `sitecustomize.py` and ordinary sourceless-`.pyc` regressions are refused. The named M1 verifier, threshold and exact-snapshot closures also remain intact. All proposed snapshot hashes equal both the filesystem bytes and the committed `HEAD` blobs, and the approved `.venv` passes the new file-by-file runtime check.

However, **NEW-HIGH-05 remains PARTIALLY CLOSED / OPEN**. The new loaded-module check trusts the mutable `module.__spec__` after the substituted module has executed. An untracked sourceless `csv.pyc` can copy the standard-library implementation, set `__spec__ = None`, and remain functionally usable. `check_sources` ignores it because it scans only `*.py`; `check_loaded` then skips it because its spec is absent. The disposable replay passed both `check_startup` and `check_loaded`. `csv` is imported by `authority.py`, `evaluate.py`, `predict_model2.py`, and `intervals.py`, so such a checkout-local substitute can change manifests, truths, groups, or prediction records used by every frozen command without being refused.

This finding stays within the declared trust model. It does not require a custodian, signatures, platform attestation, or protection against a trusted committer. It is an untracked local code substitution outside the committed root of trust.

**Open count: HIGH = 1; MEDIUM = 0.**

## Binding authority and trust model

Reviewed before implementation evidence:

- immutable `provenance/protocol_freeze.json` and `.md`;
- SPEC §§6, 7, 11, and 12;
- frozen plan TASK-05 and its literal commands;
- PROTOCOL-AMENDMENT-008 §§4 and 5.1;
- round-6 and round-7 independent TASK-05 reports.

Amendment 008 §4 says there is no independent custodian. This review therefore treats committed Git bytes and the recorded interpreter as trusted. The review asks only whether untracked, modified, or substituted local files can affect the approved computations without refusal.

## Post-round-7 delta and snapshot

`git log 4f90c9f..HEAD` contains four commits: `628c5e9`, `97f4b67`, `c62d50d`, and `cf18016`. The scientific authority changes are limited to `authority.py`, `evaluate.py`, `predict_model2.py`, and `intervals.py`; those four are in the applicable snapshot scopes.

Every proposed hash equals the real filesystem SHA256 and `git show HEAD:<path>` SHA256, and every path is tracked and clean:

| Scope | Declared entries | Proposed = filesystem = `HEAD` | Result |
|---|---:|---:|---|
| M1 | 11 | 11/11 | PASS |
| M2 | 6 | 6/6 | PASS |
| Unique paths | 14 | 14/14 | PASS |

The other changed files are absent from both snapshots: the amendment renderer, Amendment 008 JSON/Markdown, round-7 report, `tests/runtime_stub.py`, and the five changed test modules. The amendment JSON is necessarily outside its self-referential snapshot but remains subject to `committed_clean`.

## Fresh verification

Each mandated module ran in its own fresh process with `PYTHONDONTWRITEBYTECODE=1`:

| Command | Result |
|---|---:|
| `.\.venv\Scripts\python.exe -m unittest tests.test_evaluation` | 58 passed; exit 0; 129.515 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_intervals` | 32 passed; exit 0; 32.122 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_predict_model2` | 9 passed; exit 0; 4.403 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_authority_runtime` | 11 passed; exit 0; 3.394 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_kaggle_job` | 44 passed; exit 0; 0.091 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_verify_kaggle_run` | 14 passed; exit 0; 6.074 s |
| **Total** | **168 passed; 0 failures/errors; 175.599 s** |

The real approved `.venv` also passed `authority.check_environment`, followed by real `torch` and `ultralytics` imports and `check_imported`. Evidence:

- environment list equals committed `provenance/environment/inference_environment.txt`;
- runtime identity: `f1a06a70e5af9e606618b4db5321f001ad4e905b3777f528d5b4d37465f9a2c2`;
- `ultralytics`: `Lib/site-packages/ultralytics/__init__.py`;
- `torch`: `Lib/site-packages/torch/__init__.py`.

No installed importable code file had a blank `RECORD` hash.

## Round-7 finding disposition and counterexample replay

### NEW-HIGH-05 — PARTIALLY CLOSED / OPEN

#### Closed portions

1. **Round-7 `sitecustomize.py` route:** `check_startup` rejects a set `PYTHONPATH`, a loaded/reachable `sitecustomize` or `usercustomize`, and nonstandard import finders. The disposable literal child-process regression with a `sitecustomize.py` that preloaded a fake `ultralytics` module was refused. Because the review instructions prohibit creating the post-approval commit needed by the exact frozen M2 command, the post-approval branch was not manufactured; the same check is called by `approved_inference` before config, test bytes, or scientific imports.
2. **Committed `{}` frozen config:** the producer now calls the real M1 `sealed_config` validator at `predict_model2.py:86-91`, before configuring the runtime, reading the M2 manifest, creating EXP-R03, or reading images. The producer regression proved that an invalid canonical config leaves the run directory absent and never calls `csv.DictReader`. The interval regression used a committed synthetic canonical file and proved that a filename/commit alone no longer passes.
3. **Installed distribution bytes and named imports:** all installed files in the approved `.venv` matched their wheel `RECORD`; after scientific imports, top-level `ultralytics` and `torch` resolved to recorded files of their own distributions. The producer records the runtime hash/modules and `authenticate_m2` compares the runtime identity and requires both module keys.
4. **Ordinary sourceless `.pyc`:** the new regression imported a simple sourceless module and `check_loaded` refused its unrecorded `.pyc` origin.

#### Remaining counterexample

The ordinary `.pyc` regression does not cover a module that mutates its own import metadata:

1. In a disposable directory, the standard-library `csv.py` bytes were compiled to a legacy sourceless `csv.pyc` with one appended statement: `__spec__ = None`; the source was then removed.
2. A fresh approved-venv child process started in that directory with no `PYTHONPATH`, `PYTHONHOME`, `PYTHONSTARTUP`, or `PYTHONPLATLIBDIR`, and imported `csv` before the authority module, exactly as the frozen modules do.
3. `check_startup()` passed.
4. `check_sources()` also passed in a disposable Git root containing the ignored `.pyc`, because `authority.py:96-100` searches only `*.py`.
5. `check_loaded({'csv': csv})` passed because `authority.py:178-180` skips a module whose `__spec__` is `None`.

Observed result:

```text
origin=<disposable>/csv.pyc
spec_is_none=true
startup_passed=true
check_sources_passed=true
loaded_passed=true
```

This is not a hypothetical trusted-committer attack. A checkout-local `csv.pyc` is ignored by Git under the normal `*.pyc` rule, loads before the standard library from the command's checkout root, and can wrap `DictReader` while otherwise preserving normal behavior. Fresh-bytecode redirection occurs only after this module is already loaded. The same pattern applies to another shadowable module that can erase or falsify its post-execution spec.

**Consequence:** untracked code can alter M1 validation/test reconstruction, operating-point inputs, M1 interval groups, M2 manifest rows/truth, EXP-R03 records, or M2 interval groups while all reviewed source hashes and installed-distribution hashes remain unchanged. This affects every inference step, so the combined approval remains blocked.

**Resolution criterion:** before any checkout-local import can execute, reject every untracked, modified, or ignored importable code artifact in the checkout, including at least `.pyc`, `.pyo`, `.pyd`, `.dll`, and `.so`, not only `.py`. `check_loaded` must not silently accept an absent/non-location spec except for explicitly verified built-in, frozen, or namespace cases. Add a fresh literal negative using a checkout-root sourceless module that sets `__spec__ = None`; it must exit 2 before test reads or output creation. No external attestation is needed.

The spec-erasure replay is new round-8 evidence but is folded into NEW-HIGH-05 rather than double-counted as a second HIGH: it is the same unresolved requirement to refuse untracked runtime code.

### NEW-LOW-01 — CLOSED

`evaluate.py:786-790` now translates `predict_model2.RunRejected` into the wrapper's `RunRejected`. A fresh literal command on the real clean tree with the current unapproved amendment returned:

```text
REJECTED: inference needs PROTOCOL-AMENDMENT-008 APPROVED with an approved inference snapshot
EXIT_CODE=2
RUN_DIR_EXISTS=False
```

There was no traceback. The unit regression also passed. The documented invalid-input/refusal contract is restored.

## M1 closures and real EXP-R01 evidence

The round-6 M1 findings remain closed on their stated causes:

| Finding | Status | Fresh evidence |
|---|---|---|
| HIGH-04 — unrooted verifier | **CLOSED** | `verify_kaggle_run.py` remains in the exact M1 snapshot; reconciliation was re-derived from the approved verifier and files. |
| NEW-HIGH-01 — threshold authentication depended on HIGH-04 | **CLOSED** | The freezer still reaches validation only through the committed definitive attempt and approved verifier; the command-chain tests passed. |
| NEW-HIGH-03 — approval not bound to reviewed authorities | **CLOSED** | All 11 M1 entries equal the proposed and committed `HEAD` bytes; replacement-chain regressions passed. |

Read-only real EXP-R01 recomputation confirmed:

- `reconciliation.json` equals the pure recomputation byte-for-byte;
- the sole ledger entry equals the recomputed definitive entry;
- `selection_record.json` equals the recomputed seal byte-for-byte;
- 552 train/validation files verify;
- selected epoch `91`, fitness `0.760868639693682`, checkpoint SHA256 `0648da3f3641e3cdb5a1908a092ba892548942836a249bb3b39667f9ae8e8125`.

These are closures of the named M1 defects. They do not make M1 inference approvable while the shared local-runtime bypass above remains open.

## Frozen command sequence

The clean legitimate path has no newly observed parser, path, ordering, or environment rejection:

- the M1 frozen-command test ran EXP-V01 scoring, the operating-point freeze, EXP-R02 scoring, and M1 intervals in order;
- the M2 dispatcher test used the canonical manifest/weights/config/run directory;
- primary M2 intervals and M2 sensitivity tests passed with the promoted-bundle, frozen-config, runtime-record, and shared-draw checks;
- the real approved `.venv` passed the complete runtime-file and imported-module gates;
- the round-7 full ordered non-scientific replay had already exercised promotion and both M2 consumers.

No scientific inference was rerun, and the real amendment was not switched or committed: doing so would violate the explicit no-commit instruction and the current prospective gate. Therefore this is a clean-path compatibility confirmation, not a claim that a newly approved real EXP-V01/EXP-R02/EXP-R03 run occurred. The surviving `.pyc` route means clean-path runnability is insufficient for approval.

## New defect

### NEW-LOW-02 — LOW — fresh bytecode directory is created outside the workspace

- **Location:** `src/evaluation/authority.py:201-206,227-239`; call order in `predict_model2.py:83-93` and the corresponding M1 approval paths.
- **Evidence:** `fresh_bytecode()` calls `tempfile.mkdtemp` during `approved_inference`, before `configure_environment` redirects `TEMP`/`TMP`. The real check created `C:\Users\junio\AppData\Local\Temp\albus26-pyc-...`; the directly observed disposable directory was removed after the check.
- **Consequence:** later imports may write bytecode outside the declared workspace, and the directory is not cleaned automatically. This violates the frozen environment-containment rule but does not by itself change scientific values, so severity is LOW.
- **Resolution criterion:** create the fresh bytecode directory under the authenticated checkout's configured `provenance/runtime_state/tmp` after environment containment is established, and add a regression that its resolved path is inside the checkout.

## Approval decision by step

| Step | Decision | Reason |
|---|---:|---|
| EXP-V01 | **NO** | Checkout-local preloaded modules such as the accepted `csv.pyc` can alter validation reconstruction. |
| Operating-point freeze | **NO** | Its authenticated attempt can still be parsed by untracked accepted runtime code. |
| EXP-R02 | **NO** | Same shared runtime bypass can alter test reconstruction/scoring. |
| M1 intervals | **NO** | Same bypass can alter records or groups before interval computation. |
| EXP-R03 | **NO** | The config and ordinary runtime routes are fixed, but the locationless-spec `.pyc` route remains. |
| Primary M2 intervals | **NO** | Same accepted substitute can alter manifest/prediction parsing and grouping. |
| M2 sensitivity | **NO** | Same accepted substitute affects all three estimands and bootstrap inputs. |

## Final findings

| ID | Severity | Status | Blocks |
|---|---:|---|---|
| HIGH-04 | HIGH | CLOSED | — |
| NEW-HIGH-01 | HIGH | CLOSED | — |
| NEW-HIGH-03 | HIGH | CLOSED | — |
| NEW-HIGH-05 | HIGH | **PARTIALLY CLOSED / OPEN** | All M1/M2 inference and interval commands; combined approval |
| NEW-HIGH-06 | HIGH | CLOSED | — |
| NEW-LOW-01 | LOW | CLOSED | — |
| NEW-LOW-02 | LOW | OPEN | Workspace/cache containment only |

**Open count: HIGH = 1; MEDIUM = 0. Overall verdict: DO NOT APPROVE the proposed inference snapshot.**
