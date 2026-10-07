# ab_deep.py -- the tier-4 and tier-5 depth of the tag-gated pool [revision: I-087].
# Every level-2 deed node that callings pick from gets at least one min_tier-4 and one min_tier-5 ability, so that a
# narrow calling's own pool can deepen its art at tiers 4 and 5 instead of drawing those picks from kin arts (04.8.4).
# Before this file, 61 of 81 level-2 nodes had no min_tier-4 ability and 62 had no min_tier-5 ability (C2b's POOLS
# audit counted 43 with neither). One rank each (MAX_RANKS 4 and 5 = 1); every row is priced by gen_data05.py's
# budget (05.11, T-05-9) like the rest of the pool. Grouped by branch, then by level-2 node.
from dsl05 import *

FOE = 'the target of the Strike'
T = 'the target'
RES = ('resisted', 'endure', 'resolve')
END = ('resisted', 'endure', 'endurance')
EVA = ('resisted', 'evade', 'agility')
ATK = ('aimed', 'verb.strike', "the target's attack defense")
STRIKE = dict(verbs=['verb.strike'], traits=['trait.action.attack', 'trait.delivery.melee'])
SHOT = dict(verbs=['verb.strike'], traits=['trait.action.attack', 'trait.delivery.ranged'])

# ====================================================================== deed.lore
Lr = 'deed.lore.'
ab('ab.call_the_flaw', 'Call the Flaw', Lr + 'arcana.theory', 4, 'flaw_call', 'Reaction', 'reaction',
   'Name aloud the weak joint of a working as it is made.',
   'Applies to a working you can perceive being cast at you or at an ally within band.near who can hear you.',
   [rk("When a working is cast at you or an ally within band.near, call its flaw: the check to resist it is +2 and framed one stakes rung lower, and you learn who cast it.",
       [edge(2, 'the check resists the named working'), stakes('the check resists the named working'), rev('the caster of the working')], f=1, per='scene_end')],
   hook='on_declare', when='a working you can perceive is cast at you or an ally within band.near',
   x=[('breaking the working', 'ab.counterspell; ab.unbinding'), ('a working you cannot perceive', 'verb.endure')])

ab('ab.whole_weave', 'The Whole Weave', Lr + 'arcana.planes', 5, 'weave_reading', 'Working', 'beat',
   'Read every working that holds a place, and who laid it.',
   'Applies to a place within band.near of you that you study for an interval.',
   [rk("Study a place for an interval (Recall, Intellect, against the tier of its strongest working). On a success learn every working active there, who laid each one and how long each will last; you and your allies hold a Precision lever on beats against those workings this scene and +1 to checks that resist them; your next Recall about them has reach one rung higher; and the place is recorded as read by you.",
       [rev('every working active at the place'), rev('the caster of each working'), rev('the remaining duration of each working'), lev('precision', 'beats against those workings', 'scene'), edge(1, 'the check resists a working you have read here'), reach('your next Recall about those workings'), fact('the place', 'read_by', 'the pc')], f=3, per='scene_end')],
   attr='intellect', check=('aimed', 'verb.recall', "the tier of the place's strongest working"),
   x=[('ending a working', 'ab.unbinding; ab.cleansing_rite'), ('workings beyond band.near', 'ab.spell_sight on each')])

ab('ab.old_enemy', 'Old Enemy', Lr + 'bestiary.monsters', 4, 'sworn_foe_lore', 'Edge', 'passive',
   'Fight a kind you know as if you had fought it before.',
   'Applies against a creature of a kind at least one of whose tells you have learned.',
   [rk("Against a creature whose tell you know: +1 Agility defense against its attacks, +1 harm on your Strikes against it, and +1 to checks that resist its effects.",
       [dedge(1, 'agility', 'the attacker is a creature whose tell you know'), hedge(1, 'a Strike against a creature whose tell you know'), edge(1, 'the check resists an effect of a creature whose tell you know')])],
   x=[('a kind whose tells you have not learned', 'ab.know_the_beast'), ('folk', 'ab.read_the_field')])

ab('ab.bane_known', 'The Bane Known', Lr + 'bestiary.dragons', 5, 'bane_lore', 'Working', 'beat',
   'Name the one thing a great creature cannot withstand.',
   'Applies to one creature you can perceive whose threat band is at or above your power band.',
   [rk("Name the creature's bane (Recall, Intellect, against the tier of its threat band). The beat's reach is one rung higher; on a success learn two of its tells, its resistance to one harm branch does not apply this scene, and you and up to two allies who hear you hold a Precision lever and an Amplifying lever against it this scene.",
       [reach('this beat'), rev("one tell of the creature's stat block"), rev("a second tell of the creature's stat block"), waive("the creature's resistance to one harm branch you name", 'this scene'), lev('precision', 'beats against the creature', 'scene'), lev('amplifying', 'beats against the creature', 'scene'), tgt(2)], f=3, per='scene_end')],
   attr='intellect', check=('aimed', 'verb.recall', "the tier of the creature's threat band"),
   x=[('a creature below your band', 'ab.know_the_beast'), ('its numbers', 'sealed (09)')])

ab('ab.siege_reckoner', 'Siege Reckoner', Lr + 'engineering.siegecraft', 4, 'siege_reckoning', 'Working', 'beat',
   'Find where a wall, gate or engine will fail first.',
   'Applies to one fortification, gate, bridge or engine you can study for an interval.',
   [rk("Study a structure for an interval (Observe, Intellect, against its tier). On a success learn its weakest point; the siege or breaching clock against it ticks by your delivered reach; and beats against it by you and your allies hold a Precision lever this scene, have reach one rung higher and are framed one stakes rung lower.",
       [rev("the structure's weakest point"), tick('the siege or breaching clock against the structure', 'delivered_reach'), lev('precision', 'beats against the structure', 'scene'), reach('beats against the structure this scene'), stakes('beats against the structure this scene')], f=2, per='scene_end')],
   attr='intellect', check=('aimed', 'verb.observe', "the structure's tier"),
   x=[('bringing it down yourself', 'ab.breach'), ('a living defender', 'ab.read_the_field')])

ab('ab.great_works', 'Great Works', Lr + 'engineering.waterworks', 5, 'great_plan', 'Working', 'beat',
   'Lay out the plan that lets a great work be built sound.',
   'Applies to one project of building, digging, damming or engineering that you direct.',
   [rk("Lay out the plan of a work you direct (Recall, Intellect, against the work's tier). On a success its project clock ticks by your delivered reach; every helper's beat on it this scene holds a Precision lever and +1; your own beats on it have reach one rung higher; one cost that a setback would put on the work this scene does not apply; you learn its one hidden flaw; and the work is recorded as built sound.",
       [tick("the work's project clock", 'delivered_reach'), lev('precision', "helpers' beats on the work", 'scene'), edge(1, "a helper's beat on the work this scene"), reach('your beats on the work this scene'), waive('one cost a setback puts on the work', 'this scene'), rev("the work's hidden flaw"), fact('the work', 'built_sound', True)], f=3, per='scene_end')],
   attr='intellect', check=('aimed', 'verb.recall', "the work's tier"),
   x=[('the labor itself', 'the work needs its hands and materials (08)'), ('a work begun by another and badly laid', 'ab.find_the_flaw first')])

ab('ab.ruin_reader', 'Ruin-Reader', Lr + 'history.ruins', 4, 'ruin_reading', 'Edge', 'passive',
   'Walk an old place as its builders walked it.',
   'Applies to beats in a ruin, tomb or abandoned site whose builders are of a people you know.',
   [rk("+1 to beats in a ruin of a known people, your Observe there has reach one rung higher, and each success ticks the site's exploration clock one segment more.",
       [edge(1, 'the beat is in a ruin of a people you know'), reach('verb = verb.observe in a ruin of a people you know'), tick("the site's exploration clock", 1)])],
   x=[('a site of a people no lore records', 'the Oracle; exploration (10)')])

ab('ab.long_memory', 'The Long Memory', Lr + 'history.legends', 5, 'long_memory', 'Working', 'beat',
   'Bring the whole past of a people to bear on the present.',
   'Applies to one people, place, house or relic you can name.',
   [rk("Recall the history of a people, place, house or relic (Recall, Intellect, against Hard). The beat's reach is one rung higher; on a success learn one sealed fact about its past and one about whoever now holds or rules it; you and up to two allies hold a Precision lever on beats that concern it this scene; your Talk with its people holds an Amplifying lever this scene; and you are recorded as one who knows their history.",
       [reach('this beat'), rev('one sealed fact about its past'), rev('one sealed fact about its present holder'), lev('precision', 'beats that concern it', 'scene'), tgt(2), lev('amplifying', 'Talk beats with its people', 'scene', verbs=['verb.talk']), fact('the pc', 'knows_history_of', 'the subject')], f=2, per='rest_long')],
   attr='intellect', check=('aimed', 'verb.recall', 'obstacle tier hard'),
   x=[('facts the world has never recorded', 'the Oracle; investigation (15)')])

ab('ab.paper_trail', 'Paper Trail', Lr + 'investigation.records', 4, 'record_search', 'Working', 'beat',
   'Follow a name or a sum through the records that hold it.',
   'Applies to an archive, ledger store, registry or court roll you can search for an interval.',
   [rk("Search records for an interval (Observe, Intellect, against the archive's tier). The beat's reach is one rung higher; on a success learn two records that link to your subject; the inquiry's clue clock ticks by your delivered reach; and you hold a Precision lever on Talk with the people those records name this scene.",
       [reach('this beat'), rev('a record that links to the subject'), rev('a second linked record'), tick("the inquiry's clue clock", 'delivered_reach'), lev('precision', 'Talk beats with those the records name', 'scene', verbs=['verb.talk'])], f=2, per='scene_end')],
   attr='intellect', check=('aimed', 'verb.observe', "the archive's tier"),
   x=[('a record that was never written', 'the clue graph (15)'), ('reading a cipher', 'ab.cipher_breaker')])

ab('ab.dead_tongues', 'Dead Tongues', Lr + 'languages.ancient', 4, 'dead_tongue', 'Permission', 'beat',
   'Read a language no one living speaks.',
   'Applies to one dead or ancient script you can study for an interval.',
   [rk("After an interval with a dead or ancient text, hold its language at the accented grade until your next long rest; your reading of it has reach one rung higher, and you learn one thing the text conceals or implies.",
       [glic('lic.lang.<the ancient language>', 'accented', 'until_rest:rest_long', big=True), reach('the beat reads the ancient text'), rev('one thing the text conceals')], f=1)],
   attr='intellect', x=[('speaking it to the living', 'no one living answers; ab.gift_of_tongues for living tongues'), ('a text sealed by a ward', '05.7.7')])

ab('ab.tongue_of_all', 'Tongue of All Peoples', Lr + 'languages.translation', 5, 'all_tongues', 'Permission', 'beat',
   'Speak to any people as one of their own.',
   'Applies to living languages whose speakers you have heard for at least a minute.',
   [rk("After a minute among its speakers, hold a language at the accented grade until your next long rest, without the crude-fallback DC shift; your Talk with its speakers is +1 and holds an Amplifying lever this scene; and you may interpret for up to two allies, who hold it at the broken grade this scene.",
       [glic('lic.lang.<the language>', 'accented', 'until_rest:rest_long', big=True), waive('the crude-fallback DC shift for speaking a language not held', 'you speak that language'), edge(1, 'a Talk beat with its speakers'), lev('amplifying', 'Talk beats with its speakers', 'scene', verbs=['verb.talk']), glic('lic.lang.<the language>', 'broken', 'scene'), tgt(1)], f=2, per='rest_long')],
   attr='intellect', x=[('a dead language', 'ab.dead_tongues'), ('holding the language permanently', 'its acquisition paths (a project clock)')])

ab('ab.lawful_claim', 'Lawful Claim', Lr + 'law.custom', 4, 'lawful_claim', 'Lever', 'rider',
   'Hold an authority to the law it claims to keep.',
   'Applies to a Talk beat with an official, lord or arbiter whose authority rests on a law or custom you can cite.',
   [rk("On a Talk beat with an authority, cite its own law or custom: a Precision lever and an Amplifying lever on this beat, its stakes are one rung lower, the authority cannot simply refuse you this scene without breaking that law openly, and your claim is recorded.",
       [lev('precision', 'this beat'), lev('amplifying', 'this beat'), stakes('this beat'), restr({'methods': ['refusing the claim without breaking its own law']}, 'the authority', 'scene'), fact('the claim', 'on_record_with', 'the authority')], f=1, per='scene_end')],
   verbs=['verb.talk'], x=[('an authority that keeps no law', 'ab.leverage; verb.talk'), ('a formal trial', 'ab.unanswerable_case')])

ab('ab.snatched_back', 'Snatched Back', Lr + 'medicine.diagnosis', 5, 'save_the_dying', 'Working', 'beat',
   'Bring a dying body back from the edge with hands and knife.',
   'Applies to one dying or bloodied living being within band.engaged; each being once between its long rests.',
   [rk("Work on a dying or bloodied being for an action: it is stabilized, regains 8 Vitality, its bleeding and its poisoning end, its worst wound counts one rung lighter for recovery, and it holds a Protective lever on its checks until the scene ends.",
       [cleanse('the dying state (07)', 'the tended being'), heal(8, 'the tended being'), cleanse('cond.bleeding', 'the tended being'), cleanse('cond.poisoned', 'the tended being'), fact("the tended being's worst wound", 'recovers_as', 'one rung lighter'), lev('protective', "the tended being's checks", 'scene')], f=3, per='scene_end')],
   attr='intellect', oc=1, cost_text="one use of a healer's kit (08)",
   x=[('a being already dead', 'ab.breath_of_life; rit.raise_shade'), ('a curse or a disease', "ab.masters_remedy; ab.lift_the_hex")])

ab('ab.guest_of_altars', 'Guest of Every Altar', Lr + 'religion.pantheon', 5, 'altar_guest', 'Working', 'beat',
   'Walk among any faith as one who knows its law.',
   'Applies to one faith, order or cult whose servants or holy place you are among.',
   [rk("Name the rites and taboos of a faith present (Recall, Intellect, against Hard). The beat's reach is one rung higher; on a success learn its taboos and the standing of its local servants; your Talk with its faithful holds a Precision lever and an Amplifying lever this scene; those who honor it may not strike you this scene unless you strike first; and you are recorded as a guest of that faith.",
       [reach('this beat'), rev("the faith's taboos"), rev("the standing of the faith's local servants"), lev('precision', 'Talk beats with its faithful', 'scene', verbs=['verb.talk']), lev('amplifying', 'Talk beats with its faithful', 'scene', verbs=['verb.talk']), restr({'methods': ['attacking the pc unless the pc attacks first']}, 'those who honor the faith', 'scene'), fact('the pc', 'guest_of', 'the faith')], f=3, per='scene_end')],
   attr='intellect', check=('aimed', 'verb.recall', 'obstacle tier hard'),
   x=[('a faith whose servants are already hostile to you', 'verb.talk; ab.word_as_bond'), ('sacred power', 'deed.divine')])

# ====================================================================== deed.martial
M = 'deed.martial.'
ab('ab.through_the_gap', 'Through the Gap', M + 'archery.bow', 4, 'gap_shot', 'Working', 'rider',
   'Find the narrow way past a shield or a wall.',
   'Applies to a ranged Strike with a bow against a target within band.far that you can see.',
   [rk("Your shot ignores the target's cover: it loses flag.in_cover for this Strike, takes harm one severity rung heavier, +2, and is bleeding until the scene ends.",
       [move(T, 0, rem=['flag.in_cover']), sev(1, 'this Strike'), hedge(2, 'this Strike'), cond('cond.bleeding', 1, 'scene', FOE)], f=2)],
   x=[('total cover', 'it cannot be seen; ab.volley at an area'), ('a thrown weapon', 'deed.martial.thrown')], **SHOT)

ab('ab.long_shot', 'The Long Shot', M + 'archery.crossbow', 5, 'long_shot', 'Working', 'beat',
   'Kill at a distance no one thought a bolt could carry.',
   'Applies to one target you can see within band.distant, after you take a full breath to aim.',
   [rk("Take aim and loose at a target within band.distant without the long-range DC shift (Strike, Agility, against its attack defense). On a success it takes Grievous harm of your missile's type and is stunned until the end of its next turn, and if you were hidden you stay hidden.",
       [waive('the DC shift for a shot at band.distant', 'this beat'), harm(4, ["the missile's harm type"], T), cond('cond.stunned', 2, 'rounds:1', T), move('self', 0, add=['flag.hidden']), lev('precision', 'this beat')], f=3, per='scene_end')],
   attr='agility', check=ATK, x=[('a target you cannot see', 'verb.observe first'), ('a foe engaged with you', 'verb.strike')], **SHOT)

ab('ab.iron_mountain', 'Iron Mountain', M + 'armor.encumbered', 5, 'iron_mountain', 'Form', 'rider',
   'Stand in heavy armor as a hill stands in the wind.',
   'Applies while you wear heavy armor and have not moved more than one band this turn.',
   [rk("Take the stance: until it ends, physical harm against you is reduced by 2, you cannot be knocked prone or put off-balance, and you hold a Protective lever on your beats.",
       [stance('iron_mountain', [red(2, ['harm.physical']), immune(['cond.prone', 'cond.off_balance']), lev('protective', 'your beats', 'scene')])], f=2)],
   slot='slot.stance', verbs=['any'], x=[('light or no armor', 'ab.armored_ease'), ('a blow that would fell you', 'ab.bulwark')])

ab('ab.tumblers_grace', "Tumbler's Grace", M + 'athletics.acrobatics', 4, 'tumble', 'Exception', 'passive',
   'Roll, vault and fall as if the ground were soft.',
   'Applies while you are unarmored or in light armor.',
   [rk("Moving through a foe's band provokes no reaction from it, and falls count one severity rung lower for you.",
       [waive("the reaction a foe's band provokes when you move through it", 'you move through it'), hazard(['harm.physical.crush'])])],
   x=[('medium or heavy armor', 'ab.armored_ease'), ('flying', 'a movement mode (05.4.6)')])

ab('ab.strength_of_legend', 'Strength of Legend', M + 'athletics.lifting', 5, 'legend_feat', 'Permission', 'beat',
   'Do once what the songs say no body can do.',
   'Applies to one feat of lifting, breaking, holding, leaping or swimming, once between long rests.',
   [rk("Attempt a feat beyond a body's measure: lift a portcullis, hold a door against a ram, leap a gap of band.near (Exert, Might, at +2). The beat's reach is one rung higher and its stakes one rung lower; one ally beside you shares the effort and its outcome; and you are not exhausted by it.",
       [perm(4), edge(2, 'this beat'), reach('this beat'), stakes('this beat'), tgt(1), immune(['cond.exhausted'])], f=2, per='rest_long')],
   attr='might', check=('aimed', 'verb.exert', "the feat's tier"),
   x=[('harming a foe', 'verb.strike; ab.mighty_heave'), ('a feat a team could do with time', 'verb.help; a project clock')])

ab('ab.bearded_hook', 'Bearded Hook', M + 'axe.hand', 4, 'axe_hook', 'Working', 'rider',
   'Catch a foe on the beard of your axe and haul.',
   'Applies to a Strike with a hand axe against a foe engaged with you.',
   [rk("Your Strike hooks the foe: pull it one band or drag its shield aside; it is knocked prone and off-balance until the end of its next turn, and takes +2 harm.",
       [move(FOE, 1), cond('cond.prone', 1, 'rounds:1', FOE), cond('cond.off_balance', 1, 'rounds:1', FOE), hedge(2, 'this Strike')], f=1)],
   x=[('a foe larger than you by two sizes', 'verb.grapple'), ('a two-handed axe', 'ab.sunder')], **STRIKE)

ab('ab.red_harvest', 'Red Harvest', M + 'axe.great', 5, 'harvest_swing', 'Working', 'beat',
   'Swing a great axe through every foe that stands near you.',
   'Applies to up to four foes engaged with you, with a two-handed axe.',
   [rk("Swing through every foe engaged with you, up to four (Strike, Might, against each one's attack defense). Each one hit takes your axe's harm one rung heavier, is bleeding until the scene ends and is knocked prone; each foe that sees it is frightened until the scene ends.",
       [harmw(1, 'each foe hit'), tgt(3), cond('cond.bleeding', 1, 'scene', 'each foe hit'), cond('cond.prone', 1, 'rounds:1', 'each foe hit'), cond('cond.frightened', 1, 'scene', 'each foe that sees the swing')], f=3, per='scene_end')],
   attr='might', check=ATK, spread='burst',
   x=[('sparing a foe within reach', 'every foe engaged with you is struck'), ('a hand axe', 'ab.bearded_hook')], **STRIKE)

ab('ab.inside_the_guard', 'Inside the Guard', M + 'blade.dagger', 4, 'inside_guard', 'Working', 'rider',
   'Slip a short blade in where a long one cannot reach.',
   'Applies to a Strike with a dagger or knife against a foe engaged with you that holds a longer weapon, or that you hold grabbed.',
   [rk("Your Strike deals harm two severity rungs heavier, +2, and the foe is bleeding until the scene ends.",
       [sev(2, 'this Strike'), hedge(2, 'this Strike'), cond('cond.bleeding', 1, 'scene', FOE)], f=2)],
   x=[('a foe with a dagger of its own', 'verb.strike'), ('a foe beyond band.engaged', 'deed.martial.thrown')], **STRIKE)

ab('ab.ring_the_bell', 'Ring the Bell', M + 'bludgeon.mace', 5, 'bell_ringer', 'Working', 'rider',
   "Bring a mace down on a foe's helm so its head rings.",
   'Applies to a Strike with a mace, flail or club against a foe engaged with you.',
   [rk("Your Strike deals harm one severity rung heavier, +1; the foe is stunned until the end of its next turn and dazed until the scene ends.",
       [sev(1, 'this Strike'), hedge(1, 'this Strike'), cond('cond.stunned', 2, 'rounds:1', FOE), cond('cond.dazed', 1, 'scene', FOE)], f=2, per='scene_end')],
   x=[('a foe with no head or no mind (oozes, constructs)', 'ab.shatter_guard'), ('a foe beyond band.engaged', 'verb.strike')], **STRIKE)

ab('ab.ride_and_wheel', 'Ride and Wheel', M + 'mounted.skirmish', 4, 'ride_wheel', 'Working', 'rider',
   'Strike from the saddle and be gone before the answer.',
   'Applies to a Strike made while you hold flag.mounted.',
   [rk("After your Strike, move one band away without provoking a reaction; the target is off-balance until the end of its next turn and takes +1 harm, and you hold a Precision lever on your next Strike against it.",
       [move('self', 1), waive('the reaction your move away provokes', 'this turn'), cond('cond.off_balance', 1, 'rounds:1', FOE), hedge(1, 'this Strike'), lev('precision', 'your next Strike against the target', 'rounds:1', verbs=['verb.strike'])], f=1)],
   x=[('fighting on foot', 'ab.smoke_and_gone'), ('a charge', 'ab.lance_charge')], **STRIKE)

ab('ab.ride_them_down', 'Ride Them Down', M + 'mounted.charge', 5, 'trample', 'Working', 'rider',
   'Drive a mount straight through a line of foes.',
   'Applies to a Strike made while you hold flag.mounted, against up to three foes in a line within band.near.',
   [rk("Ride through up to three foes in a line: each takes your weapon's harm and is knocked prone; you end one band beyond them; each foe that sees it is frightened until the scene ends.",
       [harmw(0, 'each foe in the line'), tgt(2), cond('cond.prone', 1, 'rounds:1', 'each foe in the line'), move('self', 2), cond('cond.frightened', 1, 'scene', 'each foe that sees the charge')], f=2, per='scene_end')],
   spread='pierce', x=[('a mount too small to bear down a folk-sized foe', 'ab.lance_charge'), ('foes in cover', 'they are not in the line')], **STRIKE)

ab('ab.hook_and_haul', 'Hook and Haul', M + 'polearm.halberd', 4, 'halberd_hook', 'Working', 'rider',
   'Drag a rider from the saddle or a foe from its place.',
   'Applies to a Strike with a halberd, glaive or bill against a foe within your weapon\'s reach.',
   [rk("Your Strike hooks the foe: pull it one band and strip flag.mounted from it; it is knocked prone and takes harm one severity rung heavier, +2.",
       [move(FOE, 1, rem=['flag.mounted']), cond('cond.prone', 1, 'rounds:1', FOE), sev(1, 'this Strike'), hedge(2, 'this Strike')], f=2)],
   x=[('a spear or staff', 'ab.set_spear; ab.long_guard'), ('a foe two sizes larger', 'verb.grapple')], **STRIKE)

ab('ab.hedge_of_points', 'Hedge of Points', M + 'polearm.spear', 5, 'stance_points', 'Form', 'rider',
   'Make the ground before you a hedge no foe crosses whole.',
   'Applies while you hold a spear or polearm and do not move more than one band in a turn.',
   [rk("Take the stance: until it ends, a foe that comes within band.engaged of you takes your weapon's harm and its movement stops there; you have +1 Agility defense; and allies behind you hold a Protective lever on their beats.",
       [stance('hedge_of_points', [harmw(0, 'a foe that comes within band.engaged of you'), restr({'methods': ['moving further this turn']}, 'that foe', 'rounds:1'), dedge(1, 'agility', 'the stance holds'), lev('protective', 'beats by allies behind you', 'scene')])], f=2)],
   slot='slot.stance', verbs=['any'], x=[('a foe that flies over you', 'it does not come through'), ('a charge you see coming', 'ab.set_spear')])

ab('ab.boss_and_rim', 'Boss and Rim', M + 'shield.bash', 4, 'shield_rush', 'Working', 'rider',
   'Drive a shield into a foe and put it down.',
   'Applies to a Strike with a shield against a foe engaged with you.',
   [rk("Your shield blow pushes the foe one band, knocks it prone and dazes it until the end of its next turn; you hold a Precision lever on your next Strike against it.",
       [move(FOE, 1), cond('cond.prone', 1, 'rounds:1', FOE), cond('cond.dazed', 1, 'rounds:1', FOE), lev('precision', 'your next Strike against the foe', 'rounds:1', verbs=['verb.strike'])], f=1)],
   x=[('a foe two sizes larger', 'verb.force'), ('blocking', 'ab.shield_block')], **STRIKE)

ab('ab.roof_of_shields', 'Roof of Shields', M + 'shield.cover', 5, 'shield_roof', 'Reaction', 'reaction',
   'Throw your shield over the ones a volley is falling on.',
   'Applies to a hit from a ranged attack or an area working on an ally within band.near, while you hold a shield.',
   [rk("When an ally within band.near is hit by a missile or an area working, step to it and take the blow on your shield: negate that hit; until your next turn up to three allies beside you hold flag.in_cover and you have +1 Agility defense.",
       [prevent('an ally within band.near is hit by a ranged attack or an area working'), move('self', 1), move('up to three allies beside you', 0, add=['flag.in_cover']), tgt(2), dedge(1, 'agility', 'until your next turn')], f=2, per='scene_end')],
   hook='on_attack_hit', when='an ally within band.near is hit by a ranged attack or an area working',
   x=[('a melee blow', 'ab.shield_wall'), ('yourself alone', 'ab.shield_block')])

ab('ab.hammer_and_anvil', 'Hammer and Anvil', M + 'tactics.battle', 4, 'flank_call', 'Working', 'beat',
   'Call the move that closes a foe between two forces.',
   'Applies to one foe within band.near and up to three allies who can hear you.',
   [rk("Call the maneuver: up to three allies move one band; the foe is flanked and exposed until the scene ends; and your allies' Strikes against it are +1 and hold a Precision lever this round.",
       [move('up to three allies who hear you', 1), tgt(2), move(T, 0, add=['flag.flanked']), cond('cond.exposed', 1, 'scene', T), edge(1, "an ally's Strike against the foe this round"), lev('precision', "allies' Strikes against the foe", 'rounds:1')], f=2)],
   x=[('allies who cannot hear you', 'verb.help'), ('the whole battle', 'ab.commanding_ground')])

ab('ab.shield_breaker_throw', 'Shield-Breaker Throw', M + 'thrown.javelin', 4, 'javelin_bite', 'Working', 'rider',
   "Pin a foe's shield with a javelin so it is dead weight.",
   'Applies to a thrown Strike with a javelin or spear against a target within band.far.',
   [rk("Your throw deals harm one severity rung heavier, +2; the target is off-balance until the end of its next turn and cannot use its shield until the scene ends.",
       [sev(1, 'this Strike'), hedge(2, 'this Strike'), cond('cond.off_balance', 1, 'rounds:1', FOE), restr({'methods': ['using its shield']}, FOE, 'scene')], f=2)],
   x=[('a foe with no shield', 'the throw still harms; the restriction is empty'), ('knives', 'ab.rain_of_knives')], **SHOT)

ab('ab.rain_of_knives', 'Rain of Knives', M + 'thrown.blades', 5, 'knife_rain', 'Working', 'beat',
   'Empty a bandolier of knives into every foe near you.',
   'Applies to up to four foes within band.near, while you carry at least four throwing blades.',
   [rk("Throw at up to four foes within band.near, even while engaged and without provoking (Strike, Agility, against each one's attack defense). Each one hit takes your blade's harm, +2, is bleeding until the scene ends and distracted until the end of its next turn.",
       [harmw(0, 'each foe hit'), tgt(3), hedge(2, 'this beat'), cond('cond.bleeding', 1, 'scene', 'each foe hit'), cond('cond.distracted', 1, 'rounds:1', 'each foe hit'), waive('the reaction a ranged attack provokes while engaged', 'this beat')], f=3, per='scene_end')],
   attr='agility', check=ATK, spread='fork',
   x=[('foes beyond band.near', 'ab.throwers_eye'), ('a javelin', 'ab.shield_breaker_throw')], **SHOT)

ab('ab.nerve_strike', 'Nerve Strike', M + 'unarmed.striking', 4, 'nerve_strike', 'Working', 'rider',
   'Strike the place where a body keeps its strength.',
   'Applies to an unarmed Strike against a living foe engaged with you.',
   [rk("Your blow numbs the foe: it is weakened until the scene ends, dazed until the end of its next turn, cannot use one limb you name this scene, and takes +2 harm.",
       [cond('cond.weakened', 1, 'scene', FOE), cond('cond.dazed', 1, 'rounds:1', FOE), restr({'methods': ['using the named limb']}, FOE, 'scene'), hedge(2, 'this Strike')], f=2)],
   x=[('a foe with no nerves (constructs, undead, oozes)', 'ab.iron_palm'), ('a weapon in hand', 'verb.strike')], **STRIKE)

ab('ab.breaking_hold', 'The Breaking Hold', M + 'unarmed.wrestling', 5, 'breaking_hold', 'Working', 'beat',
   'Lock a foe so that every struggle costs it.',
   'Applies to one foe engaged with you no more than one size larger than you.',
   [rk("Seize a foe (Grapple, Might, against its attack defense). On a success it is pinned until the scene ends or it breaks your hold, takes Heavy crushing harm, and is choking until the end of its next turn; you hold it as cover, and its allies' attacks on you are framed against that cover.",
       [cond('cond.pinned', 2, 'scene', T), harm(3, ['harm.physical.crush'], T), cond('cond.choking', 1, 'rounds:1', T), move('self', 0, add=['flag.in_cover']), lev('protective', 'your beats while you hold it', 'scene')], f=3, per='scene_end')],
   attr='might', check=('aimed', 'verb.grapple', "the target's attack defense"), traits=['trait.action.attack', 'trait.delivery.melee'],
   x=[('a foe two sizes larger', 'ab.clinch_throw'), ('a foe with no body to hold (spirits, swarms)', 'it slips through')])

# ====================================================================== deed.guile
G = 'deed.guile.'
ab('ab.shot_from_nowhere', 'Shot From Nowhere', G + 'ambush.sniping', 4, 'unseen_shot', 'Working', 'rider',
   'Loose from hiding and stay hidden.',
   'Applies to a ranged Strike made while you hold flag.hidden.',
   [rk("Your shot from hiding deals harm one severity rung heavier, +2; you keep flag.hidden, and the target cannot tell where it came from and is distracted until the scene ends.",
       [sev(1, 'this Strike'), hedge(2, 'this Strike'), move('self', 0, add=['flag.hidden']), cond('cond.distracted', 1, 'scene', FOE)], f=2)],
   x=[('a target that already knows where you are', 'ab.aimed_shot'), ('a melee Strike', 'ab.backstab')], **SHOT)

ab('ab.long_con', 'The Long Con', G + 'deception.con', 5, 'long_con', 'Working', 'beat',
   'Plant a false belief so deep the mark guards it for you.',
   'Applies to one person you have spoken with across at least two scenes.',
   [rk("Close the con (Talk, Wits, against the mark's Wits defense). The beat's reach is one rung higher and its stakes one rung lower; on a success the mark holds one falsehood you choose as true and will not act against it this scene; you learn what the mark would do to protect it; your Talk with the mark holds a Precision lever and an Amplifying lever this scene; and the con's clock ticks by your delivered reach.",
       [reach('this beat'), stakes('this beat'), fact('the mark', 'believes', 'the falsehood'), restr({'methods': ['acting against the falsehood']}, 'the mark', 'scene'), rev('what the mark would do to protect the belief'), lev('precision', 'Talk beats with the mark', 'scene', verbs=['verb.talk']), lev('amplifying', 'Talk beats with the mark', 'scene', verbs=['verb.talk']), tick("the con's clock", 'delivered_reach')], f=3, per='scene_end')],
   attr='wits', check=('aimed', 'verb.talk', "the mark's Wits defense"), traits=['trait.action.speech'],
   x=[('a stranger', 'ab.plausible_lie'), ('a belief that contradicts what the mark sees', 'it breaks at once'), ('magical compulsion', 'ab.compel')],
   nmi=['that the mark is charmed or loses its will'])

ab('ab.perfect_papers', 'Perfect Papers', G + 'disguise.forgery', 4, 'forgery', 'Permission', 'beat',
   'Make a writ, seal or pass that passes every eye.',
   'Applies to one document, seal or token whose genuine form you have seen.',
   [rk("In an interval, forge a document, seal or token you have seen; those who check it roll Observe against your effect DC +2, and you learn whose authority the genuine one carries.",
       [perm(2), dcedge(2, 'someone checks the forgery'), rev('whose authority the genuine document carries')], f=1)],
   attr='intellect', check=('aimed', 'verb.handle', 'obstacle tier hard (stored as the forgery\'s effect DC)'),
   x=[('a document you have never seen', 'verb.handle at the crude fallback'), ('a magical seal', 'ab.bind_power')])

ab('ab.no_cell_holds', 'No Cell Holds', G + 'escape.breakout', 4, 'breakout', 'Working', 'beat',
   'Find the way out of any place built to keep you in.',
   'Applies to a cell, cage, locked room or guarded place you are held in, studied for an interval.',
   [rk("Study the place that holds you for an interval (Observe, Wits, against its tier). The beat's reach is one rung higher and its stakes one rung lower; on a success learn its weakest point, the escape clock ticks by your delivered reach, any grab or restraint on you ends, and you gain flag.hidden as you go.",
       [reach('this beat'), stakes('this beat'), rev("the holding place's weakest point"), tick('the escape clock', 'delivered_reach'), cleanse('cond.restrained or cond.grabbed', 'self'), move('self', 0, add=['flag.hidden'])], f=2, per='scene_end')],
   attr='wits', check=('aimed', 'verb.observe', "the holding place's tier"),
   x=[('bonds alone', 'ab.slip_free'), ('a ward that holds you', '05.7.7; ab.unbinding')])

ab('ab.like_smoke', 'Like Smoke', G + 'escape.bonds', 5, 'smoke_slip', 'Reaction', 'reaction',
   'Leave a grip or a blow holding nothing.',
   'Applies to a hit or a grab on you by a foe you can perceive.',
   [rk("When you are hit or grabbed, negate it: you were already gone. Move two bands, gain flag.hidden, and until the end of your next turn you cannot be grabbed or restrained.",
       [prevent('you perceive the attacker'), move('self', 2, add=['flag.hidden']), immune(['cond.grabbed', 'cond.restrained'])], f=2, per='scene_end')],
   hook='on_hit_taken', when='you perceive the attacker',
   x=[('an area effect', 'verb.evade'), ('bonds already on you', 'ab.slip_free')])

ab('ab.heartsbane', 'Heartsbane', G + 'poisoncraft.envenoming', 5, 'heartsbane', 'Working', 'rider',
   'Carry a poison that stops the heart by slow degrees.',
   'Applies to a Strike with a piercing or cutting weapon, using one dose of a strong poison you carry.',
   [rk("Your Strike carries the poison: a target it harms is poisoned (Heavy), weakened and exhausted until the scene ends, and takes +1 harm.",
       [cond('cond.poisoned', 3, 'scene', 'a target the Strike harms'), cond('cond.weakened', 1, 'scene', 'a target the Strike harms'), cond('cond.exhausted', 1, 'scene', 'a target the Strike harms'), hedge(1, 'this Strike')], f=2, per='scene_end')],
   verbs=['verb.strike'], oc=1, cost_text='one dose of a strong poison (08)', harm_tags=['harm.venom.poison'], traits=['trait.action.attack'],
   x=[('brewing the poison', 'lic.training.craft_alchemy'), ('a creature with no blood or breath', 'it does not take')])

ab('ab.ghost_in_the_house', 'Ghost in the House', G + 'stealth.infiltration', 4, 'infiltrate', 'Exception', 'passive',
   'Move through a guarded house as if you lived there.',
   'Applies inside a building or site whose guards are not yet alerted to you.',
   [rk("+1 to Sneak beats inside a guarded site, and the first failed Sneak there each scene ticks no alarm clock.",
       [edge(1, 'verb = verb.sneak inside a guarded site'), waive("the alarm-clock tick of the scene's first failed Sneak", 'inside a guarded site')])],
   x=[('a site already on alert', 'ab.vanish'), ('magical wards', '05.7.7')])

ab('ab.second_shadow', 'Second Shadow', G + 'stealth.shadowing', 5, 'shadowing', 'Working', 'beat',
   'Follow a person all day and be seen by no one.',
   'Applies to one being you can see, and its company, for one scene.',
   [rk("Take up the shadow of a being (Sneak, Agility, against its Wits defense). The beat's reach is one rung higher; for the scene you keep flag.hidden while you follow, and the being and its company roll Observe against your effect DC +2 to notice you; you learn where it goes and whom it meets; you hold a Precision lever on beats against it this scene; and the inquiry's clue clock ticks by your delivered reach.",
       [reach('this beat'), move('self', 0, add=['flag.hidden']), dcedge(2, 'the shadowed being or its company tries to notice you'), rev('where the being goes'), rev('whom the being meets'), lev('precision', 'beats against the being', 'scene'), tick("the inquiry's clue clock", 'delivered_reach')], f=3, per='scene_end')],
   attr='agility', check=('aimed', 'verb.sneak', "the being's Wits defense"),
   x=[('a being that is already watching for you', 'ab.vanish'), ('following into a warded place', '05.7.7')])

ab('ab.ways_under_the_wall', 'Ways Under the Wall', G + 'streetwise.smuggling', 4, 'smuggle', 'Permission', 'beat',
   'Move goods or people past a watch that is looking for them.',
   'Applies to one load of goods or up to six people you move past a watch, gate or customs post.',
   [rk("Move a load or a party past a watch (Sneak or Talk, Wits). The watch's checks to find it are against your effect DC +2; the beat's reach is one rung higher and its stakes one rung lower; and you learn the watch's schedule.",
       [perm(2), dcedge(2, 'the watch searches for the load or party'), reach('this beat'), stakes('this beat'), rev("the watch's schedule")], f=2, per='scene_end')],
   attr='wits', check=('aimed', 'verb.sneak', "the watch's tier (stored as the effect DC)"),
   x=[('a watch with magical sight', 'ab.veil'), ('selling what you move', 'ab.black_market')])

ab('ab.word_below', 'Word Below', G + 'streetwise.cant', 5, 'underworld_call', 'Working', 'beat',
   'Call on the whole underworld of a town at once.',
   'Applies in a town or city whose underworld knows your name.',
   [rk("Put out the word in cant (Talk, Wits, against Hard). The beat's reach is one rung higher; on a success the town's crooked folk send you a helper of threat band 2 for the scene, you learn who in the town means your party harm, your Talk with its criminals holds a Precision lever this scene, the inquiry or job clock ticks by your delivered reach, and the favor is recorded as owed by you.",
       [reach('this beat'), summ("a helper of the town's underworld, threat band 2", 2, 'scene', location='where you put out the word'), rev('who in the town means the party harm'), lev('precision', 'Talk beats with criminals of the town', 'scene', verbs=['verb.talk']), tick('the inquiry or job clock', 'delivered_reach'), fact('the pc', 'owes_favor_to', "the town's underworld")], f=3, per='scene_end')],
   attr='wits', check=('aimed', 'verb.talk', 'obstacle tier hard'), traits=['trait.action.speech'],
   x=[('a town where no one knows you', 'ab.word_on_the_street'), ('ordering a killing', 'the helper acts within its nature (12)')])

ab('ab.turn_the_trap', 'Turn the Trap', G + 'thievery.traps', 4, 'trap_turn', 'Working', 'beat',
   'Disarm a trap and set it again for those who follow.',
   'Applies to one trap you have found, within band.engaged.',
   [rk("Disarm a found trap (Handle, Agility, against its tier). On a success it does not go off for you, you learn its trigger and its maker, and you may reset it: the first foe to cross it takes Heavy harm of its kind and is restrained until the end of its next turn.",
       [waive('the trap going off', 'you disarm it'), rev("the trap's trigger and maker"), fact('the trap', 'reset_by', 'the pc'), harm(3, ["the trap's harm type"], 'the first foe to cross the reset trap'), cond('cond.restrained', 1, 'rounds:1', 'the first foe to cross the reset trap')], f=2, per='scene_end')],
   attr='agility', check=('aimed', 'verb.handle', "the trap's tier"),
   x=[('a trap you have not found', 'ab.keen_search first'), ('building a trap', 'ab.rig_trap')])

ab('ab.gone_from_the_hand', 'Gone From the Hand', G + 'thievery.sleight', 5, 'impossible_theft', 'Permission', 'beat',
   'Take a thing from a hand that is holding it.',
   'Applies to one object no larger than a sword held, worn or watched by a being within band.engaged.',
   [rk("Take a held or watched object (Sneak, Agility, against the holder's Wits defense). The beat's reach is one rung higher and its stakes one rung lower; on a success the object is yours, the holder does not notice its loss until the scene ends, and you hold a Precision lever on your next Sneak this scene.",
       [perm(4), reach('this beat'), stakes('this beat'), waive("the holder's notice of the loss", 'until the scene ends'), fact('the object', 'held_by', 'the pc'), lev('precision', 'your next Sneak beat', 'scene', verbs=['verb.sneak'])], f=3, per='scene_end')],
   attr='agility', check=('aimed', 'verb.sneak', "the holder's Wits defense"),
   x=[('an object bound to its holder by magic', '05.7.7'), ('a pocket', 'ab.light_fingers')])

# ====================================================================== deed.wilds
W = 'deed.wilds.'
ab('ab.eyes_aloft', 'Eyes Aloft', W + 'animals.falconry', 4, 'hawk_scout', 'Working', 'beat',
   'Send a trained hawk or hound ahead to see for you.',
   'Applies to a trained hawk, hound or ferret of yours that can reach the ground ahead within band.distant.',
   [rk("Send your trained animal ahead (Handle, Wits, against Moderate). On a success learn what waits ahead and where it lies; you and up to two allies hold a Precision lever on beats against what it found this scene; and the animal harries one foe there, who is distracted until the scene ends.",
       [rev('what waits ahead'), rev('where it lies'), lev('precision', 'beats against what the animal found', 'scene'), tgt(2), cond('cond.distracted', 1, 'scene', 'one foe the animal harries')], f=2, per='scene_end')],
   attr='wits', check=('aimed', 'verb.handle', 'obstacle tier moderate'),
   x=[('an untrained animal', 'ab.beast_at_heel'), ("speaking with it", 'ab.beast_speech')])

ab('ab.stampede', 'Stampede', W + 'animals.husbandry', 5, 'stampede', 'Working', 'beat',
   'Turn a herd into a flood of hooves.',
   'Applies to a herd or drove of animals you can reach, and up to five foes in its path within band.near.',
   [rk("Drive the herd at your foes (Handle, Presence, against Moderate). Up to five foes in its path roll Evade against your effect DC: on a failure each takes Heavy crushing harm, is knocked prone, is pushed one band and is frightened until the scene ends.",
       [fchk('evade'), harm(3, ['harm.physical.crush'], 'each foe in the path that fails'), tgt(4), cond('cond.prone', 1, 'rounds:1', 'each foe that fails'), move('each foe that fails', 1), cond('cond.frightened', 1, 'scene', 'each foe that fails')], f=3, per='scene_end')],
   attr='presence', check=EVA, spread='burst', traits=['trait.sense.loud'],
   x=[('a place with no herd', 'it needs the animals'), ('choosing which foes in the path are struck', 'the herd takes every one')])

ab('ab.lands_larder', "The Land's Larder", W + 'foraging.harvest', 5, 'great_harvest', 'Working', 'beat',
   'Gather from wild ground enough to keep a company whole.',
   'Applies to wild land you can work for an interval, for up to six beings.',
   [rk("Work the land for an interval (Observe, Wits, against the land's tier). On a success the provisioning clock ticks by your delivered reach; up to six beings regain 3 Vitality and their poisoning ends; you learn of one hidden spring, cache or herb-bed nearby; and hunger and thirst count one severity rung lower for the company until your next long rest.",
       [tick('the provisioning clock', 'delivered_reach'), heal(3, 'up to six beings'), tgt(5), cleanse('cond.poisoned', 'up to six beings'), rev('one hidden source nearby'), hazard(['harm.blight'])], f=2, per='rest_long')],
   attr='wits', check=('aimed', 'verb.observe', "the land's tier"),
   x=[('blighted or barren ground', 'ab.renewal; ch.10 terrain'), ('brewing a remedy', 'ab.wild_physic')])

ab('ab.star_road', 'Star Road', W + 'navigation.stars', 4, 'star_road', 'Exception', 'passive',
   'Never be lost under an open sky.',
   'Applies to wayfinding while you can see the sky at night or the sun by day.',
   [rk("Under an open sky you cannot become lost, your navigation beats are +1, and each success ticks the travel clock one segment more.",
       [waive('becoming lost on a failed navigation beat', 'you can see the sky'), edge(1, 'deed_tag under deed.wilds.navigation and you can see the sky'), tick('the travel clock', 1)])],
   x=[('underground or under cloud', 'ab.hidden_ways; ab.pathfinder')])

ab('ab.unfailing_road', 'The Unfailing Road', W + 'navigation.mapping', 5, 'unfailing_road', 'Working', 'beat',
   'Lead a company across a whole region by the surest way.',
   'Applies to one leg of travel you guide, for up to six beings.',
   [rk("Guide a leg of travel (Observe, Wits, against the region's tier). The beat's reach is one rung higher and its stakes one rung lower; the travel clock ticks by your delivered reach; encounters and hazards on the leg count one severity rung lower for up to six beings; and they hold a Precision lever on travel beats this leg.",
       [reach('this beat'), stakes('this beat'), tick('the travel clock', 'delivered_reach'), hazard(['harm.physical', 'harm.frost', 'harm.fire.heat']), tgt(5), lev('precision', 'travel beats on the leg', 'scene')], f=3, per='scene_end')],
   attr='wits', check=('aimed', 'verb.observe', "the region's tier (10)"),
   x=[('a place no road has crossed', 'ab.hidden_ways'), ('the sea', 'ab.storm_helm')])

ab('ab.keep_her_afloat', 'Keep Her Afloat', W + 'seafaring.boatwork', 4, 'hull_patch', 'Working', 'beat',
   'Patch, bail and rig a damaged vessel until it reaches harbor.',
   'Applies to one vessel you are aboard, worked for an interval.',
   [rk("Work the vessel for an interval (Handle, Wits, against its damage tier). On a success one gear cost on it does not apply, its repair clock ticks by your delivered reach, and the beat's reach is one rung higher; water and weather hazards count one severity rung lower for it, and the crew holds a Precision lever on its beats this scene.",
       [waive('one cost.gear on the vessel', 'this scene'), tick("the vessel's repair clock", 'delivered_reach'), reach('this beat'), hazard(['harm.physical.asphyxia', 'harm.storm']), lev('precision', "the crew's beats", 'scene')], f=2, per='scene_end')],
   attr='wits', check=('aimed', 'verb.handle', "the vessel's damage tier"),
   x=[('a vessel already sunk', 'verb.exert and ch.10'), ('steering through a storm', 'ab.storm_helm')])

ab('ab.fire_any_weather', 'Fire in Any Weather', W + 'survival.firecraft', 4, 'all_weather_fire', 'Exception', 'passive',
   'Make fire where rain and wind say there can be none.',
   'Applies in the wild, where any fuel is to be had.',
   [rk("You make fire in any weather without a check, and cold counts one severity rung lower for you and those at your fire.",
       [waive('the check to make fire in wet or wind', 'fuel is to be had'), hazard(['harm.frost.cold'])])],
   x=[('no fuel at all', 'ab.shelter_anywhere'), ('magical cold', 'ab.fire_shroud')])

ab('ab.weather_wise', 'Weather-Wise', W + 'survival.weathersense', 5, 'weather_wise', 'Working', 'beat',
   'Read the coming days in the sky and the land.',
   'Applies at the start of a day in the wild, for up to six beings.',
   [rk("Read the sky and the land (Observe, Wits, against Moderate). The beat's reach is one rung higher and its stakes one rung lower; on a success learn the weather of the next three days and the worst danger the land holds on your road; and weather counts one severity rung lower for up to six beings until the day ends.",
       [reach('this beat'), stakes('this beat'), rev('the weather of the next three days'), rev('the worst danger on the road'), hazard(['harm.frost', 'harm.fire.heat', 'harm.storm']), tgt(5)], f=2, per='rest_long')],
   attr='wits', check=('aimed', 'verb.observe', 'obstacle tier moderate'),
   x=[('weather raised by magic', 'ab.gust; deed.primal.weather'), ('changing the weather', 'deed.primal.weather')])

# ====================================================================== deed.craft
C = 'deed.craft.'
ab('ab.biting_water', 'Biting Water', C + 'alchemy.reagents', 4, 'acid_flask', 'Working', 'beat',
   'Throw a reagent that eats flesh, iron and lock alike.',
   'Applies to a point within band.near and up to three beings within band.engaged of it, using one flask of reagent.',
   [rk("Throw a flask of reagent at a point within band.near. Up to three beings within band.engaged of it roll Evade against your effect DC: on a failure each takes Heavy acid harm, is exposed until the scene ends and weakened until the end of its next turn. The reagent also eats through one lock, chain or bar it touches.",
       [fchk('evade'), harm(3, ['harm.corrosion.acid'], 'each being that fails'), tgt(2), cond('cond.exposed', 1, 'scene', 'each being that fails'), cond('cond.weakened', 1, 'rounds:1', 'each being that fails'), perm(2)], f=2)],
   attr='intellect', check=EVA, oc=1, cost_text='one flask of reagent (08)', spread='burst', harm_tags=['harm.corrosion.acid'],
   traits=['trait.action.attack', 'trait.delivery.area'],
   x=[('fire', 'ab.firepot'), ('a potion', 'ab.quick_tincture')])

ab('ab.engine_of_war', 'Engine of War', C + 'artifice.siege_engines', 4, 'siege_engine', 'Working', 'beat',
   'Lay and loose an engine you built so its stone flies true.',
   'Applies to a siege engine you built or crew, against a target within band.distant.',
   [rk("Lay and loose the engine (Handle, Intellect, against the target's attack defense or the structure's tier). On a success the target takes Grievous crushing harm and so does up to two beings beside it; those beings are knocked prone; and the siege clock against a struck structure ticks one segment.",
       [harm(4, ['harm.physical.crush'], T), tgt(2), cond('cond.prone', 1, 'rounds:1', 'each being struck'), tick('the siege clock against the structure', 1)], f=2, per='scene_end')],
   attr='intellect', check=('aimed', 'verb.handle', "the target's attack defense or the structure's tier"), spread='burst',
   traits=['trait.action.attack', 'trait.delivery.ranged', 'trait.sense.loud'],
   x=[('building the engine', 'a project (08)'), ('a target within band.near', 'the engine cannot lay so close')])

ab('ab.days_fortress', "The Day's Fortress", C + 'building.masonry', 5, 'raise_fortress', 'Working', 'beat',
   'Raise in one day a strongpoint that should take a season.',
   'Applies to one site you direct the building of for a day, with hands and stone or timber at hand.',
   [rk("Direct a day's building (Handle, Intellect, against the site's tier). The fortification's project clock ticks by your delivered reach as if a season's work were done; the site is recorded as fortified; and up to six beings who hold it hold flag.in_cover there.",
       [perm(4), tick("the fortification's project clock", 'delivered_reach'), fact('the site', 'fortified', True), move('up to six beings who hold the site', 0, add=['flag.in_cover']), tgt(5)], f=2, per='rest_long')],
   attr='intellect', check=('aimed', 'verb.handle', "the site's tier"),
   x=[('bringing a wall down', 'ab.breach'), ('a site with no hands or materials', 'the work needs both (08)')])

ab('ab.hearth_ale', 'Hearth Ale', C + 'cookery.brewing', 4, 'hearth_ale', 'Working', 'beat',
   'Pour a brew that puts heart back into a company.',
   'Applies to up to six beings who drink a brew you made, at a rest.',
   [rk("Pour your brew for up to six beings: each regains 3 Vitality and holds a Protective lever on Resolve checks until the scene ends, and the company is recorded as having drunk together.",
       [heal(3, 'each drinker'), lev('protective', "each drinker's Resolve checks", 'scene'), tgt(5), fact('the company', 'drank_together', True)], f=1, per='rest_long')],
   attr='wits', x=[('a being that cannot drink', 'it gains nothing'), ('a feast for a hall', 'ab.feast_of_accord')])

ab('ab.feast_of_accord', 'Feast of Accord', C + 'cookery.feasting', 5, 'great_feast', 'Working', 'beat',
   'Set a feast that makes rivals sit as friends.',
   'Applies to a feast you prepare for an evening, for up to six named guests and their trains.',
   [rk("Set the feast: up to six named guests regain 5 Vitality; your Talk at the table is +1 and holds an Amplifying lever this scene; you learn who at the table is allied with whom; and the feast is recorded as given in peace.",
       [heal(5, 'each named guest'), tgt(5), edge(1, 'a Talk beat at the feast'), lev('amplifying', 'Talk beats at the feast', 'scene', verbs=['verb.talk']), rev('the alliances among the guests'), fact('the feast', 'given_in_peace', True)], f=3, per='rest_long')],
   attr='presence', oc=0, cost_text='the stores of a feast (08)',
   x=[('guests who will not come', 'verb.talk'), ('poisoning a guest', 'ab.slow_draught')])

ab('ab.lasting_word', 'The Lasting Word', C + 'enchanting.inscription', 5, 'lasting_rune', 'Working', 'beat',
   'Cut a rune whose power never fades from the thing.',
   'Applies to one weapon you inscribe over a day; requires a magic training license (05.9.4).',
   [rk("Inscribe a lasting rune over a day (Handle, Intellect, against the item's tier). The beat's reach is one rung higher and its stakes one rung lower; the enchanting project clock ticks by your delivered reach; on completion its wielder has +1 to Strikes and +2 harm with it, and the item is recorded as rune-bound; you learn its history.",
       [reach('this beat'), stakes('this beat'), tick('the enchanting project clock', 'delivered_reach'), edge(1, 'a Strike with the inscribed weapon'), hedge(2, 'a Strike with the inscribed weapon'), fact('the item', 'rune_bound', True), rev("the item's history")], f=2, per='rest_long')],
   attr='intellect', check=('aimed', 'verb.handle', "the item's tier"),
   x=[('a passing rune', 'ab.rune_of_keenness'), ('a power seated beyond a rune', 'ab.bind_power')])

ab('ab.heart_of_the_stone', 'Heart of the Stone', C + 'jewelcraft.gemcutting', 4, 'focus_stone', 'Working', 'beat',
   'Cut a stone so that it holds a spark of the will.',
   'Applies to one fine gem you cut over an interval.',
   [rk("Cut a focusing stone over an interval: its bearer may once regain 2 Focus by spending an action with it; you learn the gem's worth and source; the work's clock ticks one segment; and the stone is recorded as cut by you.",
       [foc(2, 'the bearer'), rev("the gem's worth and source"), tick("the work's project clock", 1), fact('the stone', 'cut_by', 'the pc')], per='rest_long')],
   attr='intellect', x=[('a stone already cut by another', 'ab.true_cut'), ('more than one stone a rest', 'the limit')])

ab('ab.regalia', 'Regalia', C + 'jewelcraft.goldwork', 5, 'regalia', 'Working', 'beat',
   'Make a piece of gold fit for a ruler to wear.',
   'Applies to one piece of fine goldwork you make over a week for one recipient you name.',
   [rk("Make regalia over a week (Handle, Intellect, against Hard). The beat's reach is one rung higher and its stakes one rung lower; when given, the gift is recorded; your Talk with its recipient holds a Precision lever and an Amplifying lever that scene; and the piece can hold an enchantment one tier above its materials.",
       [reach('this beat'), stakes('this beat'), fact('the recipient', 'holds_gift_from', 'the pc'), lev('precision', 'Talk beats with the recipient', 'scene', verbs=['verb.talk']), lev('amplifying', 'Talk beats with the recipient', 'scene', verbs=['verb.talk']), perm(4)], f=2, per='rest_long')],
   attr='intellect', check=('aimed', 'verb.handle', 'obstacle tier hard'),
   x=[('the enchantment itself', 'ab.bind_power'), ('a recipient who refuses gifts', 'verb.talk')])

ab('ab.second_skin', 'Second Skin', C + 'leathercraft.goods', 4, 'fitted_leather', 'Working', 'beat',
   'Fit leather to a body until it moves as the body does.',
   'Applies to one set of leather armor or gear you fit to one wearer over an interval.',
   [rk("Fit leather to a wearer over an interval: while worn, physical harm against them is reduced by 1, they have +1 Agility defense and +1 to Sneak beats, and the gear is recorded as fitted to them.",
       [red(1, ['harm.physical']), dedge(1, 'agility', 'the wearer wears the fitted gear'), edge(1, 'verb = verb.sneak and the wearer wears the fitted gear'), fact('the gear', 'fitted_to', 'the wearer')], f=1)],
   attr='wits', x=[('metal armor', 'ab.masterwork'), ('mending in the field', 'ab.field_patch')])

ab('ab.hide_of_the_slain', 'Hide of the Slain', C + 'leathercraft.tanning', 5, 'trophy_hide', 'Working', 'beat',
   'Make armor of a great beast that keeps the beast\'s own guard.',
   'Applies to the hide of one creature at or below your power band, worked over a week.',
   [rk("Work the hide over a week (Handle, Intellect, against the creature's threat band). The beat's reach is one rung higher; the work's clock ticks by your delivered reach; you learn one property of the hide; on completion its wearer resists one harm branch the creature resisted, reduces physical harm by 1 and has +1 Agility defense; it is recorded as made from that creature.",
       [reach('this beat'), tick("the work's project clock", 'delivered_reach'), rev('one property of the hide'), resist(["one harm branch the creature resisted"]), red(1, ['harm.physical']), dedge(1, 'agility', 'the wearer wears the armor'), fact('the armor', 'made_from', 'the creature')], f=2, per='rest_long')],
   attr='intellect', check=('aimed', 'verb.handle', "the creature's threat band"),
   x=[('a creature above your band', 'the hide will not hold its guard'), ('taking the hide', 'ab.cure_hide')])

ab('ab.palimpsest', 'Palimpsest', C + 'scribing.copying', 4, 'recover_text', 'Working', 'beat',
   'Raise a scraped, burned or washed text from its page.',
   'Applies to one damaged or overwritten text you can study for an interval.',
   [rk("Raise the lost text (Observe, Intellect, against the text's tier). The beat's reach is one rung higher; on a success learn what the text said and what was written over it; the inquiry's clue clock ticks by your delivered reach; you hold a Precision lever on beats that use it this scene; and a fair copy is recorded.",
       [reach('this beat'), rev('what the lost text said'), rev('what was written over it'), tick("the inquiry's clue clock", 'delivered_reach'), lev('precision', 'beats that use the text', 'scene'), fact('the text', 'copied_by', 'the pc')], f=2, per='scene_end')],
   attr='intellect', check=('aimed', 'verb.observe', "the text's tier"),
   x=[('a cipher', 'ab.cipher_breaker'), ('a text destroyed to ash', 'nothing is left to raise')])

ab('ab.master_chart', 'Master Chart', C + 'scribing.cartography', 5, 'master_chart', 'Working', 'beat',
   'Draw a region so truly that it guides whoever holds the chart.',
   'Applies to a region you have crossed, drawn over a week, for up to six travellers who use the chart.',
   [rk("Draw a master chart (Handle, Intellect, against the region's tier). The beat's reach is one rung higher; you learn one hidden route through the region; for up to six travellers who use the chart, the region's hazards count one severity rung lower and each successful travel beat ticks the travel clock one segment more; and the chart is recorded as made.",
       [reach('this beat'), rev('one hidden route through the region'), hazard(['harm.physical', 'harm.frost', 'harm.fire.heat']), tgt(5), tick('the travel clock', 1), fact('the chart', 'made_by', 'the pc')], f=2, per='rest_long')],
   attr='intellect', check=('aimed', 'verb.handle', "the region's tier"),
   x=[('a region you have not crossed', 'ab.field_map'), ('the sea', 'ab.storm_helm')])

ab('ab.named_blade', 'The Named Blade', C + 'smithing.weapons', 5, 'named_blade', 'Working', 'beat',
   'Forge a weapon that will be known by its own name.',
   'Applies to one weapon you forge over a week from sound materials.',
   [rk("Forge the weapon over a week (Handle, Might, against Hard). The beat's reach is one rung higher and its stakes one rung lower; the forging clock ticks by your delivered reach; on completion its wielder has +1 to Strikes and +2 harm with it, once a scene a Strike with it deals harm one severity rung heavier, and its name is recorded.",
       [reach('this beat'), stakes('this beat'), tick('the forging clock', 'delivered_reach'), edge(1, 'a Strike with the named weapon'), hedge(2, 'a Strike with the named weapon'), sev(1, 'one Strike a scene with the named weapon'), fact('the weapon', 'named', 'the name the pc gives')], f=2, per='rest_long')],
   attr='might', check=('aimed', 'verb.handle', 'obstacle tier hard'),
   x=[('a magical power', 'ab.bind_power'), ('armor', 'ab.masterwork')])

ab('ab.company_banner', 'Company Banner', C + 'textiles.weaving', 4, 'banner', 'Working', 'beat',
   'Raise a banner whose weave tells a company who it is.',
   'Applies to a banner you wove, raised where up to six allies within band.near can see it.',
   [rk("Raise your banner: up to six allies who see it hold a Protective lever on their beats and +1 to checks that resist fear until the scene ends, and the company is recorded as fighting under it.",
       [lev('protective', 'beats by allies who see the banner', 'scene'), tgt(5), edge(1, 'an ally who sees the banner resists fear'), fact('the company', 'fights_under', 'the banner')], f=2)],
   attr='presence', x=[('allies who cannot see it', 'ab.rally'), ('magical fear only', 'it steadies against all fear alike')])

ab('ab.spiders_rigging', "Spider's Rigging", C + 'textiles.ropework', 5, 'rope_web', 'Working', 'beat',
   'Rig a place with rope and net until it fights for you.',
   'Applies to one place within band.near that you rig over an interval.',
   [rk("Rig the place over an interval: up to six allies there can climb its ropes as ground and hold flag.elevated when they choose; the first foe to cross the rigging is restrained until the end of its next turn; and the place is recorded as rigged.",
       [mode('climb', 'scene'), tgt(5), move('an ally who climbs the rigging', 0, add=['flag.elevated']), cond('cond.restrained', 1, 'rounds:1', 'the first foe to cross the rigging'), fact('the place', 'rigged_by', 'the pc')], f=3, per='scene_end')],
   attr='agility', x=[('a single knot', 'ab.knot_lore'), ('an open field with nothing to tie to', 'the rigging needs anchors')])

ab('ab.heartwood_bow', 'Heartwood Bow', C + 'woodcraft.bowyery', 4, 'heartwood_bow', 'Working', 'beat',
   'Make a bow from heartwood that casts farther than any other.',
   'Applies to one bow or crossbow you make over a day.',
   [rk("Make the bow over a day: the beat's reach is one rung higher and the work's clock ticks one segment more; its archer has +2 harm with it and shoots to band.distant without the long-range DC shift; and it is recorded as made by you.",
       [reach('this beat'), tick("the work's project clock", 1), hedge(2, 'a Strike with the bow'), waive('the DC shift for a shot at band.distant', 'a Strike with the bow'), fact('the bow', 'made_by', 'the pc')], f=1)],
   attr='wits', x=[('arrows', 'ab.fletch_true'), ('a magical bow', 'ab.bind_power')])

ab('ab.lay_the_keel', 'Lay the Keel', C + 'woodcraft.carpentry', 5, 'great_carpentry', 'Working', 'beat',
   'Build a ship, bridge or hall of timber in a fraction of the time.',
   'Applies to one vessel, bridge or timber building you direct the work on for a week.',
   [rk("Direct a week's carpentry (Handle, Intellect, against the work's tier). The beat's reach is one rung higher and its stakes one rung lower; the work's clock ticks by your delivered reach as if a season's work were done; once finished, water and weather count one severity rung lower for it; and it is recorded as built by you.",
       [perm(4), reach('this beat'), stakes('this beat'), tick("the work's project clock", 'delivered_reach'), hazard(['harm.storm', 'harm.physical.crush']), fact('the work', 'built_by', 'the pc')], f=2, per='rest_long')],
   attr='intellect', check=('aimed', 'verb.handle', "the work's tier"),
   x=[('a barricade', 'ab.sound_timber'), ('stone', 'ab.days_fortress')])

# ====================================================================== deed.influence
I = 'deed.influence.'
ab('ab.rally_to_the_standard', 'Rally to the Standard', I + 'command.rallying', 5, 'great_rally', 'Working', 'beat',
   'Call a breaking company back into one fighting body.',
   'Applies to up to six allies within band.near who can see or hear you.',
   [rk("Call the rally: up to six allies regain 3 Vitality, their fear ends, each may move one band, each holds a Precision lever on its next beat this round, and each is +1 to checks until the scene ends.",
       [heal(3, 'each ally'), tgt(5), cleanse('cond.frightened', 'each ally'), move('each ally', 1), lev('precision', "each ally's next beat", 'rounds:1'), edge(1, "an ally's check this scene")], f=3, per='scene_end')],
   attr='presence', traits=['trait.action.speech', 'trait.sense.loud'],
   x=[('allies who cannot see or hear you', 'they are not rallied'), ('yourself', 'ab.undaunted')])

ab('ab.order_of_precedence', 'Order of Precedence', I + 'etiquette.courtly', 4, 'precedence', 'Working', 'beat',
   'Read and set the order of a room so it favors you.',
   'Applies to a formal gathering, court or audience you attend.',
   [rk("Read the room's order (Observe, Presence, against Moderate). The beat's reach is one rung higher; on a success learn who outranks whom and each party's grievance; you hold a Precision lever on Talk there this scene; and a slight made against you there this scene cannot be repeated by its speaker without breaking courtesy openly.",
       [reach('this beat'), rev("the room's order of rank"), rev("each party's grievance"), lev('precision', 'Talk beats at the gathering', 'scene', verbs=['verb.talk']), restr({'methods': ['repeating a slight against the pc']}, 'the speaker of a slight', 'scene')], f=2, per='scene_end')],
   attr='presence', check=('aimed', 'verb.observe', 'obstacle tier moderate'),
   x=[('a gathering with no formal custom', 'ab.read_the_heart'), ('a foreign court', 'ab.foreign_manner')])

ab('ab.guest_right', 'Guest-Right', I + 'etiquette.foreign', 5, 'guest_right', 'Working', 'beat',
   'Claim the old law that binds a host to guard a guest.',
   'Applies to a household, camp or people whose customs you have kept since you came among them.',
   [rk("Claim guest-right (Talk, Presence, against Moderate). The beat's stakes are one rung lower; on a success none of the host's people may harm you or up to five companions under their roof or in their camp while you keep their customs; they owe you shelter; your Talk with them holds an Amplifying lever this scene; and you learn their gravest taboo.",
       [stakes('this beat'), restr({'methods': ['harming the guests under their roof']}, "the host's people", 'while:the guests keep the customs'), tgt(5), fact('the host', 'owes_shelter_to', 'the pc'), lev('amplifying', "Talk beats with the host's people", 'scene', verbs=['verb.talk']), rev("the host's gravest taboo")], f=2, per='rest_long')],
   attr='presence', check=('aimed', 'verb.talk', 'obstacle tier moderate'), traits=['trait.action.speech'],
   x=[('a host who never granted welcome', 'verb.talk'), ('a guest who breaks the custom', 'the right ends at once')])

ab('ab.hidden_wound', 'The Hidden Wound', I + 'insight.empathy', 4, 'hidden_wound', 'Working', 'beat',
   'See the grief or fear a person keeps behind their face.',
   'Applies to one person you have spoken with this scene.',
   [rk("Read a person (Observe, Wits, against their Wits defense). The beat's reach is one rung higher; on a success learn what they grieve or fear and what they want most; your Talk with them holds a Precision lever and an Amplifying lever this scene.",
       [reach('this beat'), rev('what the person grieves or fears'), rev('what the person wants most'), lev('precision', 'Talk beats with the person', 'scene', verbs=['verb.talk']), lev('amplifying', 'Talk beats with the person', 'scene', verbs=['verb.talk'])], f=2, per='scene_end')],
   attr='wits', check=('aimed', 'verb.observe', "the person's Wits defense"),
   x=[('a mind that is not folk', 'ab.beast_speech; ab.spirit_tongue'), ('reading thoughts', 'deed.arcane.mind')])

ab('ab.open_room', 'The Open Room', I + 'insight.lies', 5, 'open_room', 'Working', 'beat',
   'Watch a gathering until every lie in it shows.',
   'Applies to a gathering of up to a dozen people you watch for an interval.',
   [rk("Watch a gathering for an interval (Observe, Wits, against the highest Wits defense among them). The beat's reach is one rung higher and its stakes one rung lower; on a success learn who there has lied, whom each one serves and one secret one of them keeps; you hold a Precision lever on Talk there this scene; and the inquiry's clue clock ticks by your delivered reach.",
       [reach('this beat'), stakes('this beat'), rev('who in the gathering has lied'), rev('whom each one serves'), rev('one secret one of them keeps'), lev('precision', 'Talk beats in the gathering', 'scene', verbs=['verb.talk']), tick("the inquiry's clue clock", 'delivered_reach')], f=3, per='scene_end')],
   attr='wits', check=('aimed', 'verb.observe', 'the highest Wits defense in the gathering'),
   x=[('the content of the lies', 'the clue graph (15)'), ('a single statement', 'ab.lie_sense')])

ab('ab.promise_made', 'A Promise Made', I + 'intimidation.threat', 4, 'dread_promise', 'Working', 'beat',
   'Promise a cruelty so plainly that no one doubts you.',
   'Applies to up to three beings within band.near who can hear and understand you.',
   [rk("Make your promise (Talk, Presence, against the highest Resolve defense among them). On a success each is frightened and will not act against you this scene unless you act first; you learn what each fears most; and you hold a Precision lever on Talk with them this scene.",
       [cond('cond.frightened', 1, 'scene', 'each listener'), restr({'methods': ['acting against the pc unless the pc acts first']}, 'each listener', 'scene'), tgt(2), rev('what each listener fears most'), lev('precision', 'Talk beats with the listeners', 'scene', verbs=['verb.talk'])], f=2, per='scene_end')],
   attr='presence', check=('aimed', 'verb.talk', 'the highest Resolve defense among them'), traits=['trait.action.speech'],
   x=[('a being with no fear (constructs, the mindless)', 'it does not take'), ('breaking a captive', 'ab.break_the_will')])

ab('ab.kingmakers_table', "The Kingmaker's Table", I + 'intrigue.alliances', 5, 'kingmaker', 'Working', 'beat',
   'Bring two powers to one table and leave with their pact.',
   'Applies to two factions whose envoys you have brought together.',
   [rk("Broker a pact (Talk, Presence, against the higher Presence defense of the envoys). The beat's reach is one rung higher and its stakes one rung lower; on a success learn each side's hidden aim; the pact's clock ticks by your delivered reach; your Talk with each holds a Precision lever and an Amplifying lever this scene; and the pact, with you as its broker, is recorded.",
       [reach('this beat'), stakes('this beat'), rev("the first faction's hidden aim"), rev("the second faction's hidden aim"), tick("the pact's clock", 'delivered_reach'), lev('precision', 'Talk beats with the envoys', 'scene', verbs=['verb.talk']), lev('amplifying', 'Talk beats with the envoys', 'scene', verbs=['verb.talk']), fact('the pact', 'brokered_by', 'the pc')], f=3, per='rest_long')],
   attr='presence', check=('aimed', 'verb.talk', "the higher Presence defense of the envoys"), traits=['trait.action.speech'],
   x=[('factions at open war', 'a faction clock (11)'), ('a single rival', 'ab.leverage')])

ab('ab.words_before_the_charge', 'Words Before the Charge', I + 'performance.oratory', 4, 'battle_speech', 'Working', 'beat',
   'Speak the words that send a company into a fight as one.',
   'Applies before a conflict begins, to up to six allies who can hear you.',
   [rk("Speak before the fight: up to six allies hold a Protective lever on their beats and +1 to their checks until the conflict ends, and each holds a Precision lever on its first beat.",
       [lev('protective', 'beats by the allies', 'conflict'), tgt(5), edge(1, "an ally's check in the conflict"), lev('precision', "each ally's first beat")], f=2, per='scene_end')],
   attr='presence', traits=['trait.action.speech', 'trait.sense.loud'],
   x=[('a fight already joined', 'ab.rally; ab.stirring_song'), ('foes', 'ab.cow')])

ab('ab.tale_that_travels', 'The Tale That Travels', I + 'performance.storytelling', 5, 'travelling_tale', 'Working', 'beat',
   'Tell a deed so well that the country tells it after you.',
   'Applies to one deed you witnessed, told to an audience of at least six.',
   [rk("Tell the tale (Talk, Presence, against Hard). The beat's reach is one rung higher; on a success the deed is recorded as known through the region and its doer's renown clock ticks by your delivered reach; up to six named listeners hold your telling as true; your Talk with those who heard it holds an Amplifying lever this scene; and you learn who in the audience was moved against it.",
       [reach('this beat'), fact('the deed', 'known_through', 'the region'), tick("the doer's renown clock", 'delivered_reach'), fact('the named listeners', 'believe', 'the telling'), tgt(5), lev('amplifying', 'Talk beats with those who heard', 'scene', verbs=['verb.talk']), rev('who in the audience was moved against it')], f=3, per='rest_long')],
   attr='presence', check=('aimed', 'verb.talk', 'obstacle tier hard'), traits=['trait.action.speech'],
   x=[('a deed that did not happen', 'ab.long_con'), ('a song in a fight', 'ab.stirring_song')])

ab('ab.point_by_point', 'Point by Point', I + 'persuasion.argument', 4, 'argument', 'Lever', 'rider',
   'Take apart an objection before it is made.',
   'Applies to a Talk beat that argues a case to a listener who is weighing it.',
   [rk("On a Talk beat of argument: its reach is one rung higher and its stakes one rung lower, you learn the listener's weakest objection, and you hold a Precision lever on this beat.",
       [reach('this beat'), stakes('this beat'), rev("the listener's weakest objection"), lev('precision', 'this beat')], f=1, per='scene_end')],
   verbs=['verb.talk'], x=[('a listener who will not weigh it', 'ab.cow; ab.leverage'), ('a crowd', 'ab.turn_the_room')])

ab('ab.change_of_heart', 'Change of Heart', I + 'persuasion.appeal', 5, 'change_heart', 'Working', 'beat',
   'Turn a sworn rival by speaking to what they once loved.',
   'Applies to one rival or enemy who will hear you speak for at least a minute.',
   [rk("Make your appeal (Talk, Presence, against their Resolve defense). The beat's reach is one rung higher and its stakes one rung lower; on a success their stance toward you moves one step warmer and is recorded; they will not act against you until you wrong them; you learn what they would need to become your ally; your Talk with them holds a Precision lever and an Amplifying lever this scene; and the reconciliation clock ticks by your delivered reach.",
       [reach('this beat'), stakes('this beat'), fact('the rival', 'stance_toward_pc', 'one step warmer'), restr({'methods': ['acting against the pc until wronged'] }, 'the rival', 'while:the pc does not wrong them'), rev('what the rival would need to become an ally'), lev('precision', 'Talk beats with the rival', 'scene', verbs=['verb.talk']), lev('amplifying', 'Talk beats with the rival', 'scene', verbs=['verb.talk']), tick('the reconciliation clock', 'delivered_reach')], f=3, per='rest_long')],
   attr='presence', check=('aimed', 'verb.talk', "the rival's Resolve defense"), traits=['trait.action.speech'],
   x=[('magical charm', 'ab.honeyed_thought'), ('a rival you wronged and have not made amends to', 'it fails without a roll')])

ab('ab.drill_yard', 'Drill Yard', I + 'teaching.instruction', 4, 'drill', 'Working', 'beat',
   'Drill a company until one move is in their bones.',
   'Applies to up to six people you drill for an interval in one verb you hold competence in.',
   [rk("Drill up to six people for an interval in one verb: until their next long rest each is +1 with it and holds a Protective lever on beats with it, and the training clock of each ticks one segment.",
       [edge(1, 'the drilled verb'), tgt(5), lev('protective', 'beats with the drilled verb', 'scene'), tick("each one's training clock", 1)], f=1, per='rest_long')],
   attr='presence', x=[('a verb you do not hold', 'ab.patient_teacher'), ('an ability', 'ab.lend_the_art')])

ab('ab.sound_venture', 'Sound Venture', I + 'trade.venture', 4, 'venture', 'Working', 'beat',
   'Back a venture so that it returns more than it risked.',
   'Applies to one trading venture, caravan or shipment you back with coin.',
   [rk("Back a venture (Talk, Intellect, against the market's tier). The beat's reach is one rung higher and its stakes one rung lower; the venture's clock ticks by your delivered reach; you learn one thing the market hides; the first coin loss the venture would suffer does not apply; the venture is recorded as yours; and you hold a Precision lever on this beat.",
       [reach('this beat'), stakes('this beat'), tick("the venture's clock", 'delivered_reach'), rev('one thing the market hides'), waive("the venture's first loss of coin", 'this venture'), fact('the venture', 'backed_by', 'the pc'), lev('precision', 'this beat')], f=2, per='rest_long')],
   attr='intellect', check=('aimed', 'verb.talk', "the market's tier"),
   x=[('a single sale', 'ab.sharp_bargain'), ('a forged deal', 'ab.perfect_papers')])

ab('ab.corner_the_market', 'Corner the Market', I + 'trade.haggling', 5, 'corner_market', 'Working', 'beat',
   'Buy up a trade until every seller must come to you.',
   'Applies to one good in one market town that you have traded in this season.',
   [rk("Corner a good (Talk, Intellect, against the market's tier). The beat's reach is one rung higher and its stakes one rung lower; you learn who else trades it; the market's clock ticks by your delivered reach; rivals cannot buy or sell it there this scene except through you; the corner is recorded; your Talk there holds an Amplifying lever this scene; and your trade beats there are +1.",
       [reach('this beat'), stakes('this beat'), rev('who else trades the good'), tick("the market's clock", 'delivered_reach'), restr({'methods': ['trading the good except through the pc']}, 'rival traders', 'scene'), fact('the market', 'cornered_by', 'the pc'), lev('amplifying', 'Talk beats in the market', 'scene', verbs=['verb.talk']), edge(1, 'deed_tag under deed.influence.trade in the market')], f=3, per='rest_long')],
   attr='intellect', check=('aimed', 'verb.talk', "the market's tier"),
   x=[('a market under a guild charter', 'a faction clock (11)'), ('appraising one thing', 'ab.appraisers_eye')])

# ====================================================================== deed.divine (casting attribute Presence)
D = 'deed.divine.'
UNHOLY = 'creature.undead or creature.fiend'
ab('ab.word_of_banishment', 'Word of Banishment', D + 'exorcism.banishing', 4, 'banish_word', 'Working', 'beat',
   "Speak your keeper's name so the unclean cannot stand near you.",
   'Applies to up to two undead or fiends within band.near that can hear you.',
   [rk("Speak the name. Up to two undead or fiends within band.near roll Endure (Resolve) against your effect DC: on a failure each takes Heavy radiant harm, is frightened until the scene ends and cannot come within band.close of you this scene. You hold a Precision lever on beats against them this scene.",
       [fchk('endure'), harm(3, ['harm.radiance.holy'], 'each that fails'), tgt(1), cond('cond.frightened', 1, 'scene', 'each that fails'), restr({'methods': ['coming within band.close of the caster']}, 'each that fails', 'scene'), lev('precision', 'beats against them', 'scene')], f=2, per='scene_end')],
   check=RES, harm_tags=['harm.radiance.holy'], traits=['trait.sense.loud'],
   x=[('the living', 'ab.cow'), ('a possession', 'ab.cast_out')])

ab('ab.grave_emptied', 'The Grave Emptied', D + 'exorcism.turning', 5, 'mass_turning', 'Working', 'beat',
   'Turn every unquiet dead around you at once.',
   'Applies to up to six undead within band.near of you.',
   [rk("Raise your keeper's sign. Up to six undead within band.near roll Endure (Resolve) against your effect DC: on a failure each takes Heavy radiant harm, is frightened until the scene ends and cannot come within band.close of you this scene.",
       [fchk('endure'), harm(3, ['harm.radiance.holy'], 'each undead that fails'), tgt(5), cond('cond.frightened', 1, 'scene', 'each undead that fails'), restr({'methods': ['coming within band.close of the caster']}, 'each undead that fails', 'scene')], f=3, per='scene_end')],
   check=RES, spread='burst', harm_tags=['harm.radiance.holy'], traits=['trait.delivery.area', 'trait.sense.visible'],
   x=[('fiends', 'ab.word_of_banishment'), ('one undead', 'ab.turn_undead')])

ab('ab.circle_of_mending', 'Circle of Mending', D + 'healing.mending', 4, 'mass_mend', 'Working', 'beat',
   'Close the wounds of everyone who stands in your circle.',
   'Applies to up to four living beings within band.close of you.',
   [rk("Lay your hands in a circle: up to four living beings within band.close regain 5 Vitality, and their bleeding and their daze end.",
       [heal(5, 'each being in the circle'), tgt(3), cleanse('cond.bleeding', 'each being in the circle'), cleanse('cond.dazed', 'each being in the circle')], f=2)],
   x=[('the dying', 'ab.breath_of_life'), ('poison or disease', 'ab.purge')])

ab('ab.sworn_company', 'The Sworn Company', D + 'oaths.swearing', 5, 'company_oath', 'Working', 'beat',
   'Swear a company to one purpose before your keeper.',
   'Applies to you and up to four companions who swear the same oath aloud.',
   [rk("Swear the oath with up to four companions: until the purpose is met or a long rest passes, each is +1 to beats toward it and holds a Protective lever on its beats; you cannot be frightened; the oath's clock ticks by your delivered reach; and the oath is recorded.",
       [edge(1, 'a beat toward the sworn purpose'), tgt(4), lev('protective', "each sworn one's beats", 'scene'), immune(['cond.frightened']), tick("the oath's clock", 'delivered_reach'), fact('the company', 'sworn_to', 'the purpose')], f=2, per='rest_long')],
   traits=['trait.action.speech'],
   x=[('binding another to an oath', 'ab.binding_vow'), ('an oath sworn under compulsion', 'it does not hold')])

ab('ab.patrons_gaze', "The Patron's Gaze", D + 'pact.bargaining', 4, 'patron_gaze', 'Working', 'beat',
   'Turn the eye of the power you serve upon one foe.',
   'Applies to one being within band.near that you can see.',
   [rk("Mark a foe for your patron. It rolls Endure (Resolve) against your effect DC: on a failure it is frightened until the scene ends. Either way, your pact workings against it this scene deal +2 harm and their effect DC is +1, and you learn one of its tells.",
       [fchk('endure'), cond('cond.frightened', 1, 'scene', T), hedge(2, 'a pact working against the target this scene'), dcedge(1, 'a pact working against the target this scene'), rev("one tell of the target's stat block")], f=1, per='scene_end')],
   check=RES, x=[('a being your patron has claimed', 'it will not answer'), ('paying with your body', 'ab.blood_price')])

ab('ab.weal_or_woe', 'Weal or Woe', D + 'revelation.prophecy', 4, 'omen', 'Working', 'beat',
   'Ask your keeper whether a course leads to good or ill.',
   'Applies to one course of action you name that will be taken within a day.',
   [rk("Ask about a course: learn whether it leads to weal or woe and the gravest danger on it; its stakes are one rung lower; and you and up to three allies who take it hold a Protective lever on its beats this scene.",
       [rev('whether the course leads to weal or woe'), rev('the gravest danger on the course'), stakes('beats of the named course'), lev('protective', 'beats of the named course', 'scene'), tgt(3)], f=2, per='scene_end')],
   x=[('a course further than a day away', 'ab.far_seeing_trance; rit.augury'), ('who will do what', 'the Oracle')])

ab('ab.far_seeing_trance', 'Far-Seeing Trance', D + 'revelation.visions', 5, 'trance', 'Working', 'beat',
   'See in a trance a place or a person far from you.',
   'Applies to one person or place you have seen or hold a token of, anywhere in the world.',
   [rk("Enter a trance for an interval: see and hear the person or place as if you stood within band.near of it; learn where it is, who is with it and what is being done there; the inquiry's clue clock ticks by your delivered reach; your next beat about it has reach one rung higher; and you hold a Precision lever on beats about it this scene.",
       [perm(4), rev('where the subject is'), rev('who is with the subject'), rev('what is being done there'), tick("the inquiry's clue clock", 'delivered_reach'), reach('your next beat about the subject'), lev('precision', 'beats about the subject', 'scene')], f=3, per='rest_long')],
   traits=['trait.action.concentrate'],
   x=[('a place under a ward against sight', '05.7.7'), ('the future', 'ab.weal_or_woe')])

ab('ab.bond_of_hearth', 'Bond of Hearth and Blood', D + 'rites.bonding', 5, 'kin_bond', 'Working', 'beat',
   'Make kin before your keeper of those who were not.',
   'Applies to up to six beings who take part in the rite for an interval.',
   [rk("Perform the rite for an interval: up to six beings are recorded as kin; until a long rest passes each regains 1 Vitality, may take a hit meant for another kin within band.engaged, holds a Protective lever on its beats while another kin is within band.near, and is +1 to help kin.",
       [fact('the bonded', 'kin_to', 'one another'), heal(1, 'each bonded being'), intercept('another kin within band.engaged is hit'), lev('protective', "a bonded being's beats while another kin is within band.near", 'scene'), tgt(5), edge(1, 'verb = verb.help for kin')], f=2, per='rest_long')],
   x=[('the unwilling', 'the rite does not take'), ('marriage alone', 'ab.last_rites; 15 social')])

ab('ab.sentence_passed', 'Sentence Passed', D + 'smiting.judgment', 4, 'judgment', 'Working', 'beat',
   "Name a foe's crime and let your keeper strike it.",
   'Applies to one being within band.near whose wrong you can name.',
   [rk("Name the crime. The being rolls Endure (Resolve) against your effect DC: on a failure it takes Heavy radiant harm and is weakened and exposed until the scene ends; you learn whether the crime you named is true.",
       [fchk('endure'), harm(3, ['harm.radiance.holy'], T), cond('cond.weakened', 1, 'scene', T), cond('cond.exposed', 1, 'scene', T), rev('whether the named crime is true')], f=2, per='scene_end')],
   check=RES, harm_tags=['harm.radiance.holy'], traits=['trait.action.attack'],
   x=[('a being with no crime you can name', 'ab.searing_light'), ('a weapon blow', 'ab.smite')])

ab('ab.dawnbreak', 'Dawnbreak', D + 'smiting.radiance', 5, 'dawnbreak', 'Working', 'beat',
   'Break a sudden dawn on a place full of foes.',
   'Applies to a point within band.far and up to six beings within band.close of it.',
   [rk("Light breaks at a point within band.far. Up to six beings within band.close of it roll Evade against your effect DC: on a failure each takes Grievous radiant harm and is blinded until the end of its next turn; an undead or fiend that fails is also burning until the scene ends.",
       [fchk('evade'), harm(4, ['harm.radiance.holy'], 'each being that fails'), tgt(5), cond('cond.blinded', 1, 'rounds:1', 'each being that fails'), cond('cond.burning', 1, 'scene', 'each undead or fiend that fails')], f=3, per='rest_long')],
   check=EVA, spread='burst', harm_tags=['harm.radiance.holy'], traits=['trait.action.attack', 'trait.delivery.area', 'trait.sense.visible'],
   x=[('sparing allies inside the light', 'it takes every being in it'), ('one foe', 'ab.searing_light')])

ab('ab.hallowed_ground', 'Hallowed Ground', D + 'warding.consecration', 4, 'hallow', 'Working', 'beat',
   'Make a place holy so that the unclean burn to enter it.',
   'Applies to a place within band.near of you, consecrated for an interval; it lasts a day.',
   [rk("Consecrate a place for an interval; for a day, an undead or fiend that enters it takes Moderate radiant harm and cannot attack from inside it, up to six allies there are +1 to checks that resist profane effects, and the place is recorded as hallowed.",
       [harm(2, ['harm.radiance.holy'], 'an undead or fiend that enters'), restr({'methods': ['attacking from inside the hallowed place']}, 'undead and fiends', 'days:1'), edge(1, 'the check resists an effect whose source is ' + UNHOLY), tgt(5), fact('the place', 'hallowed', True)], f=2, per='rest_long')],
   x=[('a place already profaned', 'ab.cleansing_rite first'), ('one being', 'ab.sanctuary')])

ab('ab.keepers_shield', "The Keeper's Shield", D + 'warding.sanctuary', 5, 'keeper_shield', 'Reaction', 'reaction',
   'Let your keeper take a blow meant for one you guard.',
   'Applies to a hit on an ally within band.near of you.',
   [rk("When an ally within band.near is hit, negate that hit; the ally regains 3 Vitality, and up to five allies within band.near have +1 Agility defense until your next turn.",
       [prevent('an ally within band.near is hit'), heal(3, 'the ally'), dedge(1, 'agility', 'until your next turn'), tgt(4)], f=3, per='scene_end')],
   hook='on_attack_hit', when='an ally within band.near is hit',
   x=[('a hit on yourself', 'ab.spell_ward; ab.shield_block'), ('harm that is not a hit', 'verb.endure')])

# ====================================================================== deed.arcane (casting attribute Intellect)
A = 'deed.arcane.'
ab('ab.giants_sinew', "Giant's Sinew", A + 'alteration.enhancement', 4, 'giant_sinew', 'Working', 'beat',
   'Swell a body with a strength it was never given.',
   'Applies to one willing being you touch; it lasts until the scene ends.',
   [rk("Touch a willing being: until the scene ends it is +2 to Exert and Force, deals +2 harm with Strikes and has 2 more maximum Vitality.",
       [edge(2, 'verb = verb.exert or verb.force'), hedge(2, "the being's Strikes this scene"), maxm('vitality', 2)], f=2)],
   traits=['trait.delivery.touch'],
   x=[('an unwilling being', 'ab.wither'), ('another shape', 'deed.primal.shapeshifting')])

ab('ab.stone_flesh', 'Stone Flesh', A + 'alteration.transmutation', 5, 'petrify', 'Working', 'beat',
   'Turn living flesh to stone.',
   'Applies to up to three beings within band.close that you can see.',
   [rk("Up to three beings within band.close roll Endure (Endurance) against your effect DC: each that fails turns to stone and is frozen until the scene ends, then weakened until the scene after; each that succeeds is slowed until the scene ends.",
       [fchk('endure'), cond('cond.frozen', 2, 'scene', 'each being that fails'), cond('cond.weakened', 1, 'scene', 'each being that fails, once it moves again'), cond('cond.slowed', 1, 'scene', 'each being that succeeds'), tgt(2)], f=2)],
   check=END, x=[('a being of stone or metal', 'it is already stone'), ('a permanent change', 'a designed rite (05.8.4)')])

ab('ab.groundswell', 'Groundswell', A + 'earth.tremor', 4, 'tremor', 'Working', 'beat',
   'Make the ground roll like a wave.',
   'Applies to a point within band.near and up to four beings within band.close of it.',
   [rk("The ground heaves at a point within band.near. Up to four beings within band.close of it roll Evade against your effect DC: on a failure each takes Moderate crushing harm, is knocked prone and is slowed until the scene ends.",
       [fchk('evade'), harm(2, ['harm.physical.crush'], 'each being that fails'), tgt(3), cond('cond.prone', 1, 'rounds:1', 'each being that fails'), cond('cond.slowed', 1, 'scene', 'each being that fails')], f=2)],
   check=EVA, spread='burst', harm_tags=['harm.physical.crush'], traits=['trait.action.attack', 'trait.delivery.area', 'trait.sense.loud'],
   x=[('beings that fly', 'they are not on the ground'), ('one being', 'ab.clutching_earth')])

ab('ab.iron_obeys', 'Iron Obeys', A + 'earth.metal', 5, 'metal_command', 'Working', 'beat',
   'Command the metal a foe wears and carries.',
   'Applies to up to four beings within band.near who wear or carry metal.',
   [rk("Command the metal. Up to four beings within band.near who wear or carry it roll Endure (Endurance) against your effect DC: on a failure each takes Heavy crushing harm as its armor closes, is restrained until the end of its next turn, cannot use its metal weapon this scene and is exposed until the scene ends.",
       [fchk('endure'), harm(3, ['harm.physical.crush'], 'each being that fails'), tgt(3), cond('cond.restrained', 1, 'rounds:1', 'each being that fails'), restr({'methods': ['using its metal weapon']}, 'each being that fails', 'scene'), cond('cond.exposed', 1, 'scene', 'each being that fails')], f=3, per='scene_end')],
   check=END, spread='burst', harm_tags=['harm.physical.crush'], traits=['trait.action.attack', 'trait.delivery.area'],
   x=[('beings with no metal on them', 'ab.clutching_earth'), ('shaping metal for craft', 'deed.craft.smithing')])

ab('ab.wall_of_flame', 'Wall of Flame', A + 'fire.shaping', 4, 'fire_wall', 'Working', 'beat',
   'Raise a standing wall of fire across a space.',
   'Applies to a line within band.near of you, as long as band.near; it lasts until the scene ends.',
   [rk("Raise a wall of fire until the scene ends. A being that crosses it takes Heavy fire harm and is burning until the scene ends, up to two at a time; beings behind it hold flag.obscured against those beyond, and your allies behind it hold a Protective lever.",
       [harm(3, ['harm.fire.flame'], 'a being that crosses the wall'), cond('cond.burning', 1, 'scene', 'a being that crosses the wall'), tgt(2), move('beings behind the wall', 0, add=['flag.obscured']), lev('protective', 'beats by allies behind the wall', 'scene')], f=2, per='scene_end')],
   spread='linger', harm_tags=['harm.fire.flame'], traits=['trait.delivery.line', 'trait.sense.visible', 'trait.duration.sustained'],
   x=[('a wall that harms nothing that stays still', 'only crossing burns'), ('a burst', 'ab.firestorm')])

ab('ab.winters_breath', "Winter's Breath", A + 'frost.blast', 4, 'frost_cone', 'Working', 'beat',
   'Breathe out the cold of the deep north.',
   'Applies to up to four beings within band.close in front of you.',
   [rk("Breathe winter. Up to four beings within band.close in front of you roll Endure (Endurance) against your effect DC: on a failure each takes Heavy cold harm, is chilled until the scene ends and is slowed until the end of its next turn.",
       [fchk('endure'), harm(3, ['harm.frost.cold'], 'each being that fails'), tgt(3), cond('cond.chilled', 1, 'scene', 'each being that fails'), cond('cond.slowed', 1, 'rounds:1', 'each being that fails')], f=2)],
   check=END, spread='burst', harm_tags=['harm.frost.cold'], traits=['trait.action.attack', 'trait.delivery.area'],
   x=[('beings behind you', 'the breath goes forward'), ('one target', 'ab.rime_spear')])

ab('ab.ice_coffin', 'Ice Coffin', A + 'frost.shaping', 5, 'ice_coffin', 'Working', 'beat',
   'Close a foe inside a coffin of ice.',
   'Applies to up to two beings within band.near that you can see.',
   [rk("Up to two beings within band.near roll Endure (Endurance) against your effect DC: each that fails takes Heavy ice harm and is frozen until the scene ends; each that succeeds is chilled and slowed until the scene ends.",
       [fchk('endure'), harm(3, ['harm.frost.ice'], 'each being that fails'), cond('cond.frozen', 2, 'scene', 'each being that fails'), cond('cond.chilled', 1, 'scene', 'each being that succeeds'), cond('cond.slowed', 1, 'scene', 'each being that succeeds'), tgt(1)], f=3, per='scene_end')],
   check=END, harm_tags=['harm.frost.ice'], traits=['trait.action.attack'],
   x=[('a being of fire', 'it does not hold'), ('ground', 'ab.glaze')])

ab('ab.dread_phantasm', 'Dread Phantasm', A + 'illusion.phantasm', 4, 'fear_phantasm', 'Working', 'beat',
   'Show one mind the thing it fears most.',
   'Applies to one being with a mind within band.near.',
   [rk("The target rolls Endure (Resolve) against your effect DC: on a failure it sees its worst fear, takes Heavy psychic harm and is frightened and distracted until the scene ends; either way you learn what it fears.",
       [fchk('endure'), harm(3, ['harm.mind.psychic'], T), cond('cond.frightened', 1, 'scene', T), cond('cond.distracted', 1, 'scene', T), rev('what the target fears most')], f=2, per='scene_end')],
   check=RES, harm_tags=['harm.mind.psychic'], traits=['trait.nature.illusion', 'trait.nature.mental', 'trait.action.attack'],
   x=[('a mindless being', 'it sees nothing'), ('a false sight for all', 'ab.phantom')])

ab('ab.unremembering', 'Unremembering', A + 'mind.memory', 5, 'memory_theft', 'Working', 'beat',
   'Take an hour out of a mind, or put a false one in.',
   'Applies to one being with a mind that you touch.',
   [rk("Touch a mind. It rolls Endure (Resolve) against your effect DC: on a failure it is charmed until the end of its next turn, you learn what it remembers of the last day and of one person you name, and you take one memory of the last day from it or write in its place a false one, recorded.",
       [fchk('endure'), cond('cond.charmed', 1, 'rounds:1', T), rev('what the target remembers of the last day'), rev('what the target remembers of one named person'), perm(4), fact(T, 'remembers', 'what the caster left')], f=3, per='scene_end')],
   check=RES, traits=['trait.nature.mental', 'trait.delivery.touch'], dictates=True,
   x=[('memories older than a day', 'a designed rite (05.8.4)'), ('commanding an act', 'ab.compel')],
   nmi=['that the target knows a memory was taken'])

ab('ab.corpse_speech', 'Corpse-Speech', A + 'necromancy.communing', 4, 'corpse_speech', 'Working', 'beat',
   'Make a corpse answer what it saw in life.',
   'Applies to one corpse within band.engaged that still has a mouth, dead no longer than a month.',
   [rk("The corpse answers three questions about what it saw and knew in life, truly and as briefly as it can; you hold a Precision lever on beats of this inquiry this scene.",
       [perm(2), rev('the answer to the first question'), rev('the answer to the second question'), rev('the answer to the third question'), lev('precision', 'beats of this inquiry', 'scene')], f=2, per='scene_end')],
   traits=['trait.nature.profane'],
   x=[('a corpse older than a month', 'rit.raise_shade'), ('raising it to act', 'ab.raise_the_fallen')],
   nmi=["knowledge the dead being did not have"])

ab('ab.skein_of_lightning', 'Skein of Lightning', A + 'storm.lightning', 5, 'great_chain', 'Working', 'beat',
   'Throw a lightning that leaps from foe to foe without end.',
   'Applies to up to six beings within band.far, each within band.near of the one before.',
   [rk("Lightning leaps among up to six beings within band.far. Each rolls Evade against your effect DC: on a failure it takes Grievous lightning harm, is dazed until the end of its next turn and deafened until the scene ends.",
       [fchk('evade'), harm(4, ['harm.storm.lightning'], 'each being that fails'), tgt(5), cond('cond.dazed', 1, 'rounds:1', 'each being that fails'), cond('cond.deafened', 1, 'scene', 'each being that fails'), lev('precision', 'this beat')], f=3, per='rest_long')],
   check=EVA, spread='chain', harm_tags=['harm.storm.lightning'], traits=['trait.action.attack', 'trait.sense.loud', 'trait.sense.visible'],
   x=[('choosing an order that skips a being', 'it leaps to the nearest'), ('thunder', 'ab.thunderclap')])

ab('ab.bound_servitor', 'Bound Servitor', A + 'summoning.binding', 4, 'servitor', 'Working', 'beat',
   'Bind a called being to serve you until morning.',
   'Applies to one being of threat band 3 or lower that you call within band.close.',
   [rk("Call and bind a being of threat band 3: it serves you until your next long rest, acting when you spend an action to direct it; it may not harm you; you learn its true name; and the binding is recorded.",
       [summ('a bound being, threat band 3', 3, 'until_rest:rest_long'), restr({'methods': ['harming the caster']}, 'the bound being', 'until_rest:rest_long'), perm(2), rev("the being's true name"), fact('the being', 'bound_to', 'the pc')], f=2, per='rest_long')],
   x=[('a being above band 3', 'ab.deep_calling'), ('sending it away', 'ab.banish')])

ab('ab.deep_calling', 'Call of the Deep Places', A + 'summoning.calling', 5, 'great_summon', 'Working', 'beat',
   'Call a great being from beyond the world for one hour of service.',
   'Applies to one being of threat band 5 or lower, called within band.close.',
   [rk("Call a great being of threat band 5: it serves you until the scene ends, acting when you spend an action to direct it; it may not harm you; you learn its true name and its price; you hold a Precision lever on beats with it this scene; and the calling is recorded.",
       [summ('a called being, threat band 5', 5, 'scene'), restr({'methods': ['harming the caster']}, 'the called being', 'scene'), perm(2), rev("the being's true name and price"), lev('precision', 'beats made with the called being', 'scene'), fact('the being', 'called_by', 'the pc')], f=4, per='rest_long')],
   wk=1, weak=("The being remembers. When the scene ends it is free, and its stance toward you is recorded as hostile unless you paid its price.", ({'effect_id': 'eff.write_fact', 'params': {'subject': 'the called being', 'predicate': 'stance_toward_pc', 'value': 'hostile unless paid'}}, 0)),
   x=[('keeping it past the scene', 'rit.circle_of_binding'), ('a lesser servant', 'ab.call_servant')])

ab('ab.seal_of_closing', 'Seal of Closing', A + 'warding.sealing', 4, 'seal', 'Working', 'beat',
   'Seal a door or way so neither hand nor spell can open it.',
   'Applies to one door, gate, passage or container within band.close; it lasts until the scene ends.',
   [rk("Seal a way until the scene ends: no being may pass or open it without breaking the seal (Force against your effect DC +2); one working that would open or pass it fails; and you know when it is tested.",
       [restr({'methods': ['passing or opening the sealed way']}, 'every being but you', 'scene'), dcedge(2, 'a being tries to break the seal'), ctr('a working would open or pass the sealed way'), fact('the seal', 'tested', 'reported to the caster')], f=2, per='scene_end')],
   x=[('a seal that lasts beyond the scene', 'a designed rite (05.8.4)'), ('a living being', 'ab.compel')])

ab('ab.dome_of_force', 'Dome of Force', A + 'warding.shielding', 5, 'force_dome', 'Working', 'beat',
   'Raise a dome of force over everyone near you.',
   'Applies to you and up to five allies within band.close of you; it lasts until the scene ends.',
   [rk("Raise a dome of force until the scene ends: physical harm against those inside is reduced by 2, they hold flag.in_cover, and the first hit from outside on one of them is negated.",
       [red(2, ['harm.physical']), tgt(4), move('those inside the dome', 0, add=['flag.in_cover']), prevent('the first hit from outside the dome on one inside')], f=3, per='scene_end')],
   traits=['trait.delivery.aura', 'trait.duration.sustained'],
   x=[('allies who leave the dome', 'they are outside it'), ('a working', 'ab.counterspell')])

ab('ab.far_glass', 'The Far Glass', A + 'divination.scrying', 5, 'scrying', 'Working', 'beat',
   'Watch a named person or place in a glass from any distance.',
   'Applies to one person or place you know by name or by a token, with a glass or still water.',
   [rk("Scry for an interval: watch the person or place as if from within band.near of it; learn where it is, who is with it and what it is doing; the inquiry's clue clock ticks by your delivered reach; your next beat about it has reach one rung higher; and you hold a Precision lever on beats about it this scene.",
       [perm(4), rev('where the subject is'), rev('who is with the subject'), rev('what the subject is doing'), tick("the inquiry's clue clock", 'delivered_reach'), reach('your next beat about the subject'), lev('precision', 'beats about the subject', 'scene')], f=3, per='rest_long')],
   traits=['trait.action.concentrate'], oc=0, cost_text='a glass or a basin of still water',
   x=[('a subject under a ward against sight', '05.7.7'), ('a thread you are tied to', 'ab.trace_the_thread')])

# ====================================================================== deed.primal (casting attribute Resolve)
P = 'deed.primal.'
ab('ab.call_the_pack', 'Call the Pack', P + 'beastkin.calling', 4, 'call_pack', 'Working', 'beat',
   'Call the beasts of a place to come and fight beside you.',
   'Applies in a place where beasts live, within band.distant of you.',
   [rk("Call the beasts of the place: a pack of threat band 2 comes and fights beside you until the scene ends, acting within its nature; you learn what it has seen here; and you hold a Precision lever on beats with it this scene.",
       [summ('a pack of local beasts, threat band 2', 2, 'scene', location='within band.near of you'), perm(2), rev('what the beasts have seen here'), lev('precision', 'beats made with the pack', 'scene')], f=2, per='scene_end')],
   x=[('a place with no beasts', 'they cannot come'), ('one beast you speak with', 'ab.beast_speech')])

ab('ab.herd_lord', 'Herd-Lord', P + 'beastkin.bond', 5, 'herd_lord', 'Working', 'beat',
   'Speak for every beast in a place as their lord.',
   'Applies to every animal within band.far of you that no one else controls.',
   [rk("Speak as lord of the beasts: until the scene ends no uncontrolled animal within band.far will attack you or up to five allies, and the greatest of them, a beast of threat band 3, fights for you.",
       [restr({'methods': ['attacking the pc or the pc\'s allies']}, 'every uncontrolled animal within band.far', 'scene'), tgt(5), summ('the greatest beast present, threat band 3', 3, 'scene', location='where it stands')], f=3, per='scene_end')],
   x=[('a beast another controls', 'ab.compel; ab.lift_the_hex'), ('monsters', 'ab.know_the_beast')])

ab('ab.tidecall', 'Tidecall', P + 'elements.water', 4, 'tidecall', 'Working', 'beat',
   'Raise a wave from water and throw it.',
   'Applies to water within band.near and up to four beings within band.close of it.',
   [rk("A wave rises from the water. Up to four beings within band.close of it roll Endure (Endurance) against your effect DC: on a failure each takes Heavy crushing harm, is pushed two bands and is knocked prone.",
       [fchk('endure'), harm(3, ['harm.physical.crush'], 'each being that fails'), tgt(3), move('each being that fails', 2), cond('cond.prone', 1, 'rounds:1', 'each being that fails')], f=2)],
   check=END, spread='burst', harm_tags=['harm.physical.crush'], traits=['trait.action.attack', 'trait.delivery.area', 'trait.sense.loud'],
   x=[('a place with no water', 'there is nothing to raise'), ('drowning one being', 'ab.undertow')])

ab('ab.whirlwind', 'Whirlwind', P + 'elements.air', 5, 'whirlwind', 'Working', 'beat',
   'Wake a whirlwind that throws bodies and turns arrows.',
   'Applies to a point within band.far and up to five beings within band.close of it; it lasts until the scene ends.',
   [rk("A whirlwind rises at a point within band.far. Up to five beings within band.close of it roll Evade against your effect DC: on a failure each takes Heavy crushing harm, is thrown one band and knocked prone. Until the scene ends no missile passes through it, and beings behind it hold flag.obscured.",
       [fchk('evade'), harm(3, ['harm.physical.crush'], 'each being that fails'), tgt(4), move('each being that fails', 1), cond('cond.prone', 1, 'rounds:1', 'each being that fails'), restr({'methods': ['shooting through the whirlwind']}, 'every being', 'scene'), move('beings behind the whirlwind', 0, add=['flag.obscured'])], f=3, per='scene_end')],
   check=EVA, spread='burst', harm_tags=['harm.physical.crush'], traits=['trait.action.attack', 'trait.delivery.area', 'trait.sense.loud'],
   x=[('a gust', 'ab.gust'), ('drawing breath from one body', 'ab.stolen_breath')])

ab('ab.greenwood_rising', 'Greenwood Rising', P + 'growth.bounty', 5, 'grove', 'Working', 'beat',
   'Make a grove rise from bare ground in an hour.',
   'Applies to ground within band.near of you that can bear growing things; the grove stands.',
   [rk("Raise a grove over an interval: up to six allies in it hold flag.in_cover and regain 5 Vitality, and their poisoning ends; foes in it are slowed until the scene ends; you and your allies hold a Protective lever on beats in it this scene; and the grove is recorded as standing.",
       [move('up to six allies in the grove', 0, add=['flag.in_cover']), tgt(5), heal(5, 'each ally in the grove'), cleanse('cond.poisoned', 'each ally in the grove'), cond('cond.slowed', 1, 'scene', 'each foe in the grove'), lev('protective', 'beats in the grove', 'scene'), fact('the grove', 'standing', True)], f=3, per='rest_long')],
   x=[('salted or stone ground', 'ab.stone_shape'), ('one body', 'ab.renewal')])

ab('ab.hag_stone_charm', 'Hag-Stone Charm', P + 'hexcraft.charms', 4, 'luck_charm', 'Working', 'beat',
   'Tie a charm that turns the first bad luck aside.',
   'Applies to up to four beings who wear a charm you tie, until your next long rest.',
   [rk("Tie charms on up to four beings: until your next long rest the first hit on each is negated, each has +1 Agility defense and holds a Protective lever on its beats this scene, and the charms are recorded as yours.",
       [prevent('the first hit on a charm-bearer before your next long rest'), dedge(1, 'agility', 'the bearer wears the charm'), lev('protective', "each bearer's beats", 'scene'), tgt(3), fact('the charms', 'tied_by', 'the pc')], f=2, per='rest_long')],
   x=[('lifting a curse', 'ab.lift_the_hex'), ('a magical item', 'ab.bind_power')])

ab('ab.blackthorn_curse', 'Blackthorn Curse', P + 'hexcraft.cursing', 5, 'long_curse', 'Working', 'beat',
   'Lay a curse that clings until someone lifts it.',
   'Applies to one being within band.near whose name you know.',
   [rk("Lay the curse. The target rolls Endure (Resolve) against your effect DC: on a failure it is weakened, exposed and frightened until the curse is lifted, loses 1 Focus, cannot enter your presence uninvited while cursed, and the curse is recorded; you always know which way it lies from you.",
       [fchk('endure'), cond('cond.weakened', 1, 'until_cleansed', T), cond('cond.exposed', 1, 'until_cleansed', T), cond('cond.frightened', 1, 'until_cleansed', T), drain(1, T), restr({'methods': ['entering the caster\'s presence uninvited']}, T, 'until_cleansed'), fact(T, 'cursed_by', 'the pc'), rev('the direction of the target from the caster')], f=3, per='rest_long')],
   check=RES, traits=['trait.nature.profane'],
   x=[('a being whose name you do not know', 'ab.evil_eye'), ('lifting it', 'ab.lift_the_hex; rit.lift_curse')])

ab('ab.hawks_wings', "Hawk's Wings", P + 'shapeshifting.partial', 4, 'grow_wings', 'Form', 'beat',
   'Grow the wings of a hawk from your shoulders.',
   'Applies to yourself; the wings last until the scene ends.',
   [rk("Grow wings until the scene ends: you can fly, you take flag.aloft when you rise, you have +1 Agility defense while aloft, and the fall from losing them is softened to nothing.",
       [mode('fly', 'scene'), move('self', 0, add=['flag.aloft']), dedge(1, 'agility', 'you hold flag.aloft'), waive('harm from falling when the wings end', 'the wings end')], f=2)],
   slot='slot.movement_mode',
   x=[('the whole shape of a bird', 'ab.beast_form'), ('carrying another', 'you fly alone')])

ab('ab.ancestors_answer', 'The Ancestors Answer', P + 'spirits.ancestors', 5, 'ancestor_host', 'Working', 'beat',
   'Call the dead of a line or a land to stand with you.',
   'Applies at a grave, a barrow or a hearth of your line, or of the land you stand on.',
   [rk("Call the ancestors over an interval: they answer three questions about their line or land; the greatest of them, a being of threat band 3, stands with you until the scene ends; you hold a Precision lever on beats about their line this scene; and the calling is recorded.",
       [rev('the answer to the first question'), rev('the answer to the second question'), rev('the answer to the third question'), summ('an ancestor spirit, threat band 3', 3, 'scene'), lev('precision', 'beats about the line or land', 'scene'), fact('the ancestors', 'answered', 'the pc')], f=3, per='rest_long')],
   x=[('a place with no dead of a line', 'ab.spirit_tongue'), ('binding a spirit', 'rit.circle_of_binding')])

ab('ab.the_stilling', 'The Stilling', P + 'weather.calm', 4, 'still_weather', 'Working', 'beat',
   'Still the weather around you for a day.',
   'Applies to the weather within band.distant of you, for a day.',
   [rk("Still the weather for a day: weather counts one severity rung lower for up to six beings within band.distant, one working that raised the weather ends, the travel clock ticks one segment, and the calm is recorded.",
       [hazard(['harm.storm', 'harm.frost', 'harm.fire.heat']), tgt(5), endw('one working that raised the weather'), tick('the travel clock', 1), fact('the weather', 'stilled_by', 'the pc')], f=2, per='rest_long')],
   x=[('raising weather', 'ab.gust; ab.fog_bank'), ('a storm at sea', 'ab.storm_helm')])
