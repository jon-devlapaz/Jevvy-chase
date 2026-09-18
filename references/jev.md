# Jev question shapes

Exact `instructions` and `criteria` for jevvy-chase. Copy these strings
exactly — rephrasing between runs silently re-scales every score. Send
`state` plus `questions` in one call through `scripts/ask.py`.

## Pick among host-supplied candidates

State is the person's words plus the candidate set the host enumerated:

```json
{
  "utterance": "I want to migrate checkout sessions to Redis. Sync or async writes?",
  "candidates": [
    {"id": "c1", "text": "Sync or async session writes?"},
    {"id": "c2", "text": "What p99 or crash story matters more?"},
    {"id": "c3", "text": "What do you need to understand about Render first?"}
  ]
}
```

`pick_next` — Choice. Criteria keys are candidate `id` values; `neither`
last. Only include candidates you actually sent in `state.candidates`.

```json
{
  "type": "choice",
  "instructions": "Given `utterance`, which candidate is the best next move or clarifying question?",
  "criteria": {
    "c1": "Sync or async session writes?",
    "c2": "What p99 or crash story matters more?",
    "c3": "What do you need to understand about Render first?",
    "neither": "None of these fits; the set needs reframing"
  }
}
```

`ask_value` — Score. Point at `candidates[0]` in instructions. For extra
candidates in the same call, add parallel questions pointing at
`candidates[1]`, `candidates[2]`, …

```json
{
  "type": "score",
  "instructions": "How much does answering `candidates[0]` change what happens next given `utterance`?",
  "criteria": [
    {
      "what": "Local or already implied by the utterance",
      "signals": ["Answering it does not change what gets built or ruled out"]
    },
    {
      "what": "Changes sequencing or a local choice; live paths remain",
      "signals": ["The same live alternatives stay open after this call"]
    },
    {
      "what": "Changes the outcome or kills a live path",
      "signals": ["A different answer would build something else or rule a path out"]
    }
  ]
}
```

## Optional rec among live alternatives

Send `rec_pick` only when the person already named 2–4 live alternatives
for that candidate. Criteria are those alternatives with `neither` last.
Skip `rec_pick` when no live fork exists — do not invent options.

```json
{
  "type": "choice",
  "instructions": "Given `utterance` and `answers`, which option leads best for `candidates[0]`?",
  "criteria": {
    "sync": "Sync: simpler crash story",
    "async": "Async: protects p99",
    "neither": "Neither fits; the question needs reframing"
  }
}
```

## Reading answers

`confidence` on Choice/Score is peakedness of the returned distribution,
not P(correct). Rank on the Score's level (`round(score)` clipped to 0–2),
not the leftover fraction. For Choice, read the pick and its confidence.
