# Diagrams

This folder contains public-safe diagrams of the Home Server Lab. Diagrams must
match verified state in [`../STATUS.md`](../STATUS.md) and clearly label planned
flows that are not yet implemented.

## Current diagrams

- [`home-lab-architecture.md`](home-lab-architecture.md) — Chromebook control
  surface, private Tailscale access, the two server roles, local connectivity,
  and the planned backup direction

## Planned diagrams

Add these only when the corresponding systems exist:

- Docker service topology for the first deployed service
- Backup and restore flow after the first successful restore test
- PostgreSQL and dataset-provenance data flow
- Track A and Track B application topology

## Standards

Every diagram must:

- Be understandable without operational addresses or device identifiers
- Distinguish verified components from proposals
- Avoid public IPs, MAC addresses, Wi-Fi details, private service URLs, account
  identifiers, credentials, and screenshots of live systems
- Exclude patient data, employer material, real case identifiers, and
  proprietary clinical-system content
- Be updated in the same change that alters the documented architecture

Prefer compact Mermaid diagrams in Markdown so GitHub renders them and the
source remains reviewable in version control.
