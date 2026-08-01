# Project Status — Home Server Lab

> **Single source of truth.** Austin, Claude, and ChatGPT read and edit this file *in place* — don't
> regenerate it; append a dated line to the Changelog. Target ~one page.
> **Public-safe** (public repo): no real IPs, MACs, passwords, PHI, or employer-internal details. Live
> addresses are derivable per box with `ip -br a` (DHCP) and `tailscale status` (tailnet).

**Last updated:** 2026-08-01

---

## Who & what this is
Austin (Jerad "Austin" Anderson), CG(ASCP) Cytogenetic Technologist, building a home lab toward
clinical-lab AI. Two tracks: **Track A** — data lake + AI pipeline for cytogenetic images
(metaphases/karyograms); **Track B** — synthetic-data lab-workflow tool (GPU-free). Per **D10, Track B is
the first win.**

## Non-negotiable constraints
- **No real patient data / PHI on this lab. Ever.** Public datasets + synthetic/fake data only (D1,
  reaffirmed by D21). De-identification alone is insufficient; any non-synthetic source must be a
  legitimately public, appropriately licensed dataset.
- **Free & open-source** stack, installed cleanly (not snaps).
- **One phase at a time** — explain the *why*. Austin reviews and approves repository changes; all changes
  follow the applicable PR workflow in D16/D17.
- **Infrastructure-as-code from day one**; configs + runbook in git. Public repo + LinkedIn are sanitized
  derivatives of the truth.

## Machines and storage
| Name | Hardware | Role | OS |
|---|---|---|---|
| **compute-node** | GMKtec M8 — Ryzen 5 PRO 6650H, 16GB, 1TB NVMe, dual 2.5GbE, Oculink | Hot working store + AI compute | Ubuntu Server 26.04 |
| **pi-server** | Raspberry Pi 5 8GB + 2TB SanDisk Extreme SSD (USB; OS+data) | Planned local secondary protection + lightweight services | Ubuntu Server 26.04 |
| **Synology NAS** | DS925+ — Btrfs on SHR; two matching 16TB drives; one-drive fault tolerance | Canonical source archive + protected personal-content store | Synology DSM |
| **Chromebook** | Acer Chromebook Plus 514 | Control surface (SSH only, via Penguin terminal) | ChromeOS |

The NAS is operational on the local network. The existing SHR pool now contains both matching 16 TB drives,
reports healthy with one-drive fault tolerance, and provides approximately 13.8 TB usable capacity. Both
drives passed extended S.M.A.R.T. tests; the first data scrub completed successfully; quarterly scrubbing is
scheduled; and the DSM warning/critical email-notification path was tested successfully. Synology Hyper
Backup to Backblaze B2 remains operational for selected current personal content on a daily schedule with
version retention and client-side encryption. A disposable file restored from the encrypted repository on
2026-07-31 matched its source SHA-256 checksum; this proves the tested backup version was recoverable, not
that future metaphase data is protected. See D19–D21 and `docs/backup-restore-test.md`.

## Network
- Apartment-managed `/16` DHCP — no router admin, no static leases, no port forwarding.
- The two servers reach each other directly (~0.3 ms); mDNS `*.local` resolves *between the servers*.
- **Tailscale mesh VPN** is the remote-access layer: all three devices joined, stable per-device tailnet
  addresses, nothing exposed publicly, DHCP-churn-proof.
- **Operational rule (updated 2026-07-31):** connect from the Penguin terminal through the tested SSH host
  aliases. Each alias uses the intended private username, the existing Ed25519 identity, `IdentitiesOnly yes`,
  and keepalives; both Tailscale hostnames now resolve from Penguin. LAN addresses can drift and must not be
  published. `.local` support in Penguin remains optional convenience, not a gate.

## Phase progress
- **Phase 1 — Foundation & Secure Access ✅** — Ubuntu Server 26.04 on both boxes; SSH keys-only, hardened
  and **independently verified both ways** (`sshd -T` + a refused external password login; cloud-init override
  removed, see D14); Tailscale on all three devices with verified remote access and reboot recovery;
  source-of-truth + public documentation set established and reconciled; ShellCheck CI gate.
- **Phase 2 — Repository-on-Host Workflow ✅** — the infrastructure repo is managed from compute-node.
  GitHub push authentication works from compute-node (repository cloned over SSH on `main`; dedicated
  passphrase-protected ed25519 key; deterministic `IdentitiesOnly` configuration; GitHub host key checked
  against the published fingerprint; `ssh -T` greeting; GitHub noreply git identity). The key is deliberately
  **account-scoped** (not a repo deploy key) because compute-node may serve future Austin-owned repositories;
  the passphrase, hardened key-only SSH configuration, preferred administrative access through Tailscale, and
  per-machine revocability make this acceptable. **Machine-side proof (D17):** the first real sanitized
  compute-node-originated change — adding the durable Session Start Gate to `CONTRIBUTING.md` — was carried
  through branch → commit → push → PR → independent review → squash-merge as **PR #6**, with `main` untouched
  until merge.

## Current phase
**Phase 3 — Core Linux Administration ✅.** Both hosts completed a refreshed D18 maintenance window,
required controlled reboots, package audits, service checks, log inspection, and sanitized resource
baselines. `compute-node` now runs kernel `7.0.0-28-generic`; `pi-server` runs
`7.0.0-1015-raspi` after a protected `piboot-try` promotion. Both returned with clean package state, no
failed units, working Tailscale and SSH, and no reboot flag. The compute-node's disconnected secondary
Ethernet port is retained but marked optional in Netplan, eliminating the prior boot wait-online timeout.

**Phase 3.5 — NAS Storage Readiness** is now the current phase. Sections A and B of
`docs/nas-readiness-checklist.md` are complete. Docker remains Phase 4.

**Immediate next action:** issue #17 is complete — the dedicated metaphase archive boundary, its
least-privilege routine workflow identity, and verified `compute-node` access are recorded in
`docs/metaphase-archive-boundary.md`. Next implement provenance/license/checksum promotion controls in
issue #18 and the planned NAS-to-`pi-server` local second copy in issue #19. Only then run issue #15's one
bounded public/synthetic pilot. Passing section E completes Phase 3.5 and unlocks Phase 4.

The users/groups/ownership/permissions inventory and its least-privilege exercise are complete on both Linux
machines. One item remains open and deliberately deferred: pi-server's passwordless-sudo (`NOPASSWD`)
divergence from compute-node (see `docs/linux-command-notes.md`). Each repository change continues to
follow the applicable D16/D17 pull-request workflow.

## Open items / maintenance
- **D10 vs. roadmap ordering:** D10 makes **Track B** the first win, but the roadmap frames Phase 7
  (PostgreSQL) as the start of **Track A**. Phases 3–6 are track-agnostic, so this doesn't bite yet —
  **resolve deliberately before Phase 7** (honor D10, or add a *new* dated decision that supersedes it). Do
  not rewrite D10.
- **Deferred convenience (none are gates):** guarded ssh-agent auto-load per session; optional `.local`
  resolution in Penguin.
- Patching cadence **established and exercised twice on both machines (D18)**. The July 31 window included
  deliberate reboots and complete recovery verification on both hosts.
- **Metaphase-ingestion gate:** do not begin corpus acquisition. Second-drive protection, NAS health, one
  disposable personal-content restore, the dedicated archive share/permissions, and verified `compute-node`
  access now pass; a single small public pilot remains blocked on provenance/license/checksum controls, local
  second copy, and metaphase-specific protection design.
- **Backup boundary:** Backblaze currently protects NAS personal content off-site, but metaphase manifests,
  annotations, databases, and working derivatives do not yet have a completed, tested recovery design.
- One public repo (sanitized) vs. a future private repo for sensitive operational detail — decide later.

## Changelog
*(Append new lines at the bottom. Format: `YYYY-MM-DD — who — what`.)*
- *(prior, June 2026)* — pi-server initial build in an earlier session: Ubuntu 26.04 on the 2TB SSD,
  SSH enabled, Avahi, reachable as `pi-server.local`.
- **2026-06-24 — Austin + Claude** — Foundation build: Ubuntu 26.04 on both boxes; mutual reachability
  confirmed; Avahi on compute-node; SSH keys deployed to both; compute-node reboot-tested; password
  rotated. (A hardening file was written on compute-node but later found ineffective — see 2026-07-01.)
- **2026-07-01 — Austin + Claude** — Created STATUS.md + DECISIONS.md and committed them to the repo.
  Hardened + verified **pi-server** (removed leftover `00-enable-password-login.conf`). Discovered
  **compute-node**'s `50-cloud-init.conf` was silently re-enabling password auth; removed it. Verified
  **both** machines refuse password logins via live external test. (Lesson recorded as DECISIONS D14.)
- **2026-07-01 — Austin + Claude** — Installed **Tailscale** on both servers + the Chromebook and verified
  remote access (SSH to compute-node by tailnet address from the Chromebook, no password). Rebooted
  compute-node: pending kernel update applied (now on 7.0.0-27) and Tailscale confirmed to auto-start and
  survive the reboot. Foundation, remote access, and the shared source-of-truth system are all complete.
- **2026-07-10 — Austin + ChatGPT** — Reconciled the README, setup log, and SSH notes with the verified
  two-machine architecture; removed stale Pi-only and future-tense SSH claims; added a ShellCheck GitHub
  Actions quality gate for public shell scripts.
- **2026-07-11 — Austin + ChatGPT** — Completed the documentation reconciliation across network,
  security, backup, scripts, and diagrams; added a current architecture diagram; aligned every next-step
  list with this file; made `system-info.sh` safer to share by default; and recorded the focused Codex
  pull-request workflow as decision D16.
- **2026-07-12 — Austin + Claude** — Established GitHub push authentication on compute-node (dedicated
  passphrase-protected ed25519 account key, `IdentitiesOnly` config, verified host key + `ssh -T`, git
  identity, SSH clone on `main`, and proven test-branch push/delete). A stale-connection detour reaffirmed
  the Tailscale-from-Penguin rule and the need to use the correct private per-host usernames.
- **2026-07-13 — Austin + ChatGPT** — Reconciled the verified Git-authentication work through a focused
  Codex PR under D16; added **D17** for Austin-controlled machine-side changes; recorded the account-key
  scope as deliberate; aligned STATUS with the existing roadmap; and left Phase 2 in progress pending one
  real sanitized compute-node-originated PR. Deferred ssh-agent automation and Penguin name-resolution work.
- **2026-07-13 — Austin + Claude** — First genuine compute-node-originated change under **D17**: added a
  durable **Session Start Gate** to `CONTRIBUTING.md` (live-GitHub reconciliation before each session; treat
  rate-limit/error bodies as unverified) via branch → commit → push → PR → independent review → squash-merge
  (**PR #6**). This completed **Phase 2 — Repository-on-Host Workflow** and began **Phase 3 — Core Linux
  Administration**. The gate immediately caught stale-clone drift before branching.
- **2026-07-14 — Austin + Claude + ChatGPT** — First Phase 3 maintenance run on compute-node: simulated with
  `apt -s upgrade`, then interactively applied **38 upgrades (0 removed, 0 newly installed)**; two updates
  legitimately deferred by Ubuntu phasing; **no reboot required**; no new failed units; SSH verified healthy
  via **socket activation** (`ssh.socket` + port 22). A read-only audit showed daily **security-only**
  unattended upgrades already running healthily with auto-reboot off; recorded the combined policy as
  **D18**, added the runbook (`docs/patching-cadence.md`) and first lessons (`docs/troubleshooting-log.md`),
  and strengthened the Session Start Gate with an intended-host check. Next: the same audit on pi-server.
- **2026-07-14 — Austin + Claude + ChatGPT** — Completed pi-server's read-only automatic-update audit and
  first D18 maintenance run. Its stock daily security-only configuration matched compute-node (healthy
  timers, no automatic reboot or cleanup). The reviewed transaction applied **38 upgrades (0 removed, 0
  newly installed)** and left two legitimate phased deferrals. A pending kernel required a deliberate
  Raspberry Pi staged-asset reboot with `piboot-try`; the new kernel booted, both retained boot slots reported
  `good`, the reboot flag cleared, and Tailscale, SSH, zero failed units, and a second fresh connection were
  verified. Patching is now established on both machines; next: users/groups/ownership/permissions practice.
- **2026-07-19 — Austin + Claude + Codex** — Completed the Phase 3 users/groups/ownership/permissions
  inventory on both machines and a least-privilege exercise. Both hosts run a single regular login account
  with sole `sudo` membership, locked root password, disabled SSH password authentication, and no root SSH
  keys (no usable direct-root credential via the verified password and default authorized-keys paths; see
  `docs/linux-command-notes.md`). Both had their login user in the `lxd` group while only the
  wrapper (`lxd-installer`) — not full LXD — was installed; the membership was removed on each and verified
  in a fresh login session, eliminating latent root-equivalent access should LXD ever be installed.
  Documented the commands and concepts in `docs/linux-command-notes.md`. One divergence is recorded and
  left unresolved: pi-server grants the login user passwordless sudo (`NOPASSWD`), where compute-node
  requires a password; any future change awaits its own preflight and review.
- **2026-07-27 — Austin + ChatGPT/Codex** — Promoted the completed read-only Linux storage review into
  `docs/storage-baseline.md`; incorporated the DS925+ as the canonical source archive through D19; recorded
  the one-drive/no-protection boundary and the second 16 TB drive expected 2026-07-28; and added the Phase
  3.5 NAS-readiness gate. Recorded owner-confirmed daily Synology Hyper Backup to Backblaze B2 as operational
  for current NAS personal content through D20 while preserving the untested-restore and unverified-encryption
  boundaries.
- **2026-07-29 — Austin + ChatGPT/Codex** — Recorded the second matching 16 TB NAS drive as installed and
  added to the existing SHR pool, with DSM conversion/synchronization in progress. Preserved the unverified
  redundancy, drive-health, backup-currency, encryption, restore, and metaphase-authorization boundaries;
  clarified that readiness sections A–D authorize one bounded pilot and section E completes Phase 3.5.
  A repository-safety audit also corrected MAC-address disclosure in `system-info.sh`, reversed the local
  NAS-to-pi backup arrow, sanitized operational account/device identifiers, added continuous privacy/link
  checks, and recorded D21 to restore D1's public-or-synthetic-only data boundary.
- **2026-07-31 — Austin + ChatGPT/Codex** — Completed refreshed Phase 3 baselines and a second D18 maintenance
  window on both Linux hosts. `compute-node` was patched, rebooted into kernel `7.0.0-28-generic`, and
  verified clean after retaining its disconnected secondary Ethernet port as optional in Netplan, which
  removed the prior wait-online failure. `pi-server` was patched and promoted through the guarded
  `piboot-try` path into kernel `7.0.0-1015-raspi`; its boot state returned `good`. Both hosts passed package,
  service, SSH/Tailscale, log, disk, memory, and reboot-status checks, and both Chromebook SSH aliases were
  verified. The NAS SHR conversion completed healthy with one-drive fault tolerance; both drives passed
  extended S.M.A.R.T. tests; DSM email alerts were tested; the first data scrub completed successfully; and
  quarterly scrubbing was scheduled. Phase 3 is complete; Phase 3.5 now proceeds with restore and data-
  governance controls.

- **2026-07-31 — Austin + ChatGPT/Codex** — Inspected the current Hyper Backup task and verified a successful
  scheduled run, selected personal-content scope, daily schedule, weekly integrity checks, Smart Recycle
  version retention, client-side encryption, tested failure notifications, and privately stored recovery
  credentials. A deterministic disposable file was backed up manually, copied from the encrypted Backblaze
  repository into an isolated destination, downloaded, and verified byte-for-byte by matching SHA-256
  checksums. A first destination-selection mistake was corrected without data loss; the isolated restore was
  repeated successfully. Both disposable NAS folders were removed. Exact copy duration was not captured, so
  no recovery-time objective is claimed. Issue #13 is technically complete; metaphase-specific backup and
  recovery remain pending.
- **2026-08-01 — Austin + Claude** — Completed issue #17: created the dedicated metaphase archive share with
  its eight-area structure (governance/manifests, quarantine, canonical raw sources, approved releases,
  annotations, working derivatives, exports, logs); created a least-privilege routine workflow identity
  scoped to that share over SMB, separate from NAS administration and unable to reach personal
  home-directory storage; verified canonical raw sources and approved releases reject create/modify/rename/
  delete from that identity while remaining readable, and that the working-derivative area stays fully
  writable; verified `compute-node`'s on-demand SMB 3.1.1 automount (root-owned `0600` credential file,
  `nosuid`/`nodev`/`noexec`, network-dependent, non-fatal at boot) activates on access and survives a normal
  reboot with passing post-reboot permission tests; and confirmed active transformations stay on
  `compute-node`'s local NVMe ext4 workspace, not the NAS. No real dataset was ingested; only disposable
  synthetic placeholders were used and removed afterward. A reboot with the NAS deliberately offline was not
  tested. Recorded in `docs/metaphase-archive-boundary.md` and section B of `docs/nas-readiness-checklist.md`.
  Next: issue #18 (provenance/license/checksum controls).
