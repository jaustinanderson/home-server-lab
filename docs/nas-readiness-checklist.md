# NAS Readiness Checklist

This checklist is the gate between owning storage and safely ingesting the first
public metaphase dataset. A checked box requires evidence; planned or in-progress
work is not completion.

## A. Second-drive protection

- [ ] Confirm the new drive is the expected compatible model and capacity.
- [ ] Add it to the **existing** SHR pool; do not create a second pool.
- [ ] Allow expansion/synchronization to complete without interruption.
- [ ] Verify DSM reports the storage pool protected and healthy.
- [ ] Verify both drives report healthy.
- [ ] Run and record appropriate drive-health tests.
- [ ] Confirm storage-pool, drive, capacity, and backup-failure notifications.

## B. Archive boundary and access

- [ ] Create a dedicated metaphase source/archive share.
- [ ] Separate quarantine, governance/manifests, raw sources, approved releases,
  annotations, working derivatives, exports, and logs.
- [ ] Grant least-privilege access; keep administration separate from routine use.
- [ ] Verify `compute-node` can access the intended share.
- [ ] Verify raw sources cannot be silently overwritten by the working workflow.
- [ ] Keep working copies and transformations on `compute-node`, not mixed into
  canonical raw-source directories.

## C. Provenance and safety

- [ ] Require dataset name, version, source URL/DOI, publisher, acquisition date,
  license, redistribution limits, and intended use.
- [ ] Require SHA-256 checksums before promotion from quarantine.
- [ ] Classify every source as public, synthetic, or explicitly approved
  de-identified study data.
- [ ] Record every transformation from source to derivative.
- [ ] Reject patient data, employer material, real identifiers, uncertain-origin
  collections, and sources without an acceptable license.

## D. Backup and recovery

- [x] Daily Hyper Backup to Backblaze B2 is owner-confirmed operational for
  selected current personal NAS content.
- [ ] Verify the backup job's latest run and failure-notification path.
- [ ] Inspect and record encryption behavior without exposing keys or credentials.
- [ ] Restore a sample into a disposable location.
- [ ] Independently verify restored files or records.
- [ ] Record recovery time, missing prerequisites, and manual steps.
- [ ] Define protection for metaphase manifests, licenses, annotations, database
  state, and other irreplaceable work.
- [ ] Implement and verify the planned local second copy to `pi-server`.

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
