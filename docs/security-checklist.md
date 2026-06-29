# Security Checklist

This checklist documents security practices for the Raspberry Pi home-server lab.

The goal is to build good security habits while keeping this public repository safe for professional portfolio use.

## Public Repository Rules

Do not commit:

* Passwords
* Private SSH keys
* API keys
* Authentication tokens
* `.env` files
* Router credentials
* Wi-Fi passwords
* Public IP addresses
* Full MAC addresses
* Personal network diagrams with identifying details
* Screenshots showing private system details
* Patient data
* Employer-confidential data
* LIS, Epic, or clinical system screenshots
* Real accession numbers, MRNs, case IDs, or sample identifiers

## SSH Security

Planned SSH security practices:

* Use SSH key authentication when ready
* Store private keys only on trusted devices
* Never upload private keys to GitHub
* Confirm key-based login works before disabling password login
* Use strong passwords during early setup
* Avoid exposing SSH directly to the public internet
* Consider Tailscale for private remote access

## System Updates

Routine maintenance:

```bash
sudo apt update
sudo apt upgrade
```

Optional cleanup:

```bash
sudo apt autoremove
```

Reboot when needed:

```bash
sudo reboot
```

## User Accounts

Security goals:

* Use a non-root user for normal administration
* Use `sudo` only when needed
* Avoid shared accounts when possible
* Use strong passwords
* Remove unused accounts
* Document account roles without exposing credentials

## Firewall

Future firewall goals:

* Identify which services need network access
* Block unnecessary inbound traffic
* Avoid public port forwarding unless there is a clear reason
* Prefer private network tools for remote access
* Document open ports in a public-safe way

Potential tool:

```bash
sudo ufw status
```

## Docker Security

Docker security goals:

* Use official or reputable images when possible
* Pin image versions when stability matters
* Avoid running containers as root when possible
* Avoid storing secrets directly in `docker-compose.yml`
* Keep `.env` files out of GitHub
* Use `.gitignore` for local secrets
* Review exposed ports before starting services
* Keep containers updated intentionally

## Secrets Management

Never store secrets directly in public files.

Unsafe examples:

```text
PASSWORD=my-password
API_KEY=abc123
TOKEN=secret-token
```

Safer public documentation:

```text
PASSWORD=<your-password-here>
API_KEY=<your-api-key-here>
TOKEN=<your-token-here>
```

## Data Privacy

This project must remain public-safe.

Do not use:

* Real patient data
* Employer data
* Clinical screenshots
* Internal SOPs
* Real case identifiers
* Real lab accession numbers
* Any data that could identify a patient, coworker, employer system, or institution

Use instead:

* Synthetic examples
* Public datasets
* Mock data
* Sanitized placeholders
* General workflow diagrams

## Backup Security

Backup goals:

* Keep at least one backup separate from the main server
* Avoid storing unencrypted sensitive data
* Test restore procedures
* Document backup strategy without exposing private paths or credentials
* Keep credentials separate from backup documentation

## Remote Access

Preferred remote access strategy:

* Avoid exposing services directly to the public internet
* Avoid router port forwarding unless absolutely necessary
* Prefer private access tools such as Tailscale
* Use strong authentication
* Document remote access decisions carefully

## GitHub Safety

Before committing, check for:

* Secrets
* Personal data
* Internal network details
* Private screenshots
* Employer or patient information
* Accidentally included config files
* Terminal output containing sensitive paths or keys

Useful habit:

```bash
git status
```

Review file contents before committing.

## Future Improvements

* Add `.gitignore`
* Add SSH key setup notes
* Add firewall notes
* Add Docker security notes
* Add backup plan
* Add service inventory
* Add update schedule
