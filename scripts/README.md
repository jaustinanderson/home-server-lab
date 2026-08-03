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
| [`validate-promotion-manifest.py`](validate-promotion-manifest.py) | Fail-closed pre-promotion control check for a `docs/promotion-manifest.schema.json` manifest and its referenced fixture bytes (issue #18) | Read-only: verifies strict schema fields/formats, eligible workflow state, SHA-256, license/origin/content-safety review state, and path safety; never moves, promotes, or rewrites anything; never prints file contents |
| [`test_promotion_manifest_validator.py`](test_promotion_manifest_validator.py) | 27 automated tests for the promotion-manifest validator and schema | Synthetic data only; covers the nine shipped fixture directories plus generated workflow-state, malformed-value, unknown-field, schema-alignment, path-containment/path-escape, transformation input/output linkage, connected transformation chains with governed final outputs, unsafe transformation-reference rejection (including Windows drive-relative references and case-insensitive `file:` URI variants) while preserving legitimate relative/logical references, usage-error, and non-destructive cases |
| [`local_second_copy.py`](local_second_copy.py) | Fail-closed controller for D23's planned local Restic second copy (issue #19) | Requires an existing read-only CIFS source and initialized local repository; enforces capacity/reserve gates, suppresses private Restic output, rechecks the mount, runs `restic check`, atomically records verified success, and separately checks 36-hour staleness; never mounts, initializes, prunes, deletes, or manages credentials/accounts |
| [`test_local_second_copy.py`](test_local_second_copy.py) | 20 automated tests for the local second-copy controller and systemd templates | Temporary synthetic directories and mocked command results only; exercises success, warning, mount/permission/capacity/overlap/concurrency failures, failed snapshot/check and post-run ceiling/reserve timestamp preservation, disappearing-mount detection, stale-state behavior, unit hardening, schedule, credential loading, and the no-pruning boundary without contacting a NAS or creating a Restic repository |

Run the current utility from the repository root:

```bash
chmod +x scripts/system-info.sh
./scripts/system-info.sh
```

[`promotion-manifest-fixtures/`](promotion-manifest-fixtures/) holds nine synthetic,
obviously-fake fixture directories — one valid and eight independent rejection
fixtures. The 27-test suite supplements them with generated edge cases so every
noneligible workflow state, strict schema boundary, invalid locator/date/timestamp,
transformation sequence, transformation input/output linkage, connected
transformation chain and governed final output, unsafe transformation-reference
syntax, path escape, usage error, and non-destructive contract is checked. No real
dataset content lives here.

GitHub Actions runs ShellCheck, the system-output privacy regression, all 27
promotion-manifest tests, all 20 synthetic local-second-copy tests, and the
relative Markdown-link check on every push and pull request.

## Planned Scripts

Possible future scripts:

```text
update-server.sh
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
