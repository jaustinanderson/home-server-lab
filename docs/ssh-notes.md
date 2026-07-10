# SSH Notes

This document describes the verified SSH access model for the Home Server Lab without exposing credentials, private keys, operational addresses, or other sensitive configuration.

> Current project state lives in [`../STATUS.md`](../STATUS.md). SSH hardening decisions and configuration-precedence lessons are recorded in [`../DECISIONS.md`](../DECISIONS.md).

## Current State

SSH key authentication is configured and working from the Chromebook to both lab servers:

- **compute-node** — Ubuntu Server 26.04
- **pi-server** — Ubuntu Server 26.04

Password authentication is disabled on both machines and was independently verified from an external client. Tailscale provides private remote connectivity without public port forwarding.

## Administration Device

The Acer Chromebook Plus 514 is the control surface. SSH commands are run from its Linux terminal environment.

The Chromebook holds the private Ed25519 key. Only the corresponding public key is installed in each server account's `authorized_keys` file.

Never copy the private key into this repository, a chat, a screenshot, or another device without an explicit secure key-management plan.

## Preferred Connection Model

Use a host alias defined in the Chromebook's SSH configuration rather than repeatedly typing usernames, hostnames, or addresses.

Example public-safe configuration:

```sshconfig
Host compute-node
    HostName <private-host-or-tailnet-address>
    User austin
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes

Host pi-server
    HostName <private-host-or-tailnet-address>
    User ubuntu
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

`IdentitiesOnly yes` restricts authentication to the configured identity instead of offering every key loaded into `ssh-agent`.

Connect with:

```bash
ssh compute-node
ssh pi-server
```

Do not commit real operational addresses to this public repository.

## Local Hostnames

The two servers can resolve their `.local` mDNS names between each other:

```text
compute-node.local
pi-server.local
```

The Chromebook Linux environment does not yet resolve `.local` names consistently. Tailscale addressing remains the verified working fallback until mDNS support is improved inside the Linux container.

## Tailscale Remote Access

Tailscale is installed on:

- compute-node
- pi-server
- Chromebook

The verified model is:

- Private mesh-VPN connectivity
- No router port forwarding
- No direct public SSH exposure
- Stable per-device tailnet addressing
- Tailscale starts automatically after reboot

Inspect local status with:

```bash
tailscale status
```

Do not publish the returned addresses or device identifiers without sanitizing them.

## Verification Procedure

### Confirm the running SSH daemon configuration

```bash
sudo sshd -T | grep -E 'passwordauthentication|pubkeyauthentication'
```

Expected security-relevant output includes:

```text
passwordauthentication no
pubkeyauthentication yes
```

### Independently test that password-only login is rejected

From another client, force password authentication and disable public-key authentication:

```bash
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no <user>@<private-host>
```

Expected result:

```text
Permission denied (publickey)
```

This external test is important because inspecting a configuration file alone does not prove which settings the running SSH daemon actually applied.

## Configuration-Precedence Lesson

Both servers contained configuration fragments that could override or preempt the intended hardening behavior:

- A leftover password-login fragment on the Pi server
- A cloud-init SSH fragment on the compute node

OpenSSH configuration processing can produce unexpected results when multiple files define the same directive. The final state must therefore be checked with `sshd -T` and a live client test after any SSH configuration change.

Before restarting SSH after a change, validate syntax:

```bash
sudo sshd -t
```

Then restart the service using the command appropriate to the distribution:

```bash
sudo systemctl restart ssh
```

Keep an existing verified session open until a new key-based login succeeds. This reduces the risk of locking yourself out.

## Useful Commands

Show the current user:

```bash
whoami
```

Show the hostname:

```bash
hostname
```

Show concise network interfaces:

```bash
ip -br addr
```

Inspect SSH service state:

```bash
systemctl status ssh --no-pager
```

Inspect recent SSH logs:

```bash
journalctl -u ssh --since today
```

Check authorized-key permissions:

```bash
ls -ld ~/.ssh
ls -l ~/.ssh/authorized_keys
```

Typical secure permissions are:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

Update packages:

```bash
sudo apt update
sudo apt upgrade
```

Reboot safely:

```bash
sudo reboot
```

Shut down safely:

```bash
sudo shutdown now
```

## Troubleshooting

### `Permission denied (publickey)` during normal login

Check:

- The intended username
- The selected private key
- The server's `authorized_keys` entry
- Ownership and permissions on `~/.ssh`
- Whether `IdentitiesOnly yes` points to the correct key
- Verbose client output with `ssh -vvv <host-alias>`

### Host alias does not work

Check the SSH configuration file:

```bash
cat ~/.ssh/config
```

Then inspect the resolved client configuration:

```bash
ssh -G compute-node
```

### `.local` hostname does not resolve

Use the verified Tailscale connection temporarily. Then check whether Avahi/mDNS packages and services are available in the Chromebook Linux environment.

### Connection stops working after hardening

Use a still-open session or local console to:

- Run `sudo sshd -t`
- Run `sudo sshd -T`
- Inspect `/etc/ssh/sshd_config` and `/etc/ssh/sshd_config.d/`
- Review `journalctl -u ssh`
- Remove or correct conflicting fragments

## Public-Safety Rules

Never commit or publish:

- Private SSH keys
- Passwords or recovery codes
- Real operational IP or Tailscale addresses
- MAC addresses
- Full unsanitized SSH configuration containing sensitive hosts
- Screenshots containing addresses, usernames, fingerprints, or tokens

Public keys are not secret in the same way private keys are, but they should still be shared intentionally rather than copied into public documentation without a reason.
