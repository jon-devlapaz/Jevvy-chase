# Jevvy-chase

Ask what you want to do. **Jev** picks the best next question from a list **you** supply — not free-form LLM advice, not grading the user's answer. Confirm ≠ implement.

## Example

**Utterance:** “Migrate checkout sessions to Redis — sync or async writes?”

**You supply candidates:**

| id | text |
| --- | --- |
| `fork` | Sync or async session writes? |
| `vague` | What should we decide? |
| `context` | What do you need to understand about Render first? |

**Jev** → `fork` (not the vague trap)

**User sees:** ❓ **Q1** - **Sync or async session writes?**

Stop there.

## Install

```bash
git clone https://github.com/jon-devlapaz/Jevvy-chase.git ~/.agents/skills/jevvy-chase
export TYPESAFE_API_KEY=...   # never commit; needs python3 + uv on PATH
```

New Cursor chat → `/jevvy-chase` or `/jevvy`.

Recipe: [SKILL.md](SKILL.md). Jev shapes: [references/jev.md](references/jev.md).

## Smokes

```bash
python3 scripts/smoke_gate1.py --live   # fork pick
python3 scripts/smoke_gate2.py --live   # 6-utterance matrix
```

No key? Drop `--live` — exits 0, prints dry-run. Gate history: [HILLCLIMB.md](HILLCLIMB.md).
