# Home Server Lab

![Repository checks](https://github.com/jaustinanderson/home-server-lab/actions/workflows/shellcheck.yml/badge.svg)

A public-safe, multi-device home-lab project for Linux administration, secure remote access, resilient storage, infrastructure-as-code, Docker, data engineering, and future clinical-AI experimentation.

This repository documents the real architecture, decisions, validation steps, and lessons learned while building a small self-hosted environment. It is part of my transition from clinical cytogenetics into clinical AI, laboratory informatics, data systems, and practical software engineering.

> **Canonical project state:** read [`STATUS.md`](STATUS.md) first. Architectural decisions and their rationale are recorded in [`DECISIONS.md`](DECISIONS.md). Older documents under `docs/` provide useful background, but `STATUS.md` is the source of truth when details disagree.

## Current Architecture

| Machine | Hardware | Role | Operating system |
|---|---|---|---|
| **compute-node** | GMKtec M8, Ryzen 5 PRO 6650H, 16 GB RAM, 1 TB NVMe | Hot working storage, data services, and future AI compute | Ubuntu Server 26.04 |
| **pi-server** | Raspberry Pi 5, 8 GB RAM, 2 TB external SSD | Planned local secondary protection and lightweight services | Ubuntu Server 26.04 |
| **Synology NAS** | DS925+, Btrfs on SHR, two matching 16 TB drives, one-drive fault tolerance | Canonical source archive and current personal-content store | Synology DSM |
| **Chromebook** | Acer Chromebook Plus 514 | SSH control surface through the Linux terminal | ChromeOS |

Network addresses, MAC addresses, credentials, private keys, and other operational secrets are intentionally excluded from this public repository.

Both matching 16 TB drives are installed in one healthy SHR pool with one-drive fault tolerance and
approximately 13.8 TB usable capacity. Both drives passed extended S.M.A.R.T. tests, the first data scrub
completed successfully, quarterly scrubbing is scheduled, and DSM email alerts were tested. Synology Hyper
Backup is operational to Backblaze B2 for selected current personal content. A client-side-encrypted,
checksum-verified disposable restore passed on 2026-07-31; this proves recovery for the tested fixture and
backup version, not for future metaphase data.

## Verified Foundation

The infrastructure foundation is complete and independently verified:

- Ubuntu Server installed and verified on both servers
- SSH key authentication working from the Chromebook to both servers
- Password-based SSH disabled and tested from an external client
- Tailscale installed on all three devices for private remote access
- Remote SSH verified without public port forwarding
- Tailscale startup and unattended recovery verified after a `compute-node` reboot
- mDNS hostnames working between the two servers
- Public-safe project state and architectural decisions stored in GitHub
- Security and backup boundaries documented
- Synology NAS incorporated into the canonical storage architecture (D19)
- Healthy two-drive SHR protection, extended drive tests, tested DSM email alerts, and scheduled scrubbing
- Daily client-side-encrypted, versioned Hyper Backup to Backblaze B2, with one checksum-verified disposable restore
- Authenticated Git workflow from compute-node: SSH clone, dedicated key, and branch → commit → push → pull-request → review → merge proven end to end (D17)
- A durable Session Start Gate requiring live-GitHub reconciliation before each work session

The next work builds on this stable base rather than repeating initial setup.

## Project Tracks

### Track A: Cytogenetics data and AI pipeline

A future containerized workflow for organizing public or synthetic cytogenetic images and associated metadata. Planned work includes provenance manifests, relational data modeling, ingestion pipelines, quality-control documentation, and lightweight AI experiments.

### Track B: Laboratory workflow automation

A synthetic-data project modeling a manual laboratory workload or point-tracking process as a reproducible data workflow. This is the smaller and more operationally focused first application track.

Neither track will use patient data, employer-confidential material, internal procedures, or proprietary clinical-system content.

## Repository Map

```text
home-server-lab/
├── README.md
├── STATUS.md                 # canonical current state
├── DECISIONS.md              # architectural decision log
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
├── .gitignore
├── .github/
│   ├── dependabot.yml
│   ├── pull_request_template.md
│   └── workflows/
│       └── shellcheck.yml
├── docs/
│   ├── setup-log.md
│   ├── ssh-notes.md
│   ├── network-notes.md
│   ├── security-checklist.md
│   ├── backup-plan.md
│   ├── backup-restore-test.md
│   ├── storage-baseline.md
│   ├── nas-readiness-checklist.md
│   ├── metaphase-archive-boundary.md
│   ├── linux-command-notes.md
│   ├── patching-cadence.md
│   ├── troubleshooting-log.md
│   └── project-roadmap.md
├── docker/
│   └── compose-files/
│       └── README.md
├── scripts/
│   ├── README.md
│   ├── system-info.sh
│   ├── test-system-info-safety.sh
│   └── check-markdown-links.py
└── diagrams/
    ├── README.md
    └── home-lab-architecture.md
```

## Documentation

- [`STATUS.md`](STATUS.md) — current machines, network model, completed verification, next work, and changelog
- [`DECISIONS.md`](DECISIONS.md) — architectural choices, alternatives, rationale, and consequences
- [`docs/setup-log.md`](docs/setup-log.md) — dated public-safe build history
- [`docs/ssh-notes.md`](docs/ssh-notes.md) — current SSH model, verification, commands, and troubleshooting
- [`docs/network-notes.md`](docs/network-notes.md) — managed-network constraints and private-access strategy
- [`docs/security-checklist.md`](docs/security-checklist.md) — public-repository and server-security rules
- [`docs/backup-plan.md`](docs/backup-plan.md) — backup philosophy, scope, and restore planning
- [`docs/backup-restore-test.md`](docs/backup-restore-test.md) — sanitized evidence from the checksum-verified Backblaze restore exercise
- [`docs/storage-baseline.md`](docs/storage-baseline.md) — sanitized Linux and NAS storage inventory and readiness gates
- [`docs/nas-readiness-checklist.md`](docs/nas-readiness-checklist.md) — second-drive, protection, access, and pilot-ingestion gate
- [`docs/metaphase-archive-boundary.md`](docs/metaphase-archive-boundary.md) — sanitized evidence for the dedicated metaphase archive share, least-privilege identity, and verified `compute-node` access (issue #17)
- [`docs/promotion-controls.md`](docs/promotion-controls.md) — public-safe manifest schema, fail-closed validator, synthetic fixture suite, and stop/rollback conditions for pre-promotion controls (issue #18)
- [`docs/linux-command-notes.md`](docs/linux-command-notes.md) — sanitized Linux users, permissions, sudo, and effective-policy notes
- [`docs/patching-cadence.md`](docs/patching-cadence.md) — update policy (D18): daily automatic security patching plus the monthly manual maintenance runbook
- [`docs/troubleshooting-log.md`](docs/troubleshooting-log.md) — dated, sanitized operational findings and lessons
- [`docs/project-roadmap.md`](docs/project-roadmap.md) — phased path from foundation to data and AI projects
- [`diagrams/home-lab-architecture.md`](diagrams/home-lab-architecture.md) — current public-safe topology and implemented/planned protection flows
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — change workflow, validation expectations, and scope control
- [`SECURITY.md`](SECURITY.md) — reporting and response guidance for security or data-safety problems
- [`LICENSE`](LICENSE) — MIT License

## Current Utility Script

[`scripts/system-info.sh`](scripts/system-info.sh) prints operating-system, kernel, memory, disk, CPU,
temperature, allowlisted network-link state, and Docker-status information. Its default output omits IP
addresses, MAC addresses, and unique CPU serials, but local paths and device context should still be reviewed
before sharing.

Run it locally on a lab machine:

```bash
chmod +x scripts/system-info.sh
./scripts/system-info.sh
```

Review output before publishing it. Public-safe defaults reduce accidental disclosure; they do not replace a human review of copied terminal output.

## Continuous Checks

GitHub Actions runs ShellCheck, a privacy regression for `system-info.sh`, the
promotion-manifest validator's automated tests (synthetic fixtures only), and a
repository-relative Markdown-link check on every push and pull request.

## Security Model

This is a public portfolio repository. Do not commit:

- Passwords, tokens, API keys, recovery codes, or `.env` files
- SSH private keys
- Public or private operational IP addresses
- MAC addresses or device identifiers
- Router, Wi-Fi, or Tailscale secrets
- Non-public patient-derived or clinical study data, even if de-identified
- Accession numbers, MRNs, or clinical-system screenshots
- Employer-confidential information or internal procedures

Use synthetic examples, placeholders, public datasets, generalized diagrams, and sanitized command output instead.

## Remote-Access Design

The lab is on an apartment-managed network without router administration or port forwarding. The design therefore uses:

- SSH keys instead of passwords
- Tailscale as the private mesh-VPN layer
- No public service exposure
- Friendly mDNS names where supported
- Tailnet addresses as the stable remote-access fallback

This design avoids depending on DHCP stability and does not require opening inbound internet ports.

## Near-Term Roadmap

**Phase 3 — Core Linux Administration is complete.** Current focus is **Phase 3.5 — NAS Storage Readiness**:

1. Patching cadence **established and exercised on both machines** (D18: daily security automation plus a monthly manual window)
2. Users, groups, ownership, and permissions **audited on both machines**
3. Storage/filesystem review **completed and promoted into the sanitized baseline**
4. Refreshed system baselines, deliberate log inspection, controlled reboots, and SSH aliases **verified**
5. NAS protection gate A **completed**: healthy one-drive-fault-tolerant SHR, both extended drive tests,
   tested email alerts, successful first scrub, and quarterly scrub schedule
6. Hyper Backup recovery proof **completed** for one disposable fixture
7. Dedicated metaphase archive share, least-privilege access model, and verified `compute-node` access
   **completed** (issue #17). Provenance/license/checksum promotion-control schema, fail-closed validator,
   and synthetic-fixture tests **completed** (issue #18); next implement the local-second-copy control
   (issue #19) before the one bounded public/synthetic pilot

The first small public-metaphase pilot may begin only after the Phase 3.5 protection, access, provenance,
checksum, backup, and restore prerequisites pass. Passing that bounded pilot completes Phase 3.5; bulk
acquisition remains later work. Docker remains **Phase 4** and begins only after Phases 3 and 3.5 complete.

See [`STATUS.md`](STATUS.md) for the authoritative order and current completion state.

## Why This Project Matters

The project is a practical environment for developing skills that transfer directly into clinical AI and laboratory informatics work:

- Linux and systems administration
- Secure access and operational verification
- Infrastructure-as-code and change control
- Networking under real environmental constraints
- Backup and recovery thinking
- Docker and service lifecycle management
- Data provenance and reproducibility
- Public-safe technical communication
- Evidence-based troubleshooting

## Project Philosophy

Build slowly, verify independently, document decisions, and keep public artifacts sanitized.

The goal is not merely to operate a Raspberry Pi or mini PC. The goal is to build durable engineering habits and infrastructure capable of supporting credible data, AI, and laboratory-informatics projects.
