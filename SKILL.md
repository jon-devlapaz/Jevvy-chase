---
name: jevvy-chase
description: >
  Ask what the user wants to do, then use Jev to pick among host-supplied
  next moves or clarifying questions. Jev ranks agent options — it does not
  grade the user's answers. Use when the user types /jevvy-chase or /jevvy.
disable-model-invocation: true
---

# Jevvy-chase

`/jevvy-chase` or `/jevvy`. Requires `TYPESAFE_API_KEY`. Never put the key in
state, chat, or repo.

## Worked example

**Person:** “Migrate checkout sessions to Redis — sync or async writes?”

**You supply candidates** (`{id, text}`, 2–4 rows):

- `fork` → Sync or async session writes?
- `vague` → What should we decide?
- `context` → What do you need to understand about Render first?

**One Jev call** (`pick_next` from [references/jev.md](references/jev.md)) →
`fork`.

**Show:**

```
❓ **Q1** - **Sync or async session writes?**
Answer in your own words.
```

Stop. Do not implement.

**Illegal:** inventing a menu so Jev has something to pick; grading the
person's answer; sqlite audit; answer-settle / teacher gates.

## Recipe

1. **Open** — No utterance yet? Ask: `What do you want to do? Answer in your own words.`
2. **Pick** — `{utterance, candidates}` + `pick_next` → call `scripts/ask.py` once. Shapes from [references/jev.md](references/jev.md), copied exactly.
3. **Propose** — Top candidate as Q1. ➡️ rec line **only** if they already named live alternatives. Stop.

```
uv run --isolated --no-project --with typesafe-sdk==0.6.0 python3 /absolute/path/to/this-skill/scripts/ask.py <<'JSON'
{"state": {"utterance": "...", "candidates": [{"id": "...", "text": "..."}]}, "questions": {"pick_next": {...}}}
JSON
```

Model: `jev-1.13.0` only. Jev remembers nothing between calls — keep state small.

## Hard rules

- **Host supplies candidates. Jev picks among them.** No other path.
- Optional **`ask_value`**: drop a candidate when score rounds to 0 and confidence ≥ 0.8.
- **No sticky re-ask:** filter out candidate text already asked unless `answers` changed.
- **➡️ rec:** only when live alternatives exist in their words. No dummy fork menu.
- **No router:** no `session_kind`, blank-lock, or explore/lock/collect maze. Tags (if any) only shape *your* candidate list before the Jev call.
- **No answer-teacher:** Jev never grades the person's reply.
