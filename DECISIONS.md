# Decisions Log — Home Lab

> **Append-only.** Each entry is a settled choice and *why*. Don't silently re-open these — if
> something genuinely needs revisiting, add a **new** dated entry that supersedes the old one and
> says so. This doubles as Austin's learning record.
>
> **Public-safe** — no internal IPs/MACs/secrets.

---

**D1 — No real patient data / PHI on the home lab. Ever.** *(2026-06)*
Public datasets + synthetic/fake data only. Real clinical data stays on sanctioned institutional
infrastructure. This is the hard architectural boundary everything else respects.

**D2 — Two matched machines, split by role.** *(2026-06)*
compute-node (mini PC, fast NVMe) = hot/working store + AI compute. pi-server (Pi 5 + 2TB SSD) =
bulk archive + backup. Both on Ubuntu Server 26.04 for one consistent environment.

**D3 — Free & open-source only.** *(2026-06)*
No paid services to start; nothing needs buying to begin.

**D4 — Infrastructure-as-code from day one.** *(2026-06)*
Configs, scripts, and a runbook live in git so the whole stack is reproducible and documented.

**D5 — Network: lean on DHCP + mDNS, not static IPs.** *(2026-06)*
The apartment network is managed (no router admin, no static leases, no port forwarding). So: leave
DHCP on, use Avahi/`.local` names. A direct Cat6 link between the boxes is an optional future
upgrade — not needed (the network already allows device-to-device traffic).

**D6 — Tailscale for remote access (over port-forwarding / manual VPN).** *(2026-06)*
No router admin means no port forwarding. Tailscale gives encrypted device-to-device access from
anywhere, fixes the changing-DHCP-IP problem, and exposes nothing to the public internet.

**D7 — SSH: keys only, hardening via drop-in config files.** *(2026-06)*
Key-based auth + `PasswordAuthentication no`, applied via `/etc/ssh/sshd_config.d/99-hardening.conf`
(not by editing the main `sshd_config`). Priority was bumped up because a shared apartment network
exposes the SSH port to neighbors. Always test a fresh login in a **new tab** before trusting the lock.
(See D14 for the critical gotcha this exposed.)

**D8 — Install Docker/Postgres/etc. cleanly — NOT as snaps.** *(2026-06)*
Snap versions are often outdated or behave differently and cause confusing problems. Install the
standard way so the setup is portable and predictable. (MinIO / fancy networking are optional at this
scale, not required.)

**D9 — No GPU purchase yet.** *(2026-06)*
The real bottleneck is labeled data, not compute. Rent a cloud GPU when there's data ready to train on.
The mini PC's Oculink port leaves an eGPU path open only if a sustained need appears.

**D10 — Two tracks; workflow tool first.** *(2026-06)*
Track A = image-AI data lake (needs data + eventually GPU). Track B = lab-workflow tool on synthetic
data (GPU-free, more self-contained) — the easier first win.

**D11 — Backups: protect the irreplaceable, re-download the rest.** *(2026-06)*
Code, DB, and annotations get backed up (git + a cheap cloud bucket like Backblaze B2 / Cloudflare R2,
later). Public datasets are re-downloadable, so they don't need precious backup space.

**D12 — Single source of truth = STATUS.md + DECISIONS.md, edited in place.** *(2026-06-30)*
Both AI assistants (Claude, ChatGPT) and Austin read/edit these two files rather than each generating
separate summaries that drift apart. Public repo + LinkedIn are sanitized derivatives of this truth.
Divergence between assistants is fine and *visible* — Austin decides.

**D13 — Ubuntu installed without LVM / LUKS.** *(2026-06-24)*
Kept storage simple for a first build: plain ext4 root, no logical-volume layer, no disk encryption.
Revisit only if a concrete need appears.

**D14 — New Ubuntu boxes ship a cloud-init SSH override; remove it, then VERIFY.** *(2026-07-01)*
A fresh Ubuntu Server install writes `/etc/ssh/sshd_config.d/50-cloud-init.conf` containing
`PasswordAuthentication yes`. Because SSH reads drop-in files in order and honors the **first** match,
`50-*` overrides our `99-hardening.conf` and silently keeps password login **on**. Standing procedure
for every new box: (1) write `99-hardening.conf`; (2) remove `50-cloud-init.conf` (and any
`00-*enable-password*` file); (3) `sudo systemctl restart ssh`; (4) **verify two ways** — run
`sudo sshd -T | grep passwordauth` (must say `no`) **and** an external password-only login test
(`ssh -o PubkeyAuthentication=no -o PreferredAuthentications=password user@host`, which must be refused
with `Permission denied (publickey)`). Never assume the file worked — confirm the running service.
(Found live on compute-node 2026-07-01: it had appeared "hardened" since 06-24 but was still accepting
passwords. Caught only because we re-checked.)

**D15 — Staged AI collaboration; don't jump to the heavy agentic setup.** *(2026-07-01)*
Tiers: **Claude Pro + ChatGPT Plus.** Phase 1 (now): `home-server-lab` is the shared hub; both AIs
**read** it (via connector, or Austin pastes); **Austin commits everything himself**. Phase 2: use
**Codex** (included in Plus; runs in a cloud sandbox and opens **PRs Austin reviews**) as the natural
path for AI-authored changes. Phase 3 (only if a real need appears): heavier agentic layer — Claude Code
CLI inside Penguin, GitHub MCP server, a formal coordination issue. Rationale: match tooling to a
beginner's understanding and to the hardware (Chromebook rules out Claude Desktop; Codex is the natural
write path). This deliberately defers the all-at-once integration plan ChatGPT drafted. Austin arbitrates
any Claude/ChatGPT divergence via this log.

**D16 — Focused Codex pull requests are now the AI write path.** *(2026-07-11)*
Phase 2 of D15 is active for repository maintenance: Codex works on a focused branch, runs proportionate
checks, and opens a pull request for review rather than writing directly to `main`. Austin retains the
merge decision. This does **not** mean the lab machines have GitHub push authentication; that separate
host setup remains pending in `STATUS.md`.

**D17 — Machine-side changes use an Austin-controlled pull-request workflow, never direct pushes to `main`.** *(2026-07-12)*
With push authentication working on compute-node, Austin may directly make or apply changes from the lab
machine. Every machine-originated change follows branch → review diff → commit → push → pull request →
review → merge. Austin is responsible for verifying and approving the resulting diff. This complements D16:
Codex remains the repository-integrated AI write path, while compute-node provides Austin's directly
controlled machine-side path. Neither path writes directly to `main`.

**D18 — Patching policy: daily security-only unattended upgrades stay stock; everything else patches through a monthly manual window.** *(2026-07-14)*
A read-only audit confirmed compute-node's stock automatic-update configuration is healthy: the daily APT
timers run, unattended-upgrades installs **security updates only** (`resolute-updates` is not an allowed
origin), **automatic reboot is off**, and no automatic cleanup is configured. That configuration **remains
enabled and unchanged**. All other available updates are applied in **one monthly manual maintenance window**:
refresh metadata, simulate with `apt -s upgrade`, review the full transaction — it may install new
dependencies but must propose **zero removals** — then run an **interactive `sudo apt upgrade`**, never `-y`.
`apt full-upgrade` is allowed only after a separate simulation reviewed by Austin, Claude, and ChatGPT,
because it may remove packages. Reboots are deliberate and never automatic; for routine patching, reboot only
when `/var/run/reboot-required` exists, followed by recovery verification. Machine order: **compute-node
first as the canary**, complete verification, then pi-server — which requires the same read-only
automatic-update audit before its first maintenance run. The mechanisms are complementary, not disjoint: the
manual window considers all configured sources and may also apply a pending security update. Runbook:
`docs/patching-cadence.md`.
