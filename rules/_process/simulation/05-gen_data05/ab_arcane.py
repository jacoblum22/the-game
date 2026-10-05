# deed.arcane -- 26 spells. Casting attribute Intellect; every working needs word and gesture (05.7.2).
from dsl05 import *

A = 'deed.arcane.'
T = 'the target'
ATK = ('aimed', 'verb.strike', "the target's attack defense")
EVA = ('resisted', 'evade', 'agility')
RES = ('resisted', 'endure', 'resolve')
END = ('resisted', 'endure', 'endurance')

# ---------------- fire ----------------
ab('ab.flame_lance', 'Flame Lance', A + 'fire.blast', 1, 'fire_bolt', 'Working', 'beat',
   'Throw a line of fire at one target.',
   'Applies to one target you can see within band.near.',
   [rk("Throw fire at one target within band.near. On a success it takes Moderate fire harm (shifted by delivered reach) and is burning.",
       [harm(2, ['harm.fire.flame'], T), cond('cond.burning', 1, 'scene', T)], f=1),
    rk("Throw fire at one target within band.near. On a success it takes Heavy fire harm (shifted by delivered reach) and is burning.",
       [harm(3, ['harm.fire.flame'], T), cond('cond.burning', 1, 'scene', T)], f=1),
    rk("Throw fire at one target within band.far. On a success it takes Grievous fire harm (shifted by delivered reach) and is burning.",
       [harm(4, ['harm.fire.flame'], T), cond('cond.burning', 1, 'scene', T)], f=1)],
   check=ATK, harm_tags=['harm.fire.flame'], traits=['trait.action.attack', 'trait.delivery.ranged', 'trait.sense.visible'],
   x=[('lighting a candle or a pipe', 'a small working (05.7.6)'), ('heating an object without flame', 'a stretch (05.5.2)')])

ab('ab.fire_shroud', 'Fire Shroud', A + 'fire.shaping', 2, 'fire_aura', 'Form', 'rider',
   'Wrap your body in a standing flame.',
   'Applies to yourself; the shroud harms those engaged with you.',
   [rk("For the scene you are shrouded in fire: you halve fire harm you take, and each foe that ends its turn engaged with you takes Light fire harm.",
       [aura('band.engaged', [resist(['harm.fire']), harm(1, ['harm.fire.flame'], 'each foe that ends its turn within band.engaged of you')])], f=2),
    rk("For the scene you are shrouded in fire: you halve fire harm you take, each foe that ends its turn engaged with you takes Moderate fire harm, and a foe that hits you in melee is burning.",
       [aura('band.engaged', [resist(['harm.fire']), harm(2, ['harm.fire.flame'], 'each foe that ends its turn within band.engaged of you'), cond('cond.burning', 1, 'scene', 'a foe that hits you with a melee attack')])], f=2)],
   slot='slot.aura', verbs=['any'], harm_tags=['harm.fire.flame'], traits=['trait.delivery.aura', 'trait.sense.visible'],
   x=[('protecting what you carry or wear from your own fire', 'it is protected; anything you set down is not')])

ab('ab.firestorm', 'Firestorm', A + 'fire.blast', 5, 'fire_burst', 'Working', 'beat',
   'Fill a space with fire.',
   'Applies to a point you can see within band.far and up to six beings within band.close of it.',
   [rk("Fire fills the ground around a point within band.far. Up to six beings within band.close of it roll Evade against your effect DC: on a failure each takes Grievous fire harm and is burning; on a success, half. Until the end of your next turn, a being that enters or ends its turn there takes Moderate fire harm.",
       [fchk('evade'), harm(4, ['harm.fire.flame'], 'each being within band.close of the point'), tgt(5), cond('cond.burning', 1, 'scene', 'each being that fails'), harm(2, ['harm.fire.flame'], 'a being that enters or ends its turn in the burning ground')], f=3, per='rest_long')],
   check=EVA, spread='burst', harm_tags=['harm.fire.flame'], traits=['trait.action.attack', 'trait.delivery.area', 'trait.sense.loud', 'trait.sense.visible'],
   x=[('sparing allies inside the area', 'the fire takes every being in it')])

# ---------------- frost ----------------
ab('ab.rime_spear', 'Rime Spear', A + 'frost.blast', 1, 'frost_bolt', 'Working', 'beat',
   'Throw a shaft of killing cold at one target.',
   'Applies to one target you can see within band.near.',
   [rk("Throw cold at one target within band.near. On a success it takes Moderate frost harm (shifted by delivered reach), is chilled, and is slowed until the end of its next turn.",
       [harm(2, ['harm.frost.ice'], T), cond('cond.chilled', 1, 'scene', T), cond('cond.slowed', 1, 'rounds:1', T)], f=1),
    rk("Throw cold at one target within band.near. On a success it takes Heavy frost harm (shifted by delivered reach), is chilled, and is slowed until the end of its next turn.",
       [harm(3, ['harm.frost.ice'], T), cond('cond.chilled', 1, 'scene', T), cond('cond.slowed', 1, 'rounds:1', T)], f=1),
    rk("Throw cold at one target within band.far. On a success it takes Grievous frost harm (shifted by delivered reach), is chilled, and is slowed until the end of its next turn.",
       [harm(4, ['harm.frost.ice'], T), cond('cond.chilled', 1, 'scene', T), cond('cond.slowed', 1, 'rounds:1', T)], f=1)],
   check=ATK, harm_tags=['harm.frost.ice'], traits=['trait.action.attack', 'trait.delivery.ranged', 'trait.sense.visible'],
   x=[('freezing water to walk on', 'ab.glaze')])

ab('ab.glaze', 'Glaze', A + 'frost.shaping', 3, 'ice_ground', 'Working', 'beat',
   'Lay a skin of ice over a surface.',
   'Applies to ground, a floor, a stair or still water within band.near, up to the space four beings stand in.',
   [rk("Ice covers a patch of ground or still water within band.near for the scene (it bears weight). Up to four beings on it roll Evade against your effect DC or fall prone; any being moving on it is slowed.",
       [fchk('evade'), cond('cond.prone', 1, 'rounds:1', 'each being on the ice that fails'), cond('cond.slowed', 1, 'scene', 'any being moving on the ice'), tgt(3), fact('the patch', 'surface', 'ice until scene_end')], f=2),
    rk("Ice covers a patch of ground or still water within band.near for the scene (it bears weight). Up to five beings on it roll Evade against your effect DC or fall prone and take Light frost harm; any being moving on it is slowed.",
       [fchk('evade'), cond('cond.prone', 1, 'rounds:1', 'each being on the ice that fails'), cond('cond.slowed', 1, 'scene', 'any being moving on the ice'), tgt(4), fact('the patch', 'surface', 'ice until scene_end'), harm(1, ['harm.frost.ice'], 'each being on the ice that fails')], f=2)],
   check=EVA, spread='linger', harm_tags=['harm.frost.ice'], traits=['trait.delivery.area', 'trait.sense.visible'],
   x=[('running water or the sea', 'a designed rite (05.8.4); a stretch freezes only still water')])

# ---------------- storm ----------------
ab('ab.arc_bolt', 'Arc Bolt', A + 'storm.lightning', 1, 'lightning_bolt', 'Working', 'beat',
   'Throw lightning that leaps from one body to the next.',
   'Applies to one target you can see within band.near; the leap goes to the nearest other being within band.close of it.',
   [rk("Throw lightning at one target within band.near. On a success it takes Moderate lightning harm (shifted by delivered reach) and is off-balance until the end of its next turn; the bolt leaps to the nearest other being within band.close of it, which takes the harm one rung lighter.",
       [harm(2, ['harm.storm.lightning'], T), cond('cond.off_balance', 1, 'rounds:1', T), tgt(1)], f=1),
    rk("Throw lightning at one target within band.near. On a success it takes Heavy lightning harm (shifted by delivered reach) and is off-balance until the end of its next turn; the bolt leaps twice, each leap one rung lighter.",
       [harm(3, ['harm.storm.lightning'], T), cond('cond.off_balance', 1, 'rounds:1', T), tgt(2)], f=1),
    rk("Throw lightning at one target within band.near. On a success it takes Heavy lightning harm +1 (shifted by delivered reach) and is dazed until the end of its next turn; the bolt leaps twice, each leap one rung lighter.",
       [harm(3, ['harm.storm.lightning'], T), hedge(1, 'this working'), cond('cond.dazed', 1, 'rounds:1', T), tgt(2)], f=1)],
   check=ATK, spread='chain', harm_tags=['harm.storm.lightning'], traits=['trait.action.attack', 'trait.delivery.ranged', 'trait.sense.loud', 'trait.sense.visible'],
   x=[('choosing where the bolt leaps', 'it takes the nearest being, friend or foe')])

ab('ab.thunderclap', 'Thunderclap', A + 'storm.thunder', 4, 'thunder_burst', 'Working', 'beat',
   'Burst the air around you with sound.',
   'Applies to up to four beings within band.close of you.',
   [rk("Thunder bursts from you. Up to four beings within band.close roll Endure (Endurance) against your effect DC: on a failure each takes Moderate thunder harm, is deafened until the scene ends and is knocked prone.",
       [fchk('endure'), harm(2, ['harm.storm.thunder'], 'each being within band.close that fails'), tgt(3), cond('cond.deafened', 1, 'scene', 'each being that fails'), cond('cond.prone', 1, 'rounds:1', 'each being that fails')], f=2)],
   check=END, spread='burst', harm_tags=['harm.storm.thunder'], traits=['trait.action.attack', 'trait.delivery.area', 'trait.sense.loud'],
   x=[('sparing allies inside the burst', 'it takes every being in it but you')])

# ---------------- earth ----------------
ab('ab.clutching_earth', 'Clutching Earth', A + 'earth.stone', 1, 'earth_hold', 'Working', 'beat',
   'Make the ground close on what stands on it.',
   'Applies to one target within band.near standing on earth or stone.',
   [rk("The ground grips one target within band.near (it rolls Evade against your effect DC): on a failure it is off-balance until the end of its next turn and grabbed by the ground until it breaks free or the scene ends.",
       [fchk('evade'), cond('cond.grabbed', 1, 'scene', T), cond('cond.off_balance', 1, 'rounds:1', T)], f=1),
    rk("The ground grips one target within band.near (it rolls Evade against your effect DC): on a failure it is restrained until the end of its next turn, then grabbed by the ground until it breaks free or the scene ends.",
       [fchk('evade'), cond('cond.restrained', 1, 'rounds:1', T), cond('cond.grabbed', 1, 'scene', T)], f=1),
    rk("The ground grips up to two targets within band.near (each rolls Evade against your effect DC): on a failure each takes Light crushing harm, is restrained until the end of its next turn, then grabbed by the ground until it breaks free or the scene ends.",
       [fchk('evade'), cond('cond.restrained', 1, 'rounds:1', T), cond('cond.grabbed', 1, 'scene', T), tgt(1), harm(1, ['harm.physical.crush'], T)], f=1)],
   check=EVA, traits=['trait.delivery.ranged', 'trait.sense.visible'], x=[('a target on a wooden floor, a deck or in the air', 'G4: no earth or stone to answer')])

ab('ab.stoneskin', 'Stoneskin', A + 'earth', 3, 'stone_ward', 'Working', 'beat',
   'Give living skin the hardness of stone.',
   'Applies to yourself or one willing being you touch.',
   [rk("For the scene, physical harm the warded being takes is reduced by 2, and it cannot be knocked prone or put off-balance.",
       [red(2, ['harm.physical']), immune(['cond.prone', 'cond.off_balance'])], f=2),
    rk("For the scene, physical harm the warded being takes is reduced by 3, and it cannot be knocked prone or put off-balance.",
       [red(3, ['harm.physical']), immune(['cond.prone', 'cond.off_balance'])], f=2)],
   traits=['trait.delivery.touch', 'trait.duration.lasting'], x=[('harm that is not physical', 'ab.spell_ward'), ('reduction beyond ch.07\'s cap of 4 in total', 'the cap holds')])

# ---------------- illusion ----------------
ab('ab.phantom', 'Phantom', A + 'illusion.phantasm', 1, 'false_image', 'Working', 'beat',
   'Place a false sight and sound where there is none.',
   'Applies to one point you can see within band.near; the image is no larger than a person; sustained.',
   [rk("While you sustain it, a false image with its sound stands at a point within band.near. One being that perceives and believes it is distracted, and your next beat or an ally's against that being holds a Precision lever. Touching it, or being told of it with cause, allows an Observe check against your effect DC to see through it.",
       [perm(2), cond('cond.distracted', 1, 'scene', 'one being that believes the image'), lev('precision', "your or an ally's next beat against the distracted being")], f=1),
    rk("While you sustain it, a false image with its sound stands at a point within band.near. Up to three beings that perceive and believe it are distracted, and your next beat or an ally's against one of them holds a Precision lever. Touching it, or being told of it with cause, allows an Observe check against your effect DC to see through it.",
       [perm(2), cond('cond.distracted', 1, 'scene', 'each being that believes the image'), tgt(2), lev('precision', "your or an ally's next beat against a distracted being")], f=1),
    rk("While you sustain it, a false image up to the size of a wagon, moving and speaking as you direct, stands within band.far. Up to three beings that perceive and believe it are distracted, and your next beat or an ally's against one of them holds a Precision lever. Touching it, or being told of it with cause, allows an Observe check against your effect DC to see through it.",
       [perm(4), cond('cond.distracted', 1, 'scene', 'each being that believes the image'), tgt(2), lev('precision', "your or an ally's next beat against a distracted being")], f=1)],
   traits=['trait.nature.illusion', 'trait.duration.sustained', 'trait.sense.visible', 'trait.sense.audible'],
   x=[('an image that harms or bears weight', 'no illusion has substance'), ('fooling a mindless being or one that does not use sight or hearing', 'G4 for that target')])

ab('ab.veil', 'Veil', A + 'illusion.veiling', 2, 'unseen', 'Working', 'beat',
   'Hide one body from sight.',
   'Applies to yourself or one willing being you touch; sustained; ends when the veiled being attacks.',
   [rk("While you sustain it, the veiled being cannot be seen: it holds flag.hidden even while observed and moving, and holds a Precision lever on Sneak beats.",
       [move('the veiled being', 0, add=['flag.hidden']), perm(4), lev('precision', "the veiled being's Sneak beats", 'scene', verbs=['verb.sneak'])], f=2),
    rk("While you sustain it, you and one other willing being you touch cannot be seen: each holds flag.hidden even while observed and moving, and holds a Precision lever on Sneak beats.",
       [move('each veiled being', 0, add=['flag.hidden']), perm(4), lev('precision', "the veiled beings' Sneak beats", 'scene', verbs=['verb.sneak']), tgt(2)], f=2)],
   traits=['trait.nature.illusion', 'trait.duration.sustained', 'trait.delivery.touch'],
   x=[('silence, scent or tracks', 'verb.sneak still decides those'), ('staying veiled while attacking', 'the veil ends')], nmi=['that the veiled being makes no sound or leaves no trace'])

ab('ab.mirror_host', 'Mirror Host', A + 'illusion.glamour', 5, 'images', 'Working', 'beat',
   'Surround yourself with false copies of your body.',
   'Applies to yourself, against attackers that rely on sight.',
   [rk("For the scene copies of you move as you move: the first two hits against you from attackers that rely on sight are negated; you gain +1 to Agility defense; each attacker that strikes a copy is distracted until the scene ends; and you hold a Precision lever against a distracted attacker.",
       [prevent('the attacker relies on sight', 'scene_end', 2), prevent('the attacker relies on sight (second image)'), dedge(1, 'agility', 'the attacker relies on sight'), cond('cond.distracted', 1, 'scene', 'an attacker that strikes a copy'), lev('precision', 'your beats against a distracted attacker', 'scene')], f=3, per='scene_end')],
   traits=['trait.nature.illusion', 'trait.duration.lasting', 'trait.sense.visible'], x=[('attackers that do not rely on sight', 'they strike you as usual')])

# ---------------- divination ----------------
ab('ab.trace_the_thread', 'Trace the Thread', A + 'divination.tracing', 1, 'seeking', 'Working', 'beat',
   'Feel the direction of a thing you are tied to.',
   'Applies to one person or object you have touched within the past season, or of which you hold a token; within a day\'s travel.',
   [rk("Name a person or object you have touched or hold a token of. If it lies within a day's travel you know its direction and how far (by band, then by watches of travel) until the scene ends, and hold that as a Precision lever on your next beat to follow it.",
       [perm(4), lev('precision', 'your next beat that follows it')], f=1),
    rk("Name a person or object you have touched or hold a token of. If it lies within a day's travel you know its direction, how far, and whether it is moving, until the scene ends, and hold that as a Precision lever on your next beat to follow it.",
       [perm(4), rev('whether the traced thing is moving'), lev('precision', 'your next beat that follows it')], f=1),
    rk("Name a person or object you have touched or hold a token of. If it lies within a week's travel you know its direction, how far, whether it is moving, and the kind of place it is in, until the scene ends, and hold that as a Precision lever on your next beat to follow it.",
       [perm(4), rev('whether the traced thing is moving'), rev('the terrain tag of the place it is in'), lev('precision', 'your next beat that follows it')], f=1)],
   x=[('seeing or hearing what is around it', 'rit.scrying_pool'), ('a thing you have never touched and hold no token of', 'G4 for this working')], nmi=['sight of the traced thing'])

ab('ab.foresee', 'Foresee', A + 'divination.foresight', 4, 'forewarning', 'Reaction', 'reaction',
   'Know a blow a breath before it falls.',
   'Applies to one hit against you by an attacker you can perceive.',
   [rk("When you are hit, negate that hit: you had already moved. Move one band, learn what the attacker means to do next, and hold a Precision lever against it until the scene ends.",
       [prevent('you perceive the attacker'), move('self', 1), rev("the attacker's next declared intent"), lev('precision', 'your beats against the attacker', 'scene')], f=2, per='scene_end')],
   hook='on_hit_taken', when='you perceive the attacker', x=[('a hit on someone else', 'ab.sanctuary; eff.intercept abilities'), ('knowing events beyond the next few moments', 'rit.augury; rit.foresight')])

# ---------------- warding ----------------
ab('ab.spell_ward', 'Spell Ward', A + 'warding.shielding', 1, 'ward', 'Reaction', 'reaction',
   'Raise a plane of force against a blow.',
   'Applies to one hit against you that you perceive, of any harm type.',
   [rk("In place of Fend, when you are hit, the harm is one severity rung lighter; if it is magical harm, two rungs lighter.",
       [dreact('spell ward', [sev(-1, 'the hit being warded'), sev(-1, 'the hit being warded has trait.nature.magical')])], f=1),
    rk("In place of Fend, when you are hit, the harm is two severity rungs lighter, and your next resisted check against that attacker this scene is framed one stakes rung lower.",
       [dreact('spell ward', [sev(-2, 'the hit being warded'), lev('protective', 'your next resisted check against that attacker', 'scene')])], f=1),
    rk("In place of Fend, when you are hit, the harm is two severity rungs lighter; if it is magical harm, the hit is negated.",
       [dreact('spell ward', [sev(-2, 'the hit being warded'), prevent('the hit has trait.nature.magical')])], f=1)],
   hook='on_hit_taken', when='you perceive the attack', slot='slot.defense_reaction', ckey=True,
   x=[('warding another being', 'ab.sanctuary; ab.stoneskin'), ('a hit you did not perceive', 'no reaction is possible')])

ab('ab.counterspell', 'Counterspell', A + 'warding.countering', 2, 'counter', 'Reaction', 'reaction',
   'Break a working as it is being made.',
   'Applies to a working with trait.nature.magical declared by another within band.near whose casting you perceive.',
   [rk("When another within band.near casts, roll against that caster's effect DC (divine and primal workings: with a Precision snag). On a success the working is negated (its Focus and action are still spent) and the caster is off-balance until the end of its next turn.",
       [ctr('another entity within band.near declares a working with trait.nature.magical'), cond('cond.off_balance', 1, 'rounds:1', 'the caster'), lev('precision', 'your next beat against the caster', 'rounds:1')], f=2),
    rk("When another within band.near casts, roll against that caster's effect DC (divine and primal workings: with a Precision snag). On a success the working is negated (its Focus and action are still spent), the caster loses 1 more Focus, and it is off-balance until the end of its next turn.",
       [ctr('another entity within band.near declares a working with trait.nature.magical'), drain(1, 'the caster'), cond('cond.off_balance', 1, 'rounds:1', 'the caster'), lev('precision', 'your next beat against the caster', 'rounds:1')], f=2)],
   hook='on_declare', when="another entity within band.near declares a working with trait.nature.magical", check=('aimed', 'verb.handle', "the caster's effect DC"),
   x=[('an effect already in place', 'ab.unbinding'), ('a creature\'s natural power that is not a working', 'verb.evade or verb.endure')])

ab('ab.unbinding', 'Unbinding', A + 'warding.dispelling', 3, 'dispel', 'Working', 'beat',
   'Take apart a working that is already in place.',
   'Applies to one magical effect, ward, summoning or magical condition within band.near that you can perceive.',
   [rk("Unmake one magical effect within band.near (roll against its stored effect DC). Delivered reach 1 suppresses it for 3 rounds; 2 ends it and one magical condition on the same being or place; 3 or more also ends a second effect of the same maker and tells you that maker's signature.",
       [endw('one magical effect within band.near'), cleanse('one condition of category magical', 'the same being or place'), rev("the maker's signature"), tgt(1)], f=2),
    rk("Unmake up to two magical effects within band.near (roll against the higher stored effect DC). Delivered reach 1 suppresses them for 3 rounds; 2 ends them and one magical condition on each being or place; 3 or more also ends a further effect of the same maker, tells you that maker's signature, and gives you a Precision lever against that maker's workings this scene.",
       [endw('up to two magical effects within band.near'), cleanse('one condition of category magical', 'each being or place'), rev("the maker's signature"), tgt(2), lev('precision', "beats against that maker's workings", 'scene')], f=2)],
   check=('aimed', 'verb.handle', "the effect's stored effect DC"), x=[('a curse laid by hexcraft', 'ab.lift_the_hex (arcane unbinding takes a Precision snag against it)'), ('possession', 'ab.cast_out')])

# ---------------- mind ----------------
ab('ab.honeyed_thought', 'Honeyed Thought', A + 'mind.charm', 1, 'charm', 'Working', 'beat',
   'Make one mind regard you kindly.',
   'Applies to one being with a mind within band.close that can see or hear you; ends if you or your allies harm it.',
   [rk("One being within band.close rolls Endure (Resolve) against your effect DC: on a failure it is charmed until the scene ends or you or your allies harm it. It regards you as a friend; it takes no orders.",
       [fchk('endure'), cond('cond.charmed', 1, 'scene', T)], f=1),
    rk("One being within band.close rolls Endure (Resolve) against your effect DC: on a failure it is charmed until the scene ends or you or your allies harm it, and you hold a Precision lever on Talk with it. It regards you as a friend; it takes no orders.",
       [fchk('endure'), cond('cond.charmed', 1, 'scene', T), lev('precision', 'Talk beats with the charmed being', 'scene', verbs=['verb.talk'])], f=1),
    rk("Up to two beings within band.close roll Endure (Resolve) against your effect DC: on a failure each is charmed until the scene ends or you or your allies harm it, and you hold a Precision lever on Talk with them. They regard you as a friend; they take no orders.",
       [fchk('endure'), cond('cond.charmed', 1, 'scene', T), lev('precision', 'Talk beats with the charmed beings', 'scene', verbs=['verb.talk']), tgt(1)], f=1)],
   check=RES, traits=['trait.nature.mental'], dictates=True,
   x=[('giving the charmed being a command', 'ab.compel'), ('a mindless being', 'G4 (trait.nature.mental)')], nmi=['that the being obeys you', 'that it forgets being charmed'])

ab('ab.compel', 'Compel', A + 'mind.compulsion', 4, 'command', 'Working', 'beat',
   'Put one act into another\'s will.',
   'Applies to one being with a mind within band.close that can hear and understand you; the act is one it could do in a single turn and is not self-destroying.',
   [rk("Speak one command of a single act. The target rolls Endure (Resolve) against your effect DC: on a failure it spends its next turn doing that act and nothing else, cannot act against you until that turn ends, and afterwards does not recall that the will was not its own.",
       [fchk('endure'), perm(4), cond('cond.charmed', 1, 'rounds:1', T), restr({'methods': ['acting against the caster']}, T, 'rounds:1'), fact(T, 'remembers_compulsion', False)], f=3)],
   check=RES, traits=['trait.nature.mental'], dictates=True,
   x=[('an act that would plainly kill or maim the target', 'the command fails at once'), ('a command lasting beyond one turn', 'a designed rite (05.8.4); a geas is a rite')])

# ---------------- summoning ----------------
ab('ab.call_servant', 'Call Servant', A + 'summoning.calling', 1, 'summon_servant', 'Working', 'beat',
   'Call a lesser being to do as it is told.',
   'Applies to one summoned servant at a time; it acts only when you spend an action to command it (06).',
   [rk("Call a servant of threat band 1 for the scene. It can carry, fetch, hold, open and watch; it does not fight. Once in the scene it may Help one of your beats.",
       [summ('a servant spirit of threat band 1', 1, 'scene'), perm(2), lev('precision', 'one beat the servant helps')], f=1, per='scene_end'),
    rk("Call a servant of threat band 2 for the scene. It can carry, fetch, hold, open, watch and fight when commanded. Once in the scene it may Help one of your beats.",
       [summ('a servant spirit of threat band 2', 2, 'scene'), perm(2), lev('precision', 'one beat the servant helps')], f=1, per='scene_end'),
    rk("Call a servant of threat band 3 for the scene. It can carry, fetch, hold, open, watch and fight when commanded. Once in the scene it may Help one of your beats.",
       [summ('a servant spirit of threat band 3', 3, 'scene'), perm(2), lev('precision', 'one beat the servant helps')], f=1, per='scene_end')],
   traits=['trait.duration.lasting'], x=[('a servant that acts on its own turn', 'INV-11: it acts only when commanded'), ('a named or bound being', 'rit.circle_of_binding')])

ab('ab.banish', 'Banish', A + 'summoning.banishing', 3, 'banishment', 'Working', 'beat',
   'Send a being that does not belong here back where it came from.',
   'Applies to one summoned being, spirit, fiend or elemental within band.near.',
   [rk("One summoned or otherworldly being within band.near rolls Endure (Resolve) against your effect DC: on a failure a summoning ends at once; a being native to another place is sent from this place for the scene and cannot return to it for a day.",
       [fchk('endure'), endw('the summoning that holds the target here'), perm(4), restr({'methods': ['returning to this place']}, T, 'days:1')], f=2),
    rk("Up to two summoned or otherworldly beings within band.near roll Endure (Resolve) against your effect DC: on a failure a summoning ends at once; a being native to another place takes Moderate raw harm, is sent from this place for the scene and cannot return to it for a day.",
       [fchk('endure'), endw('the summoning that holds the target here'), perm(4), restr({'methods': ['returning to this place']}, T, 'days:1'), tgt(1), harm(2, ['harm.arcane.raw'], T)], f=2)],
   check=RES, x=[('a being native to this world', 'G4 for this working'), ('possession of a host', 'ab.cast_out')])

# ---------------- necromancy ----------------
ab('ab.wither', 'Wither', A + 'necromancy.withering', 1, 'wither', 'Working', 'beat',
   'Drain the strength from living flesh.',
   'Applies to one living being within band.near.',
   [rk("One living being within band.near rolls Endure (Endurance) against your effect DC: on a failure it takes Moderate necrotic harm and is weakened until the scene ends.",
       [fchk('endure'), harm(2, ['harm.blight.necrotic'], T), cond('cond.weakened', 1, 'scene', T)], f=1),
    rk("One living being within band.near rolls Endure (Endurance) against your effect DC: on a failure it takes Heavy necrotic harm and is weakened until the scene ends.",
       [fchk('endure'), harm(3, ['harm.blight.necrotic'], T), cond('cond.weakened', 1, 'scene', T)], f=1),
    rk("One living being within band.near rolls Endure (Endurance) against your effect DC: on a failure it takes Grievous necrotic harm and is weakened until the scene ends.",
       [fchk('endure'), harm(4, ['harm.blight.necrotic'], T), cond('cond.weakened', 1, 'scene', T)], f=1)],
   check=END, harm_tags=['harm.blight.necrotic'], traits=['trait.action.attack', 'trait.delivery.ranged'],
   x=[('undead and constructs', 'G4: no living flesh')])

ab('ab.drain_life', 'Drain Life', A + 'necromancy.draining', 2, 'life_drain', 'Working', 'beat',
   'Take life from another body into your own.',
   'Applies to one living being you touch.',
   [rk("Touch one living being (roll against its attack defense). On a success it takes Heavy necrotic harm and is weakened until the end of its next turn, and you regain 3 Vitality.",
       [harm(3, ['harm.blight.necrotic'], T), cond('cond.weakened', 1, 'rounds:1', T), heal(3, 'self')], f=2),
    rk("Touch one living being (roll against its attack defense). On a success it takes Grievous necrotic harm and is weakened until the end of its next turn, and you regain 5 Vitality.",
       [harm(4, ['harm.blight.necrotic'], T), cond('cond.weakened', 1, 'rounds:1', T), heal(5, 'self')], f=2)],
   check=ATK, harm_tags=['harm.blight.necrotic'], traits=['trait.action.attack', 'trait.delivery.touch'],
   x=[('healing another with what you take', 'no license does'), ('regaining Vitality past the healing cap', '05.7.8')])

ab('ab.raise_the_fallen', 'Raise the Fallen', A + 'necromancy.raising', 5, 'raise_dead', 'Working', 'beat',
   'Give the dead the motion of the living.',
   'Applies to up to two corpses within band.close that have not been laid to rest by rite.',
   [rk("Up to two corpses within band.close rise as mindless undead of threat band 3 for a day. They obey your spoken commands and act only when you spend an action to command them.",
       [summ('a mindless undead of threat band 3 raised from a corpse', 3, 'days:1'), summ('a second mindless undead of threat band 3 raised from a corpse', 3, 'days:1'), perm(4)], f=3, per='rest_long')],
   wk=1, weak=("While any of your raised dead stands, sacred wards and exorcisms treat you as profane.", fact('the caster', 'counts_as', 'trait.nature.profane while a raised dead stands')),
   traits=['trait.nature.profane', 'trait.duration.lasting'],
   x=[('a body laid to rest by ab.last_rites or a funeral rite', 'G4'), ('returning the person who died', 'canon_impossible')],
   nmi=['that the raised dead think, remember or speak'], basis=['03: raising the unwilling dead writes conduct evidence (piety, mercy)'])

# ---------------- alteration ----------------
ab('ab.feather_fall', 'Feather Fall', A + 'alteration.motion', 1, 'slow_fall', 'Reaction', 'reaction',
   'Slow a falling body.',
   'Applies to yourself or one being within band.close that is falling.',
   [rk("When you or a being within band.close falls, the fall's harm is two severity rungs lighter for that being.",
       [sev(-2, 'harm from the fall')], f=1),
    rk("When you or up to two other beings within band.close fall, the fall's harm is two severity rungs lighter for each.",
       [sev(-2, 'harm from the fall'), tgt(2)], f=1),
    rk("When you or up to three other beings within band.close fall, the fall's harm is two severity rungs lighter for each, and each lands where it chooses within one band of where it would have struck.",
       [sev(-2, 'harm from the fall'), tgt(3), move('each falling being', 1)], f=1)],
   hook='on_move', when='a being within band.close begins to fall', traits=['trait.delivery.ranged'],
   x=[('rising or flying', 'eff.movement_mode fly: no pool spell below a rite gives it'), ('a thrown or shot object', 'ab.spell_ward')])

ab('ab.long_step', 'Long Step', A + 'alteration.translocation', 2, 'blink', 'Working', 'beat',
   'Cross a space without passing through it.',
   'Applies to yourself, to a place you can see within two bands, with open air between you and it.',
   [rk("Step to a place you can see within two bands, across any gap or drop, provoking no reaction.",
       [move('self', 2), perm(4), waive('reactions provoked by this movement', 'this beat')], f=2),
    rk("Step to a place you can see within two bands, across any gap or drop, provoking no reaction, and bring one willing being you touch.",
       [move('self', 2), perm(4), waive('reactions provoked by this movement', 'this beat'), tgt(1)], f=2)],
   traits=['trait.action.move'], x=[('a place you cannot see, or through a wall or closed door', 'G4 for this working; rit.custom'), ('carrying an unwilling being', 'verb.grapple first, and it is still unwilling')])

# ---------------- the branch working (05.7.11; revision I-009) ----------------
# Held through every arcane training license; no slot; zero Focus. Rank = grade in the casting school's license.
ab('ab.force_bolt', 'Force Bolt', 'deed.arcane', 1, 'branch_arcane', 'Working', 'beat',
   'Throw unshaped formula at one target as raw force.',
   'Applies to one being or object you can see within band.near.',
   [rk("Throw a bolt of unshaped force at one target you can see within band.near. On a success it takes Moderate force harm (shifted by delivered reach); on a critical success it is also pushed one band away from you.",
       [harm(2, ['harm.arcane.force'], T), move(T, 1)]),
    rk("Throw a bolt of unshaped force at one target you can see within band.near. On a success it takes Heavy force harm (shifted by delivered reach); on a critical success it is also pushed one band away from you.",
       [harm(3, ['harm.arcane.force'], T), move(T, 1)]),
    rk("Throw a bolt of unshaped force at one target you can see within band.near. On a success it takes Grievous force harm (shifted by delivered reach); on a critical success it is also pushed one band away from you.",
       [harm(4, ['harm.arcane.force'], T), move(T, 1)])],
   check=('aimed', 'verb.strike', "the target's Guard"), harm_tags=['harm.arcane.force'], branch_working=True,
   traits=['trait.action.attack', 'trait.delivery.ranged', 'trait.sense.audible', 'trait.sense.visible'],
   x=[('a shaped effect: fire, frost, a ward, a charm', 'a spell of that school'), ('a target beyond band.near', 'the Far flare, or a spell that reaches further'), ('lighting, chilling or nudging a thing', 'a small working (05.7.6)')],
   nmi=['that the bolt sets things alight, freezes, binds or lingers'],
   basis=['05.7.11', '06 Interface request (b) to 05', 'I-009', 'DL-05-31'])
