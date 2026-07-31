# Security Checklist

This checklist separates controls that are verified today from controls that
must be completed before the lab hosts additional services or metaphase data. It
applies to `compute-node`, `pi-server`, the Synology NAS, and every public
artifact in this repository.

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
- [x] Tailscale starts after reboot; recovery was verified on `compute-node`
  and after the deliberate `pi-server` maintenance reboot.
- [x] The public repository excludes secrets, private keys, operational
  addresses, and local data through documented rules and `.gitignore`.
- [x] Only synthetic data or legitimately public, appropriately licensed
  datasets are permitted; de-identification alone is insufficient (D1/D21).
- [x] Daily Synology Hyper Backup to Backblaze B2 is owner-confirmed operational
  for selected current personal NAS content.

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
kernel or other relevant update requires it. Follow
[`patching-cadence.md`](patching-cadence.md) and record each verified maintenance
run; do not infer current patch status from the documented cadence alone.

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

The hardware roles, healthy one-drive-fault-tolerant SHR pool, drive-health checks,
scrubbing, tested email alerts, and an off-site NAS backup are now implemented.
A tested restore and the metaphase-specific recovery scope are not yet verified.
Before metaphase data is stored:

- Define source, destination, schedule, retention, exclusions, and encryption.
- Keep at least one copy outside the failure domain of the working machine.
- Protect credentials separately from public documentation.
- Run and document a restore test.
- Treat a backup as incomplete until the restored data is verified.
- Do not treat the second SHR drive as a backup; it provides availability through
  one-drive fault tolerance but does not create another copy.

See [`backup-plan.md`](backup-plan.md).

## Remaining security work

- [x] Establish and record a repeatable patching cadence for both servers (D18).
- [x] Complete SHR conversion and verify both drives and the storage pool
  healthy, protected, and one-drive fault tolerant.
- [ ] Inventory listening ports before the first service deployment.
- [ ] Define and verify host-firewall rules for the actual service topology.
- [x] Implement an off-site backup job for current NAS personal content.
- [ ] Complete and document a disposable Backblaze restore test.
- [ ] Define, protect, and restore-test the future metaphase manifests,
  annotations, databases, and other irreplaceable project data.
- [ ] Implement and verify the planned local NAS-to-pi second copy.
- [ ] Decide whether genuinely sensitive operational notes need a private
  repository or other private store.
