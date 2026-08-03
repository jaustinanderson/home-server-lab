# Project Status — Home Server Lab

> **Single source of truth.** Austin, Claude, and ChatGPT read and edit this file *in place* — don't
> regenerate it; append a dated line to the Changelog. Target ~one page.
> **Public-safe** (public repo): no real IPs, MACs, passwords, PHI, or employer-internal details. Live
> addresses are derivable per box with `ip -br a` (DHCP) and `tailscale status` (tailnet).

**Last updated:** 2026-08-02

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

**Phase 3.5 — NAS Storage Readiness** is now the current phase. Sections A, B, and C of
`docs/nas-readiness-checklist.md` are complete on `main`. Docker remains Phase 4.

**Immediate next action:** issue #17 is complete on `main`. Issue #18's section C
provenance/license/checksum manifest schema and fail-closed validator merged into `main` via PR #22
(`a8e361d`, reviewed head `acc15e2`); an exact-head Repository checks run #86 passed all repository
checks, including all 27 promotion-validator tests. Issue #18 is closed. For issue #19, a read-only
architecture and capacity preflight on `pi-server` is complete, and D23 records the selected architecture
(pi-server-initiated pull, encrypted Restic repository, read-only NAS SMB source, capacity/retention limits,
and a planned monitoring design). The repository now contains the fail-closed controller, hardened systemd
service/timer templates, sanitized configuration example, and a 20-test synthetic suite for the public-safe
automation layer. No account, package, mount, credential, installed service, enabled timer, initialized
repository, or snapshot has been created — issue #19 remains open, and private deployment,
monitoring/failure proof, source-immutability proof, and a checksum-verified disposable restore are still
pending. Only after that gate passes should issue #15's one bounded public/synthetic pilot begin. Passing
section E completes Phase 3.5 and unlocks Phase 4.

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
  disposable personal-content restore, the dedicated archive share/permissions, verified `compute-node`
  access, and the provenance/license/checksum/transformation-linkage/path-safety/fail-closed controls all
  pass on `main` (issue #18, PR #22). The bounded pilot remains blocked on issue #19's local second copy,
  monitoring/failure detection, and checksum-verified disposable restore. Bulk acquisition and general
  metaphase ingestion remain prohibited.
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
- **2026-08-01 — Austin + Claude + ChatGPT/Codex** — Staged the repository-controlled
  implementation for issue #18 in draft PR #22: a strict versioned JSON Schema promotion-manifest contract
  (`docs/promotion-manifest.schema.json`), a dependency-free Python standard-library validator
  (`scripts/validate-promotion-manifest.py`), nine synthetic fixture directories
  (`scripts/promotion-manifest-fixtures/`; one valid and eight rejection fixtures), and 16 automated tests
  (`scripts/test_promotion_manifest_validator.py`) wired into GitHub Actions alongside ShellCheck, the
  system-info privacy regression, and the Markdown-link check. A semantic audit found and corrected a
  pre-merge fail-closed gap: noneligible workflow states and malformed/unknown contract fields could have
  escaped the original representative fixture coverage. The validator now rejects every noneligible
  `eligibility_state`, invalid source locators/dates/timestamps/step sequences, and unknown root or nested
  fields; it still verifies actual SHA-256 bytes, path containment, approved license/origin/identifier
  states, allowed source classifications, false disallowed-content flags, and derivative history. An exact-head GitHub Actions run passed all 16 tests and every repository check. Only synthetic fixtures were used; no real
  dataset or NAS archive content was accessed or changed. Section C is implemented and CI-verified on the
  draft branch, but issue #18 remains open until PR #22 is reviewed, merged with Austin's approval, and
  verified on `main`. Issue #19 and the bounded pilot remain blocked until then.
- **2026-08-02 — Austin + Claude** — Review on PR #22 added further fail-closed coverage beyond the
  2026-08-01 checkpoint (derivative transformation linkage, transformation reference integrity, and
  rejection of drive-relative and file URI references), bringing the suite to 27 automated tests before
  merge. PR #22 merged into `main` as `a8e361d` (reviewed head `acc15e2`); the exact-head Repository checks
  run #86 passed all 27 tests and every other repository check. Section C of
  `docs/nas-readiness-checklist.md` is now complete on `main`, closing issue #18. This entry reconciles
  STATUS.md and the readiness checklist to that verified `main` state. Issue #19 — the NAS-to-`pi-server`
  local second copy, monitoring/failure detection, and checksum-verified disposable restore — is the next
  implementation gate; the bounded issue #15 pilot remains unauthorized until it is complete. No real
  dataset or NAS content was accessed during this reconciliation.
- **2026-08-02 — Austin + Claude** — Completed a read-only architecture and capacity preflight for issue
  #19's local NAS-to-`pi-server` second copy, using only pi-server measurements gathered manually through
  the existing trusted Chromebook SSH alias; neither server nor the NAS was reconfigured or accessed for
  this checkpoint. Sanitized findings: `pi-server`'s dedicated SSD reports approximately 1.79 TiB total
  root capacity at about 1% used (roughly 3.26 GiB used, 1.715 TiB available), zero mounted CIFS/NFS
  filesystems, zero failed systemd units, NTP-synchronized time, and rsync/sha256sum/Python already
  installed, while Restic, Borg, and SMB/CIFS client tooling remain uninstalled; the 06:00–07:00 UTC daily
  maintenance window was identified as undesirable for a future backup schedule. Recorded **D23**: pi-server
  will pull an encrypted Restic repository from a read-only NAS SMB source, scoped to a dedicated
  non-administrator NAS backup identity and an explicitly approved irreplaceable-data-only scope, with a 256
  GiB repository ceiling, 192 GiB warning threshold, 512 GiB minimum free-space reserve, a proposed
  ~03:30 UTC daily schedule, and a 7-daily/4-weekly/6-monthly target retention with automatic pruning
  withheld until the synthetic proof, monitoring, and Austin's approval are all in place. The plan documents
  an explicit encryption caveat: Restic's repository encryption does not by itself protect against physical
  disk extraction, since `pi-server`'s SSD is not LUKS-encrypted. Updated `docs/backup-plan.md` (architecture,
  protected scope, capacity/retention, monitoring design), `docs/backup-restore-test.md` (planned synthetic
  proof sequence), and `docs/nas-readiness-checklist.md` (preflight evidence). This is architecture selection
  and read-only verification only — no NAS or pi-server account, package, mount, credential, service, timer,
  or snapshot was created, issue #19 remains open, and issue #15's pilot remains unauthorized.
- **2026-08-03 — Austin + ChatGPT/Codex** — Implemented issue #19's public-safe repository-controlled
  automation layer without changing either server or the NAS: added a dependency-free fail-closed Python
  controller for read-only-CIFS/local-Restic preflight, conservative capacity/reserve enforcement, exclusive
  execution, quiet Restic snapshot and repository check, post-run mount/capacity verification, atomic
  success-state recording, and a separate 36-hour stale-state check; added hardened systemd oneshot and
  timer templates for the daily ~03:30 UTC job and six-hour stale check; and added a sanitized private-config
  example and deployment/rollback boundary. Twenty synthetic tests use temporary directories and mocked
  command results to prove success behavior and fail-closed rejection of writable/missing mounts, network
  repositories, path overlap, broad credential permissions, concurrent execution, capacity/reserve breach,
  disappearing mounts, Restic failures, and missing/stale success state. No package, account, credential,
  mount, repository, service, timer, snapshot, NAS access, server connection, or data copy occurred. Issue
  #19 remains open; operational deployment and the checksum/source-immutability/failure proofs still gate
  issue #15.
