# Local Second-Copy Unit Templates

These templates are the repository-controlled implementation scaffold for the
D23 NAS-to-`pi-server` local second copy. They are **not evidence of deployment**.
No account, package, mount, credential, repository, service, timer, snapshot, or
restore is created merely by merging these files.

## Components

| File | Role |
|---|---|
| [`../scripts/local_second_copy.py`](../scripts/local_second_copy.py) | Fail-closed preflight, Restic snapshot, repository check, capacity enforcement, atomic success timestamp, and stale-state check |
| [`home-lab-local-backup@.service`](home-lab-local-backup@.service) | Hardened oneshot service; the instance is the separately approved non-login local backup identity |
| [`home-lab-local-backup@.timer`](home-lab-local-backup@.timer) | Daily 03:30 UTC schedule with a small randomized delay |
| [`home-lab-local-backup-stale@.service`](home-lab-local-backup-stale@.service) | Separate 36-hour stale-state check with nonzero failure behavior |
| [`home-lab-local-backup-stale@.timer`](home-lab-local-backup-stale@.timer) | Runs the stale-state check after boot and every six hours |
| [`second-copy.conf.example`](second-copy.conf.example) | Sanitized path/limit template; never store credentials in it |

## Fail-closed behavior

Before starting Restic, the controller requires:

- an existing source directory on a CIFS filesystem whose active mount options
  include `ro` and not `rw`;
- an initialized Restic repository on local (not CIFS/NFS/SSHFS) storage;
- a Restic password file with no group or other access;
- non-overlapping source and repository paths;
- enough worst-case capacity for the entire currently measured protected scope,
  plus a fixed 1 GiB metadata/measurement safety margin, without crossing the
  256 GiB repository ceiling or 512 GiB free-space reserve;
  and
- an exclusive runtime lock, preventing concurrent snapshots.

The service runs `restic backup` without publishing Restic output, rechecks that
the source is still a read-only CIFS mount, runs `restic check`, and rechecks the
hard capacity limits. Only then does it atomically replace the last-success
timestamp. A failed run leaves the prior timestamp unchanged, allowing the
separate stale-state service to detect prolonged failure.

The controller intentionally has no initialization, mount, account-management,
credential-generation, retention, `forget`, `prune`, source-write, or cleanup
operation. Those boundaries prevent a code merge from becoming an operational
change and preserve Austin's explicit approval gate before pruning.

## Private deployment inputs (not in Git)

Operational rollout still requires a separately reviewed change window on
`pi-server` and the NAS. Before either timer is enabled, verify privately:

1. A dedicated non-administrator NAS identity can read only the approved
   irreplaceable project scope and cannot create, modify, rename, or delete the
   synthetic source fixture.
2. The SMB source is mounted read-only with root-only NAS credentials outside
   Git. The exact server, share, mount, credential path, and account name remain
   private.
3. A dedicated non-login local identity exists and is the unit-template
   instance. It can read the mount, write only the local Restic/state/runtime
   directories, and cannot administer the host.
4. Restic and the required CIFS client package are installed from the reviewed
   Ubuntu repositories.
5. The local repository is initialized with a private Restic password supplied
   through systemd's credential mechanism. The password source stays root-only
   and outside Git.
6. The controller is installed as
   `/usr/local/libexec/home-lab-local-second-copy`, owned by root and not writable
   by the service identity.
7. The private configuration is created from the example with the actual source
   path and mode `0600`; it contains no password or NAS credential.

Do not enable the daily timer until a manual synthetic preflight and snapshot
pass. Do not enable retention or pruning until the restore checksum, source
immutability, failure/stale-state, consecutive-schedule, and Austin-approval
gates in [`../docs/backup-plan.md`](../docs/backup-plan.md) all pass.

## Validation and rollback

Repository tests use temporary synthetic directories and mocked `findmnt` and
Restic results. They do not mount a filesystem, contact a NAS, initialize a real
repository, or copy data.

Operational rollback is deliberately simple and non-destructive: stop and
disable the two timers, stop any active oneshot unit, and leave the repository
and last-success timestamp intact for investigation. Removing packages,
credentials, accounts, mounts, repository snapshots, or test fixtures is a
separate reviewed cleanup action; never combine it with emergency timer disable.
