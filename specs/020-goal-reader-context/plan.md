# Plan: spec 020 (goal-first Reader, context per role)

## Technical context
Python 3.12, Pydantic v2, pytest, ruff, pyright. The packet builder (`engine/dm/packet.py::build_packet`) serves every
role; `engine/retrieve/cards.py::load_cards_for` picks cards. The Reader is `engine/dm/roles/reader.py` + its prompt +
`schemas.reader_schema`. The OFFER renders in `engine/dm/oof.py`; the pipeline passes "Then:" lines
(`engine/resolve/pipeline.py::_then`).

## Constitution check
- VIII.4 whole over parts: the Reader splits by goal, not act (US1). Pass.
- VIII.6 better context: no rule text for decisions a call does not make (US3). Pass.
- VIII.1 code must not author narrative truth: "Then:" stops printing a model's free-text field; the title is code
  words from typed slots plus the player's own words (US2). Pass.
- I (code owns the spine): typed goals stay the spine; the fold is in code, cited. Pass.

## Design

### F2 - Reader
1. **Prompt** (`prompts/reader.md` §3): "One beat per goal" replaces "one beat per distinct act whose failure would not
   stop the other" and "Two changes are two beats". Force, movement, an object or a lie in service of a goal is that
   goal's method (`purpose: serves_another_act` when the model still lists it). New field `how`: the method copied word
   for word from the message, or null.
2. **Schema** (`schemas.reader_schema`): `how` (string or null).
3. **`normalise`**: (a) a beat marked `serves_another_act` folds into the goal it serves even when it is against the
   will or uses a power; the goal beat takes its `against_will` / `uses_power` and its `how`; (b) an against-will
   hold (`restrain` or no change) directly before a Talk beat to the same person folds into that Talk beat (01.2.2's
   own example). A take, a blow or a hold with no goal to serve stays its own beat. Supersedes "a beat against
   someone's will or using a power is always its own beat".
4. **`how` is the player's words**: `read_message` keeps `how` only when it occurs in the message (case and spaces
   ignored); otherwise null. `Beat.how` carries it (one field on `engine/resolve/types.Beat`).
5. **Title and "Then:"** (`oof.goal_line`): kind and slots in plain words ("Learn from Dunwen Redmore", "Take the
   ledger from the clerk", "Go to the Blue Bell"), then `: <how>` with first-person pronouns turned to second.
   `offer_title`, `pipeline._then` and the plan pause's "Still go on to …?" use it. The separate change line under the
   title ("Taking: …") is dropped from the OFFER: the title now says it.
6. **Evals**: policy B3'/B5'/D1'/E written and applied blind; `goals` label on all 128 lines; the 35-line goal-shape
   set; `reader_live.py --set goalshape`; scorer scores `goals`.

### F3 - Context
1. **`cards.py`**: `GUIDANCE` (per-role digest sources, replacing `ROLE_CARDS`) and `guidance_digest(role)`: each
   card's `Decisions (J):` block (whole body for tables and cards without one), revision tags stripped, cached. The
   Reader's digest adds the change kinds and slots (`resolution.yaml#intended_change`) and the verb covers
   (`basic_verbs.yaml`). `load_cards_for` returns only trigger cards (scene roles) and `extra_ids`; situation cards,
   `situation_cards`, `core_cards` and `render_core` are deleted. Digests: Reader 01.2.2 + data; Framer its 12 cards'
   J blocks; Director T-12-7; World 15.2.3; Interpret 12.16.2; Narrator and Checker their current cards (A5).
2. **`build_packet`**: `core` carries the role's digest (section title GUIDANCE, `llm/base.py`); exchanges kept per
   role: Director 2, World 1, others `packet.verbatim_exchanges`.
3. **Director / World**: read their exchanges from the turn log (`turn.recent_exchanges`), so callers do not change.
4. **Identity lines** (`packet.identity_lines`): present cast, spotlight, and people named in the message and the
   exchanges; name as known, pronouns, the PC's `bond.*` tie. In the narrator view and the testimony call's view.
5. **Lead line**: the narrator and World views keep a thread only when new this turn or touched (focus, spotlight,
   shared words).
6. **Framer**: 15.3.2 as an extra card on a Talk beat.
7. **Measure**: `evals/role_tokens.py` over the seeded scripted long-horizon store, before and after.

## Retired (and by what)
| Retired | Superseded by |
|---|---|
| Reader prompt "One beat per distinct act whose failure would not stop the other"; "Two changes are two beats" | "One beat per goal" (01.2.2, DL-01-37) |
| `normalise`: "a beat against someone's will or using a power is always its own beat" | the fold of an against-will method into its goal |
| Policy B5 (and B3's "over to a person" Move) | B5', B3' (blind relabel) |
| `pipeline._then` printing `method`; `offer_title` printing the restatement; the OFFER's separate change line | `oof.goal_line` from kind and slots + the player's verbatim `how` |
| The 00.15.4 core in every packet (`render_core`, `core_cards`) | per-role guidance digest (`guidance_digest`) |
| Situation cards by tag, sorted by id (`situation_cards`, `load_cards_for` step 4) | cards only where code knows they apply |
| Role cards counted in the 12-card cap | the digest, outside the cap |
| Director and World with no conversation | last two / last exchange |
| Every open thread's lead line in every narrator packet | new or relevant only |

## Files
In lane: `roles/reader.py`, `prompts/{reader,director,world,framer,interpret}.md`, `packet.py`, `retrieve/cards.py`,
`roles/{director,world,framer}.py`, `testimony.py` (view only), `pipeline.py` (`_then`, `_ask` label), `oof.py`,
`schemas.py` (Reader), `pacing.yaml#packet` (comment), `evals/reader_*`, the golden/held-out/goal-shape files,
new tests. Outside, justified: `engine/resolve/types.py` (`Beat.how`, one field), `engine/llm/base.py` (the `core`
section's title), tests that pinned the old packet.
