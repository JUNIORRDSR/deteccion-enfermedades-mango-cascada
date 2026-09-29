# TASK-05 independent methodological review — round 9

Date: 2026-09-28  
Reviewed repository state: `93c5f8e01d3be1ad030cc22041489e05d0e52fc7`  
Scope: prospective inference-approval review of the changes after `cf1801610b4fca6e489900b8cbb30d99782a3c06`. No research inference, Kaggle/network write, product-code fix, commit, push, or `.docx` access was performed. Mutable counterexamples ran only in a disposable clone under `C:\tmp`. The only persistent worktree write made by this review is this report.

## Verdict

**DO NOT APPROVE inference for the proposed snapshot.** The intended round-8 repairs work for the lowercase artifacts covered by the new tests: the ordinary checkout `sitecustomize.py`, ordinary lowercase sourceless `csv.pyc`, round-8 spec-erasing lowercase `csv.pyc`, and a forged tracked-source cache retaining the source header are all refused. The fresh bytecode directory is now inside the workspace and is removed on normal process exit. Thus **NEW-LOW-02 is CLOSED**, while substantial parts of **NEW-HIGH-05** are closed.

However, **NEW-HIGH-05 remains PARTIALLY CLOSED / OPEN** on the actual Windows target. Git's lowercase pathspecs do not report an uppercase `.PYC`, although Windows' import loader opens it for a requested lowercase `.pyc`. A disposable untracked `csv.PYC` executed, pointed its mutable `__spec__.origin` and `__file__` at the trusted standard-library `csv.py`, and passed `check_startup`, `check_sources`, `check_loaded`, and the complete `authority.approved_inference(..., 'm2')` gate. Its loader still reported the real checkout file. This is the same local untracked-code substitution that NEW-HIGH-05 is intended to refuse.

A second, independent defect is **NEW-HIGH-07**. `committed_clean` and `check_sources` rely on `git status`; Git deliberately omits paths marked locally `assume-unchanged`. In the disposable clone, the two approval fields were changed without a commit and hidden with that flag: `git status --short` was empty, the amendment working blob differed from `HEAD`, and `approved_inference(..., 'm2')` returned successfully. Separately, a hidden modification of the tracked, imported `src/leakage_audit/audit.py` changed `duplicate_structure([])` to a fabricated result while both `check_sources` and `check_loaded` passed. This does not alter or disable the checker and requires no custodian: the present working files simply differ from committed `HEAD` bytes without being refused.

**Open count: HIGH = 2; MEDIUM = 0.**

## Binding authority and trust model

Reviewed before the implementation evidence:

- immutable `provenance/protocol_freeze.json` and `.md`;
- SPEC §§6, 7, 11, and 12;
- frozen plan TASK-05, including its literal commands;
- PROTOCOL-AMENDMENT-008 §§4 and 5.1;
- TASK-05 independent reviews rounds 6, 7, and 8.

Amendment 008 §4 declares no independent custodian. This review therefore treats committed Git bytes and the recorded interpreter as trusted. It does not require signatures, platform attestation, or proof against code already executing inside the process deliberately disabling the checker. Both open findings instead demonstrate a local file whose bytes differ from the committed repository, remain present, affect an approved code path, and are not refused.

## Post-round-8 delta and proposed snapshot

`git log cf18016..HEAD` contains five commits: `c4c94c8`, `3f23a65`, `1a40170`, `0c48229`, and `93c5f8e`. The diff contains seven files. Only `src/evaluation/authority.py` belongs to either proposed inference snapshot. The other changed files are outside both snapshots: the amendment JSON/Markdown, its sidecar writer, the round-8 report, `tests/test_authority_runtime.py`, and the separately fixed `provenance/commands/task01/install_reconstructed.py`. A no-write `compile(...)` check confirmed that the latter now parses.

Every declared proposed hash equals both the filesystem SHA256 and the committed `HEAD` blob SHA256; every path is tracked and clean in the real worktree:

| Scope | Declared entries | Proposed = filesystem = `HEAD` | Result |
|---|---:|---:|---|
| M1 | 11 | 11/11 | PASS |
| M2 | 6 | 6/6 | PASS |
| Unique paths | 14 | 14/14 | PASS |

The proposed `authority.py` SHA256 is `1207ce85aed28e67b769e3bde42ed3e25f7b3098ddca142ce56ec5ac4e2a6eb0`.

## Fresh verification

Each required test module ran in its own fresh process with `PYTHONDONTWRITEBYTECODE=1`:

| Command | Result |
|---|---:|
| `.\.venv\Scripts\python.exe -m unittest tests.test_evaluation` | 58 passed; exit 0; 136.521 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_intervals` | 32 passed; exit 0; 38.437 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_predict_model2` | 9 passed; exit 0; 5.302 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_authority_runtime` | 16 passed; exit 0; 8.760 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_kaggle_job` | 44 passed; exit 0; 0.090 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_verify_kaggle_run` | 14 passed; exit 0; 6.186 s |
| **Total** | **173 passed; 0 failures/errors; 195.296 s** |

The real approved `.venv` also passed the full file-by-file environment check, followed by real scientific imports and the post-import loaded-module check:

- runtime identity: `f1a06a70e5af9e606618b4db5321f001ad4e905b3777f528d5b4d37465f9a2c2`;
- `torch`: `Lib/site-packages/torch/__init__.py`;
- `ultralytics`: `Lib/site-packages/ultralytics/__init__.py`;
- fresh bytecode prefix was under `provenance/runtime_state/pycache/run-*`;
- after process exit, `provenance/runtime_state/pycache` had zero children;
- the real worktree remained clean.

## Requested counterexample replays

### Round-7 checkout `PYTHONPATH` / `sitecustomize.py` — REFUSED

In the disposable copy, only the two amendment approval fields were switched for the proposed snapshot. An untracked checkout-root `sitecustomize.py` printed a marker when loaded through `PYTHONPATH`. The literal M2 command was:

```powershell
.\.venv\Scripts\python.exe -m src.evaluation.evaluate --model-id model2 --config configs/evaluation_frozen.json --split test --run-dir experiments/model2/EXP-R03
```

Observed result:

```text
ROUND9_SITECUSTOMIZE_LOADED
REJECTED: the import system is overridden at startup: ['PYTHONPATH is set', 'sitecustomize is loaded', ...]
EXIT_CODE=2
RUN_DIR_EXISTS=False
```

### Committed `{}` frozen config — REFUSED

The fresh `tests.test_predict_model2.ProducerGates.test_an_unfrozen_config_is_refused_before_any_test_byte` regression passed. It presents `{}` at the canonical frozen-config path after the approval gate and proves refusal as “frozen M1 operating point,” no run directory, and no `csv.DictReader` call. The corresponding real interval regression also passed. No new disposable commit was created because this review was explicitly prohibited from running `git commit`.

### Literal wrapper refusal contract — CLOSED

On the real clean worktree with the actual false/PROPOSED approval state, the literal M2 command produced:

```text
REJECTED: inference needs PROTOCOL-AMENDMENT-008 APPROVED with an approved inference snapshot
EXIT_CODE=2
RUN_DIR_EXISTS=False
```

There was no traceback. **NEW-LOW-01 remains CLOSED.**

### Lowercase sourceless module shadow — REFUSED

An untracked checkout-root sourceless lowercase `csv.pyc` was actually selected for the module imported by the frozen commands. The literal M2 command produced:

```text
REJECTED: the checkout has untracked, ignored or modified code: ['csv.pyc']
EXIT_CODE=2
RUN_DIR_EXISTS=False
```

### Round-8 spec-erasing `csv.pyc` — REFUSED TWICE

The disposable lowercase sourceless module executed and set `csv.__spec__ = None`. `check_startup` passed, proving this was not merely the startup-hook route. Both independent controls then refused it:

```text
SOURCES_REFUSED NotApproved ... ['csv.pyc']
LOADED_REFUSED NotApproved ... ['csv: no verified origin']
```

### Forged tracked-module `__pycache__` with retained header — REFUSED TWICE

The cache for tracked `src/evaluation/provenance.py` retained the genuine 16-byte source header but carried another code object. A direct import confirmed the forged body had executed in that deliberately adversarial child process. Both controls then refused the present cache:

```text
FORGED_EXECUTED True
SOURCES_REFUSED NotApproved ... provenance.cpython-312.pyc
LOADED_REFUSED NotApproved ... is not its source compiled
```

The approved command path runs `check_sources` before importing this helper, so it would stop before that forged body executes there. Caches with another interpreter tag, a removed source, or an outdated header remain allowed because this interpreter will not read them; the fresh runtime tests covered those cases.

## NEW-HIGH-05 disposition — PARTIALLY CLOSED / OPEN

The repairs close every requested lowercase round-7/8 route, but they do not establish the stated rule that *every* untracked importable code artifact is refused.

### Surviving Windows uppercase-extension counterexample

1. A disposable checkout-root source was compiled as `csv.PYC`, then the source was removed.
2. Windows loaded that file when import machinery requested lowercase `csv.pyc`.
3. The module exposed the real `_csv.reader` so environment `RECORD` parsing remained functional, and changed only its mutable import metadata to claim the trusted standard-library `csv.py` as `__spec__.origin`/`__file__`; its loader still reported the checkout `csv.pyc`.
4. Git's `*.pyc` pathspec did not list the uppercase file, even with `core.ignorecase=true`.
5. The complete approval gate passed.

Observed result:

```text
SHADOW_EXECUTED True
SPOOFED_ORIGIN C:\Users\junio\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\Lib\csv.py
LOADER_FILENAME C:\tmp\...\repo\csv.pyc
STARTUP_PASSED
SOURCES_PASSED
LOADED_PASSED
APPROVAL_PASSED
```

**Location:** `src/evaluation/authority.py:51,148-164,229-284`. `check_sources` supplies lowercase Git pathspecs; `check_loaded` trusts the already executed module's mutable spec without cross-checking its loader filename.

**Consequence:** the substitute can implement `csv.DictReader`/`reader` wrappers and alter manifests, ground truth, groups, predictions, or attempts used by EXP-V01, the freeze, EXP-R02, EXP-R03, and both interval paths, while the approved source/package hashes remain unchanged.

**Resolution criterion:** enumerate candidate status/ignored paths without case-sensitive suffix pathspec filtering, classify extensions with a case-normalized filesystem path in Python, and cross-check a located module's claimed origin against its loader filename (and `__file__` when present). Add a literal Windows negative using an uppercase `csv.PYC` that spoofs its spec; it must be refused before test reads or output creation. No external attestation is needed.

## NEW-LOW-02 disposition — CLOSED

`fresh_bytecode()` now creates a unique directory under the authenticated checkout's `provenance/runtime_state/pycache`, records that exact prefix as the only accepted non-null `sys.pycache_prefix`, and registers removal at exit. The fresh unit checks passed, the real environment run used that path, and the parent had zero children after exit. `PYTHONPYCACHEPREFIX` and a foreign `sys.pycache_prefix` are refused. This closes the round-8 workspace-containment finding; abnormal termination may leave an unused directory, but future runs create a new prefix and never read the old one.

## M1 closures and real EXP-R01 evidence

The round-6 M1 closures still hold on their stated causes:

| Finding | Status | Fresh evidence |
|---|---|---|
| HIGH-04 — unrooted verifier | **CLOSED** | `verify_kaggle_run.py` remains in the exact M1 snapshot; reconciliation was independently re-derived from that verifier and the real attempt files. |
| NEW-HIGH-01 — threshold authentication depended on HIGH-04 | **CLOSED** | The freezer still reaches validation only through the definitive reconciled attempt; the altered-verifier/replacement-chain regressions passed. |
| NEW-HIGH-03 — approval not bound to reviewed authorities | **CLOSED** | All 11 M1 identities equal proposed, filesystem, and committed `HEAD` bytes; the exact-snapshot regressions passed. |

Read-only recomputation of the real EXP-R01 evidence confirmed:

- `reconciliation.json` equals the pure recomputation byte-for-byte;
- the sole ledger entry equals the recomputed definitive entry;
- `selection_record.json` equals the recomputed seal byte-for-byte;
- 552 train/validation files verify;
- selected epoch `91`;
- fitness `0.760868639693682`;
- checkpoint SHA256 `0648da3f3641e3cdb5a1908a092ba892548942836a249bb3b39667f9ae8e8125`.

These close the named M1 defects. They do not make M1 inference approvable while the shared local-file gates can be bypassed.

## Frozen command sequence compatibility

The actual scientific sequence was not run: the real amendment remains unapproved, EXP-V01/EXP-R02 require Kaggle inference, and this review was prohibited from network writes and from changing any worktree file other than this report. That is the correct prospective behavior.

For clean inputs, the current interfaces and ordering remain compatible once a legitimate committed approval switches only `inference_approval.state` and `inference_approved` for this exact snapshot:

- the fresh `FrozenCommands` regression ran EXP-V01 scoring, operating-point freeze, EXP-R02 scoring, and M1 intervals in order with the literal plan interface;
- the M2 dispatcher regression used the canonical manifest, weights, config, and EXP-R03 path;
- the fresh producer regression rejected `{}` before a test read and accepted the intended dispatch contract;
- the primary M2 command, promoted-bundle authentication, M2 sensitivity, shared 2,000-draw bootstrap, and output-family regressions passed;
- the real approved `.venv` passed the new runtime checks and scientific imports;
- `evaluate.py`, `predict_model2.py`, and `intervals.py` are unchanged since the round-8 clean-path assessment; the only changed snapshot source is `authority.py`.

Thus no new clean-path parser, location, promotion-order, runtime-package, or 2,000-resample incompatibility was observed for: EXP-V01 → operating-point freeze → EXP-R02 → M1 intervals → EXP-R03 → prescribed three-file promotion → primary M2 intervals → M2 sensitivity. This is a compatibility confirmation, not a claim that a new scientific run occurred. The two open HIGH bypasses make clean-path runnability insufficient for approval.

## New defect

### NEW-HIGH-07 — HIGH — Git index flags hide uncommitted approval and scientific source substitutions

**Location:** `src/evaluation/authority.py:81-87,148-164,214-217,356-373`; all consumers that use `committed_clean` for attempts, promotion bundles, and frozen authorities inherit the same assumption.

**Evidence A — local self-approval:** in the disposable clone, only `inference_approved: false → true` and `inference_approval.state: PROPOSED → APPROVED` were changed. The path was marked `assume-unchanged`, not committed. `git status --short` became empty while the committed and working blob IDs were different (`cd13d0d...` versus `ce01fdf...`). With all snapshot authority bytes equal to the proposal, `authority.approved_inference(..., 'm2')` printed `APPROVAL_PASSED APPROVED`.

**Evidence B — changed scientific computation:** tracked `src/leakage_audit/audit.py`, imported by `intervals.py`, was changed so `duplicate_structure([])` returned `{'round9_substituted': True}`. After the same local flag, `git status` was empty although its committed and working blob IDs differed (`37adfc4...` versus `98c3b02...`). The substituted function executed, then both `check_sources()` and `check_loaded({'src.leakage_audit.audit': module})` passed.

**Consequence:** the prospective approval can be enabled without a committed review record, and tracked helpers or committed attempt/promotion artifacts can differ from `HEAD` while still being accepted. The demonstrated helper directly feeds M2 sensitivity structure; the same cleanliness primitive guards M1 attempts and M2 promotion. This can change scientific results without changing the approved snapshot hashes.

**Resolution criterion:** for every amendment, authority, committed attempt/promotion artifact, and loaded tracked checkout source, compare current file bytes to the actual `HEAD:<path>` blob independently of index stat/skip flags; reject paths absent from `HEAD`. Alternatively reject any `assume-unchanged`/`skip-worktree` entry and still compare bytes. Add literal negatives for a locally flipped amendment and an imported tracked helper hidden by each flag. Both must be refused before inference or consumption. No custodian, signature, or platform attestation is required.

## Approval decision by step

| Step | Decision | Reason |
|---|---:|---|
| EXP-V01 | **NO** | Uppercase untracked import code and hidden tracked-file substitutions can pass the shared approval/runtime gate. |
| Operating-point freeze | **NO** | The same accepted substitutions can alter validation reconstruction or locally self-enable approval. |
| EXP-R02 | **NO** | The same shared gates protect test reconstruction and definitive-attempt files. |
| M1 intervals | **NO** | Loaded tracked helpers and committed artifacts are not proven equal to `HEAD` when index flags are set. |
| EXP-R03 | **NO** | The uppercase `csv.PYC` passed the complete M2 approval gate; the approval JSON can also be switched locally without a commit. |
| Primary M2 intervals | **NO** | Promotion/authentication uses the same Git-cleanliness primitive and imported helpers. |
| M2 sensitivity | **NO** | The hidden `duplicate_structure` substitution demonstrably changed this path while both runtime checks passed. |

## Final findings

| ID | Severity | Status | Blocks |
|---|---:|---|---|
| HIGH-04 | HIGH | CLOSED | — |
| NEW-HIGH-01 | HIGH | CLOSED | — |
| NEW-HIGH-03 | HIGH | CLOSED | — |
| NEW-HIGH-05 | HIGH | **PARTIALLY CLOSED / OPEN** | All M1/M2 inference and interval commands; combined approval |
| NEW-HIGH-06 | HIGH | CLOSED | — |
| NEW-HIGH-07 | HIGH | **OPEN** | Approval state, all committed-clean artifacts, and loaded checkout helpers |
| NEW-LOW-01 | LOW | CLOSED | — |
| NEW-LOW-02 | LOW | CLOSED | — |

**Open count: HIGH = 2; MEDIUM = 0. Overall verdict: DO NOT APPROVE the proposed inference snapshot.**
