# Session Checkpoint Template

Use this public-safe template after each persistent major gate, at least every 60 minutes of state-changing
work, and before a planned pause of one hour or more. Store the completed checkpoint in the canonical GitHub
issue or pull request; commit it only when it represents durable repository state.

```text
timestamp:
continuity_state: verified | unknown | REMOTE_BACKUP_PENDING
issue:
step_id:
branch:
local_sha:
remote_sha:
pull_request:
verified_completed:
live_state:
temporary_state:
secret_metadata_only:
worktree_exclusions:
portfolio_impact: none | related-projects-affected
affected_projects:
knowledge_projection: current | not-material | required | unknown
next_incomplete_gate:
blockers_or_unknowns:
```

Rules:

- A remote checkpoint requires a confirmed pushed SHA or a sanitized GitHub issue/PR record.
- Use stable step IDs and the states `not-started`, `in-progress`, `verified`, or `unknown`.
- Record only sanitized conclusions. Do not include credentials, secret values, private paths, account or
  share names, operational addresses, raw logs, or screenshots.
- If interrupted mid-step, record it as `unknown` or `in-progress`; the next session starts with read-only
  verification, not a rerun.
- Mark `knowledge_projection: required` after a material status, milestone, decision, architecture, blocker,
  or dependency change. Do not include private note paths, backlinks, or personal synthesis in this public
  checkpoint.
- If GitHub cannot be reached, use `REMOTE_BACKUP_PENDING`, stop further persistent work at the next safe
  boundary, and upload/verify this checkpoint before resuming.
