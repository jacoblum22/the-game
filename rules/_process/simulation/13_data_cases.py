# 13_data_cases.py -- the March's investigation cases (15.9; data/investigation.yaml#cases shape, case.mill_fire is
# the model): sealed solutions, clue contents, conclusion nodes, placements (>= 3 per necessary node, 2 holder kinds,
# 2 method kinds, 1 core, 2 places), two reserves per necessary node, fallbacks and opposition clocks.
# Objects named as holders are listed in OBJECTS (entity kind object; 11's subtype) with their place.
# Validated by 13-gen_region.py (15.9.4).

OBJECTS = [
    {"id": "obj.thallen.harrowby_bellframe", "name": "Harrowby's bell-frame and its empty bell", "place": "loc.harrowby.green", "facts": {"true_bell": True, "clapper": "missing"}},
    {"id": "obj.thallen.bellpit_stair", "name": "the collapsed stair behind the bell-frame", "place": "loc.harrowby.green"},
    {"id": "obj.harrowby_clapper", "name": "Harrowby's stolen clapper", "place": "loc.harrowby_bellpit", "facts": {"hidden_in": "the old casting-hole"}},
    {"id": "obj.thallen.last_bell_pin", "name": "the Last Bell's clapper-pin", "place": "loc.tolling.belltower", "facts": {"filed": True}},
    {"id": "obj.thallen.ysmay_cell", "name": "Sister Ysmay's cell in the chapter-house", "place": "loc.tolling.belltower"},
    {"id": "obj.thallen.court_roll", "name": "an Orrowan court-roll of the royal cousins (salvaged)", "place": "loc.tolling.library"},
    {"id": "obj.thallen.gatehouse_roll", "name": "the household roll in Orsolin Manor's gatehouse", "place": "loc.orsolin_manor"},
    {"id": "obj.thallen.treaty_stone_text", "name": "the Treaty Stone's half-chiselled inscription", "place": "loc.old_ford_stone"},
    {"id": "obj.thallen.library_register", "name": "the Library's salvaged register of Orrowan documents", "place": "loc.tolling.library"},
    {"id": "obj.thallen.removal_docket", "name": "the Weigh-house archive's removal docket", "place": "loc.tolling.weighhouse"},
    {"id": "obj.thallen.vantry_treaty", "name": "Tolling's copy of the Treaty of the Ford, in the Margravine's iron chest", "place": "loc.vantry_keep"},
    {"id": "obj.thallen.vey_treaty", "name": "the Vey family's sealed copy of the Treaty of the Ford", "place": "loc.orsolin_manor"},
    {"id": "obj.aude_journal", "name": "the last journal of Aude, Bell-Prior of Sael", "place": "loc.caddow_tower", "facts": {"teaches": "the truth of the Unsounding (sec.aude.why)"}},
    {"id": "obj.mother_bell", "name": "the Mother Bell of Sael", "place": "loc.sael", "facts": {"true_bell": True, "cracked": True}},
]

def P(id, holder, kind, method, access, content, nodes, request_size=None, detect_tier=None, direct=False, prerequisites=(), reveals_lead=(), invites=()):
    d = dict(id=id, holder=holder, holder_kind=kind, method=method, access=access, content=content, direct=direct, nodes=list(nodes),
             reveals_lead=list(reveals_lead), invites=list(invites), status="unfound")
    if request_size:
        d["request_size"] = request_size
    if detect_tier:
        d["detect_tier"] = detect_tier
    if prerequisites:
        d["prerequisites"] = list(prerequisites)
    return d

def R(id, holder_text, kind, method, access, content, nodes, place, request_size=None, detect_tier=None):
    d = dict(id=id, holder=holder_text, holder_kind=kind, method=method, access=access, content=content, nodes=list(nodes), place=place)
    if request_size:
        d["request_size"] = request_size
    if detect_tier:
        d["detect_tier"] = detect_tier
    return d

S, I, RD, ST, RS, SV, IN = "imethod.search", "imethod.inquiry", "imethod.read", "imethod.study", "imethod.research", "imethod.surveillance", "imethod.interrogation"

CASES = [
    # ================================================================== the opening case
    dict(id="case.silent_bells", name="The silent bells", tags=["situation.investigation", "org.cult.doomsday"],
         atmosphere="theme: a gentle hand that wants everyone asleep", begins_at="loc.tolling", thread_kind="situation",
         solution=[
             {"fact": "sol.silent_bells.thief", "value": "Dunstan Fell, a Woken drover of the Hushed Choir, stole Harrowby's clapper before midnight on Ringing-eve and hid it in the bell-pit under the green"},
             {"fact": "sol.silent_bells.pin", "value": "Sister Ysmay, sacristan of the Last Bell, has filed its clapper-pin night by night; the dawn stroke missed when the pin bound"},
             {"fact": "sol.silent_bells.choir", "value": "both serve the Hushed Choir, which means to silence the Last Bell so the Quiet may take Tolling into its peace"},
             {"fact": "sol.silent_bells.cantor", "value": "Sister Ysmay Tollard is the Cantor of the Hushed Choir"},
             {"fact": "sol.silent_bells.next", "value": "the Choir gathers at the Standing Folk of Copple Field at each new moon; its goal clock (clk.thallen.choir_goal) is the Last Bell's countdown"}],
         clues={
             "c1": "Harrowby's clapper was lifted off its pin, not torn away: the work of someone who knew bells",
             "c2": "the print of a crook's iron butt and fresh moss scrapings on the bell-pit stair",
             "c3": "Tobin saw a tall Woken drover with a bell-tongue lashed to his crook lift the clapper before midnight, cursing it in Orrowan with a Caddow accent",
             "c4": "Jessamy saw 'the quiet man' carry a sack down behind the bell-frame and come up without it",
             "c5": "the clapper itself, in the bell-pit's casting-hole, with a hand-over-mouth sign drawn in moss beside it and a line of an Orrowan lullaby chalked above",
             "c6": "Dunstan Fell drives Pell's salvage carts from Bellhollow, carries a crook with a bell-tongue lashed to it, and was away on Ringing-eve",
             "c7": "the Cellar Kin sold a bell-wright's fine file and two Orrowan clapper-pins this winter to Dunstan Fell",
             "c8": "the Last Bell's clapper-pin is filed bright along one side: a filed pin binds",
             "c9": "the pin bound at the dawn stroke; in all his years on the rope the ringer never felt it stick",
             "c10": "a pin that binds like that has been filed; Hrolla has seen it done to sabotage a foundry bell",
             "c11": "only the sacristan handles the Last Bell's clapper and pin; Sister Ysmay oils them every night",
             "c12": "Quillon copied an Orrowan fragment for Sister Ysmay last winter: a rite 'to lay a bell to sleep'",
             "c13": "the hand-over-mouth is the sign of those who serve the silence; the Mossmothers have found it cut into trees at the Hem",
             "c14": "at the new moon a choir gathers among the Standing Folk of Copple Field; its Cantor sings in Orrowan behind a veil of moss",
             "c15": "Dunstan Fell's confession: he took the clapper on the Cantor's order; the Cantor is Sister Ysmay",
             "c16": "in Ysmay's cell: a bell-wright's fine file in her sewing box and a hand-mirror wrapped in moss"},
         nodes=[
             dict(id="clu.silent_bells.n1", name="Harrowby's bell was silenced on purpose", fact="Harrowby's bell was silenced deliberately, by someone who knew bells", sealed_fact="sol.silent_bells.thief",
                  necessary=True, deducible_from=[["c1", "c2"], ["c5"], ["c3", "c4"]], points_to=["clu.silent_bells.n2", "clu.silent_bells.n3"], prerequisites=[]),
             dict(id="clu.silent_bells.n2", name="Dunstan Fell is the thief", fact="the thief is Dunstan Fell, a Woken drover", sealed_fact="sol.silent_bells.thief",
                  necessary=True, deducible_from=[["c3", "c6"], ["c2", "c6"], ["c7", "c3"], ["c15"]], points_to=["clu.silent_bells.n3"], prerequisites=[]),
             dict(id="clu.silent_bells.n3", name="the Hushed Choir means to silence the Last Bell", fact="the thieves are the Hushed Choir, servants of the Quiet, who mean to silence the Last Bell", sealed_fact="sol.silent_bells.choir",
                  necessary=True, deducible_from=[["c5", "c13"], ["c12", "c13"], ["c14"], ["c15"]], points_to=["clu.silent_bells.n5"], prerequisites=[]),
             dict(id="clu.silent_bells.n4", name="the Last Bell's pin was filed", fact="the Last Bell's missed stroke was sabotage: its clapper-pin has been filed", sealed_fact="sol.silent_bells.pin",
                  necessary=True, deducible_from=[["c8"], ["c9", "c10"], ["c9", "c7"]], points_to=["clu.silent_bells.n5"], prerequisites=[]),
             dict(id="clu.silent_bells.n5", name="Sister Ysmay is the Cantor", fact="Sister Ysmay Tollard is the Cantor of the Hushed Choir", sealed_fact="sol.silent_bells.cantor",
                  necessary=True, deducible_from=[["c11", "c8"], ["c11", "c12"], ["c14", "c11"], ["c16", "c11"], ["c15"]], points_to=[], prerequisites=[])],
         placements=[
             P("clu.silent_bells.n1.p1", "obj.thallen.harrowby_bellframe", "object", S, "core", "c1", ["clu.silent_bells.n1"], invites=["lore.craft.bell_hanging"]),
             P("clu.silent_bells.n1.p2", "obj.harrowby_clapper", "object", S, "core", "c5", ["clu.silent_bells.n1", "clu.silent_bells.n3"], direct=True, prerequisites=["pc inside loc.harrowby_bellpit's heart"]),
             P("clu.silent_bells.n1.p3", "npc.tobin_reave", "person", I, "core", "c3", ["clu.silent_bells.n1", "clu.silent_bells.n2"], request_size="R2",
               prerequisites=["Tobin's refusal lifted: no Cask is accusing him in the scene"]),
             P("clu.silent_bells.n1.p4", "npc.jessamy_cask", "person", I, "core", "c4", ["clu.silent_bells.n1", "clu.silent_bells.n2"], request_size="R1",
               prerequisites=["Jessamy's refusal lifted: her mother is not present"], reveals_lead=["clu.silent_bells.n2.p1"]),
             P("clu.silent_bells.n2.p1", "obj.thallen.bellpit_stair", "object", S, "core", "c2", ["clu.silent_bells.n1", "clu.silent_bells.n2"]),
             P("clu.silent_bells.n2.p2", "npc.wick_pell", "person", I, "core", "c6", ["clu.silent_bells.n2"], request_size="R1"),
             P("clu.silent_bells.n2.p3", "npc.lark_mossbank", "person", I, "rolled", "c7", ["clu.silent_bells.n2", "clu.silent_bells.n4"], request_size="R3"),
             P("clu.silent_bells.n2.p4", "npc.dunstan_fell", "person", IN, "rolled", "c15", ["clu.silent_bells.n2", "clu.silent_bells.n3", "clu.silent_bells.n5"], request_size="R5", direct=True),
             P("clu.silent_bells.n3.p1", "npc.ilsabet_grey", "person", I, "core", "c13", ["clu.silent_bells.n3"], request_size="R1", prerequisites=["the PC has seen the sign (c5 or a reserve)"]),
             P("clu.silent_bells.n3.p2", "npc.ansel_quillon", "person", I, "rolled", "c12", ["clu.silent_bells.n3", "clu.silent_bells.n5"], request_size="R2"),
             P("clu.silent_bells.n3.p3", "loc.standing_folk", "place", SV, "rolled", "c14", ["clu.silent_bells.n3", "clu.silent_bells.n5"], detect_tier="moderate", prerequisites=["the new moon"]),
             P("clu.silent_bells.n4.p1", "obj.thallen.last_bell_pin", "object", ST, "rolled", "c8", ["clu.silent_bells.n4", "clu.silent_bells.n5"], detect_tier="hard", prerequisites=["pc in the ringing-loft (the Prior's leave, 15.4.1 R3, or by stealth)"]),
             P("clu.silent_bells.n4.p2", "npc.jory_halloway", "person", I, "core", "c9", ["clu.silent_bells.n4"], request_size="R1"),
             P("clu.silent_bells.n4.p3", "npc.hrolla_gorrund", "person", I, "core", "c10", ["clu.silent_bells.n4"], request_size="R2", prerequisites=["the PC knows c9 or c8"]),
             P("clu.silent_bells.n5.p1", "npc.bram_ottery", "person", I, "core", "c11", ["clu.silent_bells.n5"], request_size="R1"),
             P("clu.silent_bells.n5.p2", "npc.hollis_brede", "person", I, "core", "c11", ["clu.silent_bells.n5"], request_size="R1"),
             P("clu.silent_bells.n5.p3", "obj.thallen.ysmay_cell", "object", S, "rolled", "c16", ["clu.silent_bells.n5", "clu.silent_bells.n4"], detect_tier="hard", prerequisites=["pc in the chapter-house cells"])],
         reserve=[
             R("clu.silent_bells.r1", "a miller's wife of Harrowby who heard the clapper-chain at midnight", "person", I, "core", "c1", ["clu.silent_bells.n1"], "loc.harrowby", request_size="R1"),
             R("clu.silent_bells.r2", "the bell's own pin, bright from careful work", "object", S, "core", "c1", ["clu.silent_bells.n1"], "loc.harrowby.green"),
             R("clu.silent_bells.r3", "a Copsey eel-catcher who sold Dunstan a sack on Ringing-eve", "person", I, "core", "c6", ["clu.silent_bells.n2"], "loc.copsey", request_size="R1"),
             R("clu.silent_bells.r4", "Pell's Bellhollow tally-book: 'D. Fell, away, Ringing-eve'", "document", RS, "core", "c6", ["clu.silent_bells.n2"], "loc.bellhollow"),
             R("clu.silent_bells.r5", "a moss thong with a tiny cracked bell on a dead hush-hound", "object", S, "core", "c13", ["clu.silent_bells.n3"], "loc.brightfields"),
             R("clu.silent_bells.r6", "a Woken of the Waking House who was asked to join 'the quiet singers'", "person", I, "core", "c14", ["clu.silent_bells.n3"], "loc.tolling.hearth_shrine", request_size="R2"),
             R("clu.silent_bells.r7", "Sister Mab, the other dawn ringer, who felt the pin bind a week ago too", "person", I, "core", "c9", ["clu.silent_bells.n4"], "loc.tolling.belltower", request_size="R1"),
             R("clu.silent_bells.r8", "bright filings on the loft floor under the Last Bell", "object", S, "rolled", "c8", ["clu.silent_bells.n4"], "loc.tolling.belltower", detect_tier="moderate"),
             R("clu.silent_bells.r9", "a Bellwarden novice who saw Ysmay leave the tower at the new moon", "person", I, "core", "c11", ["clu.silent_bells.n5"], "loc.tolling.belltower", request_size="R2"),
             R("clu.silent_bells.r10", "Ysmay buying moss-candles from Perrin Rushlight in Copsey", "event", SV, "rolled", "c16", ["clu.silent_bells.n5"], "loc.copsey", detect_tier="moderate")],
         fallbacks=[
             {"trigger": "clock_reaches:4 clk.thallen.choir_goal", "form": "the culprit makes a mistake", "delivers": "event: Ysmay seen in the Undercroft with Lark Mossbank, buying a second file (core, n5 via c11 + a new content)"},
             {"trigger": "stalled", "form": "a witness seeks the PC out", "delivers": "clu.silent_bells.r6 (or, if the Harrowby three were woken, Hester Tenney remembers a voice humming in Orrowan as the quiet came: core, n3)"},
             {"trigger": "scenes_without_clue:3", "form": "the threat returns", "delivers": "clu.silent_bells.r5: the hush-hounds come to Harrowby again; one wears a Choir thong"}],
         opposition_clock={"id": "clk.thallen.choir_goal", "is_faction_goal_of": "fac.thallen.hushed_choir", "name": "The Last Bell falls silent", "kind": "danger", "segments": 8, "start": 1, "visibility": "hidden",
                           "ticks": "the Choir's World Turn goal action (11.3.6) and 11.3.6's random_event; the linchpin fates of 13.7 move it",
                           "omens": {"stirring": ["the Last Bell misses a stroke (lead: n4.p2)", "Harrowby's bell found silent (lead: n1.p1)"],
                                     "building": ["Copsey's mill-bell is found silent, its clapper gone (lead: r3)", "the Last Bell sounds thin, as if from far away (lead: n4.p1)"],
                                     "imminent": ["the clapper-rope found cut through and spliced (lead: n5.p1)", "a hush-pool lies over Tolling's north ward for an hour at dawn, then lifts (lead: n3.p3)"]},
                           "on_complete": "fac.thallen.hushed_choir goal effects (13.7.4): the Last Bell is silent; Tolling's north ward becomes a hush-pool; the Quiet's clock +3"},
         lifecycle="provisional", basis=["15.9", "WE-15-3", "13.12.1", "DL-13-10"]),

    # ================================================================== the claimant
    dict(id="case.orsolin_signet", name="Whose ring is it?", tags=["situation.investigation", "org.crown.royal"],
         atmosphere="theme: a servant wearing her mistress's name for her mistress's people", begins_at="loc.tolling", thread_kind="quest",
         solution=[
             {"fact": "sol.signet.maid", "value": "the Wakeful's 'Lady Orsolin Vey' is Lisbet Mereling, maid to the true Orsolin"},
             {"fact": "sol.signet.true", "value": "the true Orsolin Vey stands stilled in Orsolin Manor's solar"},
             {"fact": "sol.signet.took", "value": "Lisbet woke beside her stilled mistress four springs ago and took the signet from her hand"}],
         clues={
             "c1": "an Orrowan court-roll: Orsolin Vey, the king's cousin, dark-haired, a harper, left-handed; the claimant is fair and right-handed",
             "c2": "Tobin served the Veys once: 'that is how the lady's maid walked, not the lady'",
             "c3": "Abel Marrow: in her first weeks at the Waking House she woke every night calling for 'my lady'",
             "c4": "read: her grief and her pride are for someone else",
             "c5": "a young woman in court-dress stilled in the manor solar beside an empty chair, the Vey signet-box open and empty at her side",
             "c6": "Wick Pell's crews saw 'a lady in the solar' and would not go near the cellars",
             "c7": "the gatehouse household roll: 'Lisbet Mereling, maid to the lady Orsolin'",
             "c8": "Lisbet's confession"},
         nodes=[
             dict(id="clu.orsolin_signet.n1", name="the claimant is not Orsolin Vey", fact="the Wakeful's leader is not Orsolin Vey", sealed_fact="sol.signet.maid",
                  necessary=True, deducible_from=[["c1", "c4"], ["c2", "c3"], ["c7", "c3"], ["c8"]], points_to=["clu.orsolin_signet.n2"], prerequisites=[]),
             dict(id="clu.orsolin_signet.n2", name="the true Orsolin is stilled at the manor", fact="the true Orsolin Vey is stilled in Orsolin Manor", sealed_fact="sol.signet.true",
                  necessary=True, deducible_from=[["c5"], ["c6", "c7"], ["c8"]], points_to=[], prerequisites=[]),
             dict(id="clu.orsolin_signet.n3", name="Lisbet took the signet", fact="Lisbet took the signet from her stilled mistress", sealed_fact="sol.signet.took",
                  necessary=False, deducible_from=[["c5", "c7"], ["c8"]], points_to=[], prerequisites=[])],
         placements=[
             P("clu.orsolin_signet.n1.p1", "obj.thallen.court_roll", "document", RS, "rolled", "c1", ["clu.orsolin_signet.n1"], detect_tier="moderate"),
             P("clu.orsolin_signet.n1.p2", "npc.tobin_reave", "person", I, "rolled", "c2", ["clu.orsolin_signet.n1"], request_size="R3"),
             P("clu.orsolin_signet.n1.p3", "npc.abel_marrow", "person", I, "core", "c3", ["clu.orsolin_signet.n1"], request_size="R1"),
             P("clu.orsolin_signet.n1.p4", "npc.orsolin_vey", "person", RD, "rolled", "c4", ["clu.orsolin_signet.n1"]),
             P("clu.orsolin_signet.n2.p1", "loc.orsolin_manor", "place", S, "core", "c5", ["clu.orsolin_signet.n2", "clu.orsolin_signet.n3"], direct=True, prerequisites=["pc in the manor's solar (the site's objective)"]),
             P("clu.orsolin_signet.n2.p2", "npc.wick_pell", "person", I, "core", "c6", ["clu.orsolin_signet.n2"], request_size="R2"),
             P("clu.orsolin_signet.n2.p3", "obj.thallen.gatehouse_roll", "document", RS, "core", "c7", ["clu.orsolin_signet.n1", "clu.orsolin_signet.n2", "clu.orsolin_signet.n3"]),
             P("clu.orsolin_signet.n2.p4", "npc.orsolin_vey", "person", IN, "rolled", "c8", ["clu.orsolin_signet.n1", "clu.orsolin_signet.n2", "clu.orsolin_signet.n3"], request_size="R5", direct=True)],
         reserve=[
             R("clu.orsolin_signet.r1", "an old Woken of Harrowby who was a groom at the manor", "person", I, "core", "c2", ["clu.orsolin_signet.n1"], "loc.harrowby", request_size="R2"),
             R("clu.orsolin_signet.r2", "a salvaged portrait of the Vey cousins in Pell's yard", "object", S, "core", "c1", ["clu.orsolin_signet.n1"], "loc.tolling.pell_yard"),
             R("clu.orsolin_signet.r3", "a Hem-guide who sheltered a night in the manor gatehouse", "person", I, "core", "c6", ["clu.orsolin_signet.n2"], "loc.bellhollow", request_size="R2"),
             R("clu.orsolin_signet.r4", "the Library's Hem-map marked 'Vey manor: the household stands'", "document", RS, "rolled", "c6", ["clu.orsolin_signet.n2"], "loc.tolling.library", detect_tier="moderate")],
         fallbacks=[{"trigger": "stalled", "form": "the world tests her", "delivers": "event (core, n1): at Vantry Keep's quarter-day hearing the Margravine's magus asks the claimant to play the harp of Orrow, and she cannot"}],
         opposition_clock={"id": "clk.thallen.vantry_digs", "name": "The Margravine's clerks find the maid", "kind": "danger", "segments": 8, "start": 0, "visibility": "hidden",
                           "auto_ticks": [{"boundary": "week", "ticks": 1, "every": 2}],
                           "omens": {"stirring": ["a charter-clerk at the Waking House asking about the Veys (lead: n1.p3)"], "building": ["Vantry outriders seen at Orsolin Manor's gate (lead: n2.p1)"],
                                     "imminent": ["the Margravine summons the claimant to the quarter-day hearing (lead: the fallback)"]},
                           "on_complete": "the Margravine exposes the claimant in her court: the Wakeful's linchpin fate 'exposed' fires (npc.orsolin_vey); Vantry's goal clock +2"},
         lifecycle="provisional", basis=["15.9", "13.12.2"]),

    # ================================================================== the treaty
    dict(id="case.treaty_of_the_ford", name="The Treaty of the Ford", tags=["situation.investigation", "org.crown.noble"],
         atmosphere="theme: a promise a lord would rather nobody remembered", begins_at="loc.tolling", thread_kind="quest",
         truth_condition="written only under 13.1.5 truth T4 option A (default)",
         solution=[
             {"fact": "sol.treaty.exists", "value": "the Treaty of the Ford, sealed at the Treaty Stone a hundred and sixty years ago, binds Esterlow's lords to honor the holdings of Orrow's folk under any crown"},
             {"fact": "sol.treaty.removed", "value": "the Margravine had Tolling's copy taken from the Weigh-house archive two winters ago; it is in the iron chest of her muniment room"},
             {"fact": "sol.treaty.copy", "value": "a sealed copy lies in Orsolin Manor's muniment chest"}],
         clues={
             "c1": "the Treaty Stone's inscription, half chiselled away: '...the holdings of Orrow's folk to stand under any crown...'",
             "c2": "the Library's salvaged register: 'Treaty of the Ford: copies to the Tolling archive and to the Vey muniments'",
             "c3": "Justiciar Ferrant: shelf seven of the land-law press stands empty; it held the Ford treaty",
             "c4": "Lady Orsolin: every Orrowan child learned that Orrow's law was guaranteed at the Ford",
             "c5": "Reeve Hask: the Margravine's clerk took a sealed packet from the archive two winters ago",
             "c6": "the archive's removal docket for shelf seven, in Hask's hand, under the Margravine's seal",
             "c7": "the Treaty itself, in the Margravine's iron chest",
             "c8": "a charter-clerk: the Margravine keeps 'the Orrowan paper' in the iron chest and reads it when she is angry",
             "c9": "the Vey copy of the Treaty, under the Vey seal, in the manor's muniment chest",
             "c10": "Lisbet (Lady Orsolin): her mistress kept the family's copy of the Ford treaty in the iron-bound chest in the manor's strongroom",
             "c11": "Wick Pell: a strongroom chest with the Vey arms her crews could not open"},
         nodes=[
             dict(id="clu.treaty.n1", name="a treaty upholds Orrowan claims", fact="a treaty binding Esterlow's lords to honor Orrowan holdings exists", sealed_fact="sol.treaty.exists",
                  necessary=True, deducible_from=[["c1", "c2"], ["c3", "c4"], ["c7"], ["c9"]], points_to=["clu.treaty.n2", "clu.treaty.n3"], prerequisites=[]),
             dict(id="clu.treaty.n2", name="the Margravine removed Tolling's copy", fact="the Margravine had Tolling's copy of the treaty removed", sealed_fact="sol.treaty.removed",
                  necessary=True, deducible_from=[["c3", "c5"], ["c6"], ["c7"], ["c8", "c3"]], points_to=[], prerequisites=[]),
             dict(id="clu.treaty.n3", name="a copy survives at Orsolin Manor", fact="a sealed copy of the treaty is in Orsolin Manor's muniment chest", sealed_fact="sol.treaty.copy",
                  necessary=True, deducible_from=[["c2", "c11"], ["c10"], ["c9"]], points_to=[], prerequisites=[])],
         placements=[
             P("clu.treaty.n1.p1", "obj.thallen.treaty_stone_text", "object", ST, "rolled", "c1", ["clu.treaty.n1"], detect_tier="moderate", invites=["lore.history.orrow"]),
             P("clu.treaty.n1.p2", "obj.thallen.library_register", "document", RS, "rolled", "c2", ["clu.treaty.n1", "clu.treaty.n3"], detect_tier="moderate"),
             P("clu.treaty.n1.p3", "npc.oda_ferrant", "person", I, "core", "c3", ["clu.treaty.n1", "clu.treaty.n2"], request_size="R2"),
             P("clu.treaty.n1.p4", "npc.orsolin_vey", "person", I, "core", "c4", ["clu.treaty.n1"], request_size="R1"),
             P("clu.treaty.n2.p1", "npc.corbin_hask", "person", I, "rolled", "c5", ["clu.treaty.n2"], request_size="R4"),
             P("clu.treaty.n2.p2", "obj.thallen.removal_docket", "document", S, "core", "c6", ["clu.treaty.n2"], prerequisites=["pc in the Weigh-house archive (Ferrant's leave at Warm, or R2)"]),
             P("clu.treaty.n2.p3", "obj.thallen.vantry_treaty", "document", S, "rolled", "c7", ["clu.treaty.n1", "clu.treaty.n2"], detect_tier="hard", direct=True, prerequisites=["pc in the muniment room of Vantry Keep"]),
             P("clu.treaty.n2.p4", "npc.aldis_vantry", "person", IN, "rolled", "c7", ["clu.treaty.n2"], request_size="R5"),
             P("clu.treaty.n3.p1", "obj.thallen.vey_treaty", "document", S, "core", "c9", ["clu.treaty.n1", "clu.treaty.n3"], direct=True, prerequisites=["pc in Orsolin Manor's strongroom (a side area of the site)"]),
             P("clu.treaty.n3.p2", "npc.orsolin_vey", "person", I, "core", "c10", ["clu.treaty.n3"], request_size="R2"),
             P("clu.treaty.n3.p3", "npc.wick_pell", "person", I, "rolled", "c11", ["clu.treaty.n3"], request_size="R2")],
         reserve=[
             R("clu.treaty.r1", "an old lowland farmer who saw the Stone's text before it was chiselled", "person", I, "core", "c1", ["clu.treaty.n1"], "loc.harrowby", request_size="R1"),
             R("clu.treaty.r2", "an Orrowan law-primer in the Bellwardens' library citing 'the Ford'", "document", RS, "rolled", "c4", ["clu.treaty.n1"], "loc.tolling.belltower", detect_tier="moderate"),
             R("clu.treaty.r3", "a dismissed archive-boy who carried the packet to the Margravine's clerk", "person", I, "core", "c5", ["clu.treaty.n2"], "loc.tolling", request_size="R2"),
             R("clu.treaty.r4", "the Keep's charter-clerk's day-book", "document", RS, "rolled", "c8", ["clu.treaty.n2"], "loc.vantry_keep", detect_tier="hard"),
             R("clu.treaty.r5", "a Vey seal-matrix sold in Pell's yard, its owner's chest described in the sale-note", "object", S, "core", "c11", ["clu.treaty.n3"], "loc.tolling.pell_yard"),
             R("clu.treaty.r6", "a Woken steward of the Veys at the Waking House", "person", I, "core", "c10", ["clu.treaty.n3"], "loc.tolling.hearth_shrine", request_size="R2")],
         fallbacks=[{"trigger": "stalled", "form": "a witness seeks the PC out", "delivers": "Justiciar Ferrant comes to the PC with her suspicion (clu.treaty.n1.p3, core)"}],
         opposition_clock={"id": "clk.thallen.treaty_burned", "name": "The Margravine's men burn the Vey copy", "kind": "danger", "segments": 6, "start": 0, "visibility": "hidden",
                           "auto_ticks": [{"boundary": "week", "ticks": 1, "when": "the fact vantry.alerted_treaty is set (the PC asked Hask, a clerk or the Margravine about the treaty, or the Wakeful petitioned with it)"}],
                           "omens": {"stirring": ["Vantry outriders asking Pell's crews the way to Orsolin Manor (lead: n3.p3)"], "building": ["Captain Stane rides north with lamp oil in his packs (lead: n3.p1)"],
                                     "imminent": ["smoke over the Hem toward the manor (lead: n3.p1)"]},
                           "on_complete": "clu.treaty.n3.p1 becomes lost (the Vey copy burned); the Keep's copy and the Stone remain"},
         lifecycle="provisional", basis=["15.9", "13.12.3"]),
]
