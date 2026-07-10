# Security Policy

## Project Scope

Home Server Lab is a public portfolio repository documenting sanitized infrastructure patterns, scripts, decisions, and runbooks. The live systems contain private operational details that do not belong in this repository.

Never commit credentials, private keys, API tokens, recovery codes, real operational IP addresses, MAC addresses, Tailscale addresses, router or Wi-Fi details, patient data, employer-confidential information, or proprietary clinical-system material.

## Supported Version

Security and safety fixes are applied to the current `main` branch. Historical branches and old commits are not maintained as separate supported releases.

## Reporting a Vulnerability

Do not publish sensitive exploit details, credentials, addresses, or private infrastructure information in a public issue.

Use GitHub's private vulnerability-reporting or Security Advisory feature when available. Otherwise, contact the repository owner through the GitHub profile and establish a private reporting channel before sharing sensitive details.

A useful report includes:

- The affected script, Compose file, workflow, or document
- Reproduction steps using placeholders or a disposable environment
- Expected and observed behavior
- Potential impact
- A proposed mitigation, when known

## Secret or Data Exposure

If a credential or sensitive infrastructure detail is accidentally committed:

1. Treat it as compromised.
2. Revoke or rotate it immediately.
3. Remove it from the active branch.
4. Assess whether Git history must be rewritten.
5. Check forks, workflow logs, artifacts, screenshots, and deployment logs.
6. Document the response without reproducing the secret.

Deleting a file in a later commit does not remove it from Git history.

## Infrastructure Boundary

Repository examples are documentation and learning artifacts. They are not a guarantee that a live host is securely configured. Security-sensitive changes must be validated on the running system using independent checks, while keeping operational details out of the public repository.
