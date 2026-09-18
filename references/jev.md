# Jev question shapes

Copy `instructions` and `criteria` **exactly** — rephrasing rescales scores
silently. One `{state, questions}` object per call through `scripts/ask.py`.

## Why these questions

- **`pick_next`** — which host candidate to ask. This is the product.
- **`ask_value`** — optional prune when the pool is crowded. Skip if ≤3 candidates and the fork is obvious.
- **`rec_pick`** — optional ➡️ line when they already named fork alternatives. Skip otherwise.

## State + pick

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

`pick_next` — Choice. Criteria keys = candidate `id` values; `neither` last.

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

`ask_value` — Score. Point at `candidates[0]`; add parallel questions for
`candidates[1]`, `candidates[2]`, … if pruning.

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

## Optional rec (live alternatives only)

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

`confidence` = peakedness, not P(correct). Rank Score by `round(score)` clipped
0–2. For Choice, read `choice` + `probabilities`.
