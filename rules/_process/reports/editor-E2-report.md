# Editor pass E2: ch.10, ch.12, ch.14

This pass read ch.10 and ch.12 section by section, as an AI DM or an implementer meeting them for the first
time, and then reviewed the new ch.14. All 46 edits are exact-match scripted replacements tagged
`[editor: E2-NNN]`. One PR-10-10 block move is also tagged. No mechanic, number or rule outcome changed. No
basis or revision tag was removed.

The validator reports 0 ERROR / 0 WARN, and the anchors were recompiled (129 entries, unchanged). Five
ledger rows (I-120 to I-124) were opened, all with status "open".

## Fix counts by category

| Category | Count | Ids |
|---|---|---|
| Stale "pending" or "requested" notes for amendments that have since been applied (`log_turn`, `revert_writes`, `anc.` prefix, `travel_points`, `random_event` tick source, 10.9.7 opt-in, 00 and 14 interface status, "scratchpad" scripts) | 16 | E2-001, 019, 020, 022, 030, 033, 034, 036, 038, 039, 040, 041, 043, 044, 045, 046 |
| Sentences broken by layered edits (the climax parenthetical, the "owner-block" antecedent, "the READ cost") | 3 | E2-009, 010, 012 |
| Card versus intro, title or table contradictions (10.5.1's "four roles" title over five roles; 10.12.9's kind tag missing `[J:enum]`; T-10-22 trap kinds not matching `traps.yaml`; 14.3.2's order not matching PR-14-1; 12.5.1's "preference tools" where 14.5.1 says none exist) | 5 | E2-003, 007, 017, 052, 035 |
| Cross-references, antecedents, abbreviations ("face 1–2" changed to "rows 1–2"; "3's avoid"; "End."; 10.13.6 changed to 10.13.7; 12.5.7 changed to 12.5.6; "T10") | 6 | E2-004, 006, 008, 011, 032, 054 |
| Numbering and tables (act.harvest duration cell; PR-10-10 moved after PR-10-9; a stray `\| --- \| --- \|` row in the non-threat table; T-10-12 caption values; T-12-9 units) | 5 | E2-013, 015, 016, 018, 042 |
| Wording an AI could read two ways, settled on the reading the mechanics or data require | 3 | E2-005 (10.9.7: the only effect of the opt-in is the timer), E2-014 (act.rest: durations are by rest type, not by mode, per 10.13.5), E2-037 (12.7.2: PEAK ends on the scene's own points, per `pacing.yaml#intensity.phases`) |
| Ch.14 citations, keys and codex views | 7 | E2-002, 021, 051, 053, 055, 056, 057 |
| Ch.14 chapter format (BRIEF §10's summary blockquote) | 1 | E2-050 |

## Ch.14 review

- **Cited rule ids.** I looked up every id ch.14 cites with `rq.py`. Two did not say what ch.14 claimed:
  - 14.2.4 said "an accepted grant can be set aside at any rest". 04.8.2 allows that only for a
    provisional grant (E2-051).
  - 14.5.3 cited "the T10 safety screen" without saying T10 is a step of PR-12-1 (E2-054).

  The `get_state` calls used three different signatures. They now all use 00.14.2 #8's full form,
  `scope: codex, view: codex` (E2-053).
- **Preference keys (T-14-1).** Every reader I found agrees with T-14-1: 01.7.4 (`auto_commit`), 07.5.14
  (`pref.death.mode`), PR-02-1 step 0 (`pref.lethality.acknowledged`), 02.10.1 (`creation.path`,
  `player.new_to_this`, `pacing.profile`), 12.7.3 and 12.9.3. `data/SCHEMAS.md` was the exception: its
  codex.yaml entry listed `preferences {auto_commit, lines, veils}`, and it now lists T-14-1's keys
  (E2-057). `codex.yaml` itself does not exist yet. `tone` has no reader in ch.12 (I-121).
- **Codex views (T-14-3) against 00.6.3.**
  - The old table left out these shown families:
    - time and calendar position;
    - location, the place graph and discovery;
    - frames and the OFFER;
    - relationship-state in conflict;
    - conditions on others;
    - adversaries' bloodied and down;
    - clocks.
  - It also left out the dying step, provisional status and vows.
  - It put NPC standing, which is `available`, in the default Journal view.
  - It put the preferences, which are `shown`, in an on-request view.

  T-14-3 now gives each shown or available family exactly one view, at its visibility (E2-055). The
  number of views is still 12. Ch.10's requested Journey, Map, Site and Weather views are carried in the
  Sheet, Gear and Journal views (E2-020), and 10.1.5's "map view" now points to the Journal view (E2-002).
- **Chapter format (BRIEF §10).** All nine sections are present. The one-paragraph `>` summary was
  missing and has been added (E2-050).

## Issue rows opened (status: open)

- **I-120:** Session zero's place in the sequence disagrees between chapters. 02 C0 says it runs session
  zero, while 12.5.1 and 14 run it before the world seed. `pacing.profile`, the pillars and
  `player.new_to_this` are each asked twice.
- **I-121:** `pref.tone` has no reader in ch.12.
- **I-122:** The turn log, the corrections ledger and the `next_time` notes are visible to the player, but
  they are not 00.6.3 families, so the codex cannot render them.
- **I-123:** PR-02-7's three creation notes overlap T-14-2's `fn.offer` and `fn.lethal`.
- **I-124:** WE-14-1's count of "seven `pref.*` facts" depends on whether a skipped "none" default is
  written.

## Also touched (outside the three chapters, as data or comments only)

- `data/effects.yaml`: the stale "PENDING 00 amendment" comment on `eff.10.travel_points` now cites
  T-00-13 [amended: DL-10-03] (E2-022).
- `data/SCHEMAS.md`: the codex.yaml preference keys (E2-057).
- `data/anchors.yaml`: recompiled. Only the source hashes changed.

## Noted, not changed

- 02.10.1 writes the `player.new_to_this` default as "no → treated as new". This can be read as the answer
  "no". T-14-1's "no answer → treated as yes" is the clear form. Ch.02 is outside this pass; I-120 covers
  the surrounding rows.
- In ch.12's Tables section, T-12-12 is printed before T-12-9. The numbering has no gaps, so the order was
  left as it is.
- I committed in this worktree because the task asked for it. CLAUDE.md says that only the orchestrator
  commits.
