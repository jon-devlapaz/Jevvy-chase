"""Shared helpers for jevvy-chase smoke scripts."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ENV_KEY = "TYPESAFE_API_KEY"
SKILL_ROOT = Path(__file__).resolve().parent.parent
ASK = SKILL_ROOT / "scripts" / "ask.py"
BLANK_LOCK_IDS = frozenset({"vague", "neither"})
VAGUE_TEXT = "What should we decide?"
MAX_PICK_TURNS = 5

UV_RUN = [
    "uv",
    "run",
    "--isolated",
    "--no-project",
    "--with",
    "typesafe-sdk==0.6.0",
    "python3",
]

PICK_INSTRUCTIONS = (
    "Given `utterance`, which candidate is the best next move or clarifying question?"
)
NEITHER_CRITERION = "None of these fits; the set needs reframing"

PLAN_SECTIONS = (
    "# Plan",
    "## Goal",
    "## Locked calls",
    "## Open questions",
    "## Next action",
    "## Non-goals",
)


def build_pick_payload(
    utterance: str,
    candidates: list[dict[str, str]],
    *,
    answers: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    criteria = {c["id"]: c["text"] for c in candidates}
    criteria["neither"] = NEITHER_CRITERION
    state: dict[str, Any] = {"utterance": utterance, "candidates": candidates}
    if answers:
        state["answers"] = answers
    return {
        "state": state,
        "questions": {
            "pick_next": {
                "type": "choice",
                "instructions": PICK_INSTRUCTIONS,
                "criteria": criteria,
            }
        },
    }


def call_jev(payload: dict[str, Any]) -> dict[str, Any]:
    proc = subprocess.run(
        [*UV_RUN, str(ASK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        try:
            err = json.loads(proc.stdout or proc.stderr or "{}")
        except json.JSONDecodeError:
            err = {"error": (proc.stdout or proc.stderr or "ask.py failed").strip()}
        raise RuntimeError(err.get("error", "ask.py failed"))
    body = json.loads(proc.stdout)
    if "error" in body:
        raise RuntimeError(body["error"])
    return body


def pick_choice(body: dict[str, Any]) -> str | None:
    return body.get("answers", {}).get("pick_next", {}).get("choice")


def candidate_text(candidates: list[dict[str, str]], choice: str | None) -> str | None:
    if choice is None:
        return None
    for row in candidates:
        if row["id"] == choice:
            return row["text"]
    return None


def filter_asked(
    candidates: list[dict[str, str]], asked_texts: set[str]
) -> list[dict[str, str]]:
    """Host rule: drop candidate rows whose text was already asked."""
    return [c for c in candidates if c["text"] not in asked_texts]


def has_env_key() -> bool:
    return bool(os.environ.get(ENV_KEY))


def utterance_names_alternatives(utterance: str) -> bool:
    """True when the person already named a fork in their words."""
    lower = utterance.lower()
    return "sync or async" in lower or " or " in lower


def render_plan(
    *,
    goal: str,
    locked: list[str],
    open_questions: list[str],
    next_action: str,
    non_goals: list[str],
) -> str:
    def bullets(items: list[str]) -> list[str]:
        if not items:
            return ["- (none)"]
        return [f"- {line}" if not line.startswith("- ") else line for line in items]

    lines = [
        "# Plan",
        "",
        "## Goal",
        goal,
        "",
        "## Locked calls",
        *bullets(locked),
        "",
        "## Open questions",
        *bullets(open_questions),
        "",
        "## Next action",
        next_action,
        "",
        "## Non-goals",
        *bullets(non_goals),
    ]
    return "\n".join(lines)


def plan_has_fork_trace(plan: str) -> bool:
    """Locked line or open question must mention the sync/async fork."""
    lower = plan.lower()
    if "sync" not in lower and "async" not in lower:
        return False
    locked_idx = lower.find("## locked calls")
    open_idx = lower.find("## open questions")
    next_idx = lower.find("## next action")
    if locked_idx == -1 or open_idx == -1:
        return False
    locked_block = lower[locked_idx:open_idx]
    open_block = lower[open_idx:next_idx] if next_idx != -1 else lower[open_idx:]
    return ("sync" in locked_block or "async" in locked_block) or (
        "sync" in open_block or "async" in open_block
    )


def plan_sections_present(plan: str) -> bool:
    return all(section in plan for section in PLAN_SECTIONS)


def understand_first_only(plan: str) -> bool:
    """Plan that only defers to understanding, with no fork trace."""
    lower = plan.lower()
    if plan_has_fork_trace(plan):
        return False
    return "understand" in lower and "sync" not in lower and "async" not in lower
