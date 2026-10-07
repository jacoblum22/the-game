# Contract: Model calls

Five roles. Each call is one structured-output request whose JSON Schema the engine builds for this
turn. Every enum below is filled from the rules and the current state; an empty list means the field is
dropped from the schema. No schema contains a numeric field except `player_quantity` (the player's own
stated number, 01.1.4). The engine re-validates every response; an invalid one is re-asked once with
the failure named, then the rule's default applies (listed per field), else the turn errors with nothing
written.

## Packet order (all roles)

`role instructions → always-loaded core (00.15.4) → loaded cards (≤12, this call's) → narrator view →
last 4 exchanges verbatim → this message verbatim`. Stable first, for prompt caching. The Reader and
Framer instructions are persona-free; only the Narrator has a voice.

## A1 Reader (Gemini, thinking low) — T2 and PARSE/GATE/NECESSITY

Cards: 12.2.2, 01.2.1–01.2.6, 01.3.1, 01.3.8, 01.4.1, 01.15.2, plus situation and trigger cards.

```yaml
ReaderOutput:
  parts:                                    # 12.2.2 [J:enum]; default SPEECH↔DECLARATION → DECLARATION
    - text: str
      class: enum[SAFETY, SESSION, DISPUTE, PENDING_ANSWER, OOF_QUESTION, FICTION_QUESTION, DECLARATION, SPEECH]
  pending_answer: enum[<open pause choice ids>] | null
  fact_questions:                           # FICTION_QUESTION and embedded questions (01.2.1)
    - subject: enum[<scene entity ids>]
      predicate: str
      odds_rung: enum[<resolution.yaml#oracle rungs>]   # 01.15.2 [J:rung]; only used if unsettled
  beats:                                    # ≤3 (01.2.3)
    - intent: str
      method: str
      assertion: str | null                 # recorded as context, never a fact (INV-9)
      shape: enum[<01.2.2 shapes>]
      target: enum[<scene entity ids>, none]
      verb: enum[<15 basic verbs>]           # GATE G1 candidate
      license: enum[<PC's held licence ids>, none]   # G2 candidate; default G3 over G2 when unsure
      gate: enum[G0, G1, G2, G3, G4]
      g4_fact: enum[<fact ids>] | null       # the established fact that rules it out
      necessity: enum[uncertain_and_costly, riding, trivial, good_idea, impossible, take_the_time, certain_with_cost]  # 01.4.1; tie → roll
      intent_verbs: [str]                    # anchor lookup keys
  clarifying_question: str | null           # at most one per declaration (01.2.4)
  restatement: str                          # 01.2.6 neutral restatement
```

Engine after A1: verifies the gate class against holdings and `covers`/`excludes` lists, answers fact
questions from the store or the Oracle, computes anchor candidates.

## A2 Framer (Gemini, thinking low) — ANCHOR and FRAME per rolled beat

Cards: 01.5.1, 01.5.3, 01.6.1–01.6.11, 01.13.1, the candidate anchors' cards, precedent rulings found.

```yaml
FramerOutput:
  anchor: enum[<≤8 candidate anchor ids>]               # default: the basic verb's anchor
  deltas: [{knob: enum[<anchor knobs>], delta: enum[<allowed_deltas>], cites_fact: enum[<fact ids>]}]  # ≤2
  attribute: enum[<anchor default + allowed deltas>]    # lower on a tie (01.6.1)
  deed_tag: enum[<anchor deed tags and ancestors>]      # two-stage shortlist if empty
  traits: [enum[<T-01-13 traits>]]
  obstacle: {kind: enum[tier, opposed, entity_defense], tier: enum[<dc tier ids>] | null, entity: enum[<cast ids>] | null}
  levers: [enum[<scene fact ids>]]                      # ≤2, each must exist and not be too recent
  snags:  [enum[<scene fact ids>]]                      # ≤2
  stakes_source: enum[<resolution.yaml#stakes_flags.source.sources>, none]   # none → safe
  stakes_heavy: bool
  lethal: bool
  reach_whole: bool                                     # resolution.yaml#reach_flags
  reach_one_factor: bool
  threatened_cost: {menu_id: enum[<cost menu ids whose fits_when matches a fact>], form_intent: str}
  alternate_cost:  {menu_id: enum[...], form_intent: str} | null   # required for risky and dire
  method_consequences: [str]
  secret: bool
```

Engine after A2: `frame_check` (PR-01-2) computes DC, modifier, odds, cost previews, or refuses naming the
failure (one re-ask). The OFFER is built from the computed frame, never from model text.

## W World (Gemini, thinking low) — T5, only when an NPC present must respond

```yaml
WorldOutput:
  responses:
    - npc: enum[<present NPC ids>]
      want_engaged: enum[<this NPC's want ids>, none]
      refusal_engaged: enum[<this NPC's refusal ids>, none]
      table_context: {tags: [enum[<npc action table tags>]]}
```

The engine rolls `tbl.npc_action` with that context; the NPC acts only from that row or a resolved frame.

## B Narrator (Gemini, thinking low) — T7 draft and T8 mentions; D redraft

Input adds the adjudication record (frames with degrees, costs applied, oracle answers, NPC action rows,
omens) and, for a redraft, the failing verdicts with the store's values.

```yaml
NarratorOutput:
  fiction: str                              # 12.14 standard; no numbers or rules words
  mentions:                                 # every new addressable element (00.6.6)
    - kind: enum[<entity kinds>]
      name: str
      implied: [{predicate: str, value: str}]
      unsettled: [str]                       # properties the draft needs but the store lacks → Oracle/table
```

OOF blocks (OFFER, STATUS, WARNING, …) are rendered by the engine from state (12.15), not by the model.

## C Checker (Gemini for now; `TODO(CROSS_FAMILY_CHECKER)`) — T9 claims and T10 flags

A separate call: it gets the draft, the scene's entity ids with names and aliases, and its own
instructions. It never sees the narrator's prompt, earlier drafts or reasoning, so moving it to another
model family later changes only its config.

```yaml
CheckerOutput:
  claims: [Claim]                           # data-model.md §4; subject ∈ scene ids ∪ {unknown}
  screen:
    intent_acknowledged: bool
    intent_substituted: bool
    next_step_exists: bool
    mechanics_in_fiction: [str]             # offending spans
    ends_on_prompt_or_one_pause: bool
    safety_spans: [str]                     # against the player's lines and veils list (12.5.6)
```

Verdicts are computed by code (`check_claims`, 12.3.2 is `[D]`). Extraction instructions: every
sentence, every assertion; when unsure whether a phrase asserts something, extract it (12.3.1).

## Recording and replay

Every request and response is stored in `model_calls` (data-model.md §1). `ReplayAdapter` serves the
stored response for the same `(turn_id, role, attempt)` and checks the schema hash, so a replay detects
when engine changes alter what the model would have been asked.
