# Project Roadmap

This roadmap defines the phased development path for the Home Server Lab's Linux hosts, Synology storage,
and protected data workflows. Current completion and operational facts are tracked in
[`../STATUS.md`](../STATUS.md); architectural rationale is tracked in
[`../DECISIONS.md`](../DECISIONS.md).

The lab exists to build practical infrastructure skills and support future public-data, synthetic-data, AI, and laboratory-informatics projects.

## Phase 1: Foundation and Secure Access — Complete

Goal: establish a stable, reachable, documented, and independently verified base.

Completed:

- Ubuntu Server installed and verified on compute-node and pi-server
- SSH keys deployed from the Chromebook to both machines
- Password-based SSH disabled and independently tested
- Conflicting SSH configuration fragments removed
- Tailscale installed and verified across all three devices
- Remote SSH tested without public port forwarding
- Reboot recovery and Tailscale startup verified
- Security and backup boundaries documented
- Canonical `STATUS.md` and `DECISIONS.md` established
- Legacy Pi-only documentation reconciled with the two-machine architecture

## Phase 2: Repository-on-Host Workflow — Complete

Goal: manage the infrastructure repository from the lab machines instead of relying only on browser uploads.

Tasks:

- Clone `home-server-lab` onto the appropriate machine or machines
- Configure GitHub authentication for push access
- Confirm branch, commit, push, and pull-request workflow
- Keep operational secrets out of the public repository
- Document the standard change workflow
- Confirm rollback and recovery procedures for configuration changes

Completed evidence:

- Repository cloned onto compute-node over SSH
- Dedicated GitHub SSH authentication verified (passphrase-protected key, host key checked, `ssh -T` greeting)
- Branch push proven from the lab machine
- First real sanitized compute-node-originated change committed, pushed, and merged
- Pull request reviewed and merged through the Austin-controlled D17 workflow (PR #6)
- Durable Session Start Gate added to `CONTRIBUTING.md` (live-GitHub reconciliation before each session)

## Phase 3: Core Linux Administration — In Progress

Goal: make routine server administration repeatable and evidence-driven.

Tasks:

- Establish a patching cadence
- Practice package and service management
- Document users, groups, ownership, and permissions
- Add log-inspection and troubleshooting notes
- Document storage and filesystem checks
- Use the system-information script on both machines
- Add public-safe evidence of verification

Planned artifacts:

- `docs/patching-cadence.md` — **added**: the D18 patching policy and monthly runbook
- `docs/troubleshooting-log.md` — **added**: first sanitized Phase 3 findings
- `docs/linux-command-notes.md` — **added**: users, groups, sudo, ownership/modes, umask, and effective SSH policy
- Sanitized system baselines

Current evidence: the **D18** patching cadence is established and exercised on both machines. The compute-node
canary completed 38 upgrades with 0 removed and needed no reboot. pi-server completed the same reviewed
transaction counts, then passed a deliberate staged kernel reboot, boot-slot validation, lifeline checks,
and a second fresh SSH connection. Both machines left two legitimate phased deferrals. The
users/groups/ownership/permissions inventory is also complete: both hosts run a single sudo-capable login
account with locked root and key-only SSH, and each had its login user removed from the unused `lxd` group
(wrapper-only; verified in a fresh session). A recorded, unresolved divergence remains — pi-server's
passwordless sudo versus compute-node's password-required sudo. The read-only Linux storage/filesystem
review is complete and recorded in `docs/storage-baseline.md`. Remaining Phase 3 work — refreshed system
baselines and deliberate log-inspection practice — continues.

## Phase 3.5: NAS Storage Readiness — In Progress

Goal: make the DS925+ a protected, recoverable source archive before any metaphase corpus is acquired.

Current evidence:

- DS925+ with Btrfs on a one-drive SHR pool is owner-confirmed healthy but has no drive-failure protection.
- Synology Hyper Backup to Backblaze B2 is owner-confirmed operational for current personal NAS content on
  a daily schedule with version retention.
- A second matching 16 TB drive is expected on 2026-07-28 but is not installed or verified.
- No metaphase share, `compute-node` mount, provenance workflow, checksum gate, or successful restore test is
  claimed yet.

Required gates:

- Add the second drive to the existing SHR pool; wait for synchronization; verify both drives and the
  protected pool healthy.
- Run and record appropriate drive-health checks and enable storage/backup failure notifications.
- Create the dedicated metaphase archive boundary and least-privilege access model.
- Verify `compute-node` access while keeping canonical raw source material separate from working copies.
- Require source, version, license, acquisition date, checksum, classification, intended use, and
  transformation history for every dataset.
- Restore a protected sample into a disposable location and verify it independently.
- Run one small public-data pilot through quarantine → provenance/license review → checksum → archive →
  working copy → restore.

Planned artifacts:

- `docs/storage-baseline.md` — **added**
- `docs/nas-readiness-checklist.md` — **added**
- `docs/backup-restore-test.md`

Bulk acquisition remains Phase 8. Passing Phase 3.5 authorizes only a bounded first public-data pilot; it
does not authorize patient, employer, uncertain-origin, or unrestricted corpus ingestion.

## Phase 4: Docker and Service Lifecycle

Goal: deploy the first service reproducibly with Docker Compose.

Tasks:

- Install Docker Engine and Compose where needed
- Confirm service and user permissions
- Run a minimal test container
- Choose the first useful service
- Add a Compose file with explicit volumes, networks, health checks, and restart behavior
- Document start, stop, update, backup, and recovery procedures
- Avoid committing secrets

Candidate first services:

- Uptime Kuma
- Portainer
- A lightweight dashboard
- PostgreSQL, if selected as the first data service

## Phase 5: Monitoring and Maintenance

Goal: detect failures and understand resource health.

Tasks:

- Track uptime and service availability
- Track disk usage and temperature
- Document alerting behavior
- Record update and restart procedures
- Add routine maintenance checklists
- Test recovery after reboot or service failure

Potential tools:

- Uptime Kuma
- Netdata
- Native systemd and journal tooling
- Simple scripted checks

## Phase 6: Storage, Backup, and Restore

Goal: complete the full multi-device recovery model for services and irreplaceable project data.

Tasks:

- Apply the D19 roles: NAS source archive, compute-node working tier, pi-server local secondary protection
- Define backup frequency and retention
- Separate code, datasets, databases, configuration, and secrets
- Implement and monitor the planned local second-copy flow
- Extend off-site protection to irreplaceable project data with a documented scope
- Run a documented restore test
- Record recovery time and gaps
- Review the design after each protected service is introduced; SHR remains redundancy, not backup

Planned artifact:

- `docs/backup-restore-test.md`

## Phase 7: PostgreSQL and Provenance Foundation

Goal: establish the first durable data service for Track A.

Tasks:

- Decide whether PostgreSQL runs on compute-node or pi-server
- Deploy it through a reproducible configuration
- Define database backup and restore procedures
- Create a dataset provenance-manifest schema
- Record source, license, checksum, acquisition date, transformations, and intended use
- Validate constraints and migration behavior

This phase is the beginning of the cytogenetics data-pipeline track, not merely a database installation exercise.

## Phase 8: Public Dataset Ingestion

Goal: scale the proven Phase 3.5 pilot into a governed public cytogenetics or related biomedical dataset
ingestion workflow.

Tasks:

- Confirm license and redistribution rules
- Download through a reproducible process
- Verify checksums
- Populate the provenance manifest
- Store raw data immutably
- Create a working derivative through a documented transformation
- Produce validation and QC output
- Demonstrate recovery from source plus manifest

No patient data, employer data, or internal clinical material is permitted.

## Phase 9: Project Tracks

### Track A: Cytogenetics image and data pipeline

Potential work:

- Public or synthetic metaphase/karyogram organization
- Metadata and provenance models
- Image quality-control experiments
- Search and retrieval
- Reproducible preprocessing
- Lightweight local inference experiments where hardware permits

### Track B: Laboratory workflow automation

Potential work:

- Synthetic workload or point-tracking model
- Data import and validation
- Rule-based scoring
- Audit history
- Exception handling
- Reports and dashboards

Track B is likely the smaller first product because it does not require GPU resources or large image datasets.

## Phase 10: Portfolio Integration

Goal: make the project legible and credible to employers and collaborators.

Tasks:

- Keep `STATUS.md` and README current
- Maintain an architectural decision record
- Add diagrams based on the real architecture
- Include verification evidence, not unsupported claims
- Write a concise case study and retrospective
- Link related portfolio projects
- Keep all public material sanitized

## Success Criteria

The Home Server Lab is successful when it demonstrates:

- Practical Linux administration
- Secure remote-access design
- Independent verification of security controls
- Infrastructure-as-code and version-control discipline
- Docker and service lifecycle management
- Backup and restore competence
- Data provenance and reproducibility
- Evidence-based troubleshooting
- Public-safe technical communication
- A credible foundation for clinical AI and laboratory informatics projects
