# deed.influence -- 18 abilities.
from dsl05 import *

I = 'deed.influence.'
T = 'the target'

# ---------------- persuasion ----------------
ab('ab.silver_tongue', 'Silver Tongue', I + 'persuasion.appeal', 1, 'appeal', 'Lever', 'passive',
   'Speak to what a listener already wants.',
   'Applies to Talk beats that persuade a listener one of whose wants is an established fact you know.',
   [rk("When you persuade someone, you may cite one of their wants that you know as an Amplifying lever.",
       [lev('amplifying', 'a Talk beat that persuades, citing a known want of the listener', 'scene', verbs=['verb.talk'])]),
    rk("When you persuade someone, you may cite one of their wants that you know as an Amplifying lever and as a Precision lever.",
       [lev('amplifying', 'a Talk beat that persuades, citing a known want of the listener', 'scene', verbs=['verb.talk']), lev('precision', 'a Talk beat that persuades, citing a known want of the listener', 'scene', verbs=['verb.talk'])]),
    rk("When you persuade someone, you may cite one of their wants that you know as an Amplifying lever and as a Precision lever, and the beat is framed one stakes rung lower.",
       [lev('amplifying', 'a Talk beat that persuades, citing a known want of the listener', 'scene', verbs=['verb.talk']), lev('precision', 'a Talk beat that persuades, citing a known want of the listener', 'scene', verbs=['verb.talk']), stakes('a Talk beat that persuades, citing a known want of the listener')])],
   x=[('a want the player asserts but no fact holds', 'ab.read_the_heart; 15'), ('past a recorded refusal', 'refusals hold (15)')])

ab('ab.turn_the_room', 'Turn the Room', I + 'persuasion.argument', 3, 'sway_crowd', 'Working', 'beat',
   'Move a gathering as if it were one listener.',
   'Applies to a group of listeners in one place who can hear you and share a concern.',
   [rk("Address a gathering as one listener (Talk, Presence, against the highest Resolve defense among its leaders). The beat's reach is one rung higher, and the gathering's social clock ticks by your delivered reach.",
       [perm(2), reach('this beat'), tick("the gathering's social clock (15)", 'delivered_reach')], f=1),
    rk("Address a gathering as one listener (Talk, Presence, against the highest Resolve defense among its leaders). The beat's reach is one rung higher and its stakes one rung lower, and the gathering's social clock ticks by your delivered reach.",
       [perm(2), reach('this beat'), tick("the gathering's social clock (15)", 'delivered_reach'), stakes('this beat')], f=1)],
   attr='presence', check=('aimed', 'verb.talk', "the highest Resolve defense among the gathering's leaders"), traits=['trait.action.speech', 'trait.sense.loud'],
   x=[('a mob already in motion', 'ab.rally; verb.talk at Dire stakes'), ('each member\'s private refusal', 'they hold (15)')])

# ---------------- command ----------------
ab('ab.rally', 'Rally', I + 'command.rallying', 1, 'rally', 'Working', 'beat',
   'Call faltering allies back to their purpose.',
   'Applies to up to three allies within band.near who can hear you.',
   [rk("Up to three allies who hear you are freed of fear, and each holds a Precision lever on its next beat.",
       [cleanse('cond.frightened', 'each ally who hears you'), tgt(2), lev('precision', "each rallied ally's next beat")], f=1),
    rk("Up to four allies who hear you are freed of fear, and each holds a Precision lever and a Protective lever on its next beat.",
       [cleanse('cond.frightened', 'each ally who hears you'), tgt(3), lev('precision', "each rallied ally's next beat"), lev('protective', "each rallied ally's next beat")], f=1),
    rk("Up to five allies who hear you are freed of fear and of being dazed, and each holds a Precision lever on its beats until the scene ends.",
       [cleanse('cond.frightened and cond.dazed', 'each ally who hears you'), tgt(4), lev('precision', "each rallied ally's beats", 'scene'), lev('protective', "each rallied ally's next beat")], f=1)],
   traits=['trait.action.speech', 'trait.sense.loud'], x=[('rallying yourself', 'ab.sworn_purpose; verb.endure'), ('allies who cannot hear you', 'they are not rallied')])

ab('ab.hold_the_line', 'Hold the Line', I + 'command.discipline', 4, 'command_aura', 'Form', 'rider',
   'Keep those who follow you steady by your presence.',
   'Applies to allies within band.near who can see or hear you, while you are not prone, stunned or unconscious.',
   [rk("For the scene, allies within band.near of you cannot be frightened, have +1 to Agility defense, and hold a Protective lever on their beats.",
       [aura('band.near', [immune(['cond.frightened']), dedge(1, 'agility', 'an ally within band.near of you'), lev('protective', 'beats by allies within band.near of you', 'scene')])], f=2)],
   slot='slot.aura', verbs=['any'], traits=['trait.delivery.aura'], x=[('allies beyond band.near', 'they are outside the aura'), ('yourself', 'the aura steadies others')])

# ---------------- performance ----------------
ab('ab.stirring_song', 'Stirring Song', I + 'performance.music', 1, 'inspire', 'Working', 'beat',
   'Lift the hearts of those who hear you play.',
   'Applies to up to three allies within band.near who can hear you; sustained.',
   [rk("While you sustain it, up to three allies who hear you hold a Protective lever on their beats.",
       [lev('protective', 'beats by allies who hear the song', 'scene'), tgt(2)], f=1),
    rk("While you sustain it, up to three allies who hear you hold a Protective lever and a Precision lever on their beats.",
       [lev('protective', 'beats by allies who hear the song', 'scene'), lev('precision', 'beats by allies who hear the song', 'scene'), tgt(2)], f=1),
    rk("While you sustain it, up to three allies who hear you hold a Protective lever and a Precision lever on their beats and cannot be frightened.",
       [lev('protective', 'beats by allies who hear the song', 'scene'), lev('precision', 'beats by allies who hear the song', 'scene'), tgt(2), immune(['cond.frightened'])], f=1)],
   traits=['trait.duration.sustained', 'trait.sense.loud', 'trait.action.speech'], x=[('going unheard', 'the song is loud'), ('deaf or deafened allies', 'they are not lifted')])

ab('ab.captivate', 'Captivate', I + 'performance.spectacle', 2, 'hold_audience', 'Working', 'beat',
   'Hold every eye in a place on yourself.',
   'Applies to up to four beings within band.near that can see and hear you and are not in a fight.',
   [rk("Perform (Talk, Presence, against the highest Wits defense among them). On a success up to four watchers are distracted while you keep performing, until the scene ends or one of them is harmed.",
       [cond('cond.distracted', 1, 'scene', 'each watcher'), tgt(3)], f=1),
    rk("Perform (Talk, Presence, against the highest Wits defense among them). On a success up to four watchers are distracted while you keep performing, until the scene ends or one of them is harmed, and allies hold a Precision lever on Sneak beats past them.",
       [cond('cond.distracted', 1, 'scene', 'each watcher'), tgt(3), lev('precision', "allies' Sneak beats past the watchers", 'scene', verbs=['verb.sneak'])], f=1)],
   attr='presence', check=('aimed', 'verb.talk', 'the highest Wits defense among the watchers'), traits=['trait.sense.visible', 'trait.sense.audible'],
   x=[('watchers already fighting or alarmed', 'ab.phantom; verb.setup')])

# ---------------- intimidation ----------------
ab('ab.cow', 'Cow', I + 'intimidation.display', 1, 'menace', 'Working', 'rider',
   'Make a listener afraid of what you will do.',
   'Applies to a Talk beat that intimidates one being that can see or hear you.',
   [rk("When your Talk to intimidate succeeds, the target is frightened of you until the scene ends.",
       [cond('cond.frightened', 1, 'scene', T)], f=1),
    rk("When your Talk to intimidate succeeds, the target is frightened of you until the scene ends and off-balance until the end of its next turn, and one other being that saw it is frightened of you until the end of its next turn.",
       [cond('cond.frightened', 1, 'scene', T), cond('cond.off_balance', 1, 'rounds:1', T), tgt(1)], f=1),
    rk("When your Talk to intimidate succeeds, the target and up to two others that saw it are frightened of you until the scene ends, and their side's morale clock ticks by your delivered reach.",
       [cond('cond.frightened', 1, 'scene', T), tgt(2), tick("the target's side's morale clock", 'delivered_reach')], f=1)],
   verbs=['verb.talk'], traits=['trait.nature.mental'], dictates=True, x=[('the mindless', 'G4 (trait.nature.mental)'), ('lasting obedience', 'fear ends with the scene; standing is 15\'s')])

ab('ab.break_the_will', 'Break the Will', I + 'intimidation.interrogation', 5, 'interrogate', 'Working', 'beat',
   'Take from a cornered mind what it is holding back.',
   'Applies to one being that is captive, cornered or at your mercy and can hear and understand you.',
   [rk("Question a captive or cornered being (Talk, Presence, against its Resolve defense). The beat's reach is one rung higher; on a success you learn two things it holds secret, it is frightened of you until the scene ends, it cannot lie to you this scene, and you hold a Precision lever on Talk with it.",
       [reach('this beat'), rev('one secret the being holds'), rev('a second secret the being holds'), cond('cond.frightened', 1, 'scene', T), restr({'methods': ['lying to the questioner']}, T, 'scene'), lev('precision', 'Talk beats with the being', 'scene', verbs=['verb.talk'])], f=3, per='scene_end')],
   attr='presence', check=('aimed', 'verb.talk', "the target's Resolve defense"), traits=['trait.action.speech', 'trait.nature.mental'], dictates=True,
   x=[('what the being does not know', 'it cannot tell it'), ('cruelty as the method', 'it works as any method does, and 03 records conduct.mercy')],
   nmi=['knowledge the being does not hold'])

# ---------------- intrigue ----------------
ab('ab.web_of_whispers', 'Web of Whispers', I + 'intrigue.networks', 1, 'court_ear', 'Working', 'beat',
   'Ask the people who watch the powerful from beside them.',
   'Applies in a court, guildhall, temple or great house where you hold a contact or have spent a day.',
   [rk("Spend a watch among servants, clerks and hangers-on (Talk, Presence, against the institution's tier). On a success learn one rumor about a named person of rank and who holds it.",
       [({'effect_id': 'eff.reveal', 'params': {'sealed_ref': 'one rumor about the named person of rank (11), with its source'}}, 2), fact('a named member of the household', 'holds_rumor_about', 'the named person')], per='scene_end'),
    rk("Spend a watch among servants, clerks and hangers-on (Talk, Presence, against the institution's tier). On a success learn two rumors about a named person of rank, who holds them, and one alliance or enmity of that person.",
       [({'effect_id': 'eff.reveal', 'params': {'sealed_ref': 'two rumors about the named person of rank (11), with their sources'}}, 3), fact('a named member of the household', 'holds_rumor_about', 'the named person'), rev('one alliance or enmity of the named person')], per='scene_end'),
    rk("Spend an hour among servants, clerks and hangers-on (Talk, Presence, against the institution's tier). On a success learn two rumors about a named person of rank and which the household believes, who holds them, and one alliance or enmity of that person.",
       [({'effect_id': 'eff.reveal', 'params': {'sealed_ref': 'two rumors about the named person of rank (11), their sources, and which the household holds true'}}, 5), fact('a named member of the household', 'holds_rumor_about', 'the named person'), rev('one alliance or enmity of the named person')], per='scene_end')],
   attr='presence', check=('aimed', 'verb.talk', "the institution's tier (ch.11)"),
   x=[('the underworld and the street', 'ab.word_on_the_street'), ('whether a rumor is true', 'sealed (11)')], nmi=['the truth value of a rumor'])

ab('ab.leverage', 'Leverage', I + 'intrigue.leverage', 4, 'hold_secret', 'Lever', 'rider',
   'Use a thing someone cannot afford to have known.',
   'Applies to a Talk beat with a being about whom you hold an established fact it wants kept secret.',
   [rk("When you Talk with someone whose secret you hold, cite it: the beat holds a Precision lever and an Amplifying lever, its reach is one rung higher and its stakes one rung lower.",
       [lev('precision', 'this beat'), lev('amplifying', 'this beat'), reach('this beat'), stakes('this beat')], f=1)],
   verbs=['verb.talk'], lim=1, x=[('a secret you only suspect', 'investigation (15) first'), ('making a friend', 'the listener\'s standing toward you falls one step after the scene (15)')])

# ---------------- trade ----------------
ab('ab.sharp_bargain', 'Sharp Bargain', I + 'trade.haggling', 1, 'haggle', 'Edge', 'passive',
   'Find the price a seller will really take.',
   'Applies to Talk beats that settle a price or the terms of an exchange.',
   [rk("+1 to Talk beats that settle a price or terms.",
       [edge(1, 'deed_tag under deed.influence.trade and the beat settles a price or terms')]),
    rk("+1 to Talk beats that settle a price or terms, and they are framed one stakes rung lower.",
       [edge(1, 'deed_tag under deed.influence.trade and the beat settles a price or terms'), stakes('deed_tag under deed.influence.trade and the beat settles a price or terms')]),
    rk("+2 to Talk beats that settle a price or terms, and they are framed one stakes rung lower.",
       [edge(2, 'deed_tag under deed.influence.trade and the beat settles a price or terms'), stakes('deed_tag under deed.influence.trade and the beat settles a price or terms')])],
   x=[('a seller with a recorded refusal to sell', 'the refusal holds (15)')])

ab('ab.appraisers_eye', "Appraiser's Eye", I + 'trade.appraisal', 2, 'appraise', 'Working', 'beat',
   'Tell what a thing is worth and where it came from.',
   'Applies to one object you can handle for a few moments.',
   [rk("Appraise an object (Observe, Wits, against Moderate, or the forger's effect DC). On a success learn its true price band and its maker or place of making.",
       [rev('the true price band of the object'), rev('the maker or place of making')]),
    rk("Appraise an object (Observe, Wits, against Moderate, or the forger's effect DC). On a success learn its true price band and its maker or place of making, and hold that as a Precision lever on buying or selling it.",
       [rev('the true price band of the object'), rev('the maker or place of making'), lev('precision', 'Talk beats that buy or sell the object', 'scene', verbs=['verb.talk'])])],
   attr='wits', check=('aimed', 'verb.observe', "obstacle tier moderate, or the forger's effect DC"), x=[('magical properties', 'ab.spell_sight; identification (08)')])

# ---------------- etiquette ----------------
ab('ab.courtly_grace', 'Courtly Grace', I + 'etiquette.courtly', 1, 'court_manner', 'Exception', 'passive',
   'Carry yourself so that rank does not close a door.',
   'Applies to Talk beats in formal settings with those above your station.',
   [rk("The snag for addressing someone above your station is waived.",
       [waive('the snag for a difference in rank or station', 'you Talk in a formal setting')]),
    rk("The snag for addressing someone above your station is waived, and you gain +1 to Talk beats in formal settings.",
       [waive('the snag for a difference in rank or station', 'you Talk in a formal setting'), edge(1, 'verb = verb.talk and the setting is formal')]),
    rk("The snag for addressing someone above your station is waived, you gain +1 to Talk beats in formal settings, and those beats are framed one stakes rung lower.",
       [waive('the snag for a difference in rank or station', 'you Talk in a formal setting'), edge(1, 'verb = verb.talk and the setting is formal'), stakes('verb = verb.talk and the setting is formal')])],
   x=[('a rank you do not hold', 'ranks are ch.11\'s; grace is not a seat')])

ab('ab.foreign_manner', 'Foreign Manner', I + 'etiquette.foreign', 3, 'adapt_custom', 'Exception', 'passive',
   'Take on the customs of a people as you meet them.',
   'Applies among a people whose customs you have watched for at least a day.',
   [rk("Among a people you have watched for a day, the snag for being an outsider is waived and you gain +1 to Talk beats with them.",
       [waive('the snag for being an outsider to a people\'s customs', 'you have watched them for a day'), edge(1, 'verb = verb.talk and the listener is of that people')]),
    rk("Among a people you have watched for a day, the snag for being an outsider is waived and you gain +2 to Talk beats with them.",
       [waive('the snag for being an outsider to a people\'s customs', 'you have watched them for a day'), edge(2, 'verb = verb.talk and the listener is of that people')])],
   x=[('their language', 'ab.gift_of_tongues; lic.lang.*')])

# ---------------- insight ----------------
ab('ab.read_the_heart', 'Read the Heart', I + 'insight.motives', 1, 'read_person', 'Working', 'beat',
   'See what someone wants from how they stand and speak.',
   'Applies to one being with a mind that you have watched or spoken with for a few moments.',
   [rk("Read a person (Observe, Wits, against their Presence defense). On a success learn one thing they want or their present mood, and hold it as a Precision lever on your next Talk with them.",
       [rev('one want or the present mood of the person'), lev('precision', 'your next Talk beat with the person')]),
    rk("Read a person (Observe, Wits, against their Presence defense). On a success learn one thing they want and one thing they will refuse, and hold that as a Precision lever on your next Talk with them.",
       [rev('one want of the person'), rev('one refusal of the person'), lev('precision', 'your next Talk beat with the person')]),
    rk("Read a person (Observe, Wits, against their Presence defense). On a success learn one thing they want and one thing they will refuse, and hold that as a Precision lever on Talk with them until the scene ends.",
       [rev('one want of the person'), rev('one refusal of the person'), lev('precision', 'Talk beats with the person', 'scene', verbs=['verb.talk'])])],
   attr='wits', check=('aimed', 'verb.observe', "the person's Presence defense"), x=[('their thoughts', 'no pool ability reads a mind'), ('their secrets', 'sealed; investigation (15)')])

ab('ab.lie_sense', 'Ear for a Lie', I + 'insight.lies', 2, 'detect_lie', 'Edge', 'passive',
   'Hear the catch in a false statement.',
   'Applies to Observe beats that test whether a speaker is lying.',
   [rk("+1 to Observe beats that test whether a speaker is lying.",
       [edge(1, 'deed_tag under deed.influence.insight.lies')]),
    rk("+2 to Observe beats that test whether a speaker is lying.",
       [edge(2, 'deed_tag under deed.influence.insight.lies')])],
   x=[('certainty without a check', 'ab.discern'), ('an honest speaker who is wrong', 'they are not lying')])

# ---------------- teaching ----------------
ab('ab.patient_teacher', 'Patient Teacher', I + 'teaching.instruction', 1, 'instruct', 'Edge', 'passive',
   'Pass a skill on faster than it was passed to you.',
   'Applies to learning clocks of pupils you mentor through a full training week.',
   [rk("A learning clock you mentor ticks one segment more each training week.",
       [tick('a learning clock you mentor', 1)]),
    rk("A learning clock you mentor ticks one segment more each training week, and so does a training-license clock you mentor; a pupil holds a Precision lever the first time they use what you taught.",
       [tick('a learning clock you mentor', 1), tick('a training-license clock you mentor', 1), lev('precision', "a pupil's first use of what you taught")]),
    rk("A learning clock you mentor ticks one segment more each training week, and so does a training-license clock you mentor; a pupil holds a Precision lever the first time they use what you taught; and you gain +1 when you Help someone with a thing you taught them.",
       [tick('a learning clock you mentor', 1), tick('a training-license clock you mentor', 1), lev('precision', "a pupil's first use of what you taught"), edge(1, 'verb = verb.help and the one helped is your pupil in that tag')])],
   x=[('teaching what you do not hold', 'lic.call.proof and the ability itself are required (05.8.5)')])

ab('ab.lend_the_art', 'Lend the Art', I + 'teaching.mentoring', 5, 'lend_skill', 'Working', 'beat',
   'Walk another through a thing they have never learned.',
   'Applies to up to two willing allies within band.close whom you instruct for an interval, in one training license you hold.',
   [rk("After an interval of instruction, up to two willing allies hold one training license of yours at the trained grade until the scene ends, with +1 to beats under it and a Precision lever on them, and without the improvised DC shift.",
       [glic('one training license you hold', 'trained', 'scene', big=True), edge(1, 'beats under the lent license'), lev('precision', 'beats under the lent license', 'scene'), waive('the crude-fallback DC shift for the lent license\'s methods', 'the license is lent'), tgt(1)], f=2, per='scene_end')],
   traits=['trait.action.speech'], x=[('lending an ability or a spell', 'abilities are held, not lent; 05.8.5 teaches them'), ('the expert or master grade', 'only a calling\'s tier gives those (05.9.2)')])
