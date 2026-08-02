#!/usr/bin/env python3

"""Automated tests for scripts/validate-promotion-manifest.py using synthetic fixtures only.

Confirms the valid fixture passes, every invalid fixture fails with an
identifiable control category, the validator never modifies the manifests or
fixture files it reads, and the shipped JSON Schema stays aligned with the
validator's own required-field and enumeration policy. No real dataset is
read, downloaded, or referenced anywhere in this test module.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
VALIDATOR = SCRIPTS_DIR / "validate-promotion-manifest.py"
FIXTURES_DIR = SCRIPTS_DIR / "promotion-manifest-fixtures"
SCHEMA_PATH = REPO_ROOT / "docs" / "promotion-manifest.schema.json"

# Expected (fixture directory -> substring that must appear in a failure line)
# for every fail-closed rejection case in the synthetic test matrix.
INVALID_FIXTURES = {
    "uncertain-origin": "[origin_review]",
    "unapproved-license": "[license]",
    "restricted-material": "[content_safety]",
    "unsupported-classification": "[source_classification]",
    "checksum-mismatch": "[checksum_mismatch]",
    "missing-provenance": "missing required field: publisher",
    "missing-transformation-history": "[transformation_history]",
    "unsafe-path": "[path_safety]",
}


def run_validator(manifest: Path, root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--manifest", str(manifest), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def snapshot_fixture_tree() -> dict[str, tuple[int, str]]:
    snapshot: dict[str, tuple[int, str]] = {}
    for path in sorted(FIXTURES_DIR.rglob("*")):
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            snapshot[str(path.relative_to(FIXTURES_DIR))] = (path.stat().st_mtime_ns, digest)
    return snapshot


class ValidFixtureTests(unittest.TestCase):
    def test_valid_fixture_exits_zero_and_reports_eligible(self) -> None:
        case_dir = FIXTURES_DIR / "valid"
        result = run_validator(case_dir / "manifest.json", case_dir)
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("ELIGIBLE", result.stdout)
        self.assertIn("does not authorize promotion", result.stdout)


class InvalidFixtureTests(unittest.TestCase):
    def test_every_invalid_fixture_is_rejected(self) -> None:
        for case_name, expected_substring in INVALID_FIXTURES.items():
            with self.subTest(case=case_name):
                case_dir = FIXTURES_DIR / case_name
                result = run_validator(case_dir / "manifest.json", case_dir)
                self.assertNotEqual(result.returncode, 0, msg=f"{case_name} unexpectedly passed")
                self.assertIn("REJECTED", result.stdout)
                self.assertIn(expected_substring, result.stdout, msg=result.stdout)


class PathSafetyTests(unittest.TestCase):
    """Confirm a relative path that appears inside the validation root but
    resolves outside it through a symbolic link is rejected. Every path used
    here is a disposable synthetic temporary directory, not a repository
    fixture; the outside file's bytes are never printed by the test or by
    the validator, and the test confirms they are untouched afterward using
    only a checksum/size/mtime comparison, never a raw-content comparison.
    """

    def test_symlink_escaping_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="promotion-control-symlink-test-") as tmp:
            tmp_path = Path(tmp)

            outside_dir = tmp_path / "outside"
            outside_dir.mkdir()
            outside_file = outside_dir / "outside-fixture.txt"
            outside_file.write_bytes(
                b"Synthetic out-of-root fixture content for the symlink-escape regression test.\n"
            )

            root_dir = tmp_path / "root"
            root_dir.mkdir()
            linked_path = root_dir / "linked-file.txt"
            try:
                linked_path.symlink_to(outside_file)
            except OSError as exc:
                self.skipTest(f"symlinks are not supported in this environment: {exc}")

            manifest = json.loads((FIXTURES_DIR / "valid" / "manifest.json").read_text(encoding="utf-8"))
            manifest["files"] = [{"path": "linked-file.txt", "sha256": "0" * 64}]
            manifest_path = root_dir / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            before_digest = hashlib.sha256(outside_file.read_bytes()).hexdigest()
            before_size = outside_file.stat().st_size
            before_mtime = outside_file.stat().st_mtime_ns

            result = run_validator(manifest_path, root_dir)

            after_digest = hashlib.sha256(outside_file.read_bytes()).hexdigest()
            after_size = outside_file.stat().st_size
            after_mtime = outside_file.stat().st_mtime_ns

            self.assertNotEqual(result.returncode, 0, msg=result.stdout)
            self.assertIn("[path_safety]", result.stdout)
            self.assertIn("escapes the validation root", result.stdout)

            # The validator must never print the linked-to file's bytes, only
            # paths, categories, and hex digests.
            self.assertNotIn("Synthetic out-of-root fixture content", result.stdout)
            self.assertNotIn("Synthetic out-of-root fixture content", result.stderr)

            # Non-destructive: the file outside the root is byte-for-byte and
            # metadata-identical before and after, checked only via digest/
            # size/mtime, never by comparing or printing raw content.
            self.assertEqual(before_digest, after_digest)
            self.assertEqual(before_size, after_size)
            self.assertEqual(before_mtime, after_mtime)


class FailClosedPolicyTests(unittest.TestCase):
    def run_mutated_valid(self, mutate) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory(prefix="promotion-control-policy-test-") as tmp:
            root = Path(tmp)
            fixture_source = FIXTURES_DIR / "valid" / "fixture.txt"
            (root / "fixture.txt").write_bytes(fixture_source.read_bytes())
            manifest = json.loads((FIXTURES_DIR / "valid" / "manifest.json").read_text(encoding="utf-8"))
            mutate(manifest)
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            return run_validator(manifest_path, root)

    def assert_rejected(self, result: subprocess.CompletedProcess, expected: str) -> None:
        self.assertNotEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("REJECTED", result.stdout)
        self.assertIn(expected, result.stdout, msg=result.stdout)

    def test_noneligible_workflow_states_never_pass(self) -> None:
        for state in ("pending_review", "quarantine", "rejected"):
            with self.subTest(state=state):
                result = self.run_mutated_valid(lambda manifest: manifest.update(eligibility_state=state))
                self.assert_rejected(result, "[eligibility_state]")

    def test_invalid_source_url_is_rejected(self) -> None:
        invalid_urls = (
            "not-a-public-url",
            "http://localhost/data",
            "https://dataset.local/data",
            "https://127.0.0.1/data",
            "https://10.0.0.1/data",
            "http://[::1]/data",
            "https://user:password@example.com/data",
            "https://example.com/white space",
            "https://single-label/data",
        )
        for source_url in invalid_urls:
            with self.subTest(source_url=source_url):
                def mutate(manifest: dict, value: str = source_url) -> None:
                    manifest.pop("doi", None)
                    manifest["source_url"] = value

                self.assert_rejected(self.run_mutated_valid(mutate), "[provenance]")

    def test_invalid_doi_is_rejected(self) -> None:
        def mutate(manifest: dict) -> None:
            manifest.pop("source_url", None)
            manifest["doi"] = "not-a-doi"

        self.assert_rejected(self.run_mutated_valid(mutate), "[provenance]")

    def test_impossible_calendar_date_is_rejected(self) -> None:
        result = self.run_mutated_valid(
            lambda manifest: manifest.update(acquisition_date="2026-02-30")
        )
        self.assert_rejected(result, "real ISO 8601 date")

    def test_unknown_top_level_and_nested_fields_are_rejected(self) -> None:
        def mutate_top(manifest: dict) -> None:
            manifest["unexpected_policy_bypass"] = True

        self.assert_rejected(self.run_mutated_valid(mutate_top), "[schema]")

        def mutate_nested(manifest: dict) -> None:
            manifest["files"][0]["unexpected"] = "ignored-before-fix"

        self.assert_rejected(self.run_mutated_valid(mutate_nested), "[schema]")

    def test_transformation_steps_and_timestamps_are_enforced(self) -> None:
        def mutate(manifest: dict) -> None:
            manifest["is_derivative"] = True
            manifest["transformation_history"] = [
                {
                    "step": 0,
                    "action": "synthetic-transform",
                    "timestamp": "not-a-date",
                    "description": "Synthetic invalid transformation record.",
                }
            ]

        result = self.run_mutated_valid(mutate)
        self.assert_rejected(result, "step must be an integer of 1 or greater")
        self.assertIn("timestamp must be a valid ISO 8601", result.stdout)

    def test_valid_derivative_linkage_passes(self) -> None:
        def mutate(manifest: dict) -> None:
            manifest["is_derivative"] = True
            manifest["transformation_history"] = [
                {
                    "step": 1,
                    "input_ref": "example-raw-source.txt",
                    "input_sha256": "0" * 64,
                    "output_ref": "fixture.txt",
                    "output_sha256": manifest["files"][0]["sha256"],
                    "action": "synthesize",
                    "timestamp": "2026-08-01T00:00:00Z",
                    "description": "Synthetic derivative generated from a synthetic input fixture for regression testing.",
                }
            ]

        result = self.run_mutated_valid(mutate)
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("ELIGIBLE", result.stdout)

    def test_derivative_missing_input_linkage_is_rejected(self) -> None:
        def mutate(manifest: dict) -> None:
            manifest["is_derivative"] = True
            manifest["transformation_history"] = [
                {
                    "step": 1,
                    "output_ref": "fixture.txt",
                    "output_sha256": manifest["files"][0]["sha256"],
                    "action": "synthesize",
                    "timestamp": "2026-08-01T00:00:00Z",
                    "description": "Exercises the rejection path for a transformation record missing input linkage.",
                }
            ]

        result = self.run_mutated_valid(mutate)
        self.assert_rejected(result, "[transformation_linkage]")
        self.assertIn("input_ref and/or input_sha256", result.stdout)

    def test_derivative_missing_output_linkage_is_rejected(self) -> None:
        def mutate(manifest: dict) -> None:
            manifest["is_derivative"] = True
            manifest["transformation_history"] = [
                {
                    "step": 1,
                    "input_ref": "example-raw-source.txt",
                    "input_sha256": "0" * 64,
                    "action": "synthesize",
                    "timestamp": "2026-08-01T00:00:00Z",
                    "description": "Exercises the rejection path for a transformation record missing output linkage.",
                }
            ]

        result = self.run_mutated_valid(mutate)
        self.assert_rejected(result, "[transformation_linkage]")
        self.assertIn("output_ref and/or output_sha256", result.stdout)

    def test_empty_input_ref_as_sole_input_linkage_is_rejected(self) -> None:
        def mutate(manifest: dict) -> None:
            manifest["is_derivative"] = True
            manifest["transformation_history"] = [
                {
                    "step": 1,
                    "input_ref": "",
                    "output_ref": "fixture.txt",
                    "output_sha256": manifest["files"][0]["sha256"],
                    "action": "synthesize",
                    "timestamp": "2026-08-01T00:00:00Z",
                    "description": "Exercises rejection of an empty input_ref used as the sole input linkage.",
                }
            ]

        result = self.run_mutated_valid(mutate)
        self.assert_rejected(result, "[reference_safety]")
        self.assertIn("non-empty, non-whitespace-only string", result.stdout)

    def test_whitespace_only_output_ref_as_sole_output_linkage_is_rejected(self) -> None:
        def mutate(manifest: dict) -> None:
            manifest["is_derivative"] = True
            manifest["transformation_history"] = [
                {
                    "step": 1,
                    "input_ref": "example-raw-source.txt",
                    "input_sha256": "0" * 64,
                    "output_ref": "   ",
                    "action": "synthesize",
                    "timestamp": "2026-08-01T00:00:00Z",
                    "description": "Exercises rejection of a whitespace-only output_ref used as the sole output linkage.",
                }
            ]

        result = self.run_mutated_valid(mutate)
        self.assert_rejected(result, "[reference_safety]")
        self.assertIn("non-empty, non-whitespace-only string", result.stdout)

    def test_unsafe_reference_syntax_is_rejected(self) -> None:
        unsafe_values = (
            "/etc/passwd",
            "../../etc/passwd",
            r"C:\Users\example\secret.txt",
            r"\\host\share\file.txt",
            "~/private/file.txt",
            "$HOME/file.txt",
            "%APPDATA%\\file.txt",
            "file:///etc/passwd",
        )
        for unsafe_ref in unsafe_values:
            with self.subTest(input_ref=unsafe_ref):
                def mutate(manifest: dict, value: str = unsafe_ref) -> None:
                    manifest["is_derivative"] = True
                    manifest["transformation_history"] = [
                        {
                            "step": 1,
                            "input_ref": value,
                            "output_ref": "fixture.txt",
                            "output_sha256": manifest["files"][0]["sha256"],
                            "action": "synthesize",
                            "timestamp": "2026-08-01T00:00:00Z",
                            "description": "Exercises rejection of an unsafe input_ref reference syntax.",
                        }
                    ]

                self.assert_rejected(self.run_mutated_valid(mutate), "[reference_safety]")

    def test_invalid_ref_with_valid_checksum_alternative_is_still_rejected(self) -> None:
        def mutate(manifest: dict) -> None:
            manifest["is_derivative"] = True
            manifest["transformation_history"] = [
                {
                    "step": 1,
                    "input_ref": "",
                    "input_sha256": "0" * 64,
                    "output_ref": "fixture.txt",
                    "output_sha256": manifest["files"][0]["sha256"],
                    "action": "synthesize",
                    "timestamp": "2026-08-01T00:00:00Z",
                    "description": (
                        "An invalid input_ref must fail even though input_sha256 is a "
                        "validly formatted checksum."
                    ),
                }
            ]

        result = self.run_mutated_valid(mutate)
        self.assert_rejected(result, "[reference_safety]")

    def test_final_output_not_matching_governed_file_is_rejected(self) -> None:
        def mutate(manifest: dict) -> None:
            manifest["is_derivative"] = True
            manifest["transformation_history"] = [
                {
                    "step": 1,
                    "input_ref": "example-raw-source.txt",
                    "input_sha256": "0" * 64,
                    "output_ref": "not-a-governed-file.txt",
                    "output_sha256": "2" * 64,
                    "action": "synthesize",
                    "timestamp": "2026-08-01T00:00:00Z",
                    "description": "Final transformation output intentionally does not match any files[] entry.",
                }
            ]

        result = self.run_mutated_valid(mutate)
        self.assert_rejected(result, "[transformation_chain]")
        self.assertIn("does not match any files[] entry", result.stdout)

    def test_valid_two_step_transformation_chain_passes(self) -> None:
        def mutate(manifest: dict) -> None:
            manifest["is_derivative"] = True
            manifest["transformation_history"] = [
                {
                    "step": 1,
                    "input_ref": "example-raw-source.txt",
                    "input_sha256": "0" * 64,
                    "output_ref": "intermediate.bin",
                    "output_sha256": "1" * 64,
                    "action": "convert",
                    "timestamp": "2026-08-01T00:00:00Z",
                    "description": "First step: synthetic raw source converted to an intermediate synthetic artifact.",
                },
                {
                    "step": 2,
                    "input_ref": "intermediate.bin",
                    "input_sha256": "1" * 64,
                    "output_ref": "fixture.txt",
                    "output_sha256": manifest["files"][0]["sha256"],
                    "action": "finalize",
                    "timestamp": "2026-08-01T01:00:00Z",
                    "description": "Second step: intermediate synthetic artifact finalized into the governed fixture.",
                },
            ]

        result = self.run_mutated_valid(mutate)
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("ELIGIBLE", result.stdout)

    def test_broken_two_step_transformation_chain_is_rejected(self) -> None:
        def mutate(manifest: dict) -> None:
            manifest["is_derivative"] = True
            manifest["transformation_history"] = [
                {
                    "step": 1,
                    "input_ref": "example-raw-source.txt",
                    "input_sha256": "0" * 64,
                    "output_ref": "intermediate.bin",
                    "output_sha256": "1" * 64,
                    "action": "convert",
                    "timestamp": "2026-08-01T00:00:00Z",
                    "description": "First step: synthetic raw source converted to an intermediate synthetic artifact.",
                },
                {
                    "step": 2,
                    "input_ref": "unrelated-artifact.bin",
                    "input_sha256": "9" * 64,
                    "output_ref": "fixture.txt",
                    "output_sha256": manifest["files"][0]["sha256"],
                    "action": "finalize",
                    "timestamp": "2026-08-01T01:00:00Z",
                    "description": "Second step intentionally does not connect to the first step's output.",
                },
            ]

        result = self.run_mutated_valid(mutate)
        self.assert_rejected(result, "[transformation_chain]")
        self.assertIn("does not connect to the output of transformation_history[0]", result.stdout)


class NonDestructiveTests(unittest.TestCase):
    def test_validator_does_not_modify_fixtures_or_manifests(self) -> None:
        before = snapshot_fixture_tree()

        run_validator(FIXTURES_DIR / "valid" / "manifest.json", FIXTURES_DIR / "valid")
        for case_name in INVALID_FIXTURES:
            case_dir = FIXTURES_DIR / case_name
            run_validator(case_dir / "manifest.json", case_dir)

        after = snapshot_fixture_tree()
        self.assertEqual(before, after, "validator run changed fixture or manifest bytes/mtimes")

    def test_validator_source_never_writes_files(self) -> None:
        source = VALIDATOR.read_text(encoding="utf-8")
        for forbidden in ("open(", "write_text", "write_bytes", "os.remove", "shutil.", "Path.rename"):
            if forbidden == "open(":
                # Only the read-only call sites are expected; every open() in the
                # validator must be opened for reading, never writing.
                for line in source.splitlines():
                    if "open(" in line:
                        self.assertNotIn('"w"', line)
                        self.assertNotIn("'w'", line)
                        self.assertNotIn('"a"', line)
                        self.assertNotIn("'a'", line)
                continue
            self.assertNotIn(forbidden, source, msg=f"validator source unexpectedly references {forbidden!r}")


class UsageErrorTests(unittest.TestCase):
    def test_missing_root_directory_is_a_usage_error_not_a_silent_pass(self) -> None:
        case_dir = FIXTURES_DIR / "valid"
        result = run_validator(case_dir / "manifest.json", FIXTURES_DIR / "does-not-exist")
        self.assertEqual(result.returncode, 2)

    def test_unparseable_manifest_is_a_usage_error_not_a_silent_pass(self) -> None:
        result = run_validator(FIXTURES_DIR / "valid" / "fixture.txt", FIXTURES_DIR / "valid")
        self.assertEqual(result.returncode, 2)


class SchemaAlignmentTests(unittest.TestCase):
    """Confirm docs/promotion-manifest.schema.json stays aligned with validator policy."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.validator_source = VALIDATOR.read_text(encoding="utf-8")

    def test_schema_required_fields_match_validator_required_fields(self) -> None:
        schema_required = set(self.schema["required"])
        # Mirrors the `required_fields` tuple in validate_top_level_fields().
        validator_required = {
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
        }
        self.assertEqual(schema_required, validator_required)

    def test_schema_rejects_unknown_fields_and_matches_license_policy(self) -> None:
        properties = self.schema["properties"]
        self.assertFalse(self.schema["additionalProperties"])
        self.assertFalse(properties["redistribution"]["additionalProperties"])
        self.assertFalse(properties["content_classification_flags"]["additionalProperties"])
        self.assertFalse(properties["files"]["items"]["additionalProperties"])
        self.assertFalse(properties["transformation_history"]["items"]["additionalProperties"])
        self.assertEqual(properties["source_url"]["pattern"], "^https?://")
        transformation_item = properties["transformation_history"]["items"]
        self.assertIn(
            {"anyOf": [{"required": ["input_ref"]}, {"required": ["input_sha256"]}]},
            transformation_item["allOf"],
        )
        self.assertIn(
            {"anyOf": [{"required": ["output_ref"]}, {"required": ["output_sha256"]}]},
            transformation_item["allOf"],
        )
        self.assertEqual(
            set(properties["license"]["enum"]),
            {
                "CC0-1.0",
                "CC-BY-4.0",
                "CC-BY-SA-4.0",
                "MIT",
                "Apache-2.0",
                "Public-Domain",
                "Synthetic-No-License-Required",
            },
        )
    def test_schema_enumerations_match_validator_allowlists(self) -> None:
        properties = self.schema["properties"]
        self.assertEqual(
            set(properties["source_classification"]["enum"]),
            {"synthetic", "public_licensed"},
        )
        self.assertEqual(
            set(properties["license_review_state"]["enum"]),
            {"not_reviewed", "pending", "approved", "rejected"},
        )
        self.assertEqual(
            set(properties["origin_review_state"]["enum"]),
            {"unverified", "uncertain", "approved", "rejected"},
        )
        self.assertEqual(
            set(properties["identifier_safety_state"]["enum"]),
            {"no_real_identifiers", "contains_real_identifiers", "uncertain"},
        )
        self.assertEqual(
            set(properties["eligibility_state"]["enum"]),
            {"pending_review", "quarantine", "eligible_for_promotion", "rejected"},
        )

    def test_schema_reference_pattern_matches_validator_reference_safety_rules(self) -> None:
        transformation_item = self.schema["properties"]["transformation_history"]["items"]
        input_pattern = transformation_item["properties"]["input_ref"]["pattern"]
        output_pattern = transformation_item["properties"]["output_ref"]["pattern"]
        self.assertEqual(input_pattern, output_pattern)

        compiled = re.compile(input_pattern)
        accepted = ("fixture.txt", "sub/dir/example-file.txt", "name-with-dots..txt", "intermediate.bin")
        rejected = (
            "",
            "   ",
            "/etc/passwd",
            "../secret.txt",
            "a/../b",
            r"C:\Users\example\secret.txt",
            r"\\host\share\file.txt",
            "~/private.txt",
            "$HOME/file.txt",
            "%APPDATA%\\file.txt",
            "file:///etc/passwd",
            "a\tb",
        )
        for value in accepted:
            with self.subTest(value=value, expect="accept"):
                self.assertTrue(compiled.match(value), msg=value)
        for value in rejected:
            with self.subTest(value=value, expect="reject"):
                self.assertFalse(compiled.match(value), msg=value)


if __name__ == "__main__":
    unittest.main()
