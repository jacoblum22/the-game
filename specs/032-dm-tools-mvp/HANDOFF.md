# HANDOFF 032 (slice 1: design only; nothing implemented)
Done: spec.md, cases.md, plan.md, tasks.md in specs/032-dm-tools-mvp/. Branch: worktree-agent-afa629b34a41df390.
Phases (lane, model): P1 harness+held-out labels (E, Sonnet) || P2 Role.DM + engine stored in save (R+G, Sonnet) ->
P3 tools: prose-only people, items, OFFER words (T, Sonnet) -> P4 world step: fights, time, clocks, leads, cuts (W, Sonnet;
Opus if re-ask ordering bites) -> P5 told/presence/pronouns/leak audit (C, Sonnet); P6 /fix on dm-tools (F, Opus; after P3,
beside P4/P5) -> P7 confirming head-to-head + default flip (E+G, Sonnet, owner gate). Start each with `git reset --hard` the prior branch.
Traced (fighter save): no conflict ever started because "the beast" was refused as a target and the retry dropped it; the
"promised roll" turn made zero tool calls with no fight facts in context. Fix = real foe + fight block + one judgment sentence.
Traps: (1) old saves have no `engine` key; read the store, never `GameConfig()` default, or the flip breaks them.
(2) `beat_cost(free)` is 0 and `_open_scene` takes the store default as free: the clock stays still unless scene mode is site.
(3) dm_tools.py is shared by P3-P5: run them in order. P6 must not edit it. (4) Unverified items: plan.md, section Analysis.
(5) tests/fixtures/scene_dock.py exists; spec 028 schema (addressee/cost) does not, so the pipeline npc_agency arm is the old arm.
Assumptions for the owner (spec.md A1-A9): one exchange = one beat; no Director call, code-only scene cuts; DM lists `said`;
creatures made as `mind: animal`; confirm on Haiku (Gemini Flash later); gate numbers C1-C11 are my proposal.
