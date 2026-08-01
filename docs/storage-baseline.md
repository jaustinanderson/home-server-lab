# Storage Baseline

This is the sanitized durable storage inventory for the Home Server Lab. It
separates direct read-only observations from owner-confirmed NAS state and avoids
operational addresses, device serials, account identifiers, credentials, and
private paths.

- **Baseline date:** 2026-07-31
- **Linux observation date:** 2026-07-19
- **NAS/backup owner confirmation:** 2026-07-31

## Role model

| Tier | System | Canonical role |
|---|---|---|
| Source/archive | Synology DS925+ | Raw public/synthetic sources, manifests, approved releases, and current personal NAS content |
| Working/compute | `compute-node` | Working copies, transformations, data services, and future AI compute |
| Local secondary protection | `pi-server` | Planned second copy of irreplaceable project data plus lightweight services |
| Off-site | Backblaze B2 | Current Hyper Backup destination; protected scope and restores must be verified per workload |
| Public documentation | GitHub | Sanitized code, catalogs, scripts, decisions, and runbooks only |

D19 supersedes the storage-role portion of D2. SHR drive redundancy and backups
are separate controls.

## Linux host observations

### `compute-node`

- One approximately 1 TB NVMe device
- GPT/UEFI layout with an EFI system partition and plain ext4 root filesystem
- No LVM or LUKS in the observed layout
- Root filesystem approximately 1% used at observation time
- 4 GB swap file on the root filesystem
- No drive-health tooling installed at observation time

### `pi-server`

- One approximately 2 TB USB-attached SSD
- GPT layout with a vfat `/boot/firmware` filesystem and plain ext4 root
- No LVM or LUKS in the observed layout
- Boot filesystem approximately 45% used and root approximately 1% used at
  observation time
- No swap configured
- No USB bus reset/error pattern observed during the reviewed boot
- No drive-health tooling installed at observation time

Usage percentages are historical observations, not live monitoring claims.

## Synology observations and owner-confirmed state

- DS925+ with two matching 16 TB NAS drives installed
- Both drives belong to the intended existing SHR pool; the pool and Btrfs volume report healthy
- The pool reports one-drive fault tolerance and approximately 13.8 TB usable capacity
- Both drives passed extended S.M.A.R.T. tests
- The first data scrub completed successfully on 2026-07-31; quarterly scrubbing is scheduled
- DSM warning/critical email delivery was tested successfully and covers storage and backup failures
- SMB is enabled; NFS is disabled
- Local-network and managed family access are operational
- The NAS is not currently a tailnet device
- Synology Hyper Backup to Backblaze B2 is owner-confirmed operational for selected current personal content
  on a daily schedule, with client-side encryption, Smart Recycle retention, and weekly integrity checks
- The latest scheduled run inspected on 2026-07-31 succeeded
- A disposable file restored into an isolated destination matched its source SHA-256 checksum
Current state: **expected → arrived → installed → recognized/added → synchronized → healthy → protected →
selected-scope backup and fixture recovery tested**. Workload authorization remains a separate evidence gate.

## Controls not yet verified

- Full-file or full-repository recovery beyond the single disposable fixture
- Dedicated metaphase share and least-privilege permissions
- Verified `compute-node` access to the NAS
- Local second copy to `pi-server`
- Provenance, license, classification, checksum, and transformation manifests
- Backup coverage for future manifests, annotations, databases, and working data

The restore proof is intentionally narrow: it validates one encrypted backup version and one disposable file,
not all selected personal content, future metaphase data, or a recovery-time objective. See
`backup-restore-test.md`.

## Metaphase ingestion boundary

Do not begin corpus acquisition merely because the NAS can store files. One
small public/synthetic pilot becomes eligible only after every gate in
`nas-readiness-checklist.md` passes. Non-public patient-derived or clinical
study data, employer material, real case identifiers, uncertain-origin images,
and restricted data remain prohibited under D1/D21; de-identification alone is
not authorization.
