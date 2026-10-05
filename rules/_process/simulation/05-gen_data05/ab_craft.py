# deed.craft -- 23 abilities.
from dsl05 import *

C = 'deed.craft.'
T = 'the target'

# ---------------- smithing ----------------
ab('ab.keen_edge', 'Keen Edge', C + 'smithing.weapons', 1, 'hone', 'Working', 'beat',
   'Put a working edge or face on a weapon.',
   'Applies to one metal weapon you can work on for an interval with a whetstone or tools.',
   [rk("Work on one metal weapon for an interval: until its wielder's next long rest it deals +1 harm, and its first Strike in each scene holds an Amplifying lever.",
       [hedge(1, 'a Strike with the honed weapon'), lev('amplifying', "the honed weapon's first Strike in a scene")]),
    rk("Work on up to three metal weapons for an interval: until each wielder's next long rest each deals +1 harm, and its first Strike in each scene holds an Amplifying lever.",
       [hedge(1, 'a Strike with a honed weapon'), lev('amplifying', "a honed weapon's first Strike in a scene"), tgt(2)]),
    rk("Work on up to four metal weapons for an interval: until each wielder's next long rest each deals +2 harm, and its first Strike in each scene holds an Amplifying lever.",
       [hedge(2, 'a Strike with a honed weapon'), lev('amplifying', "a honed weapon's first Strike in a scene"), tgt(3)])],
   attr='intellect', x=[('wooden, bone or natural weapons', 'ab.fletch_true; the weapon\'s own maker'), ('harm edge beyond +2 in total', 'the cap holds (00.10.6)')])

ab('ab.masterwork', 'Masterwork', C + 'smithing.armor', 4, 'fine_smithing', 'Edge', 'passive',
   'Draw from metal the best it can be made into.',
   'Applies to crafting beats under deed.craft.smithing.',
   [rk("+1 to smithing beats, their reach is one rung higher, and each success ticks the work's project clock one segment more.",
       [edge(1, 'deed_tag under deed.craft.smithing'), reach('deed_tag under deed.craft.smithing'), tick("the work's project clock", 1)])],
   x=[('a quality rung above what the materials allow', 'materials gate the pool (08)')])

# ---------------- woodcraft ----------------
ab('ab.fletch_true', 'Fletch True', C + 'woodcraft.bowyery', 1, 'fletching', 'Permission', 'beat',
   'Make sound arrows from what the land gives.',
   'Applies where wood or reed can be cut; takes an interval.',
   [rk("In an interval, make or mend a quiver's worth of ammunition from wood at hand.",
       [perm(2), fact("the pc's ammunition", 'replenished_by', 'one unit')]),
    rk("In an interval, make or mend a quiver's worth of ammunition from wood at hand; shots with it deal +1 harm until your next long rest.",
       [perm(2), fact("the pc's ammunition", 'replenished_by', 'one unit'), hedge(1, 'a Strike with ammunition you made')]),
    rk("In an interval, make or mend a quiver's worth of ammunition from wood at hand; shots with it deal +1 harm and gain +1 until your next long rest.",
       [perm(2), fact("the pc's ammunition", 'replenished_by', 'one unit'), hedge(1, 'a Strike with ammunition you made'), edge(1, 'a Strike with ammunition you made')])],
   attr='agility', x=[('making a bow', 'a crafting project under lic.training.craft_woodcraft (08)')])

ab('ab.sound_timber', 'Sound Timber', C + 'woodcraft.carpentry', 2, 'barricade', 'Working', 'beat',
   'Close an opening with wood so that it stays closed.',
   'Applies to one door, window or gap, with timber or furniture at hand; takes an interval.',
   [rk("In an interval, bar or barricade one opening. Forcing it is against your effect DC; one being behind it holds flag.in_cover; and beats to hold it are framed one stakes rung lower.",
       [perm(2), move('one being behind the barricade', 0, add=['flag.in_cover']), lev('protective', 'beats to hold the barricade', 'scene')]),
    rk("In an interval, bar or barricade up to three openings. Forcing each is against your effect DC; those behind them hold flag.in_cover; and beats to hold them are framed one stakes rung lower.",
       [perm(2), move('each being behind a barricade', 0, add=['flag.in_cover']), lev('protective', 'beats to hold the barricades', 'scene'), tgt(2)])],
   attr='intellect', traits=['trait.sense.loud'], x=[('stone or iron openings without timber', 'lic.training.craft_building; ab.stone_shape')])

# ---------------- leathercraft ----------------
ab('ab.field_patch', 'Field Patch', C + 'leathercraft.goods', 1, 'mend_gear', 'Permission', 'beat',
   'Make damaged gear serve a while longer.',
   'Applies to one damaged item of leather, cloth, wood or mail, at a breather, with a kit.',
   [rk("At a breather, with a kit, mend one damaged item to working order until your next long rest.",
       [perm(2), fact('the item', 'condition', 'serviceable until the next rest_long')]),
    rk("At a breather, with a kit, mend up to three damaged items to working order until your next long rest.",
       [perm(2), fact('each item', 'condition', 'serviceable until the next rest_long'), tgt(2)]),
    rk("At a breather, with a kit, mend up to three damaged or broken items to working order until your next long rest.",
       [perm(4), fact('each item', 'condition', 'serviceable until the next rest_long'), tgt(2)])],
   attr='agility', x=[('a lasting repair', 'a crafting beat (08)'), ('blades and plate', 'lic.training.craft_smithing')])

ab('ab.cure_hide', 'Cure Hide', C + 'leathercraft.tanning', 3, 'harvest', 'Edge', 'passive',
   'Take whole what a carcass has to give.',
   'Applies to beats that harvest hide, bone, gland or scale from a creature.',
   [rk("+1 to beats that harvest materials from a creature, and their reach is one rung higher.",
       [edge(1, 'the beat harvests materials from a creature'), reach('the beat harvests materials from a creature')]),
    rk("+2 to beats that harvest materials from a creature, and their reach is one rung higher.",
       [edge(2, 'the beat harvests materials from a creature'), reach('the beat harvests materials from a creature')])],
   x=[('taking the creature\'s power', 'the Taking (04.10)')])

# ---------------- textiles ----------------
ab('ab.knot_lore', 'Knot Lore', C + 'textiles.ropework', 1, 'ropes', 'Lever', 'passive',
   'Tie a rope so that it holds or gives exactly as meant.',
   'Applies to climbs, descents, hauls and bindings secured by a rope you tied.',
   [rk("A rope you tied is a Protective lever on climbs, descents and hauls it secures.",
       [lev('protective', 'Exert beats secured by a rope you tied', 'scene', verbs=['verb.exert'])]),
    rk("A rope you tied is a Protective lever on climbs, descents and hauls it secures, and you gain +1 to beats that bind or untie.",
       [lev('protective', 'Exert beats secured by a rope you tied', 'scene', verbs=['verb.exert']), edge(1, 'the beat binds with rope or works a knot')]),
    rk("A rope you tied is a Protective lever on climbs, descents and hauls it secures, you gain +1 to beats that bind or untie, and a being you bound takes -2 to slip your knots.",
       [lev('protective', 'Exert beats secured by a rope you tied', 'scene', verbs=['verb.exert']), edge(1, 'the beat binds with rope or works a knot'), ({'effect_id': 'eff.status_modifier', 'params': {'amount': -2, 'applies_when': 'a being bound by your knots attempts to slip them'}}, 2)])],
   x=[('chains and manacles', 'lic.training.craft_artifice')])

ab('ab.fine_cloth', 'Dressed for It', C + 'textiles.tailoring', 2, 'garb', 'Working', 'beat',
   'Fit a person\'s clothes to the room they must enter.',
   'Applies to one wearer and one named occasion, with an hour and a tailor\'s kit.',
   [rk("In an hour, fit one wearer's garb to a named occasion: there the wearer holds a Precision lever on Talk beats, and the snag for looking out of place is waived.",
       [lev('precision', "the wearer's Talk beats at the named occasion", 'scene', verbs=['verb.talk']), waive('the snag for looking out of place', 'the wearer is at the named occasion')]),
    rk("In an hour, fit up to two wearers' garb to a named occasion: there each holds a Precision lever on Talk beats, the snag for looking out of place is waived, and a disguise built on the garb has +1 to its effect DC.",
       [lev('precision', "the wearers' Talk beats at the named occasion", 'scene', verbs=['verb.talk']), waive('the snag for looking out of place', 'a wearer is at the named occasion'), tgt(1), dcedge(1, 'observers study a disguise built on the garb')])],
   attr='agility', x=[('passing as a specific person', 'ab.living_mask')])

# ---------------- alchemy ----------------
ab('ab.quick_tincture', 'Quick Tincture', C + 'alchemy.potions', 1, 'brew_remedy', 'Working', 'beat',
   'Brew a small remedy from a kit and a fire.',
   'Applies at a rest with an alchemist\'s kit and reagents; the doses keep until your next long rest.',
   [rk("At a rest, brew two doses. Drinking one restores 3 Vitality or ends poisoning (the drinker chooses).",
       [heal(3, 'the drinker'), cleanse('cond.poisoned', 'the drinker'), fact('the pc', 'holds_item', 'two doses of tincture'), tgt(1)], per='rest_long'),
    rk("At a rest, brew three doses. Drinking one restores 5 Vitality or ends poisoning (the drinker chooses).",
       [heal(5, 'the drinker'), cleanse('cond.poisoned', 'the drinker'), fact('the pc', 'holds_item', 'three doses of tincture'), tgt(2)], per='rest_long'),
    rk("At a rest, brew four doses. Drinking one restores 5 Vitality, or ends poisoning, or restores 1 Focus (the drinker chooses).",
       [heal(5, 'the drinker'), cleanse('cond.poisoned', 'the drinker'), fact('the pc', 'holds_item', 'four doses of tincture'), tgt(3), foc(1, 'the drinker')], per='rest_long')],
   attr='intellect', oc=1, cost_text='one use of reagents (08)',
   x=[('doses that keep beyond a long rest', 'a crafting project (08)'), ('a drinker already healed twice since its long rest, or past the consumable Focus cap', '05.7.8; 05.6.11')])

ab('ab.firepot', 'Firepot', C + 'alchemy.incendiaries', 2, 'incendiary', 'Working', 'beat',
   'Throw a vessel that bursts into flame.',
   'Applies to a point within band.near and up to two beings within band.engaged of it; uses one prepared pot.',
   [rk("Throw a prepared firepot at a point within band.near (Strike, Agility; one roll against each target's defense). Up to two beings there take Moderate fire harm and are burning.",
       [harm(2, ['harm.fire.flame'], 'each being at the point'), tgt(1), cond('cond.burning', 1, 'scene', 'each being hit')]),
    rk("Throw a prepared firepot at a point within band.near (Strike, Agility; one roll against each target's defense). Up to three beings there take Heavy fire harm and are burning.",
       [harm(3, ['harm.fire.flame'], 'each being at the point'), tgt(2), cond('cond.burning', 1, 'scene', 'each being hit')])],
   attr='agility', check=('aimed', 'verb.strike', "each target's attack defense"), spread='burst', oc=1, cost_text='one prepared firepot (made at a rest with a kit and reagents, 08)',
   harm_tags=['harm.fire.flame'], traits=['trait.action.attack', 'trait.delivery.ranged', 'trait.delivery.area', 'trait.sense.loud', 'trait.sense.visible'],
   x=[('making the pot in the middle of a fight', 'it is prepared at a rest')])

ab('ab.grand_elixir', 'Grand Elixir', C + 'alchemy.potions', 5, 'great_work', 'Working', 'beat',
   'Distil one draught that sets a body right.',
   'Applies at a long rest in a place with an alchemist\'s bench, with rare reagents; the elixir keeps for a season.',
   [rk("Over a watch of work, distil two draughts. Drinking one restores 8 Vitality and 2 Focus and ends poisoning and one other bodily condition.",
       [heal(8, 'the drinker'), foc(2, 'the drinker'), cleanse('cond.poisoned', 'the drinker'), cleanse('one condition of category physical', 'the drinker'), fact('the pc', 'holds_item', 'two draughts of grand elixir'), tgt(1)], f=2, per='rest_long')],
   attr='intellect', oc=2, cost_text='a watch of work and rare reagents of the price band 08 names',
   x=[('wounds and marks', 'ch.07'), ('past the healing cap or the consumable Focus cap', '05.7.8; 05.6.11')])

# ---------------- cookery ----------------
ab('ab.hearty_fare', 'Hearty Fare', C + 'cookery.provisions', 1, 'camp_cook', 'Reaction', 'trigger',
   'Turn rations into a meal that carries people further.',
   'Applies when you cook at a short or long rest for up to three who eat it.',
   [rk("When you cook at a rest, up to three who eat hold a Protective lever on Endure checks against weather and exhaustion until their next rest.",
       [lev('protective', "the eaters' Endure checks against weather and exhaustion", 'scene', verbs=['verb.endure']), tgt(2)], per='rest_short'),
    rk("When you cook at a rest, up to four who eat hold a Protective lever on Endure checks against weather and exhaustion until their next rest, and the meal uses one supply fewer than their number (minimum 1).",
       [lev('protective', "the eaters' Endure checks against weather and exhaustion", 'scene', verbs=['verb.endure']), tgt(3), fact('the meal', 'supply_used', 'one fewer than the eaters, minimum 1')], per='rest_short'),
    rk("When you cook at a rest, up to four who eat hold a Protective lever on Endure checks against weather and exhaustion until their next rest, the meal uses one supply fewer than their number (minimum 1), and each eater loses one stack of exhaustion.",
       [lev('protective', "the eaters' Endure checks against weather and exhaustion", 'scene', verbs=['verb.endure']), tgt(3), fact('the meal', 'supply_used', 'one fewer than the eaters, minimum 1'), cleanse('one stack of cond.exhausted', 'each eater')], per='rest_short')],
   hook='on_boundary', when='boundary in [rest_short, rest_long] and you cooked', x=[('a meal with no supply at all', 'ab.green_larder; foraging')])

ab('ab.feast', 'A Table Laid', C + 'cookery.feasting', 3, 'host', 'Working', 'beat',
   'Win a room with what you set before it.',
   'Applies to guests who sit to a meal you prepared over a watch, with supplies for the table.',
   [rk("Host a meal you prepared. For the scene each guest's standing toward the host is treated as one step warmer, the host holds a Precision lever and an Amplifying lever on Talk with the guests, and a social clock among them ticks by 2.",
       [fact('each guest', 'standing_to_host', 'one step warmer this scene'), lev('precision', "the host's Talk beats with the guests", 'scene', verbs=['verb.talk']), lev('amplifying', "the host's Talk beats with the guests", 'scene', verbs=['verb.talk']), tick('a social clock among the guests (15)', 2), tgt(1)], f=1, per='scene_end'),
    rk("Host a meal you prepared. For the scene each guest's standing toward the host is treated as one step warmer, the host holds a Precision lever and an Amplifying lever on Talk with the guests and those beats are framed one stakes rung lower, and a social clock among them ticks by 2.",
       [fact('each guest', 'standing_to_host', 'one step warmer this scene'), lev('precision', "the host's Talk beats with the guests", 'scene', verbs=['verb.talk']), lev('amplifying', "the host's Talk beats with the guests", 'scene', verbs=['verb.talk']), tick('a social clock among the guests (15)', 2), tgt(1), stakes("the host's Talk beats with the guests")], f=1, per='scene_end')],
   attr='presence', oc=1, cost_text='a watch of preparation and supplies for the table (08)',
   x=[('a guest with standing Hostile', 'they do not sit'), ('a lasting change of standing', 'that is what the Talk beats are for (15)')])

# ---------------- building ----------------
ab('ab.dig_in', 'Dig In', C + 'building.field_works', 1, 'entrench', 'Working', 'beat',
   'Make a position out of ground and what lies on it.',
   'Applies to one position, with a spade, axe or loose stone at hand; takes an interval.',
   [rk("In an interval, make a position for up to two: each holds flag.in_cover and flag.elevated there.",
       [move('up to two beings in the position', 0, add=['flag.in_cover', 'flag.elevated']), tgt(1)]),
    rk("In an interval, make a position for up to two: each holds flag.in_cover and flag.elevated there, and beats to hold the position are framed one stakes rung lower.",
       [move('up to two beings in the position', 0, add=['flag.in_cover', 'flag.elevated']), tgt(1), lev('protective', 'beats to hold the position', 'scene')]),
    rk("In an interval, make a position for up to four: each holds flag.in_cover and flag.elevated there, and beats to hold the position are framed one stakes rung lower.",
       [move('up to four beings in the position', 0, add=['flag.in_cover', 'flag.elevated']), tgt(3), lev('protective', 'beats to hold the position', 'scene')])],
   attr='might', x=[('lasting fortification', 'a building project (08)'), ('bare rock with no loose material', 'the terrain decides')])

ab('ab.breach', 'Breach', C + 'building.fortification', 4, 'breaching', 'Working', 'beat',
   'Bring down a made barrier where it is weakest.',
   'Applies to one wall, gate, door or earthwork you can reach with tools or a ram.',
   [rk("Attack a barrier (Force or Handle, Intellect or Might, against its tier). The beat holds a Precision lever and an Amplifying lever, its reach is one rung higher, its stakes one rung lower, and the entry or siege clock ticks by your delivered reach.",
       [lev('precision', 'this beat'), lev('amplifying', 'this beat'), reach('this beat'), stakes('this beat'), tick('the entry or siege clock', 'delivered_reach')], f=1)],
   attr='intellect', check=('aimed', 'verb.force', "the barrier's tier"), traits=['trait.sense.loud'],
   x=[('doing it quietly', 'it is loud'), ('a magical ward on the barrier', '05.7.7')])

# ---------------- artifice ----------------
ab('ab.rig_trap', 'Rig a Trap', C + 'artifice.traps', 1, 'trap', 'Working', 'beat',
   'Set a device that acts when you are not there.',
   'Applies to one doorway, path or object, with a trapper\'s kit; takes an interval.',
   [rk("In an interval, set a trap. The first being to cross it rolls Evade against your effect DC: on a failure it is grabbed until it breaks free or the scene ends.",
       [fchk('evade'), cond('cond.grabbed', 1, 'scene', 'the first being to cross the trap')]),
    rk("In an interval, set a trap. The first being to cross it rolls Evade against your effect DC: on a failure it takes Moderate harm of the kind the trap deals and is grabbed until it breaks free or the scene ends.",
       [fchk('evade'), cond('cond.grabbed', 1, 'scene', 'the first being to cross the trap'), harm(2, ['harm.physical'], 'the first being to cross the trap')]),
    rk("In an interval, set a trap. The first being to cross it rolls Evade against your effect DC: on a failure it takes Heavy harm of the kind the trap deals and is restrained until the end of its next turn.",
       [fchk('evade'), cond('cond.restrained', 1, 'rounds:1', 'the first being to cross the trap'), harm(3, ['harm.physical'], 'the first being to cross the trap')])],
   attr='intellect', check=('resisted', 'evade', 'agility'), oc=1, cost_text="one use of a trapper's kit (08)", harm_tags=['harm.physical'],
   x=[('setting it in the middle of a fight', 'it takes an interval'), ('a trap that tells you who crossed it', 'rit.ward_threshold')])

ab('ab.clockwork_servant', 'Clockwork Servant', C + 'artifice.clockwork', 5, 'automaton', 'Working', 'beat',
   'Wind a made thing to do a servant\'s work.',
   'Applies to one automaton you built or repaired, wound over a watch with tools and parts.',
   [rk("Over a watch, wind an automaton of threat band 4 that serves for a day: tireless, it carries, guards, labours and fights when you spend an action to command it, and may Help your beats with a Precision lever.",
       [summ('a clockwork automaton of threat band 4', 4, 'days:1'), perm(4), lev('precision', 'beats the automaton helps', 'scene')], f=2, per='rest_long')],
   attr='intellect', oc=1, cost_text='a watch of work and clockwork parts (08)',
   x=[('an automaton that acts on its own turn', 'INV-11: it acts only when commanded'), ('building the automaton itself', 'a 12-segment project (08)')])

# ---------------- jewelcraft ----------------
ab('ab.true_cut', 'True Cut', C + 'jewelcraft.gemcutting', 1, 'gem_eye', 'Edge', 'passive',
   'See the stone inside the rough.',
   'Applies to beats that appraise, cut or set gems and fine metal.',
   [rk("+1 to beats that appraise, cut or set gems and fine metal.",
       [edge(1, 'deed_tag under deed.craft.jewelcraft')]),
    rk("+1 to beats that appraise, cut or set gems and fine metal, and their reach is one rung higher.",
       [edge(1, 'deed_tag under deed.craft.jewelcraft'), reach('deed_tag under deed.craft.jewelcraft')]),
    rk("+2 to beats that appraise, cut or set gems and fine metal, and their reach is one rung higher.",
       [edge(2, 'deed_tag under deed.craft.jewelcraft'), reach('deed_tag under deed.craft.jewelcraft')])],
   x=[('magical properties of a stone', 'ab.spell_sight')])

ab('ab.fine_setting', 'Fine Setting', C + 'jewelcraft.goldwork', 3, 'setting', 'Edge', 'passive',
   'Make a setting fit to hold more than a stone.',
   'Applies to enchanting and imbuing beats worked on an item you set in gold or gem.',
   [rk("Enchanting beats on an item you set have reach one rung higher, and each success ticks the imbuing clock one segment more.",
       [reach('deed_tag under deed.craft.enchanting and the item was set by you'), tick('the imbuing clock', 1)]),
    rk("Enchanting beats on an item you set have reach one rung higher and +1, and each success ticks the imbuing clock one segment more.",
       [reach('deed_tag under deed.craft.enchanting and the item was set by you'), tick('the imbuing clock', 1), edge(1, 'deed_tag under deed.craft.enchanting and the item was set by you')])],
   x=[('a property slot beyond the item\'s cap', '08 owns slot caps')])

# ---------------- enchanting ----------------
ab('ab.rune_of_keenness', 'Rune of Keenness', C + 'enchanting.inscription', 1, 'rune', 'Working', 'beat',
   'Inscribe a sign that lends a thing a passing power.',
   'Applies to one weapon you can work on for an interval; requires a magic training license.',
   [rk("Inscribe one weapon over an interval: until the next scene ends it counts as magical, deals +1 harm, and its first Strike holds a Precision lever.",
       [perm(2), hedge(1, 'a Strike with the inscribed weapon'), lev('precision', "the inscribed weapon's first Strike")], f=1),
    rk("Inscribe up to two items over an interval: until the next scene ends an inscribed weapon counts as magical and deals +1 harm; inscribed armor reduces physical harm by 1.",
       [perm(2), hedge(1, 'a Strike with an inscribed weapon'), red(1, ['harm.physical']), tgt(1)], f=1),
    rk("Inscribe up to three items over an interval: until the next scene ends an inscribed weapon counts as magical and deals +2 harm; inscribed armor reduces physical harm by 1.",
       [perm(2), hedge(2, 'a Strike with an inscribed weapon'), red(1, ['harm.physical']), tgt(2)], f=1)],
   attr='intellect', traits=['trait.nature.magical', 'trait.duration.lasting'], lim=0,
   x=[('a lasting enchantment', 'rit.imbue and a crafting project (08)'), ('an inscriber with no magic training license', 'G3: deed.craft.enchanting requires one')])

ab('ab.bind_power', 'Bind Power', C + 'enchanting.imbuing', 4, 'imbue', 'Edge', 'passive',
   'Seat a lasting power in a made thing.',
   'Applies to beats of rit.imbue and to enchanting projects (08).',
   [rk("+1 to imbuing beats, their reach is one rung higher, and each success ticks the imbuing clock one segment more.",
       [edge(1, 'deed_tag under deed.craft.enchanting.imbuing'), reach('deed_tag under deed.craft.enchanting.imbuing'), tick('the imbuing clock', 1)])],
   x=[('a property the materials do not gate', 'materials gate the pool (08)')])

# ---------------- scribing ----------------
ab('ab.fair_copy', 'Fair Copy', C + 'scribing.copying', 1, 'copy_text', 'Permission', 'beat',
   'Make a copy that teaches as well as its original.',
   'Applies to one text you can read, with ink and a surface; a week of downtime per text.',
   [rk("In a week of downtime, copy a text that teaches an ability or a training: the copy teaches as the original does, and study from your own copies ticks one segment more each week.",
       [perm(2), tick('a learning clock ticked by study from your own copy', 1)]),
    rk("In a week of downtime, copy a text that teaches an ability or a training: the copy teaches as the original does, study from your own copies ticks one segment more each week, and you gain +1 to beats that test whether a document is genuine.",
       [perm(2), tick('a learning clock ticked by study from your own copy', 1), edge(1, 'the beat tests whether a document is genuine')]),
    rk("In a day of downtime, copy a text that teaches an ability, a training or a rite: the copy teaches as the original does, study from your own copies ticks one segment more each week, and you gain +1 to beats that test whether a document is genuine.",
       [perm(4), tick('a learning clock ticked by study from your own copy', 1), edge(1, 'the beat tests whether a document is genuine')])],
   attr='intellect', x=[('forging a seal or a hand', 'lic.training.guile_disguise (forgery)'), ('a text in a language you cannot read', 'ab.gift_of_tongues; ab.cipher_breaker')])

ab('ab.field_map', 'Field Map', C + 'scribing.cartography', 2, 'mapping', 'Working', 'beat',
   'Set down a place so that others can cross it.',
   'Applies to a site or route you have passed through or can overlook; takes an interval.',
   [rk("In an interval, map what you have seen: the map is an item, and whoever carries it holds a Precision lever on navigation beats there.",
       [fact('the pc', 'holds_item', 'a map of the site or route'), lev('precision', 'navigation beats in the mapped place by the map\'s bearer', 'scene')]),
    rk("In an interval, map what you have seen: the map is an item, whoever carries it holds a Precision lever on navigation beats there, and travel beats there are framed one stakes rung lower.",
       [fact('the pc', 'holds_item', 'a map of the site or route'), lev('precision', 'navigation beats in the mapped place by the map\'s bearer', 'scene'), stakes('travel beats in the mapped place by the map\'s bearer')])],
   attr='intellect', x=[('places you have not seen', 'G4: nothing to map; a rumor is not a survey')])
