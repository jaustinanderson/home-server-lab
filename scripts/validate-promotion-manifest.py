#!/usr/bin/env python3

"""Fail-closed pre-promotion control check for docs/promotion-manifest.schema.json manifests.

A passing result means only: this manifest and its referenced fixture bytes
satisfy the automated pre-promotion controls below. It does not authorize
promotion by itself, does not move or copy anything, and never overrides a
human license, origin, or content-safety review. See
docs/promotion-controls.md for the full control design and stop conditions.
"""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

SCHEMA_VERSION = "1.0.0"

# Policy allowlists. Changing any of these is a policy change and should go
# through the normal reviewed pull-request workflow, not a silent edit.
ALLOWED_SOURCE_CLASSIFICATIONS = {"synthetic", "public_licensed"}
ALLOWED_LICENSES = {
    "CC0-1.0",
    "CC-BY-4.0",
    "CC-BY-SA-4.0",
    "MIT",
    "Apache-2.0",
    "Public-Domain",
    "Synthetic-No-License-Required",
}
LICENSE_REVIEW_STATES = {"not_reviewed", "pending", "approved", "rejected"}
ORIGIN_REVIEW_STATES = {"unverified", "uncertain", "approved", "rejected"}
IDENTIFIER_SAFETY_STATES = {"no_real_identifiers", "contains_real_identifiers", "uncertain"}
ELIGIBILITY_STATES = {"pending_review", "quarantine", "eligible_for_promotion", "rejected"}
CONTENT_FLAG_KEYS = (
    "patient_derived",
    "institutional",
    "employer_confidential",
    "clinical_study",
    "restricted_other",
)

SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$")
CONTROL_CHARACTER_PATTERN = re.compile(r"[\x00-\x1f\x7f]")
WINDOWS_DRIVE_PATH_PATTERN = re.compile(r"^[A-Za-z]:[\\/]")
PRIVATE_PATH_PREFIXES = ("~", "$", "%", "file://")
ALLOWED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "dataset_name",
    "dataset_version",
    "publisher",
    "source_url",
    "doi",
    "acquisition_date",
    "license",
    "license_review_state",
    "redistribution",
    "intended_use",
    "source_classification",
    "origin_review_state",
    "identifier_safety_state",
    "content_classification_flags",
    "is_derivative",
    "files",
    "transformation_history",
    "eligibility_state",
}
REDISTRIBUTION_FIELDS = {"allowed", "conditions"}
FILE_ENTRY_FIELDS = {"path", "sha256"}
TRANSFORMATION_FIELDS = {
    "step",
    "action",
    "timestamp",
    "description",
    "input_ref",
    "input_sha256",
    "output_ref",
    "output_sha256",
    "tool",
    "tool_version",
}
CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class Failure:
    category: str
    message: str

    def __str__(self) -> str:
        return f"[{self.category}] {self.message}"


def load_manifest(manifest_path: Path) -> tuple[Optional[dict[str, Any]], Optional[str]]:
    try:
        raw = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"could not read manifest file: {exc.strerror or exc}"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, f"manifest is not valid JSON: {exc.msg} at line {exc.lineno}"
    if not isinstance(data, dict):
        return None, "manifest root must be a JSON object"
    return data, None


def resolve_safe_path(root: Path, raw_path: str) -> tuple[Optional[Path], Optional[str]]:
    """Resolve a manifest-declared relative path without escaping root.

    Rejects absolute paths, drive-letter paths, and parent-directory
    traversal, and confirms the resolved path stays inside root.
    """
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None, "file path is missing or empty"
    if raw_path.startswith(("/", "\\")):
        return None, "absolute paths are not allowed"
    if re.match(r"^[A-Za-z]:[\\/]", raw_path):
        return None, "absolute paths are not allowed"
    segments = re.split(r"[\\/]+", raw_path)
    if any(segment == ".." for segment in segments):
        return None, "parent-directory traversal is not allowed"

    root_resolved = root.resolve()
    candidate = (root_resolved / raw_path).resolve()
    if not candidate.is_relative_to(root_resolved):
        return None, "resolved path escapes the validation root"
    return candidate, None


def is_public_safe_reference(value: Any) -> tuple[bool, Optional[str]]:
    """Structural check for a transformation input_ref/output_ref value.

    Confirms the reference is a nonempty, printable, repository-relative-
    looking name: not an absolute POSIX path, a Windows drive or UNC path,
    parent-directory traversal, or home/environment-variable/file-URI syntax
    that could point at a private local location. This is a structural check
    only; it never touches the filesystem or network and cannot confirm the
    reference genuinely identifies the claimed material -- that remains a
    human provenance review responsibility (see docs/promotion-controls.md).
    """
    if not isinstance(value, str):
        return False, "must be a string"
    candidate = value.strip()
    if not candidate:
        return False, "must be a non-empty, non-whitespace-only string"
    if CONTROL_CHARACTER_PATTERN.search(value):
        return False, "must not contain control characters"
    if candidate.startswith(("/", "\\")):
        return False, "must not be an absolute POSIX path or a Windows/UNC path"
    if WINDOWS_DRIVE_PATH_PATTERN.match(candidate):
        return False, "must not be a Windows drive-letter path"
    segments = re.split(r"[\\/]+", candidate)
    if any(segment == ".." for segment in segments):
        return False, "must not contain parent-directory traversal"
    if candidate.startswith(PRIVATE_PATH_PREFIXES):
        return False, "must not use home-relative, environment-variable, or file-URI syntax"
    return True, None


def governed_file_identifiers(files: Any) -> tuple[set[str], set[str]]:
    """Collect the path and sha256 identifiers of well-formed `files` entries.

    Used only to check that a transformation's final output matches a
    governed file; malformed entries are skipped here because
    validate_files() already reports them independently.
    """
    paths: set[str] = set()
    checksums: set[str] = set()
    if not isinstance(files, list):
        return paths, checksums
    for entry in files:
        if not isinstance(entry, dict):
            continue
        path = entry.get("path")
        if isinstance(path, str) and path.strip():
            paths.add(path)
        checksum = entry.get("sha256")
        if isinstance(checksum, str) and SHA256_PATTERN.match(checksum):
            checksums.add(checksum)
    return paths, checksums


def refs_connect(later: dict[str, Optional[str]], earlier: dict[str, Optional[str]]) -> bool:
    """True if `later`'s input shares a validated reference or checksum with `earlier`'s output."""
    if later["input_ref"] is not None and later["input_ref"] == earlier["output_ref"]:
        return True
    if later["input_sha256"] is not None and later["input_sha256"] == earlier["output_sha256"]:
        return True
    return False


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_field(manifest: dict[str, Any], field: str, failures: list[Failure]) -> bool:
    if field not in manifest:
        failures.append(Failure("provenance", f"missing required field: {field}"))
        return False
    return True


def reject_unknown_fields(
    value: dict[str, Any], allowed: set[str], label: str, failures: list[Failure]
) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        failures.append(Failure("schema", f"{label} contains unknown fields: {', '.join(unknown)}"))


def is_valid_iso8601(value: str) -> bool:
    try:
        if DATE_PATTERN.fullmatch(value):
            date.fromisoformat(value)
        else:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def is_structurally_public_http_url(value: str) -> bool:
    """Reject malformed, credential-bearing, local, and non-global IP locators.

    This is a structural check only. Human origin review remains responsible
    for confirming that the source is genuinely public, legitimate, and
    appropriately licensed; the validator never fetches or resolves the URL.
    """
    if any(character.isspace() for character in value):
        return False
    try:
        parsed = urlparse(value)
        hostname = parsed.hostname
        # Accessing port forces urllib to reject malformed/out-of-range ports.
        parsed.port
    except ValueError:
        return False

    if parsed.scheme not in {"http", "https"} or not parsed.netloc or not hostname:
        return False
    if parsed.username is not None or parsed.password is not None:
        return False

    normalized_host = hostname.rstrip(".").lower()
    if normalized_host == "localhost" or normalized_host.endswith((".localhost", ".local")):
        return False

    try:
        address = ipaddress.ip_address(normalized_host)
    except ValueError:
        if len(normalized_host) > 253 or "." not in normalized_host:
            return False
        labels = normalized_host.split(".")
        return all(
            1 <= len(label) <= 63
            and re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", label) is not None
            for label in labels
        )
    return address.is_global


def validate_top_level_fields(manifest: dict[str, Any], failures: list[Failure]) -> None:
    required_fields = (
        "schema_version",
        "dataset_name",
        "dataset_version",
        "publisher",
        "acquisition_date",
        "license",
        "license_review_state",
        "redistribution",
        "intended_use",
        "source_classification",
        "origin_review_state",
        "identifier_safety_state",
        "content_classification_flags",
        "is_derivative",
        "files",
        "transformation_history",
        "eligibility_state",
    )
    for field in required_fields:
        require_field(manifest, field, failures)

    reject_unknown_fields(manifest, ALLOWED_TOP_LEVEL_FIELDS, "manifest", failures)

    if manifest.get("schema_version") is not None and manifest.get("schema_version") != SCHEMA_VERSION:
        failures.append(
            Failure("provenance", f"unsupported schema_version: {manifest.get('schema_version')!r}")
        )

    if "source_url" not in manifest and "doi" not in manifest:
        failures.append(Failure("provenance", "missing both source_url and doi; at least one is required"))

    if "source_url" in manifest:
        source_url = manifest.get("source_url")
        if (
            not isinstance(source_url, str)
            or not source_url.strip()
            or not is_structurally_public_http_url(source_url)
        ):
            failures.append(
                Failure(
                    "provenance",
                    "source_url must be a structurally public HTTP(S) URL without "
                    "credentials, a local hostname, or a non-global IP address",
                )
            )

    if "doi" in manifest:
        doi = manifest.get("doi")
        if not isinstance(doi, str) or not DOI_PATTERN.fullmatch(doi):
            failures.append(Failure("provenance", "doi must match the DOI form 10.<registrant>/<suffix>"))

    for string_field in ("dataset_name", "dataset_version", "publisher", "intended_use"):
        value = manifest.get(string_field)
        if string_field in manifest and (not isinstance(value, str) or not value.strip()):
            failures.append(Failure("provenance", f"{string_field} must be a non-empty string"))

    acquisition_date = manifest.get("acquisition_date")
    if "acquisition_date" in manifest:
        if (
            not isinstance(acquisition_date, str)
            or not DATE_PATTERN.fullmatch(acquisition_date)
            or not is_valid_iso8601(acquisition_date)
        ):
            failures.append(
                Failure("provenance", "acquisition_date must be a real ISO 8601 date (YYYY-MM-DD)")
            )

    if "is_derivative" in manifest and not isinstance(manifest.get("is_derivative"), bool):
        failures.append(Failure("provenance", "is_derivative must be a boolean"))

def validate_license(manifest: dict[str, Any], failures: list[Failure]) -> None:
    license_id = manifest.get("license")
    if "license" in manifest:
        if not isinstance(license_id, str) or not license_id.strip():
            failures.append(Failure("license", "license is missing"))
        elif license_id not in ALLOWED_LICENSES:
            failures.append(Failure("license", f"license is not on the approved allowlist: {license_id!r}"))

    review_state = manifest.get("license_review_state")
    if "license_review_state" in manifest:
        if review_state not in LICENSE_REVIEW_STATES:
            failures.append(
                Failure("license_review", f"license_review_state is not a recognized value: {review_state!r}")
            )
        elif review_state != "approved":
            failures.append(
                Failure("license_review", f"license review is not explicitly approved (state: {review_state})")
            )


def validate_redistribution(manifest: dict[str, Any], failures: list[Failure]) -> None:
    redistribution = manifest.get("redistribution")
    if "redistribution" not in manifest:
        return
    if not isinstance(redistribution, dict):
        failures.append(Failure("redistribution", "redistribution must be an object"))
        return
    reject_unknown_fields(redistribution, REDISTRIBUTION_FIELDS, "redistribution", failures)
    if "allowed" not in redistribution or not isinstance(redistribution.get("allowed"), bool):
        failures.append(Failure("redistribution", "redistribution.allowed must be a boolean"))
    elif redistribution["allowed"] is not True:
        failures.append(
            Failure("redistribution", "redistribution is prohibited or materially incompatible with intended use")
        )
    if "conditions" not in redistribution or not isinstance(redistribution.get("conditions"), str):
        failures.append(Failure("redistribution", "redistribution.conditions must be a string"))


def validate_classification(manifest: dict[str, Any], failures: list[Failure]) -> None:
    classification = manifest.get("source_classification")
    if "source_classification" in manifest and classification not in ALLOWED_SOURCE_CLASSIFICATIONS:
        failures.append(
            Failure("source_classification", f"unsupported source classification: {classification!r}")
        )

    origin_state = manifest.get("origin_review_state")
    if "origin_review_state" in manifest:
        if origin_state not in ORIGIN_REVIEW_STATES:
            failures.append(
                Failure("origin_review", f"origin_review_state is not a recognized value: {origin_state!r}")
            )
        elif origin_state != "approved":
            failures.append(
                Failure("origin_review", f"origin is uncertain or not verified (state: {origin_state})")
            )

    identifier_state = manifest.get("identifier_safety_state")
    if "identifier_safety_state" in manifest:
        if identifier_state not in IDENTIFIER_SAFETY_STATES:
            failures.append(
                Failure(
                    "identifier_safety",
                    f"identifier_safety_state is not a recognized value: {identifier_state!r}",
                )
            )
        elif identifier_state != "no_real_identifiers":
            failures.append(
                Failure(
                    "identifier_safety",
                    f"real or uncertain identifier safety state is not permitted (state: {identifier_state})",
                )
            )


def validate_content_flags(manifest: dict[str, Any], failures: list[Failure]) -> None:
    flags = manifest.get("content_classification_flags")
    if "content_classification_flags" not in manifest:
        return
    if not isinstance(flags, dict):
        failures.append(Failure("content_safety", "content_classification_flags must be an object"))
        return
    reject_unknown_fields(flags, set(CONTENT_FLAG_KEYS), "content_classification_flags", failures)

    missing = [key for key in CONTENT_FLAG_KEYS if key not in flags]
    if missing:
        failures.append(
            Failure("provenance", f"content_classification_flags missing keys: {', '.join(sorted(missing))}")
        )

    non_boolean = [key for key in CONTENT_FLAG_KEYS if key in flags and not isinstance(flags.get(key), bool)]
    if non_boolean:
        failures.append(
            Failure(
                "provenance",
                f"content_classification_flags must be boolean: {', '.join(sorted(non_boolean))}",
            )
        )

    raised = [key for key in CONTENT_FLAG_KEYS if flags.get(key) is True]
    if raised:
        failures.append(
            Failure("content_safety", f"disallowed content flagged: {', '.join(sorted(raised))}")
        )


def validate_files(
    manifest: dict[str, Any], root: Path, failures: list[Failure]
) -> None:
    files = manifest.get("files")
    if "files" not in manifest:
        return
    if not isinstance(files, list) or not files:
        failures.append(Failure("provenance", "files must be a non-empty array"))
        return

    for index, entry in enumerate(files):
        label = f"files[{index}]"
        if not isinstance(entry, dict):
            failures.append(Failure("provenance", f"{label} must be an object"))
            continue

        reject_unknown_fields(entry, FILE_ENTRY_FIELDS, label, failures)

        raw_path = entry.get("path")
        checksum = entry.get("sha256")

        if "path" not in entry:
            failures.append(Failure("provenance", f"{label} missing required field: path"))
        if "sha256" not in entry:
            failures.append(Failure("provenance", f"{label} missing required field: sha256"))
            continue

        if not isinstance(checksum, str) or not SHA256_PATTERN.match(checksum):
            failures.append(Failure("checksum_format", f"{label} sha256 is not a valid lowercase 64-hex digest"))
            continue

        if "path" not in entry:
            continue

        resolved, path_error = resolve_safe_path(root, raw_path)
        if path_error is not None:
            failures.append(Failure("path_safety", f"{label} ({raw_path!r}): {path_error}"))
            continue

        if not resolved.is_file():
            failures.append(Failure("checksum_mismatch", f"{label} referenced fixture file does not exist"))
            continue

        actual = sha256_of_file(resolved)
        if actual != checksum:
            failures.append(
                Failure(
                    "checksum_mismatch",
                    f"{label} SHA-256 mismatch: manifest expected {checksum}, computed {actual}",
                )
            )


def validate_transformation_history(manifest: dict[str, Any], failures: list[Failure]) -> None:
    history = manifest.get("transformation_history")
    is_derivative = manifest.get("is_derivative")

    if "transformation_history" not in manifest:
        return
    if not isinstance(history, list):
        failures.append(Failure("provenance", "transformation_history must be an array"))
        return

    steps: list[int] = []
    steps_are_valid = True
    entry_refs: list[Optional[dict[str, Optional[str]]]] = []
    for index, entry in enumerate(history):
        label = f"transformation_history[{index}]"
        if not isinstance(entry, dict):
            failures.append(Failure("provenance", f"{label} must be an object"))
            steps_are_valid = False
            entry_refs.append(None)
            continue

        reject_unknown_fields(entry, TRANSFORMATION_FIELDS, label, failures)

        for field in ("step", "action", "timestamp", "description"):
            if field not in entry:
                failures.append(Failure("provenance", f"{label} missing required field: {field}"))

        if "step" in entry:
            step = entry.get("step")
            if type(step) is not int or step < 1:
                failures.append(Failure("provenance", f"{label} step must be an integer of 1 or greater"))
                steps_are_valid = False
            else:
                steps.append(step)
        else:
            steps_are_valid = False

        for text_field in ("action", "description"):
            value = entry.get(text_field)
            if text_field in entry and (not isinstance(value, str) or not value.strip()):
                failures.append(Failure("provenance", f"{label} {text_field} must be a non-empty string"))

        timestamp = entry.get("timestamp")
        if "timestamp" in entry and (
            not isinstance(timestamp, str)
            or not timestamp.strip()
            or not is_valid_iso8601(timestamp)
        ):
            failures.append(Failure("provenance", f"{label} timestamp must be a valid ISO 8601 date or date-time"))

        for optional_text_field in ("tool", "tool_version"):
            value = entry.get(optional_text_field)
            if optional_text_field in entry and not isinstance(value, str):
                failures.append(Failure("provenance", f"{label} {optional_text_field} must be a string"))

        for ref_field in ("input_ref", "output_ref"):
            if ref_field not in entry:
                continue
            ok, error = is_public_safe_reference(entry.get(ref_field))
            if not ok:
                failures.append(Failure("reference_safety", f"{label} {ref_field} {error}"))

        for hash_field in ("input_sha256", "output_sha256"):
            value = entry.get(hash_field)
            if hash_field in entry and (not isinstance(value, str) or not SHA256_PATTERN.fullmatch(value)):
                failures.append(Failure("checksum_format", f"{label} {hash_field} is not a valid 64-hex digest"))

        if "input_ref" not in entry and "input_sha256" not in entry:
            failures.append(
                Failure(
                    "transformation_linkage",
                    f"{label} must include input_ref and/or input_sha256 to link to its source",
                )
            )
        if "output_ref" not in entry and "output_sha256" not in entry:
            failures.append(
                Failure(
                    "transformation_linkage",
                    f"{label} must include output_ref and/or output_sha256 to link to its output",
                )
            )

        entry_refs.append(
            {
                "input_ref": entry.get("input_ref") if isinstance(entry.get("input_ref"), str) else None,
                "input_sha256": entry.get("input_sha256") if isinstance(entry.get("input_sha256"), str) else None,
                "output_ref": entry.get("output_ref") if isinstance(entry.get("output_ref"), str) else None,
                "output_sha256": entry.get("output_sha256") if isinstance(entry.get("output_sha256"), str) else None,
            }
        )

    if len(entry_refs) == len(history) and len(history) > 1:
        for index in range(1, len(history)):
            later, earlier = entry_refs[index], entry_refs[index - 1]
            if later is None or earlier is None:
                continue
            if not refs_connect(later, earlier):
                failures.append(
                    Failure(
                        "transformation_chain",
                        f"transformation_history[{index}] input does not connect to the output of "
                        f"transformation_history[{index - 1}] via a matching reference or checksum",
                    )
                )

    if history and entry_refs and entry_refs[-1] is not None:
        final = entry_refs[-1]
        file_paths, file_checksums = governed_file_identifiers(manifest.get("files"))
        matches_path = final["output_ref"] is not None and final["output_ref"] in file_paths
        matches_checksum = final["output_sha256"] is not None and final["output_sha256"] in file_checksums
        if not (matches_path or matches_checksum):
            failures.append(
                Failure(
                    "transformation_chain",
                    "the final transformation_history output does not match any files[] entry "
                    "by path or sha256",
                )
            )

    if steps_are_valid and len(steps) == len(history):
        expected_steps = list(range(1, len(history) + 1))
        if steps != expected_steps:
            failures.append(
                Failure(
                    "transformation_history",
                    f"transformation steps must be unique and sequential from 1; got {steps!r}",
                )
            )

    if is_derivative is True and len(history) < 1:
        failures.append(
            Failure(
                "transformation_history",
                "material is declared a derivative (is_derivative: true) but transformation_history is empty",
            )
        )

def validate_eligibility_state(manifest: dict[str, Any], failures: list[Failure]) -> None:
    state = manifest.get("eligibility_state")
    if "eligibility_state" not in manifest:
        return
    if state not in ELIGIBILITY_STATES:
        failures.append(Failure("provenance", f"eligibility_state is not a recognized value: {state!r}"))
        return
    if state != "eligible_for_promotion":
        failures.append(
            Failure(
                "eligibility_state",
                f"eligibility_state does not permit promotion (state: {state})",
            )
        )
        return
    if failures:
        failures.append(
            Failure(
                "eligibility_consistency",
                "manifest declares eligibility_state 'eligible_for_promotion' but other controls failed; "
                "a self-declared state is never treated as authorization",
            )
        )

def validate_manifest(manifest: dict[str, Any], root: Path) -> list[Failure]:
    failures: list[Failure] = []
    validate_top_level_fields(manifest, failures)
    validate_license(manifest, failures)
    validate_redistribution(manifest, failures)
    validate_classification(manifest, failures)
    validate_content_flags(manifest, failures)
    validate_files(manifest, root, failures)
    validate_transformation_history(manifest, failures)
    validate_eligibility_state(manifest, failures)
    return failures


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fail-closed pre-promotion control check for a promotion manifest and its "
            "referenced fixture bytes. Never moves, copies, promotes, or rewrites anything."
        )
    )
    parser.add_argument("--manifest", required=True, type=Path, help="path to the manifest JSON file")
    parser.add_argument(
        "--root",
        required=True,
        type=Path,
        help="validation/quarantine root that governed file paths are resolved relative to",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if not args.root.is_dir():
        print(f"[usage] validation root is not a directory: {args.root}", file=sys.stderr)
        return 2

    manifest, load_error = load_manifest(args.manifest)
    if load_error is not None:
        print(f"[usage] {load_error}", file=sys.stderr)
        return 2

    failures = validate_manifest(manifest, args.root)

    if failures:
        print(f"REJECTED: {len(failures)} pre-promotion control(s) failed.")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("ELIGIBLE: this manifest and its referenced fixture satisfy the automated pre-promotion controls.")
    print("This result alone does not authorize promotion; see docs/promotion-controls.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
