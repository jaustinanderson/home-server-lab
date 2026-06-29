# Backup Plan

This file documents the backup strategy for the Raspberry Pi home-server lab.

The goal is to build reliable backup habits early, before the server begins hosting important projects, data, scripts, notes, or self-hosted services.

## Backup Philosophy

A home server is only useful if its data can survive mistakes, failed storage, bad updates, accidental deletion, and hardware problems.

This project should follow a simple backup mindset:

* Important files should exist in more than one place
* Backups should be tested, not just assumed
* Configuration should be documented
* Secrets should not be stored in public repositories
* Recovery steps should be clear enough to follow under stress

## What Needs Backed Up

Important categories:

* Project documentation
* Docker Compose files
* Service configuration files
* Scripts
* Notes
* Diagrams
* Databases used for practice projects
* Future AI/lab-informatics project data
* Home-server configuration notes

Do not back up unnecessary cache files, temporary files, or large rebuildable files unless there is a reason.

## What Should Not Be Publicly Backed Up Here

This GitHub repository should not contain:

* Passwords
* Private SSH keys
* API keys
* Tokens
* `.env` files
* Private network details
* Patient data
* Employer-confidential data
* Clinical screenshots
* Real accession numbers, MRNs, case IDs, or sample identifiers

## 3-2-1 Backup Rule

A mature backup plan should aim for the 3-2-1 rule:

* **3 copies** of important data
* **2 different types of storage**
* **1 copy off-site or separate from the main machine**

For this project, a practical version could be:

1. Main copy on the Raspberry Pi
2. Local backup to external SSD or another storage device
3. Off-device backup to GitHub, cloud storage, or another trusted location for public-safe files

## GitHub as Documentation Backup

GitHub is useful for backing up:

* Public-safe documentation
* Scripts
* Docker Compose templates
* Architecture notes
* Setup logs
* Sanitized configuration examples

GitHub should not be used for:

* Secrets
* Private keys
* `.env` files
* Private service data
* Personal records
* Sensitive clinical data

## Local Backup Strategy

Possible local backup targets:

* External SSD
* USB drive
* NAS
* Another computer
* Encrypted backup drive

Future documentation should include:

* Backup location
* Backup frequency
* Backup command or tool
* What is included
* What is excluded
* Restore procedure

## Example Backup Folder Structure

```text
backups/
├── configs/
├── docker/
├── scripts/
├── service-data/
└── restore-notes/
```

This is only an example. Do not commit actual private backup data into this public repository.

## Docker Backup Considerations

For Docker-based services, back up:

* `docker-compose.yml`
* Service configuration directories
* Persistent volumes
* Database dumps when applicable
* Notes about exposed ports and dependencies

Do not commit:

* `.env` files
* Secrets
* Service passwords
* Tokens
* Private database contents

## Example Docker Documentation Backup

Safe to document publicly:

```text
docker/
└── compose-files/
    └── example-service.compose.yml
```

Unsafe to commit publicly:

```text
.env
secrets.txt
private-key.pem
actual-database-backup.sql
```

## Restore Plan

A backup is incomplete until restoration is possible.

Future restore checklist:

* Reinstall operating system if needed
* Restore SSH access
* Install required packages
* Install Docker
* Restore Compose files
* Restore service configuration
* Restore persistent data
* Restart services
* Confirm services work
* Document issues encountered

## Testing Backups

Backups should be tested periodically.

Testing questions:

* Can the backup files be found?
* Can they be opened?
* Can the server be rebuilt from the notes?
* Can Docker services be restarted from the saved Compose files?
* Are any required secrets missing from the private backup location?
* Are public docs free from sensitive data?

## Backup Frequency

Possible schedule:

* Documentation: commit to GitHub whenever changed
* Scripts: commit to GitHub whenever changed
* Docker Compose files: commit after meaningful changes
* Service configuration: back up after service changes
* Service data: schedule depends on importance
* Full server image: before major changes or upgrades

## Pre-Backup Safety Check

Before backing up or committing files, check for:

* Passwords
* Tokens
* Private keys
* `.env` files
* Real IP addresses if not appropriate
* Personal network details
* Patient data
* Employer-confidential information
* Clinical system screenshots

Useful command before committing from a local repo:

```bash
git status
```

## Future Improvements

* Choose a local backup device
* Decide whether to use external SSD, NAS, or cloud backup
* Create `.gitignore`
* Document backup commands
* Document restore commands
* Test restoring a simple service
* Add encrypted backup notes
* Add backup schedule
