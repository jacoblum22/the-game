# deed.lore -- 18 abilities.
from dsl05 import *

Lr = 'deed.lore.'
FOE = 'the target of the Strike'

# ---------------- history ----------------
ab('ab.old_tales', 'Old Tales', Lr + 'history.legends', 1, 'legend_lore', 'Lever', 'passive',
   'Turn what the old stories say into a present use.',
   'Applies after a Recall about a ruin, a people or a relic delivers at least Standard reach.',
   [rk("When your Recall about a ruin, a people or a relic delivers Standard reach or more, you may cite what you recalled as a Precision lever on one later beat there this scene.",
       [lev('precision', 'one later beat at that place or with that people or relic', 'scene')]),
    rk("Your Recall about the past has reach one rung higher; when it delivers Standard reach or more, you may cite what you recalled as a Precision lever on one later beat there this scene.",
       [lev('precision', 'one later beat at that place or with that people or relic', 'scene'), reach('verb = verb.recall and the subject is the past')]),
    rk("Your Recall about the past has reach one rung higher and +1; when it delivers Standard reach or more, you may cite what you recalled as a Precision lever on one later beat there this scene.",
       [lev('precision', 'one later beat at that place or with that people or relic', 'scene'), reach('verb = verb.recall and the subject is the past'), edge(1, 'verb = verb.recall and the subject is the past')])],
   x=[('facts the world has never recorded', 'the Oracle; investigation (15)')])

ab('ab.heralds_eye', "Herald's Eye", Lr + 'history.heraldry', 2, 'read_rank', 'Working', 'beat',
   'Read who someone is from what they wear and bear.',
   'Applies to one person, banner, seal or device you can see.',
   [rk("Read a person or device (Observe or Recall, Intellect, against Moderate, or the bearer's effect DC if they conceal it). On a success learn their house or faction and their rank in it, and hold that as a Precision lever on Talk with them this scene.",
       [rev("the bearer's faction and rank"), lev('precision', 'Talk beats with the bearer', 'scene', verbs=['verb.talk'])]),
    rk("Read a person or device (Observe or Recall, Intellect, against Moderate, or the bearer's effect DC if they conceal it). On a success learn their house or faction, their rank in it and its standing toward you, and hold that as a Precision lever on Talk with them this scene.",
       [rev("the bearer's faction and rank"), rev("that faction's status toward the pc"), lev('precision', 'Talk beats with the bearer', 'scene', verbs=['verb.talk'])])],
   attr='intellect', check=('aimed', 'verb.observe', 'obstacle tier moderate'), x=[('a person who shows no device', 'ab.read_the_heart; investigation (15)')])

# ---------------- languages ----------------
ab('ab.gift_of_tongues', 'Gift of Tongues', Lr + 'languages.translation', 1, 'quick_tongue', 'Permission', 'beat',
   'Catch the working shape of a spoken language.',
   'Applies to one living language whose speakers you have listened to for at least an hour.',
   [rk("After an hour among its speakers, hold a language at the broken grade until the scene ends, without the improvised DC shift of gesture and guesswork.",
       [glic('lic.lang.<the language>', 'broken', 'scene'), waive('the crude-fallback DC shift for speaking a language not held', 'you speak that language')], per='scene_end'),
    rk("After an hour among its speakers, hold a language at the accented grade until your next long rest, and read its plain script.",
       [glic('lic.lang.<the language>', 'accented', 'until_rest:rest_long'), waive('the crude-fallback DC shift for speaking a language not held', 'you speak that language'), perm(2)], per='scene_end'),
    rk("After an interval among its speakers, hold a language at the accented grade until your next long rest, read its plain script, and pass for a foreigner who learned it well.",
       [glic('lic.lang.<the language>', 'accented', 'until_rest:rest_long', big=True), waive('the crude-fallback DC shift for speaking a language not held', 'you speak that language'), perm(2)], per='scene_end')],
   attr='intellect', x=[('a dead language or a cipher', 'ab.cipher_breaker; a project (15)'), ('holding the language permanently', 'its acquisition paths (a project clock)')])

ab('ab.cipher_breaker', 'Cipher-Breaker', Lr + 'languages.ciphers', 3, 'decipher', 'Edge', 'passive',
   'Find the pattern under a hidden text.',
   'Applies to beats that decipher, translate or decode a written text.',
   [rk("+1 to beats that decipher or decode a text, and their reach is one rung higher.",
       [edge(1, 'the beat deciphers, decodes or translates a written text'), reach('the beat deciphers, decodes or translates a written text')]),
    rk("+2 to beats that decipher or decode a text, and their reach is one rung higher.",
       [edge(2, 'the beat deciphers, decodes or translates a written text'), reach('the beat deciphers, decodes or translates a written text')])],
   x=[('a text protected by a ward', '05.7.7')])

# ---------------- bestiary ----------------
ab('ab.know_the_beast', 'Know the Beast', Lr + 'bestiary.monsters', 1, 'creature_lore', 'Working', 'beat',
   'Name what a creature is and what it cannot bear.',
   'Applies to one creature you can perceive or whose remains or traces you examine.',
   [rk("Recall what you know of a creature (Recall, Intellect, against the tier of its threat band). On a success learn one of its tells in full (a resistance, a vulnerability or a habit) and hold it as a Precision lever against that kind this scene.",
       [rev("one tell of the creature's stat block"), lev('precision', 'your beats against creatures of that kind', 'scene')]),
    rk("Recall what you know of a creature (Recall, Intellect, against the tier of its threat band). On a success learn two of its tells in full and hold them as a Precision lever against that kind this scene.",
       [rev("one tell of the creature's stat block"), rev("a second tell of the creature's stat block"), lev('precision', 'your beats against creatures of that kind', 'scene')]),
    rk("Recall what you know of a creature (Recall, Intellect, against the tier of its threat band). On a success learn two of its tells in full and hold them as a Precision lever and an Amplifying lever against that kind this scene.",
       [rev("one tell of the creature's stat block"), rev("a second tell of the creature's stat block"), lev('precision', 'your beats against creatures of that kind', 'scene'), lev('amplifying', 'your beats against creatures of that kind', 'scene')])],
   attr='intellect', check=('aimed', 'verb.recall', "the tier of the creature's threat band"),
   x=[('its numbers', 'sealed (09)'), ('a unique being no lore describes', 'the Oracle; investigation (15)')])

ab('ab.weak_point', 'Weak Point', Lr + 'bestiary.beasts', 2, 'anatomy', 'Working', 'rider',
   'Strike a creature where its kind is soft.',
   'Applies to a Strike against a creature that is not folk and of which you have learned at least one tell.',
   [rk("Your Strike against a creature whose tell you know deals harm one severity rung heavier, +1, and weakens it until the end of its next turn.",
       [sev(1, 'this Strike'), hedge(1, 'this Strike'), cond('cond.weakened', 1, 'rounds:1', FOE)], f=1),
    rk("Your Strike against a creature whose tell you know deals harm one severity rung heavier, +2, and weakens it until the scene ends.",
       [sev(1, 'this Strike'), hedge(2, 'this Strike'), cond('cond.weakened', 1, 'scene', FOE)], f=1)],
   verbs=['verb.strike'], lim=1, traits=['trait.action.attack'], x=[('folk', 'ab.read_the_field')])

# ---------------- medicine ----------------
ab('ab.field_surgeon', 'Field Surgeon', Lr + 'medicine.surgery', 1, 'treatment', 'Working', 'beat',
   'Close what a weapon opened.',
   'Applies to one living being you can tend for an interval with a healer\'s kit; each being once between its short rests.',
   [rk("Tend one being for an interval with a kit: it regains 3 Vitality and its bleeding ends.",
       [heal(3, 'the tended being'), cleanse('cond.bleeding', 'the tended being')]),
    rk("Tend one being for an interval with a kit: it regains 5 Vitality and its bleeding ends.",
       [heal(5, 'the tended being'), cleanse('cond.bleeding', 'the tended being')]),
    rk("Tend one being for an interval with a kit: it regains 5 Vitality, and its bleeding and its poisoning end.",
       [heal(5, 'the tended being'), cleanse('cond.bleeding', 'the tended being'), cleanse('cond.poisoned', 'the tended being')])],
   attr='intellect', x=[('wounds and marks', 'ch.07 treatment under lic.training.lore_medicine'), ('a being already healed twice since its long rest', 'the healing cap (05.7.8)')])

ab('ab.masters_remedy', "Master's Remedy", Lr + 'medicine.remedies', 4, 'cure', 'Working', 'beat',
   'Drive a sickness or a poison out of a body.',
   'Applies to one living being you can tend for an hour with a healer\'s kit and remedies.',
   [rk("Tend one being for an hour: it regains 8 Vitality, its poisoning ends, one affliction it carries drops one stage, and its checks against that affliction are framed one stakes rung lower this scene.",
       [heal(8, 'the tended being'), cleanse('cond.poisoned', 'the tended being'), cleanse('one affliction stage (07)', 'the tended being'), lev('protective', "the tended being's checks against that affliction", 'scene')], f=2)],
   attr='intellect', oc=1, cost_text='an hour and one use of remedies (08)',
   x=[('a curse', 'ab.lift_the_hex; rit.lift_curse'), ('a being already healed twice since its long rest', 'the healing cap (05.7.8)')])

# ---------------- engineering ----------------
ab('ab.find_the_flaw', 'Find the Flaw', Lr + 'engineering.structures', 1, 'flaw_finding', 'Working', 'beat',
   'See where a made thing will give.',
   'Applies to one structure, mechanism or made object you can examine.',
   [rk("Examine a made thing (Observe, Intellect, against its tier). On a success learn its weak point and hold it as an Amplifying lever on Force, Handle and Strike beats against that thing this scene.",
       [rev('the weak point of the examined structure or mechanism'), lev('amplifying', 'Force, Handle and Strike beats against that thing', 'scene')]),
    rk("Examine a made thing (Observe, Intellect, against its tier). On a success learn its weak point and hold it as an Amplifying lever and a Precision lever on Force, Handle and Strike beats against that thing this scene.",
       [rev('the weak point of the examined structure or mechanism'), lev('amplifying', 'Force, Handle and Strike beats against that thing', 'scene'), lev('precision', 'Force, Handle and Strike beats against that thing', 'scene')]),
    rk("Examine a made thing (Observe, Intellect, against its tier). On a success learn its weak point, hold it as an Amplifying lever and a Precision lever on Force, Handle and Strike beats against that thing this scene, and harm to it or to a construct built like it is one severity rung heavier.",
       [rev('the weak point of the examined structure or mechanism'), lev('amplifying', 'Force, Handle and Strike beats against that thing', 'scene'), lev('precision', 'Force, Handle and Strike beats against that thing', 'scene'), sev(1, 'harm to the examined thing or a construct of its make')])],
   attr='intellect', check=('aimed', 'verb.observe', "the thing's tier"), x=[('a living creature', 'ab.know_the_beast')])

ab('ab.clockwork_sense', 'Clockwork Sense', Lr + 'engineering.mechanisms', 3, 'mechanism', 'Permission', 'beat',
   'Work a mechanism you have never seen.',
   'Applies to one mechanism, lock-work, trap or engine you can reach.',
   [rk("Operate, jam or reset an unfamiliar mechanism (Handle, Intellect, against its tier) with +1; beats on traps and mechanisms are framed one stakes rung lower.",
       [perm(2), edge(1, 'the beat works a mechanism, trap or engine'), stakes('the beat works a mechanism, trap or engine')]),
    rk("Operate, jam, reset or turn against its makers an unfamiliar mechanism (Handle, Intellect, against its tier) with +1; beats on traps and mechanisms are framed one stakes rung lower.",
       [perm(4), edge(1, 'the beat works a mechanism, trap or engine'), stakes('the beat works a mechanism, trap or engine')])],
   attr='intellect', check=('aimed', 'verb.handle', "the mechanism's tier"), x=[('a magical ward on the mechanism', '05.7.7'), ('building a mechanism', 'lic.training.craft_artifice')])

# ---------------- law ----------------
ab('ab.letter_of_the_law', 'Letter of the Law', Lr + 'law.contracts', 1, 'cite_law', 'Lever', 'passive',
   'Set a rule the listener is bound by against them.',
   'Applies to Talk beats with an official, a guild or a party to a contract, citing an established law, charter, custom or term.',
   [rk("When you Talk with someone bound by a law, charter, custom or contract term that is an established fact, you may cite it as a Precision lever.",
       [lev('precision', 'Talk beats citing an established law, charter, custom or term', 'scene', verbs=['verb.talk'])]),
    rk("When you Talk with someone bound by a law, charter, custom or contract term that is an established fact, you may cite it as a Precision lever, and the beat is framed one stakes rung lower.",
       [lev('precision', 'Talk beats citing an established law, charter, custom or term', 'scene', verbs=['verb.talk']), stakes('Talk beats citing an established law, charter, custom or term')]),
    rk("When you Talk with someone bound by a law, charter, custom or contract term that is an established fact, you may cite it as a Precision lever and an Amplifying lever, and the beat is framed one stakes rung lower.",
       [lev('precision', 'Talk beats citing an established law, charter, custom or term', 'scene', verbs=['verb.talk']), lev('amplifying', 'Talk beats citing an established law, charter, custom or term', 'scene', verbs=['verb.talk']), stakes('Talk beats citing an established law, charter, custom or term')])],
   x=[('a law the player asserts but no fact holds', 'verb.recall, or the Oracle')])

ab('ab.unanswerable_case', 'The Unanswerable Case', Lr + 'law.courts', 5, 'advocacy', 'Working', 'beat',
   'Close every door an opposing argument could leave by.',
   'Applies in a formal hearing, council, trial or negotiation with a recognized arbiter or rules of procedure.',
   [rk("Make your case (Talk, Intellect, against the opposing party's Intellect defense). The beat holds a Precision lever, its reach is one rung higher and its stakes one rung lower; on a success the opposing party's present line of argument is closed to them, you learn their weakest claim, the proceeding's clock ticks by your delivered reach, and the judgment is recorded as binding on those present.",
       [lev('precision', 'this beat', 'scene'), reach('this beat'), stakes('this beat'), restr({'methods': ['the opposing party\'s present line of argument']}, 'the opposing party', 'scene'), rev("the opposing party's weakest claim"), tick("the proceeding's clock", 'delivered_reach'), fact('the judgment', 'binding_on', 'those present')], f=3, per='scene_end')],
   attr='intellect', check=('aimed', 'verb.talk', "the opposing party's Intellect defense"), traits=['trait.action.speech'],
   x=[('a party that recognizes no arbiter', 'verb.talk; ab.leverage')])

# ---------------- arcana ----------------
ab('ab.spell_sight', 'Spell-Sight', Lr + 'arcana.identification', 1, 'identify_magic', 'Working', 'beat',
   'Read the shape of a working of magic.',
   'Applies to one magical effect, item or residue within band.close that you can examine.',
   [rk("Examine magic of any branch (Observe, Intellect, against its stored effect DC or Moderate). On a success learn its branch and school and what it does.",
       [perm(2), rev('the branch, school and function of the examined effect')]),
    rk("Examine magic of any branch (Observe, Intellect, against its stored effect DC or Moderate). On a success learn its branch and school, what it does, and one sealed property of an item that bears it.",
       [perm(2), rev('the branch, school and function of the examined effect'), rev('one sealed property of the examined item')]),
    rk("Examine magic of any branch (Observe, Intellect, against its stored effect DC or Moderate). On a success learn its branch and school, what it does, one sealed property of an item that bears it, and hold what you learned as a Precision lever on beats that dispel or counter it this scene.",
       [perm(2), rev('the branch, school and function of the examined effect'), rev('one sealed property of the examined item'), lev('precision', 'beats that dispel or counter the examined effect', 'scene')])],
   attr='intellect', check=('aimed', 'verb.observe', "the effect's stored effect DC, or obstacle tier moderate"),
   x=[('ending the effect', '05.7.7 dispel'), ('sensing magic at a distance', 'deed.arcane.divination')])

ab('ab.theory_of_the_weave', 'Theory of the Weave', Lr + 'arcana.theory', 2, 'magic_theory', 'Edge', 'passive',
   'Reason from the principles under every working.',
   'Applies to research beats on magic, to rite design, and to learning a spell or rite from a text.',
   [rk("Beats that research magic or design a rite have reach one rung higher, and each week you study a spell or rite from a text ticks its learning clock one segment more.",
       [reach('the beat researches magic or designs a rite'), tick('a learning clock ticked by study from a text', 1)]),
    rk("Beats that research magic or design a rite have reach one rung higher, each week you study a spell or rite from a text ticks its learning clock one segment more, and you gain +1 to the steps of a rite you lead.",
       [reach('the beat researches magic or designs a rite'), tick('a learning clock ticked by study from a text', 1), edge(1, 'the beat is a step of a rite you lead')])],
   x=[('casting a spell you do not hold', 'emulate (05.5.4)')])

# ---------------- religion ----------------
ab('ab.name_the_power', 'Name the Power', Lr + 'religion.pantheon', 1, 'sacred_lore', 'Working', 'beat',
   'Know a sacred or profane thing for what it is.',
   'Applies to one sign, rite, relic, undead, fiend or spirit you can perceive.',
   [rk("Recall the lore of a sacred or profane thing (Recall, Intellect, against its tier). On a success learn which power or kind it belongs to and hold that as a Precision lever on beats against or with it this scene.",
       [rev('which power or kind the thing belongs to'), lev('precision', 'beats against or with the named thing', 'scene')]),
    rk("Recall the lore of a sacred or profane thing (Recall, Intellect, against its tier). On a success learn which power or kind it belongs to and which conduct that power cares for, and hold that as a Precision lever on beats against or with it this scene.",
       [rev('which power or kind the thing belongs to'), rev("the conduct axes that power cares for"), lev('precision', 'beats against or with the named thing', 'scene')]),
    rk("Recall the lore of a sacred or profane thing (Recall, Intellect, against its tier). On a success learn which power or kind it belongs to and which conduct that power cares for, hold that as a Precision lever on beats against or with it this scene, and your checks to resist its fear or possession are framed one stakes rung lower.",
       [rev('which power or kind the thing belongs to'), rev("the conduct axes that power cares for"), lev('precision', 'beats against or with the named thing', 'scene'), lev('protective', 'your resisted checks against its fear or possession', 'scene')])],
   attr='intellect', check=('aimed', 'verb.recall', "the thing's tier"), x=[('its numbers', 'sealed (09)'), ('driving it out', 'ab.turn_undead; ab.cast_out')])

ab('ab.know_the_unclean', 'Know the Unclean', Lr + 'religion.profane', 4, 'profane_lore', 'Edge', 'passive',
   'Meet the works of undead and fiends forewarned.',
   'Applies against creatures tagged creature.undead or creature.fiend and their effects.',
   [rk("+1 to checks that resist the effects of undead and fiends, +1 harm on your Strikes against them, and you may cite a kind you have named as an Amplifying lever against it.",
       [edge(1, 'the check resists an effect whose source is creature.undead or creature.fiend'), hedge(1, 'a Strike against creature.undead or creature.fiend'), lev('amplifying', 'beats against an undead or fiend whose kind you have named', 'scene')])],
   x=[('spirits and fey', 'ab.spirit_tongue; lic.training.primal_spirits')])

# ---------------- investigation ----------------
ab('ab.keen_search', 'Keen Search', Lr + 'investigation.search', 1, 'searching', 'Edge', 'passive',
   'Go over a place so that nothing in it is missed.',
   'Applies to search beats on which you spend at least one interval.',
   [rk("Search beats on which you spend an interval have reach one rung higher.",
       [reach('deed_tag under deed.lore.investigation.search and the beat takes at least one interval')]),
    rk("Search beats on which you spend an interval have reach one rung higher, and you gain +1 to them.",
       [reach('deed_tag under deed.lore.investigation.search and the beat takes at least one interval'), edge(1, 'deed_tag under deed.lore.investigation.search and the beat takes at least one interval')]),
    rk("Search beats on which you spend an interval have reach one rung higher, you gain +1 to them, and a failed search still delivers its top-ranked item at Limited reach.",
       [reach('deed_tag under deed.lore.investigation.search and the beat takes at least one interval'), edge(1, 'deed_tag under deed.lore.investigation.search and the beat takes at least one interval'), waive('the zero delivery of a failed search (the top-ranked item is delivered at Limited reach)', 'you spent an interval')])],
   x=[('finding what is not there', 'the Oracle; sealed clue nodes (15)')])

ab('ab.reconstruct', 'Reconstruct the Scene', Lr + 'investigation.deduction', 5, 'deduction', 'Working', 'beat',
   'Rebuild what happened in a place from what it left.',
   'Applies at a place where an event happened within the past week, which you can examine for an interval.',
   [rk("Examine the place for an interval (Observe, Intellect, against the scene's tier). The beat's reach is one rung higher; on a success you learn the order of what happened, how many were present and of what kinds, and one thing that was taken or left; the investigation's clock ticks by your delivered reach; you hold what you learned as a Precision lever on beats of this inquiry this scene; and you may put one yes-or-no question about the event, answered from sealed state.",
       [reach('this beat'), rev('the order of events at the place'), rev('the number and kinds of those present'), rev('one thing taken or left'), tick("the investigation's clue clock", 'delivered_reach'), lev('precision', 'beats of this inquiry', 'scene'), perm(2)], f=3, per='scene_end')],
   attr='intellect', check=('aimed', 'verb.observe', "the scene's tier (15)"),
   x=[('who did it, by name', 'the clue graph (15): this delivers nodes, never the sealed solution'), ('an event older than a week', 'rit.speak_with_the_land; rit.raise_shade')],
   nmi=['the sealed solution of a mystery'])
