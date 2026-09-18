# Hill climb

Each phase has a quality gate. Do not start the next phase until the gate
passes. Prefer deleting over adding.

## Phase 0 — Skeleton

**Deliver:** README, SKILL.md, references/jev.md, scripts/ask.py,
HILLCLIMB.md, LICENSE.

### Gate 0 checklist

- [x] **SKILL.md followable without jev-me** — `SKILL.md` documents the
  full Phase 0 loop (Open → Weigh/pick → Propose → stop), env requirement,
  and the exact `uv run … ask.py` invocation. Question shapes live in
  `references/jev.md`; no imports from jev-me session_kind, blank-lock, or
  answer-settle gates.
- [x] **README install works on paper** — `README.md` gives north star,
  `git clone … ~/.agents/skills/jevvy-chase`, `TYPESAFE_API_KEY`, and
  `/jevvy-chase` / `/jevvy` invoke instructions.
- [x] **ask.py documents env without printing secrets** — `scripts/ask.py
  --help` and `--check-env` report `TYPESAFE_API_KEY` presence as yes/no
  only; stdout redacts secret-shaped keys; the script never echoes the key.

**Evidence (paths):**

| Check | Path | How to verify |
| --- | --- | --- |
| Agent loop | `SKILL.md` | Read Loop §1–3; no jev-me cross-refs |
| Jev shapes | `references/jev.md` | Copy-paste `pick_next` / `ask_value` |
| Install | `README.md` | Clone target + slash invoke |
| Env key | `scripts/ask.py` | `python3 scripts/ask.py --check-env` |

## Phase 1 — One useful grill turn

**Deliver:**

- Open: ask what they want to do (their words).
- Host enumerates a small set of next moves / clarifying questions.
- One Jev call ranks or picks among **those host-supplied candidates**.
- Agent asks or proposes the top move; user answers in their own words.
- Stop early; no implement.

### Gate 1 checklist

- [x] **Named fork utterance** — sync vs async Redis writes
  (`scripts/smoke_gate1.py` → `SCENARIO.utterance`).
- [x] **Host supplies fork + vague trap** — candidates `fork`, `vague`,
  `context` in the smoke payload.
- [x] **One Jev call among host candidates** — `pick_next` Choice via
  `scripts/ask.py`.
- [x] **Top pick is the fork** — live smoke `actual_pick: fork`, `vague`
  probability 0.02 (2026-09-18).

**Evidence:**

| Check | Path | How to verify |
| --- | --- | --- |
| Smoke harness | `scripts/smoke_gate1.py` | `--dry-run` default; `--live` with key |
| Result note | `research/gate1-smoke.md` | pass/fail + commands |
| Live run | `python3 scripts/smoke_gate1.py --live` | `status: passed`, `actual_pick: fork` |

**CI without key:** `python3 scripts/smoke_gate1.py` exits 0 with
`status: skipped` and prints the candidate set + expected winner. Run
`--live` locally when `TYPESAFE_API_KEY` is set to satisfy the gate.

## Phase 2 — Stay in lane

**Deliver:**

- Soft routing only if needed: explore vs lock vs collect — **or** prove
  one path is enough.
- Prune low ask_value candidates; never re-ask identical candidate text in
  one session without new state.
- Rec line only when live alternatives exist.

### Gate 2

Dogfood matrix (≤6 utterances) with question-side tags; zero `blank_lock`
on named forks; no sticky identical re-ask.

**Status:** not started.

## Phase 3 — Audit (optional)

Minimal sqlite or log of Jev calls + asked candidates. Confirm ≠ implement.

### Gate 3

`list`/`log` (or equivalent) reconstructs what was asked and what Jev
scored; still no answer-teacher settle gate as the success metric.

**Status:** not started.

## Quality bars (every phase)

- Exact Jev criteria strings are stable (rephrasing rescales).
- Secrets never in chat, state, or repo.
- Smallest complete change; deleting is as good as adding.
- Tests/smokes that prove the gate, not coverage theater.
