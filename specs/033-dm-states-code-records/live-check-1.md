# Spec 033 live check 1 (2026-10-11, spec033-base da1f6f2, Haiku DM, Sonnet player)

Runs (saves under `saves/`, reports under `evals/playtests/spec033-p7/`):
- talker, fighter and explorer at 15 turns (stamp 20261011-005927);
- fighter at 25 turns (20261011-011012);
- the 24 held-out items (`heldout/heldout.json`): 14 pass, 6 judge, 4 fail.

## Numbers
- Tokens in per turn: 23k (15-turn runs), 27k (fighter25).
- Latency per turn: 17-19 s. Model calls per turn: 1.8-2.2.
- `not_chosen` defaults: 1 force (45 turns); 1 fail_on (fighter25). The DM fills almost every field.
- Walk-ons: `as` given on almost every person slot. No "you"/made-up-id walk-ons were seen.
- LEAD DUE is told every ~6 turns: talker 3x, explorer 2x, fighter25 2x. Whether the DM acted on it is not traced yet.
- **Fights: 0 in all four persona games** (C8: 0 fights / 0 exchanges / 0 foe turns). There were no `change fight` calls at all.

## Traced problems (from the tool calls in the saves and heldout.json)
1. **Melee is refused until a position is stated, and the DM cannot state one.**
   - fighter25 has 6 refusals: every strike was refused "not in reach (no position recorded)".
   - The DM's `change position` attempts swap the fields:
     - `who=pc what=close to=close`;
     - `who=npc.x to=engaged what=engaged`;
     - `to=pc.calella_stoneby what=engaged`.
   - H01: `who=npc.the_wolfhound what=npc.the_wolfhound to=engaged` was ACCEPTED ("engaged to the wolfhound", a self-band). The strike was then refused again.
   - H05: `who=npc what=engaged to=loc.the_tavern_yard` moved the NPC to the place. The grapple was refused 3 times.
   - Causes:
     - P3's `_reach` refuses an unrecorded band, and nothing records one unless the DM states it;
     - the `position` fields (`who`, `what` = other party, `to` = band) are misread;
     - `_position` accepts who==what and band words in `what`.
2. **No fight ever starts.** Since P2a, only `change fight` starts one. The DM never called it in 4 games. So no foe ever acts. H07-H12 pass only because their scene starts with a conflict already on.
3. **The same creature is made twice (H01).**
   - `new_npc` got a description in `what` and no `name`, so the recorded name is "wolfhound, the size of a calf, lips pulled back".
   - The next roll's target "the wolfhound" is not an exact name, so a second walk-on `npc.the_wolfhound` is made. The DM did not reuse the id it was given.
4. **H10:** the evade roll stated no `move_to`, so the bands never widened, the foe stayed engaged, and the DM picked strike. The code is correct for the recorded state. The DM omitted the move.
5. **Player notes** are narration-level:
   - asked for a year that was never shown;
   - coins that were never taken out;
   - "succeed and pay" felt like double cost;
   - a 10% run up a track.

## Proposed (decision for the owner on 2)
- **1 (D3, no new principle):**
  - An unrecorded band is an omitted detail. A melee roll at someone with no band on record takes `engaged`, logged as `not_chosen:position`.
  - Refuse only when a RECORDED band says out of reach.
  - `_position` refuses who==what and a `what` that is not a party. The refusal shows one exact example.
- **2 options:**
  - A: attack rolls carry `starts_fight` (yes/no) and a start band. Omitted with no fight on = yes, near, logged.
  - B: messages only.
  - C: a rule makes any attack on an able creature start a fight (the code-started fight the owner deleted).
- **3:** prompt/contract: `new_npc name` = the short label the DM will use. If omitted, use `what`, logged. No fuzzy matching.
