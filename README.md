# Home Server Lab

A documented Raspberry Pi home-server build for Linux, Docker, automation, data projects, and self-hosted AI/lab-informatics workflows.

This repository tracks the setup, configuration, decisions, and lessons learned while building a small home server environment. The goal is to create a reliable technical foundation for future projects in clinical AI, cytogenetics data workflows, lab informatics, and secure self-hosted tools.

## Project Goals

- Build a stable Raspberry Pi home server
- Practice Linux administration and SSH workflows
- Learn Docker and containerized services
- Create reproducible setup documentation
- Develop good backup and security habits
- Host future portfolio projects and internal tools
- Support future AI, data, and lab-informatics experiments

## Current Hardware

- Raspberry Pi 5
- microSD or SSD boot/storage setup
- Home network access
- Chromebook used as the primary setup/admin machine

More exact hardware details will be added as the build evolves.

## Current Setup Status

- Raspberry Pi OS / Ubuntu Server setup in progress
- SSH access configured
- Local network access tested
- Hostname/local access being configured
- Documentation being created as the build progresses

## Planned Services

Possible future services include:

- Docker
- Portainer
- Uptime Kuma
- Pi-hole or AdGuard Home
- Tailscale
- Syncthing
- Samba file sharing
- GitHub project sync
- Local databases for practice projects
- Dashboards for lab-informatics portfolio work

## Repository Structure

```text
home-server-lab/
├── README.md
├── docs/
│   ├── setup-log.md
│   ├── network-notes.md
│   ├── ssh-notes.md
│   ├── security-checklist.md
│   └── backup-plan.md
├── docker/
│   └── compose-files/
├── scripts/
└── diagrams/
