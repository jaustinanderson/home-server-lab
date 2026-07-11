# Docker Compose Files

This folder will store public-safe Docker Compose examples and service deployment notes for the home-server lab.

Docker Compose files make it easier to define, start, stop, and reproduce self-hosted services.

## Purpose

This folder is intended for:

* Example Docker Compose files
* Public-safe service templates
* Notes about containerized services
* Future home-server service deployments
* Reproducible infrastructure documentation

## Planned Services

Possible future services include:

* Portainer
* Uptime Kuma
* Pi-hole or AdGuard Home
* Syncthing
* Homepage dashboard
* PostgreSQL
* SQLite practice projects
* Documentation/wiki tools

## Security Rules

Do not commit:

* `.env` files
* Passwords
* API keys
* Tokens
* Private service URLs
* Personal network details
* Public IP addresses
* Patient data
* Employer-confidential data

Use placeholders instead:

```text
PASSWORD=<your-password-here>
API_KEY=<your-api-key-here>
SERVICE_URL=<your-service-url-here>
```

## Future Files

Planned examples:

```text
example.compose.yml
uptime-kuma.compose.yml
portainer.compose.yml
tailscale-notes.md
```

## Notes

Actual service configuration will be added gradually as the home server build progresses.

Tailscale already runs at the host level on both servers. Do not duplicate or
replace that verified access layer with a container unless a later decision
record identifies a concrete need and migration plan.
