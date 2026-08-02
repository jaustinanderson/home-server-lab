# Setup Log

This file records the public-safe setup history for the Home Server Lab. It documents progress, troubleshooting, and verification without exposing credentials, private keys, network addresses, patient data, or employer-confidential information.

> For the canonical current state, read [`../STATUS.md`](../STATUS.md). Architectural choices and their rationale are recorded in [`../DECISIONS.md`](../DECISIONS.md).

## Project Context

The lab supports practical learning in:

- Linux administration
- SSH and secure remote access
- Docker and containerized services
- Data engineering and relational databases
- Backup and recovery planning
- Infrastructure-as-code
- Future clinical-AI and laboratory-informatics projects

## Current Hardware

| Machine | Hardware | Role |
|---|---|---|
| **compute-node** | GMKtec M8, Ryzen 5 PRO 6650H, 16 GB RAM, 1 TB NVMe | Hot working storage, data services, and future AI compute |
| **pi-server** | Raspberry Pi 5, 8 GB RAM, 2 TB external SSD | Planned local secondary protection and lightweight services |
| **Synology NAS** | DS925+, Btrfs on SHR, two matching 16 TB drives, one-drive fault tolerance | Canonical source archive and current personal-content store |
| **Chromebook** | Acer Chromebook Plus 514 | SSH administration through the Linux terminal |

Both servers run Ubuntu Server 26.04. Exact network identifiers are intentionally omitted.

## Network and Access Model

The lab operates on an apartment-managed network without router administration, static DHCP reservations, or public port forwarding.

The working access model is:

- SSH key authentication from the Chromebook
- Password-based SSH disabled on both servers
- Tailscale for private remote access and stable per-device addressing
- mDNS hostnames between servers where supported
- No services exposed directly to the public internet

## Verified Foundation

The following foundation work is complete:

- Operating systems installed and verified on both servers
- SSH keys created on the Chromebook and installed on both servers
- Passwordless SSH confirmed to both machines
- Password authentication disabled and independently tested
- Conflicting SSH configuration fragments removed
- Tailscale installed on the compute node, Pi server, and Chromebook
- Remote SSH verified through Tailscale
- Tailscale startup verified after a `compute-node` reboot
- Compute node reboot recovery verified without local intervention
- Canonical `STATUS.md` and `DECISIONS.md` established in GitHub

## Current Next Steps

- Create the metaphase archive boundary and least-privilege access model
- Complete the remaining NAS-readiness controls: provenance, checksums, approved backup scope,
  and a local second copy
- Run one bounded public metaphase pilot only after every readiness gate passes
- Continue to Docker only after the storage protection boundary is trustworthy

## Troubleshooting Lessons

### SSH configuration precedence

Two different configuration fragments had re-enabled password authentication despite a later hardening file. The final state was verified using both:

```bash
sudo sshd -T
```

and an external password-only login attempt that correctly failed with:

```text
Permission denied (publickey)
```

The lesson is that writing a hardening file is not enough; the running daemon configuration and an independent client test must both confirm the intended state.

### Managed-network constraints

Because the apartment network does not provide router administration, the design avoids relying on DHCP reservations or port forwarding. Tailscale provides stable private connectivity without exposing inbound services.

### Chromebook name resolution

Tailscale hostnames now resolve from the Chromebook Linux environment and are used through tested SSH
aliases. `.local` resolution remains optional and is not required for administration.

## Security Rules

Never commit:

- Passwords, API keys, tokens, recovery codes, or `.env` files
- SSH private keys
- Public or private operational IP addresses
- MAC addresses or device identifiers
- Router, Wi-Fi, or Tailscale secrets
- Patient data, MRNs, accession numbers, or clinical-system screenshots
- Employer-confidential information or internal procedures

## Build History

### 2026-06-24

- Created the public repository and initial documentation structure
- Established the Raspberry Pi server project foundation
- Added security, backup, SSH, network, roadmap, script, Docker, and diagram placeholders

### 2026-07-01

- Expanded the architecture to a two-server lab with a compute node and Pi server
- Confirmed Ubuntu Server 26.04 on both machines
- Installed SSH keys and verified passwordless access
- Removed conflicting SSH configuration fragments
- Verified password authentication was disabled on both servers
- Installed and verified Tailscale on all three devices
- Verified remote SSH and automatic Tailscale recovery after reboot
- Added `STATUS.md` as the canonical state document
- Added `DECISIONS.md` as the architectural decision log

### 2026-07-10

- Reconciled the README and setup documentation with the verified two-machine architecture
- Added a GitHub Actions ShellCheck workflow for repository shell scripts

### 2026-07-11

- Reconciled the remaining network, security, backup, script, and diagram documentation
- Added a public-safe diagram of the verified topology and planned backup flow
- Removed stale Pi-only and already-completed next steps
- Reduced sensitive detail in the default `system-info.sh` output

### 2026-07-19

- Completed a read-only storage/filesystem review on both Linux hosts
- Confirmed simple GPT/ext4 layouts, the Pi's separate boot filesystem, and no
  observed USB reset errors during the reviewed boot
- Recorded missing drive-health tooling and the need for a sanitized durable
  baseline

### 2026-07-27

- Incorporated the DS925+ into the canonical architecture as the source archive
- Recorded the current one-drive SHR pool as healthy but without drive-failure
  protection; second matching 16 TB drive expected 2026-07-28
- Recorded daily Hyper Backup to Backblaze B2 as owner-confirmed operational for
  selected personal NAS content, with restore verification still pending
- Added the Phase 3.5 NAS-readiness gate and exact pre-ingestion checklist

### 2026-07-29

- Installed the second matching 16 TB NAS drive and added it to the existing SHR
  pool
- Began DSM conversion/synchronization; protected status, two-drive health, and
  redundancy remain pending until completion and verification
- Clarified the readiness sequence: sections A–D authorize one bounded pilot,
  while passing the pilot in section E completes Phase 3.5

### 2026-07-31

- Completed refreshed Linux baselines, log inspection, controlled reboots, and tested SSH aliases on both hosts
- Corrected compute-node's boot wait-online timeout by retaining the disconnected secondary Ethernet port as optional
- Promoted pi-server's staged kernel through the protected `piboot-try` path and verified boot state `good`
- Verified the NAS as one healthy SHR pool with one-drive fault tolerance and approximately 13.8 TB usable capacity
- Confirmed both extended drive tests passed, tested DSM email notifications, completed the first data scrub,
  and scheduled quarterly scrubbing
- Marked Phase 3 complete and moved the immediate focus to Phase 3.5 recovery and data-governance controls
- Inspected the daily, client-side-encrypted, versioned Hyper Backup configuration and privately held recovery material
- Completed a disposable restore from Backblaze into an isolated destination and verified an identical SHA-256 checksum
- Corrected an initial destination-selection mistake without data loss, removed both disposable NAS folders,
  and recorded that exact copy duration was not measured

### 2026-08-01

- Created and verified the dedicated metaphase archive boundary with eight logical areas, a least-privilege routine workflow identity, protected canonical-content permissions, and isolation from personal home-directory storage.
- Verified `compute-node` on-demand SMB 3.1.1 access, least-privilege mount options, normal-reboot recovery, and local-NVMe processing with disposable synthetic placeholders only.
- Added the versioned promotion-manifest schema, fail-closed standard-library validator, synthetic rejection/acceptance fixtures, and CI coverage for provenance, license, classification, path safety, SHA-256 integrity, and transformation history.
- Kept corpus acquisition blocked pending the local `pi-server` second copy, metaphase-specific recovery design, and one bounded public/synthetic pilot.
