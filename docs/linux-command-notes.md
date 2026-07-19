# Linux Command Notes

Sanitized reference for the Core Linux Administration work in this lab — the commands used to inventory
users, groups, sudo, ownership, permissions, and SSH policy, with the concepts behind them. Read-only
inspection unless explicitly noted. No addresses, key contents, or credentials appear here.

## Identity, users, and groups
- `id` — the current user's UID/GID and **supplementary groups**; the core of what access an account has.
- `whoami`, `hostname` — confirm *who* and *which host* before acting (a dropped SSH session can silently
  drop you back onto the local machine; always check the prompt).
- `getent group NAME` — authoritative group membership (consults all sources, not just `/etc/group`).
- Scanning `/etc/passwd` (read-only): login-capable accounts are those whose shell is not `nologin`/`false`;
  regular (human) accounts conventionally start at UID 1000; lower UIDs are system/service accounts that
  daemons run as. A `sync` account whose shell is `/bin/sync` is a harmless traditional fossil.

### Private (per-user) primary groups and `umask 0002`
Ubuntu gives each user a **private primary group** of the same name (e.g. `austin:austin`), so a
group-writable default is safe: files you create are group-owned by *your own* group, not a shared one.
`umask 0002` therefore yields `775` directories and `664` files — convenient for a single-user working tree
without exposing files to other humans, because the "group" is just you.

### Supplementary-group changes require a fresh login
Group membership is **stamped into your session at login**. After changing a user's groups, the *current*
session still shows the old set; you must open a **new login session** to see (and exercise) the change.
Verifying in a fresh session is how this lab confirms such changes took effect.

## Ownership, modes, and path traversal
- `ls -ld PATH` — owner, group, and mode of a directory itself (not its contents).
- A mode like `750` on a home directory means owner full, group read/execute, others nothing.
- **Traversal depends on every parent.** To reach `/a/b/c`, a process needs execute (`x`) on `/`, `a`, and
  `b`, plus the relevant permission on `c`. A single missing `x` anywhere along the path blocks access
  regardless of how permissive the target itself is. This is why home-directory modes and each parent's
  bits matter more than the final file's mode alone.

## sudo and root
- `sudo passwd -S USER` — password **status** only (`L` locked, `P` set, `NP` none); never reveals secrets.
- Effective SSH policy comes from `sudo sshd -T | grep -E 'permitrootlogin|passwordauthentication|pubkeyauthentication'`
  — the daemon's *running* configuration. Inspecting config files alone can mislead when drop-ins override
  them (a lesson learned earlier in this lab), so query the daemon.
- Root login is effectively impossible on a host when the root password is **locked**, SSH
  `passwordauthentication` is **no**, and root has **no** `authorized_keys` — even if `permitrootlogin` is
  `prohibit-password`, there is simply no credential to present. (Check key *count*, never contents.)
- `sudo` rules live in `/etc/sudoers.d/`; validate any edit with `visudo` (syntax-checks before saving) —
  a malformed sudoers file plus a locked root account is a console-recovery situation.

## The `lxd` group and wrapper-only LXD
`lxd` group membership is effectively **root-equivalent *if* LXD is installed**, because a member can define
containers that map the host filesystem. On both machines in this lab, only Ubuntu's on-demand
`lxd-installer` wrapper (and `lxd-agent-loader`) is present — **full LXD is not installed** (no LXD snap, no
LXD storage). Membership therefore granted no active capability today, but it was **latent** privilege that
would activate the moment LXD were ever installed.

**Least-privilege exercise (completed on both machines):** the login user was removed from the unused `lxd`
group with `sudo gpasswd -d USER lxd`, confirmed with `getent group lxd` (empty member list) and a
**fresh-session** `id` (no `lxd`). Reversible in one step (`sudo gpasswd -a USER lxd`). The `lxd-installer`
wrapper was deliberately left in place. This removes latent root-equivalent access without affecting any
running service.

## Recorded divergence (unresolved): passwordless sudo on pi-server
The two machines differ in one meaningful way. compute-node requires a password for `sudo`; pi-server's
login user has **passwordless sudo** (`NOPASSWD:ALL`, from a cloud-init sudoers drop-in). On pi-server this
means a single compromised SSH key yields silent root, whereas compute-node also requires the account
password. This is **recorded but not yet changed.** Before any change, the lab will confirm: the account has
a known, usable password; `sudo` password authentication actually works; console/recovery access is
available; the sudoers edit is `visudo`-validated; and a root-capable session stays open during testing.
Tightening sudoers without those safeguards risks locking out administrative access.
