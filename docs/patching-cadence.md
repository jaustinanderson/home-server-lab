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
- **Verified on both machines:** the read-only audit and first manual window are complete on compute-node
  and pi-server. Both retain the same stock automatic-update policy.

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
- Lifelines: `systemctl is-active tailscaled`; inspect both `ssh.socket` and `ssh.service` because activation
  state may differ by host or during an upgrade; confirm the ground truth with
  `sudo ss -tlnp | grep ':22 '` and a fresh connection — do not judge SSH by `ssh.service` alone
- Capacity: `df -h /` and `free -h`; also check the boot filesystem when separate (`/boot/firmware` on
  pi-server)
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
- `systemctl is-active tailscaled`; repeat both SSH-unit checks plus the port-22 check from preflight
- `uname -r` → the running kernel does not change until a reboot
- Check `/var/run/reboot-required` — its presence is the **only** trigger for a routine-patching reboot

### 5. Reboot rule
Reboots are **deliberate and never automatic**. For routine patching, reboot only when
`/var/run/reboot-required` exists, in a window where the machine is reachable. After the reboot, verify:
kernel version, both SSH units and port 22, `tailscaled`, failed units versus baseline, a second fresh SSH
connection, and that the reboot-required flag cleared. The local console is the last-resort access path.

On pi-server, a kernel/firmware update may stage A/B boot assets in `/boot/firmware/new`. If the login banner
reports untested assets, require physical recovery access, run `piboot-try --test`, and use
`sudo piboot-try --reboot` instead of a plain reboot. After reconnecting, verify the expected kernel and the
boot-slot state files. A successful promotion removes the pending `new` slot and leaves the retained
`current` and `old` slots marked `good`; with no pending slot, a later `piboot-try --test` exits nonzero
because there is nothing left to test.

### 6. Document
Record the run — counts, deferrals, reboot decision, anomalies — as a dated `STATUS.md` changelog entry,
and add any new lesson to [`docs/troubleshooting-log.md`](troubleshooting-log.md). Sanitized summaries
only; never raw terminal output.

## Verified first runs (2026-07-14)
- **compute-node (canary):** 38 upgrades, 0 newly installed, 0 removed, two phased deferrals; no reboot
  required; lifelines and failed-unit baseline verified.
- **pi-server:** 38 upgrades, 0 newly installed, 0 removed, two phased deferrals; the pending kernel was
  activated through a successful `piboot-try` staged reboot; boot slots, lifelines, failed units, package
  health, reboot flag, and a second fresh SSH connection were verified afterward.

## `apt full-upgrade` requires separate review
`full-upgrade` may **remove** installed packages to resolve dependencies, so it is not part of the routine
window. Use it only when a simulation shows plain `upgrade` cannot proceed, and only after its own
`apt -s full-upgrade` output is reviewed by Austin, Claude, and ChatGPT.

## Recovery limitations
There is **no universal APT rollback**. The real contingencies are: previous kernels remain selectable in
GRUB from the local console; `/var/log/apt/history.log` and `/var/log/apt/term.log` record every
transaction; and individual packages can sometimes be reinstalled at a prior version from the local cache —
per-package and not guaranteed. Patch conservatively, verify thoroughly, and keep console access available.
