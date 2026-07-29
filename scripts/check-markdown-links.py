#!/usr/bin/env python3

"""Fail when a repository-relative Markdown link points to a missing path."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def main() -> int:
    failures: list[str] = []

    for document in sorted(ROOT.rglob("*.md")):
        if ".git" in document.parts:
            continue

        for raw_target in LINK_PATTERN.findall(document.read_text(encoding="utf-8")):
            target = raw_target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith(("mailto:", "#")):
                continue

            candidate = (document.parent / target).resolve()
            if not candidate.exists():
                failures.append(f"{document.relative_to(ROOT)}: {target}")

    if failures:
        print("Missing repository-relative Markdown targets:")
        print("\n".join(failures))
        return 1

    print("All repository-relative Markdown links resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
