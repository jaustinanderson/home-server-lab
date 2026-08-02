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

**D19 — The Synology DS925+ is the canonical source archive; compute-node is the working tier and pi-server is secondary protection.** *(2026-07-27)*
This supersedes the storage-role portion of D2. The NAS holds canonical raw source material and approved
releases; `compute-node` receives working copies for transformation and AI work; `pi-server` remains a
planned local second-copy/lightweight-service tier rather than the primary archive. GitHub holds sanitized
catalogs, scripts, decisions, and documentation only. A future dedicated metaphase server may read approved
NAS releases read-only. The current one-drive SHR pool has no drive-failure protection; the expected second
16 TB drive must be added to the existing pool, finish synchronization, and pass health verification before
redundancy is claimed. SHR redundancy is availability protection, not a backup. This decision preserves D1:
only public, synthetic, or explicitly approved de-identified study data may enter the lab.

**D20 — Backblaze B2 is the approved paid off-site-backup exception.** *(2026-07-27)*
This supersedes D3 only for the off-site backup service and implements the off-site direction anticipated by
D11. Synology Hyper Backup now sends the NAS's current personal content to Backblaze B2 on a daily schedule
with version retention. Credentials, bucket identifiers, private paths, and recovery material remain outside
this public repository. Operational backup status does not prove recoverability: the design remains
incomplete until a disposable restore is completed, verified, and documented. Encryption status is not
claimed until separately inspected.

**D21 — D1 remains controlling: only public or synthetic data may enter the lab.** *(2026-07-29)*
This corrects and supersedes only D19's phrase allowing "explicitly approved de-identified study data," which
was inconsistent with D1 and is not an authorization. De-identification alone does not move real
patient-derived, institutional, employer, restricted, or uncertain-origin material across the lab boundary.
Any non-synthetic source must already be a legitimately public, appropriately licensed dataset. A future
proposal to expand that rule requires a new explicit decision after applicable legal, institutional, privacy,
security, and data-use review; until then, public datasets and synthetic/fake data are the complete allowed set.

**D22 — Promotion from quarantine to the canonical archive requires passing an automated, fail-closed,
standard-library manifest validator; a passing result never authorizes disallowed material.** *(2026-08-01)*
Section C of the NAS readiness checklist named the required provenance/license/checksum controls, but no
automated enforcement existed. This decision establishes `docs/promotion-manifest.schema.json` (a versioned
JSON Schema draft 2020-12 manifest contract) and `scripts/validate-promotion-manifest.py` (a dependency-free
Python standard-library validator) as the required technical gate ahead of any promotion: every governed file
must carry a verified SHA-256 checksum computed from its actual bytes; every source must be classified as
`synthetic` or `public_licensed`, never merely de-identified (D1/D21); license review, origin review, and
identifier-safety review must each be explicitly approved/safe, not merely present; every disallowed-content
flag (patient-derived, institutional, employer-confidential, clinical-study, restricted-other) must be false;
referenced paths must be safe relative paths that cannot escape the supplied validation root; source locators,
calendar dates, transformation timestamps, and transformation-step sequences must be valid; unknown root or
nested contract fields must be rejected; a declared derivative must carry transformation history; and
`eligibility_state` must be exactly `eligible_for_promotion` — `pending_review`, `quarantine`, and
`rejected` always fail closed. A self-declared eligible state never overrides another failure. The validator
is read-only, is deterministic, exits nonzero for every rejection, and never rewrites a manifest or
moves/promotes material. Schema, validator, documentation, and tests must remain aligned; every accepted and
rejected workflow state and every claimed strictness boundary requires positive or negative test coverage
before the gate is described as fail-closed. This decision only formalizes the enforcement *mechanism* — it
does not loosen D1, D19, or D21's substantive data-boundary rules, and a passing validator result does not by
itself authorize the bounded pilot (section E) or any real dataset; see `docs/promotion-controls.md`
(issue #18).

**D23 — pi-server pulls an encrypted Restic repository from a read-only NAS SMB source for the local
second copy of irreplaceable project data; architecture selected, not yet implemented.** *(2026-08-02)*
This is the issue #19 local-second-copy design, following a read-only architecture and capacity preflight on
pi-server (no server or NAS configuration changed). The model: (1) `pi-server` initiates the backup pull —
the NAS never authenticates outward to the Pi and never holds Pi backup-repository credentials or access;
(2) the Synology NAS remains the canonical source; (3) a dedicated non-administrator NAS backup identity
receives read-only access limited to the explicitly approved project scope defined below, exposed to the
backup process as a read-only SMB mount; (4) NAS credentials for that identity stay root-only on
`pi-server`, live outside Git, and are never printed in logs, commits, or documentation; (5) a dedicated
non-login local backup identity runs the job on `pi-server`; (6) **Restic** is the selected snapshot tool
because it provides repository encryption, deduplication, integrity checking, and versioned recovery
points from a single small repository, without the operational overhead Borg's segmented-repository model
would add here; (7) the Restic repository itself is inaccessible to ordinary interactive users on
`pi-server`; (8) the initial proof uses synthetic data only; (9) no automatic `forget`/`prune`/deletion runs
during the proof; (10) general metaphase ingestion and issue #15's pilot remain unauthorized regardless of
this decision.

**Why pull, not push:** a NAS-initiated push would require the independent backup target (`pi-server`) to
accept inbound connections or hold credentials trusted by the NAS, expanding the blast radius of a NAS
compromise to the very system meant to survive it. A pull model keeps that trust one-directional.

**Why not a plain rsync mirror:** a mirror reproduces the source state exactly, including accidental
deletion or corruption, and provides no independent versioned recovery point once the mirror has already
propagated the mistake. Restic's snapshot model preserves prior states independently of what the source
currently contains.

**Why Restic over Borg:** both are credible dedicated backup tools with encryption and deduplication. Borg
is technically viable but its repository-locking and archive model is built for larger, more actively
multi-client repositories; Restic is the simpler fit for this small, single-client, encrypted,
snapshot-oriented local repository, with less operational surface to configure correctly.

**Why not simply re-download bulk data as the backup target:** re-downloadable public bulk datasets are
explicitly excluded from this protection (see scope below) — backing them up would consume the limited
repository ceiling without protecting the material that cannot be regenerated from a public source.

**Encryption caveat — do not overstate:** Restic provides repository-level encryption, and root-only
credential storage limits access from ordinary interactive accounts. However, `pi-server`'s SSD is not
LUKS-encrypted (D13); an automatic unlock secret stored on that same unencrypted disk does not fully protect
the repository against an attacker who physically extracts the drive, since the key and the encrypted data
would travel together. LUKS, TPM-backed credential handling, or an off-device/manual unlock model remain
future hardening options if the threat model requires them. Restic alone does not eliminate the physical-
theft risk, and no document should claim otherwise.

**Protected scope (initial):** provenance and promotion manifests; license-review records; curated
annotations and metadata; database-consistent dumps once databases exist; and other irreplaceable
experiment records or configuration not adequately protected by GitHub. Explicitly excluded: re-downloadable
public bulk datasets; quarantine contents; caches and temporary files; rebuildable working derivatives;
routine exports and logs without a documented recovery requirement; Git-tracked public documentation already
protected by GitHub; secrets and credentials; personal NAS content (already covered by D20's Hyper Backup
job); and patient, employer, institutional, restricted, or uncertain-origin material (prohibited on the lab
entirely under D1/D21, backup policy notwithstanding). The exact private NAS source path and its measured
size are implementation-time operational inputs and are deliberately not published here.

**Capacity and retention policy:** repository ceiling 256 GiB (~14% of `pi-server`'s filesystem); warning
threshold 192 GiB; minimum free-space reserve 512 GiB. The backup must refuse to start or continue if the
256 GiB ceiling would be exceeded or available filesystem capacity falls below the 512 GiB reserve. Proposed
schedule: daily near 03:30 UTC (outside the identified 06:00–07:00 UTC maintenance window), optionally with
a small randomized delay. Target retention after the proof phase: 7 daily, 4 weekly, 6 monthly snapshots.
Automatic `forget`/`prune` stays disabled until all of the following hold: the synthetic restore succeeds;
checksum equality is proven; source immutability (the NAS backup identity cannot alter the source) is
proven; monitoring and stale-state detection work; several consecutive scheduled backups succeed; and Austin
explicitly approves enabling pruning.

**Planned monitoring design:** a hardened oneshot systemd backup service, a daily timer near 03:30 UTC, a
success timestamp updated only after the snapshot and required verification complete successfully, a
separate stale-state checker with a 36-hour stale threshold, nonzero exit status on backup, capacity,
integrity, mount, or stale-state failure, and visibility through systemd until Phase 5 monitoring exists.
Testing this design uses a disposable synthetic method for exercising both failure and stale-state behavior
— never real repository corruption or manipulation of the canonical NAS source.

This decision selects and records the architecture only. No NAS or `pi-server` account, package, mount,
credential, service, timer, or snapshot has been created. See `docs/backup-plan.md`,
`docs/backup-restore-test.md`, and `docs/nas-readiness-checklist.md` (issue #19).
