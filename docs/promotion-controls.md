# Promotion Controls

This is the control/runbook document for **section C** of
[`nas-readiness-checklist.md`](nas-readiness-checklist.md): the automated,
public-safe, reproducible, fail-closed controls that must pass before material
is even considered for promotion from the metaphase archive's quarantine area
into the canonical archive (see [`metaphase-archive-boundary.md`](metaphase-archive-boundary.md),
issue #17, for the archive structure these controls sit in front of). Tracks
issue #18.

- **Exercise date:** 2026-08-01
- **Scope tested:** the manifest schema, the validator's fail-closed control
  logic, and the synthetic fixture suite, run entirely on `compute-node`.
- **Dataset used:** none. Every manifest and file referenced anywhere in this
  document, the schema, the validator, and its tests is an obviously
  synthetic fixture using reserved/example identifiers (`example.com` URLs, a
  `10.1234/example.*` placeholder DOI). No real dataset was acquired,
  downloaded, ingested, promoted, copied, or modified. No NAS archive content
  was accessed or changed.

## What this control layer is, and is not

The validator answers exactly one question:

> **Does this manifest, and the fixture bytes it references, satisfy the
> automated pre-promotion controls?**

A passing (`ELIGIBLE`, exit code `0`) result means only that. It does not:

- Move, copy, promote, or ingest anything — the validator only reads bytes
  to compute a checksum.
- Authorize patient-derived, employer, institutional, clinical-study, or any
  other disallowed or uncertain-origin material. Those are rejected outright
  (see below) regardless of any other field.
- Authorize the bounded pilot in section E of `nas-readiness-checklist.md` by
  itself. Section D's remaining metaphase-specific protection and local
  second-copy requirements (issue #19) still block the pilot.
- Replace human license, origin, or content-safety review. The manifest
  records the outcome of that human review; the validator checks the record
  is complete, internally consistent, and matches the fixture bytes.
- Have any relationship to issue #18's own GitHub workflow. Editing or
  closing issue #18, and opening/merging the pull request for this change,
  are separate, later, human-controlled actions.

## Manifest structure

Manifests are JSON documents validated against
[`promotion-manifest.schema.json`](promotion-manifest.schema.json) (JSON
Schema draft 2020-12). Every field below is required unless noted.

| Field | Purpose |
|---|---|
| `schema_version` | Must be `"1.0.0"`. |
| `dataset_name`, `dataset_version`, `publisher` | Identify the source material. |
| `source_url` and/or `doi` | At least one required; where the material came from. |
| `acquisition_date` | `YYYY-MM-DD`, an unambiguous ISO 8601 calendar date. |
| `license` | The **dataset's own** license identifier. See below — this is never the repository's MIT license. |
| `license_review_state` | `not_reviewed` \| `pending` \| `approved` \| `rejected`. Only `approved` can pass. |
| `redistribution` | `{allowed: bool, conditions: string}`. `allowed` must be `true`. |
| `intended_use` | Public-safe description of how the material will be used. |
| `source_classification` | See **Allowed classifications** below. |
| `origin_review_state` | `unverified` \| `uncertain` \| `approved` \| `rejected`. Only `approved` can pass. |
| `identifier_safety_state` | `no_real_identifiers` \| `contains_real_identifiers` \| `uncertain`. Only `no_real_identifiers` can pass. |
| `content_classification_flags` | `{patient_derived, institutional, employer_confidential, clinical_study, restricted_other}`, all booleans. Every flag must be `false`. |
| `is_derivative` | `true` if this material was produced by transforming source material. |
| `files` | Array of `{path, sha256}` governed files. `path` is relative to the validation root; `sha256` is the lowercase 64-hex digest of the file's bytes. |
| `transformation_history` | Array of transformation records (empty array `[]` allowed only when `is_derivative` is `false`). Each record must identify both its input (`input_ref`/`input_sha256`) and its output (`output_ref`/`output_sha256`). |
| `eligibility_state` | `pending_review` \| `quarantine` \| `eligible_for_promotion` \| `rejected`. Only `eligible_for_promotion` can pass, and that self-declared state never overrides another failure. |

### Strict contract and format checks

- Unknown fields are rejected at the manifest root and inside redistribution, content-flag, file, and transformation records; the validator never silently ignores an unrecognized policy field.
- `source_url`, when present, must be a structurally public HTTP(S) URL: credentials, whitespace, local/single-label hostnames, and non-global IP addresses are rejected. `doi`, when present, must match DOI form. At least one is required. The human origin review—not URL parsing—establishes that the source is genuinely public and legitimate.
- `acquisition_date` must be a real calendar date, not merely a string shaped like `YYYY-MM-DD`.
- Transformation steps must be positive, unique, and sequential from 1; timestamps must parse as ISO 8601 dates or date-times.
- `eligibility_state` must be `eligible_for_promotion`. `pending_review`, `quarantine`, and `rejected` all fail closed.
### Dataset license vs. repository license

`license` describes the **dataset's** license. It is completely independent
of this repository's [`LICENSE`](../LICENSE) (MIT), which covers only the
code and documentation committed to this Git repository. A dataset's license
terms (attribution, share-alike, redistribution limits, non-commercial use,
etc.) apply to that dataset regardless of what license this repository uses
for its own scripts and docs.

## Allowed classifications

`source_classification` must be exactly one of:

- `synthetic` — fabricated data with no real source subject.
- `public_licensed` — legitimately public, appropriately licensed dataset
  material.

No other value is accepted. In particular, **de-identification alone is
never authorization** (D1/D21): a value like `de_identified` is rejected the
same as any other unrecognized classification, and there is deliberately no
classification that means "de-identified real data." If material is not
synthetic and not a legitimately public, appropriately licensed dataset, it
does not belong in this repository's lab under any classification.

## License and redistribution review

Two independent controls, both fail-closed:

1. **License control** — `license` must be one of a small reviewed allowlist
   (currently `CC0-1.0`, `CC-BY-4.0`, `CC-BY-SA-4.0`, `MIT`, `Apache-2.0`,
   `Public-Domain`, `Synthetic-No-License-Required`). Changing this allowlist
   is a policy change and goes through the normal reviewed pull-request
   workflow, not a silent edit.
2. **License-review-state control** — `license_review_state` must be
   `approved`. `not_reviewed`, `pending`, and `rejected` all fail closed;
   there is no default-approve behavior for a missing or ambiguous state.
3. **Redistribution control** — `redistribution.allowed` must be `true`.
   `redistribution.conditions` is a required public-safe free-text field
   describing any attribution/share-alike/non-commercial limits, even when
   the value is an explicit empty string for a license with no conditions.

## Origin and content-safety review

- **Origin-review control** — `origin_review_state` must be `approved`.
  `unverified` and `uncertain` are rejected as uncertain/unverified origin;
  `rejected` is rejected as rejected.
- **Identifier-safety control** — `identifier_safety_state` must be
  `no_real_identifiers`. A positive (`contains_real_identifiers`) or
  uncertain state both fail closed.
- **Content-safety control** — every key in `content_classification_flags`
  (`patient_derived`, `institutional`, `employer_confidential`,
  `clinical_study`, `restricted_other`) must be `false`. Any flag set `true`,
  missing, or not a boolean fails closed.

None of these controls treat a missing, unknown, or ambiguous value as
approval; every one of them requires an explicit, recognized, positive value
to pass.

## SHA-256 verification

For every entry in `files`:

1. The `sha256` field must be a lowercase 64-character hex string, or the
   entry is rejected for an invalid checksum format.
2. The `path` field is resolved against the validation root supplied on the
   command line (`--root`), never against an absolute path:
   - Absolute paths (`/...`, `\...`, or a drive letter) are rejected outright.
   - Any `..` path segment is rejected as parent-directory traversal.
   - The fully resolved path is confirmed to still be inside the resolved
     root; anything that would escape the root is rejected.
3. If the resolved file does not exist, that is a rejection.
4. The validator opens the file **read-only**, computes its SHA-256 from the
   actual bytes, and compares it to the manifest's expected value. Any
   mismatch is rejected. The validator never prints file contents — only
   paths, categories, and hex digests, none of which are secret.

## Transformation records

`transformation_history` is an array of records, each requiring `step`
(integer), `action`, `timestamp`, and a non-empty public-safe `description`.
Every record must also identify **both** its input and its output — a
nonempty record is not enough by itself:

- **Input linkage**: `input_ref` and/or `input_sha256` (at least one).
- **Output linkage**: `output_ref` and/or `output_sha256` (at least one).

A record missing either side of this linkage is rejected
(`[transformation_linkage]`), even if every other field on it is valid.
Optional fields `tool` and `tool_version` let a record additionally name the
tool and version used; any `*_sha256` field present must still be a valid
64-hex digest.

### Reference safety (structural, not provenance)

Whenever `input_ref` or `output_ref` is supplied, it must be a genuinely
usable, public-safe reference, not merely a present string key. The
validator (`is_public_safe_reference` in `validate-promotion-manifest.py`,
mirrored portably in the schema's `pattern` for `input_ref`/`output_ref`)
rejects a supplied reference (`[reference_safety]`) that is:

- Empty or whitespace-only after stripping.
- Contains a control character.
- An absolute POSIX path, or a Windows drive-letter or UNC path.
- Parent-directory traversal (`..` as a path segment, either slash style).
- Home-relative (`~`), environment-variable (`$VAR`, `%VAR%`), or
  `file://` URI syntax.

This check runs independently per field: a malformed `input_ref` or
`output_ref` is rejected even when a valid checksum alternative
(`input_sha256`/`output_sha256`) is also present on the same record — an
invalid field is never silently ignored just because its ref/checksum
counterpart is valid.

**This is a structural check only.** It confirms the string is
*syntactically* a plausible, non-private, non-traversal reference. It does
**not**, and cannot, confirm the reference genuinely identifies the claimed
material, that the material is what it claims to be, or anything else about
real-world provenance — that remains a human review responsibility, same as
`origin_review_state` and the other human-attested fields above. The
validator also never requires historical input files to exist locally and
never makes a network request to resolve a reference.

### Actual derivative connection (not just placeholder presence)

Beyond per-field safety, the validator confirms the history record set
actually forms a connected, reproducible chain rather than accepting
arbitrary placeholder values as claimed linkage (`[transformation_chain]`):

- **Final output must match a governed file.** The last step's
  `output_ref` and/or `output_sha256` must match a `files[]` entry's `path`
  and/or `sha256`. A final step whose output does not correspond to any
  governed file is rejected.
- **Multi-step chains must connect.** For a history with more than one
  step, each later step's input must share at least one common validated
  reference or checksum with the immediately preceding step's output
  (`input_ref == earlier output_ref`, or `input_sha256 == earlier
  output_sha256`). A step whose input does not connect to the previous
  step's output is rejected, even if both steps are individually
  well-formed.

These checks are also structural: they confirm the manifest's own claimed
references are internally consistent and terminate at a byte-checked
governed file. They do not confirm the intermediate, non-governed steps of
the chain (inputs to earlier steps that are not themselves governed files)
actually happened as described — that remains a human review responsibility.

- An **original source** with no transformation sets `is_derivative: false`
  and may use an explicitly empty `transformation_history: []`; the chain
  and final-output checks above do not apply to an empty history.
- A **declared derivative** (`is_derivative: true`) must have at least one
  transformation record, or it is rejected for missing required
  transformation history — and that record must satisfy the input/output
  linkage, reference-safety, and chain/final-output requirements above, not
  merely exist.
- Step values must be the exact sequence `1..N`, and every timestamp must be a valid ISO 8601 date or date-time.

## Validator usage

```bash
python3 scripts/validate-promotion-manifest.py \
  --manifest scripts/promotion-manifest-fixtures/valid/manifest.json \
  --root scripts/promotion-manifest-fixtures/valid
```

Standard-library-only Python 3, no third-party packages, no network access.

**Exit codes:**

| Code | Meaning |
|---|---|
| `0` | Every control passed. Printed as `ELIGIBLE: ...`. |
| `1` | At least one control failed. Printed as `REJECTED: N pre-promotion control(s) failed.`, followed by one `[category] message` line per failure. |
| `2` | Usage error — the manifest could not be read/parsed as JSON, or `--root` is not a directory. Distinct from a policy rejection. |

The validator never moves, renames, deletes, modifies, or promotes the
referenced material, and never rewrites the manifest. It is safe to run
locally and in CI against the same synthetic fixtures every time
(deterministic output for a given input).

## Meaning of successful validation

A successful (`ELIGIBLE`, exit `0`) result means only:

> This manifest and its referenced fixture satisfy the automated
> pre-promotion controls.

It is evidence for section C. It is not, by itself:

- Authorization to promote real material of any kind.
- Authorization for patient-derived, employer, institutional,
  clinical-study, or uncertain-origin material — those are rejected by the
  controls themselves, independent of what any field claims.
- Completion of the bounded pilot (section E) — section D's remaining
  metaphase-specific protection and local-second-copy work (issue #19) still
  block the pilot, and the pilot itself requires a real reviewed dataset run
  through this whole workflow, not just a synthetic fixture pass.
- Related to issue #18's GitHub workflow (editing/closing the issue, opening
  or merging the pull request) — those remain separate, later, human steps.

## Stop conditions

Stop and investigate — do not promote, and do not treat the situation as
resolved by re-running the validator — if any of the following occurs:

- The validator reports any rejection category.
- A SHA-256 checksum does not match.
- `origin_review_state`, `license_review_state`, or `identifier_safety_state`
  is anything other than an explicit approved/safe value.
- Any `content_classification_flags` value is `true`, missing, or not a
  boolean.
- `source_classification` is anything other than `synthetic` or
  `public_licensed`.
- A referenced path is absolute, contains `..`, or resolves outside the
  supplied validation root.
- A declared derivative has no transformation history, or a transformation
  record exists but does not identify both its input and its output
  (`input_ref`/`input_sha256` and `output_ref`/`output_sha256`).
- A supplied `input_ref`/`output_ref` is empty, whitespace-only, contains a
  control character, or uses an absolute, drive-letter, UNC, traversal,
  home-relative, environment-variable, or `file://` reference syntax.
- A multi-step transformation chain doesn't connect (a later step's input
  shares no validated reference or checksum with the preceding step's
  output), or the final step's output doesn't match any `files[]` entry.
- `eligibility_state` is `pending_review`, `quarantine`, or `rejected`; only `eligible_for_promotion` may pass.
- The manifest claims `eligible_for_promotion` while another control fails — the validator adds an `eligibility_consistency` failure rather than trusting the self-declared state.
- A source locator, calendar date, transformation timestamp/sequence, or declared field is invalid or unknown.
- Anything about the material's real-world origin, license, or content is
  uncertain, even if every machine-checkable field happens to be filled in.

## Correction and rollback behavior

- **Failed validation leaves material in quarantine.** The validator never
  moves, deletes, or promotes anything; a rejection changes nothing on disk.
- **No validator failure alters the manifest or referenced files.** The tool
  is read-only end to end.
- **Correct metadata through a reviewed manifest revision**, not by silently
  editing the failing field until the tool passes. A manifest correction is
  a normal, reviewed change like any other repository change (see
  `CONTRIBUTING.md`), and the prior (rejected) manifest state remains in Git
  history as an audit record.
- **A checksum mismatch requires investigation or independently verified
  reacquisition.** Do not simply replace the manifest's expected checksum
  with whatever the validator computed — that would silently launder a
  content change (or a corrupted/substituted file) into a passing result.
- **If material was incorrectly classified after promotion**, revoke its
  eligibility and return it to quarantine or an explicit `rejected` state in
  its manifest; do not leave a stale `eligible_for_promotion` claim in place.
- **If an erroneous promotion is discovered**, stop downstream use of the
  material immediately, preserve the audit record (manifest history, Git
  history), and have an administrator (Austin) review disposition before any
  further action.
- **Do not silently mutate or delete protected canonical content.** Canonical
  raw sources and approved releases are already protected against the
  routine workflow identity's create/modify/rename/delete attempts (section
  B, `metaphase-archive-boundary.md`); this control layer does not change
  that protection or provide a bypass.
- **Repository rollback** for this change is the normal Git workflow: revert
  the focused commit(s)/PR through review, same as any other change under
  D16/D17.
- **Scope discipline** — none of the above steps remove or alter unrelated
  archive structures, permissions, identities, shares, or system
  configuration. This control layer only adds a schema, a validator, its
  tests and fixtures, and documentation.

## Limitations and deliberately untested behavior

This exercise proves the schema, validator, and fixture suite behave as
designed against **synthetic data only**. It does **not** prove:

- Anything about real dataset content, license terms, or provenance, since
  no real dataset was used anywhere in this work.
- That a syntactically acceptable source URL is reachable, genuinely public,
  owned by the claimed publisher, or appropriately licensed. The validator
  performs no DNS lookup or network request; explicit human origin and license
  review remain mandatory.
- Exhaustive behavior across every adversarial input. The suite covers a symlink-based root escape and verifies the linked-to file is unchanged, but does not exhaustively cover extremely large files, nested or platform-specific path behavior beyond that case, or non-UTF-8 manifest encodings.
- Integration with an actual quarantine → canonical promotion mechanism —
  no such mechanism exists yet; this validator only gates a manifest, it
  does not perform or trigger a promotion.
- Anything about section D's remaining metaphase-specific protection and
  local-second-copy requirements (issue #19), which are separate, unstarted
  work.
- Anything about the bounded pilot in section E, which requires a real,
  reviewed, small public/synthetic dataset run through the full workflow,
  not just a synthetic fixture validator pass.

## Section C evidence summary

- The schema (`promotion-manifest.schema.json`), validator
  (`validate-promotion-manifest.py`), and fixture suite
  (`promotion-manifest-fixtures/`) were exercised only with synthetic,
  obviously-fake fixtures using reserved/example identifiers.
- Twenty-seven automated unit tests cover the shipped valid/rejection fixtures, symlink containment, non-destructive behavior, usage errors, schema alignment, rejected workflow states, malformed source locators, impossible dates, unknown fields, transformation sequence/timestamp enforcement, derivative input/output linkage, structural reference-safety rejection (empty, whitespace-only, control-character, absolute/drive/UNC/traversal, and home/environment/file-URI reference syntax), and multi-step transformation-chain/final-output-linkage enforcement.
- No real dataset was acquired, ingested, promoted, copied, or modified.
- No NAS archive content was accessed or changed; this work is entirely
  repository-local (schema, script, fixtures, tests, documentation) on
  `compute-node`.
- Passing the validator does not authorize patient-derived, employer,
  institutional, restricted, or uncertain-origin material — those are
  rejected outright by the controls themselves.
- Passing section C does not authorize the bounded pilot (section E) by
  itself.
- Section D's remaining metaphase-specific protection and local-second-copy
  requirements (issue #19) still block the pilot.
- Issue #18 and its pull-request workflow remain separate from this local
  implementation and review; this document records repository-controlled
  evidence only.
