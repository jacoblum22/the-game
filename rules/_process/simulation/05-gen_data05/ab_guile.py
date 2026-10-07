# deed.guile -- 16 abilities.
from dsl05 import *

G = 'deed.guile.'
FOE = 'the target of the Strike'

# ---------------- stealth ----------------
ab('ab.soft_step', 'Soft Step', G + 'stealth.sneaking', 1, 'quiet_move', 'Edge', 'passive',
   'Move without the sounds a body makes.',
   'Applies to Sneak beats in which you move.',
   [rk("Sneak beats in which you move are framed one stakes rung lower.",
       [stakes('verb = verb.sneak and the method moves you')]),
    rk("Sneak beats in which you move are framed one stakes rung lower, and you gain +1 to them.",
       [stakes('verb = verb.sneak and the method moves you'), edge(1, 'verb = verb.sneak and the method moves you')]),
    rk("Sneak beats in which you move are framed one stakes rung lower, you gain +1 to them, and your movement makes no sound a listener within band.near can hear.",
       [stakes('verb = verb.sneak and the method moves you'), edge(1, 'verb = verb.sneak and the method moves you'), waive('trait.sense.audible on your own movement', 'you are not running')])],
   x=[('being unseen in plain sight', 'ab.vanish')])

ab('ab.vanish', 'Vanish', G + 'stealth.hiding', 3, 'disappear', 'Working', 'beat',
   'Leave the notice of those who are watching you.',
   'Applies when at least one thing in the scene could conceal you: shadow, smoke, a crowd, cover, darkness.',
   [rk("Hide while observed (Sneak, Agility, against the best Wits defense among those watching). On a success you gain flag.hidden, every foe loses track of your band, and your next attack this scene from hiding holds a Precision lever.",
       [move('self', 0, add=['flag.hidden']), perm(4), lev('precision', 'your next attack from hiding', 'scene'), move('self', 1)], f=1),
    rk("Hide while observed (Sneak, Agility, against the best Wits defense among those watching). On a success you gain flag.hidden, move up to two bands unseen, every foe loses track of your band, and your next attack this scene from hiding holds a Precision lever and an Amplifying lever.",
       [move('self', 0, add=['flag.hidden']), perm(4), lev('precision', 'your next attack from hiding', 'scene'), lev('amplifying', 'your next attack from hiding', 'scene'), move('self', 2)], f=1)],
   attr='agility', check=('aimed', 'verb.sneak', "the best Wits defense among observers"), lim=1,
   x=[('hiding in an empty, lit room', 'G4: nothing conceals you')], nmi=['invisibility: a searcher who reaches you finds you'])

# ---------------- thievery ----------------
ab('ab.light_fingers', 'Light Fingers', G + 'thievery.pickpocketing', 1, 'lift', 'Edge', 'passive',
   'Take a small thing from a person unnoticed.',
   'Applies to Sneak and Handle beats that take, plant or palm an object small enough to close a hand on.',
   [rk("+1 to beats that lift, plant or palm a small object.",
       [edge(1, 'deed_tag under deed.guile.thievery and the object fits in a closed hand')]),
    rk("+1 to beats that lift, plant or palm a small object, and they are framed one stakes rung lower.",
       [edge(1, 'deed_tag under deed.guile.thievery and the object fits in a closed hand'), stakes('deed_tag under deed.guile.thievery and the object fits in a closed hand')]),
    rk("+2 to beats that lift, plant or palm a small object, and they are framed one stakes rung lower.",
       [edge(2, 'deed_tag under deed.guile.thievery and the object fits in a closed hand'), stakes('deed_tag under deed.guile.thievery and the object fits in a closed hand')])],
   x=[('taking an object someone is gripping', 'verb.grapple (snatch a held item)')])

ab('ab.ghost_lock', 'Ghost at the Lock', G + 'thievery.lockpicking', 2, 'fast_pick', 'Exception', 'rider',
   'Open a lock in the time it takes to try the handle.',
   'Applies to a lockpicking beat under lic.training.guile_thievery on a lock within your grade.',
   [rk("Your lockpicking beat takes one action in place of one interval, makes no sound, and leaves the lock unmarked.",
       [waive('the interval a lockpicking beat takes', 'this beat'), waive('trait.sense.audible on this beat', 'this beat'), fact('the lock', 'shows_tampering', False)], f=1),
    rk("Your lockpicking beat takes one action in place of one interval, makes no sound, leaves the lock unmarked, and its reach is one rung higher.",
       [waive('the interval a lockpicking beat takes', 'this beat'), waive('trait.sense.audible on this beat', 'this beat'), fact('the lock', 'shows_tampering', False), reach('this beat')], f=1)],
   verbs=['verb.handle'], x=[('a lock above your grade', 'G4 for picking; the fallback is verb.force'), ('a warded lock', 'the ward is a separate obstacle (05.7.7)')])

# ---------------- deception ----------------
ab('ab.plausible_lie', 'Plausible Lie', G + 'deception.lying', 1, 'lie_craft', 'Lever', 'passive',
   'Build a lie on something the listener already believes.',
   'Applies to Talk beats that deceive a listener about whom you hold at least one established fact of belief or want.',
   [rk("When you lie to someone, you may cite one established fact about what they believe or want as a Precision lever.",
       [lev('precision', 'a Talk beat that deceives, citing a fact about the listener', 'scene', verbs=['verb.talk'])]),
    rk("When you lie to someone, you may cite one established fact about what they believe or want as a Precision lever, and a failed lie is framed one stakes rung lower.",
       [lev('precision', 'a Talk beat that deceives, citing a fact about the listener', 'scene', verbs=['verb.talk']), stakes('a Talk beat that deceives')]),
    rk("When you lie to someone, you may cite one established fact about what they believe or want as a Precision lever and as an Amplifying lever, and a failed lie is framed one stakes rung lower.",
       [lev('precision', 'a Talk beat that deceives, citing a fact about the listener', 'scene', verbs=['verb.talk']), lev('amplifying', 'a Talk beat that deceives, citing a fact about the listener', 'scene', verbs=['verb.talk']), stakes('a Talk beat that deceives')])],
   x=[('a claim the listener knows to be false', 'G4 (15: known false)')])

ab('ab.misdirect', 'Misdirection', G + 'deception.misdirection', 4, 'decoy', 'Reaction', 'reaction',
   'Make an attacker strike where you are not.',
   'Applies to an aimed action against you by an attacker you can perceive, when another being or a solid object is within band.engaged of you.',
   [rk("When an aimed action targets you, it is turned onto another being or object engaged with you, of your choice; you move one band, gain flag.hidden against the attacker until the end of your next turn, and hold a Precision lever against the attacker until the scene ends.",
       [({'effect_id': 'eff.intercept', 'params': {'new_target': 'another being or object within band.engaged of you, your choice', 'applies_when': 'an aimed action targets you'}}, 4), move('self', 1, add=['flag.hidden']), lev('precision', 'your beats against the attacker', 'scene')], f=1, per='scene_end')],
   hook='on_check_against', lim=1, x=[('an area effect', 'verb.evade')], nmi=['that the new target is harmed unless the redirected roll succeeds against it'])

# ---------------- disguise ----------------
ab('ab.quick_change', 'Quick Change', G + 'disguise.costume', 1, 'guise', 'Permission', 'beat',
   'Assume the look of a kind of person.',
   'Applies to disguise as a type (a guard, a pilgrim, a porter) using clothing and materials at hand; not a named individual.',
   [rk("In one interval, with materials at hand, put on a disguise as a type of person (Sneak or Handle, Wits). It holds until you remove it; those who study you roll Observe against your effect DC.",
       [perm(2), waive('the hour a disguise takes to prepare', 'this beat')]),
    rk("In one action, with materials at hand, put on a disguise as a type of person (Sneak or Handle, Wits). It holds until you remove it; those who study you roll Observe against your effect DC, which is +1.",
       [perm(2), waive('the hour a disguise takes to prepare', 'this beat'), dcedge(1, 'observers study your disguise')]),
    rk("In one action, with materials at hand, put on a disguise as a type of person (Sneak or Handle, Wits). It holds until you remove it; those who study you roll Observe against your effect DC, which is +2.",
       [perm(2), waive('the hour a disguise takes to prepare', 'this beat'), dcedge(2, 'observers study your disguise')])],
   attr='wits', check=('aimed', 'verb.sneak', 'obstacle tier moderate (stored as the disguise\'s effect DC)'),
   x=[('passing as a specific named person', 'ab.living_mask')])

ab('ab.living_mask', 'The Living Mask', G + 'disguise.impersonation', 5, 'impersonate', 'Permission', 'beat',
   'Become, to every sense, a person you have studied.',
   'Applies to one specific person you have observed for at least a scene; lasts until you drop it or a day passes.',
   [rk("After an hour of preparation, take on a specific person's face, voice, gait and manner for a day (Sneak, Presence). Strangers do not get a check; those who know the person well roll Observe against your effect DC +2, and you may cite the mask as a Precision lever on Talk beats made as that person.",
       [perm(4), dcedge(2, 'someone who knows the person studies you'), waive('the Observe check of anyone who does not know the person well', 'you wear the mask'), lev('precision', 'Talk beats made as the person', 'scene', verbs=['verb.talk']), rev('one habit of speech or manner of the person, on taking the mask')], f=2, per='rest_long')],
   attr='presence', check=('aimed', 'verb.sneak', 'obstacle tier hard (stored as the mask\'s effect DC)'), oc=1, cost_text='an hour of preparation and materials',
   x=[('the person\'s memories or knowledge', 'no license grants them; 15 investigation'), ('a creature of another size or shape', 'a spell of alteration')],
   nmi=['knowledge the impersonated person holds'])

# ---------------- ambush ----------------
ab('ab.backstab', 'Backstab', G + 'ambush.assassination', 1, 'unseen_blow', 'Working', 'rider',
   'Strike a foe that does not know the blow is coming.',
   'Applies to a Strike against a target that is unaware of you, or against which you hold flag.hidden.',
   [rk("Your Strike from hiding or against an unaware target deals harm one severity rung heavier, +1.",
       [sev(1, 'this Strike'), hedge(1, 'this Strike')], f=1),
    rk("Your Strike from hiding or against an unaware target deals harm one severity rung heavier, +2, and the target is exposed until the scene ends.",
       [sev(1, 'this Strike'), hedge(2, 'this Strike'), cond('cond.exposed', 1, 'scene', FOE)], f=1),
    rk("Your Strike from hiding or against an unaware target deals harm two severity rungs heavier, +2, and the target is exposed until the scene ends.",
       [sev(2, 'this Strike'), hedge(2, 'this Strike'), cond('cond.exposed', 1, 'scene', FOE)], f=1)],
   verbs=['verb.strike'], lim=1, traits=['trait.action.attack'], ckey=True,
   x=[('a foe that is watching you', 'verb.strike; hide first (verb.sneak, ab.vanish)')])

ab('ab.throat_of_night', 'Throat of Night', G + 'ambush.assassination', 5, 'silent_kill', 'Working', 'beat',
   'End one unaware life without a sound.',
   'Applies to one unaware target within band.engaged whose threat band is at or below your power band.',
   [rk("Strike an unaware target at or below your band (Strike, Agility, against its Wits defense). On a success it takes Catastrophic harm of your weapon's type, the act makes no sound, and any witnesses within band.near must roll Observe against your effect DC to notice it happened.",
       [harm(5, ["the weapon's harm type"], FOE), waive('trait.sense.audible and trait.sense.loud on this beat', 'this beat'), cond('cond.stunned', 2, 'rounds:1', FOE), fchk('observe'), lev('precision', 'your Sneak beats until the scene ends', 'scene', verbs=['verb.sneak'])], f=3, per='scene_end')],
   attr='agility', check=('aimed', 'verb.strike', "the target's Wits defense"), lim=1,
   traits=['trait.action.attack', 'trait.delivery.melee'],
   x=[('a target that is aware of you', 'ab.backstab or verb.strike'), ('a target above your band', 'ab.backstab')])

ab('ab.spring_the_trap', 'Spring the Trap', G + 'ambush.waylaying', 2, 'first_blood', 'Lever', 'rider',
   'Open a fight from concealment on your own terms.',
   'Applies to your first beat in a conflict that you began while every foe was unaware of you.',
   [rk("On your first beat of a conflict you began from concealment: a Precision lever and an Amplifying lever on that beat, and each foe that sees it is off-balance until the end of its first turn.",
       [lev('precision', 'this beat'), lev('amplifying', 'this beat'), cond('cond.off_balance', 1, 'rounds:1', 'each foe that sees the beat'), tgt(1)], f=0, per='conflict_end'),
    rk("On your first beat of a conflict you began from concealment: a Precision lever and an Amplifying lever on that beat, each foe that sees it is off-balance until the end of its first turn, and you and each ally who lay hidden with you keep flag.hidden until the end of the first round.",
       [lev('precision', 'this beat'), lev('amplifying', 'this beat'), cond('cond.off_balance', 1, 'rounds:1', 'each foe that sees the beat'), tgt(1), move('you and each ally hidden with you', 0, add=['flag.hidden']), tgt(1)], f=0, per='conflict_end')],
   verbs=['any'], lim=1, x=[('a fight the foes began', 'verb.setup')])

# ---------------- poisoncraft ----------------
ab('ab.envenom', 'Envenom', G + 'poisoncraft.envenoming', 1, 'blade_venom', 'Working', 'rider',
   'Carry a poison into a wound.',
   'Applies to a Strike with a piercing or cutting weapon, using one dose of a poison you carry.',
   [rk("Your Strike carries a dose of poison: a target it harms is poisoned (Light) until the scene ends.",
       [cond('cond.poisoned', 1, 'scene', 'a target the Strike harms')]),
    rk("Your Strike carries a dose of poison: a target it harms is poisoned (Moderate) until the scene ends and weakened until the end of its next turn.",
       [cond('cond.poisoned', 2, 'scene', 'a target the Strike harms'), cond('cond.weakened', 1, 'rounds:1', 'a target the Strike harms')]),
    rk("Your Strike carries a dose of poison: a target it harms is poisoned (Heavy) and weakened until the scene ends, and takes +1 harm.",
       [cond('cond.poisoned', 3, 'scene', 'a target the Strike harms'), cond('cond.weakened', 1, 'scene', 'a target the Strike harms'), hedge(1, 'this Strike')])],
   verbs=['verb.strike'], oc=1, cost_text='one dose of poison (08)', harm_tags=['harm.venom.poison'],
   traits=['trait.action.attack'], x=[('brewing the poison', 'lic.training.craft_alchemy'), ('a creature with no blood or breath (constructs, most undead)', 'G4 for poison')])

ab('ab.slow_draught', 'Slow Draught', G + 'poisoncraft.dosing', 4, 'dosing', 'Working', 'beat',
   'Place a poison where it will be taken unknowing.',
   'Applies to food, drink or an object a target will take into the mouth or handle with bare skin; uses one dose.',
   [rk("Dose food, drink or an object unseen (Sneak or Handle, Agility, against the best Wits defense present). When the target takes it, it rolls Endure against your effect DC: on a failure it is poisoned (Heavy) until treated and weakened until its next long rest; you choose an onset of one interval, one hour or one watch.",
       [fchk('endure'), cond('cond.poisoned', 3, 'until_cleansed', 'the one who takes the dose'), cond('cond.weakened', 2, 'until_rest:rest_long', 'the one who takes the dose'), perm(2), waive('trait.sense.scent and taste on the dose', 'the dose is taken')], f=2)],
   attr='agility', check=('aimed', 'verb.sneak', 'the best Wits defense among those present'), oc=1, cost_text='one dose of poison (08)',
   harm_tags=['harm.venom.poison'], x=[('a lethal dose', 'the frame must be lethal and the scene lethal_context (07): the poison is then 07\'s staged affliction')])

# ---------------- escape ----------------
ab('ab.slip_free', 'Slip Free', G + 'escape.bonds', 1, 'slip', 'Working', 'beat',
   'Get a limb out of what holds it.',
   'Applies to a hold, rope, manacle or net on your own body.',
   [rk("End one of grabbed or restrained on yourself (no roll against rope or a hold; Sneak, Agility, against the lock's tier for manacles) and move one band.",
       [cleanse('cond.grabbed or cond.restrained', 'self'), move('self', 1)]),
    rk("End grabbed, restrained or pinned on yourself (no roll against rope or a hold; Sneak, Agility, against the lock's tier for manacles), move one band, and the one who held you is off-balance until the end of its next turn.",
       [cleanse('cond.grabbed, cond.restrained or cond.pinned', 'self'), move('self', 1), cond('cond.off_balance', 1, 'rounds:1', 'the one who held you'), lev('precision', 'your next beat against the one who held you', 'rounds:1')]),
    rk("As a reaction when you are grabbed, restrained or pinned, end it at once, move one band, and the one who held you is off-balance until the end of its next turn.",
       [cleanse('cond.grabbed, cond.restrained or cond.pinned', 'self'), move('self', 1), cond('cond.off_balance', 1, 'rounds:1', 'the one who held you'), lev('precision', 'your next beat against the one who held you', 'rounds:1'), react('you are grabbed, restrained or pinned')])],
   attr='agility', x=[('a locked cell', 'lic.training.guile_thievery or verb.force'), ('magical binding', '05.7.7 dispel')])

ab('ab.smoke_and_gone', 'Gone Like Smoke', G + 'escape.evasion', 2, 'withdraw', 'Exception', 'rider',
   'Leave a fight in a way that cannot be followed at once.',
   'Applies to a Move or Retreat that takes you out of band.engaged.',
   [rk("Your Move or Retreat out of engagement provokes no reaction, and you gain flag.hidden against those you left until the end of your next turn.",
       [waive('reactions provoked by leaving band.engaged', 'this beat'), move('self', 0, add=['flag.hidden']), move('self', 1)], f=1),
    rk("Your Move or Retreat out of engagement provokes no reaction, you gain flag.hidden against those you left until the end of your next turn, and a pursuit clock against you starts with two segments already filled in your favor.",
       [waive('reactions provoked by leaving band.engaged', 'this beat'), move('self', 0, add=['flag.hidden']), move('self', 1), tick('your escape clock', 2)], f=1)],
   verbs=['verb.move'], x=[('escaping a sealed room', 'find the exit first')])

# ---------------- streetwise ----------------
ab('ab.word_on_the_street', 'Word on the Street', G + 'streetwise.informants', 1, 'underworld_ear', 'Working', 'beat',
   'Ask the people who watch a town from below.',
   'Applies in a settlement of town size or larger where you have spent at least a day, or hold a contact.',
   [rk("Spend a watch asking (Talk, Wits, against the settlement's tier). On a success learn one rumor on a subject you name and who is said to know more.",
       [({'effect_id': 'eff.reveal', 'params': {'sealed_ref': 'one rumor on the named subject (11), with its source'}}, 2), fact('a named informant', 'knows_more_about', 'the subject')], per='scene_end'),
    rk("Spend a watch asking (Talk, Wits, against the settlement's tier). On a success learn two rumors on a subject you name, who is said to know more, and whether anyone has been asking about you.",
       [({'effect_id': 'eff.reveal', 'params': {'sealed_ref': 'two rumors on the named subject (11), with their sources'}}, 3), fact('a named informant', 'knows_more_about', 'the subject'), rev('whether a faction has a notice clock running on you')], per='scene_end'),
    rk("Spend an hour asking (Talk, Wits, against the settlement's tier). On a success learn two rumors on a subject you name and which of them the underworld itself believes, who knows more, and whether anyone has been asking about you.",
       [({'effect_id': 'eff.reveal', 'params': {'sealed_ref': 'two rumors on the named subject (11), their sources, and which one the underworld holds true'}}, 5), fact('a named informant', 'knows_more_about', 'the subject'), rev('whether a faction has a notice clock running on you')], per='scene_end')],
   attr='wits', check=('aimed', 'verb.talk', "the settlement's tier (ch.11)"),
   x=[('whether a rumor is true', 'sealed (11); ab.lie_sense reads the teller, not the tale')], nmi=['the truth value of a rumor'])

ab('ab.black_market', 'A Door in Every Town', G + 'streetwise.fences', 3, 'fence', 'Permission', 'beat',
   'Find the buyer or seller the law would rather you did not.',
   'Applies in a settlement of town size or larger.',
   [rk("In one watch, find a buyer for any illicit or stolen goods at their full price band, or a seller of one restricted thing you name (Talk, Wits, against the settlement's tier). The deal leaves no record that names you.",
       [perm(4), waive('the price penalty on stolen goods (08)', 'this deal'), fact('the deal', 'names_the_pc', False)], per='scene_end'),
    rk("In one hour, find a buyer for any illicit or stolen goods at their full price band, or a seller of one restricted thing you name (Talk, Wits, against the settlement's tier). The deal leaves no record that names you, and the fence owes you one favor of introduction.",
       [perm(4), waive('the price penalty on stolen goods (08)', 'this deal'), fact('the deal', 'names_the_pc', False), fact('the fence', 'owes_introduction_to', 'the pc'), waive('the watch the search takes', 'this beat')], per='scene_end')],
   attr='wits', check=('aimed', 'verb.talk', "the settlement's tier (ch.11)"), lim=1,
   x=[('a thing that does not exist in the settlement', 'the Oracle decides whether it is here')])
