# Handoff (2026-10-15)

For a Claude Code session picking this work up on another machine. Read `README.md`, `LESSONS.md` and
`evals/autoloop/LOG.md` too.

## Where things are
- `main` on GitHub is the owner's approved version (624e3a8). The owner's server runs it.
- Branch `autoloop` holds an autonomous improvement loop the owner asked for on 2026-10-14. Its brief:
  - Play 3 games in parallel (different classes and races), 60 rounds each.
  - Find weaknesses with numbers, two ideas per weakness, A/B test each by replaying rounds.
  - Keep an idea only if it improves things with no side effect (or with a fix for the side effect).
  - Then 60 more rounds of the same games, and again, to 180 rounds each.
  - Then a report.
  Don't merge or push to `main` without the owner.
- Block 1 (rounds 1-60) is done and analysed. Code fixes are made and tested (271 tests). The prompt A/B results are
  preliminary; see the table in LOG.md.

## Next steps, in order
1. Confirm the two leads with more runs (replay.py, about 8 runs per arm, against the baseline). Write fix wording that
   is general, never tailored to the test case.
   - 1B for contradictions: 2 of 36, against 7 of 36 in the baseline.
   - 2A for menus at the end of a reply: 0 of 36, against 4 of 36.

   Keep what holds up in `dm/prompt.md` on `autoloop`, and drop the rest. Log it.
2. Block 2: `py -3.12 evals/autoloop/run.py <cleric|barbarian|bard> 60`, from the repo root with PYTHONPATH set to
   it. Run at most 3 games at once.
   - The Claude Code conversations behind the existing saves weren't moved from the old PC, so check first that a
     save continues. If it doesn't, start three fresh games under new names (e.g. add new briefs to run.py's BRIEFS),
     and note it in LOG.md.
3. After each 60-round block, run the same analysis:
   - metrics.py and fmt.py for the numbers;
   - dump.py, then three Sonnet readers with READ.md;
   - verify the findings, then ideas and A/B tests (blind.py, score.py).
4. After block 3, write the report: what was found, what was fixed, the metrics, and the problems still open. Send
   it to the owner.

## How the owner works (standing notes)
- **Ask before changing behaviour.** Change nothing in the DM's behaviour (prompt, tools, filtering) without the
  owner. The exception is the autoloop branch, which the owner authorised. Report what you observe as observations.
  When showing play, quote the transcript inline; don't send a file.
- **Rules are the spec.** D&D 5e 2014 (SRD 5.1).
  - Build from the rule's procedure.
  - Never skip, batch or simplify a rule step without asking.
  - Never let a default stand in for a choice the rules give someone.
  - Never rewrite a rule to fit the code.
  - SRD text is copied by code, never retyped.
- **No fiction inference in code.** Code never deduces positions, presence, identity or what happened from actions or
  names. Only the DM's tool calls set story state.
- **Observe before solving.** Let the DM run free. Fix only problems seen in play, not ones only anticipated.
- **Trace before diagnosing.** Never state a cause from the surface: read the save, the model's input and output,
  and the code first. Most first guesses have been wrong.
- **Check what matters.** False positives are the bigger risk. Prefer narrow checks for things that break rules or
  spoil secrets. Prefer removing friction to adding procedure.
- **Stop pushing, not tracking.** Code gives the DM facts, never orders about how people react or what they say. Don't
  add usage-tracking gates for repeated details.
- **No test-tailored fixes.** A fix's wording must not name or hint at the failing test case. Every fix must also
  pass made-up and edge cases, and a held-out set.
- **PC past when asked.** The DM supplying the character's past is fine when the player asks; only unprompted
  invention is a problem.
- **Story facts deferred.** The DM's improvised facts drift. A fix is agreed in principle but deferred: notes
  written after the DM says something, never pre-planned lore.
- **Owner updates:**
  - Plain words with concrete examples, short enough for a phone.
  - After a playtest round: what the last fixes achieved (with numbers), then problem families by traced cause (in
    plain words, the real instance, a made-up example, the fix), the order to do them in, and the decisions needed,
    each with options and a recommendation.
- **Agents:** use Sonnet subagents for well-defined slices, and Opus only for design or tracing. Keep it to 2-3 at a
  time.
- **Practical:**
  - Never commit or handle credentials. The owner sets the API key themselves.
  - Ask before pushing.
  - The repo may go public later, so commit nothing sensitive.
  - On Windows, edit code with the Edit tool, not Git Bash heredoc Python (it mangles `\n` escapes).
