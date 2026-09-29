# Independent Audit A — TASK-05 execution

Date: 2026-09-28  
Audited HEAD: `b910e7eeae023867c950b35fe2314d952681af69`  
Disposition: **VALID, WITH ONE LOW TEST-MAINTENANCE FINDING**

## Verdict

The committed M1 and M2 results are valid outputs of the frozen protocol and are fit to be reported in the manuscript, subject to their already-declared scope and limitations. This conclusion covers:

- M1 validation `EXP-V01`, including the failed v1 attempt and successful v2 retry;
- the validation-only operating-point freeze at confidence `0.35`;
- the single M1 test run `EXP-R02`;
- the local M2 test run `EXP-R03`;
- M1 and M2 intervals and M2 duplicate sensitivity; and
- the TASK-06 local CPU benchmark.

The benchmark supports only the measured local CPU protocol. It does not supply Raspberry Pi measurements or, by itself, justify a comparative efficiency claim.

No HIGH or MEDIUM defect was found. One LOW defect is open: `tests/test_benchmark.py` retained a pre-freeze assertion after the shipped benchmark configuration was legitimately promoted. This makes that requested test module non-green, but does not change any committed scientific result or benchmark value.

The DECISION-039 residual is **CLOSED**. The unreviewed round-12 `python._pth` residual is also **CLOSED** by this audit.

## Scope, authority, and method

I treated the committed repository as the root of trust, as required. I did not require an independent custodian, signatures, or platform attestation. I read the binding freeze, design sections 6, 7, 8, 11, and 12, TASK-05 and TASK-06 including their literal commands, both forms of PROTOCOL-AMENDMENT-008, its retry policy and section 5.1 approval, DECISION-037 through DECISION-039, the prior proportionate review rounds, and history from `42270fa` through HEAD.

All executable audit work was performed in an owner-matched disposable exact-HEAD clone at `C:\tmp\albus-task05-audit-b910e7e`, with a junction to the same `.venv`. The audited worktree was not used for counterexamples or regenerated outputs. M2 inference, Kaggle inference, and benchmark timing were not rerun.

## 1. DECISION-039 executed-source review

### Accepted source set

`src/evaluation/evaluate.py:executed_source` accepts only a receipt hash matching one of these two candidates:

1. the rendered `kernel.py`; or
2. exactly `# %% [code]\n` followed by that rendered kernel.

`provenance/commands/task04/verify_kaggle_run.py:reconcile` calls the same function. `rebuild_predictions` passes the returned accepted source to `verify_prediction_run`, so reconciliation and prediction rebuilding enforce the same rule. `src/evaluation/kaggle_job.py` did not change.

The pre-existing `source_sha256` serialization rule normalizes CRLF to LF and canonicalizes final newlines. Consequently, different newline serializations of either candidate can share the accepted hash. They compute the same Python program. Apart from those pre-existing serialization equivalents and the protocol's ordinary reliance on SHA-256 collision resistance, no additional executed text can pass. In particular, a Markdown cell marker, a doubled code marker, or any inserted executable statement changes the hash and is rejected. I found no route by which text computing a different result can pass either `executed_source` or `reconcile`.

### Semantic effect of the marker

The marker is a Python comment and is semantically inert for these kernels:

- ASTs of the rendered and marker-prefixed `EXP-V01/v2/kernel.py` are identical when source locations are excluded;
- the module docstring remains identical;
- there is no encoding cookie in the first two lines;
- there is no `__future__` import;
- the kernels do not use `inspect`, `linecache`, tracing, code-object line numbers, `__doc__`, or source line numbers as scientific inputs; and
- exception rendering uses `traceback.format_exception_only`, so the one-line displacement is not incorporated into a result.

The kernel intentionally reads `__file__` to record executed-source identity; for the editor execution this produces the approved editor-form hash rather than changing the computation.

### Tests and disposition

The new tests exercise both accepted forms and reject altered prefixes. They also cover a rebuilt editor-form prediction run. Together with the existing source-normalization tests, this is adequate for the changed guarantee. The fresh module results were:

- `tests.test_evaluation`: 60/60 pass;
- `tests.test_verify_kaggle_run`: 15/15 pass; and
- `tests.test_kaggle_job`: 44/44 pass.

**DECISION-039 residual: CLOSED.**

## 2. Inference-chain reconciliation

I freshly ran `provenance/commands/task04/verify_kaggle_run.py` reconciliation in the disposable clone. For all three Kaggle attempts, the newly generated reconciliation bytes equal the committed `reconciliation.json`, and the regenerated ledger entry equals the corresponding committed `attempts.jsonl` entry.

| Attempt | Rendered kernel / executed source | Platform, payload, and ledger result | Fresh reconciliation |
|---|---|---|---|
| `EXP-V01/v1` | Kernel equals the render record; rendered source SHA begins `e70e79e…` | Payload equals render plus receipt; platform state is `ERROR`, stage `start`; 2 saved platform files; no raw predictions or checkpoint output | Byte-identical; definitive `false`; retry permitted |
| `EXP-V01/v2` | Same rendered kernel as v1; editor-form executed SHA `ae2ee4e815d659732e4116990b3fbc05bdb24c9118538b64949e423f594e73f8` | Payload SHA begins `b2f78531…`; 16 saved files all reconcile; state `COMPLETE`, stage `done` | Byte-identical; definitive `true`; no retry |
| `EXP-R02/v1` | Kernel equals the render record; rendered SHA begins `9c8971a5…`; editor-form executed SHA `9529588c4cff5958f364ddd18c3e627be225d155ac94571d543308ea4ae5d18c` | Payload SHA begins `30fd869…`; 16 saved files all reconcile; state `COMPLETE`, stage `done` | Byte-identical; definitive `true`; no retry |

Evidence inventories, downloaded files, receipt hashes, platform records, and the committed ledgers reconcile. The receipt and job log are correctly treated as recorder/self-authored artifacts rather than pretending they attest themselves.

`EXP-V01/v1` failed before model output because no attached training output was mounted. It produced no predictions, metrics, or checkpoint. Its retry therefore satisfies PROTOCOL-AMENDMENT-008: an early `FAILED`/`ERROR` attempt, no model result and no metric-bearing output, followed by only one retry, below the maximum of three. The successful v2 kernel is byte-identical to the failed v1 rendered kernel; the execution route, not the scientific program, changed.

The checkpoint consumed by both successful M1 runs is:

`experiments/model1/EXP-R01/v1/run/weights/selected.pt`  
SHA-256 `0648da3f3641e3cdb5a1908a092ba892548942836a249bb3b39667f9ae8e8125`

It agrees with the selection record (epoch 91, unrounded fitness `0.760868639693682`), both receipts, both prediction-provenance records, and the frozen configuration.

The reconciled prediction records are:

- `EXP-V01`: 113 validation images; final predictions SHA begins `a35c76ba…`; raw predictions SHA begins `c184fed…`; configuration SHA begins `f736ef86…`.
- `EXP-R02`: 117 test images; final predictions SHA begins `a4de90…`; raw predictions SHA begins `e64c273…`; frozen-configuration SHA begins `b06081e9…`.

`EXP-R03` is the protocol's local M2 run, not a Kaggle attempt, so it correctly has no `kernel.py`, render record, platform receipt, or attempts ledger. Its equivalent chain reconciles: 219 predictions; predictions SHA begins `e3700dbf…`; run-record SHA begins `2368bf…`; weights SHA begins `e277717e…`; frozen-manifest SHA begins `cd4f0d0e…`; frozen configuration SHA begins `b06081e9…`; runtime SHA begins `f1a06a70…`; environment SHA begins `64086b29…`; and producer `src/evaluation/predict_model2.py` SHA begins `dc981256…`.

## 3. Frozen-output reproduction

I removed only the target generated outputs in the disposable clone, ran the literal frozen commands, and compared the regenerated files byte-for-byte with HEAD. Every listed output was identical. The clone returned to a clean tracked state after reproduction.

| Reproduction | Result | Principal reproduced file SHA-256 |
|---|---|---|
| M1 validation scoring, `evaluation.json`, `EXP-V01` | Exact | predictions `a35c76ba…`; metrics `778c62e9…` |
| Operating-point freeze | Exact | config `b06081e926d01753cd276d2a3535b2f1e8a5975e7de1db031dc8e786c714e228`; sidecar file `fa836cd…` |
| M1 test scoring, frozen config, `EXP-R02` | Exact | predictions `a4de90…`; metrics `5c3838…` |
| M1 intervals, seed 42, 2,000 resamples | Exact | `artifacts/metrics/model1_intervals.json` `1d2192a3…` |
| M2 intervals, seed 42, 2,000 resamples | Exact | `artifacts/metrics/model2_intervals.json` `03c922cb…` |
| M2 sensitivity and sibling artifacts | All five exact | main JSON `e20b87e…`; CSV `3ae8c4e…`; confusions `d9fc29e…`; shared draws `20aa4ae…`; report `1272afc…` |
| Validation operating-point table derivation | Exact | `experiments/model1/EXP-V01/metrics_frozen.json` `cbe441b…` |

The freeze independently reselected confidence `0.35` from validation predictions, with F2 `0.8843537414965986`, and recorded the exact validation-prediction hash. `validation_operating_point.py` is a derived validation scoring step needed because normal `--score` correctly refuses to relabel records produced under the pre-freeze configuration; it did not select a new operating point.

M2 inference was not repeated. Its saved predictions and run record are authenticated by the authority and interval commands. The benchmark was not repeated; it is checked below from its saved raw records.

## 4. Test discipline and chronology

### Freeze before test inference

Commit `96a5991` committed only `configs/evaluation_frozen.json` and its sidecar at `2026-09-28T15:07:35-05:00` (`20:07:35Z`). `EXP-R02` does not exist in its parent commit. The M1 test kernel was rendered later in commit `e7d8faf` at `15:26:52-05:00`.

The account snapshot at `20:27:52Z` contains no `EXP-R02` kernel. The receipt records the test kernel starting at `20:32:17.871752Z` and finishing at `20:32:50.450669Z`; the `20:34:44Z` account snapshot adds exactly that kernel. Thus the operating-point freeze was committed roughly 20 minutes before the test kernel existed.

### Absence of test-informed choice

- Checkpoint selection was committed on 2026-09-27 and used validation fitness only.
- M1 validation predictions were committed before the operating-point freeze.
- The threshold was selected only from those validation predictions under the frozen grid and lower-threshold tie rule.
- Before the freeze, the test-access ledger contains only historical declarations and the documented integrity probe, not test predictions, test metrics, or image inspection.
- After test execution, no checkpoint, threshold, evaluation method, class rule, or model source was changed. M1 intervals and M2 sensitivity derive uncertainty/secondary estimands from the already-saved test predictions; they do not reselect the primary result.
- The benchmark configuration setter mechanically copies the already-sealed M1 confidence and verifies the selected checkpoint hash. Its image pool is validation-only.

I found no test prediction, test metric, or test image that informed the checkpoint, operating point, or another scientific choice.

### Attach probe and access ledger

The committed DECISION-038/039 record states that the throwaway attach-probe kernels listed `/kaggle/input` and, when present, hashed the sealed checkpoint. The probe did not receive the image corpus and did not read a dataset image. It generated no scientific prediction or metric. Under the specified repository-root trust model, the committed decision/account record is the authority for this non-scientific probe; no external attestation is required.

`provenance/test_access_log.csv` is complete and consistent for this period:

- `TEST-ACCESS-004` records the single M1 test inference (`EXP-R02`);
- `TEST-ACCESS-005` records the single M2 test inference (`EXP-R03`);
- the prior integrity probe is separately recorded and did not perform inference; and
- the TASK-06 benchmark is not test access: I recomputed its 32-image pool from the manifest and confirmed every selected image has `proposed_split=val`.

The before/after account kernel lists show only one `EXP-R02` kernel. No contrary test exposure appears in the committed history.

## 5. Approval and the round-12 residual

PROTOCOL-AMENDMENT-008's Markdown SHA-256 is exactly the value in its JSON sidecar. Inference approval version 10 points to the committed round-12 review with matching SHA-256 `6a246c3ec03c3e9fbe876da8d501773cadc8d09e87888327267f3e93b595c57b` and names DECISION-037/039.

Fresh exact-HEAD calls to `authority.approved_inference` passed for both scopes:

- M1: all 13 approved authority files exactly equal the version-10 snapshot;
- M2: all 8 approved authority files exactly equal the version-10 snapshot; and
- both scopes authenticate the same recorded interpreter, environment, and runtime identities.

For the round-12 residual, `42270fa` added `._pth` to the authority code suffixes, included it in the complete installed-file inventory, anchored the interpreter to the committed base runtime, and rejects an unrecorded `python._pth`. The exact planted-`python._pth` regression test passed in `tests.test_authority_runtime`; the fresh approval calls also passed after full runtime identity verification.

**Round-12 `python._pth` residual: CLOSED.**

## 6. TASK-06 record audit

Without rerunning timing, I reconciled the committed benchmark inputs and raw records:

- `configs/benchmark.json` SHA begins `1e89b424…`, matching the run record;
- `m1_conf=0.35` equals the sealed validation freeze;
- the M1 weights hash is `0648da3f…`, exactly the selected/frozen checkpoint;
- the M2 weights hash begins `e277717e…`, matching ART-002 and the actual file;
- the recomputed deterministic 32-image pool equals `benchmark_raw_pool.csv`, whose SHA begins `ae41f90…`;
- the raw timing CSV SHA begins `2a8a5a…`, matching `benchmark_raw_run.json`;
- 44,800 stage rows equal 32 images × 100 measured repetitions × 14 stages;
- all 3,200 image repetitions contain the exact stage set, with status `ok` and no recorded errors; and
- recomputing the saved records gives the reported end-to-end median `239.4089 ms` and p95 `777.73907 ms`.

The committed benchmark is therefore a valid output of its frozen local-CPU protocol. The Raspberry Pi branch remains explicitly blocked by hardware and must not be inferred from this run.

## 7. Required test modules

Each requested module ran in its own fresh process in the exact-HEAD clone.

| Module | Result |
|---|---:|
| `tests.test_evaluation` | 60 passed |
| `tests.test_intervals` | 32 passed |
| `tests.test_predict_model2` | 9 passed |
| `tests.test_authority_runtime` | 27 passed |
| `tests.test_kaggle_job` | 44 passed |
| `tests.test_verify_kaggle_run` | 15 passed |
| `tests.test_benchmark` | 16 passed, 1 failed |
| **Total** | **203 passed, 1 failed, 204 run** |

The sole failure is `Config.test_shipped_config_refuses_while_m1_is_not_frozen`. It was introduced while the shipped `configs/benchmark.json` intentionally had `m1_conf=null`; the configuration was later promoted to the sealed `0.35`, but the test continued to expect rejection. The separate synthetic-null rejection coverage remains the appropriate negative contract.

## Final findings

| ID | Severity | Status | Location | Consequence | Resolution criterion |
|---|---|---|---|---|---|
| `RESIDUAL-DECISION-039` | HIGH at entry | **CLOSED** | `src/evaluation/evaluate.py`; `provenance/commands/task04/verify_kaggle_run.py` | No weakening found: only the rendered kernel or its single editor-comment form, modulo newline normalization, can pass; both compute the same program | Satisfied by source analysis, AST equivalence, receipt reconciliation, and passing altered-prefix tests |
| `RESIDUAL-ROUND12-PYTHON-PTH` | HIGH at entry | **CLOSED** | `src/evaluation/authority.py`; `tests/test_authority_runtime.py` | The previously unreviewed path-injection case is now inventoried and rejected; approved runtime scopes pass | Satisfied by exact regression test, source review, and fresh M1/M2 approval checks |
| `AUDIT-A-LOW-01` | LOW | **OPEN** | `tests/test_benchmark.py:182` (`Config.test_shipped_config_refuses_while_m1_is_not_frozen`) | The requested benchmark module is not green and no longer tests the promoted shipped configuration's positive contract; committed benchmark data and scientific results are unaffected | Replace the stale shipped-config refusal assertion with acceptance plus exact bindings to sealed `m1_conf` and the selected M1 weights; retain a separate temporary `null`-configuration rejection test; rerun the module |

**Open findings: HIGH = 0; MEDIUM = 0; LOW = 1.**
