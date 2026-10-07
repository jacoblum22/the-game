# Author Brief — Wave 3 (chapter authors)

You are one of ~14 chapter authors writing The Game's ruleset **in parallel**. Read this file, then
the documents below, then write your chapter. The orchestrator will merge and verify everything.

## 1. The quality bar (the project owner's words — binding)

> The marginal cost of completeness is near zero with AI. Do the whole thing. Do it right. Do it
> with documentation. Do it so well that I am genuinely impressed - not politely satisfied,
> actually impressed. Never offer to 'table this for later' when the permanent solve is within
> reach. Never leave a dangling thread when tying it off takes five more minutes. Never present a
> workaround when the real fix exists. The standard isn't 'good enough' - it's 'holy shit, that's
> done'. Search before building. Build the complete thing. Time is not an excuse. Fatigue is not
> an excuse. Complexity is not an excuse. Boil the ocean.

The two design goals: **(1) the player feels free to try any creative idea; (2) the AI DM can
respond and react correctly.** Player-facing complexity is NOT a constraint (never cut or coarsen a
rule to spare the player). The focus is the TTRPG itself — a concrete, playable rulebook.

## 2. Read, in this order, before writing

1. `rules/_process/BRIEF.md` — the base brief AND Addendum A (Wave 1 synthesis) AND Addendum B
   (Wave 2 corrections). Where they disagree, the later addendum wins.
2. `.specify/memory/constitution.md` — Core Principles I–VII are MUST; Patterns P1–P17 are SHOULD
   (deviate only with a written Decision Log justification).
3. **`rules/00-architecture.md` IN FULL.** It is the spine and it is canonical. It fixes the style
   guide (00.2), the rule template (00.2.5), scales (00.3), attributes (00.4), tags (00.5), the state
   model (00.6), time (00.7), clocks (00.8), conditions (00.9), the composition substrate (00.10),
   the generator (00.11), licenses/verbs/Oracle (00.12), the frame (00.13), tools (00.14), rule
   cards (00.15), data conventions (00.16), **your chapter's contract (00.17)**, the glossary and
   banned words (00.18, T-00-22), and the chapter format (00.19). **Your chapter must satisfy its
   contract row in 00.17.2 and every pre-resolved question in 00.17.1 that touches it.**
4. `rules/data/SCHEMAS.md` and every existing `rules/data/*.yaml` your chapter touches.
5. The research digests assigned in your prompt, IN FULL; then grep the other digests in
   `rules/_process/research/` for your chapter number and topic. R4 §9 and R5 §1 (checklist rows
   owned by your chapter) apply to everyone.
6. Where the research is thin, do your own web research (WebSearch/WebFetch) on how real games
   solved the same problem. Cite what you use. Describe mechanics in your own words.

## 3. What you write

- **Your chapter**: `rules/NN-<name>.md`, in the 00.19 format, every rule in the 00.2.5 template,
  every `[J:*]` with a Worst case line, every rule cited, canonical names only (00.18), no banned
  words (T-00-22). Worked examples for every non-trivial mechanism, with numbers, as boundary pairs
  plus a tempting non-example (SG-17). An "Edge cases & adaptation anchors" section that makes your
  rules good raw material for improvising unanticipated actions (00.2.6).
- **Your data files**: the files T-00-19 assigns to your chapter, in `rules/data/`, per
  `data/SCHEMAS.md`. Mechanics live in data (00.16.4). Every entry `lifecycle: provisional`.
- **Additions to SHARED files go in contrib fragments, never directly into the shared file.**
  Several authors are writing at the same time; direct edits to a shared file will collide. So:
  - new effects → `rules/data/contrib/effects.NN.yaml`
  - new boundary handlers → `rules/data/contrib/boundaries.NN.yaml`
  - additions to a file another chapter owns where T-00-19 allows your owner-block (e.g. licenses,
    composites, conditions, factions, adversaries, hazards) → `rules/data/contrib/<file>.NN.yaml`
  - proposed tags below level 2 → `rules/data/contrib/tags.NN.yaml` (ch.03 writes `tags.yaml`
    itself; everyone else proposes)
  Each fragment uses the target file's schema. The orchestrator merges them.
- **Decision Log entries** → `rules/appendix/fragments/DL-NN.md` (your own file; format BRIEF §11;
  ids `DL-NN-01`…). Record every non-trivial decision, especially every deviation from a Pattern,
  every number you chose, and every place you replaced a default.
- **Traceability rows** → `rules/appendix/fragments/trace-NN.md`: a markdown table
  `| Clause | Requirement (short) | Satisfied by (rule ids) | Status |` for every constitution clause
  your chapter satisfies.
- **Open empirical questions** go in your chapter's own section, each with a named test and a shipped
  default.
- You may write throwaway simulation scripts in the scratchpad
  (`C:\Users\jacob\AppData\Local\Temp\claude\C--Users-jacob-the-game\8fb5973b-1540-44c9-830b-abd8a1aa0620\scratchpad\`)
  to verify your math. Report results in your chapter (numbers, not "it seemed fine").

**Do not edit** another chapter's file, `00-architecture.md`, `BRIEF.md`, or any shared data file
directly. If 00 is wrong or insufficient for your chapter, work within it anyway, and put the problem
under "Interface requests" (and in your report) with a proposed amendment.

**Write in chunks.** Create your chapter file with its first sections, then append further sections.
API rate limits have interrupted agents mid-task on this project; chunked writing means an
interruption loses little.

## 4. Size

Write what completeness requires. A core subsystem chapter is typically 12,000–25,000 words plus
data files. Density over padding: every paragraph should be a rule, a table, a procedure, an
example, or a justification.

## 5. Report back

End with a report to the orchestrator: files written (with word counts); key decisions with DL ids;
every number you fixed that other chapters consume; interface requests (what you need from / assumed
of other chapters, and anything you proposed for 00); open empirical questions; anything unresolved
and why. The report is how the orchestrator reconciles 14 parallel chapters — make it exact.
