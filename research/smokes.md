# Smoke results

Run: `python3 scripts/smoke_gate{1,2,4}.py --live` (needs `TYPESAFE_API_KEY`).
Smokes call `ask.py` via `uv run --with typesafe-sdk==0.6.0`.

| Gate | Date | Status |
| --- | --- | --- |
| 1 fork-pick | 2026-09-18 | passed — `actual_pick: fork`, vague prob 0.02 |
| 2 matrix (6 rows) | 2026-09-18 | passed — 0 blank_lock, no sticky re-ask |
| 4 plan output | 2026-09-18 | passed — 2 turns, async locked, no vague ask |

Details live in script stdout / JSON output, not duplicated here.

## Gate 4 note

Named-fork utterance (Redis sync/async). Scripted host candidates + person
replies across 2 pick turns; host folds into plan sections. Live path calls
real Jev each turn; dry-run validates plan shape without key.
