# SDD ledger — plan: C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/.worktrees/execution/docs/superpowers/plans/2026-09-17-albus26-major-revision.md

## Setup
- User conditional approval: provenance/authorizations/2026-09-18-conditional-approval.txt.
- Baseline: 3990fa7c79b77224675449b9bb676e650c47bbaf (exact first-phase snapshot).
- Ignore setup: c0463636d2288ba3370d34914c27e47b11a5e30f.
- Active worktree: C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/.worktrees/execution, branch revision/execute-approved-plan.
- Amendments author: /root/amendment_author, documentation only. Independent delta review pending.
- GATE B/C: CONDITIONALLY_APPROVED, not satisfied yet. TASK-01 forbidden until no HIGH/MEDIUM delta findings and protocol freeze.

## Tasks
Task 1: pending
Task 2: pending
Task 3: pending
Task 4: pending (conditional scientific run)
Task 5: pending
Task 6: pending
Task 7: pending (GT branch conditional)
Task 8: pending
Task 9: pending
Task 10: pending

User instructions prevail over generic skill prompts: do not ask permission between covered ordinary tasks; continue independent work for known GT/Pi/historical-runtime blocks; never delete retained research evidence or publish/push. Preserve review artifacts and a tracked ledger copy in reports/execution/ before any optional scratch cleanup.

## Resumption 2026-09-19
- Candidate amendment commit: 963b03ecaa6585628f79142ffdddc6992dc238a5. Exact baseline delta: reports/amendments/delta-3990fa7-963b03e.diff; SHA256 bb4f3b1f09c11c8678586e86fbff12e41456724ae12ff16dd8c42eb59cc4cd95.
- Fresh reviewer /root/amendment_delta_review: compliance PASS, quality PASS_WITH_LOW; HIGH=0, MEDIUM=0, LOW=1 (ADR-LOW-01 PowerShell executable variables). Report retained in reports/amendments/independent_delta_review.md.
- Documentary fix before freeze dispatched to /root/amendment_command_fix; BASE963b03ecaa6585628f79142ffdddc6992dc238a5. No scientific task started.
- Fresh integrity: 11137 source files, zero hash differences, eight legacy Git checks match initial. reports/amendments/resumed_integrity_2026-09-19_attempt2.json: REVIEW18/TASK10/AMENDMENT7 coverage PASS. Prior literal matching coverage failure retained and explained.
- GATE B/C remains pending protocol freeze; no TASK-01 yet.

## Execution authorization
- ADR-LOW-01 corrected in 2e9b009 and independently re-reviewed PASS; open HIGH/MEDIUM/LOW=0.
- Approval record: c77e707, DECISION-026. Freeze: 7d0f9985cce73740cfa2ae26154971b55282ad52; JSON SHA256 6d5aa3ff47cba97f8ecd0dd15683bb96f0d53146f3af1ce1e95bf24cec7cbc8b.
- 2026-09-20T03:52:41.583330+00:00: GATE B/C SATISFIED; frozen bytes/sidecar/commits freshly verified after commit. DECISION-027 authorizes start.
- task-brief script was run but cannot recognize TASK-01 headings; fallback extracted unchanged TASK-01 and global/environment/provenance excerpts using anchored regex. No global skill or frozen plan edits.
- Literal .diff review packages preserve mandatory context-line spaces; whitespace checks exclude *.diff, whose exact hashes are independently verified.

## Task 1 in progress
- BASE: bead3604aa2f969c827e240d87e8a60b298c85c0. Fresh implementer: /root/task01_implementer.
- Brief: task-1-brief.md; report: task-1-report.md; durable implementation report: reports/execution/task-01-implementation.md.
- Reported milestone only, pending independent review: .venv Python3.12.14 created; RED missing module; initial GREEN5provenance tests; sidecar11137SRC and inputs ART001..004; package installation running.
- Coordinator parallel documentary bibliography work is isolated in .superpowers/sdd/2026-09-17-albus26-major-revision/bibliography_recon/: notes.md,16metadata access records with raw JSON/SHA, roboflow_access.json. Pass these to fresh TASK-08 implementer and retain final evidence before scratch cleanup. This does not complete TASK-08 or change protocol/manuscript.

## Resumption 2026-09-21 (Claude Code, coordinator)
- Resumed after the Codex session's usage limit. Found TASK-01 **not** complete: `tests.test_provenance.test_two_ids_cannot_map_one_logical_file` was RED. Implemented the missing ambiguity rejection in `validate_locations`.
- Fresh verification: 7/7 unittest OK; source CLI `checked=11137 discrepancies=0` with the uniqueness check active. The earlier zero-discrepancy run did not evidence uniqueness.
- Added `provenance/commands/task01/verify_runtime_paths.py`: four unguarded child processes. Guarded import contains all Ultralytics write paths and disables telemetry; unguarded import silently escapes to %APPDATA% and is asserted as a documented hazard. Every later CLI must call `configure_environment` before importing ultralytics/torch.
- Probed CUDA with torch: 2.12.0+cpu, `cuda_available=False`. Local GPU training impossible.
- Task 1: candidate commit `675c49c`; independent adversarial review DISPATCHED to Codex, verdict pending. Task 1 stays *in review*, not done.
- User authorized Kaggle GPU compute on 2026-09-21 (`provenance/authorizations/2026-09-21-kaggle-compute-authorization.md`). Tramitted as `PROTOCOL-AMENDMENT-008`, commit `4b198bd`, state PROPOSED. Kaggle GPU quota measured: 108000 s free, 0 used. ZERO Kaggle executions until its independent review closes.
- Preliminary TASK-02 documentary evidence (manifest only, no pHash, scratchpad note, not an audit artifact): DATA-001 has 669 unique SHAs and no binary cross-split duplicate, but 432/669 rows carry `sequence_name_hint=sakit_mp4` split 329/85/18 across train/valid/test, and 7 filename bases appear in two splits each with differing box counts, one of them crossing test<->valid. Feed to the TASK-02 implementer as mandatory blind-packet candidates.
