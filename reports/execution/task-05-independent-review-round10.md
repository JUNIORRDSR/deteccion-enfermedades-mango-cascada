# TASK-05 independent methodological review — round 10

Date: 2026-09-28  
Reviewed repository state: `4c87de866c082565fa124ec813b6079d92255f7a`  
Scope: prospective inference-approval review of the changes after `93c5f8e01d3be1ad030cc22041489e05d0e52fc7`. No research inference, Kaggle/network write, product-code fix, commit, push, or `.docx` access was performed. Mutable probes ran only in disposable copies under the system temporary directory. The only persistent worktree write made by this review is this report.

## Verdict

**DO NOT APPROVE inference for the proposed snapshot.** The round-9 repairs close the named uppercase `csv.PYC` route and both Git-index-flag routes. They also preserve the earlier closures for the checkout `PYTHONPATH`/`sitecustomize.py`, committed `{}` frozen config, lowercase sourceless bytecode, spec-erasing bytecode, forged tracked-source cache, and controlled wrapper refusal.

However, **NEW-HIGH-05 remains PARTIALLY CLOSED / OPEN**. Git collapses the contents of an untracked embedded repository to one suffixless directory entry. In a disposable exact-HEAD copy, an untracked `csv/.git/` plus `csv/__init__.py` was reported by the command used in `check_sources` only as `csv/`. The Python suffix classifier therefore saw no code file and `check_sources()` passed. The present `csv/__init__.py` changed a parsed `class_name` from `Costras` to `Saludable`, claimed the trusted standard-library `csv.py` as its `__spec__.origin`, loader path, and `__file__`, and then passed the complete `check_environment()` and `check_loaded()` controls. It did not patch or disable the checker. This is a present, untracked file that can change every CSV-backed evaluation path without refusal.

**NEW-HIGH-07 is CLOSED.** Both `assume-unchanged` and `skip-worktree` hid the locally changed paths from `git status`, but the new HEAD-byte and flag checks refused locally enabled approval and the modified imported helper.

**Open count: HIGH = 1; MEDIUM = 0.**

## Binding authority and trust model

Reviewed before implementation evidence:

- immutable `provenance/protocol_freeze.json` and `.md`;
- SPEC §§6, 7, 11, and 12;
- frozen plan TASK-05 and its literal commands;
- PROTOCOL-AMENDMENT-008 §§4 and 5.1;
- TASK-05 independent reviews rounds 6, 7, 8, and 9.

Amendment 008 §4 explicitly declares no independent custodian. This review treats the committed Git repository and recorded interpreter as the root of trust. It does not require signatures, platform attestation, or resistance to code that deliberately disables an in-process checker. The surviving counterexample instead supplies an ordinary untracked Python file which is present before inference, is omitted by Git's file enumeration, changes parsed scientific input, and is not refused by either source or loaded-module validation.

## Post-round-9 delta and proposed snapshot

`git log 93c5f8e..HEAD` contains two commits:

- `669531d feat(task05): bytes de HEAD y extensiones sin mayúsculas (ronda 9)`;
- `4c87de8 docs(amendment-008): 5.1 responde a la ronda 9 e instantánea regenerada`.

The diff contains seven files. Only `src/evaluation/authority.py` belongs to either proposed inference snapshot. The amendment JSON/Markdown, sidecar writer, renderer, round-9 report, and runtime tests are outside both snapshots. No changed file is a `.docx`.

Every proposed SHA256 equals the filesystem SHA256 and the corresponding committed `HEAD` blob. The repository has `core.autocrlf=false` and no `.gitattributes`, so its raw working bytes are its blob bytes.

| Scope | Declared entries | Proposed = filesystem = `HEAD` | Result |
|---|---:|---:|---:|
| M1 | 11 | 11/11 | PASS |
| M2 | 6 | 6/6 | PASS |
| Unique paths | 14 | 14/14 | PASS |

The proposed `src/evaluation/authority.py` SHA256 is `9c754b1be0c8c3703f36450a0bbdd945040793c9880e5a1c39445bebe5873e48` in both snapshots.

## Fresh verification

### Required isolated modules

The managed review process runs as `CodexSandboxOffline`, while the linked worktree is owned by `junio`. The real-worktree invocation therefore reached Git's `dubious ownership` refusal after `_run_git` correctly removed the injected `GIT_CONFIG_*` safe-directory exception. That produced raw `CalledProcessError` failures in the three modules which reached the new Git checks. I did not weaken the control, change global Git configuration, or request a repository ownership change.

For runnable method evidence, I created an LF-exact local bundle clone at the same `4c87de8` commit, owned by the review identity, with `core.autocrlf=false` and a junction to the same approved `.venv`. Its protocol-freeze SHA256 was the required `6d5aa3ff47cba97f8ecd0dd15683bb96f0d53146f3af1ce1e95bf24cec7cbc8b`. Each requested module then ran in its own process:

| Command | Result |
|---|---:|
| `.\.venv\Scripts\python.exe -m unittest tests.test_evaluation` | 58 passed; exit 0; 112.687 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_intervals` | 32 passed; exit 0; 27.377 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_predict_model2` | 9 passed; exit 0; 5.511 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_authority_runtime` | 20 passed; exit 0; 12.132 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_kaggle_job` | 44 passed; exit 0; 0.464 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_verify_kaggle_run` | 14 passed; exit 0; 5.560 s |
| **Total** | **177 passed; 0 failures/errors; 163.731 s** |

The same approved interpreter passed the complete file-by-file environment check and post-import loaded-module check in that exact-HEAD copy:

- runtime identity `f1a06a70e5af9e606618b4db5321f001ad4e905b3777f528d5b4d37465f9a2c2`;
- `torch` at `Lib/site-packages/torch/__init__.py`;
- `ultralytics` at `Lib/site-packages/ultralytics/__init__.py`;
- fresh bytecode under `provenance/runtime_state/pycache/run-*`;
- zero children under the bytecode parent after normal process exit.

The ownership note is a limitation of this managed review identity, not evidence of altered scientific bytes. I do not claim that the managed sandbox itself completed a real-worktree inference run.

### Focused counterexample regressions

Nine focused regressions were rerun verbosely in the disposable exact-HEAD copy; all passed:

- checkout `PYTHONPATH` / `sitecustomize.py` literal child;
- committed `{}` frozen config before any test-byte read;
- untracked/ignored/modified code, including lowercase and uppercase extensions;
- sourceless bytecode;
- round-8 spec-erasing lowercase `csv.pyc`;
- round-9 origin-spoofing uppercase `csv.PYC`;
- forged tracked-source cache;
- both index flags and staged code;
- hidden/uncommitted approval bytes plus `GIT_DIR` redirection.

## Requested counterexample replay

### Round-7 checkout `PYTHONPATH` / `sitecustomize.py` — REFUSED

The literal child-process regression placed `sitecustomize.py` on checkout `PYTHONPATH` and preloaded a fake scientific module. `check_startup()` refused the set `PYTHONPATH` and loaded startup hook. The regression passed.

### Committed `{}` frozen config — REFUSED

The producer regression presented `{}` at the canonical frozen-config path after an approved-gate stub. It was refused as not being the frozen M1 operating point before a run directory, manifest read, or `csv.DictReader` call. The regression passed.

### Literal wrapper refusal contract — CLOSED

On the clean, owner-matched exact-HEAD copy with the real amendment still `false`/`PROPOSED`, the literal M2 command returned:

```text
REJECTED: inference needs PROTOCOL-AMENDMENT-008 APPROVED with an approved inference snapshot
EXIT_CODE=2
RUN_DIR_EXISTS=False
```

There was no traceback. **NEW-LOW-01 remains CLOSED.**

### Lowercase and uppercase sourceless bytecode — REFUSED

- A checkout-root lowercase `csv.pyc` was refused by the source-presence control; an actually imported sourceless module was independently refused by loaded-origin validation.
- The round-8 lowercase `csv.pyc` which erased `__spec__` was refused as having no verified origin.
- An uppercase `csv.PYC` was classified case-insensitively and refused by `check_sources`.
- The round-9 uppercase module which claimed standard-library `csv.py` was refused because its loader path still identified the checkout file.

The relevant literal and unit regressions all passed.

### Forged tracked-module `__pycache__` — REFUSED

The cache for a tracked source retained the genuine 16-byte source header but carried a different code object. The fresh source and loaded-module regressions both refused it as not being its source compiled. Genuine caches, caches for another interpreter, and caches which this interpreter would not read remained accepted as intended.

### Locally switched approval hidden by index flags — REFUSED

Two disposable exact-HEAD copies changed only:

- `inference_approved: false → true`;
- `inference_approval.state: PROPOSED → APPROVED`.

One path was marked `assume-unchanged`, the other `skip-worktree`. In both cases `git status --short` was empty and the working blob ID (`e9f162c…`) differed from `HEAD` (`25a068d…`). Both calls to `approved_inference(..., 'm2')` were refused: `the amendment and the m2 authorities must be committed and unmodified`.

### Modified imported helper hidden by index flags — REFUSED

Two other disposable copies changed tracked `src/leakage_audit/audit.py` so `duplicate_structure([])` returned `{'round10_substituted': True}`. One was hidden by `assume-unchanged`, the other by `skip-worktree`. Again `git status --short` was empty and working/HEAD blob IDs differed.

The substituted module imported and its changed result was observable, but both `check_sources()` and complete `check_environment()` refused each copy with both `flagged src/leakage_audit/audit.py` and `modified src/leakage_audit/audit.py`. The control was not disabled or modified. This closes the demonstrated scientific-helper route.

## Finding dispositions

### NEW-HIGH-07 — CLOSED

`committed_clean` now computes each working file's Git blob ID in Python and compares it with the recursive `HEAD` tree; absent paths fail. `check_sources` separately rejects `assume-unchanged`, `skip-worktree`, staged code absent from `HEAD`, and changed HEAD code bytes. Git is selected outside the checkout, runs with replacement objects/fsmonitor/untracked cache disabled, and receives no `GIT_*` variables.

Fresh evidence includes:

- both exact approval-state flag replays refused;
- both exact imported-helper flag replays refused;
- staged-code and foreign-`GIT_DIR` regressions passed;
- `render_kaggle_job.py` now delegates its cleanliness decisions to this same HEAD-byte primitive.

The round-9 cause is closed without adding a custodian or external attestation.

### NEW-HIGH-05 — PARTIALLY CLOSED / OPEN

The explicitly requested round-7/8/9 files are now refused, but the stated requirement is broader: every present untracked or ignored importable code file must be refused before inference.

#### Surviving embedded-repository counterexample

In a disposable exact-HEAD copy:

1. I created an untracked embedded Git repository at `csv/.git/` and a present `csv/__init__.py`.
2. The exact untracked-file command used by `check_sources` returned only `csv/`, not `csv/__init__.py`.
3. `_code('csv/')` is false because the collapsed directory entry has no code suffix, so `check_sources()` passed.
4. Windows/Python imported the checkout package before the standard-library module because the checkout root is first on the command path.
5. The package delegated normal CSV behavior to the trusted standard-library implementation but wrapped `DictReader` so `class_name=Costras` became `class_name=Saludable`.
6. It set its own `__spec__.origin`, loader path, and `__file__` to the trusted standard-library `csv.py`. These are module-owned mutable metadata; it did not alter the authority module or any checker function.
7. The complete environment gate and a fresh loaded-module check both passed.

Observed evidence:

```text
GIT_OTHERS ['csv/', '']
SHADOW_EXECUTED True
REAL_SOURCE_PRESENT True
ALTERED_ROW {'class_name': 'Saludable'}
ENVIRONMENT_PASSED
LOADED_PASSED
```

An equivalent untracked embedded `ultralytics/` package also passed `check_sources` and `check_imported('ultralytics', 'torch')`, with the recorded installed paths returned for both names while `YOLO` came from the checkout substitute.

**Location:** `src/evaluation/authority.py:176-216` (`_code`, `_stale_cache`, and Git-only `--others` enumeration) and `280-320` (loaded-module validation trusts mutable origin/loader/file claims once untracked presence was missed).

**Consequence:** a present untracked package can wrap `csv.DictReader` and alter manifests, attempt records, ground truth, group IDs, or predictions used by EXP-V01, the operating-point freeze, EXP-R02, EXP-R03, M1 intervals, primary M2 intervals, and M2 sensitivity, while all approved source/package hashes remain unchanged. The demonstrated class-label substitution is directly scientific, not merely an import marker.

**Resolution criterion:** enumerate actual checkout files recursively in Python, without relying on Git to expand untracked embedded repositories, while excluding only the authenticated `.venv` and the fresh runtime bytecode directory. Do not follow reparse points/symlinks outside the checkout. Case-normalize extensions and apply the existing cache exception only to a cache this interpreter would read which equals its HEAD source compiled. Alternatively, explicitly reject every collapsed untracked directory/embedded repository before imports. Add a literal negative with `csv/.git/` plus `csv/__init__.py` that wraps `DictReader` and spoofs origin/loader/file; it must be refused before test reads or output creation.

This is the same unresolved root cause as NEW-HIGH-05—present untracked runtime code is accepted—so it is not double-counted as a new HIGH ID.

## M1 closures and real EXP-R01 evidence

The round-6 M1 closures still hold:

| Finding | Round-10 status | Fresh evidence |
|---|---:|---|
| HIGH-04 — unrooted verifier | **CLOSED** | `verify_kaggle_run.py` remains in the exact M1 snapshot; real reconciliation re-derived byte-for-byte. |
| NEW-HIGH-01 — threshold authentication depended on HIGH-04 | **CLOSED** | The freezer still reaches validation only through the definitive reconciled attempt; command-chain regressions passed. |
| NEW-HIGH-03 — approval not bound to reviewed authorities | **CLOSED** | All 11 M1 identities equal the proposed SHA256 and committed HEAD bytes; replacement-chain regressions passed. |

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

These close the named M1 defects. They do not overcome the shared untracked `csv` route above.

## Frozen command-sequence compatibility

The real amendment remains `inference_approved=false` and `inference_approval.state=PROPOSED`; no real scientific inference or Kaggle write was authorized or performed. Conditional clean-path compatibility was nevertheless confirmed for an exact committed snapshot in disposable committed-repository fixtures:

- EXP-V01 scoring → operating-point freeze → EXP-R02 scoring → M1 intervals ran in order through the literal plan interface;
- the M2 dispatcher selected the canonical manifest, ART-002, frozen config, and EXP-R03 path;
- the prescribed promoted EXP-R03 bundle, approved producer, runtime identity, and M2 snapshot were authenticated;
- primary M2 intervals selected the image-weighted path;
- M2 sensitivity wrote the full sibling output family and used shared deterministic draws;
- the 2,000-draw bootstrap/determinism tests passed in the full intervals module;
- the approved `.venv` passed installed-file, scientific-import, and post-import checks in an owner-matched exact-HEAD checkout.

A focused five-test chain covering the ordered M1 commands, M2 dispatch, primary M2 intervals, M2 sensitivity outputs, and promoted-bundle authentication passed in 41.697 s. Thus no clean-path parser, path, output-order, promotion, or runtime-package incompatibility was observed if a legitimate commit changes only the two amendment approval fields for this exact snapshot.

That compatibility result is not approval. The surviving embedded-repository substitution passes the same runtime checks and can change what every command computes.

## Approval decision by step

| Step | Decision | Reason |
|---|---:|---|
| EXP-V01 | **NO** | The accepted untracked `csv` package can alter validation attempt/manifests and reconstructed predictions. |
| Operating-point freeze | **NO** | The same accepted parser can alter validation rows and therefore the selected F2 threshold. |
| EXP-R02 | **NO** | Test reconstruction consumes CSV-backed committed evidence through the same substituted module. |
| M1 intervals | **NO** | Group/manifests can be changed in memory by the accepted CSV wrapper. |
| EXP-R03 | **NO** | Both the shared CSV package and an embedded `ultralytics` substitute pass the runtime controls. |
| Primary M2 intervals | **NO** | Promoted predictions and group truth are parsed through the accepted substitute. |
| M2 sensitivity | **NO** | Class labels, group IDs, clusters, and predictions can be changed without a refused file. |

## New defects

No separate new finding ID is opened. The embedded-repository counterexample is new round-10 evidence for the still-open NEW-HIGH-05 requirement, not an independent root cause. No new MEDIUM or LOW defect was found.

## Final findings

| ID | Severity | Status | Blocks |
|---|---:|---|---|
| HIGH-04 | HIGH | CLOSED | — |
| NEW-HIGH-01 | HIGH | CLOSED | — |
| NEW-HIGH-03 | HIGH | CLOSED | — |
| NEW-HIGH-05 | HIGH | **PARTIALLY CLOSED / OPEN** | All M1/M2 inference and interval commands; combined approval |
| NEW-HIGH-06 | HIGH | CLOSED | — |
| NEW-HIGH-07 | HIGH | **CLOSED** | — |
| NEW-LOW-01 | LOW | CLOSED | — |
| NEW-LOW-02 | LOW | CLOSED | — |

**Open count: HIGH = 1; MEDIUM = 0. Overall verdict: DO NOT APPROVE inference for the proposed snapshot.**
