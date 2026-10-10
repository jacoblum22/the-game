# R7-H1. Repetition history: why T3 came back

Read-only history trace for ROUND7-ANALYSIS §2 T3 (also R7-I1 §1 and §5). The evidence comes from the three
round-7 saves (`saves/playtest-20261009-160602-talker`, `-160642-explorer` and `-160622-fighter`, opened
read-only), the round-2 to round-6 saves (for one count), `git log -S` on the engine, and the history documents
named in the brief. Scratch scripts are in the session temp area, not in the repo.

## Summary

**T3 has one root cause, and it has come back at least six times.** The engine puts standing texture in every
narrator packet: a look, a habit, a lead, the incident sentence or a label. Each time, the fix was built for the
one surface that had been traced:
- the place's look;
- activities;
- thread lead lines;
- quoted speech openers.

The one general mechanism, the `last_used` usage marks of spec 009 B, replaced the old prose scan. But it was
keyed to a store representation that seeded NPC texture never entered. So no fix reached NPC looks, NPC habits,
the incident line or the label templates.

Two explicit "revisit if" conditions were recorded and later met, but nobody acted on them:
- DL-12-99, after spec 018 found "scenery repetition now comes from people's descriptions";
- HANDOFF §4, "revisit only if catchphrases persist after F1".

**Causes that were not known before (new in this trace):**
- The rule itself exempts the habit from freshness. 12.14.11 says "except a deliberate callback (**an NPC's
  recorded habit**; …)". The freshness line repeats "a deliberate callback is fine". Only 12.11.3 says "once per
  scene", and 12.11.3 is not in the narrator's GUIDANCE: turn.4's packet carries 12.11.1 and 12.11.9, but not
  12.11.3 or 12.14.11, in all three saves.
- The usage-mark machinery fired **0 times** in round 7. Every earlier playtest save has some marks: 13, 12, 8,
  5, 7, 4, 3, 1, 5 and 6. Even in round 6 the marks fell only on scene-state slots (`detail.activity`, `.manner`,
  `.posture`, `.held`), which `used_details` skips (`narrator.py:482`). **Since spec 009 B, the freshness line has
  never once carried an NPC's seeded look or habit in any playtest.**
- The refusal record line *requires* the habit. `npc_layer.py:489-491` `voiced_refusal`: "refuses, in their own
  voice (jovial, whispers secrets far too loudly)". This comes from spec 006 (0ccda80) and rule 12.11.9 ("said
  through their voice register and habit").

## The earlier bugs, one by one

| # | Earlier symptom (id, round) | Diagnosis then | What was built (commit, spec) | Why it did not hold in round 7 |
|---|---|---|---|---|
| H1 | **P-030**, round 1: "Narration repeats the same scene details turn after turn (the wiped counter, wet wool, the murmur)" | No freshness memory | 74f7749 (12.14.11): per entity, word 3-grams repeated in 2+ of the last 10 deliveries, listed as "Already used lately, do not reuse" | **(c)** Retired by spec 009 B (3f14432) and replaced by `last_used` marks; **(e)** the replacement's coverage of seeded looks was never built |
| H2 | **P-078**, round 1: "NPC repeats the same stock line every turn ('Mark me'); freshness covers images, not dialogue" | Freshness lacks dialogue | 3c6cbbf: `_repeated_lines`, a scan of speech openers | **(a)** It still works, but only for quoted speech openers. Gestures and manners are in the narrator's voice |
| H3 | **P-094**, round 1: "A notice's lettering line repeats every turn" | Object text not covered | Nothing (status `open`). DL-12-76 promised `written_words` marks | **(e)** Never built. `pacing.yaml` still lists `covers: [details, written_words, …]` |
| H4 | Round 3, problems 1–2: NPCs repeat their own lines ("Tibgit Lucky" ×4); activity lines every turn | S1 and S2: code over-determines dialogue; texture pushed as must-name | Spec 013 (b084308): `said` fed back and `not_a_repeat`; activities **rolled once per scene, shown as optional material** | It holds for said lines and activities. **(a)** The once-per-scene treatment was never extended to looks or habits |
| H5 | Round 4 R6: "The narrator repeats its own scenery" | First "freshness misses atmospheric phrasing"; traced to "the place's seeded look line was in every narrator packet" (HANDOFF §3.1) | R2-I DL-12-99 and spec 018 (0d3f8c1): `scene_setting(full=False)` drops the place's look on later turns | **(a)** Built for the place only. People's looks were deliberately kept in `present:` "for pronouns", and the known cost was written down. **(e)** The DL-12-99 revisit option was never built |
| H6 | Round 5 T3: "'Mark me' ×5 from the captain" | Blind repair calls; second cause: "the habit is stored as a rule"; also "people's descriptions still go out every turn … send only the pronoun line on later turns" | Spec 019 (1c25419): one passage and one sighted revision. Habit wording deferred (HANDOFF §4). Pronoun-only line never built | **(d)** The main diagnosis explained stacking *within* a turn, not repetition *across* turns. **(e)** The habit and description parts were never built |
| H7 | Round 6 I1 §5(c): a lead line in every packet; the model copies its own sentences; "FRESHNESS lists only openings" | The same shape as the look line | Spec 020 (f424cb2): thread lead lines only when new or touched (281 of 528 packets). The 0.8-copy passage check was not built | **(a)** The sibling `matter at hand` incident line was not touched: 44 of 44. **(e)** No copy check exists |
| H8 | Round 6 I2 §4: pronoun flips | Absent people's pronouns are in no packet | Spec 016 (7dc6b1f): pronouns on `present:` lines; spec 020 F3: pronouns for anyone named | **(a)** Pronouns were added, but the template strings stayed pronoun-neutral: `call them "…"` (P-095, e17a4f9), "their morning work", and habit rows such as "counts on their fingers" |
| — | "X brought the word" and the verbatim faction label | **Never filed** before round 7. Round 6 had 8 deliveries of the incident line, unnoticed | — | **(e)** These are new surfaces of the same cause |

### H1. P-030 → the 3-gram scan → retired by spec 009 B (c, e)

- **Then.** 74f7749 (2026-10-07) added `freshness_lines()`. It recorded phrases of three or more words that
  recurred in 2+ of the last 10 deliveries, per entity, and listed them under "Already used lately, do not reuse".
- **Retired.** Spec 009 B (3f14432, 2026-10-08) says: "freshness from last_used (image 3-gram scan retired)". The
  design memo (A_memory_and_context.md §P1) assumed three things would be built alongside:
  1. "seed `detail`/`appearance` text → slot migration";
  2. a view that renders "a compact profile … with a `(used last turn)` mark";
  3. "richer seeds (2–4 lasting details per NPC)".

  The spec 009 implementation results list item 1 under **Deferred**. Part B migrated only *created* looks
  ("created looks into detail slots"). Items 2 and 3 were never built. The `_DESCRIPTIVE_KEYS` hack, which the
  memo said would be superseded, is still at `packet.py:58`.
- **Now.**
  - The seed still writes `npc["voice"]` and `npc["detail"]` as entity data (`engine/gen/_seed_lib.py:340-341`),
    not as `detail.*` facts.
  - `used_details()` (`narrator.py:468-485`) reads only `state.details`.
  - `_mark_used()` (`narration.py:593-613`) marks only `detail.*` facts.
  - The round-7 saves hold 12, 21 and 16 `detail.*` rows, all `activity` or `manner`, and **0 `details_used`
    events**.
  - "Details stated lately" appears in 5 of 44 packets, with one item ("back door: state").
- **Counterfactual.** The retired 74f7749 function, run on round-7 deliveries, would have listed:
  - the seam at talker turn.2;
  - the hire notice at turn.4;
  - the crutch at explorer turn.4;
  - **the kettle at turn.6** (it was delivered in 11 of 11);
  - the scar at turn.10.

  It would have caught Kerric's finger-counting only at turn.15, because the model rewords it each turn ("counts on
  her fingers", "fingers stop on the third count", "fingers resume their count"). So the retirement lost the
  coverage of model-made images (the kettle and the seam). A prose scan would never have held the habit anyway.

### H2. P-078 → the speech-opener scan (a; it holds where it applies)

`narrator.py:401-437` is live. In the fighter save it listed `Belie Greenwort: "mark me"` on turn.14–16 (after uses
at turn.1, 11 and 13), and Belie did not say it again. **When the packet names the repeated thing, the model
complies.** The scan cannot see:
- gestures in the narrator's voice (finger-counting);
- narrated manner ("speaking far too loudly for a secret": 5 of 5 of the sellsword's turns);
- a catchphrase on its own ("Mark me." is under its two-word minimum).

### H5. Round 4 R6 → setting once (a, e)

- **Then.** `packet.py:353-355` now drops the place's look after framing, and it works: the explorer's kettle is
  in the view only at turn.3.
- **The deliberate gap.** The spec 018 implementation results say: "Scenery repetition now comes from people's
  descriptions ('his cloak of foreign cut' ×5), which stay in the setting every turn for pronouns: R6's phrase
  feedback (DL-12-99's revisit condition) is the next step." It was never built.
- **Now.** `packet.py:385` `look = ", ".join(... ("pronouns", "age", "detail", "demeanor") ...)` puts the look on
  every `present:` line in 42 of 44 packets. Talker turn.4 has `- present: Kerric Hartsmith, the captain of the
  gate (she/her, middle-aged, a finely embroidered collar, suspicious)`.
- **The second channel.** The raw view prints `voice: register=cold, habit=counts on their fingers while
  thinking` (`packet.py:491-495`, every data key up to the cap) in 42 of 44 packets.

### H6. Round 5 T3 → wrong as to the main cause (d), the rest never built (e)

- **Then.** Round 5 blamed blind add-repairs (5 of 14 turns) and noted that "a global freshness list would only
  have treated the symptom". F1 (spec 019) removed blind repairs.
- **Round 7 tests that diagnosis.** There is one narrator call per narrated turn (15, 15 and 14 calls; one
  revision), yet the habit shows in 16 of 21 speaking turns. The secondary causes round 5 named are exactly what
  remains:
  - the habit is worded as a rule (`tbl.npc_voice_habit`: "says 'mark me' before anything important", "counts on
    their fingers while thinking");
  - descriptions go out every turn.

  HANDOFF §4 deferred the first ("revisit only if catchphrases persist after F1"). The second was never picked up.

### H7. The incident line, a sibling of the lead line (a, e)

- **Origin.** `incident_line()` (`incident.py:44`, "{name} brought the word.") came in with the P-067 fix
  (00b6534) to fill an empty hook. It was kept through 008 A (bc722d7), and the content-contract memo says
  "`incident_line` can survive as a renderer".
- **Packet.** `packet.py:397-401` appends it to SCENE SETTING on every call.
- **The sibling fix.** Spec 020 gated *thread* lead lines (`_touched_threads`) after round 6 I1 §5(c) found that
  shape. The `matter at hand` line was not in that diagnosis.
- **Counts.** It is in 44 of 44 round-7 packets (15/15, 15/15, 14/14). It was delivered as prose at talker turn.1
  and explorer turn.1 and turn.15.

### H8 and the labels: templates for the same text on every screen (a, e)

- **The label.** P-095's fix (e17a4f9) added `call them "{who}", as every other screen does` (`packet.py:388`, and
  `:484`). Its purpose was consistent labels; its side effect is repeating the label word for word.
- **The template.** It is pronoun-neutral even on the same line as `(he/him)`. "The farmer" and "the sellsword
  between contracts" are he/him in 9 of 15 talker packets.
- **The faction label.** `_seed_steps.py:517` (`"officer of {}".format(fac["name"])`, from feature 004, 4d58ec8)
  produces "the officer of The faithful of Alett". The packet then orders the model to repeat it.
- **History.** Neither was ever filed as a repetition bug.

## Plain answers

**Same root cause or new?** It is the same root cause, and it has never been fixed in general. The cause is
code-supplied texture standing in every packet: **mandatory texture** and **wrong context**, plus **code authoring
narrative truth** for the incident line and the labels. Round 7's T3 is not a regression of any fix. Each fix still
works on its own surface: place looks, activities, lead lines, said lines and speech openers. T3 is the set of
surfaces that no fix reached.

One part *is* a regression: spec 009 B retired the only prose-level image backstop, and its replacement never
received the seeded data. That is why the kettle and the seam now loop with nothing to stop them.

**What a fix needs to do differently so it holds:**
1. **One gate for all standing texture, not one per surface.** Any non-mechanical string in the narrator packet
   (a look, habit, activity, place look, incident or lead) goes through a single code path: offer it once per
   scene, mark it offered or used, then drop it for the rest of the scene. Make the default for entity data keys
   "not printed". Allow only identity keys: name, pronouns and role. Then the next new surface inherits the rule
   instead of needing its own fix.
2. **Key the marks on what code offered, not on prose detection.** The 009 B marks depend on the model's wording
   matching a `detail.*` fact at 0.8. They never fired for seeded texture, and in round 7 they never fired at all.
   Marking on offer, or from the side list's `used` field, needs no store migration.
3. **Remove the instructions that force repetition:**
   - the habit inside `voiced_refusal`'s MUST line;
   - 12.14.11's "an NPC's recorded habit" callback exemption;
   - 12.11.9's "through register and habit";
   - the always-on wording of the habit table;
   - the verbatim-label "as every other screen does".

   Put the frequency rule on the offer line itself ("may use once this scene"), since GUIDANCE does not carry
   12.11.3.
4. **Keep one cheap backstop for model-made images**, covering closings as well as openings. 009 B removed it, and
   the kettle shows that copying forward from RECENT EXCHANGES needs no packet source.
5. **Add a lint so it stays fixed.** Over a seeded multi-turn replay, flag any non-allow-listed packet line repeated
   verbatim in three or more consecutive narrator packets of one scene. This would have caught the `present:`
   look, `voice:`, the incident line and the labels without a playtest. Also check the recorded "revisit if"
   conditions (DL-12-99, HANDOFF §4) at each round's analysis. Both were met in round 4/5 and missed.
