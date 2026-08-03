#!/usr/bin/env python3

"""Fail-closed controller for the planned NAS-to-pi-server local second copy.

The controller implements the public-safe, repository-controlled portion of
Decision D23. Runtime paths and credentials are supplied outside Git. It never
mounts a share, initializes a Restic repository, creates credentials, prunes
snapshots, or removes source data.

The ``backup`` command requires an already-mounted read-only CIFS source and an
already-initialized local Restic repository. It updates the success timestamp
only after the Restic snapshot, a repository check, and post-run capacity and
mount checks all succeed. The ``stale-check`` command exits nonzero if that
timestamp is missing, malformed, in the future, or older than the configured
threshold.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator, Mapping, Sequence

GIB = 1024**3
DEFAULT_REPOSITORY_CEILING_BYTES = 256 * GIB
DEFAULT_REPOSITORY_WARNING_BYTES = 192 * GIB
DEFAULT_FREE_SPACE_RESERVE_BYTES = 512 * GIB
DEFAULT_CAPACITY_SAFETY_MARGIN_BYTES = GIB
DEFAULT_STALE_AFTER_SECONDS = 36 * 60 * 60
MAX_FUTURE_SKEW_SECONDS = 5 * 60
NETWORK_FILESYSTEMS = {"cifs", "nfs", "nfs4", "fuse.sshfs"}


class ControlFailure(RuntimeError):
    """A public-safe, expected control failure."""


@dataclass(frozen=True)
class BackupConfig:
    source: Path
    repository: Path
    password_file: Path
    success_stamp: Path
    lock_file: Path
    repository_ceiling_bytes: int = DEFAULT_REPOSITORY_CEILING_BYTES
    repository_warning_bytes: int = DEFAULT_REPOSITORY_WARNING_BYTES
    free_space_reserve_bytes: int = DEFAULT_FREE_SPACE_RESERVE_BYTES
    capacity_safety_margin_bytes: int = DEFAULT_CAPACITY_SAFETY_MARGIN_BYTES


CommandRunner = Callable[..., subprocess.CompletedProcess[str]]
SizeReader = Callable[[Path], int]
FreeSpaceReader = Callable[[Path], int]


def run_command(args: Sequence[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
    """Run one command without ever enabling ``check=True``."""
    return subprocess.run(list(args), check=False, text=True, **kwargs)  # noqa: S603


def require_absolute_path(environment: Mapping[str, str], variable: str) -> Path:
    raw_value = environment.get(variable, "")
    if not raw_value:
        raise ControlFailure(f"required environment variable {variable} is missing")
    path = Path(raw_value)
    if not path.is_absolute():
        raise ControlFailure(f"{variable} must contain an absolute path")
    return path


def positive_integer(
    environment: Mapping[str, str], variable: str, default: int
) -> int:
    raw_value = environment.get(variable)
    if raw_value is None or raw_value == "":
        return default
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ControlFailure(f"{variable} must be a positive integer") from exc
    if value <= 0:
        raise ControlFailure(f"{variable} must be a positive integer")
    return value


def load_backup_config(environment: Mapping[str, str]) -> BackupConfig:
    config = BackupConfig(
        source=require_absolute_path(environment, "HOME_LAB_BACKUP_SOURCE"),
        repository=require_absolute_path(environment, "RESTIC_REPOSITORY"),
        password_file=require_absolute_path(environment, "RESTIC_PASSWORD_FILE"),
        success_stamp=require_absolute_path(environment, "HOME_LAB_BACKUP_SUCCESS_STAMP"),
        lock_file=require_absolute_path(environment, "HOME_LAB_BACKUP_LOCK_FILE"),
        repository_ceiling_bytes=positive_integer(
            environment,
            "HOME_LAB_REPOSITORY_CEILING_BYTES",
            DEFAULT_REPOSITORY_CEILING_BYTES,
        ),
        repository_warning_bytes=positive_integer(
            environment,
            "HOME_LAB_REPOSITORY_WARNING_BYTES",
            DEFAULT_REPOSITORY_WARNING_BYTES,
        ),
        free_space_reserve_bytes=positive_integer(
            environment,
            "HOME_LAB_FREE_SPACE_RESERVE_BYTES",
            DEFAULT_FREE_SPACE_RESERVE_BYTES,
        ),
    )
    if config.repository_warning_bytes >= config.repository_ceiling_bytes:
        raise ControlFailure(
            "HOME_LAB_REPOSITORY_WARNING_BYTES must be lower than the repository ceiling"
        )
    return config


def load_stale_config(environment: Mapping[str, str]) -> tuple[Path, int]:
    return (
        require_absolute_path(environment, "HOME_LAB_BACKUP_SUCCESS_STAMP"),
        positive_integer(
            environment,
            "HOME_LAB_STALE_AFTER_SECONDS",
            DEFAULT_STALE_AFTER_SECONDS,
        ),
    )


def validate_runtime_paths(config: BackupConfig) -> None:
    if not config.source.is_dir():
        raise ControlFailure("the configured backup source is unavailable")
    if not config.repository.is_dir():
        raise ControlFailure("the configured Restic repository directory is unavailable")
    if not (config.repository / "config").is_file():
        raise ControlFailure("the configured Restic repository is not initialized")
    if not config.password_file.is_file():
        raise ControlFailure("the Restic password credential is unavailable")
    if not config.success_stamp.parent.is_dir():
        raise ControlFailure("the success-timestamp directory is unavailable")
    if not config.lock_file.parent.is_dir():
        raise ControlFailure("the backup lock directory is unavailable")

    password_mode = stat.S_IMODE(config.password_file.stat().st_mode)
    if password_mode & 0o077:
        raise ControlFailure("the Restic password credential permissions are too broad")

    source = config.source.resolve()
    repository = config.repository.resolve()
    if source == Path("/") or repository == Path("/"):
        raise ControlFailure("the filesystem root cannot be used as a source or repository")
    if source == repository or source.is_relative_to(repository) or repository.is_relative_to(source):
        raise ControlFailure("the source and Restic repository must not overlap")


def find_mount(
    target: Path, runner: CommandRunner = run_command
) -> tuple[str, set[str]]:
    result = runner(
        ["findmnt", "--json", "--target", str(target), "--output", "FSTYPE,OPTIONS"],
        capture_output=True,
    )
    if result.returncode != 0:
        raise ControlFailure("could not verify the required filesystem mount")
    try:
        payload = json.loads(result.stdout)
        filesystems = payload["filesystems"]
        filesystem = filesystems[0]
        fstype = filesystem["fstype"]
        raw_options = filesystem["options"]
    except (IndexError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ControlFailure("could not parse the filesystem mount state") from exc

    if not isinstance(fstype, str):
        raise ControlFailure("the filesystem mount type is invalid")
    if isinstance(raw_options, str):
        options = {option.strip() for option in raw_options.split(",") if option.strip()}
    elif isinstance(raw_options, list) and all(isinstance(item, str) for item in raw_options):
        options = set(raw_options)
    else:
        raise ControlFailure("the filesystem mount options are invalid")
    return fstype.lower(), options


def verify_mount_policy(config: BackupConfig, runner: CommandRunner = run_command) -> None:
    source_fstype, source_options = find_mount(config.source, runner)
    if source_fstype != "cifs":
        raise ControlFailure("the backup source is not mounted through CIFS")
    if "ro" not in source_options or "rw" in source_options:
        raise ControlFailure("the CIFS backup source is not read-only")

    repository_fstype, _ = find_mount(config.repository, runner)
    if repository_fstype in NETWORK_FILESYSTEMS:
        raise ControlFailure("the Restic repository must use local storage")


def directory_size_bytes(path: Path, runner: CommandRunner = run_command) -> int:
    result = runner(
        ["du", "--bytes", "--summarize", "--one-file-system", str(path)],
        capture_output=True,
    )
    if result.returncode != 0:
        raise ControlFailure("could not measure backup capacity safely")
    try:
        value = int(result.stdout.split(maxsplit=1)[0])
    except (IndexError, ValueError) as exc:
        raise ControlFailure("could not parse the measured backup capacity") from exc
    if value < 0:
        raise ControlFailure("the measured backup capacity is invalid")
    return value


def free_space_bytes(path: Path) -> int:
    return shutil.disk_usage(path).free


def evaluate_capacity(
    config: BackupConfig,
    repository_size: int,
    source_size: int,
    free_space: int,
) -> bool:
    """Validate conservative capacity gates and return warning-state status."""
    if repository_size > config.repository_ceiling_bytes:
        raise ControlFailure("the Restic repository already exceeds its hard ceiling")
    if (
        repository_size + source_size + config.capacity_safety_margin_bytes
        > config.repository_ceiling_bytes
    ):
        raise ControlFailure("the worst-case next snapshot would exceed the repository ceiling")
    if free_space < config.free_space_reserve_bytes:
        raise ControlFailure("available storage is below the required free-space reserve")
    if (
        free_space - source_size - config.capacity_safety_margin_bytes
        < config.free_space_reserve_bytes
    ):
        raise ControlFailure("the worst-case next snapshot would breach the free-space reserve")
    return repository_size >= config.repository_warning_bytes


def run_preflight(
    config: BackupConfig,
    runner: CommandRunner = run_command,
    size_reader: SizeReader | None = None,
    free_reader: FreeSpaceReader = free_space_bytes,
) -> bool:
    validate_runtime_paths(config)
    verify_mount_policy(config, runner)
    measure = size_reader or (lambda path: directory_size_bytes(path, runner))
    return evaluate_capacity(
        config,
        repository_size=measure(config.repository),
        source_size=measure(config.source),
        free_space=free_reader(config.repository),
    )


@contextmanager
def exclusive_lock(lock_file: Path) -> Iterator[None]:
    try:
        with lock_file.open("a", encoding="utf-8") as handle:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ControlFailure("another local second-copy job is already running") from exc
            yield
    except OSError as exc:
        raise ControlFailure("could not acquire the local second-copy lock") from exc


def run_restic_quietly(
    command: Sequence[str],
    config: BackupConfig,
    runner: CommandRunner = run_command,
) -> None:
    restic_environment = os.environ.copy()
    restic_environment["RESTIC_REPOSITORY"] = str(config.repository)
    restic_environment["RESTIC_PASSWORD_FILE"] = str(config.password_file)
    result = runner(
        ["restic", "--quiet", *command],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=restic_environment,
    )
    if result.returncode != 0:
        action = "snapshot" if command and command[0] == "backup" else "integrity check"
        raise ControlFailure(f"the Restic {action} failed")


def write_success_stamp(stamp: Path, epoch: int) -> None:
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=stamp.parent,
            prefix=f".{stamp.name}.",
            delete=False,
        ) as handle:
            temporary_name = handle.name
            handle.write(f"{epoch}\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary_name, 0o600)
        os.replace(temporary_name, stamp)
    except OSError as exc:
        raise ControlFailure("could not update the successful-backup timestamp") from exc
    finally:
        if temporary_name is not None:
            try:
                Path(temporary_name).unlink(missing_ok=True)
            except OSError:
                pass


def run_backup(
    config: BackupConfig,
    runner: CommandRunner = run_command,
    size_reader: SizeReader | None = None,
    free_reader: FreeSpaceReader = free_space_bytes,
    now: Callable[[], float] = time.time,
) -> bool:
    """Run one guarded snapshot; return whether the warning threshold was reached."""
    with exclusive_lock(config.lock_file):
        warning = run_preflight(config, runner, size_reader, free_reader)
        run_restic_quietly(
            ["backup", "--one-file-system", "--tag", "home-lab-local-second-copy", str(config.source)],
            config,
            runner,
        )

        # A disappearing mount can reveal the empty mount-point directory. Do
        # not call that a success even if Restic itself exited zero.
        verify_mount_policy(config, runner)
        run_restic_quietly(["check"], config, runner)

        measure = size_reader or (lambda path: directory_size_bytes(path, runner))
        repository_size = measure(config.repository)
        free_space = free_reader(config.repository)
        if repository_size > config.repository_ceiling_bytes:
            raise ControlFailure("the Restic repository exceeded its hard ceiling after the snapshot")
        if free_space < config.free_space_reserve_bytes:
            raise ControlFailure("available storage breached the reserve after the snapshot")

        write_success_stamp(config.success_stamp, int(now()))
        return warning or repository_size >= config.repository_warning_bytes


def check_staleness(stamp: Path, stale_after_seconds: int, now_epoch: int) -> int:
    try:
        raw_value = stamp.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ControlFailure("the successful-backup timestamp is missing or unreadable") from exc
    try:
        success_epoch = int(raw_value)
    except ValueError as exc:
        raise ControlFailure("the successful-backup timestamp is malformed") from exc
    if success_epoch <= 0:
        raise ControlFailure("the successful-backup timestamp is malformed")
    if success_epoch > now_epoch + MAX_FUTURE_SKEW_SECONDS:
        raise ControlFailure("the successful-backup timestamp is unexpectedly in the future")
    age = max(0, now_epoch - success_epoch)
    if age > stale_after_seconds:
        raise ControlFailure("the local second copy is stale")
    return age


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fail-closed controls for the D23 local second copy."
    )
    parser.add_argument(
        "command",
        choices=("preflight", "backup", "stale-check"),
        help="validate controls, run one snapshot, or verify the last-success timestamp",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "stale-check":
            stamp, threshold = load_stale_config(os.environ)
            age = check_staleness(stamp, threshold, int(time.time()))
            print(f"OK: local second copy is fresh ({age} seconds since verified success)")
            return 0

        config = load_backup_config(os.environ)
        if args.command == "preflight":
            warning = run_preflight(config)
            print("OK: local second-copy preflight passed")
        else:
            warning = run_backup(config)
            print("OK: local second-copy snapshot and repository check passed")
        if warning:
            print("WARNING: the Restic repository has reached its configured warning threshold")
        return 0
    except ControlFailure as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    except Exception:
        # Do not leak command output, runtime paths, or credential details from
        # an unexpected exception into the service journal.
        print("FAILED: unexpected local second-copy controller error", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
