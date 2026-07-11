# Backup Plan

This document defines the intended backup and restore model for the two-machine
Home Server Lab. It distinguishes current hardware roles from controls that are
not yet implemented.

> **Current status:** `compute-node` is the working-storage machine and
> `pi-server` is the intended archive and local-backup target. No automated
> backup job, retention policy, off-site data backup, or completed restore test
> is claimed yet. Do not place irreplaceable data on the lab until those controls
> are implemented and verified.

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
| Reproducible public data | Original public datasets with recorded source and checksum | Provenance manifest; re-download when practical |
| Irreplaceable project data | Annotations, curated metadata, database state, experiment decisions | Local second copy plus encrypted off-site copy |
| Service state | Database dumps, persistent-volume data, configuration | Service-specific backup and restore runbook |
| Secrets | Tokens, private keys, private addresses, recovery material | Private secret store; never this repository |
| Caches and rebuildable artifacts | Package caches, images that can be rebuilt, temporary exports | Exclude unless a concrete recovery need exists |

Patient data, employer-confidential material, proprietary clinical-system
content, and real clinical identifiers are prohibited on the lab entirely; a
backup policy does not make them acceptable.

## Practical 3-2-1 target

For irreplaceable project data, the intended model is:

1. **Working copy:** `compute-node`.
2. **Local second copy:** `pi-server`, created by a documented and monitored
   backup job.
3. **Off-site copy:** an encrypted, access-controlled destination selected when
   valuable private project data exists.

GitHub supplies an off-device copy of public source and documentation. It is not
a substitute for database dumps, service data, private configuration, or a
general off-site backup.

Because both servers share the same location and network, copying from one to
the other protects against a single-disk or single-machine failure but not
theft, fire, account compromise, or a destructive command that reaches both.

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

1. Decide which first service or data class is valuable enough to protect.
2. Define the backup scope with the template above.
3. Select the tool and create a public-safe runbook.
4. Implement the local `compute-node` to `pi-server` copy.
5. Add failure monitoring and a retention policy.
6. Complete and document a restore test.
7. Add an encrypted off-site copy for irreplaceable private data.
8. Review the design after the NAS is introduced; a NAS is storage, not
   automatically a backup.
