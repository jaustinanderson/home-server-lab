# Metaphase Archive Boundary

This record captures public-safe evidence for **section B** of
[`nas-readiness-checklist.md`](nas-readiness-checklist.md): the dedicated metaphase
source/archive share, its least-privilege access model, and verified `compute-node`
access. It intentionally excludes share names, account names, addresses, hostnames,
credential-file paths, mount paths, serials, screenshots, and raw command output.
Tracks issue #17.

- **Exercise date:** 2026-08-01
- **Scope tested:** archive structure, identity separation, canonical-content
  protection, `compute-node` access, and local processing isolation
- **Dataset used:** none — disposable synthetic placeholders only, removed after
  each test
- **Result:** pass for every control described below

## Archive structure

A dedicated archive/source share was created on the canonical NAS archive (D19),
separate from existing personal-content shares. It is organized into the following
logical areas, each with a distinct role:

| Area | Role |
|---|---|
| Governance / manifests | Provenance, license, and checksum records (Section C, not yet populated) |
| Quarantine | Landing zone for material pending review; nothing is promoted automatically |
| Canonical raw sources | Immutable original material once promoted from quarantine |
| Approved releases | Reviewed, checksum-verified material approved for workflow use |
| Annotations | Derived labels/metadata associated with approved material |
| Working derivatives | Writable intermediate outputs produced from approved material |
| Exports | Finished outputs intended to leave the working workflow |
| Logs | Operational records of archive activity |

No real dataset was ingested into any of these areas. Structural testing used only
disposable synthetic placeholders, which were removed afterward.

## Least-privilege identity

A dedicated, non-administrator **routine workflow identity** was created for
day-to-day archive access, separate from the NAS administrator account:

- Restricted to the intended file-sharing protocol and the dedicated archive share.
- Cannot browse or access personal home-directory storage.
- Has no interactive NAS administration role.

Administrative access to the NAS remains a separate, more privileged path than the
routine workflow identity uses. This keeps the blast radius of a compromised
workflow credential limited to the archive share.

## Canonical-content protection

Using the routine workflow identity:

- **Canonical raw sources** and **approved releases**: browse/read succeeded;
  create, modify, rename, and delete attempts were all denied as intended.
- **Working derivatives**: write, read, and delete all succeeded, confirming the
  writable area is usable for day-to-day work.

This confirms the routine identity cannot silently overwrite or remove canonical
material while still being able to do its job in the writable area, satisfying the
"raw sources cannot be silently overwritten" gate in section B.

## Compute-node access

`compute-node` reaches the archive share over **SMB 3.1.1** using the routine
workflow identity. Configuration details, generalized to remove implementation
identifiers:

- Credentials are stored in a **root-owned credential file, mode `0600`**, outside
  version control.
- The mount is configured with least-privilege safety options equivalent to
  `nosuid`, `nodev`, and `noexec`, plus network-dependent mounting so it does not
  block boot when the network isn't ready.
- Mount failures are treated as **non-fatal at boot** (the host still boots cleanly
  if the archive is unreachable).
- The share is brought online through **on-demand systemd automounting** with
  bounded idle and mount timeouts, rather than a permanently mounted filesystem.

Validation performed:

- The automount activated successfully and triggered the SMB connection on first
  access.
- The configuration survived a normal `compute-node` reboot; post-reboot access and
  permission tests passed.
- A reboot with the NAS deliberately offline was **not** tested and is not claimed.

## Local processing boundary

Active working copies, transformations, and scratch processing live in a
**dedicated local workspace on `compute-node`**, not on the NAS:

- Owned by the normal `compute-node` user, mode `0750`.
- Resolves to `compute-node`'s internal NVMe **ext4** filesystem.

A disposable synthetic tabular input was transformed into a disposable synthetic
output entirely within this local workspace; both input and output were confirmed
to remain on the local ext4 filesystem, then removed. This confirms the NAS is the
controlled archive/source boundary while active computation stays local, satisfying
the "working copies and transformations stay on `compute-node`" gate in section B.

## Isolation test

Two separate personal-home access attempts were made using the routine workflow
identity, both **denied** by the NAS with an authentication/authorization failure:

- A mount attempt against the administrator-facing aggregate personal-home storage
  path.
- A separate, read-only mount attempt against the identity's own personal-home
  storage path.

This confirms the identity's access is scoped to the archive share only, with no
route into personal storage — neither the shared administrative view nor its own
personal-home path. No personal-home contents were listed or accessed in either
attempt. The temporary test mount points were removed afterward.

## Supported conclusion

This exercise proves that, for the tested configuration:

- A dedicated archive/source share with the required logical separation exists.
- The routine workflow identity is least-privilege: scoped to one protocol and one
  share, unable to reach personal storage, and without administrative capability.
- Canonical raw sources and approved releases resist accidental modification or
  deletion by the routine workflow identity, while the working-derivative area
  remains usable.
- `compute-node` reaches the archive on demand, safely, and the configuration
  survives a normal reboot.
- Active computation stays on `compute-node`'s local filesystem, not the NAS.

It does **not** prove:

- Recovery behavior if the NAS is offline at boot (not tested).
- Provenance, license, or checksum controls (section C — separate, not yet done).
- A local second copy to `pi-server` (separate planned work).
- Anything about real dataset content, since no real dataset was used.

## Rollback

If this configuration needs to be reversed, at a sanitized operational level:

1. Stop and disable the on-demand archive automount unit; reload the service
   manager after removing its unit file.
2. Unmount the archive if currently mounted, then remove the dedicated mount point.
3. Remove the root-only credential file only after confirming it is no longer
   referenced by any mount configuration.
4. If abandoning the workflow entirely, remove the routine workflow identity's
   archive authorization (or the identity itself) on the NAS.
5. Remove explicit archive ACL rules only through an administrator account, and
   only after confirming no other workflow depends on them.
6. Do not delete any archive storage or share until ownership, retention, and data
   disposition have been reviewed — this record only covers access and isolation,
   not data lifecycle.
7. Leave unrelated NAS shares, users, permissions, and `compute-node` configuration
   untouched; none of the above steps should affect them.

Each step above was reasoned through as sanitized guidance, not executed as part of
this exercise, since no rollback was required.
