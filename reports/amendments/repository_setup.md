# Canonical Git and worktree setup

AMENDMENT-01 authorization is recorded in provenance/authorizations/2026-09-18-conditional-approval.txt.

The repository exists exclusively at C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/.git. Baseline 3990fa7c79b77224675449b9bb676e650c47bbaf contains the 141 documentary files previously delivered (18,344,555 bytes). No scientific data images or model weights were imported. No Git LFS or remote was added. Local identity was already configured; no global settings were changed. core.autocrlf=false is local so baseline bytes are preserved.

Commit c0463636d2288ba3370d34914c27e47b11a5e30f adds ignore rules for worktrees, virtual environment, runtime caches, derived/raw data views and large checkpoints/packages. Small manifests, code, reports, predictions and metrics are versioned. Before staging each task, inspect sizes and index paths; large outputs remain local with path/hash/size in registries. Do not use git add -f on large assets.

Execution uses revision/execute-approved-plan at .worktrees/execution inside the authorized revision directory. Its git-dir differs from git-common-dir and it is not a submodule. The native app worktree tool targets the calling task repository and offers no repository-directory parameter; the task's containing cwd is not a Git repo. It therefore cannot select this newly initialized nested repo. The skill's Git fallback was used with an ignored .worktrees path. No legacy .git was changed.

The skill sdd-workspace script ran through Git Bash and created the plan-specific ignored ledger. No package setup ran: runtime installation is TASK-01 and still gated. Baseline verification is byte identity with the approved documents, not a claim of scientific tests passing. Source/hash and legacy status verification is in pre_execution_integrity.json.

All path resolution for new science must use logical roots supplied by TASK-01; do not interpret the worktree parent as the legacy corpus. Historical first-phase scripts remain records of their original absolute context, not portable execution commands.
