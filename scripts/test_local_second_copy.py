#!/usr/bin/env python3

"""Synthetic, non-mutating tests for the D23 local second-copy controller."""

from __future__ import annotations

import fcntl
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTROLLER_PATH = REPO_ROOT / "scripts" / "local_second_copy.py"

SPEC = importlib.util.spec_from_file_location("local_second_copy", CONTROLLER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load local_second_copy.py")
controller = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = controller
SPEC.loader.exec_module(controller)


class FakeRunner:
    def __init__(self, source: Path, repository: Path) -> None:
        self.source = source
        self.repository = repository
        self.source_fstype = "cifs"
        self.source_options = "ro,nosuid,nodev,noexec"
        self.repository_fstype = "ext4"
        self.restic_results = {"backup": 0, "check": 0}
        self.commands: list[list[str]] = []

    def __call__(self, args, **kwargs) -> subprocess.CompletedProcess[str]:
        command = list(args)
        self.commands.append(command)
        if command[0] == "findmnt":
            target = Path(command[command.index("--target") + 1])
            if target == self.source:
                fstype = self.source_fstype
                options = self.source_options
            else:
                fstype = self.repository_fstype
                options = "rw,relatime"
            output = json.dumps(
                {"filesystems": [{"fstype": fstype, "options": options}]}
            )
            return subprocess.CompletedProcess(command, 0, stdout=output, stderr="")
        if command[0] == "restic":
            action = command[2]
            return subprocess.CompletedProcess(
                command,
                self.restic_results[action],
                stdout="private runtime path must never be surfaced",
                stderr="private credential detail must never be surfaced",
            )
        raise AssertionError(f"unexpected command: {command[0]}")

    def restic_actions(self) -> list[str]:
        return [command[2] for command in self.commands if command[0] == "restic"]


class ControllerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="local-second-copy-test-")
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.repository = self.root / "repository"
        self.state = self.root / "state"
        self.runtime = self.root / "runtime"
        for directory in (self.source, self.repository, self.state, self.runtime):
            directory.mkdir()
        (self.repository / "config").write_text("synthetic restic config\n", encoding="utf-8")
        self.password_file = self.root / "restic-password"
        self.password_file.write_text("synthetic-only-secret\n", encoding="utf-8")
        self.password_file.chmod(0o600)
        self.stamp = self.state / "last-success"
        self.lock = self.runtime / "backup.lock"
        self.config = controller.BackupConfig(
            source=self.source,
            repository=self.repository,
            password_file=self.password_file,
            success_stamp=self.stamp,
            lock_file=self.lock,
            repository_ceiling_bytes=1_000,
            repository_warning_bytes=700,
            free_space_reserve_bytes=2_000,
            capacity_safety_margin_bytes=25,
        )
        self.runner = FakeRunner(self.source, self.repository)
        self.sizes = {self.source: 100, self.repository: 200}

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def size_reader(self, path: Path) -> int:
        return self.sizes[path]

    @staticmethod
    def free_reader(_path: Path) -> int:
        return 10_000

    def run_backup(self, now: int = 1_000) -> bool:
        return controller.run_backup(
            self.config,
            runner=self.runner,
            size_reader=self.size_reader,
            free_reader=self.free_reader,
            now=lambda: now,
        )


class BackupSuccessTests(ControllerTestCase):
    def test_success_runs_snapshot_then_check_and_atomically_updates_stamp(self) -> None:
        warning = self.run_backup(now=12_345)
        self.assertFalse(warning)
        self.assertEqual(self.runner.restic_actions(), ["backup", "check"])
        self.assertEqual(self.stamp.read_text(encoding="utf-8"), "12345\n")
        self.assertEqual(self.stamp.stat().st_mode & 0o777, 0o600)

    def test_warning_threshold_does_not_claim_a_hard_failure(self) -> None:
        self.sizes[self.repository] = 700
        self.assertTrue(self.run_backup())
        self.assertTrue(self.stamp.exists())


class FailClosedBackupTests(ControllerTestCase):
    def test_read_write_source_mount_is_rejected_before_restic(self) -> None:
        self.runner.source_options = "rw,nosuid,nodev,noexec"
        with self.assertRaisesRegex(controller.ControlFailure, "not read-only"):
            self.run_backup()
        self.assertEqual(self.runner.restic_actions(), [])
        self.assertFalse(self.stamp.exists())

    def test_non_cifs_source_is_rejected_before_restic(self) -> None:
        self.runner.source_fstype = "ext4"
        with self.assertRaisesRegex(controller.ControlFailure, "not mounted through CIFS"):
            self.run_backup()
        self.assertEqual(self.runner.restic_actions(), [])

    def test_network_repository_is_rejected_before_restic(self) -> None:
        self.runner.repository_fstype = "nfs4"
        with self.assertRaisesRegex(controller.ControlFailure, "local storage"):
            self.run_backup()
        self.assertEqual(self.runner.restic_actions(), [])

    def test_projected_repository_ceiling_refuses_snapshot(self) -> None:
        self.sizes[self.repository] = 950
        with self.assertRaisesRegex(controller.ControlFailure, "would exceed"):
            self.run_backup()
        self.assertEqual(self.runner.restic_actions(), [])

    def test_projected_free_space_reserve_refuses_snapshot(self) -> None:
        with self.assertRaisesRegex(controller.ControlFailure, "would breach"):
            controller.run_backup(
                self.config,
                runner=self.runner,
                size_reader=self.size_reader,
                free_reader=lambda _path: 2_050,
                now=lambda: 1_000,
            )
        self.assertEqual(self.runner.restic_actions(), [])

    def test_snapshot_failure_preserves_previous_success_stamp(self) -> None:
        self.stamp.write_text("777\n", encoding="utf-8")
        self.runner.restic_results["backup"] = 3
        with self.assertRaisesRegex(controller.ControlFailure, "snapshot failed") as raised:
            self.run_backup()
        self.assertEqual(self.stamp.read_text(encoding="utf-8"), "777\n")
        self.assertNotIn(str(self.source), str(raised.exception))
        self.assertNotIn("credential", str(raised.exception))

    def test_integrity_check_failure_preserves_previous_success_stamp(self) -> None:
        self.stamp.write_text("888\n", encoding="utf-8")
        self.runner.restic_results["check"] = 1
        with self.assertRaisesRegex(controller.ControlFailure, "integrity check failed"):
            self.run_backup()
        self.assertEqual(self.stamp.read_text(encoding="utf-8"), "888\n")
        self.assertEqual(self.runner.restic_actions(), ["backup", "check"])

    def test_post_snapshot_ceiling_breach_preserves_previous_success_stamp(self) -> None:
        self.stamp.write_text("889\n", encoding="utf-8")
        repository_measurements = iter((200, 1_001))

        def changing_size_reader(path: Path) -> int:
            if path == self.repository:
                return next(repository_measurements)
            return self.sizes[path]

        with self.assertRaisesRegex(controller.ControlFailure, "exceeded its hard ceiling"):
            controller.run_backup(
                self.config,
                runner=self.runner,
                size_reader=changing_size_reader,
                free_reader=self.free_reader,
                now=lambda: 1_000,
            )
        self.assertEqual(self.stamp.read_text(encoding="utf-8"), "889\n")
        self.assertEqual(self.runner.restic_actions(), ["backup", "check"])

    def test_post_snapshot_reserve_breach_preserves_previous_success_stamp(self) -> None:
        self.stamp.write_text("890\n", encoding="utf-8")
        free_measurements = iter((10_000, 1_999))
        with self.assertRaisesRegex(controller.ControlFailure, "breached the reserve"):
            controller.run_backup(
                self.config,
                runner=self.runner,
                size_reader=self.size_reader,
                free_reader=lambda _path: next(free_measurements),
                now=lambda: 1_000,
            )
        self.assertEqual(self.stamp.read_text(encoding="utf-8"), "890\n")
        self.assertEqual(self.runner.restic_actions(), ["backup", "check"])

    def test_disappearing_source_mount_after_snapshot_never_updates_stamp(self) -> None:
        original_call = self.runner.__call__
        source_probes = 0

        def changing_runner(args, **kwargs):
            nonlocal source_probes
            command = list(args)
            if command[0] == "findmnt":
                target = Path(command[command.index("--target") + 1])
                if target == self.source:
                    source_probes += 1
                    if source_probes == 2:
                        self.runner.source_fstype = "ext4"
            return original_call(args, **kwargs)

        with self.assertRaisesRegex(controller.ControlFailure, "not mounted through CIFS"):
            controller.run_backup(
                self.config,
                runner=changing_runner,
                size_reader=self.size_reader,
                free_reader=self.free_reader,
                now=lambda: 1_000,
            )
        self.assertFalse(self.stamp.exists())
        self.assertEqual(self.runner.restic_actions(), ["backup"])

    def test_password_file_with_group_access_is_rejected(self) -> None:
        self.password_file.chmod(0o640)
        with self.assertRaisesRegex(controller.ControlFailure, "permissions are too broad"):
            self.run_backup()
        self.assertEqual(self.runner.restic_actions(), [])

    def test_source_and_repository_cannot_overlap(self) -> None:
        overlapping = controller.BackupConfig(
            source=self.repository,
            repository=self.repository,
            password_file=self.password_file,
            success_stamp=self.stamp,
            lock_file=self.lock,
            repository_ceiling_bytes=1_000,
            repository_warning_bytes=700,
            free_space_reserve_bytes=2_000,
            capacity_safety_margin_bytes=25,
        )
        with self.assertRaisesRegex(controller.ControlFailure, "must not overlap"):
            controller.validate_runtime_paths(overlapping)

    def test_concurrent_run_is_rejected_without_restic_or_stamp_update(self) -> None:
        with self.lock.open("a", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(controller.ControlFailure, "already running"):
                self.run_backup()
        self.assertEqual(self.runner.restic_actions(), [])
        self.assertFalse(self.stamp.exists())


class StaleStateTests(ControllerTestCase):
    def test_fresh_timestamp_passes(self) -> None:
        self.stamp.write_text("1000\n", encoding="utf-8")
        self.assertEqual(controller.check_staleness(self.stamp, 600, 1_500), 500)

    def test_missing_timestamp_fails(self) -> None:
        with self.assertRaisesRegex(controller.ControlFailure, "missing or unreadable"):
            controller.check_staleness(self.stamp, 600, 1_500)

    def test_stale_timestamp_fails(self) -> None:
        self.stamp.write_text("1000\n", encoding="utf-8")
        with self.assertRaisesRegex(controller.ControlFailure, "is stale"):
            controller.check_staleness(self.stamp, 600, 1_601)

    def test_malformed_or_future_timestamp_fails(self) -> None:
        for value, expected in (("not-an-epoch\n", "malformed"), ("2000\n", "in the future")):
            with self.subTest(value=value.strip()):
                self.stamp.write_text(value, encoding="utf-8")
                with self.assertRaisesRegex(controller.ControlFailure, expected):
                    controller.check_staleness(self.stamp, 600, 1_000)


class UnitTemplateTests(unittest.TestCase):
    def test_templates_preserve_hardening_and_no_pruning_boundary(self) -> None:
        systemd_dir = REPO_ROOT / "systemd"
        backup_service = (systemd_dir / "home-lab-local-backup@.service").read_text(
            encoding="utf-8"
        )
        backup_timer = (systemd_dir / "home-lab-local-backup@.timer").read_text(
            encoding="utf-8"
        )
        stale_service = (systemd_dir / "home-lab-local-backup-stale@.service").read_text(
            encoding="utf-8"
        )
        all_templates = "\n".join(
            path.read_text(encoding="utf-8") for path in systemd_dir.glob("*.service")
        )

        self.assertIn("NoNewPrivileges=yes", backup_service)
        self.assertIn("ProtectSystem=strict", backup_service)
        self.assertIn("LoadCredential=restic-password:", backup_service)
        self.assertIn("OnCalendar=*-*-* 03:30:00 UTC", backup_timer)
        self.assertIn("stale-check", stale_service)
        self.assertNotIn("RESTIC_PASSWORD=", all_templates)
        self.assertNotIn(" forget ", all_templates.lower())
        self.assertNotIn(" prune ", all_templates.lower())


if __name__ == "__main__":
    unittest.main()
