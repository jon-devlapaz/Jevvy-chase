---
name: jevvy-chase
description: >
  Ask what the user wants to do, then use Jev to pick among host-supplied
  next moves until a written plan is ready. Jev ranks agent options — it does
  not grade the user's answers. Use when the user types /jevvy-chase or /jevvy.
disable-model-invocation: true
---

# Jevvy-chase

`/jevvy-chase` or `/jevvy`. Requires `TYPESAFE_API_KEY`. Never put the key in
state, chat, or repo.

## Worked example

**Person:** “Migrate checkout sessions to Redis — sync or async writes?”

### Turn 1

**You supply candidates** (`{id, text}`, 2–4 rows):

- `fork` → Sync or async session writes?
- `vague` → What should we decide?
- `context` → What do you need to understand about Render first?

**One Jev call** (`pick_next` from [references/jev.md](references/jev.md)) →
`fork`. Ask it. They answer: *Async. p99 matters more than crash simplicity.*
Fold into **Locked calls** — never invent; use their words.

### Turn 2

New candidates from utterance + answers so far:

- `seq` → What do we lock first: dual-write or cutover?
- `scope` → Which checkout paths migrate first?

Jev → `seq`. They answer: *Dual-write first; cutover after a week of clean metrics.*
Fold into **Locked calls**.

Skeleton is fillable. **Exit** — paste the plan. Ask once: *Does this match what you decided?* Stop. Do not implement.

```markdown
# Plan

## Goal
Migrate checkout sessions to Redis.

## Locked calls
- Session writes: async (p99 matters more than crash simplicity).
- Sequencing: dual-write first, cutover after a week of clean metrics.

## Open questions
- Which checkout paths migrate first?

## Next action
Spike dual-write adapter for guest-checkout sessions behind a flag.

## Non-goals
- Replacing the entire checkout stack in one release.
- Sync write path (ruled out).
```

**Illegal:** inventing locked lines Jev didn't unlock; grading the person's
answer; sqlite audit; answer-settle / teacher gates; stopping after Q1 only.

## Recipe

1. **Open** — No utterance yet? Ask: `What do you want to do? Answer in your own words.`
2. **Fill** — Until the plan skeleton is fillable or they stop (cap ~4–5 pick turns):
   - Supply 2–4 candidates grounded in utterance + answers so far.
   - One Jev `pick_next` per turn ([references/jev.md](references/jev.md), exact copy).
   - Ask the picked candidate; fold their reply into the right plan section (you write the plan; no answer-settle gates).
3. **Exit** — Paste plan markdown (sections below). Ask once: *Does this match what you decided?* Stop.

Plan sections (fixed order):

```markdown
# Plan
## Goal
## Locked calls
## Open questions
## Next action
## Non-goals
```

Every **Locked calls** line comes from folding their words after a Jev-picked
question. **Open questions** = still unresolved. **Next action** = one concrete
step. **Non-goals** = explicit outs.

```
uv run --isolated --no-project --with typesafe-sdk==0.6.0 python3 /absolute/path/to/this-skill/scripts/ask.py <<'JSON'
{"state": {"utterance": "...", "candidates": [{"id": "...", "text": "..."}], "answers": [...]}, "questions": {"pick_next": {...}}}
JSON
```

Model: `jev-1.13.0` only. Jev remembers nothing between calls — keep state small.

## Hard rules

- **Host supplies candidates. Jev picks among them.** No other path.
- Optional **`ask_value`**: drop a candidate when score rounds to 0 and confidence ≥ 0.8.
- **No sticky re-ask:** filter out candidate text already asked unless `answers` changed.
- **➡️ rec:** only when live alternatives exist in their words. No dummy fork menu.
- **Named alternatives:** if utterance already names a fork, do not offer blank “What should we decide?” or generic “understand first” unless answers introduced new uncertainty.
- **No router:** no `session_kind`, blank-lock, or explore/lock/collect maze. Tags (if any) only shape *your* candidate list before the Jev call.
- **No answer-teacher:** Jev never grades the person's reply. Confirming the plan ≠ implement.
