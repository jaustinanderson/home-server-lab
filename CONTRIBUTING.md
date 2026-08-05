# Contributing to Home Server Lab

Home Server Lab is a public-safe infrastructure learning project. Contributions should improve reproducibility, security, verification, documentation, or operational clarity without exposing the live environment.

## Read First

- [`STATUS.md`](STATUS.md) is the canonical current state.
- [`DECISIONS.md`](DECISIONS.md) records architectural decisions and rationale.
- The README and `docs/` provide public-safe context and runbooks.

When documents disagree, update them deliberately and preserve `STATUS.md` as the source of truth.

## Session Start and Continuity Gate

Before answering a current-status or next-step question, recommending or running a machine command, or
making any repository change, reconcile against **live GitHub**. GitHub is authoritative for repository
content, intended state, and sanitized progress records. Read-only inspection of the live device is
authoritative for actual operational state. Chat history, memory, screenshots, and pasted summaries are
evidence, but none is a sufficient checkpoint by itself.

A **verified remote checkpoint** is either a pushed commit whose remote SHA was confirmed or a sanitized
checkpoint recorded on the canonical GitHub issue or pull request. A local commit, terminal output, or
conversation-only summary does not qualify.

Treat the session as continuity-sensitive when any of these conditions applies:

- At least four hours have passed since the last verified checkpoint.
- The calendar date changed, a terminal/device/session restarted, or an SSH connection was interrupted.
- The user says `continue`, `resume`, `overnight`, or otherwise returns after a material pause.
- The last checkpoint time or the outcome of any persistent step is unknown.

Run this gate before any mutation:

1. Record the current timestamp and identify the latest verified remote checkpoint and its timestamp.
2. Confirm the default branch, the current `main` HEAD, and the open pull requests and their refs with
   `git ls-remote` (git protocol — do not depend on the rate-limited REST API).
3. Read the current canonical files (`STATUS.md`, `DECISIONS.md`, `docs/project-roadmap.md`,
   `CONTRIBUTING.md`, `README.md`) from live GitHub, plus the active issue and pull request.
4. Treat any GitHub response whose body is a rate-limit notice or other error as **unverified** — never parse
   an error body as data.
5. If the session is continuity-sensitive, search backward to the last verified remote checkpoint and
   reconstruct every material action after it. Do not assume the most recent conversational summary is the
   most complete one.
6. Before any machine or repository command, confirm the shell is on the **intended host** — the prompt must
   identify it (for example `<private-user>@compute-node`). If an SSH session has dropped, or the prompt
   shows a different machine (such as the Penguin container), **stop**: reconnect to the intended host and
   discard evidence gathered on the wrong host before continuing.
7. When working from a lab machine, reconcile the local clone read-only before branching:
   - `git fetch --prune origin`
   - `git status --short --branch`
   - `git branch -vv`
   - `git log --oneline --decorate -5 origin/main`
8. Reconcile GitHub's recorded state and the post-checkpoint history with read-only live checks for every
   material operational fact. Unknown does not mean absent or incomplete.
9. Report any difference between memory, historical evidence, the local clone, open issues/pull requests,
   live `main`, and the target device before proceeding. Distinguish facts merged to `main`, facts recorded
   only in an open pull request or issue checkpoint, and verified live operational facts.
10. Record the `main` commit or retrieval time used and state one exact resume point. If live GitHub cannot
    be read, label the state **unverified** and stop rather than filling the gap from memory.

### Duplication-prevention gate

Before proposing or running a non-idempotent or secret-bearing step — including account, package,
credential, mount, repository initialization, service, timer, or persistent configuration creation — all
three sources must agree that the step is incomplete:

1. The canonical GitHub issue/checkpoint records it as incomplete.
2. The reconstructed history since the last verified checkpoint contains no completed proof.
3. A read-only check on the intended target shows the state is absent or incomplete.

If any source conflicts or remains unknown, stop and reconcile. Do not repeat the operation. A script's
`already exists` guard is a last safety net, not a substitute for this gate. Track each material step as
`not-started`, `in-progress`, `verified`, or `unknown`; `unknown` always requires read-only verification.

### Checkpoint and handoff gate

- Record a sanitized remote checkpoint after every persistent major gate and no later than 60 minutes into
  state-changing work.
- Before a planned pause of at least one hour, or at the end of a session, stop at an atomic boundary and
  checkpoint before giving another state-changing instruction.
- Push repository changes to the existing focused branch and verify the remote SHA. Update an existing pull
  request rather than creating a duplicate. For operational work, update the canonical issue with sanitized
  evidence even when no repository file changed.
- Use [`docs/session-checkpoint-template.md`](docs/session-checkpoint-template.md). Record the timestamp,
  issue, branch, local and remote SHAs, pull-request state, verified completed steps, live/temporary state,
  dirty-tree exclusions, exact next gate, and blockers or unknowns.
- Never commit credentials, private paths, operational addresses, raw logs, or sensitive screenshots. Record
  secret metadata only: purpose, storage class, ownership/mode verification, and verification date.
- If GitHub is unavailable, create a sanitized `REMOTE_BACKUP_PENDING` local checkpoint, stop further
  persistent changes at the next safe boundary, and make remote upload/verification the first recovery
  action.
- If older history is unavailable or truncated, say continuity is `unknown`; use the latest GitHub checkpoint
  plus read-only live checks to reconstruct state, and do not run a non-idempotent or secret-bearing step
  until the uncertainty is resolved.

Do not answer a current-state question or begin work based solely on remembered state.

### Portfolio continuity boundary

Home Server Lab is a **major project** with one dedicated primary repository. This repository is
authoritative for its code, public-safe technical documentation, decisions, issues, pull requests, and
sanitized checkpoints. The read-only live environment remains authoritative for actual operational state.

Private portfolio and knowledge-system records are derived summaries, not competing sources of truth:

- Project status flows from verified live state to this repository, then from this repository to the
  private project summary used for cross-project links and synthesis.
- Personal interpretation, ideas, and cross-project connections may originate in the private knowledge
  system, but an actionable technical decision is not authoritative here until it is deliberately promoted
  into a repository issue, decision, or pull request.
- A private vault backup proves only that the vault was backed up. It does not prove that its Home Server
  Lab summary reflects the latest repository checkpoint.
- Never edit or restore the private vault by changing its GitHub mirror from this repository workflow.

After a material merge, milestone, decision, architecture change, blocker, or dependency change, set
`knowledge_projection` to `required` in the checkpoint. Reconcile the derived project summary within seven
days for an active project and before cross-project planning that depends on the change. Ordinary code-only
commits may be marked `not-material`. A stale derived summary does not authorize changing correct repository
state; record the drift and refresh the summary from the verified repository.

Keep three clocks separate: the repository checkpoint time, the private project-summary refresh time, and
the private vault-backup verification time. Never use one as evidence for another.

## Public-Safety Rules

Do not add:

- Passwords, private keys, tokens, recovery codes, or `.env` files
- Real operational IP, Tailscale, or MAC addresses
- Router, Wi-Fi, account, or device secrets
- Unsanitized command output or screenshots
- Patient data, employer-confidential information, or proprietary clinical-system content

Use placeholders, generalized diagrams, synthetic examples, and sanitized evidence.

## Change Workflow

1. Create a focused branch from `main`.
2. Read the current status and relevant decision records.
3. Make the smallest coherent change.
4. Validate scripts and configuration locally or in a disposable environment.
5. Update `STATUS.md` and append a dated changelog entry when the current state changes.
6. Add or update a decision record when the architecture, security model, or operating policy changes.
7. Open a pull request with verification evidence and explicit safety confirmation.

## Shell Scripts

- Use `#!/usr/bin/env bash` when Bash is required.
- Prefer `set -euo pipefail` when failure behavior is understood and appropriate.
- Quote expansions unless word splitting is intentional.
- Avoid printing secrets or unnecessary network identifiers.
- Pass ShellCheck before merging.
- Run `bash scripts/test-system-info-safety.sh` after changing shared diagnostic output.
- Run `python3 scripts/check-markdown-links.py` after changing Markdown structure.
- Document prerequisites, side effects, and rollback behavior.

## Docker and Configuration

- Prefer reproducible Compose files over undocumented manual container commands.
- Pin versions deliberately where reproducibility or compatibility requires it.
- Keep secrets outside Git and reference them through documented local mechanisms.
- Define volumes, networks, health checks, restart behavior, backups, updates, and removal procedures.
- Do not expose services publicly without a separately reviewed threat model.

## Pull-Request Expectations

State:

- What changed and why
- Which machine or architectural role the change concerns
- How the change was tested
- What evidence confirms the expected result
- Whether `STATUS.md` or `DECISIONS.md` changed
- Whether rollback was tested or documented
- Confirmation that all public material is sanitized

## Scope Control

Large additions such as public service exposure, authentication systems, new storage architecture, production data, or major platform changes require a separate proposal and decision record. They should not be bundled into routine documentation or maintenance work.
