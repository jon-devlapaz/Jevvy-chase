#!/usr/bin/env python3
"""Gate 4 smoke: multi-turn session ends in a plan; fork never loses to vague."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from smoke_common import (
    ASK,
    ENV_KEY,
    MAX_PICK_TURNS,
    VAGUE_TEXT,
    build_pick_payload,
    call_jev,
    candidate_text,
    filter_asked,
    has_env_key,
    plan_has_fork_trace,
    plan_sections_present,
    pick_choice,
    render_plan,
    understand_first_only,
    utterance_names_alternatives,
)

UTTERANCE = "I want to migrate checkout sessions to Redis. Sync or async writes?"

TURN_SPECS: list[dict[str, Any]] = [
    {
        "candidates": [
            {"id": "fork", "text": "Sync or async session writes?"},
            {"id": "vague", "text": VAGUE_TEXT},
            {
                "id": "context",
                "text": "What do you need to understand about Render first?",
            },
        ],
        "expected_pick": "fork",
        "answer": (
            "Async writes. p99 on checkout matters more than crash simplicity."
        ),
        "locked": "Session writes: async (p99 on checkout matters more than crash simplicity).",
    },
    {
        "candidates": [
            {"id": "seq", "text": "What do we lock first: dual-write or cutover?"},
            {"id": "scope", "text": "Which checkout paths migrate first?"},
            {"id": "vague", "text": VAGUE_TEXT},
        ],
        "expected_pick": "seq",
        "answer": "Dual-write first; cutover after a week of clean metrics.",
        "locked": "Sequencing: dual-write first, cutover after a week of clean metrics.",
    },
]

PLAN_TAIL = {
    "open_questions": ["Which checkout paths migrate first?"],
    "next_action": "Spike dual-write adapter for guest-checkout sessions behind a flag.",
    "non_goals": [
        "Replacing the entire checkout stack in one release.",
        "Sync write path (ruled out).",
    ],
}


def fold_plan(turn_records: list[dict[str, Any]]) -> str:
    locked = [row["locked"] for row in turn_records if row.get("locked")]
    return render_plan(
        goal="Migrate checkout sessions to Redis.",
        locked=locked,
        open_questions=PLAN_TAIL["open_questions"],
        next_action=PLAN_TAIL["next_action"],
        non_goals=PLAN_TAIL["non_goals"],
    )


def run_session() -> dict[str, Any]:
    asked_texts: set[str] = set()
    answers: list[dict[str, str]] = []
    asked_questions: list[str] = []
    turn_records: list[dict[str, Any]] = []

    for spec in TURN_SPECS:
        if len(turn_records) >= MAX_PICK_TURNS:
            break
        pool = filter_asked(spec["candidates"], asked_texts)
        if not pool:
            break

        body = call_jev(build_pick_payload(UTTERANCE, pool, answers=answers))
        choice = pick_choice(body)
        text = candidate_text(spec["candidates"], choice)
        asked_questions.append(text or "")
        if text:
            asked_texts.add(text)

        record: dict[str, Any] = {
            "expected_pick": spec["expected_pick"],
            "actual_pick": choice,
            "asked_text": text,
            "answer": spec["answer"],
            "locked": spec.get("locked"),
            "probabilities": body.get("answers", {}).get("pick_next", {}).get(
                "probabilities"
            ),
        }
        turn_records.append(record)

        answers.append(
            {
                "id": f"q{len(answers) + 1}",
                "question": text or "",
                "text": spec["answer"],
            }
        )

    plan = fold_plan(turn_records)
    return {
        "utterance": UTTERANCE,
        "turns": turn_records,
        "asked_questions": asked_questions,
        "plan": plan,
    }


def evaluate(session: dict[str, Any]) -> dict[str, Any]:
    plan = session["plan"]
    asked = session["asked_questions"]
    fork_named = utterance_names_alternatives(UTTERANCE)

    vague_asked = VAGUE_TEXT in asked
    turns = session.get("turns", [])
    picks_match = (
        all(row["actual_pick"] == row["expected_pick"] for row in turns)
        if turns
        else True
    )
    checks = {
        "sections_present": plan_sections_present(plan),
        "fork_in_locked_or_open": plan_has_fork_trace(plan),
        "not_understand_first_only": not understand_first_only(plan),
        "no_vague_when_fork_named": (not vague_asked) if fork_named else True,
        "picks_match_expected": picks_match,
    }
    passed = all(checks.values())
    return {
        "gate": 4,
        "checks": checks,
        "fork_named_in_utterance": fork_named,
        "asked_questions": asked,
        "plan_excerpt": plan[:500],
        "passed": passed,
    }


def dry_run_report() -> dict[str, Any]:
    scripted = [
        {
            "expected_pick": spec["expected_pick"],
            "asked_text": next(
                c["text"] for c in spec["candidates"] if c["id"] == spec["expected_pick"]
            ),
            "answer": spec["answer"],
        }
        for spec in TURN_SPECS
    ]
    plan = fold_plan(
        [{"locked": spec["locked"]} for spec in TURN_SPECS if spec.get("locked")]
    )
    return {
        "gate": 4,
        "mode": "dry-run",
        "utterance": UTTERANCE,
        "scripted_turns": scripted,
        "plan": plan,
        "assertions": [
            "plan sections: Goal, Locked calls, Open questions, Next action, Non-goals",
            "locked or open mentions sync/async (never understand-first-only)",
            f'"{VAGUE_TEXT}" never asked when utterance names alternatives',
        ],
        "live_command": "TYPESAFE_API_KEY=... python3 scripts/smoke_gate4.py --live",
        "ask_command": (
            "uv run --isolated --no-project --with typesafe-sdk==0.6.0 "
            f"python3 {ASK}"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate 4 plan-output smoke")
    parser.add_argument("--live", action="store_true", help="Call Jev (needs key)")
    parser.add_argument("--dry-run", action="store_true", help="Scenario summary only")
    args = parser.parse_args()

    if args.dry_run or not args.live:
        report = dry_run_report()
        eval_dry = evaluate(
            {
                "plan": report["plan"],
                "asked_questions": [
                    row["asked_text"] for row in report["scripted_turns"]
                ],
            }
        )
        report["dry_checks"] = eval_dry["checks"]
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
        session = run_session()
        result = evaluate(session)
    except RuntimeError as exc:
        json.dump(
            {"gate": 4, "mode": "live", "status": "error", "error": str(exc)},
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 1

    report = {
        "gate": 4,
        "mode": "live",
        **session,
        **result,
        "status": "passed" if result["passed"] else "failed",
    }
    # Plan is long; keep full plan in output for debugging
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
