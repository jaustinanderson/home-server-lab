# Network Notes

This document records the verified, public-safe network model for the two-machine
Home Server Lab. Operational addresses, device identifiers, Wi-Fi details, and
account credentials are intentionally omitted.

> [`../STATUS.md`](../STATUS.md) is the source of truth for current state.
> [`../DECISIONS.md`](../DECISIONS.md) records why the lab uses DHCP, mDNS, and
> Tailscale.

## Current topology

| Device | Local role | Verified access |
|---|---|---|
| **Chromebook** | SSH control surface | Reaches both servers through the private Tailscale mesh |
| **compute-node** | Working storage, data services, and future compute | Key-based SSH; local server-to-server connectivity; Tailscale |
| **pi-server** | Archive, planned backup target, and lightweight services | Key-based SSH; local server-to-server connectivity; Tailscale |

The apartment-managed network provides DHCP and device-to-device connectivity,
but no router administration, static DHCP reservations, or public port
forwarding. Nothing in the lab depends on opening an inbound internet port.

See the rendered topology in
[`../diagrams/home-lab-architecture.md`](../diagrams/home-lab-architecture.md).

## Addressing and name resolution

- **DHCP remains enabled.** Local addresses may change and are not committed.
- **mDNS/Avahi works between the two servers.** They can reach
  `compute-node.local` and `pi-server.local` from one another.
- **The Chromebook Linux container does not yet resolve `.local` names
  reliably.** This is a quality-of-life item, not a connectivity blocker.
- **Tailscale is the stable remote-access path.** Each device has a private
  tailnet address that can be discovered locally with `tailscale status`.

Do not copy real DHCP or tailnet addresses into this public repository.

## Preferred SSH model

Use the sanitized host aliases documented in
[`ssh-notes.md`](ssh-notes.md):

```bash
ssh compute-node
ssh pi-server
```

The aliases can point to private Tailscale addresses until Chromebook `.local`
resolution is reliable. SSH uses the configured Ed25519 key and
`IdentitiesOnly yes`; password authentication is disabled on both servers.

## Useful verification commands

Run locally and sanitize output before sharing:

```bash
ip -brief addr
hostnamectl
tailscale status
systemctl status tailscaled --no-pager
ping -c 4 compute-node.local
ping -c 4 pi-server.local
```

Use `ip -brief addr` and `tailscale status` for troubleshooting only. Their
output contains operational addresses and device information that should not be
published unchanged.

## Troubleshooting

### A `.local` hostname does not resolve from the Chromebook

Use the verified Tailscale-backed SSH alias. Then inspect mDNS support inside
the Chromebook Linux container. Installing or enabling Avahi there is the next
planned quality-of-life task; it is not required for secure remote access.

### A server-to-server `.local` hostname stops resolving

On the affected server:

```bash
systemctl status avahi-daemon --no-pager
getent hosts compute-node.local
getent hosts pi-server.local
```

Confirm both machines are reachable over the local network and fall back to
Tailscale while investigating.

### A previous local address no longer works

That is expected under DHCP. Discover the current address locally or use the
stable Tailscale path. Do not hard-code a changing local address into public
documentation or automation.

### Remote SSH fails

Check, in order:

1. Tailscale is connected on the Chromebook and target server.
2. The SSH alias resolves to the intended private host.
3. The configured username and identity file are correct.
4. The SSH service is active on the target.
5. `ssh -vvv <host-alias>` identifies where negotiation fails.

Do not weaken the verified key-only SSH configuration to work around a name or
route problem.

## Security boundary

- No public SSH exposure or router port forwarding
- No operational addresses, MAC addresses, Wi-Fi names, or device IDs in Git
- No screenshots copied without reviewing every visible field
- No patient, employer, or proprietary clinical-system data on the lab
- New public service exposure requires a separate threat model and decision
  record

## Next network work

1. Improve `.local` resolution inside the Chromebook Linux environment.
2. Document the standard Git/SSH authentication path for repository pushes.
3. Inventory ports and firewall rules before deploying the first service.
4. Update the architecture diagram when a service topology is actually
   verified.
