# Research: Measurement harness

Sources: `research_notes/Playtest round 2 solutions/` (cited as A/B/C/D §…), the saves under `saves/`, the
engine as of `milestone-1-playable` (0dd4b7d).

**R1. Corpus shape.** *Decision:* one gzip JSON file: per-save role call counts, every narrated turn's draft
history reduced to sentence keys, claim (sentence, class, subject-unknown), verdict (name, fix, reason head),
mentions (name, kind), plus ≤ 150 first-draft narrator packets split by `[SECTION]` with sections stored once
by hash. *Rationale:* a narrator packet is ~66 kB but ~54 kB of it (instructions, core rules, rule cards) repeats
across calls; the varying part is ~12 kB. *Alternatives:* committing saves (368 MB, gitignored by design);
packet digests only (`Game.export_record`) — no text to A/B on.

**R2. What "first draft" and "pass" mean.** *Decision:* the first checked version of a turn is the first
draft-history entry with claims (a mention redraft precedes the check, PR-00-7). It passes when no recorded
verdict is non-`supported` (`audit.claims.failing`). Delivered-as-drafted = one version and no fallback.
*Rationale:* reproduces B §1.2's 290/294 and 3/374 definitions.

**R3. Class instability.** *Decision:* for consecutive checked versions of a turn, each sentence whose
normalised text (`narration._key`: lower-cased word tokens) appears in both is compared by its set of claim
classes; unstable = sets differ. *Rationale:* B §1.2 row "identical sentence re-checked".

**R4. Oracle redrafts.** *Decision:* count verdict reasons written by `narration._settle`: "settled it as
drafted" (yes) vs "the Oracle settled it:" (no → redraft) vs "nothing settles it" (cut). *Rationale:* the turn
record keeps the reasons; oracle events would need the full save.

**R5. Pluggable bench.** *Decision:* `narrator(packet) -> {"fiction", "mentions", ...}` and
`judge(packet, draft) -> [{"text", "ok", "cls"}]` loaded by `module:function`. Pass rate, cut share and
declared/undeclared counts are computed from the judge's sentences. *Rationale:* per D5 support is judged
against the packet, so a judge needs nothing else; B P1's judge lives in spec 006. The `recorded` plugs return
the recorded draft and the recorded verdicts mapped to sentences, so the bench's own numbers and the plug path
are the same code.

**R6. Golden labels.** *Decision:* labels follow 01.3.1 (gate) and 01.4.1 (necessity) as a correct Reader
would, PC holding no licence unless the context names one; facets per D P1; `question_kind` per C §3 Option B
plus `none`. Lines with several beats are labelled on the first beat. The recorded Haiku answer (first beat of
the Reader call of that turn) is frozen in the line, so today's accuracy needs no model call. Constructed lines
(minimal pairs, controls) have no recorded answer. *Alternatives:* running today's Reader live — needs a game
state per line and a paid or CLI model; the `--reader` plug leaves room for it.

**R7. Long-horizon driver.** *Decision:* reuse `tests/e2e/driver.Driver` (offline setup, pause settling,
resume checks); scripted lines come from a fixed list of templates filled from the live state (names of present
and absent NPCs, reachable places, readable notices). *Rationale:* the driver already plays 500 offline turns in
the slow suite. *Alternative:* `evals/playtest.py` through the CLI — harder to interleave probes and store reads.

**R8. Aged store.** *Decision:* after setup, append seeded synthetic events directly to the store: per scene a
`scene_started`, one new NPC, 3 facts (one known to the PC via `knowledge_recorded`, every 10th a commitment), a
standing change, `scene_ended`. At 50/200/300 scenes, play two lines (a look and a recall probe) and read packet
sizes from `model_calls`. *Rationale:* boundedness without 300 scenes of play (A P8 mode 3).

**R9. Metrics.** Tokens ≈ characters / 4 (state the ceiling; no tokenizer dependency). Cached-prefix share =
common prefix with the role's previous packet ÷ packet length (Gemini implicit caching is prefix-based, A P6).
Novelty-4 = share of a delivery's word 4-grams absent from the previous 10 deliveries (A P8). Recall: probe
"What do I know about <name>?"; coverage = share of the PC-known facts about that entity whose value words
appear in the answer; precision = share of answer lines naming the entity that match some stored fact about
it. Contradictions = `contradicted` verdicts in first checked drafts by claim class per 100 narrated turns; the
12.4.8 scene-end sweep is not built in the engine (hook listed for its owner).

**R10. Real-model flag.** `--model gemini` builds `GameConfig(offline=False).model()`; owner-run only (D9).
