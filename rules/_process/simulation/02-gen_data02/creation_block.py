CREATION_BLOCK = """creation_defaults:          # what the fast path uses when the player makes no choice (02.2.2)
  people: orig.people.human
  livelihood: orig.life.soldier
  first_seven: [orig.life.soldier, orig.life.hunter, orig.life.thief, orig.life.healer, orig.life.apprentice, orig.life.performer, orig.life.wanderer]   # shown first at C1 (PR-02-7)
  shape: peaked
  typical_rule: true                 # a non-human people defaults to its Typical rule
  birth_circumstance: unremarked
  second_tongue: lic.lang.dwarvish   # ch.13 overrides with its region's commonest second tongue
  learning_pick_order: [lic.lang.letters, "raise lic.lang.common one grade (if below native)", "the second tongue at accented", lic.lang.old_tongue]
  human_extra_training: "the first tag on the livelihood's list that no pick has taken"
  kit_choice: first_option
  bonds: {anchor: "the upbringing's first bond seed", thorn: open}
  faction_tie: open
  true_thing: open
  aspiration: "the one the drive answer names, else open"
  pacing_profile: standard
  pillar_weights: same
bond_kinds:                 # 02.9.2; standing on the 00.3.16 scale, set (not rolled) because a bond is not a first impression
  anchor: [{id: kin, standing: 2}, {id: friend, standing: 2}, {id: mentor, standing: 1}, {id: ward, standing: 2, commitment: "they depend on you"}]
  thorn: [{id: rival, standing: -1}, {id: creditor, standing: 0, commitment: "a debt you owe them"}, {id: enemy, standing: -2}, {id: lost, standing: null, hook_kind: question}]
faction_tie_brackets:       # 02.9.5; audited brackets, not a point pool (P11)
  - {id: none, ties: []}
  - {id: foot_in_the_door, ties: [1]}
  - {id: sworn_and_hunted, ties: [2, -2]}
tables:                     # Fate's hand (02.2.2): rolled by roll_table when the player says "surprise me"
  - id: tbl.creation.people
    die: d100
    results: [{range: [1, 55], result: orig.people.human}, {range: [56, 65], result: orig.people.dwarf}, {range: [66, 75], result: orig.people.elf}, {range: [76, 83], result: orig.people.halfling}, {range: [84, 89], result: orig.people.orc_kin}, {range: [90, 93], result: orig.people.goblin_kin}, {range: [94, 97], result: orig.people.beastfolk}, {range: [98, 100], result: orig.people.giant_kin}]
  - id: tbl.creation.upbringing
    die: d100
    results: [{range: [1, 30], result: orig.up.village}, {range: [31, 42], result: orig.up.wilds}, {range: [43, 54], result: orig.up.streets}, {range: [55, 66], result: orig.up.townhouse}, {range: [67, 76], result: orig.up.road}, {range: [77, 86], result: orig.up.sea}, {range: [87, 92], result: orig.up.cloister}, {range: [93, 96], result: orig.up.court}, {range: [97, 100], result: orig.up.bonded}]
  - id: tbl.creation.livelihood
    die: d100
    results: [{range: [1, 5], result: orig.life.soldier}, {range: [6, 10], result: orig.life.hunter}, {range: [11, 15], result: orig.life.rider}, {range: [16, 20], result: orig.life.laborer}, {range: [21, 25], result: orig.life.thief}, {range: [26, 30], result: orig.life.charlatan}, {range: [31, 35], result: orig.life.sailor}, {range: [36, 40], result: orig.life.herder}, {range: [41, 45], result: orig.life.scholar}, {range: [46, 50], result: orig.life.healer}, {range: [51, 55], result: orig.life.apprentice}, {range: [56, 60], result: orig.life.acolyte}, {range: [61, 63], result: orig.life.hedge_taught}, {range: [64, 65], result: orig.life.touched}, {range: [66, 70], result: orig.life.merchant}, {range: [71, 75], result: orig.life.performer}, {range: [76, 80], result: orig.life.courtier}, {range: [81, 85], result: orig.life.artisan}, {range: [86, 90], result: orig.life.watchman}, {range: [91, 95], result: orig.life.tinker}, {range: [96, 100], result: orig.life.wanderer}]
concept_branches:           # 02.2.4: classify a described concept by branch first, then within the branch
  deed.martial: [orig.life.soldier, orig.life.rider, orig.life.laborer, orig.life.watchman]
  deed.guile: [orig.life.thief, orig.life.charlatan]
  deed.wilds: [orig.life.hunter, orig.life.herder, orig.life.sailor, orig.life.wanderer]
  deed.lore: [orig.life.scholar, orig.life.healer, orig.life.watchman]
  deed.arcane: [orig.life.apprentice]
  deed.divine: [orig.life.acolyte]
  deed.primal: [orig.life.hedge_taught, orig.life.touched]
  deed.influence: [orig.life.merchant, orig.life.performer, orig.life.courtier]
  deed.craft: [orig.life.artisan, orig.life.tinker, orig.life.laborer]
"""
