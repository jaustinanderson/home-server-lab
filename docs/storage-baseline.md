# Storage Baseline

This is the sanitized durable storage inventory for the Home Server Lab. It
separates direct read-only observations from owner-confirmed NAS state and avoids
operational addresses, device serials, account identifiers, credentials, and
private paths.

- **Baseline date:** 2026-07-29
- **Linux observation date:** 2026-07-19
- **NAS/backup owner confirmation:** 2026-07-29

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
- The second drive has been added to the existing SHR pool
- DSM conversion/synchronization is in progress as of 2026-07-29
- Redundancy, protected pool status, and two-drive health are not yet verified
- SMB is enabled; NFS is disabled
- Local-network and managed family access are operational
- The NAS is not currently a tailnet device
- Synology Hyper Backup to Backblaze B2 is owner-confirmed operational for
  selected current personal content on a daily schedule with version retention
Current state: **expected → arrived → installed → recognized/added → conversion
in progress**. Synchronization complete, healthy, redundant, backup current,
restore verified, and workload authorized remain separate evidence gates.

## Controls not yet verified

- Successful disposable restore from the Backblaze backup
- Hyper Backup encryption settings
- Storage/backup failure-notification test
- Extended drive-health test evidence for both NAS drives
- Completed SHR conversion with the pool protected and both drives healthy
- Dedicated metaphase share and least-privilege permissions
- Verified `compute-node` access to the NAS
- Local second copy to `pi-server`
- Provenance, license, classification, checksum, and transformation manifests
- Backup coverage for future manifests, annotations, databases, and working data

## Metaphase ingestion boundary

Do not begin corpus acquisition merely because the NAS can store files. One
small public/synthetic pilot becomes eligible only after every gate in
`nas-readiness-checklist.md` passes. Non-public patient-derived or clinical
study data, employer material, real case identifiers, uncertain-origin images,
and restricted data remain prohibited under D1/D21; de-identification alone is
not authorization.
