# deed.martial -- 27 abilities. Every row is individually designed; budgets are checked by gen_data05.py.
from dsl05 import *

M = 'deed.martial.'
FOE = 'the target of the Strike'

# ---------------- blade ----------------
ab('ab.riposte', 'Riposte', M + 'blade.fencing', 1, 'counterstroke', 'Reaction', 'reaction',
   'Answer a failed attack with your blade.',
   'Applies to a melee attack against you that fails while you hold a blade and can see the attacker.',
   [rk("When a melee attack against you fails, the attacker takes your blade's harm one rung lighter and is off-balance until the end of its next turn.",
       [harmw(-1, 'the attacker'), cond('cond.off_balance', 1, 'rounds:1', 'the attacker'), lev('precision', 'your next Strike against the attacker', 'rounds:1', verbs=['verb.strike'])], f=1),
    rk("When a melee attack against you fails, the attacker takes your blade's harm, is off-balance until the end of its next turn, and you hold a Precision lever on your next Strike against it this round.",
       [harmw(0, 'the attacker'), cond('cond.off_balance', 1, 'rounds:1', 'the attacker'), lev('precision', 'your next Strike against the attacker', 'rounds:1', verbs=['verb.strike']), move('self', 1)], f=1),
    rk("When a melee attack against you fails, the attacker takes your blade's harm one rung heavier, is exposed until the scene ends, and you hold a Precision lever on your next Strike against it this round.",
       [harmw(1, 'the attacker'), cond('cond.exposed', 1, 'scene', 'the attacker'), lev('precision', 'your next Strike against the attacker', 'rounds:1', verbs=['verb.strike']), move('self', 1)], f=1)],
   hook='on_degree', when='an attack with trait.delivery.melee against you has degree failure or critical_failure',
   traits=['trait.action.attack', 'trait.delivery.melee'], x=[('a failed ranged attack', 'ab.shield_block or verb.evade')],
   nmi=['that the attacker is disarmed'])

ab('ab.cleaving_arc', 'Cleaving Arc', M + 'blade.greatsword', 2, 'sweep', 'Working', 'rider',
   'Carry one swing of a long blade through every foe in reach.',
   'Applies to a Strike made with a two-handed blade against a foe engaged with you.',
   [rk("Your Strike also strikes up to two other foes engaged with you: compare the same roll to each one's defense; each one hit takes the blade's harm one rung lighter. The first target is off-balance until the end of its next turn.",
       [tgt(2), cond('cond.off_balance', 1, 'rounds:1', FOE)], f=1),
    rk("Your Strike also strikes up to three other foes engaged with you: compare the same roll to each one's defense; each one hit takes the blade's harm, +1. Each foe hit is off-balance until the end of its next turn.",
       [tgt(3), hedge(1, 'this Strike'), cond('cond.off_balance', 1, 'rounds:1', 'each foe hit')], f=1)],
   verbs=['verb.strike'], spread='burst', traits=['trait.action.attack', 'trait.delivery.melee'],
   x=[('foes beyond band.engaged', 'ab.volley or a second beat')])

ab('ab.finishing_stroke', 'Finishing Stroke', M + 'blade.sword', 5, 'execution', 'Working', 'beat',
   'End a faltering foe with one committed blow.',
   'Applies to one bloodied foe engaged with you whose threat band is at or below your power band.',
   [rk("Strike a bloodied foe at or below your band. On a success it takes Catastrophic harm of your blade's type and is stunned until the end of its next turn; each of its allies within band.near that sees the blow is frightened until the scene ends.",
       [harm(5, ["the blade's harm type"], FOE), cond('cond.stunned', 2, 'rounds:1', FOE), cond('cond.frightened', 2, 'scene', "each ally of the target within band.near that sees the blow")], f=3, per='scene_end')],
   attr='by_method', check=('aimed', 'verb.strike', 'the target\'s attack defense'), lim=1,
   traits=['trait.action.attack', 'trait.delivery.melee', 'trait.sense.visible'], dictates=True,
   x=[('a foe that is not bloodied', 'verb.strike'), ('a foe above your band', 'verb.strike')])

# ---------------- axe ----------------
ab('ab.hew', 'Hew', M + 'axe', 1, 'heavy_blow', 'Working', 'rider',
   'Drive an axe through what it meets.',
   'Applies to a Strike made with an axe.',
   [rk("Your axe Strike deals harm one severity rung heavier, and the target is off-balance until the end of its next turn.",
       [sev(1, 'this Strike'), cond('cond.off_balance', 1, 'rounds:1', FOE)], f=1),
    rk("Your axe Strike deals harm one severity rung heavier, +1, and the target is off-balance until the end of its next turn.",
       [sev(1, 'this Strike'), hedge(1, 'this Strike'), cond('cond.off_balance', 1, 'rounds:1', FOE)], f=1),
    rk("Your axe Strike deals harm one severity rung heavier, +2, and knocks the target prone.",
       [sev(1, 'this Strike'), hedge(2, 'this Strike'), cond('cond.prone', 1, 'rounds:1', FOE)], f=1)],
   verbs=['verb.strike'], traits=['trait.action.attack', 'trait.delivery.melee'],
   x=[('breaking a door or a lock', 'verb.force')])

ab('ab.sunder', 'Sunder', M + 'axe.great', 3, 'break_gear', 'Working', 'beat',
   'Break the armor or shield a foe relies on.',
   'Applies to one foe engaged with you that bears a shield or wears armor.',
   [rk("Strike at a foe's shield or armor. On a success it takes your weapon's harm one rung heavier, the shield or armor is damaged, the foe is knocked prone, and it is exposed until the scene ends.",
       [harmw(1, FOE), fact("the target's shield or armor", 'condition', 'damaged'), cond('cond.prone', 1, 'rounds:1', FOE), cond('cond.exposed', 1, 'scene', FOE)], f=2),
    rk("Strike at a foe's shield or armor. On a success it takes your weapon's harm two rungs heavier, the shield or armor is broken, the foe is knocked prone, and it is exposed until the scene ends.",
       [harmw(2, FOE), fact("the target's shield or armor", 'condition', 'broken'), cond('cond.prone', 1, 'rounds:1', FOE), cond('cond.exposed', 1, 'scene', FOE)], f=2)],
   attr='might', check=('aimed', 'verb.strike', "the target's attack defense"),
   traits=['trait.action.attack', 'trait.delivery.melee', 'trait.sense.loud'],
   x=[('a relic or an item marked cost_immune', 'no ability breaks it (08)')])

# ---------------- bludgeon ----------------
ab('ab.stagger_blow', 'Staggering Blow', M + 'bludgeon', 1, 'concussion', 'Working', 'rider',
   'Ring a foe with blunt force.',
   'Applies to a Strike made with a mace, hammer, club, flail or staff.',
   [rk("Your bludgeon Strike dazes the target until the end of its next turn and drives it back one band.",
       [cond('cond.dazed', 1, 'rounds:1', FOE), move(FOE, 1)], f=1),
    rk("Your bludgeon Strike dazes the target until the end of its next turn and knocks it prone.",
       [cond('cond.dazed', 1, 'rounds:1', FOE), cond('cond.prone', 1, 'rounds:1', FOE)], f=1),
    rk("Your bludgeon Strike deals +2 harm, dazes the target until the end of its next turn and knocks it prone.",
       [hedge(2, 'this Strike'), cond('cond.dazed', 1, 'rounds:1', FOE), cond('cond.prone', 1, 'rounds:1', FOE)], f=1)],
   verbs=['verb.strike'], traits=['trait.action.attack', 'trait.delivery.melee'],
   x=[('knocking a foe unconscious', 'defeat it with a non-lethal frame (07)')])

ab('ab.shatter_guard', 'Shatter Guard', M + 'bludgeon.hammer', 4, 'guard_break', 'Working', 'rider',
   'Crush a foe\'s defense under a heavy head.',
   'Applies to a Strike made with a hammer or mace against a foe engaged with you.',
   [rk("Your Strike deals harm one severity rung heavier; the target is weakened and exposed until the scene ends.",
       [sev(1, 'this Strike'), cond('cond.weakened', 2, 'scene', FOE), cond('cond.exposed', 1, 'scene', FOE)], f=2)],
   verbs=['verb.strike'], traits=['trait.action.attack', 'trait.delivery.melee', 'trait.sense.loud'],
   x=[('destroying the foe\'s armor', 'ab.sunder')])

# ---------------- polearm ----------------
ab('ab.set_spear', 'Set the Spear', M + 'polearm.spear', 1, 'brace', 'Reaction', 'reaction',
   'Meet a charge with a braced point.',
   'Applies when a foe moves into band.engaged with you while you hold a polearm and did not move this turn.',
   [rk("When a foe moves into engagement with you, it takes your polearm's harm one rung lighter and is off-balance until the end of its next turn.",
       [harmw(-1, 'the foe that moved'), cond('cond.off_balance', 1, 'rounds:1', 'the foe that moved')], per='round'),
    rk("When a foe moves into engagement with you, it takes your polearm's harm, is off-balance until the end of its next turn, and its move ends at band.close.",
       [harmw(0, 'the foe that moved'), cond('cond.off_balance', 1, 'rounds:1', 'the foe that moved'), move('the foe that moved', 1)], per='round'),
    rk("When a foe moves into engagement with you, it takes your polearm's harm one rung heavier, is knocked prone, and its move ends at band.close.",
       [harmw(1, 'the foe that moved'), cond('cond.prone', 1, 'rounds:1', 'the foe that moved'), move('the foe that moved', 1)], per='round')],
   hook='on_move', when='another entity\'s band to you becomes band.engaged by its own move', lim=1, ckey=True,
   traits=['trait.action.attack', 'trait.delivery.melee'], x=[('a foe already engaged', 'verb.strike')])

ab('ab.long_guard', 'Long Guard', M + 'polearm', 2, 'stance_reach', 'Form', 'rider',
   'Hold foes at the length of your weapon.',
   'Applies while you hold a polearm in both hands and are not prone.',
   [rk("Enter the Long Guard stance for the scene: +1 to your Agility defense against melee attacks, and your polearm Strikes reach band.close.",
       [stance('long guard', [dedge(1, 'agility', 'the attack has trait.delivery.melee'), perm(2)])], f=1),
    rk("Enter the Long Guard stance for the scene: +1 to your Agility defense against melee attacks, your polearm Strikes reach band.close, and they deal +1 harm.",
       [stance('long guard', [dedge(1, 'agility', 'the attack has trait.delivery.melee'), perm(2), hedge(1, 'a Strike with the polearm')])], f=1)],
   slot='slot.stance', verbs=['any'], x=[('striking at band.near', 'a thrown or ranged weapon')])

# ---------------- archery ----------------
ab('ab.aimed_shot', 'Aimed Shot', M + 'archery.bow', 1, 'aim', 'Working', 'rider',
   'Place one arrow where it will tell.',
   'Applies to a ranged Strike with a bow or crossbow on a turn in which you have not moved.',
   [rk("Your shot gains a Precision lever and deals harm one severity rung heavier.",
       [lev('precision', 'this Strike'), sev(1, 'this Strike')], f=1),
    rk("Your shot gains a Precision lever, deals harm one severity rung heavier, and the snag for the target's cover is waived.",
       [lev('precision', 'this Strike'), sev(1, 'this Strike'), waive('the snag from flag.in_cover on the target', 'this Strike')], f=1),
    rk("Your shot gains a Precision lever, deals harm one severity rung heavier, the snag for the target's cover is waived, and the target is exposed until the scene ends.",
       [lev('precision', 'this Strike'), sev(1, 'this Strike'), waive('the snag from flag.in_cover on the target', 'this Strike'), cond('cond.exposed', 1, 'scene', FOE)], f=1)],
   verbs=['verb.strike'], lim=1, traits=['trait.action.attack', 'trait.delivery.ranged'],
   x=[('a shot after moving', 'verb.strike'), ('hitting a named small part to disarm or blind', 'verb.setup, or Great reach on the Strike (01.18.8)')])

ab('ab.volley', 'Volley', M + 'archery', 3, 'many_arrows', 'Working', 'beat',
   'Loose arrows at several marks in one breath.',
   'Applies to up to four targets within the bow\'s range bands that you can see; uses one arrow each.',
   [rk("Shoot at up to four targets you can see: one roll, compared to each one's defense. Each one hit takes your bow's harm and is off-balance until the end of its next turn.",
       [harmw(0, 'each target hit'), tgt(3), cond('cond.off_balance', 1, 'rounds:1', 'each target hit')], f=1),
    rk("Shoot at up to five targets you can see: one roll, compared to each one's defense. Each one hit takes your bow's harm, +1, and is off-balance until the end of its next turn.",
       [harmw(0, 'each target hit'), tgt(4), hedge(1, 'this Working'), cond('cond.off_balance', 1, 'rounds:1', 'each target hit')], f=1)],
   attr='agility', check=('aimed', 'verb.strike', "each target's attack defense"), spread='fork',
   traits=['trait.action.attack', 'trait.delivery.ranged'], x=[('more than one arrow at one target', 'the repeated-attempt shape (01.14.3)')])

# ---------------- thrown ----------------
ab('ab.throwers_eye', "Thrower's Eye", M + 'thrown.blades', 1, 'throw_true', 'Edge', 'passive',
   'Judge a short throw exactly.',
   'Applies to thrown Strikes at targets within band.close.',
   [rk("+1 to thrown Strikes at targets within band.close.",
       [edge(1, 'verb = verb.strike and the weapon is thrown and the target is within band.close')]),
    rk("+1 to thrown Strikes at targets within band.close, and they deal +1 harm.",
       [edge(1, 'verb = verb.strike and the weapon is thrown and the target is within band.close'), hedge(1, 'a thrown Strike within band.close')]),
    rk("+2 to thrown Strikes at targets within band.close, and they deal +1 harm.",
       [edge(2, 'verb = verb.strike and the weapon is thrown and the target is within band.close'), hedge(1, 'a thrown Strike within band.close')])],
   x=[('throws beyond band.close', 'verb.strike unmodified')])

ab('ab.pinning_cast', 'Pinning Cast', M + 'thrown.entangling', 2, 'pin_throw', 'Working', 'rider',
   'Fix a foe in place with a thrown weapon or net.',
   'Applies to a thrown Strike with a javelin, knife, bolas or net at a target within band.near that stands beside a surface or on soft ground.',
   [rk("Your thrown Strike holds the target where it stands: it is off-balance until the end of its next turn and grabbed (by the weapon or net) until it or an ally spends an action to pull free, or the scene ends.",
       [cond('cond.grabbed', 1, 'scene', FOE), cond('cond.off_balance', 1, 'rounds:1', FOE)], f=1),
    rk("Your thrown Strike pins the target where it stands: it is restrained until the end of its next turn, then grabbed until it or an ally spends an action to pull free, or the scene ends.",
       [cond('cond.restrained', 1, 'rounds:1', FOE), cond('cond.grabbed', 1, 'scene', FOE)], f=1)],
   verbs=['verb.strike'], lim=1, traits=['trait.action.attack', 'trait.delivery.ranged'],
   x=[('pinning a creature two size steps larger than you', 'verb.grapple with help')])

# ---------------- unarmed ----------------
ab('ab.iron_palm', 'Iron Palm', M + 'unarmed.striking', 1, 'body_weapon', 'Edge', 'passive',
   'Harden the striking surfaces of your body.',
   'Applies to your unarmed Strikes.',
   [rk("Your unarmed Strikes deal harm one severity rung heavier (base Moderate).",
       [sev(1, 'verb = verb.strike and you strike unarmed')]),
    rk("Your unarmed Strikes deal harm one severity rung heavier (base Moderate), +1.",
       [sev(1, 'verb = verb.strike and you strike unarmed'), hedge(1, 'an unarmed Strike')]),
    rk("Your unarmed Strikes deal harm one severity rung heavier (base Moderate), +2, and you may cite a target's off-balance or prone condition as an Amplifying lever.",
       [sev(1, 'verb = verb.strike and you strike unarmed'), hedge(2, 'an unarmed Strike'), lev('amplifying', 'an unarmed Strike against a target that is off-balance or prone', 'scene')])],
   x=[('striking a foe at band.close', 'a weapon with reach')])

ab('ab.clinch_throw', 'Clinch and Throw', M + 'unarmed.wrestling', 2, 'throw', 'Working', 'rider',
   'Turn a hold into a fall.',
   'Applies to a Grapple that succeeds against a foe no more than one size step larger than you.',
   [rk("On your successful Grapple you may throw the foe: it is prone, moved one band, and takes Light crushing harm.",
       [cond('cond.prone', 1, 'rounds:1', 'the grappled foe'), move('the grappled foe', 1), harm(1, ['harm.physical.crush'], 'the grappled foe')], f=1),
    rk("On your successful Grapple you may throw the foe: it is prone, moved up to two bands, and takes Moderate crushing harm.",
       [cond('cond.prone', 1, 'rounds:1', 'the grappled foe'), move('the grappled foe', 2), harm(2, ['harm.physical.crush'], 'the grappled foe')], f=1)],
   verbs=['verb.grapple'], traits=['trait.action.attack', 'trait.delivery.touch'], harm_tags=['harm.physical.crush'],
   x=[('throwing a foe into a hazard for the hazard\'s harm', 'the Strike knob `harm_severity` via verb.force (01.18.10)')])

# ---------------- shield ----------------
ab('ab.shield_block', 'Shield Block', M + 'shield.block', 1, 'block', 'Reaction', 'reaction',
   'Turn a blow aside with a shield.',
   'Applies to a physical attack that hits you while you hold a shield and can see the attacker.',
   [rk("In place of Fend, when a physical attack hits you, its harm is one severity rung lighter.",
       [dreact('shield block', [sev(-1, 'the hit being blocked')])], per='round'),
    rk("In place of Fend, when a physical attack hits you, its harm is one severity rung lighter; if the attack was melee, the attacker is off-balance until the end of its next turn.",
       [dreact('shield block', [sev(-1, 'the hit being blocked'), cond('cond.off_balance', 1, 'rounds:1', 'a melee attacker')])], per='round'),
    rk("In place of Fend, when a physical attack hits you, its harm is two severity rungs lighter; if the attack was melee, the attacker is off-balance until the end of its next turn.",
       [dreact('shield block', [sev(-2, 'the hit being blocked'), cond('cond.off_balance', 1, 'rounds:1', 'a melee attacker')])], per='round')],
   hook='on_hit_taken', when='the attack deals harm.physical and you hold a shield and perceive the attacker', slot='slot.defense_reaction',
   x=[('harm that is not physical (fire, spells of force)', 'ab.spell_ward or cover'), ('a blow from an unseen attacker', 'no reaction is possible')])

ab('ab.shield_wall', 'Shield Wall', M + 'shield.cover', 3, 'stance_cover', 'Form', 'rider',
   'Make your shield cover the one beside you.',
   'Applies while you hold a shield and are not prone; covers you and one ally engaged with you.',
   [rk("Enter the Shield Wall stance for the scene: you and one ally engaged with you count as in cover against ranged attacks, you gain +1 to your Agility defense, and you may take a hit meant for that ally.",
       [stance('shield wall', [dedge(1, 'agility', 'you hold a shield'), move('you and one ally engaged with you', 0, add=['flag.in_cover']), intercept()])], f=1),
    rk("Enter the Shield Wall stance for the scene: you and one ally engaged with you count as in cover against ranged attacks, you gain +1 to your Agility defense, physical harm you take is reduced by 1, and you may take a hit meant for that ally.",
       [stance('shield wall', [dedge(1, 'agility', 'you hold a shield'), move('you and one ally engaged with you', 0, add=['flag.in_cover']), intercept(), red(1, ['harm.physical'])])], f=1)],
   slot='slot.stance', verbs=['any'], ckey=True, x=[('cover against attacks from behind', 'flag.flanked removes it (06)')])

# ---------------- armor ----------------
ab('ab.armored_ease', 'Armored Ease', M + 'armor.encumbered', 1, 'armor_habit', 'Edge', 'passive',
   'Move in armor as in your own skin.',
   'Applies while you wear medium or heavy armor.',
   [rk("+1 to Exert and Move checks while you wear medium or heavy armor.",
       [edge(1, 'verb in [verb.exert, verb.move] and you wear medium or heavy armor')]),
    rk("+1 to Exert and Move checks while you wear medium or heavy armor, and physical harm you take in it is reduced by 1.",
       [edge(1, 'verb in [verb.exert, verb.move] and you wear medium or heavy armor'), red(1, ['harm.physical'])]),
    rk("+2 to Exert and Move checks while you wear medium or heavy armor, and physical harm you take in it is reduced by 1.",
       [edge(2, 'verb in [verb.exert, verb.move] and you wear medium or heavy armor'), red(1, ['harm.physical'])])],
   x=[('swimming in heavy armor', 'verb.exert at the armor\'s own snag (08)')])

ab('ab.bulwark', 'Bulwark', M + 'armor.bulwark', 4, 'last_stand', 'Reaction', 'reaction',
   'Stand under a blow that should have felled you.',
   'Applies to a hit that would bring your Vitality to 0 while you wear medium or heavy armor.',
   [rk("When a hit would bring your Vitality to 0: negate that hit, regain 3 Vitality, and until the end of your next turn you cannot be knocked prone or put off-balance.",
       [prevent('the hit would bring your Vitality to 0 and you wear medium or heavy armor'), heal(3, 'self'), immune(['cond.prone', 'cond.off_balance'])], f=2, per='scene_end')],
   hook='on_hit_taken', when='the hit would bring your Vitality to 0', lim=1,
   x=[('harm that is not a hit (falling, burning, poison)', 'verb.endure')], nmi=['that the armor is undamaged if the frame\'s cost says otherwise'])

# ---------------- tactics ----------------
ab('ab.pressing_advantage', 'Pressing Advantage', M + 'tactics.maneuver', 1, 'momentum', 'Reserve', 'trigger',
   'Draw fresh resolve from a foe\'s faltering.',
   'Applies when your own declared beat or ability applies a condition to a foe.',
   [rk("When you apply a condition to a foe, regain 1 Focus.",
       [foc(1)], per='scene_end'),
    rk("When you apply a condition to a foe, regain 1 Focus and hold a Precision lever on your next beat against that foe this round.",
       [foc(1), lev('precision', 'your next beat against that foe', 'rounds:1')], per='scene_end'),
    rk("When you apply a condition to a foe, regain 2 Focus and hold a Precision lever on your next beat against that foe this round.",
       [foc(2), lev('precision', 'your next beat against that foe', 'rounds:1')], per='scene_end')],
   hook='on_condition_applied', when='by = self and the target is a foe', x=[('a condition applied by a triggered effect', 'it is depth 1 and fires nothing (INV-12)')])

ab('ab.read_the_field', 'Read the Field', M + 'tactics.reading', 2, 'battle_sight', 'Working', 'beat',
   'Find the flaw in how a foe fights.',
   'Applies to one foe you can see that has acted in this scene.',
   [rk("Study a foe that has acted this scene (Observe, Wits, against its Wits defense). On a success, learn one of its tells in full and hold it as a Precision lever against that foe until the scene ends.",
       [rev("one tell of the target's stat block"), lev('precision', 'your beats against that foe', 'scene')]),
    rk("Study a foe that has acted this scene (Observe, Wits, against its Wits defense). On a success, learn two of its tells in full, and you and one ally who can hear you each hold a Precision lever against that foe until the scene ends.",
       [rev("two tells of the target's stat block"), lev('precision', 'your beats against that foe', 'scene'), lev('precision', "one ally's beats against that foe", 'scene')])],
   attr='wits', check=('aimed', 'verb.observe', "the target's Wits defense"), x=[('its numbers', 'sealed (09); the tell is what you get')])

ab('ab.commanding_ground', 'Commanding Ground', M + 'tactics.ground', 5, 'battle_plan', 'Working', 'beat',
   'Fix the shape of a fight before it is joined.',
   'Applies to a conflict on ground you have had at least one round to see; affects you and allies who can hear you.',
   [rk("Declare the plan (Talk or Observe, Wits, Hard). On a success, until the conflict ends you and each ally who heard it gain +1 to attack checks and +1 to Agility defense, your side's conflict beats are framed one stakes rung lower, each ally's first beat each round has reach one rung higher, none of you can be frightened, you learn the enemy leader's intent, and the enemy's morale clock ticks by your delivered reach.",
       [edge(1, 'trait.action.attack beats by you and allies who heard the plan'), dedge(1, 'agility', 'you and allies who heard the plan'), stakes('conflict beats by you and allies who heard the plan'), reach("each ally's first beat each round"), immune(['cond.frightened']), rev("the enemy leader's declared intent"), tick('the opposing side\'s morale clock', 'delivered_reach')], f=3, per='scene_end')],
   attr='wits', check=('aimed', 'verb.talk', 'obstacle tier hard'), traits=['trait.action.speech'],
   x=[('a fight already past its third round', 'ab.read_the_field')])

# ---------------- mounted ----------------
ab('ab.lance_charge', 'Lance Charge', M + 'mounted.charge', 1, 'charge', 'Working', 'rider',
   'Put a mount\'s weight behind a point.',
   'Applies to a melee Strike made from a mount on a turn in which the mount moved at least one band toward the target.',
   [rk("Your mounted Strike deals harm one severity rung heavier and drives the target back one band.",
       [sev(1, 'this Strike'), move(FOE, 1)], f=1),
    rk("Your mounted Strike deals harm one severity rung heavier, knocks the target prone and drives it back one band.",
       [sev(1, 'this Strike'), cond('cond.prone', 1, 'rounds:1', FOE), move(FOE, 1)], f=1),
    rk("Your mounted Strike deals harm two severity rungs heavier, knocks the target prone and drives it back one band.",
       [sev(2, 'this Strike'), cond('cond.prone', 1, 'rounds:1', FOE), move(FOE, 1)], f=1)],
   verbs=['verb.strike'], lim=1, traits=['trait.action.attack', 'trait.delivery.melee'],
   x=[('a charge on foot', 'verb.move then verb.strike')])

ab('ab.saddle_born', 'Saddle-Born', M + 'mounted.skirmish', 3, 'riding_fight', 'Exception', 'passive',
   'Fight from the saddle as from firm ground.',
   'Applies while you carry flag.mounted.',
   [rk("While mounted: +1 to your Agility defense, and moving away from an engaged foe provokes no reaction.",
       [dedge(1, 'agility', 'you carry flag.mounted'), waive('reactions provoked by your mount moving out of band.engaged', 'you carry flag.mounted')]),
    rk("While mounted: +1 to your Agility defense, moving away from an engaged foe provokes no reaction, and you may cite the saddle's height as a Precision lever on ranged Strikes.",
       [dedge(1, 'agility', 'you carry flag.mounted'), waive('reactions provoked by your mount moving out of band.engaged', 'you carry flag.mounted'), lev('precision', 'a ranged Strike made while mounted', 'scene', verbs=['verb.strike'])])],
   lim=1, x=[('the mount\'s own defense', 'ch.16 companions')])

# ---------------- athletics ----------------
ab('ab.surefoot', 'Surefoot', M + 'athletics.climbing', 1, 'footing', 'Edge', 'passive',
   'Keep your footing where a fall waits.',
   'Applies to Exert and Move beats whose declared failure cost is a fall.',
   [rk("Exert and Move beats whose failure would be a fall are framed one stakes rung lower.",
       [stakes('verb in [verb.exert, verb.move] and the threatened cost is a fall')]),
    rk("Exert and Move beats whose failure would be a fall are framed one stakes rung lower, and you gain +1 to climbing, jumping and balancing.",
       [stakes('verb in [verb.exert, verb.move] and the threatened cost is a fall'), edge(1, 'deed_tag under deed.martial.athletics and the method is climbing, jumping or balancing')]),
    rk("Exert and Move beats whose failure would be a fall are framed one stakes rung lower, you gain +1 to climbing, jumping and balancing, and you climb as a movement mode.",
       [stakes('verb in [verb.exert, verb.move] and the threatened cost is a fall'), edge(1, 'deed_tag under deed.martial.athletics and the method is climbing, jumping or balancing'), mode('climb', 'permanent')])],
   x=[('a sheer surface with no holds', 'G4 without a climbing mode')])

ab('ab.mighty_heave', 'Mighty Heave', M + 'athletics.lifting', 2, 'feat_of_strength', 'Permission', 'beat',
   'Move a weight no one should move alone.',
   'Applies to one object or barrier you can grip or set your shoulder to.',
   [rk("Lift, hold, shove or break one thing by main strength (Force or Exert, Might): the beat gains a Precision lever, its reach is one rung higher, and you may hold what you have lifted for 3 rounds.",
       [lev('precision', 'this beat'), reach('this beat'), perm(2)], f=1),
    rk("Lift, hold, shove or break one thing by main strength (Force or Exert, Might): the beat gains a Precision lever, its reach is one rung higher, an obstacle that would be Beyond for one person is Legendary for you, and you may hold what you have lifted for the scene.",
       [lev('precision', 'this beat'), reach('this beat'), perm(4)], f=1)],
   attr='might', check=('aimed', 'verb.force', 'the obstacle tier'), traits=['trait.sense.loud'],
   x=[('throwing the lifted thing at a foe for harm', 'verb.strike with the object\'s improvised stats')])
