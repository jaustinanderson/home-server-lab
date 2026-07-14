# Troubleshooting Log

Dated, sanitized findings from real operations — the *why* behind rules that might otherwise look
arbitrary. Newest entries at the bottom. No addresses, identifiers, secrets, or raw logs; summaries only.

## 2026-07-13 — systemd-networkd-wait-online fails once at boot (pre-existing, benign)
Patching preflight found `systemd-networkd-wait-online.service` in a failed state. The journal showed a
single boot-time timeout (from 2026-07-01) while waiting for the wired interfaces to reach a fully "online"
state; runtime connectivity over Tailscale was unaffected the whole time. Classified **pre-existing and
benign**, and recorded so post-maintenance comparisons don't misattribute it to patching. Deliberately not
"fixed" during a maintenance session — any networkd change is separate, reviewed work.

## 2026-07-14 — ssh.service "inactive" while SSH works fine (socket activation)
After a package upgrade, `systemctl is-active ssh` returned `inactive` — alarming, but benign. This host
uses **socket activation**: `ssh.socket` (enabled) holds port 22 and starts the service on demand, and the
upgrade's restart step had cleanly stopped the long-running daemon. What actually proves SSH health:
`ssh.socket` active, port 22 listening (`ss -tlnp`), and a fresh connection succeeding — all three were
verified. Lesson: on socket-activated hosts, judge SSH by the socket and the port, not `ssh.service` alone.

## 2026-07-14 — Phased updates legitimately deferred
`apt` listed two packages under "Not upgrading yet due to phasing." Ubuntu stages some updates to a
percentage of machines at a time (phased rollout), and apt deliberately waits its turn. Correct handling:
leave them — they arrive in a later window. This is not a dependency hold; do not force them.

## 2026-07-14 — Updates accumulating despite healthy automatic updates (by design)
The login banner showed dozens of available updates even though daily unattended upgrades had run
successfully every day. The automatic-update audit explained it: stock unattended-upgrades installs
**security pockets only**, and the accumulated packages were in `resolute-updates` — outside its allowed
origins. Accumulation of non-security updates between manual windows is **normal**, not a malfunction. The
combined policy is recorded as **D18**.

## 2026-07-14 — Wrong-host commands after a silently dropped SSH session
The Chromebook slept overnight and dropped the SSH session; the next commands ran **locally in the Penguin
container**, which answered with its own — different — timer and service state. The mistake was caught via
the shell prompt and failing repository paths; all wrong-host evidence was discarded and the audit rerun on
compute-node. Lesson: **verify the prompt identifies the intended host before every group of machine
commands**, and if a session drops, stop until the intended host is re-established. The Session Start Gate
now requires this check.
