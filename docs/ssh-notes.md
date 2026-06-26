# SSH Notes

This file documents SSH access for the Raspberry Pi home-server lab.

The goal is to keep a clear, repeatable record of how the server is accessed and administered without exposing private keys, passwords, personal network details, or sensitive configuration.

## Purpose

SSH allows remote command-line access to the Raspberry Pi from another device, such as a Chromebook or laptop.

For this project, SSH is used to:

* Administer the Raspberry Pi remotely
* Run Linux commands
* Install packages
* Configure services
* Manage Docker containers
* Troubleshoot the server
* Practice secure infrastructure workflows

## Current SSH Goal

The preferred SSH workflow is hostname-based access instead of relying on a changing local IP address.

Preferred command:

```bash
ssh ubuntu@pi-server.local
```

Fallback example using a sanitized local IP placeholder:

```bash
ssh ubuntu@192.168.x.x
```

Do not commit real public IP addresses, passwords, private keys, or sensitive network details.

## Username

Current or expected SSH username:

```text
ubuntu
```

This may change depending on the operating system image and user configuration.

## Hostname

Preferred hostname:

```text
pi-server.local
```

Using a hostname is easier than remembering a local IP address and may reduce problems caused by DHCP address changes.

## Chromebook SSH Notes

The Chromebook can be used as the primary admin machine for the Raspberry Pi.

Saved SSH connection goal:

```bash
ssh ubuntu@pi-server.local
```

If hostname resolution does not work, use the current local IP address temporarily and troubleshoot local DNS/mDNS.

## Password vs SSH Key Authentication

Early setup may use password authentication.

Long-term goal:

* Generate an SSH key on the admin machine
* Add the public key to the Raspberry Pi
* Test key-based login
* Disable password login only after key login is confirmed working

## Public-Safe SSH Key Rule

Never commit:

* Private SSH keys
* Passwords
* Token files
* `.env` files
* Personal network secrets

Public keys are generally safer than private keys, but they should still be shared intentionally and only when necessary.

## Common Commands

Connect to the server:

```bash
ssh ubuntu@pi-server.local
```

Check the current hostname:

```bash
hostname
```

Check the current user:

```bash
whoami
```

Check IP addresses on the server:

```bash
ip addr
```

Update package lists:

```bash
sudo apt update
```

Upgrade installed packages:

```bash
sudo apt upgrade
```

Reboot the server:

```bash
sudo reboot
```

Shut down the server safely:

```bash
sudo shutdown now
```

## Troubleshooting

### Hostname does not resolve

If this fails:

```bash
ssh ubuntu@pi-server.local
```

Try:

* Confirm the Raspberry Pi is powered on
* Confirm both devices are on the same local network
* Confirm the hostname is set correctly
* Try connecting with the current local IP address
* Check whether mDNS/Avahi is installed and running

### Local IP address changes

Potential solutions:

* Use hostname-based access with `.local`
* Configure a DHCP reservation in the router if available
* Use Tailscale later for stable private access
* Document limitations if using a managed apartment network

### Permission denied

Possible causes:

* Wrong username
* Wrong password
* SSH key not installed correctly
* SSH service not running
* Password authentication disabled before key authentication was confirmed

## Next Improvements

* Confirm final hostname
* Confirm final SSH command
* Configure SSH key authentication
* Document SSH key setup
* Consider Tailscale for secure remote access
* Add SSH hardening checklist
