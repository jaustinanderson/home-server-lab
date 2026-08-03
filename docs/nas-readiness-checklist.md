# NAS Readiness Checklist

This checklist is the gate between owning storage and safely ingesting the first
public metaphase dataset. A checked box requires evidence; planned or in-progress
work is not completion. Sections A–D must pass before one bounded pilot is
authorized. Passing section E completes Phase 3.5 and authorizes planning for
broader acquisition in the later roadmap phase.

## Evidence state — 2026-08-02

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
| Second-copy architecture | Selected; repository controls prepared; not deployed | D23 records the pi-server-pull/Restic/read-only-SMB design; fail-closed controller/unit templates pass 20 synthetic tests |
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

## C. Provenance and safety — complete on `main`

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

Evidence recorded in `promotion-controls.md` (issue #18, D22): the strict versioned JSON Schema manifest
contract (`promotion-manifest.schema.json`), the dependency-free Python standard-library validator
(`../scripts/validate-promotion-manifest.py`), its documentation, nine synthetic fixture directories
(`../scripts/promotion-manifest-fixtures/`; one valid and eight rejection fixtures), and the automated
regression suite (`../scripts/test_promotion_manifest_validator.py`) are merged on `main` through PR #22
(merge commit `a8e361d`, reviewed head `acc15e2`). The validator implements every control above as a
fail-closed check: missing, ambiguous, malformed, or unknown values do not pass. It computes SHA-256 from
referenced bytes; accepts only `synthetic` or `public_licensed`; requires explicit license/origin/identifier
approval, false disallowed-content flags, contained relative paths, and valid source locators and dates; and
requires `eligibility_state` to be exactly `eligible_for_promotion`. Every transformation record must carry
validated input and output linkage, and a declared derivative must have transformation history connecting
to a governed file: consecutive steps' input and output references or checksums must match, and the final
step's output must correspond to a `files[]` entry — a chain that doesn't connect, or doesn't terminate at a
governed file, is rejected. Empty, whitespace-only, control-character, absolute/drive-letter/UNC,
parent-directory-traversal, home-relative, environment-variable, and `file://` URI transformation references
all fail closed. Passing this validation confirms structural integrity only; it is not promotion
authorization and does not itself approve a dataset for ingestion. The final suite contains 27 automated
tests, and the exact-head Repository checks run #86 passed all 27 tests and every other repository check.
Only synthetic fixtures were used; no real dataset was acquired, ingested, promoted, or referenced, and no
NAS content was accessed or changed. Section C is complete on `main`. Passing section C still does not
authorize section E; issue #19's local second-copy and metaphase-specific recovery work remain incomplete
and unauthorized.

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

A read-only architecture and capacity preflight for the planned pi-server local second copy is complete
(issue #19, D23): `pi-server`'s dedicated SSD reports approximately 1.79 TiB total root capacity at about 1%
used, zero mounted CIFS/NFS filesystems, zero failed systemd units, NTP-synchronized time, and rsync,
sha256sum, and Python already installed, while Restic, Borg, and SMB/CIFS client tooling are not yet
installed; the 06:00–07:00 UTC daily maintenance window was identified as undesirable for a future backup
schedule. D23 records the selected architecture — a pi-server-initiated pull of an encrypted Restic
repository from a read-only NAS SMB source, scoped to explicitly approved irreplaceable project material,
with capacity ceilings, a conservative retention model, and a planned monitoring design documented in
`backup-plan.md`, and a planned synthetic proof sequence documented in `backup-restore-test.md`. No NAS or
`pi-server` account, package, mount, credential, installed service, enabled timer, initialized repository,
or snapshot has been created.

The repository-controlled layer now includes `../scripts/local_second_copy.py`, hardened systemd service
and timer templates under `../systemd/`, a sanitized configuration example, and 20 synthetic tests. The
controller fails closed on writable or missing CIFS source state, non-local repository state, overlapping
paths, broad password-file permissions, concurrent execution, capacity/reserve violations, disappearing
mounts, Restic snapshot/check failures, and missing/stale success state. It updates success state only after
the snapshot, mount recheck, repository check, and post-run capacity gates all pass, and it contains no
retention/pruning or source-write operation. Those tests use temporary directories and mocked command
results only; they did not access either server or the NAS and do not satisfy the operational checklist.
The two checklist items above remain open until private deployment, source-immutability proof, failure/stale
test, checksum-verified isolated restore, duration/rollback/cleanup evidence, and review are complete.

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
