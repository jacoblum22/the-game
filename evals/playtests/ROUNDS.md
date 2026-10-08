# Playtest rounds

Engine model: Claude Haiku 5.5 via the Claude Code CLI; player: Claude Sonnet. No Gemini, no API spend.

## Round 1 (code ead9d5c, 5 personas × 40 inputs, ~25 of them setup)

| Persona | Play turns | Narrator calls/turn | Fallbacks | Notes |
|---|---|---|---|---|
| breaker | 7 | 2.14 | 3 | setup help loops (P-013), hidden lists |
| newcomer | 18 | 1.39 | 6 | never got the scene described (P-018) |
| explorer | 16 | 3.06 | 12 | fallback debug text, "what do I know" loops (P-019) |
| talker | 18 | 2.67 | 13 | raw NPC-action text (P-021), duplicate OFFER (P-020), rejected model output (P-022) |
| fighter | 18 | 2.67 | 9 | intent substitution to violence (P-023), odds on trivial acts (P-024) |

Fixed and merged into integrate-r1 (12f51f2), suite 996 passed, validator 0/0:
P-001 Oracle crash leak + CLI never prints engine errors · P-002 claim-check convergence · P-003 fallback reads as
fiction, time costs in words · P-004 held licence passes the gate · P-006/P-009/P-010/P-013/P-014 setup questions
answered, full lists, glosses, pronoun with name · P-016/P-018 mixed OOC+fiction messages narrated, checked
sentences delivered past the redraft budget. Harness: quick setup, 15-turn limit, faster CLI, pinned worktrees.
Ledger: I-131..I-136.

## Rolling runs (from 12f51f2)

| Run | Code | Play turns | Narrator calls/turn | Fallbacks | Main findings |
|---|---|---|---|---|---|
| breaker 170157 | 12f51f2 | 17 | 1.94 (r1 2.14) | 2 (r1 3 of 7) | prose now good; NPC replies cut (P-026); OFFER leaks (P-027); pause questions (P-028) |
