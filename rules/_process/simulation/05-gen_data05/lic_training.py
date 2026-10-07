# lic_training.py -- the 81 training licenses (one per level-2 deed tag) and the Focus licenses.
# Row: (tag suffix, name, attribute, licensed methods (what the basic verbs exclude), crude fallback or None, extra excludes)
# Fallback tuple: (verb, method, dc_shift, reach_cap, consequence)
F = lambda verb, method, shift=5, cap='limited', cons=None: (verb, method, shift, cap, cons)
BASIC = lambda verb, what: (verb, what, 0, 'standard', None)

ROWS = [
    # ---------------- martial ----------------
    ('martial.blade', 'Bladework', 'by_method', "Fight with swords, daggers and knives using their techniques (the basic Strike already covers hitting with one).", BASIC('verb.strike', 'cut or thrust with the blade untrained'), []),
    ('martial.axe', 'Axework', 'by_method', "Fight with axes using their techniques.", BASIC('verb.strike', 'swing the axe untrained'), []),
    ('martial.bludgeon', 'Bludgeon-work', 'by_method', "Fight with maces, hammers, clubs, flails and staves using their techniques.", BASIC('verb.strike', 'swing the weapon untrained'), []),
    ('martial.polearm', 'Polearm-work', 'by_method', "Fight with spears, halberds and staves at reach using their techniques.", BASIC('verb.strike', 'thrust with the polearm untrained'), []),
    ('martial.archery', 'Archery', 'agility', "Shoot bows, crossbows and slings using their techniques; string, tune and judge a bow.", BASIC('verb.strike', 'shoot untrained'), []),
    ('martial.thrown', 'Thrown weapons', 'agility', "Throw javelins, knives, axes, nets and bolas using their techniques.", BASIC('verb.strike', 'throw untrained'), []),
    ('martial.unarmed', 'Unarmed fighting', 'by_method', "Strike and wrestle with the body using its techniques.", BASIC('verb.strike', 'punch, kick or grapple untrained'), []),
    ('martial.shield', 'Shieldwork', 'by_method', "Block, bash and cover with a shield using its techniques.", BASIC('verb.evade', 'put the shield between you and the blow as cover'), []),
    ('martial.armor', 'Armored fighting', 'endurance', "Fight, march and rest in medium and heavy armor without the untrained wearer's snag (08).", F('verb.endure', 'bear the armor and its snag', 0, 'standard', 'the armor\'s untrained snag applies'), []),
    ('martial.tactics', 'Tactics', 'wits', "Read a fight, choose ground, direct a formation, plan an assault or a defense.", F('verb.observe', 'judge the fight by eye', 5, 'limited'), []),
    ('martial.mounted', 'Mounted combat', 'agility', "Fight from the saddle: strike, shoot and charge while mounted, and control a mount in a melee.", F('verb.handle', 'stay in the saddle and strike as you can', 5, 'limited', 'cond.off_balance on a failure'), ['riding to travel (verb.handle; lic.training.wilds_animals)']),
    ('martial.athletics', 'Athletics', 'might', "Feats of the trained body using their techniques (the basic Exert already covers climbing, jumping, swimming, lifting and running).", BASIC('verb.exert', 'attempt the feat untrained'), []),
    # ---------------- guile ----------------
    ('guile.stealth', 'Stealth', 'agility', "Shadow a person through a town, infiltrate a guarded place, hide a group, using their techniques (the basic Sneak already covers hiding and quiet movement).", BASIC('verb.sneak', 'hide or creep untrained'), []),
    ('guile.thievery', 'Thievery', 'agility', "Pick mechanical locks, disarm mechanical traps, cut purses, palm and switch objects under watch.", F('verb.force', 'break the lock, hasp or hinges', 0, 'standard', 'trait.sense.loud'), ['warded or magical locks (05.7.7)']),
    ('guile.deception', 'Deception', 'presence', "Run a sustained false story, a confidence game or a planned misdirection (the basic Talk already covers a simple lie).", BASIC('verb.talk', 'tell a plain lie'), []),
    ('guile.disguise', 'Disguise', 'wits', "Disguise yourself or another as a type of person; imitate a voice; forge a document, hand or seal.", F('verb.sneak', 'hide your face with hood, mud or distance', 5, 'limited'), ['passing as a specific person (ab.living_mask)']),
    ('guile.ambush', 'Ambush', 'agility', "Lay an ambush for a group, pick a killing place, strike from concealment using its techniques.", F('verb.sneak', 'wait in hiding and strike with the basic Strike', 0, 'standard'), []),
    ('guile.poisoncraft', 'Poisoncraft', 'agility', "Handle, apply and administer poisons safely; judge a dose; recognize a poisoning.", F('verb.handle', 'smear or pour the poison untrained', 5, 'limited', 'a critical failure poisons the handler'), ['brewing poison (lic.training.craft_alchemy)']),
    ('guile.escape', 'Escape', 'agility', "Slip manacles and locked bonds, break out of a cell, lose a pursuit in a crowd.", F('verb.exert', 'strain against the bonds', 5, 'limited', 'trait.sense.audible'), []),
    ('guile.streetwise', 'Streetwise', 'wits', "Find a fence, an informer or a smuggler; read cant and street signs; know whose territory this is.", F('verb.talk', 'ask openly in taverns', 5, 'limited', 'cost.exposure on a failure'), []),
    # ---------------- wilds ----------------
    ('wilds.survival', 'Survival', 'wits', "Build lasting shelter, make fire in the wet, read weather a day ahead, keep a group alive in hard country.", F('verb.handle', 'make a crude lean-to or fire', 5, 'limited'), []),
    ('wilds.tracking', 'Tracking', 'wits', "Follow a trail more than a day old or over hard ground; read number, kind and haste from sign; hunt game.", F('verb.observe', 'follow fresh, plain tracks', 5, 'limited'), []),
    ('wilds.navigation', 'Navigation', 'wits', "Keep a course without road or landmark, by stars or underground; make and read charts.", F('verb.observe', 'follow a road, a river or a visible landmark', 5, 'limited'), []),
    ('wilds.animals', 'Animal handling', 'presence', "Train an animal, ride in difficult conditions, calm a hostile beast, tend a sick one.", F('verb.handle', 'lead or ride a docile, trained animal', 5, 'limited'), []),
    ('wilds.foraging', 'Foraging', 'wits', "Find food and water for a group; identify edible, medicinal and poisonous plants; harvest materials from the wild.", F('verb.observe', 'gather what is plainly edible', 5, 'limited', 'a critical failure gathers something harmful'), []),
    ('wilds.seafaring', 'Seafaring', 'wits', "Sail, pilot and maintain a vessel; read water and wind; command a deck.", F('verb.handle', 'row or pole a small boat in calm water', 5, 'limited'), []),
    # ---------------- lore ----------------
    ('lore.history', 'History', 'intellect', "Recall specialist knowledge of past events, peoples, heraldry, ruins and legends.", F('verb.recall', 'recall what your own people commonly tell', 5, 'limited'), []),
    ('lore.languages', 'Languages', 'intellect', "Translate between tongues you hold, decipher scripts and ciphers, learn a language at double pace.", F('verb.talk', 'gesture, tone and shared nouns', 5, 'limited'), ['speaking a language you do not hold (lic.lang.*)']),
    ('lore.bestiary', 'Bestiary', 'intellect', "Recall specialist knowledge of creatures: natures, habits, weaknesses.", F('verb.recall', 'recall the common tales about such a creature', 5, 'limited'), []),
    ('lore.medicine', 'Medicine', 'intellect', "Diagnose illness and poison; perform surgery; treat wounds and afflictions (ch.07's treatment rules).", F('verb.handle', 'first aid: stabilize only', 0, 'limited'), ['magical healing (deed.divine.healing)']),
    ('lore.engineering', 'Engineering', 'intellect', "Understand, assess and direct work on mechanisms, structures, siege works and waterworks.", F('verb.observe', 'look for what is plainly broken or loose', 5, 'limited'), ['building the thing (lic.training.craft_building, craft_artifice)']),
    ('lore.law', 'Law and custom', 'intellect', "Recall and argue law, rights, contracts and precedent; draft a binding document.", F('verb.recall', 'recall what everyone knows is forbidden', 5, 'limited'), []),
    ('lore.arcana', 'Arcana', 'intellect', "Identify spells, wards and enchanted items of any branch; know the theory of magic and the planes; design a rite (05.8.4).", F('verb.recall', 'recall common superstition about magic', 10, 'limited'), ['casting (the magic branches)']),
    ('lore.religion', 'Religion', 'intellect', "Recall specialist knowledge of gods, rites, holy orders, the dead and the profane; conduct a lay service.", F('verb.recall', 'recall the common observances of your own faith', 5, 'limited'), ['divine power (deed.divine)']),
    ('lore.investigation', 'Investigation', 'intellect', "Search records, reconstruct events from evidence, conduct a formal inquiry.", F('verb.observe', 'search by eye and hand', 5, 'limited'), []),
    # ---------------- arcane (crude fallback: none) ----------------
    ('arcane.fire', 'Fire sorcery', 'intellect', "Cast the fire spells you hold; small workings of flame and heat; sense arcane magic within band.near; end your own workings; cast your branch working, Force Bolt (ab.force_bolt), at no Focus and in no slot (05.7.11).", None, []),
    ('arcane.frost', 'Frost sorcery', 'intellect', "Cast the frost spells you hold; small workings of cold and ice; sense arcane magic within band.near; end your own workings; cast your branch working, Force Bolt (ab.force_bolt), at no Focus and in no slot (05.7.11).", None, []),
    ('arcane.storm', 'Storm sorcery', 'intellect', "Cast the storm spells you hold; small workings of spark, breeze and sound; sense arcane magic within band.near; end your own workings; cast your branch working, Force Bolt (ab.force_bolt), at no Focus and in no slot (05.7.11).", None, []),
    ('arcane.earth', 'Earth sorcery', 'intellect', "Cast the earth spells you hold; small workings of stone, metal and soil; sense arcane magic within band.near; end your own workings; cast your branch working, Force Bolt (ab.force_bolt), at no Focus and in no slot (05.7.11).", None, []),
    ('arcane.illusion', 'Illusion', 'intellect', "Cast the illusions you hold; small workings of false light, color and sound; sense arcane magic within band.near; end your own workings; cast your branch working, Force Bolt (ab.force_bolt), at no Focus and in no slot (05.7.11).", None, []),
    ('arcane.divination', 'Divination', 'intellect', "Cast the divinations you hold; small workings (know north, the hour, whether a thing in hand is magical); sense arcane magic within band.near; end your own workings; cast your branch working, Force Bolt (ab.force_bolt), at no Focus and in no slot (05.7.11).", None, []),
    ('arcane.warding', 'Warding', 'intellect', "Cast the wards and counters you hold; small workings (a tell-tale thread on a door, a chalk line that smudges if crossed); sense arcane magic within band.near; end your own workings; cast your branch working, Force Bolt (ab.force_bolt), at no Focus and in no slot (05.7.11).", None, []),
    ('arcane.mind', 'Mind sorcery', 'intellect', "Cast the mind spells you hold; small workings (a word carried to one ear within band.close; a name called to mind); sense arcane magic within band.near; end your own workings; cast your branch working, Force Bolt (ab.force_bolt), at no Focus and in no slot (05.7.11).", None, []),
    ('arcane.summoning', 'Summoning', 'intellect', "Cast the summonings you hold; small workings (a spark of an unseen hand that can lift a cup); sense arcane magic within band.near; end your own workings; cast your branch working, Force Bolt (ab.force_bolt), at no Focus and in no slot (05.7.11).", None, []),
    ('arcane.necromancy', 'Necromancy', 'intellect', "Cast the necromancies you hold; small workings (know whether a body is dead and how long; wilt a cut flower); sense arcane magic within band.near; end your own workings; cast your branch working, Force Bolt (ab.force_bolt), at no Focus and in no slot (05.7.11).", None, []),
    ('arcane.alteration', 'Alteration', 'intellect', "Cast the alterations you hold; small workings (mend a tear, clean a stain, warm or cool what you hold); sense arcane magic within band.near; end your own workings; cast your branch working, Force Bolt (ab.force_bolt), at no Focus and in no slot (05.7.11).", None, []),
    # ---------------- divine ----------------
    ('divine.healing', 'Sacred healing', 'presence', "Cast the healing prayers you hold; small workings (ease pain for a breath, stop a nosebleed, know whether a body is sick); sense divine magic within band.near; cast your branch working, Rebuke (ab.rebuke), at no Focus and in no slot (05.7.11).", None, []),
    ('divine.warding', 'Sacred warding', 'presence', "Cast the wards and blessings you hold; small workings (bless food and water as wholesome, mark a threshold with your keeper's sign); sense divine magic within band.near; cast your branch working, Rebuke (ab.rebuke), at no Focus and in no slot (05.7.11).", None, []),
    ('divine.smiting', 'Smiting', 'presence', "Cast the smiting prayers you hold; small workings (your sign gives a candle's light); sense divine magic within band.near; cast your branch working, Rebuke (ab.rebuke), at no Focus and in no slot (05.7.11).", None, []),
    ('divine.rites', 'Rites', 'presence', "Perform the ceremonies of your faith with their sacred effect: blessings, funerals, marriages, consecrations; lead the rites you know; cast your branch working, Rebuke (ab.rebuke), at no Focus and in no slot (05.7.11).", F('verb.talk', 'speak the lay words of the ceremony, without sacred effect', 0, 'limited'), []),
    ('divine.oaths', 'Oaths', 'presence', "Swear, witness and enforce sacred vows with the prayers you hold; know whether an oath taken before you was meant; cast your branch working, Rebuke (ab.rebuke), at no Focus and in no slot (05.7.11).", F('verb.talk', 'give your plain word', 0, 'limited'), []),
    ('divine.revelation', 'Revelation', 'presence', "Cast the prayers of revelation you hold; small workings (know which way your keeper's nearest holy place lies); sense divine magic within band.near; cast your branch working, Rebuke (ab.rebuke), at no Focus and in no slot (05.7.11).", None, []),
    ('divine.exorcism', 'Exorcism', 'presence', "Cast the turnings and castings-out you hold; small workings (know whether an undead or fiend is within band.close); sense divine magic within band.near; cast your branch working, Rebuke (ab.rebuke), at no Focus and in no slot (05.7.11).", None, []),
    ('divine.pact', 'Pact', 'presence', "Call on the power you bargained with through the invocations you hold; small workings (its mark shows or hides on your skin; a whisper of its attention); sense profane magic within band.near; cast your branch working, Rebuke (ab.rebuke), at no Focus and in no slot (05.7.11).", None, []),
    # ---------------- primal ----------------
    ('primal.growth', 'Growth', 'resolve', "Cast the growth workings you hold; small workings (a bud opens, a seed sprouts in your hand, a vine shifts aside); sense primal magic within band.near; cast your branch working, Wild Lash (ab.wild_lash), at no Focus and in no slot (05.7.11).", None, []),
    ('primal.beastkin', 'Beast-kinship', 'resolve', "Cast the beast-kin workings you hold; small workings (know a beast's mood, call a small bird to your hand); sense primal magic within band.near; cast your branch working, Wild Lash (ab.wild_lash), at no Focus and in no slot (05.7.11).", None, []),
    ('primal.weather', 'Weather-working', 'resolve', "Cast the weather workings you hold; small workings (a breath of wind, know the weather until nightfall); sense primal magic within band.near; cast your branch working, Wild Lash (ab.wild_lash), at no Focus and in no slot (05.7.11).", None, []),
    ('primal.shapeshifting', 'Shapeshifting', 'resolve', "Cast the shape-workings you hold; small workings (your eyes or voice take a beast's cast for a moment); sense primal magic within band.near; cast your branch working, Wild Lash (ab.wild_lash), at no Focus and in no slot (05.7.11).", None, []),
    ('primal.spirits', 'Spirit-speaking', 'resolve', "Cast the spirit-workings you hold; small workings (know whether a spirit is present here); sense primal magic within band.near; cast your branch working, Wild Lash (ab.wild_lash), at no Focus and in no slot (05.7.11).", None, []),
    ('primal.elements', 'Raw elements', 'resolve', "Cast the elemental workings you hold; small workings (coax an ember to flame, still a cup of water, firm a handful of earth); sense primal magic within band.near; cast your branch working, Wild Lash (ab.wild_lash), at no Focus and in no slot (05.7.11).", None, []),
    ('primal.hexcraft', 'Hexcraft', 'resolve', "Cast the hexes and unhexings you hold; make small charms (a knot against nightmares, a sign over a door); sense primal magic and curses within band.near; cast your branch working, Wild Lash (ab.wild_lash), at no Focus and in no slot (05.7.11).", F('verb.handle', 'hang a folk charm with no power in it', 0, 'limited'), []),
    # ---------------- influence ----------------
    ('influence.persuasion', 'Persuasion', 'presence', "Carry a formal argument, a suit or a negotiation using its techniques (the basic Talk already covers persuading).", BASIC('verb.talk', 'make your case plainly'), []),
    ('influence.command', 'Command', 'presence', "Direct a body of people in action: drill, order of march, a company in a fight.", F('verb.talk', 'shout an order to those who already follow you', 5, 'limited'), []),
    ('influence.performance', 'Performance', 'presence', "Perform music, oratory, story or spectacle to a professional standard, for pay or effect.", F('verb.talk', 'sing or tell a tale as anyone can', 5, 'limited'), []),
    ('influence.intimidation', 'Intimidation', 'presence', "Conduct an interrogation; cow a group; make a threat carry without a weapon drawn.", BASIC('verb.talk', 'threaten plainly'), []),
    ('influence.intrigue', 'Intrigue', 'wits', "Work a court or council: build an alliance, start or kill a rumor, trade favors, find leverage.", F('verb.talk', 'ask openly who stands with whom', 5, 'limited', 'cost.exposure on a failure'), []),
    ('influence.trade', 'Trade', 'wits', "Appraise goods, run a venture, find a market, bargain at a merchant's standard.", F('verb.talk', 'haggle as a customer', 5, 'limited'), []),
    ('influence.etiquette', 'Etiquette', 'presence', "Move correctly through formal and foreign custom: precedence, forms of address, gifts, table and court.", F('verb.observe', 'copy what those around you do', 5, 'limited', 'a critical failure gives offense'), []),
    ('influence.insight', 'Insight', 'wits', "Read motive, mood and deceit in a person using its techniques (the basic Observe already covers reading a person).", BASIC('verb.observe', 'watch their face and hands'), []),
    ('influence.teaching', 'Teaching', 'presence', "Instruct another in a training or technique you hold, as a mentor for learning clocks (05.8.5, 05.9.4).", F('verb.help', 'show them once and correct them', 5, 'limited', 'the learning clock ticks 1 instead of the mentor\'s rate'), []),
    # ---------------- craft ----------------
    ('craft.smithing', 'Smithing', 'might', "Forge and mend weapons, armor and tools of metal (08's crafting).", F('verb.handle', 'crude repair: straighten, bind, patch', 5, 'limited', 'the item is serviceable until the next rest_long only; worn, common or fine items only (08.6.7)'), []),  # [revision: I-092]
    ('craft.woodcraft', 'Woodcraft', 'agility', "Make bows, shafts, furniture, carts and carved work; frame a structure in timber.", F('verb.handle', 'lash and wedge a crude fix', 5, 'limited'), []),
    ('craft.leathercraft', 'Leathercraft', 'agility', "Tan hides and make or mend leather goods, harness and light armor.", F('verb.handle', 'stitch a crude patch', 5, 'limited'), []),
    ('craft.textiles', 'Textiles', 'agility', "Spin, weave, sew and make rope; tailor garments to a purpose.", F('verb.handle', 'tie and patch crudely', 5, 'limited'), []),
    ('craft.alchemy', 'Alchemy', 'intellect', "Brew potions, poisons, reagents, remedies and incendiaries with a kit (08's recipes).", F('verb.handle', 'steep a folk tea with no alchemical effect', 10, 'limited', 'a critical failure spoils the reagents'), []),
    ('craft.cookery', 'Cookery', 'wits', "Cook for a company, preserve food, brew, and lay a table that honors a guest.", BASIC('verb.handle', 'cook a plain meal'), []),
    ('craft.building', 'Building', 'intellect', "Raise and repair works in stone and timber: walls, bridges, fortifications, shelters beyond crude.", F('verb.force', 'pile and prop a crude barrier', 5, 'limited'), []),
    ('craft.artifice', 'Artifice', 'intellect', "Make and repair locks, traps, clockwork and engines.", F('verb.handle', 'rig a crude snare or wedge', 5, 'limited'), []),
    ('craft.jewelcraft', 'Jewelcraft', 'agility', "Cut gems and work fine metal; judge stones and settings.", F('verb.observe', 'judge by shine and weight', 10, 'limited'), []),
    ('craft.enchanting', 'Enchanting', 'intellect', "Inscribe and imbue items with magical properties (08's enchanting; rit.imbue). Requires a magic training license of the property's branch.", None, ['an enchanter with no magic training license (acquire one first)']),
    ('craft.scribing', 'Scribing', 'intellect', "Copy texts accurately, draw maps and plans, keep records in a fair hand.", F('verb.handle', 'scrawl notes and a rough sketch', 5, 'limited'), []),
]

MAGIC = ('arcane', 'divine', 'primal')
REQUIRES = {
    'arcane': "literacy, and a text or teacher of the school (the region's seed may tighten, 12.16.5)",
    'divine': "a keeper that accepts you: a fact pc.keeper.<school> written when the license is acquired (05.7.4)",
    'primal': "a place or spirit that accepts you: an established fact, or the Oracle at a place of resonance (05.7.3)",
}


def lic_id(tag_suffix):
    return 'lic.training.' + tag_suffix.replace('.', '_')


def fallback_map():
    out = {}
    for suf, name, attr, methods, fb, exc in ROWS:
        tag = 'deed.' + suf
        if fb is None:
            out[tag] = 'none'
        else:
            out[tag] = dict(verb=fb[0], method=fb[1], dc_shift=fb[2], reach_cap=fb[3], consequence=fb[4])
    return out


def build(TAGS):
    entries = []
    for suf, name, attr, methods, fb, exc in ROWS:
        tag = 'deed.' + suf
        assert tag in TAGS and TAGS[tag]['level'] == 2, tag
        branch = suf.split('.')[0]
        magic = branch in MAGIC
        tech = "hold, learn (05.8.5) and emulate (05.5.4) abilities whose first tag is at or under %s, and stretch them at your grade's price (T-05-6)" % tag
        e = dict(
            id=lic_id(suf), name=name, kind='training', tags=[tag],
            principle="Practise the trade or art of %s as one trained in it." % name.lower(),
            scope="%s Also: %s. The grade caps the obstacle tier at which these methods can succeed: trained Hard, expert Very hard, master Legendary." % (methods, tech),
            excludes=[dict(what=x, needs=x[x.find('(') + 1:-1] if '(' in x else 'its own license') for x in exc] + [
                dict(what='methods and abilities of any other level-2 deed tag', needs='that tag\'s own lic.training.* license'),
                dict(what='an ability of this tag that you neither hold nor have witnessed', needs='a pick (04.8.4), a teacher or text (05.8.5), or lic.call.open_art')],
            grades=[dict(grade='trained', scope='licensed methods up to Hard obstacles; techniques of min_tier 1-2; stretch DC +5, +1 Focus, Limited reach; one flare'),
                    dict(grade='expert', scope='licensed methods up to Very hard obstacles; techniques of min_tier 1-4; stretch DC +5, +1 Focus, Standard reach; one flare'),
                    dict(grade='master', scope='licensed methods up to Legendary obstacles; techniques of min_tier 1-5; stretch DC +0, +1 Focus, Standard reach; two flares')],
            attribute=attr,
            grants_competence=[dict(tag=tag, value=2, when='acquired by the mentor or text path (an origin sets its own value, at most +2; a calling sets its own, 04.5.2)')],
            crude_fallback=('none' if fb is None else dict(verb=fb[0], method=fb[1], dc_shift=fb[2], reach_cap=fb[3], consequence=fb[4])),
            stretch=dict(dc_shift=5, cost_add=1, reach_cap='limited', within='principle', by_grade={'expert': dict(dc_shift=5, cost_add=1, reach_cap='standard'), 'master': dict(dc_shift=0, cost_add=1, reach_cap='standard')}),
            emulate=dict(allowed_for="active abilities whose first tag is at or under %s, that you have witnessed (a pc.witnessed fact), with min_tier within your grade's technique cap (trained 2, expert 4, master 5); not oath-gated, not adversary_only" % tag,
                         dc_shift=5, cost_mult=2, reach_cap='limited',
                         crit_fail=({'effect_id': 'eff.deal_harm', 'params': {'severity': 'the miscast of the branch, one rung heavier (05.7.5)', 'harm_tags': ['harm.arcane.raw'], 'target': 'self'}} if magic else {'effect_id': 'eff.apply_condition', 'params': {'condition': 'cond.off_balance', 'severity': 'S1', 'duration': 'rounds:1', 'target': 'self'}}),
                         learn_clock=dict(name='learning <ability>', kind='project', segments='6 (min_tier 1-2) | 8 (3-4) | 12 (5)', visibility='public', direction='fill',
                                          tick_sources=[dict(on='a successful emulation of the ability', ticks='delivered_reach'), dict(on='a training week with a mentor who holds it', ticks=3), dict(on='a week of study from a text that teaches it', ticks=2), dict(on='a week of practice alone after witnessing it', ticks=1)],
                                          on_complete=dict(effects=[{'effect_id': 'eff.grant_license', 'params': {'license': 'the learned ability', 'grade': 'rank 1', 'duration': 'permanent'}}], interrupting=False, then='close'))),
            acquisition_paths=[
                dict(type='origin', detail='granted by an origin at creation (ch.02)', clock=None, requires=None),
                dict(type='mentor', detail='a training week with a mentor ticks 2 (ch.15; writes cnt.training)', clock='clk.train (8 segments, project, public)', requires="a mentor who holds lic.call.proof for this tag or this license at expert" + ("; " + REQUIRES[branch] if magic else "")),
                dict(type='project', detail='a week of study from a manual ticks 1', clock='clk.train (8 segments, project, public)', requires="a text that teaches the trade" + ("; " + REQUIRES[branch] if magic else "")),
                dict(type='recognition', detail="a calling whose key is at or above this tag: its Mark (lic.call.mark) gives use of this license at the tier's grade (04.5.1)", clock=None, requires=None)],
            source='data',
            lifecycle='provisional', basis=['05.9', '00.12.1', '04 Interface request 5', 'DL-05-06'])
        entries.append(e)
    return entries


FOCUS_LICENSES = [
    dict(id='lic.focus.push', name='Push', kind='basic_verb', tags=['deed'],
         principle="Spend your reserves to make an ordinary effort count for more.",
         scope="Spend 1 Focus on your own declared, rolled beat whose primary deed tag (or an ancestor) carries competence above the PC floor: choose reach +1 rung or stakes -1 rung. Once per beat, declared at the OFFER (05.6.7).",
         excludes=[dict(what='a bonus to the roll or a change to the DC', needs='a lever citing an established fact (00.3.9)'), dict(what='a resisted check or an Oracle question', needs='nothing: a push applies to declared beats only'), dict(what='a beat at a tag where you have only the floor', needs='training in that tag (05.9.4)')],
         attribute='by_method', crude_fallback='none', stretch=None, emulate=None,
         effects=[{'effect_id': 'eff.reach_step', 'params': {'ladder': 'reach', 'steps': 1, 'applies_when': 'the pushed beat, when the player chose reach'}}, {'effect_id': 'eff.stakes_step', 'params': {'ladder': 'stakes', 'steps': -1, 'applies_when': 'the pushed beat, when the player chose stakes'}}],
         cost={'focus': 1}, limits={'per': 'beat_end', 'uses': 1},
         acquisition_paths=[dict(type='origin', detail='held by every character from creation', clock=None, requires=None)],
         source='every character', lifecycle='provisional', basis=['05.6.7', 'C:P2', 'R3 #9', 'DL-05-12']),
    dict(id='lic.focus.reserve', name='The Reserve', kind='training', tags=['deed.lore.arcana.theory'],
         principle="Set aside your own reserves in a vessel and take back exactly what you set aside.",
         scope="Bank Focus into a vessel (an item tagged item.tool.implement that you made or have kept for a season) and draw it later at a ratio of 1 to 1: capacity 2, or 3 when your highest tier is 3 or more, or 4 at tier 5 (05.6.12).",
         excludes=[dict(what="drawing from another's vessel", needs='this license and that vessel in hand: it is then yours to draw'), dict(what='banking above capacity or without a day at the lowered maximum', needs='nothing: the bound is fixed')],
         attribute='resolve', crude_fallback='none', stretch=None, emulate=None,
         acquisition_paths=[dict(type='mentor', detail='a training week with one who holds it ticks 2', clock='clk.train (8 segments, project, public)', requires='any training license'),
                            dict(type='project', detail='a week of study from a text that teaches it ticks 1', clock='clk.train (8 segments, project, public)', requires='a text'),
                            dict(type='origin', detail='an origin may grant it (ch.02; the region\'s seed, 12.16.7)', clock=None, requires=None)],
         source='data', lifecycle='provisional', basis=['05.6.12', 'R2 #8 (Feruchemy)', 'DL-05-15']),
]
