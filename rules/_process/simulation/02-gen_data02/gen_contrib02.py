# gen_contrib02.py -- emits ch.02's contrib fragments: licenses.02.yaml, effects.02.yaml, boundaries.02.yaml
import os as _os
_RULES = _os.environ.get('GAME_RULES', _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..')))
import json, os, re
D = _os.path.join(_RULES, '_process', 'merged-contrib')
def q(s): return json.dumps(s, ensure_ascii=False)
def flow(v):
    if isinstance(v, dict): return "{" + ", ".join("%s: %s" % (k, flow(x)) for k, x in v.items()) + "}"
    if isinstance(v, (list, tuple)): return "[" + ", ".join(flow(x) for x in v) + "]"
    if v is None: return "null"
    if isinstance(v, bool): return "true" if v else "false"
    if isinstance(v, (int, float)): return str(v)
    s = str(v)
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.\-]*", s) and s not in ("null", "true", "false", "yes", "no", "on", "off", "none"): return s
    if s == "none": return "none"
    return q(s)
def entry(d, ind="      "):
    out = []; first = True
    for k, v in d.items():
        pre = ind + ("- " if first else "  "); first = False
        if isinstance(v, list) and v and isinstance(v[0], dict):
            out.append("%s%s:" % (pre, k))
            for x in v: out.append("%s    - %s" % (ind, flow(x)))
        else: out.append("%s%s: %s" % (pre, k, flow(v)))
    return "\n".join(out)

LANG_CLOCK = "clk.learn_tongue (8 segments, project, public): a week living among speakers ticks 2; a week with a teacher or a text (needs lic.lang.letters) ticks 1; completion raises the grade one step"
def lang(id_, name, who, note=None):
    d = dict(id=id_, name=name, kind="language", tags=["deed.lore.languages"],
             principle="Speak and understand %s." % name,
             scope="Talk, listen and (with lic.lang.letters) read and write in %s, to the extent of the grade held. %s" % (name, who),
             excludes=[dict(what="reading or writing it without lic.lang.letters", needs="lic.lang.letters"),
                       dict(what="any other tongue", needs="that tongue's own lic.lang.* license"),
                       dict(what="deciphering a dead or coded text", needs="lic.training.lore_languages")],
             grades=[dict(grade="broken", scope="needs, directions, prices, warnings and other simple concrete matters; every Talk in it holds a Precision snag and its reach is capped at Limited"),
                     dict(grade="accented", scope="everyday speech with no snag; you are plainly a foreigner; subtle, technical or courtly matters hold a Precision snag"),
                     dict(grade="native", scope="everything a native speaker can say or catch, including idiom, rank and insult")],
             attribute="by_method", crude_fallback=dict(verb="verb.talk", method="gesture, tone and shared nouns", dc_shift=5, reach_cap="limited", consequence=None),
             stretch=None, emulate=None,
             effects=[dict(effect_id="eff.06.grant_snag", params=dict(type="precision", sign="snag", to="the bearer", fact="speaks %s brokenly" % name, applies_when="a Talk beat is spoken in this tongue and the grade held is broken", duration="permanent")),
                      dict(effect_id="eff.reach_step", params=dict(ladder="reach", steps=-1, applies_when="a Talk beat is spoken in this tongue, the grade held is broken, and the framed reach is above Limited")),
                      dict(effect_id="eff.06.grant_snag", params=dict(type="precision", sign="snag", to="the bearer", fact="speaks %s as a foreigner" % name, applies_when="a Talk beat is spoken in this tongue, the grade held is accented, and the matter is subtle, technical or courtly (a fact on the scene or the NPC)", duration="permanent"))],
             acquisition_paths=[dict(type="origin", detail="granted by a people or an upbringing at creation, or bought with a learning pick (02.5.6), at the stated grade", clock=None, requires=None),
                                dict(type="mentor", detail=LANG_CLOCK, clock="clk.learn_tongue", requires="speakers to live among, or a teacher who holds it at accented or better"),
                                dict(type="project", detail="a week of study from a grammar or a bilingual text ticks 1", clock="clk.learn_tongue", requires="lic.lang.letters and such a text")],
             source="data", lifecycle="provisional", basis=["02.4.6", "00.12.1", "01.18 (Talk: a language not held)", "WE-01-4", "DL-02-12"])
    if note: d["notes"] = note
    return d

LICS = [
 lang("lic.lang.common", "the Common tongue", "The tongue of roads, markets and mixed company; nearly everyone met in a settlement holds it at accented or better.", "The region's seed (12.16.7) names it for its region and may rename this entry (lifecycle: retired + superseded_by)."),
 lang("lic.lang.elvish", "Elvish", "The speech of elves among themselves."),
 lang("lic.lang.dwarvish", "Dwarvish", "The speech of dwarf-holds; its runes are cut wherever dwarves have built."),
 lang("lic.lang.orcish", "Orcish", "The speech of orc clans and war-bands."),
 lang("lic.lang.goblin", "Goblin", "The speech of goblins, hobgoblins and their kin."),
 lang("lic.lang.giantish", "Giantish", "The speech of giants, ogres and trolls that speak (WE-01-4 calls it ogrish in passing; this is that tongue)."),
 lang("lic.lang.kinspeech", "Kin-speech", "The speech of one beastfolk people among themselves; the player names which."),
 lang("lic.lang.old_tongue", "the Old Tongue", "The dead language of ruins, liturgy and old books. No one speaks it natively: its highest grade is accented.", "Bought only with a learning pick or learned in play; lettered folk meet it in inscriptions and spellbooks."),
 lang("lic.lang.cant", "the Cant", "The slang, signs and chalk-marks of thieves, beggars and smugglers. It is always held with the Common tongue and passes for it to outsiders.", "Its marks can be read without lic.lang.letters."),
 dict(id="lic.lang.letters", name="Letters", kind="language", tags=["deed.lore.languages", "deed.craft.scribing"],
      principle="Read and write the tongues you speak.",
      scope="Read and write every tongue you hold at accented or native, at an ordinary pace. Keep written notes, read a sign, a letter, a ledger or a book. Satisfies 'literacy' wherever a license or a learning path requires it (05.9.4, 05.8.5).",
      excludes=[dict(what="a tongue held only at broken, or not held", needs="that tongue at accented"), dict(what="ciphers, dead scripts, damaged or archaic hands", needs="lic.training.lore_languages"), dict(what="fine copying, forgery or illumination", needs="lic.training.craft_scribing or lic.training.guile_disguise")],
      attribute="intellect", crude_fallback=dict(verb="verb.observe", method="pick out numerals, seals, names seen before and a few common signs", dc_shift=5, reach_cap="limited", consequence=None),
      stretch=None, emulate=None,
      acquisition_paths=[dict(type="origin", detail="granted by the guild-quarter, court and cloister upbringings and by the scholar and apprentice livelihoods, or bought with a learning pick (02.5.6)", clock=None, requires=None),
                         dict(type="mentor", detail="clk.learn_letters (8 segments, project, public): a week with a lettered teacher ticks 2", clock="clk.learn_letters", requires="a teacher who holds this license"),
                         dict(type="project", detail="a week alone with a primer ticks 1", clock="clk.learn_letters", requires="a primer")],
      source="data", lifecycle="provisional", basis=["02.4.6", "05.9.4 (arcane requires literacy)", "01.18 (Observe: an unknown script)", "DL-02-12"]),
]
def gift(id_, name, people, principle, scope, excludes, effects, fallback="none", attribute="by_method", notes=None):
    d = dict(id=id_, name=name, kind="fact", tags=["creature.folk." + people], principle=principle, scope=scope,
             excludes=excludes, attribute=attribute, crude_fallback=fallback, stretch=None, emulate=None, effects=effects,
             acquisition_paths=[dict(type="origin", detail="born of this people (02.4.2); kept by one who is uncommon of their kind (02.3.4); never learned, taught or bought", clock=None, requires=None)],
             source="orig.people.*", lifecycle="provisional", basis=["02.4.2", "C:P4", "R2 02 (HWFWM racial gifts: a small fixed package)", "DL-02-04"])
    if notes: d["notes"] = notes
    return d
LICS += [
 gift("lic.people.starsight", "Starsight", "elf", "Your eyes need very little light.",
      "In dim light (dusk, moonlight, starlight, one candle across a room) you see as others see by day: you count as having night-sight for 06.3.7's dim rule, so nothing is flag.obscured to you because of dimness.",
      [dict(what="seeing in full darkness", needs="a light, or a license that says so"), dict(what="seeing through smoke, fog or cover", needs="nothing in this license")],
      [dict(effect_id="eff.05.waive", params=dict(event_kind="flag.obscured from dim light (06.3.7), and any snag that cites dim light", applies_when="scene.light is dim and the check relies on sight"))]),
 gift("lic.people.stonesense", "Stonesense", "dwarf", "Worked stone and the deep places speak plainly to you.",
      "Underground you always know which way is down, roughly how deep you are and which way you came (a G0 question answered Certain). Observe and Recall about worked stone, mines, tunnels and caves hold a Precision lever.",
      [dict(what="seeing in darkness", needs="a light"), dict(what="knowing who built it or why", needs="lic.training.lore_history or lic.training.lore_engineering")],
      [dict(effect_id="eff.grant_lever", params=dict(type="precision", for_verbs=["verb.observe", "verb.recall"], for_tags=["deed.lore.engineering", "deed.craft.building", "deed.wilds.navigation.underways"], duration="permanent", applies_when="the subject is worked stone, a mine, a tunnel or a cave"))]),
 gift("lic.people.underfoot", "Underfoot", "halfling", "Bigger folk do not look down.",
      "A Sneak holds a Precision lever while a crowd, or any creature larger than you, stands between you and the watcher.",
      [dict(what="hiding with nothing and no one between you and the watcher", needs="cover, a veil or a distraction (06.3.7)")],
      [dict(effect_id="eff.grant_lever", params=dict(type="precision", for_verbs=["verb.sneak"], for_tags=[], duration="permanent", applies_when="a crowd, or a creature larger than you, is recorded between you and the watcher"))]),
 gift("lic.people.iron_blood", "Iron blood", "orc", "Your body throws off what would lay another low.",
      "Hazards of venom and disease count one severity rung lighter against you.",
      [dict(what="harm from a weapon or a working that happens to carry venom", needs="nothing: this license steps hazards only")],
      [dict(effect_id="eff.hazard_step", params=dict(ladder="severity", steps=-1, harm_tags=["harm.venom", "harm.blight.disease"], applies_when="hazard"))]),
 gift("lic.people.cave_eyes", "Cave-eyes", "goblin", "Darkness is only a deeper dusk to you.",
      "In full darkness you see shapes and movement out to band.close as others see in dim light: you count as having night-sight for 06.3.7's dark rule (you are not cond.blinded by darkness), and whatever lies beyond band.close is flag.obscured to you.",
      [dict(what="reading, colors or fine detail in darkness", needs="a light"), dict(what="seeing beyond band.close in darkness", needs="a light")],
      [dict(effect_id="eff.05.waive", params=dict(event_kind="cond.blinded from darkness (06.3.7) for sight-reliant beats at band.engaged and band.close", applies_when="scene.light is dark and you carry no light"))]),
 gift("lic.people.great_frame", "Great frame", "giant", "You are simply bigger than what you are pushing.",
      "+1 edge on Force and Grapple checks.",
      [dict(what="reaching further or striking harder", needs="nothing in this license (weapons and mastery set harm, 06.4.5)"), dict(what="counting as a larger size for any other rule", needs="chapter 06's size steps, which this license does not change")],
      [dict(effect_id="eff.check_edge", params=dict(amount=1, applies_when="verb is verb.force or verb.grapple"))],
      notes="Interface request to 08: carrying capacity may treat the holder as Might +1 for the carry formula only."),
 gift("lic.people.keen_nose", "Keen nose", "beastfolk", "You smell what others must see.",
      "Observe by scent holds a Precision lever: following a scent trail, telling who or what has been in a place within the day, catching smoke, blood or rot before it is seen.",
      [dict(what="tracking where no scent could lie (running water, a day of rain)", needs="another method"), dict(what="knowing a stranger's intent by smell", needs="nothing in this license")],
      [dict(effect_id="eff.grant_lever", params=dict(type="precision", for_verbs=["verb.observe"], for_tags=["deed.wilds.tracking"], duration="permanent", applies_when="the method is scent and a fact does not rule scent out"))]),
]

HEAD = """# data/contrib/licenses.02.yaml
# Purpose: ch.02's owner-block for data/licenses.yaml (T-00-19 allows owner-block 02: origin licenses). Seventeen
#   licenses that origins grant and that no other file defines:
#     - nine LANGUAGE licenses with grades broken < accented < native, and lic.lang.letters (literacy);
#     - seven PEOPLE GIFTS (kind: fact): one small innate capability per non-human people.
#   Training licenses (lic.training.*) are chapter 05's; origins grant those by id and never redefine them.
# Setting note: these are the setting-agnostic tongues the eight peoples of origins.yaml need. The region's seed
#   owns its tongues (12.16.7; a pre-made seed such as ch.13 through T-00-19 owner-block 13): it may add tongues, and may retire one of these with
#   `superseded_by` when the region names it differently (00.16.3).
# Every entry carries explicit principle, scope, excludes, crude_fallback, stretch, emulate and acquisition_paths
#   (ch.01's requirement). stretch and emulate are null: a tongue or an inborn sense cannot be stretched or emulated.
# Owner: 02-character. Schema: data/SCHEMAS.md#licensesyaml (License, 00.12.1).
# GENERATED by scratchpad ch02/gen_contrib02.py.
# Basis: [C:VII] [C:P4] [00.12.1] [00.4.4 Intellect -> languages or lore at creation] [R4 9 02 #4] [DL-02-04] [DL-02-12]

schema_version: 1
blocks:
  - owner: "02"
    entries:
"""
with open(os.path.join(D, "licenses.02.yaml"), "w", encoding="utf-8", newline="\n") as f:
    f.write(HEAD + "\n".join(entry(l) for l in LICS) + "\n")

EFF = """# data/contrib/effects.02.yaml
# Purpose: ch.02's addition to data/effects.yaml. ONE definition, added because no core effect expresses it
#   (PR-00-8). T-00-19 lists owner-blocks 04-11, 15, 16 for effects.yaml; ch.02 REQUESTS an owner-block "02"
#   for this single entry (02 Interface requests, item 00-1).
# Owner: 02-character. Schema: data/SCHEMAS.md#effectsyaml. Decision: DL-02-11.

schema_version: 1
blocks:
- owner: '02'
  entries:
  - id: eff.02.bent
    op: set_fact
    regime: independent_trigger
    params: {attribute: attr_id, amount: '1'}
    applies_when: "the player ACCEPTED the Bent offer (02.6.6); the attribute is +2 or lower"
    limits: {per: lifetime, uses: 1}
    player_only: true
    text: 'Permanently raises {attribute} by {amount}, never above +3 (00.4.3 a).'
    why_not_core: attributes are not quantities of the evaluation pass (T-00-13) and no modify effect may change them
      (00.4.3); the birth Bent is the one write 00.4.3 a allows, expressed as a recorded fact, as ch.07 did for eff.07.maim
    lifecycle: provisional
    basis: [00.4.3 a, 02.6.5, 02.6.6, 'C:P1', DL-02-11]
"""
with open(os.path.join(D, "effects.02.yaml"), "w", encoding="utf-8", newline="\n") as f: f.write(EFF)

BND = """# data/contrib/boundaries.02.yaml
# Purpose: ch.02's owner-block for data/boundaries.yaml (every chapter may register its own handlers, 00.7.4).
# Owner: 02-character. Schema: data/SCHEMAS.md#boundariesyaml. Phases per 00.7.5.
# Basis: [00.7.4] [C:P1] [C:P4] [SG-11] [SG-19] [DL-02-11] [DL-02-15]

schema_version: 1
blocks:
  - owner: "02"
    handlers:
      - {id: h.02.creation_lock, boundary: reflection, phase: 9, interrupting: false, rule_id: "02.2.6", effect: "at the first reflection after creation, close the creation window: creation choices become permanent (P4) and the fact pc.creation.locked is written; a no-op afterwards"}
      - {id: h.02.bent_offer, boundary: reflection, phase: 8, interrupting: false, rule_id: "02.6.5", effect: "if the creation window is closed and the Bent is neither accepted nor forgone: when no Bent offer is open and the spacing rule is met, draw one (generate gen.birth, circumstance bent_first or bent_again) and present it as an offer; a deferred or unanswered offer is never applied"}
      - {id: h.02.open_slots, boundary: reflection, phase: 9, interrupting: false, rule_id: "02.9.8", effect: "if any creation slot is still open (second bond, the true thing, a faction tie, an aspiration), queue ONE out-of-fiction reminder for the next session start; never more than one per session, and never after the player has said to stop asking"}
"""
with open(os.path.join(D, "boundaries.02.yaml"), "w", encoding="utf-8", newline="\n") as f: f.write(BND)
print("wrote licenses.02.yaml (%d entries), effects.02.yaml, boundaries.02.yaml" % len(LICS))
