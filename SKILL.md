---
name: jevvy-chase
description: >
  Ask what the user wants to do, then use Jev to pick among host-supplied
  next moves or clarifying questions. Jev ranks agent options — it does not
  grade the user's answers. Use when the user types /jevvy-chase or /jevvy.
disable-model-invocation: true
---

# Jevvy-chase

The person types `/jevvy-chase` or `/jevvy`. The agent asks what they want
to do. **Jev** picks or ranks among **host-supplied candidates** — next
moves, clarifying questions, or options the agent enumerates. Jev does
**not** grade the person's answers like a teacher. A confirmed choice is
**not** a license to implement.

**Requires:** `TYPESAFE_API_KEY` in the environment. If auth fails, stop and
tell the person to set it. Never put the key in state, questions, chat, or
repo files.

## Call Jev

`ASK` is `scripts/ask.py`. Call it only this way. Copy question shapes from
[references/jev.md](references/jev.md) exactly.

```
uv run --isolated --no-project --with typesafe-sdk==0.6.0 python3 /absolute/path/to/this-skill/scripts/ask.py <<'JSON'
{"state": { }, "questions": { }}
JSON
```

The script pins `model="jev-1.13.0"`. If that version is missing, stop.

Each call is a fresh `{state, questions}`. Jev remembers nothing.

- State for the one-turn pick: `utterance` (their words) and `candidates`
  (`{id, text}` rows the host supplies).
- Copy question shapes from [references/jev.md](references/jev.md). Point
  backticks at those paths.

Do not put skill rules, folder maps, or long essays in state. If deleting a
field would not change the score, leave it out.

One Jev call per invoke. Questions cannot read each other. Candidates must
be real next moves or clarifying questions grounded in the utterance — do
not invent a menu so Jev has something to pick.

## Loop

```
1 Open → 2 Weigh/pick → 3 Propose → stop
```

### 1. Open

If they typed only `/jevvy-chase` or `/jevvy`, ask this and wait:

```
What do you want to do? Answer in your own words.
```

If the first message already answers that, use it. That text is the
`utterance`.

### 2. Weigh / pick (one Jev call)

The host (you) supplies a **small** set of candidates — typically 2–4 next
moves or clarifying questions derived from the utterance. Each candidate
needs `{id, text}`.

Build state from [references/jev.md](references/jev.md). Send one call
through `ASK` with `pick_next` and/or `ask_value` as documented there.

Rank or pick among **those candidates only**. Do not add options the person
did not imply.

### 3. Propose

Show the top candidate. One numbered question:

```
❓ **Q1** - **<candidate text>**
```

If Jev returned a recommendation line for a fork, show it after ➡️. Otherwise:

```
Answer in your own words.
```

**Stop here.** Do not implement. Do not start a multi-turn interview,
sqlite audit, or answer-settle gate. Confirming is not a license to
implement.

## Stay in lane

**One path is enough.** Use `pick_next` (and optional `ask_value` to
prune) only. Question-side tags like explore, lock, or collect shape
**host candidate lists** — there is no `session_kind` router.

- **Prune:** drop a candidate when `ask_value` rounds to 0 and
  confidence ≥ 0.8. Remove it from the pool before the next pick.
- **No sticky re-ask:** never propose candidate text already asked in
  this session unless `answers` (or other new state) changed. Filter
  the pool before calling Jev.
- **Rec line (➡️):** only when the person already named live
  alternatives for that candidate. Otherwise show “Answer in your own
  words.” No dummy fork menu.

Jev still grades **host-supplied candidates** only — never run
answer-settle or teacher gates on the person's reply.

## What the person sees

The bare invoke question, or one proposed next move. No session ids, no
lookup narration, no teacher-style grading of their reply.
