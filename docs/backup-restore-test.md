# Hyper Backup Restore Test

This record captures public-safe evidence from the first disposable restore of the existing Synology Hyper
Backup repository. It intentionally excludes account identifiers, bucket identifiers, private paths, personal
file names, credentials, screenshots, and recovery material.

- **Exercise date:** 2026-07-31
- **Protected scope tested:** one disposable text fixture within the selected current personal-content backup
- **Destination class:** Backblaze B2 through Synology Hyper Backup
- **Result:** pass for the tested fixture and backup version

## Configuration observed

- The latest scheduled backup inspected on 2026-07-31 reported success.
- Backup runs daily.
- Client-side encryption is enabled.
- Smart Recycle retains up to 60 versions.
- Weekly backup-integrity checks are enabled.
- DSM warning/critical email delivery was tested and covers backup failures.
- The encryption password and downloaded recovery-key file are stored privately outside GitHub.

These observations apply to the inspected job only. They do not authorize publishing identifiers, private
paths, or recovery material.

## Procedure and evidence

1. Created a deterministic disposable text fixture outside the NAS and recorded its SHA-256 checksum.
2. Uploaded the fixture into the selected backup scope.
3. Ran a manual backup and confirmed successful completion on 2026-07-31 at 18:40.
4. Opened the backed-up version in Backup Explorer.
5. Copied the fixture into a separate disposable destination instead of restoring over live content.
6. Downloaded the recovered copy and calculated its SHA-256 checksum independently.
7. Confirmed the source and restored checksums were identical:

   `8c565eac78f2ebc67a59dd5665d9db4530ed4eb37fb0274a75df2497b6ee0ef4`

8. Removed both disposable NAS folders after verification.

The Hyper Backup copy operation itself was not timed precisely. The full guided exercise completed in the
same interactive session, but no recovery-time objective is inferred from that observation.

## Correction made during the exercise

The first copy attempt targeted the original disposable location because a clearly separate destination had
not yet been created. No production or personal file was deleted. A new, unambiguous disposable destination
was created, the copy-from-backup operation was repeated, and the isolated restored file was then verified.
Future exercises should create and visibly confirm the isolated destination before opening Backup Explorer.

## Supported conclusion

This exercise proves that one disposable file from one inspected, client-side-encrypted Backblaze backup
version could be restored and matched byte-for-byte with its source. It does **not** prove:

- recovery of every selected personal file or every retained version;
- protection or recoverability of future metaphase manifests, annotations, databases, or working derivatives;
- the planned local second copy to `pi-server`;
- a tested recovery-time or recovery-point objective; or
- a complete disaster-recovery system.

Those boundaries remain governed by `nas-readiness-checklist.md` and the later workload-specific restore
exercises.

## Planned pi-server Restic synthetic proof (not yet performed)

This section records the intended proof sequence for the D23 local NAS-to-`pi-server` second copy (issue
#19). The repository now contains the fail-closed controller, hardened unit/timer templates, and a synthetic
mock-based regression suite, but **none of the operational proof steps below have been executed**. No
account, package, mount, credential, installed service, enabled timer, initialized repository, or snapshot
exists yet; repository tests are not recovery evidence.

1. Create one deterministic synthetic fixture in an approved disposable NAS source location.
2. Record its SHA-256 checksum.
3. Back it up through the read-only source path (NAS backup identity, read-only SMB mount, Restic).
4. Restore it into a separate disposable destination on `pi-server`.
5. Calculate the restored checksum independently.
6. Confirm byte-for-byte equality.
7. Demonstrate that the NAS backup identity cannot create, modify, rename, or delete the source fixture.
8. Record duration and expected failure behavior (capacity refusal, mount failure, stale-state detection).
9. Remove only the explicitly created disposable test artifacts after verification.

This proof must pass, along with the other D23 preconditions, before automatic `forget`/`prune` is enabled
and before issue #19 or the bounded issue #15 pilot can be considered complete.
