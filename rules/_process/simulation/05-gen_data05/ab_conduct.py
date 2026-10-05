# Oath-gated abilities (05.3.10): 30 for the positive poles (vows, oath-bearing callings), 18 for the negative
# poles (dark callings). Each carries one conduct axis and a pole; eligibility needs the axis AND the pole.
from dsl05 import *

POS, NEG = 'positive', 'negative'


def c(axis, pole):
    return ('conduct.' + axis, pole)


# ============================== POSITIVE POLES ==============================
# ---- mercy ----
ab('ab.open_hand', 'The Open Hand', 'deed.influence.persuasion.appeal', 1, 'oath_mercy_a', 'Reaction', 'trigger',
   'Offer life to a foe you have beaten.',
   'Applies when your own beat defeats a foe that can understand an offer of quarter.',
   [rk("When you defeat a foe you may spare it: it yields alive, its side's morale clock ticks by 2, and you hold a Precision lever on Talk beats that call on its allies to yield this scene.",
       [fact('the defeated foe', 'yielded_and_spared', True), tick("the foe's side's morale clock", 2), lev('precision', "Talk beats calling on the foe's allies to yield", 'scene', verbs=['verb.talk'])], f=1, per='scene_end'),
    rk("When you defeat a foe you may spare it: it yields alive, its side's morale clock ticks by 2, you hold a Precision lever and an Amplifying lever on Talk beats that call on its allies to yield this scene.",
       [fact('the defeated foe', 'yielded_and_spared', True), tick("the foe's side's morale clock", 2), lev('precision', "Talk beats calling on the foe's allies to yield", 'scene', verbs=['verb.talk']), lev('amplifying', "Talk beats calling on the foe's allies to yield", 'scene', verbs=['verb.talk'])], f=1, per='scene_end'),
    rk("When you defeat a foe you may spare it: it yields alive, its side's morale clock ticks by 2, you hold a Precision lever and an Amplifying lever on Talk beats that call on its allies to yield this scene. Twice per scene.",
       [fact('the defeated foe', 'yielded_and_spared', True), tick("the foe's side's morale clock", 2), lev('precision', "Talk beats calling on the foe's allies to yield", 'scene', verbs=['verb.talk']), lev('amplifying', "Talk beats calling on the foe's allies to yield", 'scene', verbs=['verb.talk'])], f=1, per='scene_end', uses=2)],
   hook='on_defeat', when='the defeating beat was yours and the foe can understand you', conduct=c('mercy', POS),
   x=[('a mindless foe', 'it cannot yield')])

ab('ab.balm_of_mercy', 'Balm of Mercy', 'deed.lore.medicine.remedies', 3, 'oath_mercy_b', 'Working', 'beat',
   'Tend one who is at your mercy.',
   'Applies to one defeated, helpless or yielded being you touch.',
   [rk("Tend a defeated or helpless being: it regains 3 Vitality, its bleeding ends, its standing toward you is recorded one step warmer, and it tells you one true thing in return.",
       [heal(3, 'the tended being'), cleanse('cond.bleeding', 'the tended being'), fact('the tended being', 'standing_to_pc', 'one step warmer'), rev('one true thing the tended being knows and will give')], f=1),
    rk("Tend a defeated or helpless being: it regains 5 Vitality, its bleeding and poisoning end, its standing toward you is recorded one step warmer, and it tells you one true thing in return.",
       [heal(5, 'the tended being'), cleanse('cond.bleeding', 'the tended being'), cleanse('cond.poisoned', 'the tended being'), fact('the tended being', 'standing_to_pc', 'one step warmer'), rev('one true thing the tended being knows and will give')], f=1)],
   conduct=c('mercy', POS), x=[('an ally in the fight', 'ab.mend_flesh; ab.field_surgeon'), ('past the healing cap', '05.7.8')])

ab('ab.quarter_given', 'Quarter Given', 'deed.influence.command.rallying', 5, 'oath_mercy_c', 'Reaction', 'reaction',
   'Let one surrender end a fight.',
   'Applies when a foe yields to you in sight of its allies.',
   [rk("When a foe yields to you, up to four of its allies within band.near that see it cannot attack you until the end of their next turn; their morale clock ticks by 2; you hold a Precision lever on Talk with them this scene; and you regain 1 Focus.",
       [restr({'methods': ['attacking the one who gave quarter']}, 'each ally of the yielded foe that sees it', 'rounds:1'), tgt(3), tick("the yielded foe's side's morale clock", 2), lev('precision', 'Talk beats with those allies', 'scene', verbs=['verb.talk']), foc(1)], f=2, per='scene_end')],
   hook='on_defeat', when='a foe yields to you', lim=1, conduct=c('mercy', POS), dictates=True,
   x=[('foes that cannot see the surrender', 'they fight on')])

# ---- honesty ----
ab('ab.plain_word', 'The Plain Word', 'deed.influence.persuasion.argument', 1, 'oath_honesty_a', 'Lever', 'passive',
   'Be believed because you do not lie.',
   'Applies to Talk beats in which you state a truth that an established fact shows is to your own cost.',
   [rk("When you tell a truth that costs you, you may cite it as a Precision lever on Talk with its hearer this scene.",
       [lev('precision', 'Talk beats with a hearer of your costly truth', 'scene', verbs=['verb.talk'])]),
    rk("When you tell a truth that costs you, you may cite it as a Precision lever on Talk with its hearer this scene, and those beats are framed one stakes rung lower.",
       [lev('precision', 'Talk beats with a hearer of your costly truth', 'scene', verbs=['verb.talk']), stakes('Talk beats with a hearer of your costly truth')]),
    rk("When you tell a truth that costs you, you may cite it as a Precision lever and an Amplifying lever on Talk with its hearer this scene, and those beats are framed one stakes rung lower.",
       [lev('precision', 'Talk beats with a hearer of your costly truth', 'scene', verbs=['verb.talk']), lev('amplifying', 'Talk beats with a hearer of your costly truth', 'scene', verbs=['verb.talk']), stakes('Talk beats with a hearer of your costly truth')])],
   conduct=c('honesty', POS), x=[('a truth that costs you nothing', 'verb.talk unmodified')])

ab('ab.unclouded', 'Unclouded', 'deed.influence.insight.lies', 3, 'oath_honesty_b', 'Exception', 'passive',
   'See past what is made to deceive you.',
   'Applies to lies told to you and to effects with trait.nature.illusion.',
   [rk("+1 to Observe beats that test a lie, and you roll to see through an illusion the moment you perceive it, without first touching it or being told.",
       [edge(1, 'the beat tests whether a speaker is lying'), waive('the need to interact with an illusion before rolling to disbelieve it', 'you perceive the illusion')]),
    rk("+2 to Observe beats that test a lie, and you roll to see through an illusion the moment you perceive it, without first touching it or being told.",
       [edge(2, 'the beat tests whether a speaker is lying'), waive('the need to interact with an illusion before rolling to disbelieve it', 'you perceive the illusion')])],
   conduct=c('honesty', POS), x=[('a disguise that uses no magic', 'verb.observe against its effect DC')])

ab('ab.word_as_bond', 'Word as Bond', 'deed.influence.persuasion.rapport', 5, 'oath_honesty_c', 'Working', 'beat',
   'Speak a truth so that its hearer knows it for one.',
   'Applies to one thing you know to be true, said plainly to listeners who can hear and understand you.',
   [rk("State one true thing you know. Each listener knows you mean it; your Talk beat built on it has reach one rung higher, stakes one rung lower and a Precision lever; and their standing toward you is recorded one step warmer for the scene.",
       [perm(4), reach('the Talk beat built on the stated truth'), stakes('the Talk beat built on the stated truth'), lev('precision', 'Talk beats built on the stated truth', 'scene', verbs=['verb.talk']), fact('each listener', 'standing_to_pc', 'one step warmer this scene')], f=2, per='scene_end')],
   conduct=c('honesty', POS), traits=['trait.action.speech'], x=[('a thing you believe but that is false', 'the listeners know you mean it; they do not know it is so')])

# ---- courage ----
ab('ab.stand_fast', 'Stand Fast', 'deed.martial.tactics.single_combat', 1, 'oath_courage_a', 'Reaction', 'reaction',
   'Refuse fear when it comes.',
   'Applies when the frightened condition is applied to you.',
   [rk("When you would be frightened, the fear ends at once and your next beat holds a Precision lever.",
       [cleanse('cond.frightened', 'self'), lev('precision', 'your next beat')], per='scene_end'),
    rk("When you would be frightened, the fear ends at once, your next beat holds a Precision lever, and one ally within band.close who sees you is freed of fear as well.",
       [cleanse('cond.frightened', 'self'), lev('precision', 'your next beat'), cleanse('cond.frightened', 'one ally within band.close who sees you')], per='scene_end'),
    rk("When you would be frightened, the fear ends at once, your beats hold a Precision lever against its source until the scene ends, and one ally within band.close who sees you is freed of fear as well.",
       [cleanse('cond.frightened', 'self'), lev('precision', "your beats against the fear's source", 'scene'), cleanse('cond.frightened', 'one ally within band.close who sees you'), lev('protective', 'your next beat')], per='scene_end')],
   hook='on_condition_applied', when='to = self and the condition is cond.frightened', conduct=c('courage', POS),
   x=[('fear that is a staged affliction', 'ch.07')])

ab('ab.into_the_breach', 'Into the Breach', 'deed.martial.tactics.maneuver', 3, 'oath_courage_b', 'Working', 'rider',
   'Go where the danger is greatest for another\'s sake.',
   'Applies to a beat of yours framed at Dire stakes that is made to protect or reach another being.',
   [rk("Your Dire beat made for another's sake has reach one rung higher, holds a Precision lever and deals +1 harm, and you cannot be frightened until the end of your next turn.",
       [reach('this beat'), lev('precision', 'this beat'), hedge(1, 'this beat'), immune(['cond.frightened'])], f=1),
    rk("Your Dire beat made for another's sake has reach one rung higher, holds a Precision lever and deals +2 harm, and you cannot be frightened until the scene ends.",
       [reach('this beat'), lev('precision', 'this beat'), hedge(2, 'this beat'), immune(['cond.frightened']), lev('protective', 'your next resisted check', 'rounds:1')], f=1)],
   verbs=['any'], lim=1, conduct=c('courage', POS), x=[('a beat framed below Dire', 'the push (05.6.7)')])

ab('ab.undaunted', 'Undaunted', 'deed.influence.command.discipline', 5, 'oath_courage_c', 'Exception', 'passive',
   'Be past the reach of dread.',
   'Applies to yourself at all times.',
   [rk("You cannot be frightened; you gain +1 to Endure checks made with Resolve; and while you are Staggered your beats are framed one stakes rung lower.",
       [immune(['cond.frightened']), edge(1, 'verb = verb.endure and the attribute is resolve'), stakes('you are Staggered')])],
   conduct=c('courage', POS), x=[('allies\' fear', 'ab.rally; ab.hold_the_line')])

# ---- loyalty ----
ab('ab.at_your_side', 'At Your Side', 'deed.martial.tactics.maneuver', 1, 'oath_loyalty_a', 'Lever', 'passive',
   'Fight better beside one you are bound to.',
   'Applies to Help beats given to a being with whom you hold a recorded bond.',
   [rk("When you Help a being you hold a bond with, the helped beat also holds an Amplifying lever.",
       [lev('amplifying', 'a beat you Help, made by a being you hold a bond with', 'scene', verbs=['verb.help'])]),
    rk("When you Help a being you hold a bond with, the helped beat also holds an Amplifying lever, and you gain +1 to the Help.",
       [lev('amplifying', 'a beat you Help, made by a being you hold a bond with', 'scene', verbs=['verb.help']), edge(1, 'verb = verb.help and the one helped holds a bond with you')]),
    rk("When you Help a being you hold a bond with, the helped beat also holds an Amplifying lever and is framed one stakes rung lower, and you gain +1 to the Help.",
       [lev('amplifying', 'a beat you Help, made by a being you hold a bond with', 'scene', verbs=['verb.help']), edge(1, 'verb = verb.help and the one helped holds a bond with you'), stakes('a beat you Help, made by a being you hold a bond with')])],
   conduct=c('loyalty', POS), x=[('a stranger', 'verb.help unmodified')])

ab('ab.take_the_blow', 'Take the Blow', 'deed.martial.shield.cover', 3, 'oath_loyalty_b', 'Reaction', 'reaction',
   'Put your body between harm and one you are bound to.',
   'Applies to a hit on a being you hold a bond with, within band.close of you.',
   [rk("When a bonded ally within band.close is hit, move to them and take the hit in their place, one severity rung lighter.",
       [intercept('a being you hold a bond with, within band.close, is hit'), move('self', 1), sev(-1, 'the hit you take in their place')], f=1, per='round'),
    rk("When a bonded ally within band.close is hit, move to them and take the hit in their place, two severity rungs lighter.",
       [intercept('a being you hold a bond with, within band.close, is hit'), move('self', 1), sev(-2, 'the hit you take in their place')], f=1, per='round')],
   hook='on_hit_taken', when='the one hit is a being you hold a bond with, within band.close', conduct=c('loyalty', POS),
   x=[('an area effect', 'each being resists it for itself')])

ab('ab.unbroken_bond', 'Unbroken Bond', 'deed.martial.shield.block', 5, 'oath_loyalty_c', 'Reaction', 'reaction',
   'Refuse to let one you are bound to fall.',
   'Applies to a hit that would bring a bonded ally within band.near to 0 Vitality.',
   [rk("When a hit would bring a bonded ally within band.near to 0 Vitality: move up to two bands to them, negate that hit, and they regain 3 Vitality, are freed of fear, and hold a Protective lever until the scene ends.",
       [move('self', 2), prevent('the hit would bring a being you hold a bond with to 0 Vitality'), heal(3, 'the bonded ally'), cleanse('cond.frightened', 'the bonded ally'), lev('protective', "the bonded ally's beats and resisted checks", 'scene')], f=2, per='rest_long')],
   hook='on_hit_taken', when='the hit would bring a bonded ally within band.near to 0 Vitality', conduct=c('loyalty', POS),
   x=[('harm that is not a hit', 'verb.help; healing')])

# ---- generosity ----
ab('ab.open_purse', 'Open Purse', 'deed.influence.trade.venture', 1, 'oath_generosity_a', 'Reaction', 'trigger',
   'Give so that the gift is remembered.',
   'Applies when you give away, with no return asked, something whose loss matters to you (a state write shows the transfer).',
   [rk("When you give away something that matters to you, the receiver's standing toward you is recorded one step warmer, and you hold a Precision lever on Talk with those who saw it this scene.",
       [fact('the receiver', 'standing_to_pc', 'one step warmer'), lev('precision', 'Talk beats with those who saw the gift', 'scene', verbs=['verb.talk'])], per='scene_end'),
    rk("When you give away something that matters to you, the receiver's standing toward you is recorded one step warmer, you hold a Precision lever on Talk with those who saw it this scene, and you regain 1 Focus.",
       [fact('the receiver', 'standing_to_pc', 'one step warmer'), lev('precision', 'Talk beats with those who saw the gift', 'scene', verbs=['verb.talk']), foc(1)], per='scene_end'),
    rk("When you give away something that matters to you, the receiver's standing toward you is recorded one step warmer, you hold a Precision lever and an Amplifying lever on Talk with those who saw it this scene, and you regain 1 Focus.",
       [fact('the receiver', 'standing_to_pc', 'one step warmer'), lev('precision', 'Talk beats with those who saw the gift', 'scene', verbs=['verb.talk']), lev('amplifying', 'Talk beats with those who saw the gift', 'scene', verbs=['verb.talk']), foc(1)], per='scene_end')],
   hook='on_fact_set', when='a possession or coin of yours passes to another as a gift', conduct=c('generosity', POS),
   x=[('a trade or a bribe', 'ab.sharp_bargain; 15')])

ab('ab.shared_strength', 'Shared Strength', 'deed.influence.command.rallying', 3, 'oath_generosity_b', 'Reserve', 'rider',
   'Give another the reserves you would have spent.',
   'Applies to one willing ally within band.close.',
   [rk("Give up to 2 of your own Focus to an ally within band.close: they regain what you give, one condition on them ends, and they hold a Precision lever until the scene ends.",
       [foc(2, 'one ally within band.close'), cleanse('one condition of category physical or mental', 'that ally'), lev('precision', "that ally's beats", 'scene')]),
    rk("Give up to 3 of your own Focus to an ally within band.close: they regain what you give, one condition on them ends, and they hold a Precision lever until the scene ends.",
       [foc(3, 'one ally within band.close'), cleanse('one condition of category physical or mental', 'that ally'), lev('precision', "that ally's beats", 'scene')])],
   verbs=['any'], oc=4, cost_text='you lose as much Focus as you give (2 or 3)', conduct=c('generosity', POS),
   x=[('giving Vitality', 'healing abilities'), ('past the receiver\'s generation cap', '05.6.10')])

ab('ab.widows_mite', "The Widow's Mite", 'deed.influence.persuasion.rapport', 5, 'oath_generosity_c', 'Reserve', 'trigger',
   'Be repaid for giving what you could not spare.',
   'Applies when you give away the last of something you need: the last supply, coin, dose or arrow.',
   [rk("When you give away the last of something you need, regain 2 Focus, hold a Protective lever on your beats until the scene ends, and the receiver's standing toward you is recorded one step warmer.",
       [foc(2), lev('protective', 'your beats', 'scene'), fact('the receiver', 'standing_to_pc', 'one step warmer')], per='rest_long')],
   hook='on_resource_depleted', when='the quantity reached its minimum because you gave it away', conduct=c('generosity', POS),
   x=[('spending or losing the last of it', 'only a gift counts')])

# ---- justice ----
ab('ab.name_the_wrong', 'Name the Wrong', 'deed.lore.law.custom', 1, 'oath_justice_a', 'Lever', 'rider',
   'Charge someone with what they did.',
   'Applies to a Talk beat that accuses a being of a wrong that is an established fact.',
   [rk("When you accuse someone of a wrong that is an established fact, the beat holds a Precision lever and an Amplifying lever.",
       [lev('precision', 'this beat'), lev('amplifying', 'this beat')]),
    rk("When you accuse someone of a wrong that is an established fact, the beat holds a Precision lever and an Amplifying lever and is framed one stakes rung lower.",
       [lev('precision', 'this beat'), lev('amplifying', 'this beat'), stakes('this beat')]),
    rk("When you accuse someone of a wrong that is an established fact, the beat holds a Precision lever and an Amplifying lever and is framed one stakes rung lower, and the accused is off-balance until the end of its next turn.",
       [lev('precision', 'this beat'), lev('amplifying', 'this beat'), stakes('this beat'), cond('cond.off_balance', 1, 'rounds:1', 'the accused'), fact('the accusation', 'made_before', 'those present')])],
   verbs=['verb.talk'], conduct=c('justice', POS), x=[('a wrong you only suspect', 'investigation (15) first')])

ab('ab.mark_of_judgment', 'Mark of Judgment', 'deed.lore.law.courts', 3, 'oath_justice_b', 'Working', 'beat',
   'Declare a wrongdoer answerable to you.',
   'Applies to one being within band.near whose wrong against the innocent is an established fact.',
   [rk("Declare one wrongdoer judged. Until the scene ends it is exposed, your Strikes against it deal +1 harm, you hold a Precision lever against it, and you cannot be frightened by it.",
       [cond('cond.exposed', 1, 'scene', 'the judged being'), hedge(1, 'a Strike against the judged being'), lev('precision', 'your beats against the judged being', 'scene'), immune(['cond.frightened'])], f=1, per='scene_end'),
    rk("Declare one wrongdoer judged. Until the scene ends it is exposed and weakened, your Strikes against it deal +1 harm, you hold a Precision lever against it, and you cannot be frightened by it.",
       [cond('cond.exposed', 1, 'scene', 'the judged being'), cond('cond.weakened', 1, 'scene', 'the judged being'), hedge(1, 'a Strike against the judged being'), lev('precision', 'your beats against the judged being', 'scene'), immune(['cond.frightened'])], f=1, per='scene_end')],
   conduct=c('justice', POS), traits=['trait.action.speech'], x=[('a being whose wrong is not established', 'it has no hold')])

ab('ab.scales_balanced', 'The Scales Balanced', 'deed.martial.tactics.single_combat', 5, 'oath_justice_c', 'Reaction', 'reaction',
   'Return to a wrongdoer the harm it deals the innocent.',
   'Applies when a foe\'s attack harms an ally or a bystander within band.near of you.',
   [rk("When a foe harms an ally or bystander within band.near, that foe takes Grievous radiant harm, is weakened until the scene ends, and you hold a Precision lever against it until the scene ends.",
       [harm(4, ['harm.radiance.holy'], 'the foe that dealt the harm'), cond('cond.weakened', 1, 'scene', 'the foe that dealt the harm'), lev('precision', 'your beats against that foe', 'scene')], f=2, per='scene_end')],
   hook='on_harm_taken', when='an ally or bystander within band.near of you takes harm from a foe', conduct=c('justice', POS), harm_tags=['harm.radiance.holy'],
   x=[('harm done to you', 'ab.riposte; your own defenses')])

# ---- humility ----
ab('ab.quiet_service', 'Quiet Service', 'deed.influence.teaching.mentoring', 1, 'oath_humility_a', 'Edge', 'passive',
   'Make another\'s work better than your own.',
   'Applies to your Help beats.',
   [rk("+1 to your Help beats.",
       [edge(1, 'verb = verb.help')]),
    rk("+1 to your Help beats, and a beat you help is framed one stakes rung lower.",
       [edge(1, 'verb = verb.help'), stakes('a beat you Help')]),
    rk("+2 to your Help beats, and a beat you help is framed one stakes rung lower.",
       [edge(2, 'verb = verb.help'), stakes('a beat you Help')])],
   conduct=c('humility', POS), x=[('your own beats', 'they are unchanged')])

ab('ab.unseen_hand', 'The Unseen Hand', 'deed.martial.tactics.maneuver', 3, 'oath_humility_b', 'Exception', 'passive',
   'Help where you could not have done the thing yourself.',
   'Applies to your Help beats.',
   [rk("You may Help a beat you could not attempt alone, and a beat you help has reach one rung higher.",
       [waive('the rule that a helper must be able to attempt the beat alone', 'you Help'), reach('a beat you Help')]),
    rk("You may Help a beat you could not attempt alone, a beat you help has reach one rung higher, and it also holds an Amplifying lever.",
       [waive('the rule that a helper must be able to attempt the beat alone', 'you Help'), reach('a beat you Help'), lev('amplifying', 'a beat you Help', 'scene', verbs=['verb.help'])])],
   conduct=c('humility', POS), x=[('helping from beyond band.close', 'you must be there')])

ab('ab.last_made_first', 'The Last Made First', 'deed.influence.command.directing', 5, 'oath_humility_c', 'Working', 'beat',
   'Spend your own moment wholly on another\'s.',
   'Applies to one ally within band.close; it takes your beat.',
   [rk("Give your beat to an ally within band.close: their next beat has reach one rung higher, stakes one rung lower, +1, a Precision lever and an Amplifying lever; one condition on them ends; and they regain 1 Focus.",
       [reach("the ally's next beat"), stakes("the ally's next beat"), edge(1, "the ally's next beat"), lev('precision', "the ally's next beat"), lev('amplifying', "the ally's next beat"), cleanse('one condition of category physical or mental', 'the ally'), foc(1, 'the ally')], f=2, per='scene_end')],
   conduct=c('humility', POS), x=[('an extra action for the ally', 'INV-11: their next beat is improved; none is added')])

# ---- restraint ----
ab('ab.measured_blow', 'Measured Blow', 'deed.martial.unarmed.striking', 1, 'oath_restraint_a', 'Working', 'rider',
   'Strike to stop and not to break.',
   'Applies to a Strike you choose to deal one severity rung lighter.',
   [rk("Deal this Strike's harm one rung lighter: the target is off-balance until the end of its next turn, and your next beat against it holds a Precision lever.",
       [cond('cond.off_balance', 1, 'rounds:1', 'the target of the Strike'), lev('precision', 'your next beat against the target')]),
    rk("Deal this Strike's harm one rung lighter: the target is off-balance and dazed until the end of its next turn, and your next beat against it holds a Precision lever.",
       [cond('cond.off_balance', 1, 'rounds:1', 'the target of the Strike'), cond('cond.dazed', 1, 'rounds:1', 'the target of the Strike'), lev('precision', 'your next beat against the target')]),
    rk("Deal this Strike's harm one rung lighter: the target is knocked prone and dazed until the end of its next turn, and your beats against it hold a Precision lever until the scene ends.",
       [cond('cond.prone', 1, 'rounds:1', 'the target of the Strike'), cond('cond.dazed', 1, 'rounds:1', 'the target of the Strike'), lev('precision', 'your beats against the target', 'scene')])],
   verbs=['verb.strike'], conduct=c('restraint', POS), traits=['trait.action.attack'],
   x=[('a Strike at full harm', 'it gives nothing')])

ab('ab.still_water', 'Still Water', 'deed.martial.unarmed.wrestling', 3, 'oath_restraint_b', 'Reaction', 'reaction',
   'Let a provocation pass through you.',
   'Applies when charm, fear or a compulsion is applied to you.',
   [rk("When you would be charmed, frightened or compelled, it ends at once, and neither charm nor fear can be applied to you until the scene ends.",
       [cleanse('cond.charmed or cond.frightened', 'self'), immune(['cond.charmed', 'cond.frightened'])], f=1, per='scene_end'),
    rk("When you would be charmed, frightened or compelled, it ends at once, neither charm nor fear can be applied to you until the scene ends, and your next beat holds a Precision lever and a Protective lever.",
       [cleanse('cond.charmed or cond.frightened', 'self'), immune(['cond.charmed', 'cond.frightened']), lev('precision', 'your next beat'), lev('protective', 'your next beat')], f=1, per='scene_end')],
   hook='on_condition_applied', when='to = self and the condition is cond.charmed or cond.frightened', conduct=c('restraint', POS),
   x=[('bodily conditions', 'verb.endure')])

ab('ab.empty_hand', 'The Empty Hand', 'deed.martial.unarmed.wrestling', 5, 'oath_restraint_c', 'Form', 'rider',
   'Fight so that no one need die of it.',
   'Applies while you hold no weapon.',
   [rk("Enter the Empty Hand stance for the scene: +1 to Agility defense, physical harm you take is reduced by 1, you hold a Precision lever against a foe that attacked you this round, and a foe you defeat is left alive and defeated if you choose.",
       [stance('empty hand', [dedge(1, 'agility', 'you hold no weapon'), red(1, ['harm.physical']), lev('precision', 'your beats against a foe that attacked you this round', 'scene'), perm(2)])], f=1)],
   slot='slot.stance', verbs=['any'], conduct=c('restraint', POS), x=[('fighting with a weapon in hand', 'the stance ends')])

# ---- piety ----
ab('ab.daily_office', 'The Daily Office', 'deed.lore.religion.rites', 1, 'oath_piety_a', 'Reserve', 'trigger',
   'Keep the observance your keeper asks each dawn.',
   'Applies at dawn, after an interval of observance.',
   [rk("At dawn, after an interval of observance, regain 1 Focus and hold a Protective lever on your first resisted check of each scene until the next dawn.",
       [foc(1), lev('protective', 'your first resisted check of each scene', 'scene')], per='day'),
    rk("At dawn, after an interval of observance, regain 1 Focus and hold a Protective lever on your first resisted check and a Precision lever on your first beat of each scene until the next dawn.",
       [foc(1), lev('protective', 'your first resisted check of each scene', 'scene'), lev('precision', 'your first beat of each scene', 'scene')], per='day'),
    rk("At dawn, after an interval of observance, regain 2 Focus and hold a Protective lever on your first resisted check and a Precision lever on your first beat of each scene until the next dawn.",
       [foc(2), lev('protective', 'your first resisted check of each scene', 'scene'), lev('precision', 'your first beat of each scene', 'scene')], per='day')],
   hook='on_boundary', when='boundary = day and you kept an interval of observance', conduct=c('piety', POS),
   x=[('a dawn on which you kept no observance', 'nothing is given')])

ab('ab.hallow', 'Hallow', 'deed.lore.religion.pantheon', 3, 'oath_piety_b', 'Working', 'beat',
   'Mark the ground you stand on as your keeper\'s.',
   'Applies to the ground within band.close of you, for the scene.',
   [rk("For the scene the ground within band.close of where you stand is recorded as consecrated: undead and fiends on it take -2 to their checks, allies on it hold a Protective lever, and none of them can be frightened there.",
       [fact('the ground within band.close', 'consecrated', 'until scene_end'), ({'effect_id': 'eff.status_modifier', 'params': {'amount': -2, 'applies_when': 'the actor is creature.undead or creature.fiend and stands on the hallowed ground'}}, 2), lev('protective', 'beats and resisted checks by allies on the hallowed ground', 'scene'), immune(['cond.frightened'])], f=1, per='scene_end'),
    rk("For the scene the ground within band.near of where you stand is recorded as consecrated: undead and fiends on it take -2 to their checks and Light radiant harm when they enter it, allies on it hold a Protective lever, and none of them can be frightened there.",
       [fact('the ground within band.near', 'consecrated', 'until scene_end'), ({'effect_id': 'eff.status_modifier', 'params': {'amount': -2, 'applies_when': 'the actor is creature.undead or creature.fiend and stands on the hallowed ground'}}, 2), lev('protective', 'beats and resisted checks by allies on the hallowed ground', 'scene'), immune(['cond.frightened']), harm(1, ['harm.radiance.holy'], 'an undead or fiend that enters the hallowed ground'), tgt(1)], f=1, per='scene_end')],
   conduct=c('piety', POS), traits=['trait.nature.sacred'], x=[('a lasting consecration', 'rit.consecrate_ground')])

ab('ab.intercession', 'Intercession', 'deed.lore.religion.rites', 5, 'oath_piety_c', 'Working', 'beat',
   'Ask your keeper to stand between one life and its end.',
   'Applies to one being you name aloud within band.close; lasts until the next dawn; one intercession at a time.',
   [rk("Pray over one being. The next hit before dawn that would bring it to 0 Vitality is negated; it then regains 5 Vitality, is freed of fear and charm, and holds a Protective lever until that scene ends.",
       [prevent('the hit would bring the named being to 0 Vitality', 'day', 1), heal(5, 'the named being'), cleanse('cond.frightened', 'the named being'), cleanse('cond.charmed', 'the named being'), lev('protective', "the named being's beats and resisted checks", 'scene')], f=2, per='rest_long')],
   conduct=c('piety', POS), traits=['trait.action.speech', 'trait.nature.sacred'], x=[('harm that is not a hit', 'healing; verb.endure')])

# ---- protection ----
ab('ab.interpose', 'Interpose', 'deed.martial.shield.cover', 1, 'oath_protection_a', 'Reaction', 'reaction',
   'Step into a blow meant for the one beside you.',
   'Applies to a hit on an ally engaged with you.',
   [rk("When an ally engaged with you is hit, take the hit in their place.",
       [intercept()], per='round'),
    rk("When an ally engaged with you is hit, take the hit in their place, one severity rung lighter.",
       [intercept(), sev(-1, 'the hit you take in their place')], per='round'),
    rk("When an ally engaged with you is hit, take the hit in their place, one severity rung lighter, and the attacker is off-balance until the end of its next turn.",
       [intercept(), sev(-1, 'the hit you take in their place'), cond('cond.off_balance', 1, 'rounds:1', 'the attacker'), lev('precision', 'your next beat against the attacker')], per='round')],
   hook='on_hit_taken', when='the one hit is an ally engaged with you', conduct=c('protection', POS),
   x=[('an ally beyond band.engaged', 'ab.take_the_blow')])

ab('ab.shelter_the_weak', 'Shelter the Weak', 'deed.martial.shield.cover', 3, 'oath_protection_b', 'Form', 'rider',
   'Make the space around you safe for those who cannot fight.',
   'Applies to allies within band.close of you who are bloodied or are not combatants.',
   [rk("For the scene, bloodied allies and noncombatants within band.close of you have +1 to Agility defense, count as in cover, and hold a Protective lever on their resisted checks.",
       [aura('band.close', [dedge(1, 'agility', 'a bloodied ally or noncombatant within band.close of you'), move('each sheltered being', 0, add=['flag.in_cover']), lev('protective', 'resisted checks by those sheltered', 'scene')])], f=1),
    rk("For the scene, bloodied allies and noncombatants within band.close of you have +1 to Agility defense, count as in cover, hold a Protective lever on their resisted checks, and take 1 less physical harm.",
       [aura('band.close', [dedge(1, 'agility', 'a bloodied ally or noncombatant within band.close of you'), move('each sheltered being', 0, add=['flag.in_cover']), lev('protective', 'resisted checks by those sheltered', 'scene'), red(1, ['harm.physical'])])], f=1)],
   slot='slot.aura', verbs=['any'], conduct=c('protection', POS), traits=['trait.delivery.aura'], x=[('yourself', 'the aura shelters others')])

ab('ab.none_shall_pass', 'None Shall Pass', 'deed.martial.shield.block', 5, 'oath_protection_c', 'Form', 'rider',
   'Hold a place so that harm must come through you.',
   'Applies to one being or doorway within band.close that you name as guarded; ends if you move away from it.',
   [rk("Enter the stance for the scene: +1 to Agility defense; a foe that attacks the one you guard strikes you instead; hits you take in its place are one severity rung lighter; and the first hit each scene that would reach the guarded one past you is negated.",
       [stance('none shall pass', [dedge(1, 'agility', 'you hold the guarded place'), intercept('a foe attacks the one you guard'), sev(-1, 'a hit you take in the guarded one\'s place'), prevent('a hit would reach the guarded one', 'scene_end', 1)])], f=2)],
   slot='slot.stance', verbs=['any'], conduct=c('protection', POS), x=[('guarding more than one being or opening', 'one stance, one charge')])

# ============================== NEGATIVE POLES (dark callings) ==============================
ab('ab.twist_the_knife', 'Twist the Knife', 'deed.guile.ambush.assassination', 1, 'dark_mercy_a', 'Working', 'rider',
   'Make a helpless foe\'s harm worse than it need be.',
   'Applies to a Strike against a target that is prone, grabbed, restrained or defeated.',
   [rk("Your Strike against a helpless target deals +1 harm and holds an Amplifying lever.",
       [hedge(1, 'this Strike'), lev('amplifying', 'this Strike')]),
    rk("Your Strike against a helpless target deals +2 harm and holds an Amplifying lever.",
       [hedge(2, 'this Strike'), lev('amplifying', 'this Strike')]),
    rk("Your Strike against a helpless target deals harm one severity rung heavier, +1, holds an Amplifying lever, and leaves it bleeding.",
       [sev(1, 'this Strike'), hedge(1, 'this Strike'), lev('amplifying', 'this Strike'), cond('cond.bleeding', 1, 'rounds:1', 'the target')])],
   verbs=['verb.strike'], conduct=c('mercy', NEG), traits=['trait.action.attack'], x=[('a foe on its feet and free', 'verb.strike')])

ab('ab.terror_of_example', 'Terror of Example', 'deed.influence.intimidation.display', 3, 'dark_mercy_b', 'Reaction', 'trigger',
   'Make one death teach the others.',
   'Applies when you kill or maim a defeated foe in sight of its allies.',
   [rk("When you kill or maim a defeated foe, up to three of its allies that see it are frightened of you until the scene ends, and their morale clock ticks by 2.",
       [cond('cond.frightened', 1, 'scene', 'each ally that sees it'), tgt(2), tick("the foe's side's morale clock", 2)], f=1, per='scene_end'),
    rk("When you kill or maim a defeated foe, up to five of its allies that see it are frightened of you until the scene ends, and their morale clock ticks by 2.",
       [cond('cond.frightened', 1, 'scene', 'each ally that sees it'), tgt(4), tick("the foe's side's morale clock", 2)], f=1, per='scene_end')],
   hook='on_fact_set', when='a defeated foe is killed or maimed by you in sight of its allies', conduct=c('mercy', NEG), dictates=True, traits=['trait.nature.mental'],
   x=[('the mindless', 'they learn nothing')])

ab('ab.forked_tongue', 'Forked Tongue', 'deed.guile.deception.lying', 1, 'dark_honesty_a', 'Lever', 'passive',
   'Use another\'s trust as the handle of a lie.',
   'Applies to Talk beats that deceive a listener whose standing toward you is Warm or better.',
   [rk("When you lie to someone who trusts you, you may cite that trust as a Precision lever.",
       [lev('precision', 'a Talk beat that deceives a listener whose standing toward you is Warm or better', 'scene', verbs=['verb.talk'])]),
    rk("When you lie to someone who trusts you, you may cite that trust as a Precision lever and an Amplifying lever.",
       [lev('precision', 'a Talk beat that deceives a listener whose standing toward you is Warm or better', 'scene', verbs=['verb.talk']), lev('amplifying', 'a Talk beat that deceives a listener whose standing toward you is Warm or better', 'scene', verbs=['verb.talk'])]),
    rk("When you lie to someone who trusts you, you may cite that trust as a Precision lever and an Amplifying lever, and the lie is framed one stakes rung lower.",
       [lev('precision', 'a Talk beat that deceives a listener whose standing toward you is Warm or better', 'scene', verbs=['verb.talk']), lev('amplifying', 'a Talk beat that deceives a listener whose standing toward you is Warm or better', 'scene', verbs=['verb.talk']), stakes('a Talk beat that deceives a listener whose standing toward you is Warm or better')])],
   conduct=c('honesty', NEG), x=[('a listener who is Neutral or worse', 'ab.plausible_lie')])

ab('ab.false_witness', 'False Witness', 'deed.guile.deception.con', 3, 'dark_honesty_b', 'Working', 'beat',
   'Plant a thing that did not happen in another\'s belief.',
   'Applies to one listener, about one event the listener did not see.',
   [rk("Tell one listener of an event they did not see (Talk, Presence, against their Wits defense). On a success it is recorded as believed by them until they meet proof against it, and you hold a Precision lever on Talk built on it.",
       [perm(4), fact('the listener', 'believes', 'the stated event'), lev('precision', 'Talk beats built on the planted belief', 'scene', verbs=['verb.talk'])], f=1),
    rk("Tell up to three listeners of an event they did not see (Talk, Presence, against the highest Wits defense). On a success it is recorded as believed by them until they meet proof against it, and you hold a Precision lever on Talk built on it.",
       [perm(4), fact('each listener', 'believes', 'the stated event'), lev('precision', 'Talk beats built on the planted belief', 'scene', verbs=['verb.talk']), tgt(2)], f=1)],
   attr='presence', check=('aimed', 'verb.talk', "the listener's Wits defense"), conduct=c('honesty', NEG),
   x=[('an event the listener saw otherwise', 'G4 (15: known false)')])

ab('ab.knife_in_the_back', 'Knife in the Back', 'deed.guile.ambush.waylaying', 1, 'dark_loyalty_a', 'Working', 'rider',
   'Strike one who counts you a friend.',
   'Applies to a Strike against a being whose standing toward you is Warm or better, or who fights on your side.',
   [rk("Your Strike against one who counts you an ally deals harm one severity rung heavier.",
       [sev(1, 'this Strike')]),
    rk("Your Strike against one who counts you an ally deals harm one severity rung heavier, +1, and holds a Precision lever.",
       [sev(1, 'this Strike'), hedge(1, 'this Strike'), lev('precision', 'this Strike')]),
    rk("Your Strike against one who counts you an ally deals harm two severity rungs heavier, +1, and holds a Precision lever.",
       [sev(2, 'this Strike'), hedge(1, 'this Strike'), lev('precision', 'this Strike')])],
   verbs=['verb.strike'], conduct=c('loyalty', NEG), traits=['trait.action.attack'], x=[('a declared foe', 'ab.backstab')])

ab('ab.turncoat', 'Turncoat', 'deed.guile.deception.feint', 3, 'dark_loyalty_b', 'Working', 'beat',
   'Change sides at the moment it pays most.',
   'Applies in a conflict in which you have fought on one side; once per conflict.',
   [rk("Declare for the other side. Up to three of your former allies are exposed until the scene ends, your first beat against one of them holds a Precision lever and an Amplifying lever, and your new side's standing toward you is recorded as Neutral for the scene.",
       [cond('cond.exposed', 1, 'scene', 'each former ally'), tgt(2), lev('precision', 'your first beat against a former ally'), lev('amplifying', 'your first beat against a former ally'), fact('the new side', 'standing_to_pc', 'Neutral this scene')], f=1, per='scene_end'),
    rk("Declare for the other side. Up to three of your former allies are exposed until the scene ends, your beats against them hold a Precision lever until the scene ends and your first holds an Amplifying lever, and your new side's standing toward you is recorded as Neutral for the scene.",
       [cond('cond.exposed', 1, 'scene', 'each former ally'), tgt(2), lev('precision', 'your beats against former allies', 'scene'), lev('amplifying', 'your first beat against a former ally'), fact('the new side', 'standing_to_pc', 'Neutral this scene'), move('self', 1)], f=1, per='scene_end')],
   conduct=c('loyalty', NEG), x=[('the new side\'s lasting trust', 'standing is 15\'s; betrayal is remembered (11)')])

ab('ab.grasping_hand', 'Grasping Hand', 'deed.guile.thievery.pickpocketing', 1, 'dark_generosity_a', 'Edge', 'passive',
   'Take what another holds.',
   'Applies to beats that take an object from a being by stealth, snatch or threat.',
   [rk("+1 to beats that take an object from another being.",
       [edge(1, 'the beat takes an object from another being')]),
    rk("+1 to beats that take an object from another being, and they are framed one stakes rung lower.",
       [edge(1, 'the beat takes an object from another being'), stakes('the beat takes an object from another being')]),
    rk("+2 to beats that take an object from another being, and they are framed one stakes rung lower.",
       [edge(2, 'the beat takes an object from another being'), stakes('the beat takes an object from another being')])],
   conduct=c('generosity', NEG), x=[('unattended objects', 'a free activity')])

ab('ab.price_of_everything', 'The Price of Everything', 'deed.influence.trade.haggling', 3, 'dark_generosity_b', 'Working', 'beat',
   'Find what a person would sell themselves for.',
   'Applies to one being with a mind that you have spoken with for a few moments.',
   [rk("Study a person (Observe or Talk, Wits, against their Resolve defense). On a success learn the price that would buy their cooperation in one thing you name, and hold it as a Precision lever on bribing them; that beat is framed one stakes rung lower.",
       [rev('the price that would buy the person\'s cooperation in the named thing'), lev('precision', 'Talk beats that bribe the person', 'scene', verbs=['verb.talk']), stakes('Talk beats that bribe the person')]),
    rk("Study a person (Observe or Talk, Wits, against their Resolve defense). On a success learn the price that would buy their cooperation in one thing you name and what they fear losing, and hold both as a Precision lever on bribing or threatening them; that beat is framed one stakes rung lower.",
       [rev('the price that would buy the person\'s cooperation in the named thing'), rev('what the person most fears losing'), lev('precision', 'Talk beats that bribe or threaten the person', 'scene', verbs=['verb.talk']), stakes('Talk beats that bribe or threaten the person')])],
   attr='wits', check=('aimed', 'verb.observe', "the person's Resolve defense"), conduct=c('generosity', NEG),
   x=[('a person with a recorded refusal on the matter', 'the refusal holds: the price is "nothing you have"')])

ab('ab.heavy_hand', 'Heavy Hand', 'deed.influence.command.discipline', 1, 'dark_justice_a', 'Lever', 'rider',
   'Command one who cannot refuse you safely.',
   'Applies to a Talk beat that commands a being in your power or of lower station.',
   [rk("When you command one in your power, the beat holds a Precision lever and an Amplifying lever.",
       [lev('precision', 'this beat'), lev('amplifying', 'this beat')]),
    rk("When you command one in your power, the beat holds a Precision lever and an Amplifying lever and is framed one stakes rung lower.",
       [lev('precision', 'this beat'), lev('amplifying', 'this beat'), stakes('this beat')]),
    rk("When you command one in your power, the beat holds a Precision lever and an Amplifying lever, is framed one stakes rung lower, and the one commanded is frightened of you until the end of its next turn.",
       [lev('precision', 'this beat'), lev('amplifying', 'this beat'), stakes('this beat'), cond('cond.frightened', 1, 'rounds:1', 'the one commanded')])],
   verbs=['verb.talk'], conduct=c('justice', NEG), dictates=True, x=[('an equal or a superior', 'verb.talk')])

ab('ab.make_an_example', 'Make an Example', 'deed.influence.intimidation.threat', 3, 'dark_justice_b', 'Working', 'beat',
   'Punish one so that many obey.',
   'Applies to one being in your power, punished in view of up to four others.',
   [rk("Punish one being in view of others. Up to four who see it are frightened of you until the scene ends and cannot openly disobey you this scene.",
       [cond('cond.frightened', 1, 'scene', 'each one who sees it'), tgt(3), restr({'methods': ['openly disobeying the punisher']}, 'each one who sees it', 'scene')], f=1, per='scene_end'),
    rk("Punish one being in view of others. Up to six who see it are frightened of you until the scene ends and cannot openly disobey you this scene.",
       [cond('cond.frightened', 1, 'scene', 'each one who sees it'), tgt(5), restr({'methods': ['openly disobeying the punisher']}, 'each one who sees it', 'scene')], f=1, per='scene_end')],
   conduct=c('justice', NEG), dictates=True, traits=['trait.nature.mental'], x=[('lasting obedience', 'fear ends with the scene; what they do after is 11\'s and 15\'s')])

ab('ab.none_my_equal', 'None My Equal', 'deed.martial.tactics.single_combat', 1, 'dark_humility_a', 'Edge', 'passive',
   'Fight best when the glory is yours alone.',
   'Applies to your beats against a foe at or above your band while no ally is engaged with that foe.',
   [rk("+1 to beats against a foe at or above your band that you face alone.",
       [edge(1, 'the target is at or above your band and no ally is engaged with it')]),
    rk("+1 to beats against a foe at or above your band that you face alone, and your Strikes against it deal +1 harm.",
       [edge(1, 'the target is at or above your band and no ally is engaged with it'), hedge(1, 'a Strike against that foe')]),
    rk("+2 to beats against a foe at or above your band that you face alone, and your Strikes against it deal +1 harm.",
       [edge(2, 'the target is at or above your band and no ally is engaged with it'), hedge(1, 'a Strike against that foe')])],
   lim=1, conduct=c('humility', NEG), x=[('a foe an ally is also fighting', 'it gives nothing')])

ab('ab.towering_will', 'Towering Will', 'deed.influence.intimidation.display', 3, 'dark_humility_b', 'Exception', 'passive',
   'Admit no power over your own mind.',
   'Applies to yourself at all times.',
   [rk("You cannot be frightened, and you gain +1 to Endure checks made with Resolve.",
       [immune(['cond.frightened']), edge(1, 'verb = verb.endure and the attribute is resolve')]),
    rk("You cannot be frightened or charmed, and you gain +1 to Endure checks made with Resolve.",
       [immune(['cond.frightened', 'cond.charmed']), edge(1, 'verb = verb.endure and the attribute is resolve')])],
   conduct=c('humility', NEG), x=[('accepting Help', 'you still may; your keeper notes it (04)')])

ab('ab.red_mist', 'Red Mist', 'deed.martial.axe.great', 1, 'dark_restraint_a', 'Form', 'rider',
   'Give yourself to the fight and to nothing else.',
   'Applies to yourself until the conflict ends.',
   [rk("Enter the Red Mist stance until the conflict ends: your Strikes deal +1 harm and you cannot be frightened.",
       [stance('red mist', [hedge(1, 'your Strikes'), immune(['cond.frightened'])])]),
    rk("Enter the Red Mist stance until the conflict ends: your Strikes deal +2 harm and you cannot be frightened.",
       [stance('red mist', [hedge(2, 'your Strikes'), immune(['cond.frightened'])])]),
    rk("Enter the Red Mist stance until the conflict ends: your Strikes deal harm one severity rung heavier, +2, and you cannot be frightened.",
       [stance('red mist', [hedge(2, 'your Strikes'), sev(1, 'your Strikes'), immune(['cond.frightened'])])])],
   slot='slot.stance', verbs=['any'], wk=1, weak=("While in the Red Mist you take -1 to Agility defense and cannot Retreat or Yield.", ({'effect_id': 'eff.defense_status', 'params': {'amount': -1, 'applies_when': 'you hold the red mist stance'}}, 0)),
   conduct=c('restraint', NEG), x=[('ending the stance by choice', 'it ends with the conflict')])

ab('ab.blood_for_blood', 'Blood for Blood', 'deed.martial.unarmed.striking', 3, 'dark_restraint_b', 'Reaction', 'trigger',
   'Answer harm with worse.',
   'Applies when a foe\'s attack harms you.',
   [rk("When a foe harms you, your next Strike against it this round deals harm one severity rung heavier and holds a Precision lever.",
       [sev(1, 'your next Strike against the foe that harmed you, this round'), lev('precision', 'your next Strike against the foe that harmed you')], per='round'),
    rk("When a foe harms you, your next Strike against it this round deals harm one severity rung heavier, +2, and holds a Precision lever.",
       [sev(1, 'your next Strike against the foe that harmed you, this round'), hedge(2, 'that Strike'), lev('precision', 'your next Strike against the foe that harmed you')], per='round')],
   hook='on_harm_taken', when='the harm came from a foe\'s attack', conduct=c('restraint', NEG), x=[('harm from a hazard', 'there is no one to answer')])

ab('ab.defilers_touch', "Defiler's Touch", 'deed.lore.religion.profane', 1, 'dark_piety_a', 'Working', 'beat',
   'Unmake what was made holy.',
   'Applies to one sacred sign, object, effect or patch of consecrated ground you touch.',
   [rk("Defile one sacred thing you touch (roll against its stored effect DC, or Moderate): its sacred effect ends and it is recorded as desecrated.",
       [endw('one effect with trait.nature.sacred on the thing touched'), fact('the thing touched', 'desecrated', True)], f=1),
    rk("Defile one sacred thing you touch (roll against its stored effect DC, or Moderate): its sacred effect ends, it is recorded as desecrated, and the one who made it holy knows and is distracted until the end of its next turn if present.",
       [endw('one effect with trait.nature.sacred on the thing touched'), fact('the thing touched', 'desecrated', True), cond('cond.distracted', 1, 'rounds:1', 'the maker of the sacred effect, if present'), lev('precision', 'your next beat against the maker')], f=1),
    rk("Defile up to two sacred things you touch (roll against the higher stored effect DC, or Moderate): their sacred effects end, they are recorded as desecrated, the one who made them holy knows and is distracted until the end of its next turn if present, your next beat against that maker holds a Precision lever, and divine workings cast on that ground take -2 until it is cleansed.",
       [endw('up to two effects with trait.nature.sacred on the things touched'), fact('each thing touched', 'desecrated', True), cond('cond.distracted', 1, 'rounds:1', 'the maker of the sacred effect, if present'), lev('precision', 'your next beat against the maker'), tgt(1), ({'effect_id': 'eff.status_modifier', 'params': {'amount': -2, 'applies_when': 'a divine working is cast on the desecrated ground'}}, 2)], f=1)],
   attr='resolve', check=('aimed', 'verb.handle', "the effect's stored effect DC, or obstacle tier moderate"), conduct=c('piety', NEG), traits=['trait.nature.profane'],
   x=[('a keeper itself', 'canon_impossible')])

ab('ab.scorn_the_holy', 'Scorn the Holy', 'deed.lore.religion.profane', 3, 'dark_piety_b', 'Exception', 'passive',
   'Be proof against what the sacred sends.',
   'Applies to radiant harm and to effects with trait.nature.sacred that target you.',
   [rk("You halve radiant harm you take.",
       [resist(['harm.radiance'])]),
    rk("You halve radiant harm you take, and you are not counted as profane by sacred wards.",
       [resist(['harm.radiance']), waive('being treated as profane by sacred wards', 'a sacred ward tests you')])],
   conduct=c('piety', NEG), x=[('healing from sacred power', 'it still heals you, unless its maker withholds it')])

ab('ab.cull_the_weak', 'Cull the Weak', 'deed.guile.ambush.waylaying', 1, 'dark_protection_a', 'Working', 'rider',
   'Fall on whoever is already failing.',
   'Applies to a Strike against a target that is bloodied or frightened.',
   [rk("Your Strike against a bloodied or frightened target deals +1 harm and holds an Amplifying lever.",
       [hedge(1, 'this Strike'), lev('amplifying', 'this Strike')]),
    rk("Your Strike against a bloodied or frightened target deals +2 harm and holds an Amplifying lever and a Precision lever.",
       [hedge(2, 'this Strike'), lev('amplifying', 'this Strike'), lev('precision', 'this Strike')]),
    rk("Your Strike against a bloodied or frightened target deals harm one severity rung heavier, +2, and holds an Amplifying lever and a Precision lever.",
       [sev(1, 'this Strike'), hedge(2, 'this Strike'), lev('amplifying', 'this Strike'), lev('precision', 'this Strike')])],
   verbs=['verb.strike'], conduct=c('protection', NEG), traits=['trait.action.attack'], x=[('a fresh, unafraid foe', 'verb.strike')])

ab('ab.human_shield', 'Living Shield', 'deed.guile.escape.evasion', 3, 'dark_protection_b', 'Reaction', 'reaction',
   'Put another body between you and a blow.',
   'Applies to a hit on you while another being is engaged with you or grabbed by you.',
   [rk("When you are hit, turn the hit onto a being engaged with you or grabbed by you; move one band; and your next beat holds a Precision lever.",
       [({'effect_id': 'eff.intercept', 'params': {'new_target': 'a being engaged with you or grabbed by you, your choice', 'applies_when': 'you are hit'}}, 4), move('self', 1), lev('precision', 'your next beat')], f=1, per='scene_end'),
    rk("When you are hit, turn the hit onto a being engaged with you or grabbed by you; move one band; your next beat holds a Precision lever; and you gain flag.hidden against the attacker until the end of your next turn.",
       [({'effect_id': 'eff.intercept', 'params': {'new_target': 'a being engaged with you or grabbed by you, your choice', 'applies_when': 'you are hit'}}, 4), move('self', 1, add=['flag.hidden']), lev('precision', 'your next beat'), lev('protective', 'your next beat')], f=1, per='scene_end')],
   hook='on_hit_taken', when='another being is engaged with you or grabbed by you', conduct=c('protection', NEG),
   x=[('an area effect', 'verb.evade')])
