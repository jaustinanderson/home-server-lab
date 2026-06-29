# Project Roadmap

This roadmap defines the planned development path for the Raspberry Pi home-server lab.

The purpose of this project is to build practical infrastructure skills while creating a foundation for future AI, data, and clinical lab-informatics projects.

## Phase 1: Foundation

Goal: Get the server stable, reachable, documented, and safe to work on.

Tasks:

* Create GitHub repository
* Add professional README
* Add setup documentation
* Document SSH access
* Document network setup
* Add security checklist
* Add backup plan
* Confirm operating system
* Confirm hostname
* Confirm SSH command
* Run system updates

Status:

```text
In progress
```

## Phase 2: Core Linux Administration

Goal: Build confidence with normal server administration.

Tasks:

* Learn basic Linux navigation
* Practice package management
* Document useful commands
* Configure users and permissions
* Review service status commands
* Learn log inspection basics
* Document reboot and shutdown procedures
* Create troubleshooting notes

Planned documentation:

* `docs/linux-command-notes.md`
* `docs/troubleshooting-log.md`

## Phase 3: Docker Setup

Goal: Install Docker and begin running services in a reproducible way.

Tasks:

* Install Docker
* Install Docker Compose
* Confirm Docker service status
* Run a test container
* Create `docker/compose-files/`
* Add example Compose files
* Document container start/stop/update commands
* Learn Docker volumes and networks

Planned documentation:

* `docs/docker-notes.md`
* `docker/compose-files/example.compose.yml`

## Phase 4: Monitoring and Maintenance

Goal: Track whether the server and services are healthy.

Potential services:

* Uptime Kuma
* Netdata
* Portainer
* Basic disk-usage monitoring
* Basic temperature monitoring

Tasks:

* Pick first monitoring tool
* Deploy with Docker Compose
* Document access method
* Document ports in a public-safe way
* Add restart procedure
* Add update procedure

## Phase 5: Secure Remote Access

Goal: Access the server safely without exposing services directly to the public internet.

Potential tools:

* Tailscale
* WireGuard
* Cloudflare Tunnel, if appropriate later

Preferred direction:

* Avoid public port forwarding
* Use private access methods
* Use strong authentication
* Document the security tradeoffs

Planned documentation:

* `docs/remote-access-notes.md`

## Phase 6: Storage and Backups

Goal: Make data storage and recovery more reliable.

Tasks:

* Decide primary storage device
* Decide backup target
* Document backup frequency
* Test restore process
* Create backup checklist
* Document what should and should not be backed up
* Keep secrets separate from public documentation

Planned documentation:

* `docs/backup-restore-test.md`

## Phase 7: Self-Hosted Tools

Goal: Add useful services that support learning, productivity, and future portfolio projects.

Possible services:

* File sharing
* Syncthing
* Gitea
* PostgreSQL
* SQLite practice projects
* Homepage dashboard
* Documentation wiki
* Automation tools

Selection criteria:

* Useful for real workflows
* Reasonable maintenance burden
* Safe to document publicly
* Good learning value
* Relevant to future AI or lab-informatics work

## Phase 8: AI and Data Project Foundation

Goal: Prepare the server to support future data and AI experiments.

Possible future projects:

* Synthetic cytogenetics data organization
* Metaphase image file management
* Mock lab workflow dashboards
* Python data pipelines
* Local development databases
* Lightweight model-serving experiments
* Retrieval-augmented generation experiments using public-safe data

Important rule:

This project must not use real patient data, employer-confidential data, internal SOPs, clinical system screenshots, real accession numbers, MRNs, or identifiable lab information.

## Phase 9: Portfolio Integration

Goal: Make this repository useful to hiring managers, collaborators, and future technical mentors.

Tasks:

* Keep README clear and current
* Add architecture diagrams
* Add screenshots only when public-safe
* Add setup summaries
* Add project lessons learned
* Link related repositories
* Pin the repo on GitHub profile
* Eventually link from personal portfolio site

## Future Repository Connections

This home-server repo may eventually connect to:

* `metaphase-data-pipeline`
* `cytogenetics-python-notebooks`
* `clinical-ai-lab-informatics`
* `portfolio-site`

## Success Criteria

This project is successful if it demonstrates:

* Practical Linux competence
* Clear technical documentation
* Security awareness
* GitHub fluency
* Docker/container knowledge
* Backup and recovery thinking
* Ability to build infrastructure for real projects
* A credible career shift toward clinical AI and lab informatics
