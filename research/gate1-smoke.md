# Gate 1 smoke — fork pick

**Date:** 2026-09-18  
**Harness:** `scripts/smoke_gate1.py`

## Scenario

- **Utterance:** “I want to migrate checkout sessions to Redis. Sync or async writes?”
- **Candidates (host-supplied):**
  - `fork` — Sync or async session writes? *(expected winner)*
  - `vague` — What should we decide? *(trap)*
  - `context` — What do you need to understand about Render first?
- **One Jev call:** `pick_next` Choice (shapes from `references/jev.md`)

## Live result

**Status: passed** (live key present in dev environment)

```
actual_pick: fork
expected_pick: fork
confidence: 0.24
probabilities: vague 0.02, fork 0.43, context 0.29, neither 0.26
model: jev-1.13.0
```

Jev picked the named fork, not the vague fallback.

## Commands

Dry-run / CI skip (no key required):

```bash
python3 scripts/smoke_gate1.py
env -u TYPESAFE_API_KEY python3 scripts/smoke_gate1.py   # exits 0, status skipped
```

Live smoke:

```bash
export TYPESAFE_API_KEY=...   # do not commit
python3 scripts/smoke_gate1.py --live
# or with uv + pinned sdk (matches SKILL.md):
uv run --isolated --no-project --with typesafe-sdk==0.6.0 \
  python3 scripts/smoke_gate1.py --live
```

Exit codes: `0` pass or skip; `1` live failure or Jev error.
