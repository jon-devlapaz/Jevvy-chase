# Jevvy-chase

A **grill-me** agent skill: ask what you want to do, then use **Jev** to
power the decision among next moves the agent supplies — not free-form LLM
advice. Jev ranks or picks among **host-supplied candidates**; it does not
grade your answers like a teacher. Confirming a choice is not a license to
implement.

## Install

1. Clone this skill into your personal skills folder:

   ```
   git clone https://github.com/jon-devlapaz/Jevvy-chase.git ~/.agents/skills/jevvy-chase
   ```

2. Set `TYPESAFE_API_KEY` in the environment. Do not put the secret in
   chat. The agent also needs `python3` and `uv` on your `PATH`.

3. In a **new** Cursor chat, type `/jevvy-chase` or `/jevvy`. If it is not
   offered, start a new chat after the clone.

The agent will not start this skill by itself. Cloning into
`~/.agents/skills/jevvy-chase` is what makes the slash command available
from other projects.

## How it works (Phase 0)

1. You say what you want to do (your words).
2. The agent supplies a small set of next moves or clarifying questions.
3. One Jev call ranks or picks among those candidates.
4. The agent proposes the top move and stops — no implementation.

Full agent rules are in [SKILL.md](SKILL.md). Question shapes are in
[references/jev.md](references/jev.md).

## Environment check

```
uv run --isolated --no-project --with typesafe-sdk==0.6.0 \
  python3 ~/.agents/skills/jevvy-chase/scripts/ask.py --check-env
```

Reports whether `TYPESAFE_API_KEY` is set without printing the value.

## Smoke

```bash
python3 ~/.agents/skills/jevvy-chase/scripts/smoke_gate1.py --live   # Gate 1 fork-pick
python3 ~/.agents/skills/jevvy-chase/scripts/smoke_gate2.py --live   # Gate 2 matrix
```

Without `--live` or without `TYPESAFE_API_KEY`, both exit 0 and print a
dry-run / skip summary (CI-friendly).

Results: [research/gate1-smoke.md](research/gate1-smoke.md),
[research/gate2-smoke.md](research/gate2-smoke.md).

## Roadmap

Multi-phase delivery and quality gates live in [HILLCLIMB.md](HILLCLIMB.md).
