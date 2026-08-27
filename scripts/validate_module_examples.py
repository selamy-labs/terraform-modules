#!/usr/bin/env python3
"""Validate checked-in examples against the module in the current checkout."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "modules" / "gemini-managed-agents"
SOURCE_PATTERN = re.compile(
    r'(?m)^(\s*source\s*=\s*)"git::https://github\.com/selamy-labs/terraform-modules\.git//modules/gemini-managed-agents\?ref=v[0-9]+\.[0-9]+\.[0-9]+"$'
)


def run_example(example: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="managed-agent-example-") as directory:
        copied = Path(directory) / example.name
        shutil.copytree(example, copied)
        main = copied / "main.tf"
        source = main.read_text(encoding="utf-8")
        rewritten, count = SOURCE_PATTERN.subn(rf'\1"{MODULE.as_posix()}"', source)
        if count != 1:
            raise SystemExit(f"{example}: expected exactly one pinned module source, found {count}")
        main.write_text(rewritten, encoding="utf-8")
        for arguments in (
            ["tofu", "init", "-backend=false", "-input=false"],
            ["tofu", "validate"],
        ):
            subprocess.run(arguments, cwd=copied, check=True)


def main() -> None:
    examples = sorted(path for path in (MODULE / "examples").iterdir() if path.is_dir())
    if not examples:
        raise SystemExit("no managed-agent examples found")
    for example in examples:
        run_example(example)
    print(f"validated {len(examples)} managed-agent examples")


if __name__ == "__main__":
    main()
