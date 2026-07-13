# Contributing to Home Server Lab

Home Server Lab is a public-safe infrastructure learning project. Contributions should improve reproducibility, security, verification, documentation, or operational clarity without exposing the live environment.

## Read First

- [`STATUS.md`](STATUS.md) is the canonical current state.
- [`DECISIONS.md`](DECISIONS.md) records architectural decisions and rationale.
- The README and `docs/` provide public-safe context and runbooks.

When documents disagree, update them deliberately and preserve `STATUS.md` as the source of truth.

## Session Start Gate

Before making any change in a work session, reconcile against **live GitHub** — it is authoritative. Chat history, memory, and pasted summaries are only leads.

1. Confirm the default branch, the current `main` HEAD, and the open pull requests and their refs with `git ls-remote` (git protocol — do not depend on the rate-limited REST API).
2. Read the current canonical files (`STATUS.md`, `DECISIONS.md`, `docs/project-roadmap.md`, `CONTRIBUTING.md`, `README.md`) from `raw.githubusercontent.com`.
3. Treat any GitHub response whose body is a rate-limit notice or other error as **unverified** — never parse an error body as data.
4. When working from a lab machine, reconcile the local clone read-only before branching:
   - `git fetch --prune origin`
   - `git status --short --branch`
   - `git branch -vv`
   - `git log --oneline --decorate -5 origin/main`
5. Report any difference between memory, the local clone, and live GitHub before proceeding.

Do not begin work based solely on remembered state.

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
