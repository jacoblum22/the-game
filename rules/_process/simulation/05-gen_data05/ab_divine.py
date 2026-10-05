# deed.divine -- 17 spells. Casting attribute Presence; every working needs the invocation, the sign and the keeper's regard (05.7.2, 05.7.4).
from dsl05 import *

D = 'deed.divine.'
T = 'the target'
ATK = ('aimed', 'verb.strike', "the target's attack defense")
RES = ('resisted', 'endure', 'resolve')

# ---------------- healing ----------------
ab('ab.mend_flesh', 'Mend Flesh', D + 'healing.mending', 1, 'heal_touch', 'Working', 'beat',
   'Close a wound in living flesh.',
   'Applies to one living being you touch.',
   [rk("One living being you touch regains 3 Vitality and its bleeding ends.",
       [heal(3, T), cleanse('cond.bleeding', T)], f=1),
    rk("One living being you touch regains 5 Vitality, and its bleeding and its weakness end.",
       [heal(5, T), cleanse('cond.bleeding', T), cleanse('cond.weakened', T)], f=1),
    rk("One living being within band.close regains 8 Vitality, and its bleeding and its weakness end.",
       [heal(8, T), cleanse('cond.bleeding', T), cleanse('cond.weakened', T)], f=1)],
   traits=['trait.delivery.touch'], x=[('wounds, marks and afflictions', 'ch.07; rit.vigil_of_healing; ab.purge'), ('undead, constructs, objects', 'G4: not living flesh'), ('a being already healed twice since its long rest', 'the healing cap (05.7.8)')],
   nmi=['a wound closed (wounds are 07\'s)', 'the dead returned'])

ab('ab.purge', 'Purge', D + 'healing.purging', 2, 'cleansing', 'Working', 'beat',
   'Drive a foulness out of a living body.',
   'Applies to one living being you touch.',
   [rk("One living being you touch is freed of poisoning and of one other bodily or mental condition, and its checks against what afflicted it are framed one stakes rung lower this scene.",
       [cleanse('cond.poisoned', T), cleanse('one condition of category physical or mental', T), lev('protective', "the target's checks against that affliction", 'scene')], f=1),
    rk("One living being you touch is freed of poisoning and of one other bodily or mental condition, regains 3 Vitality, and its checks against what afflicted it are framed one stakes rung lower this scene.",
       [cleanse('cond.poisoned', T), cleanse('one condition of category physical or mental', T), lev('protective', "the target's checks against that affliction", 'scene'), heal(3, T)], f=1)],
   traits=['trait.delivery.touch'], x=[('a curse or a possession', 'ab.lift_the_hex; ab.cast_out'), ('a staged affliction past its first stage', 'ab.masters_remedy; rit.purification')])

ab('ab.breath_of_life', 'Breath of Life', D + 'healing.sustaining', 5, 'recall_the_dying', 'Working', 'beat',
   'Hold a departing life in its body.',
   'Applies to one being you touch that is Dying.',
   [rk("One Dying being you touch is stabilized at once, regains 8 Vitality, is freed of bleeding and poisoning, and its beats and resisted checks are framed one stakes rung lower until the scene ends.",
       [perm(4), heal(8, T), cleanse('cond.bleeding', T), cleanse('cond.poisoned', T), lev('protective', "the target's beats and resisted checks", 'scene')], f=3, per='rest_long')],
   traits=['trait.delivery.touch'], x=[('a being that is dead', 'canon decides whether anything can (05.7.10); no pool ability does'), ('wounds taken while Staggered', 'they remain (07)')],
   nmi=['that wounds or marks are gone'])

# ---------------- sacred warding ----------------
ab('ab.sanctuary', 'Sanctuary', D + 'warding.sanctuary', 1, 'protect_other', 'Working', 'beat',
   'Set one being under your keeper\'s protection.',
   'Applies to one being within band.close; ends for that being when it attacks.',
   [rk("For the scene one being within band.close is under protection: a foe that would attack it must first roll Endure (Resolve) against your effect DC or choose another act, and the warded being's resisted checks are framed one stakes rung lower.",
       [restr({'methods': ['attacking the warded being without first succeeding at Endure against your effect DC']}, 'each foe', 'scene'), fchk('endure'), lev('protective', "the warded being's resisted checks", 'scene')], f=1),
    rk("For the scene up to two beings within band.close are under protection: a foe that would attack one must first roll Endure (Resolve) against your effect DC or choose another act; each warded being has +1 to Agility defense and its resisted checks are framed one stakes rung lower.",
       [restr({'methods': ['attacking a warded being without first succeeding at Endure against your effect DC']}, 'each foe', 'scene'), fchk('endure'), lev('protective', "the warded beings' resisted checks", 'scene'), tgt(1), dedge(1, 'agility', 'a warded being is attacked')], f=1),
    rk("For the scene up to three beings within band.close are under protection: a foe that would attack one must first roll Endure (Resolve) against your effect DC or choose another act; each warded being has +1 to Agility defense and its resisted checks are framed one stakes rung lower.",
       [restr({'methods': ['attacking a warded being without first succeeding at Endure against your effect DC']}, 'each foe', 'scene'), fchk('endure'), lev('protective', "the warded beings' resisted checks", 'scene'), tgt(2), dedge(1, 'agility', 'a warded being is attacked')], f=1)],
   check=RES, traits=['trait.duration.lasting'], dictates=True, x=[('area effects and hazards', 'they take the warded being as they would anyone'), ('a warded being that attacks', 'the protection ends for it')])

ab('ab.blessing', 'Blessing', D + 'warding.blessing', 2, 'bless', 'Working', 'beat',
   'Lay your keeper\'s favor on another\'s undertaking.',
   'Applies to one willing being within band.close, for one undertaking you name aloud.',
   [rk("For the scene one willing being holds, on beats that serve the undertaking you named, a Precision lever and a Protective lever, and it cannot be frightened.",
       [lev('precision', "the blessed being's beats that serve the named undertaking", 'scene'), lev('protective', "the blessed being's beats that serve the named undertaking", 'scene'), immune(['cond.frightened'])], f=1),
    rk("For the scene up to three willing beings hold, on beats that serve the undertaking you named, a Precision lever and a Protective lever, and they cannot be frightened.",
       [lev('precision', "the blessed beings' beats that serve the named undertaking", 'scene'), lev('protective', "the blessed beings' beats that serve the named undertaking", 'scene'), immune(['cond.frightened']), tgt(2)], f=1)],
   traits=['trait.duration.lasting'], x=[('an undertaking against the keeper\'s axes', 'the blessing does not take (05.7.4)'), ('blessing yourself', 'ab.sworn_purpose')])

# ---------------- smiting ----------------
ab('ab.smite', 'Smite', D + 'smiting.weapon', 1, 'holy_strike', 'Form', 'rider',
   'Carry sacred power into a weapon\'s blow.',
   'Applies to one Strike with a weapon you hold.',
   [rk("This Strike deals radiant harm in place of its own type; against an undead or a fiend it is one severity rung heavier.",
       [sdel(['harm.radiance.holy'], 0, 'uses:1'), sev(1, 'the target is creature.undead or creature.fiend')], f=1),
    rk("This Strike deals radiant harm in place of its own type, +1, and is one severity rung heavier.",
       [sdel(['harm.radiance.holy'], 1, 'uses:1'), sev(1, 'this Strike')], f=1),
    rk("This Strike deals radiant harm in place of its own type, +1, and is one severity rung heavier; an undead or a fiend it harms is blinded until the end of its next turn.",
       [sdel(['harm.radiance.holy'], 1, 'uses:1'), sev(1, 'this Strike'), cond('cond.blinded', 1, 'rounds:1', 'an undead or fiend the Strike harms')], f=1)],
   slot='slot.strike_delivery', verbs=['verb.strike'], harm_tags=['harm.radiance.holy'], traits=['trait.action.attack', 'trait.sense.visible'], ckey=True,
   x=[('a Strike already made', 'declare it with the beat')])

ab('ab.searing_light', 'Searing Light', D + 'smiting.radiance', 3, 'radiant_bolt', 'Working', 'beat',
   'Cast a beam of sacred light at one foe.',
   'Applies to one target you can see within band.far.',
   [rk("Cast light at one target within band.far. On a success it takes Heavy radiant harm (shifted by delivered reach; one rung heavier against undead and fiends), is blinded until the end of its next turn, and is exposed until the scene ends.",
       [harm(3, ['harm.radiance.light'], T), sev(1, 'the target is creature.undead or creature.fiend'), cond('cond.blinded', 1, 'rounds:1', T), cond('cond.exposed', 1, 'scene', T)], f=2),
    rk("Cast light at one target within band.far. On a success it takes Grievous radiant harm (shifted by delivered reach; one rung heavier against undead and fiends), is blinded until the end of its next turn, and is exposed until the scene ends.",
       [harm(4, ['harm.radiance.light'], T), sev(1, 'the target is creature.undead or creature.fiend'), cond('cond.blinded', 1, 'rounds:1', T), cond('cond.exposed', 1, 'scene', T)], f=2)],
   check=ATK, harm_tags=['harm.radiance.light'], traits=['trait.action.attack', 'trait.delivery.ranged', 'trait.sense.visible'],
   x=[('lighting a dark place', 'a small working (05.7.6)')])

# ---------------- rites ----------------
ab('ab.last_rites', 'Last Rites', D + 'rites.funerary', 1, 'lay_to_rest', 'Permission', 'beat',
   'Give the dead their rest.',
   'Applies to one dead body you can tend for an interval.',
   [rk("Tend a body for an interval: it is laid to rest, and from then it cannot be raised as undead or called back to answer questions.",
       [perm(2), fact('the body', 'laid_to_rest', True)]),
    rk("Tend a body for an interval: it is laid to rest, it cannot be raised as undead or called back to answer questions, and you learn the manner of its death.",
       [perm(2), fact('the body', 'laid_to_rest', True), rev('the manner of the death')]),
    rk("Tend a body for an interval: it is laid to rest, it cannot be raised as undead or called back to answer questions, you learn the manner of its death, and you hold a Precision lever on Talk with the dead one's kin and people this scene.",
       [perm(2), fact('the body', 'laid_to_rest', True), rev('the manner of the death'), lev('precision', "Talk beats with the dead one's kin and people", 'scene', verbs=['verb.talk'])])],
   x=[('an undead that is already risen', 'ab.turn_undead; ab.cast_out'), ('who killed them', 'investigation (15)')])

ab('ab.cleansing_rite', 'Cleansing Rite', D + 'rites.purification', 4, 'purify', 'Working', 'beat',
   'Wash a profane hold from a place or a person.',
   'Applies to one being or one room-sized place you can tend for an interval.',
   [rk("Tend a being or a room-sized place for an interval: one profane or magical effect on it ends, up to two magical conditions on it end, the place is recorded as consecrated until the next dawn, and those in it hold a Protective lever against undead and fiends this scene.",
       [endw('one profane or magical effect on the being or place'), cleanse('one condition of category magical', 'the being or each being in the place'), cleanse('a second condition of category magical', 'the being or each being in the place'), fact('the place', 'consecrated', 'until the next day boundary'), lev('protective', 'beats and resisted checks against undead and fiends by those in the place', 'scene')], f=2)],
   oc=1, cost_text='an interval of rite, with water, salt or ash', check=('aimed', 'verb.handle', "the effect's stored effect DC, or obstacle tier hard"),
   x=[('a lasting consecration', 'rit.consecrate_ground'), ('a staged affliction', 'ab.masters_remedy; rit.purification')])

# ---------------- oaths ----------------
ab('ab.sworn_purpose', 'Sworn Purpose', D + 'oaths.swearing', 1, 'swear_deed', 'Working', 'beat',
   'Bind yourself aloud to one deed.',
   'Applies to one deed you name aloud, to be done before the next dawn; one sworn purpose at a time.',
   [rk("Swear a deed to be done before the next dawn (it is recorded as a commitment). Until it is done or the dawn comes, on beats that directly advance it you hold a Precision lever and an Amplifying lever, and you cannot be frightened.",
       [fact('the pc', 'sworn_purpose', 'the named deed, until the next day boundary'), lev('precision', 'beats that directly advance the sworn deed', 'scene'), lev('amplifying', 'beats that directly advance the sworn deed', 'scene'), immune(['cond.frightened'])], f=0, per='rest_long'),
    rk("Swear a deed to be done before the next dawn (it is recorded as a commitment). Until it is done or the dawn comes, on beats that directly advance it you hold a Precision lever and an Amplifying lever and are framed one stakes rung lower, and you cannot be frightened.",
       [fact('the pc', 'sworn_purpose', 'the named deed, until the next day boundary'), lev('precision', 'beats that directly advance the sworn deed', 'scene'), lev('amplifying', 'beats that directly advance the sworn deed', 'scene'), immune(['cond.frightened']), stakes('beats that directly advance the sworn deed')], f=0, per='rest_long'),
    rk("Swear a deed to be done before the next dawn (it is recorded as a commitment). Until it is done or the dawn comes, on beats that directly advance it you hold a Precision lever and an Amplifying lever and are framed one stakes rung lower, you cannot be frightened, and when the deed is done you regain 1 Focus.",
       [fact('the pc', 'sworn_purpose', 'the named deed, until the next day boundary'), lev('precision', 'beats that directly advance the sworn deed', 'scene'), lev('amplifying', 'beats that directly advance the sworn deed', 'scene'), immune(['cond.frightened']), stakes('beats that directly advance the sworn deed'), foc(1)], f=0, per='rest_long')],
   wk=1, weak=("If the dawn comes with the deed undone by your own choice, you are weakened until your next long rest.", cond('cond.weakened', 1, 'until_rest:rest_long', 'self')),
   traits=['trait.sense.audible'], x=[('a deed sworn silently', 'it must be spoken'), ('binding another to the deed', 'ab.binding_vow')])

ab('ab.binding_vow', 'Binding Vow', D + 'oaths.binding', 4, 'witness_oath', 'Working', 'beat',
   'Give another\'s freely sworn word a hold on them.',
   'Applies to one being that swears an oath freely, in your hearing, with your hand on it or your sign between you.',
   [rk("Witness an oath freely sworn. It is recorded as a commitment on the swearer; you learn at once whether they mean it as they swear; you may cite it as a Precision lever on Talk with them; and if they break it by choice they are weakened and exposed until they make it good or a season passes.",
       [fact('the swearer', 'bound_oath', 'the words sworn'), rev('whether the swearer means the oath as it is sworn'), lev('precision', 'Talk beats with the swearer that cite the oath', 'scene', verbs=['verb.talk']), perm(4), restr({'methods': ['breaking the oath without the stated consequence']}, 'the swearer', 'permanent')], f=2)],
   traits=['trait.delivery.touch', 'trait.duration.lasting'], x=[('an oath sworn under threat or charm', 'the vow does not bind: it must be free'), ('forcing the swearer to act', 'the vow punishes the breach; it does not compel')])

# ---------------- revelation ----------------
ab('ab.discern', 'Discern', D + 'revelation.discernment', 1, 'truth_sense', 'Working', 'beat',
   'Ask your keeper whether a speaker believes their words.',
   'Applies to one statement just made in your hearing by a being with a mind.',
   [rk("Of one statement just made in your hearing, learn whether its speaker believes it, and hold that as a Precision lever on your next Talk with them.",
       [perm(2), rev('whether the speaker believes the statement'), lev('precision', 'your next Talk beat with the speaker')], f=1, per='scene_end'),
    rk("Of up to two statements just made in your hearing, learn whether each speaker believes it, and hold that as a Precision lever on your next Talk with them.",
       [perm(2), rev('whether the speaker believes the first statement'), rev('whether the speaker believes the second statement'), lev('precision', 'your next Talk beat with the speaker')], f=1, per='scene_end'),
    rk("Of up to two statements just made in your hearing, learn whether each speaker believes it and what feeling lay under it, and hold that as a Precision lever on Talk with them this scene.",
       [perm(2), rev('whether the speaker believes the first statement'), rev('whether the speaker believes the second statement'), rev('the feeling under the statements'), lev('precision', 'Talk beats with the speaker', 'scene', verbs=['verb.talk'])], f=1, per='scene_end')],
   traits=['trait.nature.mental'], x=[('whether the statement is true in the world', 'sealed; the speaker may be honestly wrong'), ('thoughts not spoken', 'no pool ability reads a mind')],
   nmi=['the truth of the matter', 'unspoken thoughts'])

ab('ab.prophetic_dream', 'Prophetic Dream', D + 'revelation.visions', 3, 'dream', 'Reaction', 'trigger',
   'Receive in sleep a sign of what is moving.',
   'Applies on completing a long rest of full quality, to one hidden or sensed clock that bears on a commitment, vow or thread of yours.',
   [rk("When you complete a long rest, receive one omen of a hidden or sensed clock that bears on your commitments, and learn its stage (stirring, building or imminent). Your first beat the next day that acts on it holds a Precision lever.",
       [rev('one omen of a hidden or sensed clock that bears on your commitments'), rev("that clock's stage"), lev('precision', 'your first beat the next day that acts on the omen')], per='rest_long'),
    rk("When you complete a long rest, receive one omen of a hidden or sensed clock that bears on your commitments, and learn its stage and the place it concerns. Beats the next day that act on it hold a Precision lever.",
       [rev('one omen of a hidden or sensed clock that bears on your commitments'), rev("that clock's stage"), rev('the place the clock concerns'), lev('precision', 'beats the next day that act on the omen', 'scene')], per='rest_long')],
   hook='on_boundary', when='boundary = rest_long with quality full', x=[('the clock\'s exact fill or its owner\'s plan', 'sealed; investigation (15)'), ('choosing what the dream is about', 'the engine picks the clock nearest completion')],
   nmi=["the clock's number", 'a clear prophecy: the dream is an omen'])

# ---------------- exorcism ----------------
ab('ab.turn_undead', 'Turn the Dead', D + 'exorcism.turning', 1, 'turning', 'Working', 'beat',
   'Drive the unquiet dead back by your keeper\'s name.',
   'Applies to up to three undead within band.near that can see or hear you.',
   [rk("Up to three undead within band.near roll Endure (Resolve) against your effect DC: on a failure each is frightened of you until the scene ends.",
       [fchk('endure'), cond('cond.frightened', 1, 'scene', 'each undead that fails'), tgt(2)], f=1),
    rk("Up to four undead within band.near roll Endure (Resolve) against your effect DC: on a failure each is frightened of you until the scene ends and takes Light radiant harm.",
       [fchk('endure'), cond('cond.frightened', 1, 'scene', 'each undead that fails'), tgt(3), harm(1, ['harm.radiance.holy'], 'each undead that fails')], f=1),
    rk("Up to five undead within band.near roll Endure (Resolve) against your effect DC: on a failure each is frightened of you until the scene ends and takes Moderate radiant harm.",
       [fchk('endure'), cond('cond.frightened', 1, 'scene', 'each undead that fails'), tgt(4), harm(2, ['harm.radiance.holy'], 'each undead that fails')], f=1)],
   check=RES, spread='burst', harm_tags=['harm.radiance.holy'], traits=['trait.sense.audible', 'trait.sense.visible'], dictates=True,
   x=[('fiends and spirits', 'ab.cast_out; ab.banish'), ('the living', 'G4 for this working')])

ab('ab.cast_out', 'Cast Out', D + 'exorcism.dispossession', 3, 'exorcise', 'Working', 'beat',
   'Break an unclean hold on a body or a place.',
   'Applies to one possession, or one effect made by an undead or a fiend, on a being or place within band.close.',
   [rk("Cast out one possession or one effect of an undead or a fiend (roll against its stored effect DC, or the possessor's Resolve defense). On a success it ends; the possessor takes Moderate radiant harm and cannot return to that host for a day; and the freed being's charm or fear ends.",
       [endw('one possession, or one effect made by an undead or a fiend'), harm(2, ['harm.radiance.holy'], 'the possessor or maker, if present'), restr({'methods': ['returning to that host']}, 'the possessor', 'days:1'), cleanse('cond.charmed or cond.frightened', 'the freed being')], f=2),
    rk("Cast out up to two possessions or effects of undead or fiends (roll against the higher stored effect DC, or the possessor's Resolve defense). On a success they end; each possessor takes Heavy radiant harm and cannot return to that host for a day; and each freed being's charm or fear ends.",
       [endw('up to two possessions, or effects made by undead or fiends'), harm(3, ['harm.radiance.holy'], 'each possessor or maker, if present'), restr({'methods': ['returning to that host']}, 'each possessor', 'days:1'), cleanse('cond.charmed or cond.frightened', 'each freed being'), tgt(1)], f=2)],
   check=('aimed', 'verb.talk', "the effect's stored effect DC, or the possessor's Resolve defense"), harm_tags=['harm.radiance.holy'],
   traits=['trait.sense.audible'], x=[('arcane wards and summonings', 'ab.unbinding; ab.banish'), ('hexes', 'ab.lift_the_hex')])

# ---------------- pact ----------------
ab('ab.patrons_brand', "Patron's Brand", D + 'pact.invocation', 1, 'pact_bolt', 'Working', 'beat',
   'Throw the mark of the power you bargained with.',
   'Applies to one target you can see within band.near.',
   [rk("Throw your patron's mark at one target within band.near. On a success it takes Moderate necrotic harm (shifted by delivered reach) and is frightened of you until the end of its next turn.",
       [harm(2, ['harm.blight.necrotic'], T), cond('cond.frightened', 1, 'rounds:1', T)], f=1),
    rk("Throw your patron's mark at one target within band.near. On a success it takes Heavy necrotic harm (shifted by delivered reach) and is frightened of you until the scene ends.",
       [harm(3, ['harm.blight.necrotic'], T), cond('cond.frightened', 1, 'scene', T)], f=1),
    rk("Throw your patron's mark at one target within band.far. On a success it takes Grievous necrotic harm (shifted by delivered reach) and is frightened of you until the scene ends.",
       [harm(4, ['harm.blight.necrotic'], T), cond('cond.frightened', 1, 'scene', T)], f=1)],
   check=ATK, harm_tags=['harm.blight.necrotic'], traits=['trait.nature.profane', 'trait.action.attack', 'trait.delivery.ranged', 'trait.sense.visible'], dictates=True,
   x=[('constructs and the mindless (the fear)', 'they take the harm only')])

ab('ab.blood_price', 'Blood Price', D + 'pact.sacrifice', 5, 'sacrifice', 'Working', 'rider',
   'Pay with your own body for a greater result.',
   'Applies to any one working or Strike of your own, declared with it.',
   [rk("Pay 3 Vitality as you act: this working or Strike is two severity rungs heavier, +1, its reach is one rung higher, and it holds a Precision lever.",
       [sev(2, 'this beat'), hedge(1, 'this beat'), reach('this beat'), lev('precision', 'this beat')], f=1)],
   verbs=['any'], oc=2, cost_text='3 Vitality (harm.blight.necrotic, no reduction, never lethal: refused if it would bring you to 0)',
   traits=['trait.nature.profane'], x=[('paying with another\'s blood', 'no pool ability; a rite with a sacrifice condition (05.8.4), and 03 records it')],
   nmi=['a lasting mark from the payment'])
