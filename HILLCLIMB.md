# Hill climb

Gates 0–2 passed. Phase 4 adds plan output. Prefer deleting over adding.

## Gate 0 ✓

| Check | Path |
| --- | --- |
| Agent recipe | `SKILL.md` |
| Jev shapes | `references/jev.md` |
| Install | `README.md` |
| Env key (no leak) | `scripts/ask.py --check-env` |

## Gate 1 ✓

Named fork → Jev picks fork, not vague trap. Live 2026-09-18.

`python3 scripts/smoke_gate1.py --live`

## Gate 2 ✓

6-utterance matrix; 0 blank_lock on named forks; no sticky re-ask. Live 2026-09-18.

`python3 scripts/smoke_gate2.py --live`

## Gate 3 — deferred

Not checked.

**Why:** North star is multi-turn grill ending in a plan. Smoke stdout already
records utterance, candidates, picks, and final plan — enough to debug today.
A sqlite/JSONL audit store is ceremony before you can't reconstruct sessions
from chat + smoke output alone.

Revisit when that reconstruction fails in practice.

## Gate 4 — plan output

Multi-turn session ends in plan markdown; fork never loses to vague; no
understand-first-only plan when utterance names sync/async.

`python3 scripts/smoke_gate4.py --live`

| Check | Assert |
| --- | --- |
| Plan sections | `# Plan`, Goal, Locked calls, Open questions, Next action, Non-goals |
| Fork trace | Locked or open mentions sync/async — not understand-first-only |
| Named fork | `"What should we decide?"` never the asked Q when utterance names alternatives |
| Pick cap | ~4–5 turns max in recipe; smoke uses 2 scripted turns + fold |
| ask.py DX | gate1/2/4 call `ask.py` via `uv run --with typesafe-sdk` |
| No teacher | No answer-settle / decided gates in skill or smoke |
| No router | No `session_kind` / blank-lock maze |

## Quality bars

- Exact Jev criteria strings (rephrasing rescales).
- Secrets never in repo, state, or chat.
- Smokes prove gates; no coverage theater.
