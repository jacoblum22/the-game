# Integration Report — Wave 3 → Wave 4

Single integrator agent. Rollback point: scratchpad `rules-snapshot-pre-integration` (untouched).
Work list: `_process/INTERFACE-REQUESTS.md` (all sections), `_process/issue-ledger.md` (I-023, I-024, I-026,
I-027 and every item marked integration), BRIEF §12 + Addenda, AUTHOR-BRIEF §3.

Progress notes are appended per step as work completes, so an interruption loses nothing.

## Progress log

- [started] Read BRIEF §12/Addenda, AUTHOR-BRIEF §3, INTERFACE-REQUESTS (full), issue ledger, 00 in full,
  SCHEMAS, every chapter's Interface-requests section. Inventoried all 41 contrib fragments.
- [step 1, part A — done] 00-architecture.md: 56 exact-match amendments applied by
  `scratchpad/integ/edit00.py` + `edit00b.py` (each asserted to match once); T-00-9 regenerated from the merged
  registry (105 handlers, 25 boundary rows); SCHEMAS.md (21 edits), scales.yaml (3), substrate.yaml (14),
  effects.yaml core (3). Details in "Step 1" below.
- [step 2, part A — done] boundaries.yaml rebuilt from seeded rows + 13 contrib owner-blocks (105 handlers, 0
  duplicates; 03/04 reserved-row wording applied; one defect fixed: `h.10.watch_check.rule_id` parsed as the
  number 10.9, now the string "10.9"). Ten canonical files received owner-blocks by text merge (entries
  preserved byte-for-byte, verified by parse + deep equality): effects (10 blocks, 38 entries), licenses (5/30),
  composites (1/32), conditions (1/6), factions (1/19), adversaries (1/33), origins (1/2), kits (1/2), hazards
  (1/2), calendar (1/1). YAML anchors in the 13 fragments renamed per fragment to stay unique. tags.yaml: 31 of
  31 proposals adopted (832 → 863 tags); 29 `trait.*` rows now cite T-01-13; `terrain.road.bridge` narrowed
  (DL-INT-03). All 42 fragments moved to `_process/merged-contrib/`; 66 path references in chapters, appendix
  fragments and data headers re-pointed to the canonical owner-blocks.
- [step 3, part A — done] Integration edits applied (each with an `[integration: …]` citation; every edit an
  exact unique match, logged): 01 (15 edits incl. I-024), 03 (9 + evidence.yaml 6 + index tables T-03-1/T-03-12
  for the 31 adopted tags), 04 (11), 05 (3 + composites.yaml cone/spread_form_map, rituals.yaml rit.imbue,
  abilities.yaml "in place of Fend" ×8), basic_verbs.yaml Handle (2), 06 (13), 07 (6), 08 (2), 09 (4).
  Generator scripts in `_process/simulation/` repointed from `data/contrib/` to `_process/merged-contrib/` (13
  scripts) so they stay runnable. Remaining: 10, 11 (I-026), 12, 13, 15, 16; I-027 audit.

## Continuation (Wave 3c, cloud session): progress log

The first integrator stopped after "step 3, part A". This session follows `HANDOFF.md`. Each edit is
applied by `scratchpad/xedit.py`, which asserts that every old string matches exactly once and that its
replacement is present afterwards. The script aborts with no write on any mismatch.

- [C1, done] **Integration edits and 00 amendments for chapters 10, 11, 12, 13, 15 and 16 verified.**
  Authoring order was 01 → 12 → 03–09 → 10 → 15 → 16 → 11 → 13 (ORCHESTRATION-LOG), so a target chapter
  receives integration edits only from chapters written after it. Item by item:
  - **To 10** (from 16, 13): quartermaster role (16 a: 10.5.1 table and `travel.yaml#roles`, 5 roles), night
    rota (16 b), one significant beat per interval (16 c); 16 (d) was already in 10.8.3 as authored and
    16 (e) was "adopted as written". Readable place facts `hushed`/`true_bell` (13's 00 amendment, 10.1.2).
    The PR-10-8 word step (I-027) is covered in C3. All carry markers.
  - **To 11** (from 13): I-026 (T-11-24 note, marker). The re-run is covered in C3.
  - **To 12** (from 02, 03, 04, 07, 09, 10, 11, 15): all registered "(integration)" items are present with
    markers. They are T6 PR-03-1 and `scene_end`, disputes → PR-03-4, `[RECOGNITION]`, lead engine placing
    the V2/V12 NPC, open offers in SITUATION, `[WARNING]`/`[STATUS]`, the no-default CHOICE, the bond NPC's
    set standing, `reaction_roll`, `[JOURNEY]`, `[SEASON]`/`[RETIRE]`, kickers reading the rotation ledger,
    `home`/`member_of`, the lead audit after `h.15.placement_audit`, and the `kind` column on
    `tbl.npc_refusal` (`oracles.yaml`). Fallback bangs at the next `scene_start` are in 12.8.4 as authored.
    **Fixed:** 12.15.15 (added by the first pass) sat before 12.15.14. It was moved after 12.15.14, and a
    check confirmed the move changed no characters.
  - **To 13:** none, since 13 was written last.
  - **To 15** (from 16, 11, 13): 16 (a)–(f) carry markers. `dt.11.train_successor` was present in T-15-16 and
    `downtime.yaml#menu_also` but had no marker. **Added** `[integration: IR ch.11 to 15]`. The three cases
    are in `investigation.yaml#cases` (verified by parse: 4 cases), and `region_thallen.yaml#cases` lists
    their 3 ids (DL-INT-07).
  - **To 16:** none. Chapters 11 and 13, the only ones written after 16, address no request to it. That is
    why ch.16 has no markers. Every request *from* 16 (to 03, 04, 06, 07, 08, 09, 10, 15) is applied with
    markers. The one exception is 08 (b): the handler order `h.08.upkeep` before `h.16.retinue_upkeep` (week
    phase 4) holds by registry order, so it needs no text.
  - **Fixed in 13:** the first pass left the "To 15" sentence in 13's Interface requests half-rewritten,
    stating both "moved at integration" and "15 may move them". It now reads as one sentence citing
    DL-INT-07 and keeps its marker.
  - **00 amendments from 10, 11, 12, 13, 15 and 16:** 115 scripted checks (`scratchpad/check00.py`) cover
    prefixes in 00.16.2, handlers in T-00-9, glossary terms, `travel_points`, `ally_kind`,
    `request_size`/`plausibility` steps, the `record_knowledge` how-list, owner-blocks in T-00-19,
    SCHEMAS keys (T-11-1, T-13-16, `clock_templates`, companions), tools #35/#36 and the 00.15.4 packet
    numbers. All pass on manual reading. The script's regex missed the packet and "march unit" wording,
    which are present at 00.15.4 and in the glossary. The amendments that name trigger ids
    (`trg.16.*`, `trg.11.flashpoint`) and labels need no 00 text: 00 keeps no trigger list (the `trg.`
    prefix is reserved in 00.16.2; each `[T]` rule lives in its owner chapter), and 00's glossary says
    "Out-of-fiction labels are 12.15's list", where they are registered (12.15.15).
  - **Not marked "(integration)" and therefore not applied:** later chapters' "To 12" notes written after
    ch.12 was finished (05, 06, 08, 16). One of them is a real gap and is logged as an issue (C6): 16 (b)
    names a claim class `action` that 12.3.1's closed list does not contain.
- [C2, done] **Contrib fragments.** `rules/data/contrib/` does not exist: no fragment is unmerged. All 42
  fragments are in `_process/merged-contrib/`. Independent re-check (parse plus deep equality, fragment block
  against canonical owner-block): 42 of 42 blocks match. The one exception is the intended repair of
  `h.10.watch_check.rule_id` (fragment `10.9`, a YAML float; canonical `"10.9"`). All 31 tag proposals are
  present in `tags.yaml` (863 tags). The generator scripts read and write `_process/merged-contrib/`; the
  leftover `data/contrib/...` strings in their docstrings and emitted header comments only record where each
  fragment came from. `integration-merge.py`, run on a scratch copy of `rules/`, leaves `data/`
  byte-identical (`diff -rq`: no differences), so the merge is idempotent and keeps the float repair.
- [C3, done] **Ledger integration items.** All four are marked resolved in `issue-ledger.md`, with evidence.
  - **I-023:** already resolved by the first pass (DL-INT-05; 00.7.5 marker; `boundaries.yaml` header).
    Verified: `h.07.affliction_onset` (07 block) runs before `h.10.site_exposure` (10 block), both in
    `interval` phase 2. 07.9.3's stage checks are consistent with this order. No edit needed.
  - **I-024:** WE-01-2 was already fixed (DL-INT-10). **Follow-through applied:** three other examples cite
    the same NPC and still said "no brother(s)", contradicting the fact `two brothers, no sister`. They are
    01.3.6's G4 redirect example, 01.3.7's CONTRADICTS-A-FACT example and 00.6.1's fact-table example. All
    three now read "no sister" `[integration: I-024]` (3 exact-match edits). A grep finds no remaining
    "no brother".
  - **I-026:** the `gain_hold()` fix and `steadfast` row were already in the script and noted in T-11-24
    and 13. On re-running, the output did not reproduce: two runs differed. **Cause:**
    `Faction.__init__` drew its first goal from the unseeded module RNG. **Fixed:** `run()` now calls
    `random.seed(seed)`, and two runs are byte-identical. `11-world-sim-output.txt` was regenerated.
    T-11-24 was rewritten from the reproducible run (highest tier 3, tier 5 in 0%, mean tier 2.01 / 1.99 /
    1.98; every count within 1 of the committed output except traces, within 5). **Stale numbers fixed:**
    11.3.9's "mean tier rose 0.6 and a tier-5 power arose in 8%" now reads "about 0.25 and no faction
    passed tier 3" [integration: I-026]. `11-world-sim.md` gained a re-run section, and DL-11-06's evidence
    gained the re-run figures. `13-world-sim.py --rule-cap` crashed against the fixed script, because its
    patch target was gone and the exec'd 11 code read `--rule-cap` as the seed count. It is now an
    accepted no-op that asserts the cap is native and filters argv. Both 13 outputs were regenerated: the
    numbers are unchanged (2.66–2.71 goals per full faction per year, 0% tier 5) and only the header line
    differs.
  - **I-027:** the clarification of PR-10-8 step 2 was already applied (DL-INT-04; marker), and
    `10-word-audit.py` already existed. Re-run: byte-identical, 7 of 55 cases pass and 48 fail. 10.10.2
    still claimed "the generic tables pass it by construction", which the audit refutes. It now names the
    items that hold by construction (1, 4, 5) and points to the failure [integration: I-027]. The failure
    itself is content, not integration, so it is **opened as I-029 (MAJOR, owner 10 with 09)**.
- [C4, done] **Appendix and DL-INT-11.**
  - `decision-log.md` and `traceability.md` were already assembled by
    `simulation/integration-assemble-appendix.py` from all 16 DL and 16 trace fragments (chapters 00–13,
    15, 16, plus INT; no ch.14 by design). Re-assembled after this session's fragment edits. Checks: each
    of the 379 fragment entries appears exactly once as a heading; each fragment's body appears verbatim;
    traceability.md is byte-identical on re-assembly (24 clauses; 111 other obligations; P5 and P14
    met-with-deviation; P6 and P17 met with a chapter-local partial).
  - **Validator ERROR fixed:** `DL-INT-11`, cited by 00.16.2a, was never written. Its decision was real:
    the id-prefix registry table generated from data. **Added DL-INT-11** to `fragments/DL-INT.md`. It
    records the decision: 53 named prefixes vs 90 in use, so 37 file-local families are registered by a
    generated table the validator reads. It also records the alternatives and the evidence.
  - **Generator defect fixed:** `integration-prefix-registry.py` looked up annotated file strings verbatim,
    so owners for `clk.`, `gen.`, `req.` and `tbl.` printed "?". It now strips the locator or note and maps
    `00-architecture.md#…` to 00. The table was regenerated and only those 4 rows changed (`req.` → 04;
    `gen.` → 00; 02; 04; 08).
  - Every DL id cited anywhere in chapters, appendix and data (414, including DL-INT-01..11) resolves to an
    entry.
- [C5, done] **anchors.yaml recompiled** (`simulation/12-compile_anchors.py`): 129 anchors (15 verb cards,
  69 chapter rules, 40 T-06-9 rulings, 5 of 07's shapes), 0 errors, 13 warnings recorded in
  `compile.warnings` (unchanged from the first pass: 5 cards with no T-00-20 knob, 3 intent verbs taken from
  rule titles, 5 T-06-9 rows whose anchor is not a basic-verb name). Against the previous file, the anchor
  content is identical. Only the source sha256 values (for chapters edited this session) changed.
  **Compiler defect fixed:** every run appended the two (c)/(d) source descriptions to `compile.sources`
  again. The committed file already held three copies, from the first pass's three runs. The compiler now
  drops existing copies before adding them once. Two consecutive runs are byte-identical, and
  `compile.sources` lists 5 entries.
- [C6, done] **Validation** (`python rules/_process/validate_ruleset.py`, exit 0). 54 data files; 3,431 ids
  (+ 873 tags and facets); 105 handlers; 2,864 rule-level ids indexed; 238 `[J:*]` rules, every one with a
  Worst case line (85 in template form, 153 inline; I-001 decides whether inline is compliant).
  **0 ERROR, 0 WARN, 78 INFO.** The INFO lines are 69 REFS-MD-EX (illustrative ids in worked examples and
  proposals, as expected) and 9 REFS-EX (placeholder ids inside `case.mill_fire`, 15's unplaced model case,
  by design). The single ERROR at the start of this session (`DL-INT-11`) was fixed in C4. The other
  mechanical defects fixed this session never reached the validator: the 12.15 order, the ch.13 duplicate
  sentence, the missing ch.15 marker, the "?" owners in 00.16.2a, the non-reproducible 11 sim, the
  crashing `--rule-cap` and the non-idempotent anchor compiler. All `data/*.yaml` files parse. Non-mechanical findings were logged as new ledger
  rows:
  - **I-029 (MAJOR, 10 with 09):** the generic encounter tables fail PR-10-8's word step in 48 of 55
    table × home-band cases.
  - **I-030 (MINOR, 12 with 16/05/06/08):** the claim class `action` named by 16.13.3 does not exist in
    12.3.1's closed list. Post-12 "To 12" notes were never registered as integration items and are
    unreviewed.
  - **I-031 (MINOR, 02/06/08/09):** 13 anchor-compile warnings (missing knobs or intent verbs; T-06-9 anchors
    that are not basic-verb names).
  - **I-032 (MINOR, 11 sim):** the world sims' AGENDA simplifies 11.3.7 (several rows read as `goal`;
    steadfast strikes at ≤ −2, not −3); align and re-run.
  The DL-INT preamble's pointer was corrected from "I-028 on" to "I-029 to I-032".

### Back-fill: what the first integrator did after "step 3, part A" (reconstructed from on-disk evidence)

The first pass logged nothing after step 3 part A. The commit `cbbd27e` (the rollback point) contains the
following, which this session verified rather than re-did:
- **Step 3, part B (integration edits to 10, 11, 12, 13, 15).** Markers in the committed text: 10 ×6, 11 ×1,
  12 ×13, 13 ×2, 15 ×10. Data edits: `travel.yaml#roles` + quartermaster; `evidence.yaml#journey_roles` +
  quartermaster (tag `deed.wilds.survival.provisioning`); `oracles.yaml` `tbl.npc_refusal` rows carrying
  `kind: refusal.*`; `downtime.yaml#menu_also` listing `dt.11.train_successor`; the three Thallen cases moved
  into `investigation.yaml#cases` (DL-INT-07). It also wrote `simulation/10-word-audit.py` and its output
  (I-027, DL-INT-04), and fixed `11-world-sim.py`'s `gain_hold` and `steadfast` row (I-026). Defects found
  and fixed in C1/C3: one missing marker (15), a half-rewritten sentence (13), 12.15.15 out of order, I-024's
  three uncorrected sibling examples, the non-reproducible sim, and 10.10.2's "by construction" claim.
- **Step 4 (appendix).** `simulation/integration-assemble-appendix.py` assembled `decision-log.md` (DL-00 and
  DL-00A kept; 15 chapter sections; DL-INT-01..10) and `traceability.md` (one matrix over I–VII and P1–P17
  plus the other traced obligations; 00's original rows preserved as `fragments/trace-00.md`). DL-INT-11,
  which 00.16.2a cites, was missing and was added in C4.
- **Step 5 (anchors).** `simulation/12-compile_anchors.py` (copied from ch.12's scratchpad spec) compiled
  `anchors.yaml` (`compiled_at: integration (Wave 3 -> 4)`; 129 anchors, 0 errors, 13 warnings).
- **Step 6 (validation).** It wrote `validate_ruleset.py` (YAML, ids, prefixes, references in data and in
  markdown, handlers, owner-blocks, `[J:*]` Worst-case form) and `simulation/integration-prefix-registry.py`
  (generating 00.16.2a). It regenerated T-00-9 from `boundaries.yaml` (DL-INT-08) and wrote
  `simulation/integration-merge.py` so merges can be re-applied (DL-INT-01). It stopped with one validator
  ERROR (DL-INT-11).
- **Step 7 (report).** Not written. Completed below.

### Ledger bookkeeping

I-005 was still "decided — integration edit to ch.03 pending", but the first pass had applied that edit (03.4.3,
`[integration: DL-00-05; closes I-005]`). Its status is now **resolved**, with that citation. No other row marked
`integration` remains open.

### Status of I-028

**I-028 (world-seed procedure for setting-free play): open, deferred to Wave 5 (revision). Not written at
integration, as instructed.** The ledger row says so.

### Final summary

Integration of Wave 3 is complete:
- Every approved 00 amendment and every registered "(integration)" item, across all chapters, is applied
  and carries an `[integration: …]` or `[amended: …]` citation. Chapter 16 has no markers because no
  later chapter made a request of it.
- All 42 contrib fragments are merged (deep-equality verified; the merge is idempotent), and
  `data/contrib/` is gone.
- Ledger integration items I-023, I-024, I-026 and I-027 are resolved, with evidence.
- The decision log (379 entries, DL-INT-01..11) and the traceability matrix are assembled from their
  fragments, and every cited DL id resolves.
- `anchors.yaml` is recompiled.
- The validator reports 0 ERROR and 0 WARN.

Open for later waves (not integration work):
- I-029: the generic encounter tables are out of budget (MAJOR).
- I-030: ch.12's claim classes vs ch.16, and other unreviewed "To 12" notes.
- I-031: anchor-card knobs and verbs.
- I-032: sim fidelity to 11.3.7.
- I-028: deferred to Wave 5.
- The earlier open rows: I-001, I-003, I-004, I-007..I-010, I-012, I-014..I-022 and I-025.

Rollback point: commit `cbbd27e`. Nothing has been committed by this session.
