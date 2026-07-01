# Project Status — Home Lab (compute-node + pi-server)

> **Single source of truth.** Anyone working on this project — Austin, Claude, or ChatGPT —
> reads and edits **this file**. Do **not** regenerate it from scratch; edit it in place and
> add a dated line to the Changelog at the bottom. Keep it to ~one page.
>
> **This file is public-safe** (it lives in a public GitHub repo). No real IPs, MACs, passwords,
> patient data, or employer-internal details. Current DHCP addresses are derivable on each box
> with `ip -br a`.

**Last updated:** 2026-07-01

---

## Who & what this is
Austin (Jerad "Austin" Anderson), CG(ASCP) Cytogenetic Technologist, building a home lab toward
clinical-lab AI. Two long-term tracks:

- **Track A** — containerized data lake + AI pipeline for cytogenetic images (metaphases/karyograms).
- **Track B** — lab-workflow automation tool (Epic/Excel exports → replace a manual point system),
  built on synthetic data, GPU-free. The easier first win.

## Non-negotiable constraints
- **No real patient data / PHI on this lab. Ever.** Public datasets + synthetic/fake data only.
  Real clinical data stays on sanctioned institutional infrastructure.
- **Free & open-source** stack only.
- **One phase at a time.** Austin is learning as he goes — explain the *why*, not just the commands.
  Austin executes and reports back (often via photos of terminal output).
- **Infrastructure-as-code from day one.** Configs + a runbook live in git.
- **Public repo + LinkedIn are sanitized derivatives of the truth** — scrub IPs, MACs, anything internal.

## Machines
| Name | Hardware | Role | OS | User |
|---|---|---|---|---|
| **compute-node** | GMKtec M8 — Ryzen 5 PRO 6650H, 16GB, 1TB NVMe, dual 2.5GbE, Oculink | Hot/working store + AI compute | Ubuntu Server 26.04 | `austin` |
| **pi-server** | Raspberry Pi 5 8GB + 2TB SanDisk Extreme SSD (USB; OS+data) | Bulk archive + backup (cold) | Ubuntu Server 26.04 | `ubuntu` |
| **Chromebook** | Acer Chromebook Plus 514 | Control surface (SSH only, via Penguin terminal) | ChromeOS | `jeradaustinanderson` |

## Network
- Apartment-managed network, `/16`, DHCP (no router admin, no static leases, no port forwarding).
- The two servers reach each other directly (~0.3 ms, 0% loss). A direct Cat6 link is an optional
  future upgrade — not needed.
- **mDNS/Avahi**: `pi-server.local` and `compute-node.local` resolve between the two servers.
- The Chromebook's Penguin container can't resolve `.local` yet (uses raw DHCP IPs for now) — fix pending.

## Done ✅
- Ubuntu Server 26.04 installed + verified on both machines (no LVM, no LUKS — kept simple).
- compute-node: clean headless NVMe boot confirmed (reboot test passed).
- SSH key pair created on the Chromebook (ed25519), installed on both servers — passwordless login works to both.
- **SSH hardened AND independently verified on BOTH machines** (password auth off, keys only).
  Verified via `sudo sshd -T` (running service reports `passwordauthentication no`) **and** an external
  password-only login test that is correctly refused with `Permission denied (publickey)`.
  - pi-server: removed a leftover `00-enable-password-login.conf` so `99-hardening.conf` takes effect.
  - compute-node: removed `50-cloud-init.conf`, which had silently been re-enabling password auth
    (it sorts before `99-hardening.conf` and SSH honors the first match). See DECISIONS D14.
- Chat-exposed password rotated (`passwd`).

## In progress 🔧
- **Seed the repo** — commit `STATUS.md` + `DECISIONS.md` to `home-server-lab` as the shared source of
  truth (done via github.com web upload; no push auth needed yet). *(Immediate next action.)*

## Next up (rough order)
1. Fix `.local` resolution inside Chromebook Penguin (`sudo apt install avahi-daemon avahi-utils`).
2. **Tailscale** on both servers + Chromebook → remote access from anywhere; also retires the IP/`.local`
   headaches. (No port-forwarding needed.)
3. Clone the `home-server-lab` repo onto the machine(s); set up GitHub push auth
   (Personal Access Token or a GitHub SSH key — not done yet).
4. **Reconcile docs:** the older `home-server-lab` docs are **Pi-only** and treat SSH keys as a future
   "plan" — update to reflect the real two-machine setup + completed key auth/hardening.
5. PostgreSQL + dataset **provenance-manifest** schema.
6. Ingest one public cytogenetics dataset end-to-end.
7. Branch into Track A and Track B.

## Open items / maintenance
- **compute-node shows `*** System restart required ***`** — a pending kernel/firmware update. Reboot it
  soon (not urgent; won't affect SSH). Fold into a "keep both boxes updated" routine.
- Where does PostgreSQL live — compute-node (compute proximity) or pi-server (next to the 2TB data)?
  Decide when we get there.
- Keep everything in one public repo (sanitized), or add a private repo for genuinely sensitive
  operational detail later?

## Changelog
*(Append new lines at the bottom. Format: `YYYY-MM-DD — who — what`.)*
- *(prior, June 2026)* — pi-server initial build in an earlier session: Ubuntu 26.04 on the 2TB SSD,
  SSH enabled, Avahi, reachable as `pi-server.local`.
- **2026-06-24 — Austin + Claude** — Foundation build: Ubuntu 26.04 on both boxes; mutual reachability
  confirmed; Avahi on compute-node; SSH keys deployed to both; compute-node reboot-tested; password
  rotated. (A hardening file was written on compute-node but later found ineffective — see 2026-07-01.)
- **2026-07-01 — Austin + Claude** — Created STATUS.md + DECISIONS.md. Hardened + verified **pi-server**
  (removed leftover `00-enable-password-login.conf`). Discovered **compute-node**'s `50-cloud-init.conf`
  was silently re-enabling password auth; removed it. Verified **both** machines refuse password logins
  via live external test. Foundation complete + verified. (Lesson recorded as DECISIONS D14.)
