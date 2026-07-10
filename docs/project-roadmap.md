# Project Roadmap

This roadmap defines the phased development path for the two-machine Home Server Lab. Current completion and operational facts are tracked in [`../STATUS.md`](../STATUS.md); architectural rationale is tracked in [`../DECISIONS.md`](../DECISIONS.md).

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

## Phase 2: Repository-on-Host Workflow — Next

Goal: manage the infrastructure repository from the lab machines instead of relying only on browser uploads.

Tasks:

- Clone `home-server-lab` onto the appropriate machine or machines
- Configure GitHub authentication for push access
- Confirm branch, commit, push, and pull-request workflow
- Keep operational secrets out of the public repository
- Document the standard change workflow
- Confirm rollback and recovery procedures for configuration changes

Success evidence:

- A branch created from a lab machine
- A sanitized documentation or configuration change committed and pushed
- A pull request reviewed and merged

## Phase 3: Core Linux Administration

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

- `docs/linux-command-notes.md`
- `docs/troubleshooting-log.md`
- Sanitized system baselines

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

Goal: make data placement and recovery intentional.

Tasks:

- Define hot, working, archive, and backup storage roles
- Decide what belongs on compute-node versus pi-server
- Define backup frequency and retention
- Separate code, datasets, databases, configuration, and secrets
- Run a documented restore test
- Record recovery time and gaps
- Evaluate future NAS integration without treating storage as backup by default

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

Goal: ingest one public cytogenetics or related biomedical dataset end to end.

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
