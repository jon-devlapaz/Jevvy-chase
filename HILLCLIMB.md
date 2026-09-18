# Hill climb

Gates 0–2 passed. Prefer deleting over adding.

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

**Why:** North star is one-turn grill + Jev pick among host candidates. Smoke
stdout already records utterance, candidates, and Jev's pick — enough to debug
today. A sqlite/JSONL audit store is ceremony before multi-turn sessions are a
product requirement. You might not need an audit store yet.

Revisit when: multi-turn sessions ship and you can't reconstruct what was
asked from chat + smoke output alone.

## Quality bars

- Exact Jev criteria strings (rephrasing rescales).
- Secrets never in repo, state, or chat.
- Smokes prove gates; no coverage theater.
