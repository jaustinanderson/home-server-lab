# Project Status — Home Lab (compute-node + pi-server)

> **Single source of truth.** Austin, Claude, and ChatGPT read and edit this file *in place* — don't
> regenerate it; append a dated line to the Changelog. Target ~one page.
> **Public-safe** (public repo): no real IPs, MACs, passwords, PHI, or employer-internal details. Live
> addresses are derivable per box with `ip -br a` (DHCP) and `tailscale status` (tailnet).

**Last updated:** 2026-07-13

---

## Who & what this is
Austin (Jerad "Austin" Anderson), CG(ASCP) Cytogenetic Technologist, building a home lab toward
clinical-lab AI. Two tracks: **Track A** — data lake + AI pipeline for cytogenetic images
(metaphases/karyograms); **Track B** — synthetic-data lab-workflow tool (GPU-free). Per **D10, Track B is
the first win.**

## Non-negotiable constraints
- **No real patient data / PHI on this lab. Ever.** Public datasets + synthetic/fake data only.
- **Free & open-source** stack, installed cleanly (not snaps).
- **One phase at a time** — explain the *why*. Austin reviews and approves repository changes; all changes
  follow the applicable PR workflow in D16/D17.
- **Infrastructure-as-code from day one**; configs + runbook in git. Public repo + LinkedIn are sanitized
  derivatives of the truth.

## Machines
| Name | Hardware | Role | OS | User |
|---|---|---|---|---|
| **compute-node** | GMKtec M8 — Ryzen 5 PRO 6650H, 16GB, 1TB NVMe, dual 2.5GbE, Oculink | Hot/working store + AI compute | Ubuntu Server 26.04 | `austin` |
| **pi-server** | Raspberry Pi 5 8GB + 2TB SanDisk Extreme SSD (USB; OS+data) | Bulk archive + intended backup target (cold) | Ubuntu Server 26.04 | `ubuntu` |
| **Chromebook** | Acer Chromebook Plus 514 (tailnet device "nissa") | Control surface (SSH only, via Penguin terminal) | ChromeOS | `jeradaustinanderson` |

## Network
- Apartment-managed `/16` DHCP — no router admin, no static leases, no port forwarding.
- The two servers reach each other directly (~0.3 ms); mDNS `*.local` resolves *between the servers*.
- **Tailscale mesh VPN** is the remote-access layer: all three devices joined, stable per-device tailnet
  addresses, nothing exposed publicly, DHCP-churn-proof.
- **Operational rule (2026-07-12):** connect to the servers **from the Penguin terminal over their Tailscale
  addresses** — LAN IPs drift and the Chromebook's old saved SSH profiles were stale/mislabeled.
  **compute-node's login user is `austin`; pi-server's is `ubuntu`.** (MagicDNS name resolution from *inside
  Penguin* is untested — verify later; `.local` support in Penguin is optional convenience, not a gate.)

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
**Phase 3 — Core Linux Administration.** See [`docs/project-roadmap.md`](docs/project-roadmap.md) for the
authoritative phase sequence. Docker remains Phase 4.

**Immediate next action:** establish a patching cadence — on compute-node, review available updates
(`apt list --upgradable`), apply them through a documented, reboot-aware process, and capture a sanitized
before/after baseline as the first Phase 3 evidence. Each change continues to follow the D17 pull-request
workflow from the machine.

## Open items / maintenance
- **D10 vs. roadmap ordering:** D10 makes **Track B** the first win, but the roadmap frames Phase 7
  (PostgreSQL) as the start of **Track A**. Phases 3–6 are track-agnostic, so this doesn't bite yet —
  **resolve deliberately before Phase 7** (honor D10, or add a *new* dated decision that supersedes it). Do
  not rewrite D10.
- **Deferred convenience (none are gates):** guarded ssh-agent auto-load per session; MagicDNS-from-Penguin
  test; optional `.local` resolution in Penguin.
- Patching cadence for both boxes; pi-server due a kernel/reboot pass on the next visit.
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
  the Tailscale-from-Penguin rule and the `austin`/`ubuntu` usernames.
- **2026-07-13 — Austin + ChatGPT** — Reconciled the verified Git-authentication work through a focused
  Codex PR under D16; added **D17** for Austin-controlled machine-side changes; recorded the account-key
  scope as deliberate; aligned STATUS with the existing roadmap; and left Phase 2 in progress pending one
  real sanitized compute-node-originated PR. Deferred ssh-agent automation and Penguin name-resolution work.
- **2026-07-13 — Austin + Claude** — First genuine compute-node-originated change under **D17**: added a
  durable **Session Start Gate** to `CONTRIBUTING.md` (live-GitHub reconciliation before each session; treat
  rate-limit/error bodies as unverified) via branch → commit → push → PR → independent review → squash-merge
  (**PR #6**). This completed **Phase 2 — Repository-on-Host Workflow** and began **Phase 3 — Core Linux
  Administration**. The gate immediately caught stale-clone drift before branching.
