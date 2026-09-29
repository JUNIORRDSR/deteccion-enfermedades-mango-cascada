# First independent adversarial review — PROTOCOL-AMENDMENT-009

Date: 2026-09-22  
Reviewer: Codex `/root`  
Review posture: hostile methodological referee  
Residual blind-check outcome: **not reviewed**; it is in progress and was excluded as instructed.

## Verdict

**PROTOCOL-AMENDMENT-009 may not be approved merely when the residual check completes, regardless of that check's outcome.** The current evidence shows that `sakit_mp4` is heterogeneous and is plausibly a montage, but it does not establish the amendment's proposed independence unit—physical-fruit identity—well enough to replace the frozen conservative rule. The residual design also conflicts with the frozen adjudication contract and does not close over the final partition.

The amendment can be reconsidered only after the resolution criteria below are met and a fresh independent review verifies them. A defensible fallback is to retain option A for the primary analysis and report its limited power, while treating B as a sensitivity analysis. A preferable hybrid is to exclude the montage from the primary test, or exhaustively divide all 432 items into atomic shot/fruit blocks and union blocks whenever identity is uncertain; the resulting groups can then be passed unchanged to the frozen section 6 algorithm.

**Open findings: HIGH = 5; MEDIUM = 4.** Two LOW findings are also open.

## Binding authority and checks performed

The binding authority was read before the amendment: `provenance/protocol_freeze.json` and `.md`, and SPEC sections 5, 6, and 11. The freeze JSON hash is `6d5aa3ff47cba97f8ecd0dd15683bb96f0d53146f3af1ce1e95bf24cec7cbc8b`, matching the abbreviated identity in the amendment; the frozen SPEC hash is `76ef27520460abb7c4c6eee76061adad59e9c6f34f203c1a941f41125d60ec8b`.

All reproduction work was in memory. No split CLI was run and no experimental output was written. The following positive facts were independently verified:

- Option B excludes the `sequence_cluster` container record in `split._relations(..., include_container_records=False)` and disables the sequence-name union in `build_groups(..., merge_sequence_hint=False)`. The inventory has exactly one non-empty sequence hint, `sakit_mp4` on 432 rows, so no other current sequence is accidentally affected. pHash clusters, adjudicated pair relations, and `extra_relations.csv` still merge visual identities. No other current path re-merges the whole montage.
- `dihedral_hashes` constructs the eight elements of the dihedral group, identity first. `rotation_invariant_distance` is correct for hashes produced by that function: by group closure, comparing all transforms of A to identity B covers every relative rotation/reflection. A fresh non-square random-image check returned distance zero in both directions for all eight transforms.
- The B draft exactly matches a fresh in-memory replay of the current relations and the frozen section 6 assignment. An independent exact-rational implementation produced the same assignment as `assign_groups`. The result is 669 images and 641 groups: train 464/464 groups, validation 102/87, test 103/90; the test has 48 groups carrying `Enfermo`. The block rule returns no reason.
- The draft is sorted by `image_id`, has 669 unique IDs, remains atomic by `group_id`, and has SHA-256 `fbfe99b956b5838de9b53e5c733a579b9bbd7af95116dff9ee6715ad1657545f`, matching its sidecar and proposal. All 669 image paths, label paths, image hashes, label hashes, and YOLO labels were checked; no mismatch was found. All 669 pHashes were recomputed with Pillow 12.2.0/ImageHash 4.3.2 and matched.
- The residual key contains one query for each of the 103 B-draft test images, five distinct non-test neighbours per query, and equivalent underlying panels for reviewers A and B.
- Fresh targeted tests passed: 29/29 across `tests.test_split`, `RotationInvariance`, and `Adjudications`.

These implementation checks establish faithful execution of the proposed B draft. They do not establish that B is the scientifically valid grouping rule.

## HIGH findings

### HIGH-01 — The montage evidence does not establish the proposed unit of independence

**Location:** `PROTOCOL-AMENDMENT-009-montage-grouping.md:21-29`; `reports/execution/task-02-audit-report.md:88-106`; `src/leakage_audit/adjudication.py:74-83,138-143`; `data/audits/model1/adjudications.csv`, `CAND-021`.

**Finding:** Both reviewers saw the same 16 systematically selected panels out of 432 (3.7%). The renderer takes every `len(members)//16`th ordered member; the displayed frames span approximately 0000, 0032, 0064, …, 0453. This is useful evidence against the narrow hypothesis that the file is one continuous shot, but it is not a probability sample of physical fruits and does not estimate how often fruits or acquisition setups recur. “15 scenes” is not “15 independent fruits.” Indeed, both reviewers identified panels 7–8 as the same fruit in different photographs.

The two supposed positive controls were not positive controls: they were consecutive frame numbers assumed, without ground truth, to be related. Both proved to be different photographs. Their failure refutes the assumption that consecutive numbering implies a common scene, but it provides no estimate of reviewer sensitivity. Two reviewers judging the same 16 panels provide replication of judgement, not 32 sampled observations.

**Scientific consequence:** B can fragment repeated fruits, shot sequences, or acquisition sessions across train/validation/test. The amendment therefore replaces a known conservative grouping with an incompletely measured and potentially anti-conservative grouping. The evidence supports “heterogeneous container” but not “432 mostly independent photographs” or “visual-identity components are sufficient independence units.”

**Resolution criterion:** Recover verifiable source/shot metadata, or perform a pre-specified blind assessment that directly measures the target relation. Given only 432 items, the strongest resolution is exhaustive shot-boundary and physical-fruit grouping, with all uncertain links merged conservatively. At minimum, use randomized/stratified sampling across temporal blocks plus dense adjacent windows, label physical-fruit identity separately from scene identity, include multiple verified positives and hard negatives, report recurrence/cluster-size uncertainty, and obtain an independent review of the sampling plan before using its results.

### HIGH-02 — Disclosure and user choice do not cure outcome-conditioned protocol selection

**Location:** `PROTOCOL-AMENDMENT-009-montage-grouping.md:31-38`; `docs/research/decision_log.md:88-92`; `data/manifests/model1_clean_manifest_B_draft.csv`; `reports/model1_split_proposal_B_draft.md:5-11`.

**Finding:** The disclosure is necessary and commendable, but it does not make the evidence independent of test size. The coordinator knew that A produced an unattractive diseased-test count before proposing B; the user was then shown both options and their consequences. User authorization satisfies a governance stop rule, not scientific independence. The user is not a blinded methodological adjudicator, and choosing the more informative-looking test after seeing its size remains an outcome-conditioned design choice even though no model predictions or metrics were viewed.

The dependence is material. In B, 65 of 103 test images and 58 of 90 test groups come from the disputed montage. Of the 48 test groups carrying `Enfermo`, 43 are montage groups; only five are non-montage groups. Thus nearly all of B's apparent gain in diseased-group count is produced by the rule being disputed.

**Scientific consequence:** The primary test's composition and effective sample size are selected after observing the consequence of the frozen rule. This creates design-selection bias and can make the final uncertainty look more informative without demonstrating that the added units are independent.

**Resolution criterion:** Have an independent reviewer apply a pre-specified evidence threshold without access to A/B balance counts, and retain a complete sensitivity analysis under A. If such independence is no longer attainable, use A (or montage exclusion) for the primary inference and label B exploratory/sensitivity-only. User choice and disclosure must remain recorded, but neither may be presented as curing the conflict.

### HIGH-03 — The residual merge rule violates the frozen adjudication contract

**Location:** frozen SPEC section 5; `PROTOCOL-AMENDMENT-009-montage-grouping.md:52-57`; `provenance/commands/amendment009/apply_residual.py:21-55,57-76`.

**Finding:** Frozen section 5 requires an A/B disagreement to remain `PENDING_SEPARATE_ADJUDICATION` until a separate third adjudicator resolves it, and requires the original A/B decisions, reviewer identities, agreement, evidence, rationale, adjudicator, timestamp, and blinding exceptions to be preserved. Amendment 009 says it modifies only the conservative video-grouping rule; it does not amend this adjudication contract.

`apply_residual.py` instead unions `a | b`, so any one-reviewer flag is immediately converted to `POSSIBLE_SEQUENCE_RELATION`. It emits only a pair, final label, and “flagged by” string. It does not preserve the complete required adjudication record, and it does not send disagreements to a third reviewer. It also calculates control scores but never blocks application when the positive controls fail, despite amendment section 6 making positive-control detection an approval condition.

**Scientific consequence:** A single unconfirmed judgement can alter components and the entire deterministic split, while the audit trail cannot reconstruct the two original decisions under the frozen schema. A failed calibration can still produce a nominally successful application.

**Resolution criterion:** Follow the frozen rule: every one-reviewer-only flag remains pending until a third blinded adjudicator decides it; persist a complete row in the frozen adjudication schema and preserve the original answer artifacts and hashes. Enforce the pre-registered positive-control gate before creating any final manifest. Any intended departure from these requirements must be stated as an additional material protocol change and independently approved before answers are inspected.

### HIGH-04 — `k=5`, the embedding, and the controls provide no defensible error calibration

**Location:** `PROTOCOL-AMENDMENT-009-montage-grouping.md:52-57`; `provenance/commands/amendment009/residual_packets.py:1-10,78-97`; `data/audits/model1/residual_key.json`.

**Finding:** `k=5` was chosen after inspecting where the sole known same-fruit/different-photo pair ranked. That is a calibration on one positive, not evidence of recall. The two positive controls are duplicate presentations of that same pair, so there is still only one positive case. The negative controls are random non-test images, not visually similar different fruits from the nearest-neighbour decision region. They do not measure the false-positive behaviour that matters for an at-least-one-reviewer rule.

A generic ImageNet full-image embedding is acceptable as a candidate generator, but it is not an identity detector. It may rank background, colour, watermark, crop, or scene more strongly than fruit identity. The known pair demonstrates only that this one pair appears at non-test-neighbour rank 5; it says nothing about other poses, lighting, occlusions, multiple-fruit scenes, or background changes.

**Scientific consequence:** A negative residual outcome cannot be read as evidence that no same-fruit relation remains, and a positive outcome may contain unmeasured false positives. Without hard negatives, even apparent control success does not calibrate specificity in the nearest-neighbour regime. Individual visually convincing pairs may still be useful grouping evidence, but the aggregate residual result is uninterpretable as validation of split independence. The statement that the rule “cannot inflate results” is false: false-positive merges can change group ordering, global assignment, test composition, class balance, and the estimand in either direction.

**Resolution criterion:** Construct a calibration set independent of the target decisions with multiple verified same-fruit positives spanning relevant transformations and hard negatives drawn from high-similarity neighbours. Pre-specify and meet recall@k and false-positive acceptance thresholds, preferably with leave-one-fruit/source-out evaluation. Choose `k` from that calibration with uncertainty, not from the single motivating pair. Use fruit crops or a justified ensemble if full-image embeddings fail the required recall. Keep visual adjudication as the decision layer.

### HIGH-05 — The residual design does not close over the final partition and leaves known pending candidates

**Location:** `PROTOCOL-AMENDMENT-009-montage-grouping.md:54-63,65-67`; `provenance/commands/amendment009/apply_residual.py:1-7,65-76`; `data/audits/model1/rotation_candidates.csv`; `data/audits/model1/embedding_candidates.csv`; `data/audits/model1/residual_key.json`.

**Finding:** The residual packets cover only the current B-draft test versus current non-test. Merging relations and recomputing the greedy split can introduce different test images, but the design explicitly does not review those new members. It also excludes train↔validation, although leakage there can influence checkpoint and operating-point selection.

This is not merely theoretical. The rotation audit has seven rows, all still `PENDING_ADJUDICATION`. Under the B draft, `SRC-009819` is in test and `SRC-009899` is in train; their rotation-invariant pHash distance is 10, but the non-test neighbour is rank 22 by the residual embedding and is absent from the five-neighbour panel. `SRC-009714`↔`SRC-010765` remains a pending train↔validation candidate. The top-40 embedding artifact has ten pairs that cross B splits; its test-boundary pairs happen to be in the residual panels, but six train↔validation pairs are outside the residual design.

**Scientific consequence:** The final partition can contain an already-known, unadjudicated test/train candidate, newly introduced unchecked test members, and train/validation relations. Completing the current packets therefore cannot establish the atomicity required by frozen sections 5–6.

**Resolution criterion:** Resolve every pending rotation/embedding candidate that crosses the proposed B split. Preferably construct and adjudicate the candidate graph across all 669 images before assignment, then split once. If test-dependent querying is retained, repeat blinded candidate generation and adjudication until group relations and test membership reach a documented fixed point, and run a final all-boundary atomicity audit. Approval requires zero pending relation that could alter grouping, including train↔validation.

## MEDIUM findings

### MEDIUM-01 — The disclosed option-A consequence is not reproducible from retained artifacts

**Location:** `PROTOCOL-AMENDMENT-009-montage-grouping.md:33`; `docs/research/decision_log.md:88-92`; absence of an A manifest/proposal alongside the retained B draft.

**Finding:** No option-A manifest, command record, relation-set hash, or proposal is retained. With the current adjudications and resolution file, an in-memory run of current code under A yields 114 test images and 10 test groups carrying `Enfermo`. Omitting the adjudicated sensitivity-band edges reproduces 112 test images but 16 groups carrying `Enfermo`. Neither replay reproduces “9 diseased images from 9 groups.” This may reflect an unpublished intermediate relation set or a different definition of “diseased image,” but that definition and input state are absent.

**Scientific consequence:** The consequence presented to the user, and hence the informed A/B choice, cannot be audited against the final evidence set.

**Resolution criterion:** Retain an exact A manifest and proposal generated from the same final audit artifacts and code revision as B, with command, input hashes, output hash, and an explicit definition of image-, instance-, and group-level `Enfermo` counts. Correct the amendment and decision record if the retained count differs.

### MEDIUM-02 — The residual embedding cache is not cryptographically or semantically bound to ART-004

**Location:** `provenance/commands/amendment009/residual_packets.py:53-76`; `embedding_summary.json`; `data/derived/embeddings_art004.npy`.

**Finding:** `embedding_candidates.py` verifies the ART-004 weight hash, but `residual_packets.py` loads `embeddings_art004.npy` whenever it exists without checking a cache hash, model hash, input-manifest hash, preprocessing/runtime versions, shape, normalization, or an ordered ID sidecar. If the cache is absent, it loads the weight path without verifying the ART-004 hash. The observed cache is finite, normalized, shaped 669×256, and has SHA-256 `28914dd71ed8a4f8ad551ca921825337707b92c50cc4bb39a296b7cbcd91ec3d`, but no retained artifact binds those bytes to the claimed model and ordered inputs.

**Scientific consequence:** A stale or differently generated cache can silently change nearest neighbours while the narrative continues to identify ART-004.

**Resolution criterion:** Record and verify the cache hash, ART-004 hash, ordered image IDs and image hashes, model/runtime/preprocessing versions, vector shape/dtype, and normalization. Fail closed on any mismatch; otherwise recompute from verified weights.

### MEDIUM-03 — `apply_residual.py` reports process success even when the split is blocked or fails

**Location:** `provenance/commands/amendment009/apply_residual.py:65-79`.

**Finding:** The subprocess return code is recorded in JSON, but `main()` always returns zero. A blocked split or execution failure can therefore look successful to an outer runner. Invalid residual panel numbers are also silently filtered rather than rejected for non-control questions.

**Scientific consequence:** Automation can advance the amendment state despite a blocked/failed split or malformed answer, contrary to fail-closed protocol gates.

**Resolution criterion:** Validate the answer schema and panel indices, fail on malformed values, propagate a nonzero split return code, and make the approval state depend explicitly on a successful final split plus all methodological gates—not merely creation of `residual_outcome.json`.

### MEDIUM-04 — The amendment and audit narrative overstate the evidence and contain stale contradictions

**Location:** `PROTOCOL-AMENDMENT-009-montage-grouping.md:23-29,35-38,54-56`; `reports/execution/task-02-audit-report.md:84-86,102-106,136-154`; `docs/research/decision_log.md:88-92`.

**Finding:** The documents move from “15 scenes in 16 panels” to “432 photographs mostly independent”; describe the evidence as independent of test size despite acknowledged prior knowledge; call assumed consecutive pairs “positive controls”; and state that the at-least-one merge rule cannot inflate results. The audit report calls the operationally adjudicated band relations “real contamination,” says the failed controls prove the reviewers were right, and still states at line 141 that the montage must not be split to improve numbers. Its final checklist says adjudication remains outstanding even though the preceding section presents it as complete.

**Scientific consequence:** Readers can mistake evidence of container heterogeneity for demonstrated biological independence, and can miss the unresolved protocol conflict and pending artifacts.

**Resolution criterion:** Replace absolute language with protocol-bounded statements: the sample detected heterogeneous scenes; visual identity outside reviewed candidates remains unresolved; reviewer agreement is operational evidence only; B may change results in either direction. Reconcile the audit report's provisional/stale sections, and state separately what is complete, pending, or superseded.

## LOW findings

### LOW-01 — The option-B switch is globally scoped even though the amendment is montage-specific

**Location:** `src/leakage_audit/split.py:175-176,207-213`.

**Finding:** The flag excludes every `sequence_cluster` record and disables all `sequence_hint` unions, not specifically `sakit_mp4`. The current inventory contains no other non-empty sequence hint, so this does not alter the present draft.

**Scientific consequence:** Reuse on a changed inventory could silently ungroup unrelated sequences beyond the approved exception.

**Resolution criterion:** Scope the exception to `sakit_mp4`, or fail unless the inventory proves it is the only affected sequence and record that invariant.

### LOW-02 — Tests cover the transform and generic grouping primitive, not the amendment's critical end-to-end contracts

**Location:** `tests/test_split.py:96-115`; `tests/test_leakage.py:280-316`; `provenance/commands/amendment009/green.log`.

**Finding:** Existing tests verify dihedral transforms and `merge_sequence_hint=False`, but not `_relations` excluding only the intended container, complete B-draft replay, residual disagreement handling, control gating, fixed-point coverage, cache identity, or propagation of a blocked split.

**Scientific consequence:** The high-risk behaviours above can regress while the retained GREEN log remains green.

**Resolution criterion:** Add the smallest deterministic tests for each amended contract before approval, including a disagreement requiring third adjudication, failed-positive-control block, post-merge test-membership change, pending cross-split candidate, and subprocess failure propagation.

## Could B be less independent than A?

Yes. A prevents every `sakit_mp4` relation from crossing a split, at the cost of a small and imprecise non-montage test. B is less independent whenever the montage revisits a fruit, acquisition setup, source image, burst, background, camera session, or uploader-specific domain in a way not captured by the visual-identity edges. Full-image embeddings can miss identity under pose/background change, and a five-neighbour horizon plus one recomputation does not rule that out. B's primary test is also dominated by the same montage source, so source/domain dependence can remain even if every physical fruit were distinct.

The preferred hybrid is:

1. Keep all montage material out of the primary test (or retain A) and honestly report the small effective diseased sample.
2. Exhaustively construct conservative shot/fruit components for the 432 montage items, merging uncertain blocks.
3. Report a secondary B-like evaluation as sensitivity/exploratory evidence, with cluster-aware uncertainty and without calling it a new independent holdout.

## Final approval statement

**No: PROTOCOL-AMENDMENT-009 may not be APPROVED simply once the current residual check completes.** Its outcome cannot repair the sampling, post-selection, adjudication-contract, calibration, and coverage defects in the current design. Approval requires a revised amendment and fresh independent review with **HIGH = 0 and MEDIUM = 0**.

Current open count: **5 HIGH, 4 MEDIUM**.
