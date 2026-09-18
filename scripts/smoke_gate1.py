#!/usr/bin/env python3
"""Gate 1 smoke: named fork utterance → Jev picks the fork, not the vague trap."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from smoke_common import ASK, ENV_KEY, build_pick_payload, call_jev, pick_choice

EXPECTED_PICK = "fork"

SCENARIO = {
    "utterance": (
        "I want to migrate checkout sessions to Redis. Sync or async writes?"
    ),
    "candidates": [
        {"id": "fork", "text": "Sync or async session writes?"},
        {"id": "vague", "text": "What should we decide?"},
        {"id": "context", "text": "What do you need to understand about Render first?"},
    ],
}


def dry_run_report() -> dict[str, Any]:
    return {
        "gate": 1,
        "mode": "dry-run",
        "utterance": SCENARIO["utterance"],
        "candidates": SCENARIO["candidates"],
        "expected_pick": EXPECTED_PICK,
        "assertion": "pick_next.choice must be the fork candidate, not vague",
        "live_command": (
            "TYPESAFE_API_KEY=... python3 scripts/smoke_gate1.py --live "
            "(calls ask.py via uv run)"
        ),
        "ask_command": (
            "uv run --isolated --no-project --with typesafe-sdk==0.6.0 "
            f"python3 {ASK}  # stdin: build_payload() JSON"
        ),
    }


def evaluate(body: dict[str, Any]) -> dict[str, Any]:
    pick_block = body.get("answers", {}).get("pick_next", {})
    choice = pick_choice(body)
    passed = choice == EXPECTED_PICK
    return {
        "gate": 1,
        "mode": "live",
        "utterance": SCENARIO["utterance"],
        "candidates": SCENARIO["candidates"],
        "expected_pick": EXPECTED_PICK,
        "actual_pick": choice,
        "confidence": pick_block.get("confidence"),
        "probabilities": pick_block.get("probabilities"),
        "model": body.get("model"),
        "passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate 1 fork-pick smoke")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Call Jev (requires TYPESAFE_API_KEY)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print scenario and expected winner only",
    )
    args = parser.parse_args()

    if args.dry_run or not args.live:
        report = dry_run_report()
        if not os.environ.get(ENV_KEY):
            report["status"] = "skipped"
            report["reason"] = f"{ENV_KEY} not set; live smoke not run"
            json.dump(report, sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
            return 0
        if not args.live:
            report["status"] = "dry-run-only"
            report["reason"] = "Pass --live to call Jev"
            json.dump(report, sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
            return 0

    if not os.environ.get(ENV_KEY):
        report = dry_run_report()
        report["status"] = "skipped"
        report["reason"] = f"{ENV_KEY} not set"
        json.dump(report, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    try:
        body = call_jev(
            build_pick_payload(SCENARIO["utterance"], SCENARIO["candidates"])
        )
        report = evaluate(body)
    except RuntimeError as exc:
        json.dump(
            {
                "gate": 1,
                "mode": "live",
                "status": "error",
                "error": str(exc),
                "expected_pick": EXPECTED_PICK,
            },
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 1

    report["status"] = "passed" if report["passed"] else "failed"
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
