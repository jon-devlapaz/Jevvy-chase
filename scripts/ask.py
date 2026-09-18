#!/usr/bin/env python3
"""Call Jev. Does not apply skill logic or write audit logs."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

MODEL = "jev-1.13.0"
ENV_KEY = "TYPESAFE_API_KEY"
SECRET_KEYS = frozenset(
    {
        "api_key",
        "apikey",
        "typesafe_api_key",
        "authorization",
        "password",
        "secret",
        "token",
        "access_token",
    }
)


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for key, inner in value.items():
            if str(key).lower() in SECRET_KEYS:
                out[key] = "[redacted]"
            else:
                out[key] = redact(inner)
        return out
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        lowered = value.lower()
        if "typesafe_api_key" in lowered or "api_key=" in lowered:
            return "[redacted]"
    return value


def to_question(spec: dict[str, Any]) -> Any:
    from typesafe_sdk import Choice, Noul, Score

    if not isinstance(spec, dict):
        raise ValueError("question must be an object")
    kind = spec.get("type")
    instructions = spec.get("instructions")
    criteria = spec.get("criteria")
    if kind == "noul":
        kwargs: dict[str, Any] = {"instructions": instructions}
        if criteria is not None:
            kwargs["criteria"] = criteria
        return Noul(**kwargs)
    if kind == "score":
        return Score(instructions=instructions, criteria=criteria)
    if kind == "choice":
        return Choice(instructions=instructions, criteria=criteria)
    raise ValueError(f"question type must be noul, score, or choice, not {kind!r}")


def serialize(resp: Any) -> dict[str, Any]:
    import msgspec

    payload = msgspec.to_builtins(resp)
    if not isinstance(payload, dict):
        raise TypeError("Jev response was not an object")
    return payload


def env_status() -> dict[str, str]:
    present = bool(os.environ.get(ENV_KEY))
    return {
        "env_key": ENV_KEY,
        "configured": "yes" if present else "no",
        "model": MODEL,
        "note": "Set the key in your environment; this script never prints it.",
    }


def print_help() -> None:
    print(
        """Usage: ask.py [--check-env]  (stdin: {"state": {}, "questions": {}})

Call Jev with a JSON payload on stdin. Requires TYPESAFE_API_KEY in the
environment. The key is never logged or echoed.

Options:
  --check-env   Report whether TYPESAFE_API_KEY is set (yes/no only)
  --help        Show this message

Example:
  uv run --isolated --no-project --with typesafe-sdk==0.6.0 \\
    python3 scripts/ask.py <<'JSON'
  {"state": {"utterance": "..."}, "questions": {"pick_next": {...}}}
  JSON
"""
    )


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--check-env", action="store_true")
    parser.add_argument("--help", action="store_true")
    args = parser.parse_args()

    if args.help:
        print_help()
        return 0

    if args.check_env:
        json.dump(env_status(), sys.stdout, ensure_ascii=True, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    raw = sys.stdin.read()
    if not raw.strip():
        json.dump({"error": "stdin is empty; pass {state, questions}"}, sys.stdout)
        sys.stdout.write("\n")
        return 1
    try:
        body = json.loads(raw)
        if not isinstance(body, dict):
            raise ValueError("payload must be an object")
        state = body["state"]
        specs = body["questions"]
        if not isinstance(specs, dict) or not specs:
            raise ValueError("questions must be a non-empty object")
        model = body.get("model", MODEL)
        if model != MODEL:
            raise ValueError(f"model must be {MODEL}; do not fall back")
        from typesafe_sdk import TypeSafeClient

        questions = {qid: to_question(spec) for qid, spec in specs.items()}
        try:
            with TypeSafeClient(model=MODEL) as client:
                resp = client.system_one(state, questions, model=MODEL)
        except Exception as exc:
            json.dump({"error": str(exc)}, sys.stdout)
            sys.stdout.write("\n")
            return 1
        payload = serialize(resp)
        answers = payload.get("answers")
        returned = payload.get("model")
        json.dump(
            redact({"model": returned, "answers": answers}),
            sys.stdout,
            ensure_ascii=True,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError) as exc:
        json.dump({"error": str(exc)}, sys.stdout)
        sys.stdout.write("\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
