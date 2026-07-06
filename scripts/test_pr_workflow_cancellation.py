#!/usr/bin/env python3
from pathlib import Path


WORKFLOW_DIR = Path(__file__).resolve().parents[1] / ".github" / "workflows"
EXPECTED_CANCEL = "cancel-in-progress: ${{ github.event_name == 'pull_request' }}"
EXPECTED_GROUP_FALLBACK = "${{ github.event.pull_request.number || github.ref }}"


def main() -> int:
    missing: list[str] = []
    workflows = sorted(WORKFLOW_DIR.glob("*.yml")) + sorted(WORKFLOW_DIR.glob("*.yaml"))

    for workflow in workflows:
        text = workflow.read_text(encoding="utf-8")
        if "pull_request:" not in text:
            continue
        if "concurrency:" not in text:
            missing.append(f"{workflow.name}: missing concurrency block")
            continue
        if EXPECTED_GROUP_FALLBACK not in text:
            missing.append(f"{workflow.name}: concurrency group does not fall back to github.ref")
        if EXPECTED_CANCEL not in text:
            missing.append(f"{workflow.name}: does not limit cancellation to pull_request runs")

    if missing:
        for issue in missing:
            print(issue)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
