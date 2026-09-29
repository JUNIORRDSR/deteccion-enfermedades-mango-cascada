# TASK-05 independent methodological review — round 6

Date: 2026-09-27  
Reviewed repository state: `b1b0d2f6bbcadadd9a24c381e9c66f88503f3f93`  
Scope: prospective inference-approval review after `e1ad6c0` and `86f1308`. No research inference, Kaggle call, network write, product-code fix, repository commit, push, or change under the real `experiments/` tree was performed. All mutable replays used disposable repositories outside the worktree.

## Verdict

**DO NOT APPROVE the combined inference snapshot yet.** The M1 chain is now approvable: HIGH-04, NEW-HIGH-01, and NEW-HIGH-03 are closed, the proposed M1 hashes match the committed repository, EXP-R01 reconciles exactly, and the complete post-approval M1 command sequence has no legitimate-run rejection.

The common approval still includes M2, where two HIGH issues remain. First, NEW-HIGH-05 is only partially closed: the bundle and approved producer are now Git-rooted, but the environment and canonical config named in the round-5 resolution criterion are not authenticated. An untracked in-checkout `ultralytics` substitute produced EXP-R03 through the unchanged approved `predict_model2.py`; after the prescribed promotion commit, both M2 interval consumers accepted it. Second, the producer itself never checks `inference_approved`, so the literal EXP-R03 command completed in a disposable copy while the real amendment state was still `inference_approved=false` / `inference_approval.state=PROPOSED`.

These findings do not ask for a custodian, signatures, or Kaggle/platform attestation. The committed Git repository remains the root of trust. The required correction is only to put the actual M2 producer environment/config and the pre-inference approval check inside that declared root.

**Open count: HIGH = 2; MEDIUM = 0.**

## Binding authority and review basis

Read before review:

- immutable `provenance/protocol_freeze.json` and `.md`;
- SPEC §§6, 7, 11, and 12;
- frozen plan TASK-05 and its literal commands;
- PROTOCOL-AMENDMENT-008 §§4, 5, and proposed §5.1;
- `reports/execution/task-05-independent-review-round5.md`.

Section 4 of Amendment 008 declares that there is no independent custodian and that the local and Kaggle venues share that limitation. This review therefore asks whether committed Git identities, the approval snapshot, and the promoted result are enforced. It does not ask the code to prove that a trusted committer could not fabricate all repository evidence.

The repository advanced during the review from `41adf65` to `b1b0d2f` through a TASK-06 commit. A final check at `b1b0d2f` confirmed that none of the 15 proposed TASK-05 authority identities changed.

## Fresh verification

Each requested module completed in its own fresh Python process with bytecode disabled. The complete runs, excluding an earlier discarded wrapper timeout, were:

| Command | Result |
|---|---|
| `.\.venv\Scripts\python.exe -m unittest tests.test_evaluation -v` | 56 passed; exit 0; 108.628 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_intervals -v` | 31 passed; exit 0; 23.933 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_predict_model2 -v` | 6 passed; exit 0; 0.024 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_kaggle_job -v` | 44 passed; exit 0; 0.208 s |
| `.\.venv\Scripts\python.exe -m unittest tests.test_verify_kaggle_run -v` | 14 passed; exit 0; 5.272 s |
| **Total** | **151 passed; 0 failures/errors** |

The suite includes the new verifier/snapshot/promotion regressions. It does not cover the two M2 failures described below.

## Round-5 finding disposition and counterexample replay

The verifier and replacement-chain replays used the real sealed code copied into fresh temporary Git repositories. The M2 replay used a fresh temporary repository with the same authority and interval code.

| Round-5 finding | Round-6 status | Replay evidence |
|---|---|---|
| **HIGH-04 — attempt root evaluated by an unrooted verifier** | **CLOSED** | `verify_kaggle_run.py` is now in `authority.SEALED_CODE` and in the exact M1 approval snapshot. An untracked altered verifier was rejected because the M1 authorities were not committed-clean. After committing the altered verifier, it was rejected because the M1 authorities differed from the approved snapshot. `_verifier()` was reached only after `approved_inference()` checked those bytes. |
| **NEW-HIGH-01 — threshold authentication depended on HIGH-04** | **CLOSED** | The freezer reaches validation records only through `verified_provenance` → `rebuilt` → `attempt_root`. The altered-verifier replay was rejected before re-reconciliation or F2 selection, closing the remaining route for the fully rehashed 0.05 substitution. `tests.test_evaluation.ReviewRound4.test_an_altered_verifier_outside_the_approved_snapshot_is_refused` passed. |
| **NEW-HIGH-03 — approval not bound to reviewed authority snapshot** | **CLOSED** | In one post-approval commit, the replay replaced checkpoint bytes (SHA256 `d814c177…e4e175c`), selection record, kernel version `9`, evaluation config, and evaluator. `freeze_operating_point` rejected it with `the m1 authorities differ from the snapshot the review approved`. All exact M1 hashes are now compared before freezing or consuming test results. |
| **NEW-HIGH-05 — EXP-R03 predictions lack an authenticated producer root** | **PARTIALLY CLOSED / OPEN** | The exact round-5 unpromoted self-authored predictions/sidecar/run-record bundle now exits 2: `the EXP-R03 predictions, sidecar and run record must be committed`. The amended promotion step and approved producer SHA are enforced. A promoted self-authored bundle is accepted as a Git-root assertion, which is expected under the declared trust model. However, the producer environment and canonical config are not part of the authenticated assertion: a bundle produced through an untracked substitute backend was promoted and accepted by both consumers. |

The last distinction is deliberate and proportionate. Detecting a trusted committer inventing a promoted record would require a stronger trust model that the protocol rejects. Detecting an untracked or wrong inference dependency/config is different: those bytes are outside the declared root even when the approved producer source itself is unchanged.

## Real-repository snapshot and EXP-R01 checks

### Proposed inference snapshot

For every entry in `inference_approval.m1` and `.m2`, the proposed SHA256 equalled both the current filesystem bytes and the `HEAD` blob. All files were tracked and clean.

| Scope | Entries | Result |
|---|---:|---|
| M1 | 10 | 10/10 equal to proposed SHA256 and committed blob |
| M2 | 5 | 5/5 equal to proposed SHA256 and committed blob |
| **Total** | **15** | **15/15 equal** |

This includes `authority.py`, `verify_kaggle_run.py`, the M1 and M2 manifests/sidecars, the M1 freeze record and EXP-R01 selection record, and every evaluation/producer/consumer source named in the amendment.

### Evaluation config, manifest, and training selection

The real committed identities reconcile:

| Identity | Verified value |
|---|---|
| M1 checkpoint / `selected.pt` | `0648da3f3641e3cdb5a1908a092ba892548942836a249bb3b39667f9ae8e8125` |
| EXP-R01 selection record SHA256 | `4a67bdca43a1c6a782dc6bb172702fcb36ebfcbe9caaa4c73f01808bcb98706c` |
| Training kernel version | `1` |
| M1 manifest SHA256 | `dd9431dd7bbc00c6117baf6a0f6cf49eff8bc55f144016b4a98dbdea049ecf5f` |
| Selected epoch / fitness | `91` / `0.760868639693682` |

`configs/evaluation.json` matches the selection record for checkpoint, selection-record hash, and kernel version. Its manifest identity matches the committed manifest bytes, the `.sha256` sidecar, `model1_clean_manifest.freeze.json`, and the EXP-R01 render record.

### Pure EXP-R01 reconciliation

On the real repository, read-only calls to `verify_kaggle_run.py` reproduced:

- `reconciliation.json` byte-for-byte;
- the sole definitive `attempts.jsonl` entry;
- `selection_record.json` byte-for-byte;
- the selected checkpoint hash from `v1/run/weights/selected.pt`;
- the receipt/render payload relationship and all 552 verified train/validation files.

All 13 reconciliation/config/manifest checks passed. The verifier CLI was not invoked in finalizing mode on the real repository.

## Frozen command-sequence assessment

A disposable clone of the real `b1b0d2f` tree was used. Only that clone's Amendment JSON was changed to `inference_approved=true` and `inference_approval.state=APPROVED`, then committed there. The approval JSON is intentionally not an entry in its own authority snapshot.

No Kaggle call was made. To exercise downstream interfaces without creating research observations, downloaded M1 predictions were represented by deterministic synthetic receipts over the real frozen manifest, and the M2 inference backend was replaced by a deterministic stub. The real manifest memberships, labels/images, hashes, ART-002 bytes, producer code, authority checks, promotion steps, and literal CLIs were retained.

| Ordered step | Result |
|---|---|
| Render EXP-V01 v1 against the real manifest/checkpoint | Passed; 113 validation images selected, 556 excluded |
| Represent download, run `verify_kaggle_run.py`, commit definitive EXP-V01 | Passed; reconciliation and ledger created and committed in the disposable clone |
| Literal `evaluate --model-id model1 --config configs/evaluation.json --split val --run-dir experiments/model1/EXP-V01` | Passed |
| Literal operating-point freeze | Passed; synthetic replay selected the expected lower-tie grid value `0.05` |
| Commit frozen config and EXP-V01 products | Passed |
| Render EXP-R02 v1 from committed frozen config | Passed; 117 test images selected, 552 excluded |
| Represent download, reconcile, commit definitive EXP-R02 | Passed |
| Literal M1 test evaluation | Passed |
| Literal M1 intervals, seed 42 / 2,000 draws | Passed; exit 0 in 313.6 s |
| Literal `evaluate --model-id model2 ... EXP-R03` with a non-scientific deterministic backend | Passed; producer validated real ART-002 and all 219 test image hashes and wrote the expected bundle |
| Commit the three-file EXP-R03 promotion bundle | Passed |
| Literal primary M2 intervals, seed 42 / 2,000 draws | Passed |
| Literal M2 sensitivity, seed 42 / 2,000 draws | Passed |

Thus no path, parser, hash-field, or ordering defect rejects a legitimate **post-approval** run. This does not cure the pre-approval and environment-authentication defects below.

## Open findings

### NEW-HIGH-05 — HIGH — EXP-R03 promotion authenticates the producer source but not the producer environment/config

- **Status:** PARTIALLY CLOSED / OPEN.
- **Location:** `src/evaluation/predict_model2.py:68-120`; `src/evaluation/provenance.py:228-266`; `src/evaluation/authority.py:45-52`; `src/statistics/intervals.py:599-656`; Amendment 008 §5.1 “Productor de EXP-R03”.
- **Evidence:** in the approved disposable sequence, an untracked `ultralytics` module inside the checkout shadowed the installed dependency. The unchanged approved `predict_model2.py` accepted it, recorded version `8.4.52-synthetic-sequence-replay`, and generated the 219-row bundle. The prescribed promotion committed only predictions, sidecar, and run record—not the substitute backend. `authenticate_m2` checks producer SHA but ignores the run record's `ultralytics` and `config_sha256`; both the primary interval command and sensitivity command accepted the promoted bundle. Separately, a self-authored bundle without promotion was correctly rejected.
- **Consequence:** the committed result can be attributed to the approved producer while its probabilities came from inference code/environment outside the approved Git snapshot. This changes all EXP-R03 point estimates and intervals and leaves the environment/config part of the round-5 resolution criterion unenforced.
- **Resolution criterion:** before EXP-R03, bind a committed canonical config and reconstructed environment identity to the M2 approval/promotion contract; require the imported Ultralytics/runtime identity and origin to match that authority; and have `authenticate_m2` verify those fields rather than merely preserve them. Add a negative test with an in-checkout shadow module and an arbitrary config: inference or promotion must fail. No independent custodian, signature, or platform attestation is required.

### NEW-HIGH-06 — HIGH — EXP-R03 inference executes before inference approval

- **Location:** `src/evaluation/evaluate.py:768-775`; `src/evaluation/predict_model2.py:68-120`; contrast `src/evaluation/evaluate.py:410-417,490-501` for the M1 gate.
- **Evidence:** a disposable clone retained the real amendment state `APPROVED`, `inference_approved=false`, `inference_approval.state=PROPOSED`. With a harmless deterministic backend and an arbitrary `{}` config, the literal frozen M2 command exited 0, validated ART-002 and the 219 frozen test images, and wrote a complete EXP-R03 bundle. Neither the dispatcher nor `predict_model2.run` calls `authority.approved_inference(root, 'm2')`. Downstream refusal before promotion cannot undo a first test observation.
- **Consequence:** the one-time M2 test can be observed before the independent approval whose purpose is to authorize it. This defeats the prospective inference gate even though later interval consumers enforce promotion.
- **Resolution criterion:** call the M2 approval validator before creating the run directory, importing the model runtime, or reading/inferencing any test image; require the canonical committed config intended by the literal command. Add a test with the current false/PROPOSED state that proves exit 2, no model call, and no EXP-R03 directory. After changing the M2 authority set, refresh the proposed snapshot and repeat independent review.

## Per-step approval decision

| Step | Decision | Reason |
|---|---:|---|
| EXP-V01 | **APPROVABLE in isolation** | Exact authority snapshot, verifier, attempt root, checkpoint, config, and manifest are enforced. |
| Operating-point freeze | **APPROVABLE in isolation** | It rebuilds only the authenticated EXP-V01 attempt and rejects post-approval authority replacement. |
| EXP-R02 | **APPROVABLE in isolation** | Frozen config, test selection, attempt root, and evaluator identities are enforced. |
| M1 interval command | **APPROVABLE in isolation** | It revalidates the frozen config and authenticated EXP-R02 predictions. |
| EXP-R03 | **NO** | It is callable before approval and does not authenticate the inference environment/config. |
| Primary M2 interval command | **NO** | Promotion is enforced, but the promoted producer environment/config is not. |
| M2 sensitivity command | **NO** | Same unauthenticated EXP-R03 source as the primary M2 intervals. |

Because Amendment 008 exposes one common `inference_approved` switch for both scopes, the M1-only positive assessment is not a recommendation to flip it now. The combined snapshot must remain unapproved until both M2 HIGH findings are closed and the affected M2 snapshot is independently re-reviewed.

## Final finding table

| ID | Severity | Status | Blocks |
|---|---:|---|---|
| HIGH-04 | HIGH | CLOSED | — |
| NEW-HIGH-01 | HIGH | CLOSED | — |
| NEW-HIGH-03 | HIGH | CLOSED | — |
| NEW-HIGH-05 | HIGH | PARTIALLY CLOSED / OPEN | EXP-R03, primary M2 intervals, M2 sensitivity |
| NEW-HIGH-06 | HIGH | OPEN | EXP-R03 and all downstream M2 results |

**Open count: HIGH = 2; MEDIUM = 0. Overall verdict: DO NOT APPROVE the combined inference snapshot.**
