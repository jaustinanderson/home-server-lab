# Scripts

This folder stores public-safe scripts for the home-server lab.

The goal is to build useful automation while keeping scripts readable, documented, and safe for a public portfolio repository.

## Purpose

Scripts in this folder may eventually help with:

* Server setup checks
* Package update reminders
* Backup tasks
* Docker maintenance
* Service health checks
* Log collection
* Storage checks
* Temperature checks
* Future data workflow automation

## Security Rules

Do not commit scripts that contain:

* Passwords
* API keys
* Tokens
* Private SSH keys
* Personal network secrets
* Public IP addresses
* Patient data
* Employer-confidential data
* Real clinical identifiers

Use placeholders instead:

```text
SERVER_HOST=<your-server-hostname>
API_KEY=<your-api-key-here>
BACKUP_PATH=<your-backup-path-here>
```

## Available Scripts

| Script | Purpose | Safety note |
|---|---|---|
| [`system-info.sh`](system-info.sh) | Summarize OS, kernel, uptime, memory, root-filesystem use, CPU, temperature, network-link state, and Docker availability | Allowlists interface name/state so IP and MAC addresses are omitted; review all output before sharing |
| [`test-system-info-safety.sh`](test-system-info-safety.sh) | Regression-test the network-output privacy contract with a mocked link-layer address | Fails if a MAC address escapes or expected sanitized fields disappear |
| [`check-markdown-links.py`](check-markdown-links.py) | Check repository-relative Markdown links | Reads repository Markdown only and reports missing local targets |

Run the current utility from the repository root:

```bash
chmod +x scripts/system-info.sh
./scripts/system-info.sh
```

GitHub Actions runs ShellCheck, the system-output privacy regression, and the
relative Markdown-link check on every push and pull request.

## Planned Scripts

Possible future scripts:

```text
update-server.sh
backup-check.sh
docker-status.sh
service-health-check.sh
storage-check.sh
temperature-check.sh
```

## Script Standards

Scripts should be:

* Simple
* Commented
* Public-safe
* Easy to run
* Easy to understand
* Written with clear filenames
* Tested before being relied on

## Example Script Header

```bash
#!/usr/bin/env bash

# Script: example-script.sh
# Purpose: Briefly describe what this script does.
# Safety: This script should not contain secrets or private data.

set -e
```

## Future Improvements

* Add a non-mutating update-status check
* Add a backup verification check after a backup workflow exists
* Add service-health and storage-threshold checks after the first service is deployed
* Add script-specific prerequisites, side effects, and rollback notes
* Add a lightweight script testing checklist
