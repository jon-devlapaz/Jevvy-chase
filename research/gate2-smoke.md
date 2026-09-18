# Gate 2 smoke — stay in lane matrix

**Date:** 2026-09-18  
**Harness:** `scripts/smoke_gate2.py` (+ `scripts/smoke_common.py`)

## Routing choice

**One path is enough:** `pick_next` only. Question-side tags (`named_fork`,
`explore`, `lock`, `collect_issues`, `wish`) shape **host candidate lists**
only — no jev-me `session_kind` router.

## Matrix (6 utterances)

| Tag | Utterance (short) | Expected pick | Live pick | blank_lock |
| --- | --- | --- | --- | --- |
| `named_fork` | Redis sync vs async | `fork` | `fork` | no |
| `named_fork` | hard-gate vs soft prompt | `fork` | `fork` | no |
| `explore` | understand caching options | `explore` | `explore` | no |
| `lock` | async writes — lock sequencing | `lock` | `lock` | no |
| `collect_issues` | flaky checkout | `collect` | `collect` | no |
| `wish` | make checkout faster | `scope` | `scope` | no |

**Named-fork blank_locks:** 0  
**Total blank_locks:** 0  
**Sticky identical re-ask:** no (re-ask sub-smoke on Redis fork row)

### Re-ask sub-smoke

- Turn 1: picked `fork` → “Sync or async session writes?”
- Host filtered that text from turn-2 pool; added simulated `answers`.
- Turn 2: picked `follow` → “What p99 or crash story matters more?” (not sticky)

## Live result

**Status: passed** (live key present in dev environment)

## Commands

Dry-run / CI skip:

```bash
python3 scripts/smoke_gate2.py
env -u TYPESAFE_API_KEY python3 scripts/smoke_gate2.py   # exits 0, status skipped
```

Live matrix:

```bash
export TYPESAFE_API_KEY=...   # do not commit
python3 scripts/smoke_gate2.py --live
```

Exit codes: `0` pass or skip; `1` live failure or Jev error.
