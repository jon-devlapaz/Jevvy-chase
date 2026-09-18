#!/usr/bin/env python3
"""Gate 2 smoke: dogfood matrix, no blank_lock on forks, no sticky re-ask."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from smoke_common import (
    BLANK_LOCK_IDS,
    ASK,
    build_pick_payload,
    call_jev,
    candidate_text,
    filter_asked,
    has_env_key,
    pick_choice,
)

# One path is enough: pick_next only. Tags label host candidate shaping, not
# a session_kind router (no explore/lock/collect Jev routing maze).
MATRIX: list[dict[str, Any]] = [
    {
        "tag": "named_fork",
        "utterance": (
            "I want to migrate checkout sessions to Redis. Sync or async writes?"
        ),
        "candidates": [
            {"id": "fork", "text": "Sync or async session writes?"},
            {"id": "vague", "text": "What should we decide?"},
            {"id": "context", "text": "What do you need to understand about Render first?"},
        ],
        "expected_pick": "fork",
        "blank_lock_forbidden": True,
    },
    {
        "tag": "named_fork",
        "utterance": "Should we hard-gate the feature flag or use a soft prompt?",
        "candidates": [
            {"id": "fork", "text": "Hard-gate the flag or use a soft prompt?"},
            {"id": "vague", "text": "What should we decide?"},
            {"id": "context", "text": "Who owns feature-flag rollouts today?"},
        ],
        "expected_pick": "fork",
        "blank_lock_forbidden": True,
    },
    {
        "tag": "explore",
        "utterance": (
            "I need to understand our caching options before we commit to one."
        ),
        "candidates": [
            {
                "id": "explore",
                "text": "What do you need to learn about each caching option?",
            },
            {"id": "vague", "text": "What should we decide?"},
            {"id": "lock_trap", "text": "What do we lock first?"},
        ],
        "expected_pick": "explore",
        "blank_lock_forbidden": True,
    },
    {
        "tag": "lock",
        "utterance": (
            "We're going async on session writes. What sequencing do we lock first?"
        ),
        "candidates": [
            {
                "id": "lock",
                "text": "What sequencing or irreversible step do we lock first?",
            },
            {"id": "vague", "text": "What should we decide?"},
            {"id": "explore_trap", "text": "What are all the options again?"},
        ],
        "expected_pick": "lock",
        "blank_lock_forbidden": True,
    },
    {
        "tag": "collect_issues",
        "utterance": "Checkout is flaky in prod. Help me collect what went wrong.",
        "candidates": [
            {"id": "collect", "text": "What broke, where, and what churned?"},
            {"id": "vague", "text": "What should we decide?"},
            {"id": "design_fork", "text": "Sync or async session writes?"},
        ],
        "expected_pick": "collect",
        "blank_lock_forbidden": True,
    },
    {
        "tag": "wish",
        "utterance": "Make checkout faster.",
        "candidates": [
            {"id": "scope", "text": "What part of checkout should get faster first?"},
            {"id": "vague", "text": "What should we decide?"},
            {"id": "meta", "text": "Why are you asking me this?"},
        ],
        "expected_pick": "scope",
        "blank_lock_forbidden": True,
    },
]

REASK_ROW = MATRIX[0]
REASK_TURN2_CANDIDATES = [
    {"id": "follow", "text": "What p99 or crash story matters more?"},
    {"id": "vague", "text": "What should we decide?"},
    {"id": "context", "text": "What do you need to understand about Render first?"},
]
REASK_SIMULATED_ANSWER = "Async. p99 matters more than crash story."


def dry_run_report() -> dict[str, Any]:
    return {
        "gate": 2,
        "mode": "dry-run",
        "routing": "one_path",
        "routing_note": (
            "pick_next only; question-side tags shape host candidates, "
            "no session_kind router"
        ),
        "matrix": [
            {
                "tag": row["tag"],
                "utterance": row["utterance"],
                "expected_pick": row["expected_pick"],
                "blank_lock_forbidden": row["blank_lock_forbidden"],
            }
            for row in MATRIX
        ],
        "reask_check": {
            "tag": REASK_ROW["tag"],
            "turn1_expected": REASK_ROW["expected_pick"],
            "turn2_candidates": REASK_TURN2_CANDIDATES,
            "rule": "filter_asked drops identical candidate text without new state",
        },
        "live_command": (
            "TYPESAFE_API_KEY=... python3 scripts/smoke_gate2.py --live "
            "(calls ask.py via uv run)"
        ),
        "ask_path": str(ASK),
    }


def run_matrix_row(row: dict[str, Any]) -> dict[str, Any]:
    body = call_jev(build_pick_payload(row["utterance"], row["candidates"]))
    choice = pick_choice(body)
    blank_lock = choice in BLANK_LOCK_IDS
    expected = row["expected_pick"]
    passed = choice == expected
    if row["blank_lock_forbidden"] and blank_lock:
        passed = False
    return {
        "tag": row["tag"],
        "utterance": row["utterance"],
        "expected_pick": expected,
        "actual_pick": choice,
        "proposed_text": candidate_text(row["candidates"], choice),
        "blank_lock": blank_lock,
        "probabilities": body.get("answers", {}).get("pick_next", {}).get(
            "probabilities"
        ),
        "passed": passed,
    }


def run_reask_check() -> dict[str, Any]:
    turn1_body = call_jev(
        build_pick_payload(REASK_ROW["utterance"], REASK_ROW["candidates"])
    )
    turn1_choice = pick_choice(turn1_body)
    turn1_text = candidate_text(REASK_ROW["candidates"], turn1_choice)
    asked = {turn1_text} if turn1_text else set()

    turn2_pool = filter_asked(REASK_TURN2_CANDIDATES, asked)
    answers = [
        {
            "id": "q1",
            "question": turn1_text or "",
            "text": REASK_SIMULATED_ANSWER,
        }
    ]
    turn2_body = call_jev(
        build_pick_payload(REASK_ROW["utterance"], turn2_pool, answers=answers)
    )
    turn2_choice = pick_choice(turn2_body)
    turn2_text = candidate_text(turn2_pool, turn2_choice)
    sticky = turn2_text in asked if turn2_text else False

    return {
        "tag": REASK_ROW["tag"],
        "turn1_pick": turn1_choice,
        "turn1_text": turn1_text,
        "turn2_pick": turn2_choice,
        "turn2_text": turn2_text,
        "asked_texts": sorted(asked),
        "sticky_reask": sticky,
        "passed": not sticky and turn1_choice == REASK_ROW["expected_pick"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate 2 dogfood matrix smoke")
    parser.add_argument("--live", action="store_true", help="Call Jev (needs key)")
    parser.add_argument("--dry-run", action="store_true", help="Matrix summary only")
    args = parser.parse_args()

    if args.dry_run or not args.live:
        report = dry_run_report()
        if not has_env_key():
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

    if not has_env_key():
        report = dry_run_report()
        report["status"] = "skipped"
        report["reason"] = f"{ENV_KEY} not set"
        json.dump(report, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    try:
        rows = [run_matrix_row(row) for row in MATRIX]
        reask = run_reask_check()
    except RuntimeError as exc:
        json.dump(
            {"gate": 2, "mode": "live", "status": "error", "error": str(exc)},
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 1

    blank_locks = sum(1 for r in rows if r["blank_lock"])
    named_fork_rows = [r for r in rows if r["tag"] == "named_fork"]
    named_fork_blank = sum(1 for r in named_fork_rows if r["blank_lock"])
    matrix_passed = all(r["passed"] for r in rows)
    passed = matrix_passed and reask["passed"]

    report = {
        "gate": 2,
        "mode": "live",
        "routing": "one_path",
        "matrix": rows,
        "reask": reask,
        "summary": {
            "rows": len(rows),
            "named_fork_blank_locks": named_fork_blank,
            "total_blank_locks": blank_locks,
            "sticky_reask": reask["sticky_reask"],
            "passed": passed,
        },
        "status": "passed" if passed else "failed",
    }
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
