## Summary

Describe the focused infrastructure or documentation change and why it is needed.

## Areas Changed

- [ ] `STATUS.md` / current state
- [ ] Architectural decision record
- [ ] Shell script
- [ ] Docker or service configuration
- [ ] Network or remote-access documentation
- [ ] Backup or recovery documentation
- [ ] Documentation only

## Verification

- [ ] ShellCheck passed for affected shell scripts
- [ ] Change tested on the intended host or in a disposable environment
- [ ] Expected state independently verified
- [ ] Rollback or recovery steps documented when applicable
- [ ] `STATUS.md` changelog updated when current state changed
- [ ] `DECISIONS.md` updated when architecture or policy changed

## Public-Safety Review

- [ ] No passwords, private keys, tokens, or recovery codes are included
- [ ] No real IP, Tailscale, MAC, router, Wi-Fi, or device identifiers are included
- [ ] Command output and screenshots are sanitized
- [ ] No patient data or employer-confidential material is included

## Operational Effect

Describe any effect on compute-node, pi-server, Chromebook access, running services, storage, backups, or recovery.

## Deferred Work or Known Limitations

List anything intentionally left out of this pull request.
