# Home Server Lab

A documented Raspberry Pi home-server build for Linux, Docker, automation, data projects, and self-hosted AI/lab-informatics workflows.

This repository tracks the setup, configuration, decisions, and lessons learned while building a small home server environment. The goal is to create a reliable technical foundation for future projects in clinical AI, cytogenetics data workflows, lab informatics, and secure self-hosted tools.

## Project Purpose

This project is part of my broader career transition from clinical cytogenetics into clinical AI, laboratory informatics, data workflows, and practical automation.

The home server is being used as a real learning environment for:

* Linux administration
* SSH workflows
* Raspberry Pi infrastructure
* Docker and containerized services
* Secure self-hosted tools
* Backup and recovery planning
* Public-safe technical documentation
* Future AI, data, and lab-informatics projects

## Project Goals

* Build a stable Raspberry Pi home server
* Practice Linux administration and SSH workflows
* Learn Docker and containerized services
* Create reproducible setup documentation
* Develop good backup and security habits
* Host future portfolio projects and internal tools
* Support future AI, data, and lab-informatics experiments
* Document the build in a way that is useful to future employers, collaborators, and technical mentors

## Current Hardware

* Raspberry Pi 5
* microSD or SSD boot/storage setup
* Chromebook used as the primary setup/admin machine
* Home network access

More exact hardware details will be added as the build evolves.

## Current Setup Status

* GitHub account rebranded for professional portfolio use
* `home-server-lab` repository created
* Initial project README created
* Documentation folder created
* SSH notes started
* Network notes started
* Security checklist created
* Backup plan created
* Project roadmap created
* Docker folder structure created
* Scripts folder structure created
* Diagrams folder structure created
* First utility script added

## Repository Map

```text
home-server-lab/
├── README.md
├── .gitignore
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
    └── README.md
```

## Documentation

* [`docs/setup-log.md`](docs/setup-log.md) — Build log, setup history, and public-safe progress notes
* [`docs/ssh-notes.md`](docs/ssh-notes.md) — SSH access notes, hostname strategy, and troubleshooting
* [`docs/network-notes.md`](docs/network-notes.md) — Network setup, DHCP/hostname notes, and managed-network limitations
* [`docs/security-checklist.md`](docs/security-checklist.md) — Public repo safety, SSH security, Docker security, and data privacy rules
* [`docs/backup-plan.md`](docs/backup-plan.md) — Backup philosophy, restore planning, and safe backup boundaries
* [`docs/project-roadmap.md`](docs/project-roadmap.md) — Development phases and future project direction

## Project Folders

* [`docker/compose-files/`](docker/compose-files/) — Future Docker Compose templates and service deployment notes
* [`scripts/`](scripts/) — Public-safe utility scripts for server administration and automation
* [`diagrams/`](diagrams/) — Architecture, network, Docker, backup, and future AI/lab-informatics diagrams

## Current Utility Scripts

* [`scripts/system-info.sh`](scripts/system-info.sh) — Prints public-safe system information for the Raspberry Pi home-server lab

## Planned Services

Possible future services include:

* Docker
* Portainer
* Uptime Kuma
* Pi-hole or AdGuard Home
* Tailscale
* Syncthing
* Samba file sharing
* GitHub project sync
* Local databases for practice projects
* Dashboards for lab-informatics portfolio work

## Security Principles

This is a public portfolio repository, so it must remain public-safe.

Do not commit:

* Passwords
* SSH private keys
* API keys
* Tokens
* `.env` files
* Personal network secrets
* Public IP addresses
* Patient data
* Employer-confidential data
* Clinical system screenshots
* Real accession numbers, MRNs, case IDs, or sample identifiers

Use instead:

* Synthetic examples
* Public datasets
* Mock data
* Sanitized placeholders
* General workflow diagrams
* Public-safe documentation

## Why This Project Matters

This project is not just about running a Raspberry Pi.

It is a practical infrastructure lab for building the habits needed in clinical AI, laboratory informatics, and technical project work:

* Clear documentation
* Repeatable setup
* Version control
* Security awareness
* Backup planning
* Systems thinking
* Troubleshooting discipline
* Public-safe technical communication

## Career Relevance

My background is in clinical cytogenetics, including chromosome analysis, FISH workflows, metaphase imaging, and clinical laboratory operations.

This repository helps connect that laboratory experience to technical skills in:

* Linux
* GitHub
* Docker
* Server administration
* Automation
* Data engineering fundamentals
* AI-ready infrastructure
* Lab-informatics project design

## Current Status

```text
Foundation phase in progress.
```

## Next Technical Milestones

* Pull this repository onto the Raspberry Pi
* Make `scripts/system-info.sh` executable
* Run the system information script
* Add sanitized system notes to `docs/setup-log.md`
* Confirm operating system version
* Confirm hostname
* Confirm final SSH access method
* Install Docker
* Add first Docker Compose example
* Add first architecture diagram
* Begin documenting actual service deployments

## Future Repository Connections

This home-server repository may eventually support or connect to:

* `metaphase-data-pipeline`
* `cytogenetics-python-notebooks`
* `clinical-ai-lab-informatics`
* `portfolio-site`

## Project Philosophy

Build slowly, document clearly, and keep everything public-safe.

The goal is not to create a flashy demo. The goal is to develop durable technical competence that can support real AI, data, and laboratory informatics projects.
