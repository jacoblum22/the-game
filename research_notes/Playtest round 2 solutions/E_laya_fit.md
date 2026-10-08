# E. Where Laya fits the round-2 redesign

Written 2026-10-08. Earlier assessments: `research_notes/Tech stack and Phase 0 build/laya_letta_and_fine_tuning.md` and
`reports/Tech stack and Phase 0 build plan.md` §5 (both 2026-10-07). This note re-checks Laya against its repo
as of today (v0.4.0; README, BENCHMARKS.md and issue #377 read directly) and against the
[synthesis](00_SYNTHESIS.md).

## What changed since the first look

- **Version and community.** Now v0.4.0, with about 31k stars, ~50 contributors and 116 open issues. The
  single-author risk is lower than it was, but the project is three weeks old and releases several times a
  day.
- **Context length:**
  - the English `laya` checkpoint is still limited to 512 tokens;
  - `laya-typed-decisions` reads 1,024 tokens;
  - `laya-multilingual` reads up to 8,192 tokens, with accuracy holding to about 4k.
- **CPU speed.** About 110 ms per question on the English checkpoint, measured on a 28-thread CPU. Batching
  questions cuts that sharply (7 ms per question batched on a T4). It can also run on Intel GPUs and through
  ONNX.
- **Unchanged:**
  - zero-shot accuracy is below the majority-class baseline (0.36 against 0.46);
  - fine-tuned, it reaches 0.77;
  - choice questions must stay under about 20 options (Banking77: 0.43 to 0.49).
- **Negation (#377) is still open, and the author calls it a model limitation.** "Please do NOT refund my
  charge" was answered `refund_charge` at 0.97. Wrong answers come at 0.7–0.9998 confidence, so a confidence
  gate does **not** catch them.

## The key point: the redesign is what makes Laya fit

Before the redesign, Laya fits poorly. The Reader picks from 83 licences and five gates, and the Checker
extracts claims from prose. Laya can't do either: one is too many labels, the other is generation.

After the redesign, nearly every remaining model *judgment* is a short closed-list choice over a short text,
which is exactly Laya's sweet spot. So Laya is not an alternative to the redesign. It multiplies its benefit:
**the redesign turns guesses into small typed decisions; Laya makes those decisions free, fast and
deterministic.**

| Decision after the redesign | Options | Laya fit | Notes |
|---|---|---|---|
| Message class (12.2.2), SPEECH vs DECLARATION | 8 / 2 | **Good** | Every turn |
| Reader verb | 15 | **Good** | |
| Method facets: against someone's will / uses a power / mainly words | 3 yes/no | **Good only with a negation guard** | "I *don't* hurt him" is exactly the #377 failure, so it must be trained on negated minimal pairs |
| `question_kind` (C P2) | 6 | **Good** | |
| Target among the scene and spotlight entities | ≤12, dynamic | **Good** | Labels are entity names |
| Framer obstacle class (D P2) | ≤6 per verb | **Good** | The one-rung nudge is ordinal, Laya's weakest type, so leave it to Gemini or drop it |
| Snag and lever relevance | one yes/no per candidate fact (≤8) | **Possible** | About 8 questions batched in one pass |
| NPC practice and motive match (C P4) | 6 / one yes/no per motive | **Good** | Replaces the World LLM tie-breaker |
| Element kind / tier check on narrator declarations (C P1) | 9 | **Good, as a second opinion** | It comes from a different model family than Gemini; disagreement escalates to T2 |
| Diff-audit gate (B P2): "does this sentence assert more than its declarations?" | yes/no per sentence | **Possible, as a skip signal only** | Run the Gemini audit when Laya is unsure; B's 1-in-10 full extraction measures misses. Never the sole auditor |
| Detail contradiction (A P1) | yes/no | **Weak** | Contradiction is polarity, which is where negation fails. Code diffs typed slots instead |
| Harness: classify player notes, score contradictions offline | various | **Good** | Replaces the crude keyword "positive note" measure |
| Narration, T1b answer proposals, repairs | generative | **No** | These are about 69% of model calls today, and they stay with Gemini |

## Doors it opens

1. **The Reader stops being a model call on most turns.** The redesigned Reader is entirely closed lists, so
   Laya can answer it in about 100–300 ms on the player's CPU and hand off to Gemini only below a fitted
   confidence threshold or when a negation guard trips. That saves about 1–2 s and roughly 0.1–0.3¢ per turn.
   Together with the Framer class pick and the NPC layer, the saving is about 0.3–0.6¢ per turn. That is a
   meaningful hedge against the 2027 price doubling, but not a transformation, because narration dominates the
   cost.
2. **Determinism and drift resistance.** The same input always gives the same answer, and the weights are
   ours. Gemini version bumps can no longer silently change how actions are classified or how hard they are.
   That answers D's model-drift risk better than any prompt can. D's golden set becomes Laya's release gate.
3. **Calibrated probabilities are a routing signal.** Each decision returns a distribution, so the engine
   can choose per step: act, hand off to Gemini, or ask the player ("Do you mean to force it, or talk?").
   That last option makes the 12.2.7 player-input fidelity rule cheap to apply.
4. **An independent model family for checks.** The constitution requires the auditor to come from a
   different family than the Gemini narrator. A Laya tier gate (element kind, diff-audit skip) satisfies that
   at zero API cost.
5. **The project already holds good training data:**
   - **Recorded decisions.** The saves contain 742 Reader, 353 Framer, 414 World and 1,901 Checker calls,
     each with its packet. The labels came from Haiku, so relabel them to the new schema with Claude via the
     CLI (subscription, no API spend) and spot-check.
   - **The rules' own `[J]` cards.** 231 `[J:flag]` and 180 `[J:enum]` cards, each with inside, outside and
     non-example cases. These are ready-made seed examples, plus hard negatives taken from neighbouring cards.
   - **Synthetic minimal pairs**, especially negations ("I shove past" / "I don't shove, I squeeze past").
   - **Evaluation:** D's ~80-line hand-labelled golden set, never trained on.

   Training runs free on Kaggle's 2×T4 GPUs in about 4–5 hours.

## Costs and cautions

- **Ship weight.** torch plus a 421M checkpoint adds about 2–3 GB to a CLI game that is currently pure
  Python. Try the ONNX export with onnxruntime first, or make Laya an optional speed-up with Gemini as the
  default path.
- **Negation is the real hazard.** It will hit the facets (against someone's will), contradiction checks and
  refusals. Required before trusting Laya on any facet:
  - negated minimal pairs in the training data;
  - a cheap negation-cue router (not / don't / never / without / instead) that sends those messages to
    Gemini;
  - minimal-pair tests in the golden set.
- **Never on irreversible or high-severity decisions alone.** The gate on lethal or Dire frames stays code
  and Gemini, as the earlier note concluded.
- **Teacher ceiling.** Trained on model labels, Laya at best matches its teacher. Prefer code-derived labels
  (gate, necessity and DC are now computed) and hand-checked items.
- **Churn.** Pin the version, vendor the checkpoint with its sha256, and wrap it behind the existing
  `StructuredModel` adapter so it can be removed in an afternoon.

## Recommendation

Make it a **2–3 day spike right after Phase 2**, once the Reader schema has shrunk. It is not a replacement for
any part of the redesign.

1. Relabel the 742 recorded Reader calls to the new schema and add about 2k synthetic and negation pairs.
   Train on Kaggle.
2. Score the result against D's golden set alongside Gemini Flash: accuracy per field, negation pairs,
   calibration, and CPU latency on the owner's machine.
3. **Adopt it if** it matches Flash within 2 points on verb and facets, with negation pairs at or above 95%
   after the guard, and confident answers on at least 70% of turns. Then extend it to the Framer class, the
   NPC practice and the diff-audit gate.
