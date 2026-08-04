# Home Server Lab Agent Instructions

These instructions apply to every AI collaborator working in this repository.

1. Before a current-state answer, next-step recommendation, machine command, or repository mutation, read
   `CONTRIBUTING.md` and complete its **Session Start and Continuity Gate** against live GitHub.
2. Treat `STATUS.md` as the canonical repository status and the live target's read-only state as canonical
   for operational facts. Conversation memory is evidence, never the only checkpoint.
3. After a gap of four hours or more, a date/session/device restart, an interrupted command, an explicit
   resume, or an unknown checkpoint, search backward to the last verified remote checkpoint and reconcile
   every material action after it.
4. Never repeat a non-idempotent or secret-bearing step unless GitHub, post-checkpoint history, and a
   read-only target check all show it is incomplete. A conflict or unknown state is a stop condition.
5. Record sanitized progress on GitHub after each persistent major gate, at least every 60 minutes of
   state-changing work, and before a planned pause of at least one hour. Verify the remote SHA or issue/PR
   checkpoint before continuing.
6. Preserve unrelated user changes and all public-safety boundaries. Never commit secrets, private paths,
   operational addresses, raw logs, or sensitive screenshots.

Use `docs/session-checkpoint-template.md` for every interruption or end-of-session handoff.
