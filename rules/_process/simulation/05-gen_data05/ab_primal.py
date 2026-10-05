# deed.primal -- 17 spells. Casting attribute Resolve; every working needs its source present in the scene (05.7.3).
from dsl05 import *

P = 'deed.primal.'
T = 'the target'
EVA = ('resisted', 'evade', 'agility')
RES = ('resisted', 'endure', 'resolve')
MIG = ('resisted', 'endure', 'might')

# ---------------- growth ----------------
ab('ab.root_snare', 'Root Snare', P + 'growth.entangling', 1, 'entangle', 'Working', 'beat',
   'Make growing things seize what stands among them.',
   'Applies to one target within band.near that stands on or beside living plants or roots.',
   [rk("Roots and stems seize one target within band.near (it rolls Evade against your effect DC): on a failure it is off-balance until the end of its next turn and grabbed by the growth until it breaks free or the scene ends.",
       [fchk('evade'), cond('cond.grabbed', 1, 'scene', T), cond('cond.off_balance', 1, 'rounds:1', T)], f=1),
    rk("Roots and stems seize one target within band.near (it rolls Evade against your effect DC): on a failure it is restrained until the end of its next turn, then grabbed by the growth until it breaks free or the scene ends.",
       [fchk('evade'), cond('cond.restrained', 1, 'rounds:1', T), cond('cond.grabbed', 1, 'scene', T)], f=1),
    rk("Roots and stems seize up to three targets within band.near (each rolls Evade against your effect DC): on a failure each is restrained until the end of its next turn, then grabbed by the growth until it breaks free or the scene ends.",
       [fchk('evade'), cond('cond.restrained', 1, 'rounds:1', T), cond('cond.grabbed', 1, 'scene', T), tgt(2)], f=1)],
   check=EVA, traits=['trait.delivery.ranged', 'trait.sense.visible'], x=[('a place with nothing growing', 'G4: the source is absent (05.7.3)')])

ab('ab.thorn_coat', 'Thorn Coat', P + 'growth.thorns', 2, 'thorn_aura', 'Form', 'rider',
   'Grow a hide of thorn over your own.',
   'Applies to yourself, with a living plant, seed or cutting on your person.',
   [rk("For the scene thorns cover you: physical harm you take is reduced by 1, and a foe that hits you in melee takes Light piercing harm.",
       [aura('band.engaged', [red(1, ['harm.physical']), harm(1, ['harm.physical.pierce'], 'a foe that hits you with a melee attack')])], f=1),
    rk("For the scene thorns cover you: physical harm you take is reduced by 1, and a foe that hits you in melee takes Moderate piercing harm and bleeds.",
       [aura('band.engaged', [red(1, ['harm.physical']), harm(2, ['harm.physical.pierce'], 'a foe that hits you with a melee attack'), cond('cond.bleeding', 1, 'rounds:1', 'a foe that hits you with a melee attack')])], f=1)],
   slot='slot.aura', verbs=['any'], harm_tags=['harm.physical.pierce'], traits=['trait.delivery.aura', 'trait.sense.visible'],
   x=[('fire', 'the coat burns: it gives no reduction against harm.fire')])

ab('ab.renewal', 'Renewal', P + 'growth.renewal', 4, 'regrowth', 'Working', 'beat',
   'Quicken a living body\'s own mending.',
   'Applies to one living being you touch.',
   [rk("One living being you touch regains 5 Vitality now and 5 more at the start of its next turn, and its bleeding and its poisoning end. This counts as one healing effect.",
       [heal(5, T), heal(5, T), cleanse('cond.bleeding', T), cleanse('cond.poisoned', T)], f=2)],
   traits=['trait.delivery.touch'], x=[('wounds and marks', 'ch.07; rit.vigil_of_healing'), ('a being already healed twice since its long rest', 'the healing cap (05.7.8)')])

# ---------------- beast-kinship ----------------
ab('ab.beast_speech', 'Beast Speech', P + 'beastkin.speech', 1, 'speak_beast', 'Permission', 'beat',
   'Trade meaning with an animal.',
   'Applies to beasts (creature.beast) within band.close; they answer as beasts: what they saw, smelled, fear and want.',
   [rk("For the scene you may Talk with beasts within band.close and understand their answers, and you hold a Precision lever on Talk and Handle beats with them.",
       [perm(2), lev('precision', 'Talk and Handle beats with beasts', 'scene', verbs=['verb.talk', 'verb.handle'])]),
    rk("For the scene you may Talk with beasts within band.close and understand their answers, you hold a Precision lever on Talk and Handle beats with them, and one beast tells you what it perceived here within the past day.",
       [perm(2), lev('precision', 'Talk and Handle beats with beasts', 'scene', verbs=['verb.talk', 'verb.handle']), rev('what one beast perceived at this place within the past day')]),
    rk("For the scene you may Talk with beasts within band.close and understand their answers, you hold a Precision lever on Talk and Handle beats with them, one beast tells you what it perceived here within the past day, and you may ask of a willing beast one service within its nature (carry word, keep watch, lead the way).",
       [perm(4), lev('precision', 'Talk and Handle beats with beasts', 'scene', verbs=['verb.talk', 'verb.handle']), rev('what one beast perceived at this place within the past day')])],
   attr='resolve', x=[('commanding a beast against its nature', 'ab.gentle_hand; ch.16 companions'), ('creatures that are not beasts', 'verb.talk if they have speech')],
   nmi=['that a beast knows names, numbers or reasons'])

ab('ab.borrowed_senses', 'Borrowed Senses', P + 'beastkin.senses', 3, 'beast_eyes', 'Working', 'beat',
   'See and hear through an animal that lets you.',
   'Applies to one beast you have calmed, bonded or spoken with, within band.distant; sustained.',
   [rk("While you sustain it, you perceive through one willing beast within band.distant: you may make Observe beats from where it is, with a Precision lever, and a scouting clock ticks by your delivered reach.",
       [perm(4), rev('what the beast perceives where it is'), lev('precision', 'Observe beats made through the beast', 'scene', verbs=['verb.observe']), tick('your scouting or search clock', 'delivered_reach')], f=2),
    rk("While you sustain it, you perceive through one willing beast within a watch's travel: you may make Observe beats from where it is, with a Precision lever and reach one rung higher, and a scouting clock ticks by your delivered reach.",
       [perm(4), rev('what the beast perceives where it is'), lev('precision', 'Observe beats made through the beast', 'scene', verbs=['verb.observe']), tick('your scouting or search clock', 'delivered_reach'), reach('Observe beats made through the beast')], f=2)],
   wk=2, weak=("While you look through the beast you are blinded and deafened in your own body.", cond('cond.blinded', 1, 'while:you sustain borrowed senses', 'self')),
   traits=['trait.duration.sustained'], x=[('directing what the beast does', 'ab.beast_speech; ch.16'), ('an unwilling beast', 'ab.gentle_hand first')])

# ---------------- weather ----------------
ab('ab.gust', 'Gust', P + 'weather.wind', 1, 'wind_push', 'Working', 'beat',
   'Push a body of air in one direction.',
   'Applies where air moves: under open sky, or where a draught is an established fact; up to two targets within band.near in one line from you.',
   [rk("A blast of wind strikes up to two targets within band.near in a line from you (each rolls Endure (Might) against your effect DC): on a failure each is pushed one band away and knocked prone.",
       [fchk('endure'), move(T, 1), cond('cond.prone', 1, 'rounds:1', T), tgt(1)], f=1),
    rk("A blast of wind strikes up to three targets within band.near in a line from you (each rolls Endure (Might) against your effect DC): on a failure each is pushed two bands away and knocked prone.",
       [fchk('endure'), move(T, 2), cond('cond.prone', 1, 'rounds:1', T), tgt(2)], f=1),
    rk("A blast of wind strikes up to four targets within band.near in a line from you (each rolls Endure (Might) against your effect DC): on a failure each is pushed two bands away and knocked prone; until the end of your next turn, ranged attacks with arrows, bolts or thrown weapons through that line take a Precision snag.",
       [fchk('endure'), move(T, 2), cond('cond.prone', 1, 'rounds:1', T), tgt(3), ({'effect_id': 'eff.status_modifier', 'params': {'amount': -2, 'applies_when': 'a ranged attack with a physical missile crosses the line of the gust, until the end of your next turn'}}, 2)], f=1)],
   check=MIG, spread='pierce', traits=['trait.delivery.line', 'trait.sense.audible'],
   x=[('pulling something toward you', 'no: the principle pushes (05.5.2)'), ('a sealed, still room', 'G4: the source is absent (05.7.3)')])

ab('ab.fog_bank', 'Fog Bank', P + 'weather.mist', 2, 'mist', 'Working', 'beat',
   'Draw the water in the air into a standing fog.',
   'Applies where there is water or damp: near open water, after rain, in a marsh, at dawn or dusk; covers the ground within band.near of a point; sustained.',
   [rk("While you sustain it, fog stands within band.near of a point you choose: sight beyond band.engaged fails inside it, every being in it holds flag.hidden against those beyond band.engaged, and Sneak beats in it hold a Precision lever.",
       [perm(2), move('each being in the fog', 0, add=['flag.hidden']), tgt(3), lev('precision', 'Sneak beats inside the fog', 'scene', verbs=['verb.sneak'])], f=2),
    rk("While you sustain it, fog stands within band.near of a point you choose: sight beyond band.engaged fails inside it for everyone but you, every being in it holds flag.hidden against those beyond band.engaged, and Sneak beats in it hold a Precision lever.",
       [perm(2), move('each being in the fog', 0, add=['flag.hidden']), tgt(3), lev('precision', 'Sneak beats inside the fog', 'scene', verbs=['verb.sneak']), waive('the loss of sight inside your own fog', 'you sustain the fog')], f=2)],
   spread='linger', traits=['trait.duration.sustained', 'trait.delivery.area', 'trait.sense.visible'],
   x=[('a dry, hot place', 'G4: the source is absent (05.7.3)'), ('sparing allies the blindness', 'the fog hides and blinds alike')])

ab('ab.call_lightning', 'Call Lightning', P + 'weather.storm', 5, 'sky_bolt', 'Working', 'beat',
   'Bring down the fire of the sky on a place.',
   'Applies under open sky, to a point within band.far and up to four beings within band.close of it.',
   [rk("Lightning falls on a point within band.far. Up to four beings within band.close of it roll Evade against your effect DC: on a failure each takes Grievous lightning harm (one rung heavier if a storm is recorded overhead), is dazed until the end of its next turn and deafened until the scene ends.",
       [fchk('evade'), harm(4, ['harm.storm.lightning'], 'each being within band.close of the point that fails'), tgt(3), sev(1, 'a storm is recorded in the weather'), cond('cond.dazed', 1, 'rounds:1', 'each being that fails'), cond('cond.deafened', 1, 'scene', 'each being that fails')], f=3, per='scene_end')],
   check=EVA, spread='burst', lim=1, harm_tags=['harm.storm.lightning'], traits=['trait.action.attack', 'trait.delivery.area', 'trait.sense.loud', 'trait.sense.visible'],
   x=[('indoors or underground', 'G4: the source is absent (05.7.3)'), ('calling the storm itself', 'rit.call_rain')])

# ---------------- shapeshifting ----------------
ab('ab.claws', 'Claws', P + 'shapeshifting.partial', 1, 'natural_weapons', 'Form', 'rider',
   'Change your hands into a predator\'s.',
   'Applies to your own hands, for unarmed Strikes.',
   [rk("For the scene your unarmed Strikes deal cutting harm one severity rung heavier (base Moderate), +1.",
       [sdel(['harm.physical.cut'], 1, 'scene'), sev(1, 'an unarmed Strike with the claws')], f=1),
    rk("For the scene your unarmed Strikes deal cutting harm one severity rung heavier (base Moderate), +1, and you climb as a movement mode.",
       [sdel(['harm.physical.cut'], 1, 'scene'), sev(1, 'an unarmed Strike with the claws'), mode('climb', 'scene')], f=1),
    rk("For the scene your unarmed Strikes deal cutting harm one severity rung heavier (base Moderate), +1, a target they harm bleeds, and you climb as a movement mode.",
       [sdel(['harm.physical.cut'], 1, 'scene'), sev(1, 'an unarmed Strike with the claws'), mode('climb', 'scene'), cond('cond.bleeding', 1, 'rounds:1', 'a target the claws harm')], f=1)],
   slot='slot.strike_delivery', verbs=['any'], harm_tags=['harm.physical.cut'], traits=['trait.sense.visible'],
   wk=0, x=[('fine work with the hands while clawed', 'trait.action.manipulate beats take a Precision snag (the claws are a fact)'), ('a whole beast\'s shape', 'ab.beast_form')])

ab('ab.beast_form', 'Beast Form', P + 'shapeshifting.beast_form', 3, 'beast_shape', 'Form', 'beat',
   'Take the whole shape of a beast you know.',
   'Applies to yourself; the form is a beast you have touched or tracked, of threat band below your power band, that walks, climbs or swims.',
   [rk("For the scene you take a beast's shape: its size, movement modes and senses, with your own Vitality, attributes and mind. You hold a Precision lever on Sneak and Observe beats that suit the form.",
       [bform('a beast you have touched or tracked, threat band below your power band', 'scene'), perm(2), mode('swim', 'scene'), lev('precision', 'Sneak and Observe beats that suit the form', 'scene')], f=2),
    rk("For the scene you take a beast's shape, which may be one that flies: its size, movement modes and senses, with your own Vitality, attributes and mind. You hold a Precision lever on Sneak and Observe beats that suit the form.",
       [bform('a beast you have touched or tracked, threat band below your power band', 'scene'), perm(4), mode('swim', 'scene'), lev('precision', 'Sneak and Observe beats that suit the form', 'scene')], f=2)],
   slot='slot.body_form', wk=1, weak=("In the beast's shape you cannot speak, cast workings that need word or gesture, or use what your hands held.", restr({'methods': ['speech', 'trait.action.manipulate beats', 'workings with trait.action.speech']}, 'self', 'scene')),
   traits=['trait.sense.visible'], x=[('the beast\'s own powers or harm', 'the Taking (04.10) for a Devourer; otherwise your own Strikes at unarmed harm'), ('a folk shape or a named individual', 'ab.living_mask')],
   nmi=["the beast's stat block", 'healing on changing back'])

ab('ab.elemental_form', 'Elemental Form', P + 'shapeshifting.elemental_form', 5, 'element_shape', 'Form', 'beat',
   'Become, for a time, one of the living elements.',
   'Applies to yourself, in the presence of the element you take: flame, water, stone or wind.',
   [rk("For the scene you take the shape of the element present: you halve harm of that element, cannot be grabbed or restrained, your Strikes deal that element's harm +1, and you move as it moves (fire and wind: fly; water: swim; stone: burrow).",
       [bform('an elemental body of the element present', 'scene'), resist(["the element's harm tag"]), immune(['cond.grabbed', 'cond.restrained']), sdel(["the element's harm tag"], 1, 'scene'), mode('swim', 'scene')], f=3, per='rest_short')],
   slot='slot.body_form', wk=1, weak=("In the elemental shape you take double harm of the opposed element (fire and frost oppose; storm and crushing oppose) and cannot speak.", ({'effect_id': 'eff.harm_vulnerability', 'params': {'factor': 2, 'harm_tags': ["the element opposed to the form's"]}}, 0)),
   traits=['trait.sense.visible'], x=[('holding or using carried items', 'they merge with the form until it ends'), ('an element not present', 'G4: the source is absent (05.7.3)')])

# ---------------- spirits ----------------
ab('ab.spirit_tongue', 'Spirit Tongue', P + 'spirits.speaking', 1, 'speak_spirit', 'Permission', 'beat',
   'Perceive and address the spirits of a place.',
   'Applies to spirits of place and the lingering dead that are present, as an established fact or by the Oracle.',
   [rk("For the scene you perceive the spirits present at this place and may Talk with them.",
       [perm(4)]),
    rk("For the scene you perceive the spirits present at this place and may Talk with them, with a Precision lever.",
       [perm(4), lev('precision', 'Talk beats with spirits', 'scene', verbs=['verb.talk'])]),
    rk("For the scene you perceive the spirits present at this place and may Talk with them, with a Precision lever, and you learn what the eldest spirit here wants.",
       [perm(4), lev('precision', 'Talk beats with spirits', 'scene', verbs=['verb.talk']), rev('one want of the eldest spirit present')])],
   attr='resolve', x=[('a place with no spirit', 'the Oracle decides; then nothing answers'), ('compelling a spirit', 'ab.spirit_bargain; rit.circle_of_binding')],
   nmi=['a spirit where no fact or Oracle answer placed one'])

ab('ab.spirit_bargain', 'Spirit Bargain', P + 'spirits.bargaining', 4, 'spirit_service', 'Working', 'beat',
   'Ask one service of a spirit and name its price.',
   'Applies to one spirit present that you can perceive and address.',
   [rk("Ask a service of a spirit present (Talk, Resolve, against its Resolve defense). On a success it names its price truly and, once you agree, acts for you within its nature for the scene as a being of threat band 3, when you spend an action to direct it; you hold a Precision lever on your next Talk with it.",
       [summ('the spirit, acting within its nature as threat band 3', 3, 'scene'), perm(2), rev("the spirit's price"), lev('precision', 'your next Talk beat with the spirit')], f=2, per='scene_end')],
   attr='resolve', check=('aimed', 'verb.talk', "the spirit's Resolve defense"), wk=1,
   weak=("The price agreed is recorded as a commitment; while it is unpaid past its term, every primal working you cast costs 1 more Focus.", ({'effect_id': 'eff.focus_cost_step', 'params': {'amount': 1, 'applies_when': 'deed_tag under deed.primal and the bargain is unpaid past its term'}}, 0)),
   x=[('a service against the spirit\'s nature', 'it refuses; no roll'), ('binding it beyond the scene', 'rit.circle_of_binding')])

# ---------------- raw elements ----------------
ab('ab.cinder_stride', 'Cinder Stride', P + 'elements.fire', 1, 'fire_weapon', 'Form', 'rider',
   'Draw living fire along what you strike with.',
   'Applies to your own Strikes, with open flame or embers within band.close or carried.',
   [rk("For 3 rounds your Strikes deal fire harm in place of their own type, +1.",
       [sdel(['harm.fire'], 1, 'rounds:3')], f=1),
    rk("For 3 rounds your Strikes deal fire harm in place of their own type, +1, and a target they harm is burning.",
       [sdel(['harm.fire'], 1, 'rounds:3'), cond('cond.burning', 1, 'rounds:1', 'a target your Strike harms')], f=1),
    rk("For the scene your Strikes deal fire harm in place of their own type, +2, and a target they harm is burning.",
       [sdel(['harm.fire'], 2, 'scene'), cond('cond.burning', 1, 'scene', 'a target your Strike harms')], f=1)],
   slot='slot.strike_delivery', verbs=['any'], harm_tags=['harm.fire'], traits=['trait.sense.visible'], ckey=True,
   x=[('throwing the fire', 'ab.flame_lance'), ('a second coating on the same weapon', 'the higher priority rank owns slot.strike_delivery (05.10.3)')],
   basis=['WE-00-6 (00 names this ability; defined here)'])

ab('ab.stone_shape', 'Stone Shape', P + 'elements.earth', 3, 'shape_earth', 'Permission', 'beat',
   'Mould earth and unworked stone like clay.',
   'Applies to earth or unworked stone you touch, up to the bulk of a door.',
   [rk("Reshape up to a door's bulk of earth or unworked stone you touch: open a gap, close one, raise a step or a low wall (which gives flag.in_cover). Force beats against earth and stone have reach one rung higher this scene and hold an Amplifying lever.",
       [perm(4), move('one being behind the raised wall', 0, add=['flag.in_cover']), reach('Force beats against earth or unworked stone'), lev('amplifying', 'Force beats against earth or unworked stone', 'scene', verbs=['verb.force'])], f=2),
    rk("Reshape up to a door's bulk of earth or unworked stone you touch: open a gap, close one, raise a step or a low wall (which gives flag.in_cover), or close it on one being standing there, which is grabbed until it breaks free or the scene ends. Force beats against earth and stone have reach one rung higher this scene and hold an Amplifying lever.",
       [perm(4), move('one being behind the raised wall', 0, add=['flag.in_cover']), reach('Force beats against earth or unworked stone'), lev('amplifying', 'Force beats against earth or unworked stone', 'scene', verbs=['verb.force']), cond('cond.grabbed', 1, 'scene', 'one being standing on the shaped ground')], f=2)],
   traits=['trait.delivery.touch', 'trait.sense.visible'], x=[('worked stone, mortar, brick or metal', 'verb.force; lic.training.craft_building'), ('making a lasting building', 'craft (08): the shape holds, but it is rough')])

END = ('resisted', 'endure', 'endurance')

# Revision I-015: a min_tier-1 working for each of water, air and earth, so the Touched's spark (02.6.3, T-02-7)
# starts with a working of the element it names. (Stone Shape is min_tier 3 and cannot be a gifted technique.)
ab('ab.undertow', 'Undertow', P + 'elements.water', 1, 'water_drag', 'Working', 'beat',
   'Make water rise and drag a body down.',
   'Applies to one being within band.near that stands in, on or beside standing or running water.',
   [rk("Water rises around one being within band.near (it rolls Endure (Might) against your effect DC): on a failure it takes Light crushing harm, is dragged one band toward the water and knocked prone.",
       [fchk('endure'), harm(1, ['harm.physical.crush'], T), move(T, 1), cond('cond.prone', 1, 'rounds:1', T)], f=1),
    rk("Water rises around one being within band.near (it rolls Endure (Might) against your effect DC): on a failure it takes Moderate crushing harm, is dragged one band toward the water, knocked prone, and choking until the end of its next turn.",
       [fchk('endure'), harm(2, ['harm.physical.crush'], T), move(T, 1), cond('cond.prone', 1, 'rounds:1', T), cond('cond.choking', 1, 'rounds:1', T)], f=1),
    rk("Water rises around one being within band.near (it rolls Endure (Might) against your effect DC): on a failure it takes Heavy crushing harm, is dragged one band toward the water, knocked prone, and choking until the end of its next turn.",
       [fchk('endure'), harm(3, ['harm.physical.crush'], T), move(T, 1), cond('cond.prone', 1, 'rounds:1', T), cond('cond.choking', 1, 'rounds:1', T)], f=1)],
   check=MIG, harm_tags=['harm.physical.crush'], traits=['trait.delivery.ranged', 'trait.sense.visible', 'trait.sense.audible'],
   x=[('a dry place', 'G4: the source is absent (05.7.3); a waterskin poured out supplies it once'), ('drowning a being outright', 'a rite, or holding it under by verb.grapple')],
   basis=['I-015', '02.6.3', 'DL-05-32'])

ab('ab.stolen_breath', 'Stolen Breath', P + 'elements.air', 1, 'air_breath', 'Working', 'beat',
   'Draw the air out of a breathing body.',
   'Applies to one being that breathes, within band.near, where air moves (05.7.3).',
   [rk("Pull the air from the lungs of one breathing being within band.near (it rolls Endure (Endurance) against your effect DC): on a failure it takes Moderate harm from lack of air and is choking until the end of its next turn.",
       [fchk('endure'), harm(2, ['harm.physical.asphyxia'], T), cond('cond.choking', 1, 'rounds:1', T)], f=1),
    rk("Pull the air from the lungs of one breathing being within band.near (it rolls Endure (Endurance) against your effect DC): on a failure it takes Heavy harm from lack of air, is choking until the end of its next turn and distracted until the end of its next turn.",
       [fchk('endure'), harm(3, ['harm.physical.asphyxia'], T), cond('cond.choking', 1, 'rounds:1', T), cond('cond.distracted', 1, 'rounds:1', T)], f=1),
    rk("Pull the air from the lungs of one breathing being within band.near (it rolls Endure (Endurance) against your effect DC): on a failure it takes Grievous harm from lack of air, is choking until the end of its next turn and distracted until the end of its next turn.",
       [fchk('endure'), harm(4, ['harm.physical.asphyxia'], T), cond('cond.choking', 1, 'rounds:1', T), cond('cond.distracted', 1, 'rounds:1', T)], f=1)],
   check=END, harm_tags=['harm.physical.asphyxia'], traits=['trait.delivery.ranged'],
   x=[('a being that does not breathe (the undead, constructs, spirits)', 'G4 for this working'), ('a sealed, still room', 'G4: the source is absent (05.7.3)')],
   basis=['I-015', '02.6.3', 'DL-05-32'])

ab('ab.heave', 'Heave', P + 'elements.earth', 1, 'earth_heave', 'Working', 'beat',
   'Make the ground buck under a being\'s feet.',
   'Applies to beings within band.near that stand on bare earth or unworked stone.',
   [rk("The ground under one being within band.near bucks and heaves (it rolls Evade against your effect DC): on a failure it takes Light crushing harm, is knocked prone and is slowed until the end of its next turn.",
       [fchk('evade'), harm(1, ['harm.physical.crush'], T), cond('cond.prone', 1, 'rounds:1', T), cond('cond.slowed', 1, 'rounds:1', T)], f=1),
    rk("The ground under up to two beings within band.near bucks and heaves (each rolls Evade against your effect DC): on a failure each takes Moderate crushing harm, is knocked prone and is slowed until the end of its next turn.",
       [fchk('evade'), harm(2, ['harm.physical.crush'], T), cond('cond.prone', 1, 'rounds:1', T), cond('cond.slowed', 1, 'rounds:1', T), tgt(1)], f=1),
    rk("The ground under up to three beings within band.near bucks and heaves (each rolls Evade against your effect DC): on a failure each takes Heavy crushing harm, is knocked prone and is slowed until the end of its next turn.",
       [fchk('evade'), harm(3, ['harm.physical.crush'], T), cond('cond.prone', 1, 'rounds:1', T), cond('cond.slowed', 1, 'rounds:1', T), tgt(2)], f=1)],
   check=EVA, spread='burst', harm_tags=['harm.physical.crush'], traits=['trait.delivery.area', 'trait.sense.loud', 'trait.sense.visible'],
   x=[('worked stone, timber floors, ships\' decks', 'G4: the source is absent (05.7.3)'), ('a being aloft', 'it stands on nothing')],
   basis=['I-015', '02.6.3', 'DL-05-32'])

# ---------------- hexcraft ----------------
ab('ab.evil_eye', 'Evil Eye', P + 'hexcraft.cursing', 1, 'hex', 'Working', 'beat',
   'Lay ill luck on one who meets your gaze.',
   'Applies to one being within band.near that can see you.',
   [rk("One being within band.near that can see you rolls Endure (Resolve) against your effect DC: on a failure it is weakened and distracted until the scene ends.",
       [fchk('endure'), cond('cond.weakened', 1, 'scene', T), cond('cond.distracted', 1, 'scene', T)], f=1),
    rk("One being within band.near that can see you rolls Endure (Resolve) against your effect DC: on a failure it is weakened and distracted until the scene ends and frightened of you until the end of its next turn.",
       [fchk('endure'), cond('cond.weakened', 1, 'scene', T), cond('cond.distracted', 1, 'scene', T), cond('cond.frightened', 1, 'rounds:1', T)], f=1),
    rk("One being within band.near that can see you rolls Endure (Resolve) against your effect DC: on a failure it is weakened, exposed and frightened of you until the scene ends.",
       [fchk('endure'), cond('cond.weakened', 1, 'scene', T), cond('cond.exposed', 1, 'scene', T), cond('cond.frightened', 1, 'scene', T)], f=1)],
   check=RES, traits=['trait.nature.mental', 'trait.delivery.ranged'], dictates=True, ckey=True,
   x=[('a being that cannot see you', 'G4 for this working'), ('a curse that lasts beyond the scene', 'rit.lay_curse')])

ab('ab.lift_the_hex', 'Lift the Hex', P + 'hexcraft.unhexing', 2, 'unhex', 'Working', 'beat',
   'Unpick a curse from the one who bears it.',
   'Applies to one curse, hex or ill-wishing on a being or object you touch.',
   [rk("Lift one curse from a being or object you touch (roll against its stored effect DC). On a success it ends, one condition it caused ends, and you learn who laid it.",
       [endw('one curse or hex on the being or object touched'), cleanse('one condition the curse caused', T), rev('who laid the curse')], f=2),
    rk("Lift one curse from a being or object you touch (roll against its stored effect DC). On a success it ends, up to two conditions it caused end, you learn who laid it, and the freed being's checks against that maker's hexes are framed one stakes rung lower this scene.",
       [endw('one curse or hex on the being or object touched'), cleanse('one condition the curse caused', T), cleanse('a second condition the curse caused', T), rev('who laid the curse'), lev('protective', "the freed being's checks against that maker's hexes", 'scene')], f=2)],
   check=('aimed', 'verb.handle', "the curse's stored effect DC"), traits=['trait.delivery.touch'],
   x=[('arcane wards', 'ab.unbinding (primal unhexing takes a Precision snag against them)'), ('a curse laid by a rite of regional scale', 'rit.lift_curse')])

# ---------------- the branch working (05.7.11; revision I-009) ----------------
ab('ab.wild_lash', 'Wild Lash', 'deed.primal', 1, 'branch_primal', 'Working', 'beat',
   'Let the source present strike one target for you.',
   'Applies to one being within band.near of you and of the source present (05.7.3).',
   [rk("The source present lashes one being within band.near: a thorned vine, a flung stone, a fist of water, a tongue of flame or a cut of wind. On a success it takes Moderate harm of the source's kind (shifted by delivered reach) and is off-balance until the end of its next turn.",
       [harm(2, ['harm.physical.pierce', 'harm.physical.crush', 'harm.physical.cut', 'harm.fire.flame'], T), cond('cond.off_balance', 1, 'rounds:1', T)]),
    rk("The source present lashes one being within band.near: a thorned vine, a flung stone, a fist of water, a tongue of flame or a cut of wind. On a success it takes Heavy harm of the source's kind (shifted by delivered reach) and is off-balance until the end of its next turn.",
       [harm(3, ['harm.physical.pierce', 'harm.physical.crush', 'harm.physical.cut', 'harm.fire.flame'], T), cond('cond.off_balance', 1, 'rounds:1', T)]),
    rk("The source present lashes one being within band.near: a thorned vine, a flung stone, a fist of water, a tongue of flame or a cut of wind. On a success it takes Grievous harm of the source's kind (shifted by delivered reach) and is off-balance until the end of its next turn.",
       [harm(4, ['harm.physical.pierce', 'harm.physical.crush', 'harm.physical.cut', 'harm.fire.flame'], T), cond('cond.off_balance', 1, 'rounds:1', T)])],
   check=('aimed', 'verb.strike', "the target's Guard"), harm_tags=['harm.physical.pierce', 'harm.physical.crush', 'harm.physical.cut', 'harm.fire.flame'], branch_working=True,
   traits=['trait.action.attack', 'trait.delivery.ranged', 'trait.sense.visible'],
   x=[('a place with no source present', 'G4: the source is absent (05.7.3)'), ('holding, shaping or calling the source', 'a spell of that school (ab.root_snare, ab.gust, ab.stone_shape)')],
   nmi=['a source no fact holds', 'that the source stays roused after the lash'],
   basis=['05.7.11', '05.7.3', '06 Interface request (b) to 05', 'I-009', 'DL-05-31'])
