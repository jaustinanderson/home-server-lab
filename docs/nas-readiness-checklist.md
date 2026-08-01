# NAS Readiness Checklist

This checklist is the gate between owning storage and safely ingesting the first
public metaphase dataset. A checked box requires evidence; planned or in-progress
work is not completion. Sections A–D must pass before one bounded pilot is
authorized. Passing section E completes Phase 3.5 and authorizes planning for
broader acquisition in the later roadmap phase.

## Evidence state — 2026-08-01

| Stage | State | Evidence boundary |
|---|---|---|
| Expected | Complete historically | Matching 16 TB drive selected |
| Arrived | Owner-confirmed complete | Second drive received |
| Installed | Owner-confirmed complete | Second drive physically installed |
| Recognized | Owner-confirmed complete | DSM recognized the second drive and began the now-completed conversion |
| Synchronized | Complete | Existing SHR pool finished conversion |
| Healthy | Complete | Pool, Btrfs volume, and both drives report healthy; both extended tests passed |
| Redundant | Complete | SHR reports one-drive fault tolerance |
| Backup current | Complete for selected personal scope | Latest scheduled run succeeded; daily versioned encrypted job inspected |
| Restore verified | Complete for one fixture | Isolated restore matched the source SHA-256 checksum |
| Workload authorized | No | Pre-ingestion gates remain incomplete |

## A. Second-drive protection

- [x] Confirm the matching 16 TB drive arrived.
- [x] Confirm the drive is physically installed.
- [x] Confirm DSM recognizes the drive and reports conversion of the existing
  SHR pool in progress.
- [x] Allow expansion/synchronization to complete without interruption.
- [x] Verify the final topology is the intended SHR pool, not a second
  independent pool.
- [x] Verify DSM reports the storage pool protected and healthy.
- [x] Verify both drives report healthy after conversion.
- [x] Run and record appropriate drive-health tests.
- [x] Confirm storage-pool, drive, capacity, and backup-failure notifications.
- [x] Complete the first data scrub and schedule recurring quarterly scrubbing.

## B. Archive boundary and access

- [x] Create a dedicated metaphase source/archive share.
- [x] Separate quarantine, governance/manifests, raw sources, approved releases,
  annotations, working derivatives, exports, and logs.
- [x] Grant least-privilege access; keep administration separate from routine use.
- [x] Verify `compute-node` can access the intended share.
- [x] Verify raw sources cannot be silently overwritten by the working workflow.
- [x] Keep working copies and transformations on `compute-node`, not mixed into
  canonical raw-source directories.

Evidence recorded in `metaphase-archive-boundary.md` (issue #17): the dedicated
archive share is organized into the eight listed areas; a non-administrator routine
workflow identity is scoped to the archive share only over SMB 3.1.1, with no access
to personal home-directory storage and no NAS administration role; canonical raw
sources and approved releases denied create/modify/rename/delete attempts from that
identity while remaining readable, and the working-derivative area remained fully
writable; `compute-node`'s on-demand automount (root-owned `0600` credential file,
`nosuid`/`nodev`/`noexec`, network-dependent and non-fatal at boot) activated
successfully and survived a normal reboot with passing post-reboot permission tests;
and active transformations were confirmed to stay on `compute-node`'s local ext4
filesystem. No real dataset was ingested; only disposable synthetic placeholders
were used, and they were removed afterward. A reboot with the NAS deliberately
offline was not tested.

## C. Provenance and safety — staged in draft PR #22

- [x] Require dataset name, version, source URL/DOI, publisher, acquisition date,
  license, redistribution limits, and intended use.
- [x] Require SHA-256 checksums before promotion from quarantine.
- [x] Classify every source as synthetic or as a legitimately public,
  appropriately licensed dataset; de-identification alone is insufficient
  (D1/D21).
- [x] Record every transformation from source to derivative.
- [x] Reject non-public patient-derived or clinical study data, employer
  material, real identifiers, uncertain-origin collections, restricted data,
  and sources without an acceptable license.

Evidence staged in `promotion-controls.md` (issue #18, D22): a strict versioned
JSON Schema manifest contract (`promotion-manifest.schema.json`) and a dependency-free Python
standard-library validator (`../scripts/validate-promotion-manifest.py`) implement every control above as
a fail-closed check. Missing, ambiguous, malformed, or unknown values do not pass. The validator computes
SHA-256 from referenced bytes; accepts only `synthetic` or `public_licensed`; requires explicit
license/origin/identifier approval, false disallowed-content flags, contained relative paths, valid source
locators and dates, sequential transformation steps with valid timestamps, and transformation history for
derivatives; and requires `eligibility_state` to be exactly `eligible_for_promotion`. Nine synthetic
fixture directories (`../scripts/promotion-manifest-fixtures/`; one valid and eight rejection fixtures)
plus 16 automated tests (`../scripts/test_promotion_manifest_validator.py`) cover the shipped fixtures,
noneligible workflow states, schema alignment, unknown fields, malformed values, path escape,
non-destructive behavior, and usage errors. An exact-head GitHub Actions run passed all 16 tests and every repository
check. No real dataset was acquired, ingested, promoted, or referenced, and no NAS content was accessed or
changed. The checked boxes describe the implementation on draft PR #22; issue #18 remains open, and section
C is not complete on `main`, until Austin reviews and merges the PR and the result is verified on `main`.
Passing section C still does not authorize section E; issue #19's metaphase-specific protection and local
second-copy work also remain blockers.

## D. Backup and recovery

- [x] Daily Hyper Backup to Backblaze B2 is owner-confirmed operational for
  selected current personal NAS content.
- [x] Verify the backup job's latest scheduled run.
- [x] Verify the notification delivery path covers backup failures.
- [x] Inspect and record encryption behavior without exposing keys or credentials.
- [x] Restore a sample into a disposable location.
- [x] Independently verify restored files or records.
- [x] Record timing limitations, missing prerequisites, and manual steps.
- [ ] Define protection for metaphase manifests, licenses, annotations, database
  state, and other irreplaceable work.
- [ ] Implement and verify the planned local second copy to `pi-server`.

Evidence recorded in `backup-restore-test.md`: on 2026-07-31 the latest scheduled run was successful; the
job was confirmed as daily, client-side encrypted, versioned with Smart Recycle, and covered by weekly
integrity checks. A disposable file was backed up, restored into a separate destination, and verified by an
identical SHA-256 checksum. The exact copy duration was not measured. An initial destination-selection error
was corrected by creating a clearly separate destination and repeating the restore; disposable NAS folders
were removed after verification.

## E. First bounded pilot

- [ ] Select one small, clearly licensed public or synthetic dataset.
- [ ] Prove: download → quarantine → license review → checksum → manifest →
  archive → working copy → restore.
- [ ] Record failures and corrections before scaling.
- [ ] Authorize broader acquisition only after the pilot passes.

## Stop conditions

Stop and investigate if DSM reports a degraded pool or drive warning, backup
status becomes stale/failed, a restore cannot be verified, permissions are
broader than intended, provenance is incomplete, checksums differ, or the data's
origin/license is uncertain.
