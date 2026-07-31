# Backup Plan

This document defines the backup and restore model for the Home Server Lab's
Linux hosts, Synology source archive, and off-site protection. It distinguishes
implemented controls from planned controls and unverified recovery claims.

> **Current status (2026-07-31):** the DS925+ is the canonical source archive,
> `compute-node` is the hot working tier, and `pi-server` is the planned local
> secondary-protection tier (D19). Synology Hyper Backup to Backblaze B2 is
> owner-confirmed operational for selected current personal NAS content on a daily schedule
> with version retention (D20). The two-drive SHR pool is healthy with one-drive
> fault tolerance; both extended drive tests passed; email alerts work; and quarterly scrubbing is set. No
> successful restore test, local NAS-to-pi backup job, or metaphase-data recovery
> workflow is claimed yet.

## Backup principles

- Protect irreplaceable data; re-download reproducible public datasets.
- Keep important data in more than one failure domain.
- Separate configuration, databases, datasets, annotations, logs, and secrets.
- Automate only after the source, destination, exclusions, and recovery path are
  understood.
- Test restoration; a successful copy is not proof of recoverability.
- Keep public documentation sanitized and credentials in a private mechanism.

## Data classes

| Data class | Examples | Intended protection |
|---|---|---|
| Source and public documentation | Git-tracked code, Compose files, runbooks, diagrams | GitHub plus local clones |
| Personal NAS content | Family home/Photos content currently selected in Hyper Backup | Daily versioned Backblaze B2 backup; restore verification pending |
| Reproducible public data | Original public datasets with recorded source and checksum | Canonical NAS copy plus provenance manifest; re-download when practical |
| Irreplaceable project data | Annotations, curated metadata, database state, experiment decisions | NAS source/archive plus planned local second copy and off-site copy |
| Service state | Database dumps, persistent-volume data, configuration | Service-specific backup and restore runbook |
| Secrets | Tokens, private keys, private addresses, recovery material | Private secret store; never this repository |
| Caches and rebuildable artifacts | Package caches, images that can be rebuilt, temporary exports | Exclude unless a concrete recovery need exists |

Non-public patient-derived or clinical study data, employer-confidential
material, proprietary clinical-system content, and real clinical identifiers
are prohibited on the lab under D1/D21; de-identification or a backup policy
does not make them acceptable.

## Practical 3-2-1 target

For irreplaceable project data, the target model is:

1. **Canonical source/archive copy:** Synology NAS.
2. **Working copy:** `compute-node`, separate from immutable raw sources.
3. **Local second copy:** `pi-server`, created by a documented and monitored
   backup job; not implemented yet.
4. **Off-site copy:** Backblaze B2 through Synology Hyper Backup, with each
   protected workload explicitly added and verified.

GitHub supplies an off-device copy of public source and documentation. It is not
a substitute for database dumps, service data, private configuration, or a
general off-site backup.

The second NAS drive is incorporated into the existing healthy SHR pool, which
now provides one-drive-failure tolerance. This is availability protection, not another copy.
The NAS, compute-node, and pi-server share a location; local replication protects
against some device failures but not theft, fire, account compromise, or a
destructive command that reaches multiple systems.

## Implemented off-site job

The current public-safe facts are:

- Synology Hyper Backup sends selected current personal NAS content to Backblaze B2.
- The job runs daily and uses version retention.
- The owner reports the backup as active and currently protecting the selected content.
- DSM warning/critical email delivery was tested and the configured rule covers backup failures.
- Credentials, account identifiers, bucket identifiers, private paths, and recovery
  material are deliberately excluded here.

Not yet claimed:

- A completed disposable restore and independent content verification
- Verified client-side encryption settings
- Coverage for future metaphase manifests, annotations, databases, or working derivatives
- A tested recovery-time or recovery-point objective

Until the restore test passes, describe the job as **operational backup with
recoverability unverified**, not as a complete disaster-recovery system.

## Backup scope template

Before implementing a job, document:

| Field | Required decision |
|---|---|
| Source | Exact data or service being protected |
| Destination | Storage target and failure domain |
| Method | Tool and command or configuration |
| Schedule | Frequency and acceptable data-loss window |
| Retention | Number and age of copies kept |
| Exclusions | Caches, public datasets, secrets, or temporary files omitted |
| Integrity | Checksums, tool verification, or database consistency method |
| Encryption | At rest and in transit, when required |
| Monitoring | How a failed or stale backup is detected |
| Restore owner | Who can recover the data and where credentials live |

Do not place real paths, addresses, credentials, or private inventory in this
public file.

## Service-specific requirements

For a Dockerized service, protect the material needed to recreate and recover
it:

- Versioned Compose and public-safe configuration
- Image/version information
- Persistent-volume or bind-mount data
- Application-consistent database dumps where applicable
- Required private configuration stored outside Git
- Start, stop, update, rollback, and restore instructions

Copying a live database file is not automatically application-consistent. Use
the database's supported dump or backup mechanism and test the result.

## Restore test

Every protected workload needs a disposable restore exercise:

1. Choose a known backup point.
2. Restore into a separate path, database, volume, or disposable host.
3. Verify checksums or application-level records.
4. Start the restored service without touching the live copy.
5. Record duration, missing prerequisites, manual steps, and failures.
6. Correct the runbook and repeat until the result is reproducible.

Capture public-safe evidence only. A restore test should not expose private
paths, tokens, addresses, or service data.

## Pre-commit and pre-share safety

Before committing backup documentation or copying output into a pull request,
check for:

- Credentials, keys, tokens, `.env` contents, or recovery material
- Operational addresses, device identifiers, private paths, or account names
- Private database contents or service exports
- Patient data, real identifiers, employer information, or clinical screenshots
- Archive files or backup directories accidentally added to Git

The repository `.gitignore` excludes common secret, backup, database, local
data, and archive patterns. That is a safety net, not a content review.

## Implementation order

1. Confirm the latest scheduled Hyper Backup run, included scope, retention, and encryption state.
2. Complete and document a disposable restore of the existing Backblaze-protected content.
3. Define the metaphase manifest/annotation/database backup scope with the template above.
4. Add only that approved scope to off-site protection and verify it.
5. Implement the local NAS-to-`pi-server` second-copy flow for irreplaceable project data.
6. Complete and document a restore from each required failure domain.
7. Review scope, retention, encryption, credentials, and recovery timing after each new service.
