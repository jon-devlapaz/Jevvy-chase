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

PICK_INSTRUCTIONS = (
    "Given `utterance`, which candidate is the best next move or clarifying question?"
)
NEITHER_CRITERION = "None of these fits; the set needs reframing"


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
        [sys.executable, str(ASK)],
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
