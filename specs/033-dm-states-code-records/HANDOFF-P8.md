# HANDOFF 033 P8 (fixes from live check 1; base spec033-base ac701e1)
Done [owner ruling 2026-10-11]: `propose_roll` gets `starts_fight` ("", yes, no) and `fight_to` ("", band). `_attack_starts_fight`
(dm_tools.py) runs after `_stated`, BEFORE `_reach`, for a Strike/Grapple/Force at an npc/adversary that `_acting` lets act.
Blank/yes starts the fight through `_fight`; blank logs `not_chosen:fight.starts`, blank `fight_to` logs `not_chosen:fight.to`
and takes the weapon's first band (`_reach_bands`: engaged for melee/Grapple/Force, close for a bow). A band already RECORDED
stays when `fight_to` is blank. "no" = one blow. A roll that starts a fight prefixes "A fight begins with X, at range B."
Live fight, target already a foe: ignored (no restart, band, Vitality, conflict, default). Live fight, newcomer: `_fight` ->
`conflict.start` joins him (Vitality if none, band set if `fight_to` given or none recorded, foes list appended; mode, boundary,
conflict meta `previous` and the other foes untouched). Nothing is restarted or reset. Trap: `_fight` answers a joined newcomer
"already in the fight (or cannot be a foe)" (start() returns False whenever a conflict exists); harmless, text only.
Reach: no band recorded -> first reachable band written, `not_chosen:position`; recorded band out of reach -> REFUSED with
`change kind=position who=pc to=<band> what=<id>`. `_position`: refuses who==what, a `what` not pc/entity, a `to` neither band nor
place, each with that example; `what=pc` now works. `new_npc`: `not_chosen:name`, result ends "Use <id> for them from now on."
Schema fields carry plain `description`s; dm.md 799 words; offline `_dm` sends one roll (yes, engaged), no move call.
Tests: `tests/engine/test_spec033_p8.py` (H01, H05, fighter25 swaps, recorded near, live-fight cases); old tests updated
(p2a BASE and p3 `roll()` say starts_fight "no"; r16/f11/engine offline). `test_spec033_p8` added to GUARDED. dmtools replay
re-recorded (offline_seed11.json byte-equal); `reached.txt` regenerated.
Open: ranged unrecorded band takes the weapon's first band (close); a companion target gets a band default but starts no fight;
`contracts/dm.md.draft` was not updated (it predates P3). Next: P7 live re-check with these fields.
