# Backup Plan

This document defines the backup and restore model for the Home Server Lab's
Linux hosts, Synology source archive, and off-site protection. It distinguishes
implemented controls from planned controls and unverified recovery claims.

> **Current status (2026-08-02):** the DS925+ is the canonical source archive,
> `compute-node` is the hot working tier, and `pi-server` is the planned local
> secondary-protection tier (D19). Synology Hyper Backup to Backblaze B2 is
> owner-confirmed operational for selected current personal NAS content on a daily schedule
> with version retention (D20). The two-drive SHR pool is healthy with one-drive
> fault tolerance; both extended drive tests passed; email alerts work; and quarterly scrubbing is set. One
> encrypted Backblaze restore of a disposable fixture matched its source SHA-256 checksum. A read-only
> architecture and capacity preflight on `pi-server` is complete, and D23 records the selected design for
> the local NAS-to-pi second copy (pi-server-initiated pull, read-only NAS SMB source, Restic). A fail-closed
> controller, hardened systemd unit/timer templates, and 20 synthetic tests now implement the public-safe
> repository-controlled layer. Nothing has been deployed on the NAS or `pi-server`; no operational snapshot
> or metaphase-data recovery workflow is claimed yet.

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
| Personal NAS content | Selected current personal content in Hyper Backup | Daily encrypted, versioned Backblaze B2 backup; one checksum-verified disposable restore passed |
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
   backup job; architecture and repository-controlled automation are prepared
   under D23 (see below), but nothing is deployed yet.
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
- The job runs daily, uses client-side encryption, retains up to 60 versions through Smart Recycle, and has weekly integrity checks enabled.
- The latest scheduled run inspected on 2026-07-31 succeeded; a later manual test backup also succeeded.
- The owner reports the backup as active and currently protecting the selected content.
- DSM warning/critical email delivery was tested and the configured rule covers backup failures.
- One disposable file was restored from the encrypted repository into an isolated destination and matched the source SHA-256 checksum.
- Recovery credentials are stored privately outside GitHub.
- Credentials, account identifiers, bucket identifiers, private paths, and recovery
  material are deliberately excluded here.

Not yet claimed:

- Coverage for future metaphase manifests, annotations, databases, or working derivatives
- Full-file or full-repository recovery validation beyond the single disposable fixture
- A tested recovery-time or recovery-point objective
- A complete disaster-recovery system

The supported claim is **operational, client-side-encrypted, versioned backup with one checksum-verified
disposable restore for the selected current scope**. See `backup-restore-test.md`.

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

## Local second copy — pi-server (D23, repository controls prepared)

Following a read-only architecture and capacity preflight on `pi-server`, D23 records the selected design
for the planned local NAS-to-pi second copy of irreplaceable project data. The public-safe controller,
systemd templates, configuration example, and synthetic regression suite are now repository-controlled.
**Nothing has been deployed** — no account, package, mount, credential, installed service, enabled timer,
initialized repository, or snapshot exists.

**Architecture:**

- `pi-server` initiates the backup pull; the NAS never authenticates outward to `pi-server` and never holds
  credentials or access to the Pi backup repository.
- The Synology NAS remains the canonical source.
- A dedicated non-administrator NAS backup identity gets read-only access limited to the approved scope
  below, exposed to the backup process as a read-only SMB mount.
- NAS credentials for that identity are root-only on `pi-server`, stored outside Git, and never printed.
- A dedicated non-login local backup identity runs the job on `pi-server`.
- **Restic** is the selected snapshot tool (encryption, deduplication, integrity checking, versioned
  recovery points); the repository itself is inaccessible to ordinary interactive users on `pi-server`.
- The initial proof uses synthetic data only, with no automatic `forget`/`prune`/deletion during the proof.

**Encryption caveat:** Restic provides repository-level encryption and root-only credential storage limits
ordinary-user access, but `pi-server`'s SSD is not LUKS-encrypted (D13). An automatic unlock secret stored
on that same unencrypted disk does not fully protect against physical disk extraction, since the key and the
encrypted repository would travel together. LUKS, TPM-backed credential handling, or an off-device/manual
unlock model remain future hardening options. Restic alone does not eliminate the physical-theft risk.

**Protected scope (initial):**

| Included | Excluded |
|---|---|
| Provenance and promotion manifests | Re-downloadable public bulk datasets |
| License-review records | Quarantine contents |
| Curated annotations and metadata | Caches and temporary files |
| Database-consistent dumps, once databases exist | Rebuildable working derivatives |
| Irreplaceable experiment records/config not adequately protected by GitHub | Routine exports/logs without a documented recovery requirement |
| | Git-tracked public documentation already protected by GitHub |
| | Secrets and credentials |
| | Personal NAS content (covered by D20's Hyper Backup job) |
| | Patient, employer, institutional, restricted, or uncertain-origin material (prohibited under D1/D21 regardless of backup policy) |

The exact private NAS source path and its measured size are implementation-time operational inputs and are
deliberately not published in this repository.

**Capacity and retention policy:**

- Repository ceiling: 256 GiB (~14% of `pi-server`'s filesystem).
- Repository warning threshold: 192 GiB.
- Minimum free-space reserve: 512 GiB.
- The backup must refuse to start or continue if the 256 GiB ceiling would be exceeded or available
  filesystem capacity falls below the 512 GiB reserve.
- Proposed schedule: daily near 03:30 UTC (outside the identified 06:00–07:00 UTC maintenance window),
  optionally with a small randomized delay.
- Target retention after the proof phase: 7 daily, 4 weekly, 6 monthly snapshots.
- Automatic `forget`/`prune` stays disabled until: the synthetic restore succeeds; checksum equality is
  proven; source immutability is proven; monitoring and stale-state detection work; several consecutive
  scheduled backups succeed; and Austin explicitly approves enabling pruning.

**Planned monitoring design:** a hardened oneshot systemd backup service; a daily timer near 03:30 UTC; a
success timestamp updated only after the snapshot and required verification complete successfully; a
separate stale-state checker with a 36-hour stale threshold; nonzero exit status on backup, capacity,
integrity, mount, or stale-state failure; visibility through systemd until Phase 5 monitoring exists; and a
disposable synthetic method for testing both failure and stale-state behavior — never real repository
corruption or manipulation of the canonical NAS source.

**Repository-controlled implementation:** [`../scripts/local_second_copy.py`](../scripts/local_second_copy.py)
implements the fail-closed preflight, local Restic snapshot, post-snapshot repository check, atomic
last-success timestamp, and separate stale-state check. The templates in [`../systemd/`](../systemd/) define
the hardened oneshot services and the daily/stale timers without publishing private paths or credentials.
The controller refuses a non-CIFS or writable source, a network-hosted repository, overlapping source and
repository paths, broad password-file permissions, concurrent execution, a projected hard-ceiling/reserve
breach (including a fixed 1 GiB safety margin), a disappearing source mount, a failed snapshot, a failed
repository check, or a post-run capacity breach. It has no mount, repository-initialization, credential,
account, retention, `forget`, `prune`,
source-write, or cleanup function. Its 20 automated tests use only temporary synthetic directories and
mocked command results; passing them is code evidence, not operational backup or recovery evidence.

See `docs/backup-restore-test.md` for the planned synthetic proof sequence and
`docs/nas-readiness-checklist.md` section D for gate status.

## Implementation order

1. Define the metaphase manifest/annotation/database backup scope with the template above.
2. Add only that approved scope to off-site protection and verify it.
3. Implement the local NAS-to-`pi-server` second-copy flow for irreplaceable project data per the D23
   architecture above.
4. Complete and document a restore from each required failure domain.
5. Review scope, retention, encryption, credentials, and recovery timing after each new service.
