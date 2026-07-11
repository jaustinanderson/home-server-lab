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
| **compute-node** | GMKtec M8, Ryzen 5 PRO 6650H, 16 GB RAM, 1 TB NVMe | Working storage, data services, and future AI compute |
| **pi-server** | Raspberry Pi 5, 8 GB RAM, 2 TB external SSD | Bulk archive, intended backup target, and lightweight services |
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

- Improve `.local` name resolution inside the Chromebook Linux environment
- Clone this repository onto the lab machines
- Configure authenticated Git push workflows
- Select and deploy the first Dockerized service
- Decide where PostgreSQL should run
- Create the first dataset-provenance schema

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

The Chromebook Linux environment does not yet resolve `.local` names consistently. Tailnet addresses provide a working fallback until Avahi/mDNS support is improved inside the Linux container.

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
