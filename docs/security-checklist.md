# Security Checklist

This checklist separates controls that are verified today from controls that
must be completed before the lab hosts additional services. It applies to both
`compute-node` and `pi-server` and to every public artifact in this repository.

> Current facts live in [`../STATUS.md`](../STATUS.md). Security decisions and
> the SSH configuration-precedence lesson live in
> [`../DECISIONS.md`](../DECISIONS.md).

## Verified controls

- [x] SSH key authentication works from the Chromebook to both servers.
- [x] Password-based SSH is disabled on both servers.
- [x] The running daemon configuration was checked with `sshd -T`.
- [x] An independent password-only client test was rejected.
- [x] Conflicting cloud-init and legacy SSH fragments were removed.
- [x] Tailscale provides private remote access without public port forwarding.
- [x] Tailscale starts after reboot; unattended recovery was verified on
  `compute-node`.
- [x] The public repository excludes secrets, private keys, operational
  addresses, and local data through documented rules and `.gitignore`.
- [x] No patient data, employer-confidential material, or proprietary clinical
  content is permitted on the lab.

Verified does not mean permanent. Re-run the relevant checks after SSH, network,
package, or operating-system changes.

## Public repository gate

Before every commit or pull request, confirm the change contains none of the
following:

- Passwords, private keys, API keys, tokens, recovery codes, or `.env` files
- Real DHCP, public, or Tailscale addresses
- MAC addresses, device serials, Wi-Fi names, router details, or account IDs
- Unsanitized terminal output, logs, exports, or screenshots
- Patient data, real case identifiers, accession numbers, or MRNs
- Employer-confidential material, internal procedures, or clinical-system
  screenshots

Use placeholders, synthetic examples, public datasets, generalized diagrams,
and sanitized evidence.

## SSH verification after a change

Keep an existing session open until a fresh key-based login succeeds.

```bash
sudo sshd -t
sudo sshd -T | grep -E 'passwordauthentication|pubkeyauthentication'
```

Expected security-relevant output:

```text
passwordauthentication no
pubkeyauthentication yes
```

From another client, verify that password-only authentication is rejected:

```bash
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no <user>@<private-host>
```

Do not publish the private host or verbose connection output.

## System maintenance

Routine package review:

```bash
sudo apt update
apt list --upgradable
```

Apply approved updates deliberately, inspect service impact, and reboot when a
kernel or other relevant update requires it. Record the patching cadence and
last verified run in a future maintenance runbook; do not claim a cadence until
it is actually followed.

## Firewall and service exposure

No application service topology is deployed yet, so a final firewall policy is
not claimed. Before the first Dockerized service:

- Inventory listening ports with a local command such as `ss -lntup`.
- Decide which devices need each service.
- Bind services to the narrowest appropriate interface.
- Prefer Tailscale or local-only access over public exposure.
- Document UFW or other host-firewall rules and verify them independently.
- Add public exposure only through a separately reviewed threat model and
  decision record.

## Docker gate

Before accepting a Compose file:

- Use reputable images and pin versions deliberately.
- Avoid root containers when the image supports a non-root user.
- Keep secrets outside Compose and Git.
- Define volumes, networks, health checks, and restart behavior.
- Review every published port.
- Document start, stop, update, rollback, backup, and removal procedures.
- Validate the file in a disposable environment before relying on it.

## Backup and recovery gate

The hardware roles are chosen, but an automated backup and tested restore are
not yet verified. Before valuable data is stored:

- Define source, destination, schedule, retention, exclusions, and encryption.
- Keep at least one copy outside the failure domain of the working machine.
- Protect credentials separately from public documentation.
- Run and document a restore test.
- Treat a backup as incomplete until the restored data is verified.

See [`backup-plan.md`](backup-plan.md).

## Remaining security work

- [ ] Establish and record a repeatable patching cadence for both servers.
- [ ] Inventory listening ports before the first service deployment.
- [ ] Define and verify host-firewall rules for the actual service topology.
- [ ] Implement a backup job and complete a restore test.
- [ ] Decide whether genuinely sensitive operational notes need a private
  repository or other private store.
