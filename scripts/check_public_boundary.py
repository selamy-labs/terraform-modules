#!/usr/bin/env python3
"""Reject a prohibited adopter token in the current tree or proposed metadata."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


PROHIBITED = bytes((109, 97, 116, 99, 104, 112, 111, 105, 110, 116))
ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", ".terraform", "__pycache__"}


def tree_findings() -> list[str]:
    findings: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if PROHIBITED in relative.as_posix().encode("utf-8").lower():
            findings.append(f"path:{relative.as_posix()}")
        if path.is_file() and PROHIBITED in path.read_bytes().lower():
            findings.append(f"content:{relative.as_posix()}")
    return findings


def git_findings(revision_range: str) -> list[str]:
    result = subprocess.run(
        ["git", "log", "--format=%H%x00%B%x00", revision_range],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    if PROHIBITED not in result.stdout.lower():
        return []
    return [f"git-metadata:{revision_range}"]


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--tree", action="store_true", help="scan current file paths and contents")
    result.add_argument("--git-range", help="scan commit metadata in a proposed revision range")
    result.add_argument("--metadata", action="append", default=[], help="scan a proposed title, body, branch, comment, or release note")
    return result


def main() -> int:
    args = parser().parse_args()
    findings: list[str] = []
    if args.tree:
        findings.extend(tree_findings())
    if args.git_range:
        findings.extend(git_findings(args.git_range))
    for index, value in enumerate(args.metadata):
        if PROHIBITED in value.encode("utf-8").lower():
            findings.append(f"proposed-metadata:{index + 1}")
    if findings:
        print("public-boundary scan failed")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("public-boundary scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
