#!/usr/bin/env python3
"""Check that documented module refs identify a real or next release."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = "modules/gemini-managed-agents"
REF_PATTERN = re.compile(
    r"github\.com/selamy-labs/terraform-modules\.git//modules/gemini-managed-agents\?ref=(v[0-9]+\.[0-9]+\.[0-9]+)"
)
VERSION_PATTERN = re.compile(r"^v([0-9]+)\.([0-9]+)\.([0-9]+)$")


def version(value: str) -> tuple[int, int, int]:
    match = VERSION_PATTERN.fullmatch(value)
    if match is None:
        raise SystemExit(f"invalid semantic-version tag: {value}")
    return tuple(int(part) for part in match.groups())


def git(*arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(ROOT), *arguments],
        check=check,
        text=True,
        capture_output=True,
    )


def main() -> None:
    paths = [
        ROOT / MODULE_PATH / "README.md",
        ROOT / MODULE_PATH / "examples" / "minimal" / "main.tf",
        ROOT / MODULE_PATH / "examples" / "complete" / "main.tf",
    ]
    refs = []
    for path in paths:
        matches = REF_PATTERN.findall(path.read_text(encoding="utf-8"))
        if len(matches) != 1:
            raise SystemExit(f"{path}: expected one pinned managed-agent release ref")
        refs.extend(matches)
    if len(set(refs)) != 1:
        raise SystemExit(f"managed-agent examples disagree on release ref: {sorted(set(refs))}")
    target = refs[0]

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    heading = re.search(r"(?m)^## \[(v[0-9]+\.[0-9]+\.[0-9]+)\]", changelog)
    if heading is None or heading.group(1) != target:
        raise SystemExit(f"top changelog release must be {target}")

    tag_exists = git("rev-parse", "--verify", "--quiet", f"refs/tags/{target}", check=False).returncode == 0
    if tag_exists:
        if git("cat-file", "-e", f"{target}:{MODULE_PATH}", check=False).returncode != 0:
            raise SystemExit(f"{target} exists but does not contain {MODULE_PATH}")
    else:
        tags = [line for line in git("tag", "--list", "v[0-9]*").stdout.splitlines() if VERSION_PATTERN.fullmatch(line)]
        if tags and version(target) <= max(version(tag) for tag in tags):
            raise SystemExit(f"unreleased ref {target} must be newer than every existing release")

    print(f"managed-agent release ref {target} is consistent")


if __name__ == "__main__":
    main()
