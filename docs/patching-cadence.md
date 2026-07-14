# Patching Cadence (D18)

Operating policy and monthly runbook for OS updates on the lab machines. Recorded as decision **D18** in
[`DECISIONS.md`](../DECISIONS.md). This document changes no machine state.

## Policy summary

- **Automatic (stock, unchanged):** daily unattended upgrades install **security updates only**. The APT
  timers (`apt-daily.timer`, `apt-daily-upgrade.timer`) stay enabled; allowed origins remain the stock
  security set; **automatic reboot stays off**; no automatic cleanup is configured. Do not broaden the
  origins or add automatic cleanup.
- **Manual (monthly maintenance window):** all other available updates are applied by a human using the
  runbook below — simulate first, execute interactively, verify after.
- The two mechanisms are **complementary, not disjoint**: the manual `apt upgrade` considers all configured
  sources and may also apply a security update the daily run has not yet reached.
- **Machine order:** compute-node first (canary) → complete verification → then pi-server.
- **pi-server prerequisite:** run the same read-only automatic-update audit there before its first
  maintenance run; its configuration is unverified until then.

## Monthly window runbook

### 0. Session gate
1. Live-GitHub reconciliation per the Session Start Gate in [`CONTRIBUTING.md`](../CONTRIBUTING.md).
2. **Intended-host check:** the shell prompt must identify the target machine (for example
   `austin@compute-node`) before every group of commands. If the SSH session dropped, stop, reconnect, and
   discard anything run on the wrong host.
3. Open a second idle SSH session as a fallback and confirm local-console access is possible.

### 1. Preflight (read-only)
- Package health: `sudo dpkg --audit` (expect no output) and `apt-mark showhold` (expect none)
- Failed units: `systemctl --failed` — compare against the known baseline before adding change
- Lifelines: `systemctl is-active tailscaled`; SSH is **socket-activated**, so check `systemctl is-active
  ssh.socket` and confirm port 22 is listening with `sudo ss -tlnp | grep ':22 '` — do not judge SSH by
  `ssh.service` alone
- Capacity: `df -h /` (and `/boot` if it is a separate filesystem) and `free -h`
- Kernel and reboot state: `uname -r`; check whether `/var/run/reboot-required` already exists

### 2. Refresh and simulate
Run, in order: `sudo apt update`, then `apt list --upgradable`, then `apt -s upgrade`.

Use the **same command family** for simulation and execution (`apt`, not `apt-get`) so the plan matches the
action. Read the sectioned plan — Upgrading / Installing / Removing / Not upgrading. `apt upgrade` may
**install new dependencies** but must not remove packages: require **Removing: 0**. Entries under "Not
upgrading yet due to phasing" are legitimate Ubuntu phased-rollout deferrals — leave them for a later
window. Every source must be an expected official pocket. **Any proposed removal, dependency problem, or
unexpected source or package: stop and review before executing.**

### 3. Execute (interactive)
Run `sudo apt upgrade` — never `-y`. Read the complete live summary; it must match the simulation and still
show **Removing: 0** before answering `Y`. If a configuration-file or service-restart prompt appears, pause
and review it before answering. If the SSH session drops mid-run, do not rerun blindly: reconnect, check
whether APT is still running (`pgrep -a 'apt|dpkg'`), and inspect state (`sudo dpkg --audit`) before doing
anything else.

### 4. Verify (before any reboot)
- `sudo dpkg --audit` → clean
- `apt list --upgradable` → only expected leftovers (for example phased deferrals)
- `systemctl --failed` → no new failures versus the baseline
- `systemctl is-active tailscaled`; repeat the `ssh.socket` + port-22 check from preflight
- `uname -r` → the running kernel does not change until a reboot
- Check `/var/run/reboot-required` — its presence is the **only** trigger for a routine-patching reboot

### 5. Reboot rule
Reboots are **deliberate and never automatic**. For routine patching, reboot only when
`/var/run/reboot-required` exists, in a window where the machine is reachable. After the reboot, verify:
kernel version, `ssh.socket` and port 22, `tailscaled`, failed units versus baseline, and that the
reboot-required flag cleared. The local console is the last-resort access path.

### 6. Document
Record the run — counts, deferrals, reboot decision, anomalies — as a dated `STATUS.md` changelog entry,
and add any new lesson to [`docs/troubleshooting-log.md`](troubleshooting-log.md). Sanitized summaries
only; never raw terminal output.

## `apt full-upgrade` requires separate review
`full-upgrade` may **remove** installed packages to resolve dependencies, so it is not part of the routine
window. Use it only when a simulation shows plain `upgrade` cannot proceed, and only after its own
`apt -s full-upgrade` output is reviewed by Austin, Claude, and ChatGPT.

## Recovery limitations
There is **no universal APT rollback**. The real contingencies are: previous kernels remain selectable in
GRUB from the local console; `/var/log/apt/history.log` and `/var/log/apt/term.log` record every
transaction; and individual packages can sometimes be reinstalled at a prior version from the local cache —
per-package and not guaranteed. Patch conservatively, verify thoroughly, and keep console access available.
