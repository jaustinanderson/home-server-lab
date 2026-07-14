# Home Server Lab

![Shell checks](https://github.com/jaustinanderson/home-server-lab/actions/workflows/shellcheck.yml/badge.svg)

A public-safe, two-machine home-lab project for Linux administration, secure remote access, infrastructure-as-code, Docker, data engineering, and future clinical-AI experimentation.

This repository documents the real architecture, decisions, validation steps, and lessons learned while building a small self-hosted environment. It is part of my transition from clinical cytogenetics into clinical AI, laboratory informatics, data systems, and practical software engineering.

> **Canonical project state:** read [`STATUS.md`](STATUS.md) first. Architectural decisions and their rationale are recorded in [`DECISIONS.md`](DECISIONS.md). Older documents under `docs/` provide useful background, but `STATUS.md` is the source of truth when details disagree.

## Current Architecture

| Machine | Hardware | Role | Operating system |
|---|---|---|---|
| **compute-node** | GMKtec M8, Ryzen 5 PRO 6650H, 16 GB RAM, 1 TB NVMe | Working storage, data services, and future AI compute | Ubuntu Server 26.04 |
| **pi-server** | Raspberry Pi 5, 8 GB RAM, 2 TB external SSD | Bulk archive, intended backup target, and lightweight services | Ubuntu Server 26.04 |
| **Chromebook** | Acer Chromebook Plus 514 | SSH control surface through the Linux terminal | ChromeOS |

Network addresses, MAC addresses, credentials, private keys, and other operational secrets are intentionally excluded from this public repository.

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
│   └── project-roadmap.md
├── docker/
│   └── compose-files/
│       └── README.md
├── scripts/
│   ├── README.md
│   └── system-info.sh
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
- [`docs/project-roadmap.md`](docs/project-roadmap.md) — phased path from foundation to data and AI projects
- [`diagrams/home-lab-architecture.md`](diagrams/home-lab-architecture.md) — current public-safe topology and planned backup flow
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — change workflow, validation expectations, and scope control
- [`SECURITY.md`](SECURITY.md) — reporting and response guidance for security or data-safety problems
- [`LICENSE`](LICENSE) — MIT License

## Current Utility Script

[`scripts/system-info.sh`](scripts/system-info.sh) prints operating-system, kernel, memory, disk, CPU, temperature, network-link, and Docker-status information. Its default output omits network addresses and unique CPU serials, but local paths and device context should still be reviewed before sharing.

Run it locally on a lab machine:

```bash
chmod +x scripts/system-info.sh
./scripts/system-info.sh
```

Review output before publishing it. Public-safe defaults reduce accidental disclosure; they do not replace a human review of copied terminal output.

## Continuous Checks

GitHub Actions runs ShellCheck against repository shell scripts on pushes and pull requests. This provides a lightweight quality gate while the repository is still infrastructure- and documentation-focused.

## Security Model

This is a public portfolio repository. Do not commit:

- Passwords, tokens, API keys, recovery codes, or `.env` files
- SSH private keys
- Public or private operational IP addresses
- MAC addresses or device identifiers
- Router, Wi-Fi, or Tailscale secrets
- Patient data, accession numbers, MRNs, or clinical-system screenshots
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

Current focus is **Phase 3 — Core Linux Administration**:

1. Establish a regular patching cadence across both machines
2. Practice and document package and service administration
3. Collect sanitized system baselines with the system-information script
4. Document users, permissions, and storage/filesystem checks
5. Add log-inspection and troubleshooting notes

Docker and the first containerized service remain **Phase 4**; PostgreSQL, dataset ingestion, and the Track A/Track B branches follow in later phases.

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
