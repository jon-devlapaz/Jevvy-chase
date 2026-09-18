# Jevvy-chase

Ask what you want to do. **Jev** picks the best next question from a list **you** supply — not free-form LLM advice, not grading the user's answer. The session ends in a **written plan**. Confirm ≠ implement.

## Example

**Utterance:** “Migrate checkout sessions to Redis — sync or async writes?”

**Turn 1 — you supply candidates:**

| id | text |
| --- | --- |
| `fork` | Sync or async session writes? |
| `vague` | What should we decide? |
| `context` | What do you need to understand about Render first? |

**Jev** → `fork`. They answer: *Async — p99 matters more.*

**Turn 2 — new candidates, Jev picks sequencing.** They answer: *Dual-write first.*

**Plan (output):**

```markdown
# Plan

## Goal
Migrate checkout sessions to Redis.

## Locked calls
- Session writes: async (p99 matters more).
- Sequencing: dual-write first.

## Open questions
- Which checkout paths migrate first?

## Next action
Spike dual-write adapter behind a flag.

## Non-goals
- Sync write path (ruled out).
```

*Does this match what you decided?* — then stop.

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
python3 scripts/smoke_gate4.py --live   # multi-turn → plan
```

No key? Drop `--live` — exits 0, prints dry-run. Gate history: [HILLCLIMB.md](HILLCLIMB.md).
