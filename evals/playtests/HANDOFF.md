# Automated playtest loop: handoff report (2026-10-07)

For the next agent picking this up. It covers what was done, how, what was found, what was fixed and how,
what is still open, what went wrong in the process, and where to look next (rules and tech stack). Read
"Where things are" and "Recommendations" first.

---

## 1. Where things are

**Code.** All work is in **local commits on branch `milestone-1-playable`** (renamed from `claude/project-thread-q2smmv`).
- It was fast-forwarded from the integration branch, and the branch structure was then collapsed: only
  `main` and `milestone-1-playable` remain, with one working copy and no extra worktrees.
- The code head is `eb570e1`; later commits are logs, this report, and the run transcripts.
- Commit hashes cited below (from the `integrate-r1` and `worktree-agent-*` branches) are all ancestors of
  this branch, so `git show <hash>` still works.
- 152 commits since `ead9d5c` (the I-127 commit), about 65 of them substantive.
- Engine and CLI: +3,466 / −362 lines across 52 files. Tests: +3,528 lines across 33 files.
- Full suite **1113 passed, 3 skipped**; `rules/_process/validate_ruleset.py` **0 ERROR / 0 WARN**.
- **Nothing is pushed.**
- `rules/` content is untouched except new rows in `rules/_process/issue-ledger.md` (**I-127 … I-158**).

**Tracking files (in `evals/playtests/`):**
- `evals/playtests/ISSUES.md`: 123 deduplicated issues (P-001 … P-127), each with class, severity, evidence
  (run stamp and input numbers) and status. About 90 fixed, 6 logged as rules questions, 3 partly fixed,
  ~24 open (mostly low-severity polish; a few rows still say "open" though fixed: P-091 and P-126 were fixed
  in a31eabe and 1062541).
- `evals/playtests/ROUNDS.md`: one row per playtest run (code commit, play turns, narrator calls per turn,
  fallbacks, the main findings).
- `evals/playtest.py`: the harness (section 3).

**Transcripts and saves.**
- Per-run transcripts (`<stamp>-claude-<persona>.md`) and findings (`.findings.jsonl`) are committed in
  `evals/playtests/` (about 3.4 MB).
- Saves are in `saves/` (gitignored, local only).
- Every issue row cites its run stamp, so the evidence is findable.

**Worktrees and branches.** At the owner's request, every extra worktree (about 42: the integration
checkout, 5 pinned playtest checkouts, and one per fixer) was removed, and every merged branch was deleted
with `git branch -d`. Each was verified merged first. One fixer worktree held stray uncommitted files; they
were confirmed already contained in the branch, and a patch copy was kept in the session scratchpad.

**Running at handoff.** Nothing. All playtest processes were stopped at the owner's request.

---

## 2. Why this was done

The owner's first live session (Gemini engine, `saves/My World2.db`) opened with one line and answered "set
the scene" with two. Diagnosis: the narration claim check (12.3.1–12.3.3) deleted ordinary description, and
redrafts shrank the prose. The rules were revised (I-127 / DL-12-37) and the engine followed (commit
`ead9d5c`). To find the next problems faster than one human playing, the owner asked for many automated
player/game pairs in parallel, with errors logged and fixed by subagents, improving until satisfactory.
Constraints:
- No API spend (no Gemini calls).
- Don't delete files.
- Rules problems go to the ledger, never edits to `rules/`.

---

## 3. Process

### 3.1 The harness: `evals/playtest.py`

- **It runs the real CLI** (`play.cli.main`) **and the real engine. Only the model is swapped.**
  - `ClaudeModel` calls the Claude Code CLI headless (`claude -p --json-schema … --tools "" --strict-mcp-config
    --setting-sources project`) on the owner's subscription, so there is no API spend.
  - The engine model was **Haiku** (`--engine-model haiku`), as the closest cheap analogue to Gemini Flash.
  - The packet, schema, validation and every rule run exactly as with Gemini.
- **The player is also Claude** (Sonnet), playing one of five personas: explorer, talker, fighter, breaker,
  newcomer.
  - Each turn the player reads the terminal output and types a line, plus a private `note` saying what
    confused or annoyed it.
  - The player sees its own typed lines echoed. Without this it reported "skipped" steps (P-008).
- **`--quick-setup`** scripts world-building and picks a random ready-made character. The newcomer persona
  always did the full setup, so setup stayed tested.
- **`--turns 15`** counts play turns, not inputs (setup used to eat 25 of 40 inputs).
- **Findings** (`.findings.jsonl`) are written automatically per run:
  - leaked errors (Traceback, pydantic, "Input should be");
  - repeated output;
  - every fallback and redraft, with the failing verdicts and reasons;
  - model-call failures;
  - stats (turns, calls per role, narrator calls per turn);
  - every player note.
- **Pinned launcher** (`scratchpad/launch_pt.sh <persona> <commit> [--quick-setup]`): each persona runs from
  its own worktree checked out at a verified commit. Merging fixes elsewhere can't change code under a
  running game (the engine imports modules lazily).
- **Speed:** each CLI call took about 4 s of start-up (8 s before `--strict-mcp-config` and
  `--setting-sources`). A play turn made 4–8 calls, so a 15-turn run took 25–45 min.

The harness needs the Claude CLI logged in once. On this machine the CLI is inside the Microsoft Store app's
virtualised folder:
`%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude-code\<ver>\<hash>\claude.exe`
(the app itself sees it under `%APPDATA%\Claude\claude-code\…`).

### 3.2 The loop

1. **Play.** Up to 5 runs in parallel, one per persona, each relaunched on the newest verified commit as soon
   as it finished (a rolling cadence rather than rounds).
2. **Triage (orchestrator).** Read the findings file and only the parts of the transcript or save needed.
   Classify each finding as bug, polish, rules, harness or claude-only. Deduplicate into `ISSUES.md`. Rules
   questions go to the ledger.
3. **Fix.** One subagent per independent cluster, each in its own git worktree (`isolation: worktree`), with
   explicit file "lanes" to avoid collisions. Each brief contained:
   - the evidence (transcript, input numbers, save path);
   - the root-cause requirement (fix the shared function, not one caller);
   - tests first;
   - the full suite;
   - commit on its branch, no push, report in ≤250 words.
4. **Verify (orchestrator).** Merge into `integrate-r1` and resolve conflicts by hand. Re-record the replay
   game (`py -3.12 -m tests.replay.record_games`) when packets changed on purpose. Run the full suite and the
   rules validator, log to `ISSUES.md`, `ROUNDS.md` and the ledger, then commit.
5. Relaunch personas on the new commit; hold a persona whose main topic was mid-fix (talker during P-026,
   fighter during combat).

About 40 fixer subagents ran. Typical turnaround was 6–25 minutes each, with 2–4 running at once.

---

## 4. Results

### 4.1 Metrics across 62 runs

| Period | Runs | Turns ending in the plain fallback | Narrator calls / turn | Notes reporting something broken |
|---|---|---|---|---|
| Round 1 (code `ead9d5c`) | 5 | **56 %** | 2.39 | 22 % |
| 17:00–18:00 | 13 | 10 % | 2.06 | 23 % |
| 18:00–19:30 | 18 | 6 % | 1.75 | 23 % |
| 19:30–21:55 | 26 | **4 %** | 1.79 | 17 % |

- In the last ~15 runs: 0 crashes or leaked errors, and 0–2 fallbacks per 17-turn run.
- The best runs had 1.0–1.2 narrator calls per turn, meaning zero redrafts.
- The "positive note" share stayed flat at about 50%. That measure is crude (keyword-based), and the player
  is told to find fault.
- The bigger signal is what the complaints say:
  - **Early:** "raw error", "garbled", "NPCs never speak", "setup loops".
  - **Late:** "she agreed but never said what", "odds feel harsh", "the same detail repeats".

### 4.2 What was fixed (by area; commits on `integrate-r1`)

**Narration and claim check:**
- **Atmosphere and furniture (I-127):** atmosphere is not checked, and new furniture is written rather than
  cut.
- **Redraft convergence:** sentences that passed carry over, an Oracle answer that agrees with the draft
  needs no redraft, and a cut-only remainder is delivered instead of the fallback.
- **Fallback text:** reads as fiction and never as debug text; facts render through one `fact_sentence`
  helper, checked against a committed 770-shape fixture.
- **Openings:** they no longer fall back. Screen 12.2.7 needs a player part, and the inciting incident
  sources crowd reactions.
- **Freshness:** a recently-used images and lines memory (12.14.11). The record and the store are never
  named in prose, and the narrator never parrots the player.

**NPCs and knowledge:**
- **NPC behaviour:** an addressed NPC may speak and react; NPCs created mid-scene join the cast; narrated
  presence stays consistent with the store's scene cast; one label per unnamed NPC; NPC names stay unknown
  until learned.
- **Learning:** a successful Talk, Observe or Recall records knowledge. A Talk success always delivers:
  - a "who" question is bound to an existing NPC (`settle_who`);
  - a "what" question about an ordinary thing is named and written;
  - otherwise a lead.
- **Opening incident:** bound to an existing seed NPC, with witnesses who know clues (`engine/dm/incident.py`).
- **"What do I know?"** is answered from the store; the journal reads learned facts.
- **Reading:** literate PCs get a notice's words, and illiterate PCs never do.

**Adjudication:**
- **Gate:** a held licence passes (G2). A G3 on a basic verb with no licence becomes G1, and so do speech
  acts with a no-DC crude fallback.
- **Talk is never framed as force:** anchor candidates are limited to the beat's verb family.
- **Framer:** offered only legal costs, tiers and levers (shared predicates between the schema and
  `frame_check`). Opposed social frames get a defence attribute.
- **Movement and rules mechanics:** Move writes position and band; riding (01.4.2) is implemented and
  attacks never ride; condition cleanse is implemented; extended goals use a progress clock.
- **Combat core (`engine/resolve/conflict.py`):** conflict start and end, strikes deal harm, foes answer with
  `beh.default_melee`, contact bands are written, and harm shows as a `Changed:` line.

**Pauses and the CLI:**
- Every resolved roll prints a `[RESULT]` block, labelled by beat when a turn has several.
- An empty line never silently takes a menu default.
- Questions asked at a pause are answered (go big, near miss, cost terms, Luck).
- Go big keeps the offer; change approach asks how.
- No engine exception text ever reaches the player; validation reasons are logged on model-call records.

**Setup:** questions at a step are answered, full lists are available, jargon is glossed, pronouns are taken
with the name, and typed words never silently become the default.

**Crash fixed (P-084):** an Oracle yes/no stored under predicate `wants` replaced an NPC's list. Every later
turn crashed until the run ended. The Oracle now never writes NPC list fields.

### 4.3 Still open

**Owner decisions (ledger):**
- **I-153** (MAJOR, the largest remaining gap): what may a successful Talk reveal when the world holds
  nothing on the topic? The current engine stopgap is described in 4.2; it needs a ruled design.
- **I-158, with I-143 and I-155** (MAJOR): difficulty. The engine's odds follow 01.8.1 / T-01-3 exactly;
  harshness comes from the Framer's tier and snag choices. Example: "push through a crowd" at a moderate tier
  with two −2 snags gives 10% success and 45% critical failure. Needed: a rubric, a snag cap, and the
  relationship between the critical-failure and success bands.
- **I-154 / I-156** (MAJOR): combat subsystems still missing: morale (yield or flee), sides and objectives,
  surprise, tempo, reactions, the dealer-side harm pass, called shots, and non-melee behaviour rows. Also a
  quick default build for named NPCs who fight.
- **I-134 / I-138:** plain-language OFFER wording (S2, Reach, DC, Mode).
- **I-140, I-145, I-148, I-149:** "who is X" tables, incident binding at seed time, who counts as common
  knowledge.
- **I-128 … I-152:** smaller rule clarifications; each states what the engine now does.

**Engine (open rows in `ISSUES.md`):**
- Consistency drift: descriptions contradict across turns (P-063, P-127).
- Repeated object text (P-094).
- Fallback echoing the player's questions (P-125).
- Travel arrival narration (P-098).
- Junk objects from mentions in the journal (P-119).
- Assorted setup polish.

---

## 5. What went right and wrong in the process

**Right:**
- **Real engine, model swapped:** every finding was a real code path, not a simulation.
- **Machine-readable findings plus player notes:** fallbacks and verdicts pinpointed where to look; notes
  showed what a person would feel.
- **Pinned worktrees and rolling relaunch:** merges never disturbed a running game, and each finished
  persona immediately tested the newest code.
- **Evidence-rich, root-cause briefs with lanes:** most fixes landed first try with tests. Conflicts were few
  and small: `pipeline.py`, `reader.md` (word budget), `fallback.py`, one test file.
- **Rules discipline:** about 30 ledger rows record exactly what the engine does where the rules were silent
  or contradictory, so the rules editor can rule on them instead of discovering drift.

**Wrong, or lessons for next time:**
- **Harness artifacts cost time:** the player not seeing its own input (fixed); tracebacks lost because the
  launcher piped stderr through `tail` (later recovered by `Game.replay` on the pinned commit).
- **Fixer worktrees started on old `main` (99b0249).** Every brief must start with
  `git reset --hard integrate-r1`.
- **A fixer committed a generated cache pickle** (`engine/data/_cache/`). It is now gitignored and the file
  untracked.
- **Cross-worktree leakage:** one fixer found another fixer's uncommitted files in its worktree and rebuilt
  its commit. Check `git diff --stat` before merging.
- **Windows Git Bash heredoc gotcha:** writing Python source through a heredoc turned `"\n"` into a real
  newline at least 6 times. Use the Edit tool for code (a project memory file records this).
- **A test read live `saves/`,** so new runs broke the suite. It was replaced by a committed fixture.
- **Prompt word budgets** (`tests/engine/test_prompts.py`: Reader 700, Checker 700, Narrator 1000) forced
  trimming at merge time. Prompt-only fixes are nearly exhausted; this is a sign to move logic into code
  (theme D).
- **The replay test needs re-recording after every packet change.** Fine, but it hides nothing only if every
  re-record is a deliberate step after review.
- **Patch accumulation.** The engine now carries about 10 rule-adjacent stopgaps with `ponytail:` comments or
  ledger rows (keyword lists for forbidden kinds, `settle_who` role fit, incident binding, riding match key,
  cleanse heuristic, first-name matching). Each is reasonable alone; together they are a second, implicit
  rulebook. The structural work below should absorb them.
- **Haiku is not Gemini.** Model-specific behaviour (verbosity, schema adherence, how often it invents) will
  differ. Validate the final state with the real Gemini model (the owner runs it; about 1–3¢ per turn).

---

## 6. Structural analysis: why the patches cluster

**A. The store is too thin for a truth-gated narrator.** *(the largest)*
The rules enforce "only what the store holds may be stated", but the world seed stores very little: places
with only a name, NPCs without knowledge, incidents without a subject.
- **Result:** vague prose, NPCs who can't answer, unreadable notices, empty successes.
- **Issues:** I-127, I-130, I-140, I-145, I-148, I-153, P-054, P-061, P-067, P-110, P-120.

**B. The narrator–checker loop reverse-engineers prose.**
A second model guesses what the prose claimed, code judges the guesses, and each redraft re-guesses.
Extraction is the noisiest step.
- **Issues:** P-002, P-018, P-079, P-112, I-131, I-135.

**C. NPC agency is "forbidden unless sourced".**
Every ordinary NPC behaviour (replying, reacting, moving, being present) needed its own exception.
- **Issues:** I-128, I-140, P-026, P-056, P-095, P-099, P-118.

**D. The language models make choices that code could make.**
The Reader and Framer choose verbs, licences, gates and tiers from large option sets. Wrong picks cause
redirects, forceful framings and harsh odds.
- **Issues:** P-004, P-023, P-031, P-038, P-049, P-064, P-115, P-122, P-123, I-158.

**E. Difficulty has no rubric.** Tier and snag choice is left to the model. *(I-143, I-155, I-158)*

**F. Player-facing blocks are rules text, not UX.** *(I-134, I-138, P-028, P-044, P-092)*

**G. Text is rendered by munging strings.** Fallback "You …" rewriting, `fact_sentence`, OFFER clean-up and
negation all needed repeated fixes. *(P-003, P-040, P-077, P-091, P-096, P-097, P-108, P-126)*

**H. The engine misses parts of the rules.** Combat, riding, cleanse, progress clocks, literacy, knowledge
records and name knowledge were discovered missing only in play.

---

## 7. Recommendations

Use the project's process: rules changes are revisions with DL entries, re-assembled appendices, anchors and
a clean validator; engine changes go through spec-kit (specify → plan → tasks → analyze → implement).

1. **Owner decisions first: I-153 (content policy) and I-158 (difficulty).** Most of themes A and E hang on
   them. Present 2–3 options each, with tradeoffs.
2. **Theme A, a content contract (rules revision plus engine feature).** Three tiers:
   - atmosphere is free;
   - ordinary furniture and common knowledge are written on mention, including NPC common knowledge on a
     successful Talk;
   - consequential content (clues, secrets, people with wants, adversaries) comes only from tables or
     generators.

   Plus a **richer seed**: every NPC gets 2–4 knowledge facts and a stance; every place gets a look, 2–4
   furniture items and exits; every incident gets a subject, a reporter, witnesses and clues. This retires
   the stopgaps `settle_who`, incident binding and the forbidden-kind keyword list.
3. **Theme B, narrator declares, checker verifies.** The narrator returns prose plus a structured list of the
   facts it asserts and the new elements it introduces (extending `mentions`). Code checks declarations and
   samples undeclared sentences. Keep the Checker as a cheap second pass for undeclared assertions only.
4. **Theme C, a default NPC layer.** Each turn every present NPC gets a disposition-driven response
   (12.11 / ch.15 standing, wants, refusals), using the World role and tables. An addressed NPC always
   answers. Positions are part of every resolved beat.
5. **Theme D, code decides, the model proposes.**
   - The gate is computed from verb plus held licences plus the verb's excludes.
   - The Reader names only a verb (short list), target and method.
   - The Framer's tier comes from a rubric lookup that the model can only nudge one step, with reasons.
6. **Theme E, a difficulty rubric plus a simulation.** Use the project's existing sim habit:
   `rules/_process/simulation/`, with seeded output committed.
7. **Theme F, a presentation spec.** A player-facing glossary, plain-English block templates, and one menu
   convention.
8. **Theme G, a small rendering layer.** Templates over typed fields (subject, verb lemma, object, tense,
   person), never regex over model text.
9. **Theme H, a coverage audit.** List every PR- procedure and numbered rule against engine call sites
   (rq.py `--refs` plus grep). This finds gaps before players do.
10. **Then resume playtests** at lower intensity (2 personas) as a regression monitor, and validate once with
   real Gemini.

---

## 8. Research directions

**Rules and design (for themes A, C, E):**
- **Investigation design:**
  - The *Three Clue Rule* and node-based scenario design (The Alexandrian blog).
  - GUMSHOE's "core clues are never gated by a roll". This directly answers P-120 / I-153: a success should
    never yield nothing.
- **Fail forward and partial success:**
  - PbtA moves (10+ / 7–9 / 6−).
  - *Blades in the Dark*'s position and effect, which separates risk from payoff. Relevant to I-158 and to
    what "Go big" should mean.
- **Oracles and generators:**
  - The *Mythic Game Master Emulator*, and *Ironsworn* / *Starforged* oracle tables (answers with content,
    not only yes/no).
  - *Dwarf Fortress* legends and lazy, on-demand world generation (generate when observed, then persist).
- **Storylets and quality-based narrative:**
  - Emily Short's writing on storylets.
  - Failbetter's *Fallen London* (QBN): structured content with preconditions, a good fit for a store-backed
    world.
- **NPC social simulation:**
  - *Versu* (social practices), *Prom Week* / Comme il Faut, and *Façade*'s drama manager. Models for theme
    C's default NPC layer.

**Tech stack (for themes B, D, G):**
- **Structured or constrained generation:**
  - JSON schema-constrained decoding (already used).
  - Plan-then-write: the model emits a plan or fact list, then prose conditioned on it.
  - Grammar-constrained outputs, to shrink the Reader's and Framer's choice surface.
- **Claim verification:**
  - Atomic fact decomposition and verification (FActScore-style).
  - Self-consistency checks.
  - Prefer deterministic checks over LLM-as-judge where possible.
- **LLM agents as playtesters:** persona-based automated testing, and how to calibrate LLM player notes
  against humans (our notes ran consistently negative). Consider a fixed seed-and-script regression set
  alongside free play.
- **Cost and latency:**
  - Prompt caching, since the packets are about 15k tokens and mostly stable.
  - Fewer model calls per turn: merge the Checker into the Narrator under theme B.
  - A long-lived model session instead of a CLI process per call, for the harness.
- **Model portability:** keep the model adapter thin. Behaviour differs between Haiku and Gemini Flash, so
  run the same persona set against both before shipping.

---

## 9. Quick reference

- **Run one playtest:**

  ```bash
  py -3.12 evals/playtest.py --engine claude --player claude --engine-model haiku --persona talker --turns 15 --quick-setup
  ```

  Add `--out` and `--saves` to choose where transcripts and saves go.
- **Free offline smoke run:** `py -3.12 evals/playtest.py --engine offline --player script --quick-setup --turns 8`
- **Full suite:** `PYTHONUTF8=1 py -3.12 -m pytest -q -p no:cacheprovider` (about 3 min).
- **Re-record the replay** after an intended packet change: `py -3.12 -m tests.replay.record_games`.
- **Rules gate:** `py -3.12 rules/_process/validate_ruleset.py` must show 0 ERROR / 0 WARN.
- **Rule lookup:** `py -3.12 rules/tools/rq.py <id>`. Never read whole chapters; `rules/` is about 500k words.
- **Logged reasons a model answer was rejected:** `model_calls.response.rejected` in a save.
- **Recover a traceback from a save:** check out its commit in a temporary worktree and run
  `Game.replay(<save>)`.
