"""The claim check (12.3.1–12.3.2, PR-12-2 step 2; T044). `[D]`: verdicts are computed by code, never by a model.

    verdicts = check_claims(claims, state, record, scene_ids)          # one Verdict per claim, in order
    missing = owed_blocks(record.triggers, response_text)              # "[WARNING]" / "[STATUS]" owed, absent

Order of tests per claim: PC agency (12.14.3) → leak (sealed partition, audit view) → `subject: unknown` (written on
mention, or cut only for 12.14.13's forbidden kinds) → the class's own comparison with the store. A change claim (`asserts_change`) is supported only when a
write this turn (the adjudication record's `writes`) backs it; a change is never written to match prose (INV-1).

Store conventions read here (other modules write them):
- identity: `EntityRecord.name`, `data` keys (gender, pronouns, age, role, detail, demeanor, people/species,
  title, kin, aliases) or a current fact with that predicate on the entity;
- possession: an item whose `data.holder` (or `owner`, `carried_by`, `held_by`) or current fact `holder` names
  the subject; facts on the subject with predicate carries/holds/has/equipped/possessions/inventory/owns; a
  quantity on the subject;
- attitude: `relationship_set` kind `standing` with `a` = the NPC, `b` = the PC (rungs from social.yaml);
- harm: conditions on the subject, `harm_state` facts, the `vitality` quantity, `EntityRecord.exists`.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from engine.audit import text as tx
from engine.dm.adjudication import AdjudicationRecord, BeatEntry
from engine.store.projection import WorldState

ClaimClass = Literal["existence", "identity", "quantity", "harm_condition", "position", "possession",
                     "location_time", "knowledge", "capability", "clock", "attitude", "outcome", "action", "sealed"]
VerdictName = Literal["supported", "new_element", "undetermined", "contradicted", "unsourced_change", "overreach",
                      "leak", "pc_agency"]
Fix = Literal["write_on_mention", "oracle", "redraft_to_store", "cut", "replace_with_slice"]

UNKNOWN = "unknown"
# classes not about one entity: checked even when the subject is unknown
_FREE_SUBJECT = ("clock", "location_time", "sealed", "outcome")


class Claim(BaseModel):
    """data-model.md §4 Claim (the Checker's output item)."""

    model_config = ConfigDict(populate_by_name=True)

    sentence: int = 0
    subject: str = UNKNOWN
    cls: ClaimClass = Field(alias="class")
    predicate: str = ""
    value: str = ""
    asserts_change: bool = False
    pc_words_or_feelings: bool = False

    @field_validator("sentence", mode="before")
    @classmethod
    def _int(cls, v: Any) -> int:  # the schema's sentence is a string enum "0".."n-1"
        return int(v)

    @property
    def text(self) -> str:
        return f"{self.predicate} {self.value}".strip()


class Verdict(BaseModel):
    """data-model.md §4 Verdict. `fix` is None for `supported`."""

    claim: int
    verdict: VerdictName
    store_value: str | None = None
    fix: Fix | None = None
    reason: str = ""


_DEFAULT_FIX: dict[str, Fix | None] = {
    "supported": None, "new_element": "cut", "undetermined": "oracle", "contradicted": "redraft_to_store",
    "unsourced_change": "cut", "overreach": "redraft_to_store", "leak": "cut", "pc_agency": "cut",
}

# ------------------------------------------------------------------------------------------- vocabulary

_ABSENT = ["gone", "dead", "destroyed", "departed", "absent", "missing", "vanish", "fled", "no longer",
           "not here", "disappear", "nowhere", "empty of", "left the", "has left", "leaves"]
_IDENTITY_KEYS: dict[str, list[str]] = {
    "name": ["name", "called", "named"],
    "gender": ["gender", "sex"],
    "pronouns": ["pronoun", "pronouns"],
    "age": ["age", "aged", "old", "young"],
    "role": ["role", "profession", "job", "occupation", "trade", "title", "work"],
    "people": ["species", "people", "folk", "race", "kind"],
    "detail": ["appearance", "look", "detail", "feature", "wears", "dress"],
    "demeanor": ["demeanor", "demeanour", "manner", "bearing", "temper"],
    "kin": ["kin", "family", "sister", "brother", "father", "mother", "son", "daughter", "wife", "husband"],
}
_GENDER = {"f": ["female", "woman", "she", "her", "girl", "lady", "matron", "f"],
           "m": ["male", "man", "he", "him", "his", "boy", "lad", "gentleman", "m"],
           "x": ["they", "them", "nonbinary", "non binary", "x"]}
_QTY_SYNONYMS: dict[str, list[str]] = {
    "coin": ["coin", "silver", "purse", "money", "gold", "copper", "penny", "pennies"],
    "vitality": ["vitality"],
    "arrows": ["arrow", "arrows", "quiver", "shaft"],
    "supply": ["supply", "supplies", "ration", "rations", "food"],
    "torch": ["torch", "torches"],
}
_DEAD = ["dead", "dies", "died", "killed", "slain", "lifeless", "corpse", "perish"]
_REMOVED = ["shake off", "no longer", "recover", "steady", "fade", "free of", "clear", "stop bleeding",
            "throw off", "pass", "ease", "lift"]
_HURT = ["wound", "bleed", "hurt", "injur", "bloodied", "barely standing", "stagger", "batter", "bruise",
         "cut", "gash", "limp", "reel", "dying", "down"]
_UNHURT = ["unhurt", "unharmed", "unscathed", "fresh", "whole", "untouched", "uninjured"]
_COND_WORDS: dict[str, list[str]] = {  # in-fiction words for conditions (T-12-10 spirit), beyond their names
    "cond.frightened": ["fear", "afraid", "dread", "terror", "panic", "scared"],
    "cond.bleeding": ["bleed", "blood"],
    "cond.exhausted": ["tired", "weary", "exhaust", "spent"],
    "cond.poisoned": ["poison", "venom", "sick"],
    "cond.prone": ["prone", "on the ground", "sprawl", "knocked down"],
    "cond.off_balance": ["off balance", "stumble", "unsteady"],
    "cond.heartened": ["hope", "heartened", "courage", "emboldened"],
    "cond.charmed": ["charmed", "enthralled"],
    "cond.dazed": ["dazed", "reeling", "dizzy"],
    "cond.unconscious": ["unconscious", "senseless", "out cold"],
    "cond.burning": ["burning", "on fire", "aflame"],
    "cond.chilled": ["chilled", "numb with cold"],
}
_NEAR = ["shoulder", "beside", "next to", "at your side", "close", "adjacent", "within reach", "elbow"]
_FAR = ["far", "distant", "across the", "out of reach", "away"]
_WATCH_WORDS: dict[int, list[str]] = {
    0: ["dawn", "morning", "sunrise", "daybreak", "first light"],
    1: ["noon", "midday", "afternoon"],
    2: ["dusk", "evening", "sunset", "twilight", "nightfall"],
    3: ["night", "midnight", "small hours"],
}
_WATCH_NAMES = {0: "morning", 1: "afternoon", 2: "evening", 3: "night"}
_WATCH_EDGES = {"dawn": {3, 0}, "daybreak": {3, 0}, "sunrise": {3, 0}, "dusk": {1, 2}, "sunset": {1, 2},
                "twilight": {1, 2}, "nightfall": {2, 3}}
_NEGATION = ["not", "no", "never", "fail", "cannot", "can't", "doesn't", "don't", "won't", "isn't", "hasn't"]
_KNOW_NEGATIVE = ["no idea", "forgot", "forgets", "unaware", "doesn't know", "does not know", "fails to recogni",
                  "don't know", "do not know", "can't place", "cannot place", "unknown to"]
_POS_ATT = ["warm", "friendly", "trust", "smile", "soften", "relax", "pleased", "grateful", "kind", "approv",
            "welcom", "glad", "cordial", "fond", "devoted", "adore", "love", "like", "eager", "help", "friend"]
_NEG_ATT = ["angry", "anger", "furious", "fury", "hostile", "suspicious", "suspicion", "cold", "scowl", "glare",
            "distrust", "wary", "annoyed", "irritat", "contempt", "hate", "sneer", "rude", "unfriendly", "enmity",
            "bristle", "seethe", "resent", "spit", "loathe"]
_WRITING = ["text", "reads", "read", "says", "say", "words", "letters", "lettering", "inscription", "inscribed",
            "written", "writing", "wording", "headline", "legend", "caption"]
_BOND_WORDS = ["relation", "relationship", "bond", "to you", "to the pc"]
_STRONG_ATT = ["furious", "fury", "hostile", "hate", "loathe", "devoted", "adore", "love", "enmity", "seethe"]
_SUCCESS = ["make it", "succeed", "gives", "give way", "opens", "open", "works", "manage", "across", "done", "free",
            "catch", "find", "found", "breaks", "break", "lands", "land", "reach", "convince", "agree", "yield",
            "slip through", "clear", "win", "pass"]
_FAILURE = ["fail", "holds firm", "the lock holds", "won't budge", "will not budge", "slip", "miss", "nothing",
            "no luck", "stuck", "falls short", "fall short", "refuse", "can't", "cannot", "not enough", "in vain",
            "resists", "does not give", "doesn't give", "stays shut", "remains shut", "unmoved",
            "breaks off", "goes cold", "gone cold", "go cold", "lose the", "lost", "blurs", "gone under"]
_COST = ["cost", "costs", "price", "pay for", "at a cost", "toll"]
_BIG = ["perfectly", "flawlessly", "effortlessly", "completely", "entirely", "utterly", "at once", "easily",
        "without a trace", "and more", "every last", "masterfully", "with ease"]
_CLOCK_DONE = ["complete", "completes", "done", "finished", "raised", "sounds", "full", "arrive", "too late",
               "comes to pass", "falls on"]
_CLOCK_MOVE = ["spread", "build", "rise", "rising", "closer", "grow", "gather", "mount", "near", "louder",
               "quicken", "swell", "creep"]
_POSSESS_PREDICATES = ("carries", "holds", "has", "equipped", "possessions", "inventory", "owns", "possession",
                       "wields", "wears")
_HOLDER_KEYS = ("holder", "owner", "carried_by", "held_by")
# acts that change the world (12.2.9: the source decides *what*); everything else an addressed NPC does in answer is
# words and manner, which are the narrator's. ponytail: a phrase list; upgrade path: a Checker field for "deed".
_DEEDS = ["give", "hand over", "hand you", "hand it", "pass you", "slide across", "toss you", "pay you", "pay the",
          "pay for", "sell", "buy", "take the", "take your", "take it", "grab", "seize", "snatch", "steal", "pocket",
          "draw a blade", "draw a knife", "draw a sword", "draw a dagger", "draw steel", "attack", "strike", "hit",
          "punch", "stab", "slash", "shoot", "kick", "shove", "push you", "leave", "walk away", "walk off",
          "walk out", "storm off", "storm out", "depart", "exit", "flee", "run off", "run away", "come with you",
          "go with you", "lead you", "open the", "unlock", "lock the", "shut the door", "close the door", "call for",
          "call the", "shout for", "summon", "fetch", "send for", "signal to", "kill", "set free", "let go of",
          "let you pass", "step aside", "show you the", "write", "sign"]
_YOU = ["you", "your", "yours", "the pc"]
_LOSE = ["drop", "lose", "lost", "give", "hand over", "hands over", "sold", "sell", "stolen", "no longer", "toss",
         "throw away", "surrender", "gone"]


def _has(text: str, phrases: Iterable[str]) -> bool:
    return tx.any_phrase(text, phrases) is not None


def _negated(text: str) -> bool:
    return _has(text, _NEGATION) or "n't" in text.lower()


# ------------------------------------------------------------------------------------------- context


class _Ctx:
    def __init__(self, state: WorldState, record: AdjudicationRecord, scene_ids: Sequence[str], rules: Any) -> None:
        self.state = state
        self.record = record
        self.scene_ids = list(scene_ids)
        self.rules = rules
        self.pc = record.pc or next((e.id for e in state.entities.values() if e.kind == "pc"), None)
        self.player_text = " ".join(p.text for p in record.parts)
        self._conditions: dict[str, Any] | None = None

    # -- rules data (loaded lazily: many claims need none)
    def conditions(self) -> dict[str, Any]:
        if self._conditions is None:
            self._conditions = dict(self._rules().conditions)
        return self._conditions

    def _rules(self) -> Any:
        if self.rules is None:
            from engine.data.loader import load_rules

            self.rules = load_rules()
        return self.rules

    def license(self, lid: str) -> Any:
        try:
            return self._rules().license(lid)
        except Exception:  # noqa: BLE001 - an unknown licence id reads as no scope
            return None

    def standings(self) -> list[tuple[int, str]]:
        return [(int(x["standing"]), str(x["name"])) for x in self._rules().social["standing_effects"]]

    # -- store reads
    def name(self, eid: str | None) -> str:
        if eid is None:
            return ""
        e = self.state.entities.get(eid)
        return e.name if e else eid

    def present(self, eid: str) -> bool:
        s, sc = self.state, self.state.scene
        if eid == self.pc:
            return True
        if sc is not None and (eid in sc.cast_present or eid == sc.place_id):
            return True
        holder = self.holder(eid)
        if holder and holder != eid and self.present(holder):
            return True
        pos = s.positions.get(eid)
        loc = pos.location if pos is not None else None
        here = sc.place_id if sc is not None else (s.positions[self.pc].location if self.pc in s.positions else None)
        if loc is not None and here is not None:
            return loc == here
        return sc is None and loc is None  # no scene and no position: nothing says it is elsewhere

    def holder(self, eid: str) -> str | None:
        e = self.state.entities.get(eid)
        if e is not None:
            for k in _HOLDER_KEYS:
                if isinstance(e.data.get(k), str):
                    return e.data[k]
        v = self.state.fact_value(eid, "holder")
        return v if isinstance(v, str) else None

    def backed(self, entity: str | None, *types: str, key: str | None = None) -> bool:
        """A write this turn touched `entity` (of one of `types`; with `key` when given)."""
        if entity is None:
            return False
        for w in self.record.writes_for(entity, *types):
            if key is None or w.key is None or tx.same(w.key, key) or key in (w.key or ""):
                return True
        return False

    def entity_named(self, text: str, *, kinds: Sequence[str] = (), among: Iterable[str] | None = None) -> str | None:
        """The entity whose whole name (or id tail) appears in `text`; the longest name wins."""
        best: tuple[int, str] | None = None
        pool = among if among is not None else self.state.entities
        for eid in pool:
            e = self.state.entities.get(eid)
            if e is None or (kinds and e.kind not in kinds):
                continue
            names = [e.name, eid.split(".", 1)[-1].replace("_", " ")]
            names += [a for a in e.data.get("aliases", []) if isinstance(a, str)]
            if e.kind in ("npc", "pc", "companion") and len(e.name.split()) > 1 and len(e.name.split()[0]) > 2:
                names.append(e.name.split()[0])  # a person by their given name ("Mara")
            for n in names:
                if tx.content(n) and tx.covers(n, text, ratio=1.0):
                    size = len(tx.content(n))
                    if best is None or size > best[0]:
                        best = (size, eid)
        return best[1] if best else None


def _v(c: Claim, idx: int, verdict: VerdictName, store_value: Any = None, *, fix: Fix | None | Literal["default"] = "default",
       reason: str = "") -> Verdict:
    sv = None if store_value is None else (store_value if isinstance(store_value, str) else _words(store_value))
    if not reason and sv and verdict != "supported":
        reason = f"the truth is: {sv}"  # the redraft is told why, never an empty reason; never "store" (P-045)
    return Verdict(claim=idx, verdict=verdict, store_value=sv,
                   fix=_DEFAULT_FIX[verdict] if fix == "default" else fix, reason=reason)


def _words(v: Any) -> str:
    if isinstance(v, dict):
        return "; ".join(f"{k}: {_words(x)}" for k, x in v.items())
    if isinstance(v, list | tuple | set):
        return ", ".join(_words(x) for x in v)
    return str(v)


def _flat(v: Any) -> str:
    """Every string inside a value (lists of dicts included), joined."""
    if isinstance(v, dict):
        return " ".join(_flat(x) for x in v.values())
    if isinstance(v, list | tuple | set):
        return " ".join(_flat(x) for x in v)
    return "" if isinstance(v, bool) or v is None else str(v)


# ------------------------------------------------------------------------------------------- entry point


def check_claims(claims: Iterable[Claim | dict[str, Any]], state: Any, record: AdjudicationRecord | None = None,
                 scene_ids: Sequence[str] = (), *, rules: Any = None) -> list[Verdict]:  # rule: 12.3.2
    """One verdict per claim (12.3.2). `state`: a `WorldState` or a `Store` (its projection is read).
    `scene_ids`: the ids the Checker was offered (the schema's subject enum). Subjects are checked against the
    whole store; presence in the scene comes from the scene record and positions, not from this list."""
    ws: WorldState = state.state if hasattr(state, "transaction") else state
    ctx = _Ctx(ws, record or AdjudicationRecord(), scene_ids, rules)
    out = []
    for i, raw in enumerate(claims):
        c = raw if isinstance(raw, Claim) else Claim.model_validate(raw)
        out.append(_check(ctx, c, i))
    return out


def _check(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: PR-12-2
    if c.pc_words_or_feelings and not _agency_licensed(ctx, c):  # rule: 12.14.3
        return _v(c, i, "pc_agency", reason="gives the PC words, choices or feelings the player did not state")
    leak = _leak(ctx, c)
    if leak is not None:
        return _v(c, i, "leak", leak or None, fix="replace_with_slice" if leak else "cut",
                  reason="matches sealed content")
    if _restates_given(ctx, c):
        return _v(c, i, "supported")
    subject = c.subject
    if subject != UNKNOWN and subject not in ctx.state.entities:
        subject = UNKNOWN  # an id the store does not hold is no better than unknown
    if subject == UNKNOWN:
        subject = _resolve_new(ctx, c) or UNKNOWN
    if subject == UNKNOWN and c.cls not in _FREE_SUBJECT:  # rule: 12.3.2 [revision: I-127; DL-12-37]
        if c.cls == "action" and not c.asserts_change and _atmosphere(ctx, c):
            return _v(c, i, "supported", reason="background activity that changes nothing: atmosphere (12.3.2)")
        if c.cls == "action" and _reacts_to_incident(ctx, c):
            return _v(c, i, "supported", reason="a bystander's reaction to the inciting incident (12.16.16)")
        if c.asserts_change or c.cls == "action":
            return _v(c, i, "unsourced_change", reason="an unidentified subject changed or acted; cut")
        forbidden = _forbidden_new(c)
        if forbidden:  # 12.14.13: the only new things the narration may not create
            return _v(c, i, "new_element", fix="cut", reason=f"a new {forbidden} may not be created by mention; cut")
        return _v(c, i, "new_element", fix="write_on_mention", reason="a new ordinary element: write it on mention")
    c = c.model_copy(update={"subject": subject})
    return _CLASS_CHECKS[c.cls](ctx, c, i)


# record notes that hand the narration an event as given (the opening's inciting incident, a lead, the scene's
# impetus): the engine wrote them from the seed or a table, so the record is their source this turn
GIVEN_NOTES = ("the inciting incident:", "a lead to make noticeable:", "a lead arrives", "the scene's impetus")


# 12.14.13: a new clue, an item beyond common value, a hazard or trap, an adversary, or a person with a want, secret
# or thread knowledge is never created by mention. ponytail: a keyword proxy on the claim's words (the checker
# schema carries no element kind); upgrade path: have the checker label the kind and test that instead.
_FORBIDDEN_NEW: dict[str, tuple[str, ...]] = {
    "clue": ("clue", "hidden", "secret", "concealed", "cipher", "evidence", "sign of", "trace of the", "lead to"),
    "item beyond common value": ("treasure", "hoard", "jewel", "gem", "relic", "artifact", "artefact", "heirloom",
                                 "enchanted", "magic item", "ancient", "priceless", "chest of", "vault"),
    "hazard or trap": ("trap", "snare", "tripwire", "pitfall", "ambush", "hazard", "poisoned", "booby"),
    "adversary": ("bandit", "assassin", "monster", "cultist", "raider", "brigand", "foe", "enemy", "wolf pack",
                  "lurk", "stalks", "stalking"),
    "person with a want, secret or thread knowledge": ("knows about", "knows of", "knows the", "wants ", "seeks",
                                                       "plots", "plotting", "spy", "informant", "cult"),
}


def _forbidden_new(c: Claim) -> str | None:  # rule: 12.14.13
    if c.cls == "knowledge":
        return "secret or thread knowledge"
    text = c.text.lower()
    for kind, words in _FORBIDDEN_NEW.items():
        if any(w in text for w in words):
            return kind
    return None


def _deed(text: str) -> bool:  # rule: 12.2.9
    return _has(text, _DEEDS) and not _negated(text)


def _involves_pc(ctx: _Ctx, text: str) -> bool:
    return _has(text, _YOU) or (ctx.pc is not None and ctx.entity_named(text, among=[ctx.pc]) is not None)


def _atmosphere(ctx: _Ctx, c: Claim) -> bool:  # rule: 12.3.2 [revision: I-127]
    """Unnamed background activity that changes nothing and does not touch the PC: atmosphere, never a claim."""
    return not (_forbidden_new(c) or _deed(c.text) or _involves_pc(ctx, c.text))


def _reacts_to_incident(ctx: _Ctx, c: Claim) -> bool:  # rule: 12.16.16
    """The opening's inciting incident is its record source: those who witness it react (heads turn, a murmur,
    someone swears, folk gather), in words and manner. A deed (taking, leaving, attacking) still needs its own
    source, and nothing 12.14.13 forbids is created this way."""
    return _incident_given(ctx) and not _deed(c.text) and not _forbidden_new(c)


def _incident_given(ctx: _Ctx) -> bool:  # rule: 12.16.16
    """This is the opening: the record carries the inciting incident as given."""
    return any(n.startswith(GIVEN_NOTES[0]) for n in ctx.record.notes)


def _addressed(ctx: _Ctx, npc: str) -> bool:  # rule: 12.2.9
    """The PC addressed or acted on this NPC this turn: a beat targets them, a part of the player's message names
    them, or the record gives them a response row."""
    r = ctx.record
    return (any(npc in b.targets for b in r.beats) or any(a.npc == npc for a in r.npc_actions)
            or any(ctx.entity_named(p.text, among=[npc]) for p in r.parts if p.cls != "OOF_QUESTION"))


def _restates_given(ctx: _Ctx, c: Claim) -> bool:  # rule: 12.3.1
    """The claim restates an event the adjudication record itself gives (most of its content words are in it)."""
    for note in ctx.record.notes:
        if note.startswith(GIVEN_NOTES) and tx.covers(c.text, note.split(":", 1)[-1], ratio=0.75):
            return True
    return False


def _resolve_new(ctx: _Ctx, c: Claim) -> str | None:
    """An unknown subject that names an entity created this turn (write-on-mention ran before the check)."""
    created = [e for w in ctx.record.writes if w.type == "entity_created" for e in w.entities]
    return ctx.entity_named(c.text, among=created) if created else None


# ------------------------------------------------------------------------------------------- agency, leaks


def _agency_licensed(ctx: _Ctx, c: Claim) -> bool:  # rule: 12.14.3
    """The player stated it, or a resolved effect (a condition on the PC) produces it."""
    if ctx.player_text and tx.covers(c.value or c.text, ctx.player_text, ratio=0.8):
        return True
    if ctx.pc is None:
        return False
    for inst in ctx.state.conditions_on(ctx.pc):
        cond = ctx.conditions().get(inst.condition_id, {})
        words = [str(cond.get("name", "")), inst.condition_id.split(".")[-1], *_COND_WORDS.get(inst.condition_id, [])]
        if any(w and tx.has_phrase(c.text, w) for w in words) or any(tx.overlap(w, c.text) for w in words if w):
            return True
    return False


def _leak(ctx: _Ctx, c: Claim) -> str | None:  # rule: 00.6.5
    """None: no leak. Otherwise the permitted slice ("" when there is none)."""
    s = ctx.state
    text = c.text
    for ref, seal in s.seals.items():
        if seal.slice and tx.covers(text, seal.slice, ratio=0.6):
            continue  # the permitted slice is narrator-visible
        ent, _, fieldname = ref.partition("#")
        hit = False
        if ent in s.entities and not fieldname:  # a whole sealed entity
            e = s.entities[ent]
            hit = c.subject == ent or (bool(tx.content(e.name)) and tx.covers(e.name, text, ratio=1.0))
        elif ent in s.entities:  # a sealed data field
            content = _flat(s.entities[ent].data.get(fieldname))
            if c.subject == ent:
                hit = (c.cls == "sealed" and tx.same(c.predicate, fieldname)) or (
                    bool(tx.content(content)) and tx.covers(content, text, ratio=0.5))
            else:
                hit = len(tx.content(content)) >= 2 and tx.covers(content, text, ratio=0.6)
        elif ref in s.facts:  # a sealed fact
            f = s.facts[ref]
            content = _flat(f.value)
            pred_hit = tx.same(c.predicate, f.predicate) or tx.covers(f.predicate, text, ratio=0.6)
            if c.subject == f.subject:
                hit = pred_hit or (bool(tx.content(content)) and tx.covers(content, text, ratio=0.5))
            else:
                hit = len(tx.content(content)) >= 2 and tx.covers(content, text, ratio=0.6)
        if hit:
            return seal.slice or ""
    return None


# ------------------------------------------------------------------------------------------- classes


def _existence(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.3.1
    e = ctx.state.entities[c.subject]
    text = c.text
    absent_claim = _has(text, _ABSENT) or _negated(text)
    if e.kind == "place" and not absent_claim and _names_other(e.name, c.value):
        # "a bench by the wall" about the place: the feature, not the place
        other = ctx.entity_named(c.value)
        if other is None:
            return _v(c, i, "new_element", fix="cut" if c.asserts_change else "write_on_mention",
                      reason="a feature the store does not hold")
        c = c.model_copy(update={"subject": other})
        e = ctx.state.entities[other]
    store_absent = e.exists != "exists" or not ctx.present(e.id)
    store_words = e.exists if e.exists != "exists" else ("present" if ctx.present(e.id) else "not in this scene")
    if absent_claim:
        if store_absent:
            return _v(c, i, "supported")
        if c.asserts_change:
            return _v(c, i, "unsourced_change", store_words, reason="no write this turn removed it")
        return _v(c, i, "contradicted", store_words)
    if e.exists != "exists":
        return _v(c, i, "contradicted", e.exists)
    if not ctx.present(e.id):
        if c.asserts_change and ctx.backed(e.id, "position_set", "entity_created"):
            return _v(c, i, "supported")
        return _v(c, i, "unsourced_change" if c.asserts_change else "contradicted", store_words)
    return _v(c, i, "supported")


def _names_other(name: str, value: str) -> bool:
    return bool(tx.content(value) - tx.content(name) - tx.content("here there present stands lies is room place"))


def _identity_key(predicate: str) -> str | None:
    for key, ws in _IDENTITY_KEYS.items():
        if any(tx.has_phrase(predicate, w) for w in ws):
            return key
    return None


def _gender(v: Any) -> str | None:
    t = tx.norm(v)
    for g, ws in _GENDER.items():
        if any(tx.has_phrase(t, w) for w in ws):
            return g
    return None


def _identity(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.3.1
    e = ctx.state.entities[c.subject]
    key = _identity_key(c.predicate) or _identity_key(c.value)
    pred_slug = "_".join(tx.words(c.predicate))
    if key == "name":
        names = [e.name, *[a for a in e.data.get("aliases", []) if isinstance(a, str)]]
        if any(tx.same(c.value, n) or tx.covers(c.value, n, ratio=1.0) for n in names):
            return _v(c, i, "supported")
        return _v(c, i, "contradicted", e.name)
    store: Any = None
    for k in [key, pred_slug] if key else [pred_slug]:
        if k is None:
            continue
        store = e.data.get(k)
        if store is None and k == "people":
            store = e.data.get("species")
        if store is None:
            store = ctx.state.fact_value(e.id, k)
        if store is not None:
            break
    if key in ("gender", "pronouns"):
        store_g = _gender(e.data.get("gender")) or _gender(e.data.get("pronouns")) or _gender(
            ctx.state.fact_value(e.id, "gender") or ctx.state.fact_value(e.id, "pronouns"))
        claim_g = _gender(c.value)
        if store_g is None:
            return _v(c, i, "undetermined", reason="gender and pronouns not in the store (12.11.1 pronoun rule)")
        if claim_g is None or claim_g == store_g:
            return _v(c, i, "supported")
        return _v(c, i, "contradicted", e.data.get("pronouns") or e.data.get("gender") or store_g)
    if store is None and (_has(c.predicate, _WRITING) or pred_slug == "text"):  # rule: 12.3.1 [P-041]
        said = next((ctx.state.fact_value(e.id, k) for k in ("text", "inscription", "reads", "words", "says")
                     if ctx.state.fact_value(e.id, k) is not None), None)
        if said is not None and tx.covers(c.value, _flat(said)):  # the stored words hold the claimed ones
            beyond = " ".join(w for w in c.value.split() if w.lower() not in _flat(said).lower().split())
            if _negated(beyond):  # "they do not say NO QUESTIONS ASKED" (the notice's own "NO" is not a denial)
                return _v(c, i, "contradicted", said, reason="the words written there are on record; use them")
            return _v(c, i, "supported")
    bond = ctx.state.fact_value(ctx.pc, "bond.anchor") if ctx.pc else None  # rule: 02.9.2 [P-036]
    if store is None and isinstance(bond, dict) and bond.get("npc") == e.id and _has(c.predicate, _BOND_WORDS):
        kind = str(bond.get("kind") or "friend")  # the PC's anchor bond is who this NPC is to them, never asked anew
        if _negated(c.value) or not tx.covers(c.value, kind, ratio=1.0):
            return _v(c, i, "contradicted", kind, reason=f"the PC's anchor bond: {kind}")
        return _v(c, i, "supported")
    if store is None and e.kind in ("object", "place") and key not in ("name", "gender", "pronouns") and (
            _incident_given(ctx) or ctx.backed(e.id, "entity_created")) and not _forbidden_new(c):
        # how ordinary furniture looks (wet staves, a curling notice, a stone base) is an implied property of an element
        # written on mention this turn (00.6.6), or the opening's scene dressing; the Oracle is not asked about it
        # [revision: I-127]. ponytail: not written back; write it as an implied property if later turns ask anew
        return _v(c, i, "supported", reason="furniture described as it is written (00.6.6; I-127)")
    if store is None:
        return _oracle_settled(ctx, c, i, pred_slug) or _v(
            c, i, "undetermined", reason=f"{c.predicate or 'property'} not settled in the store")
    if tx.same(c.value, store) or tx.covers(c.value, _flat(store), ratio=0.5) or tx.covers(_flat(store), c.value):
        return _v(c, i, "supported")
    return _v(c, i, "contradicted", store)


def _oracle_settled(ctx: _Ctx, c: Claim, i: int, pred_slug: str) -> Verdict | None:  # rule: 12.3.2
    """A yes/no the Oracle settled for this property at check time: a fact `<predicate>_<asked value>` = bool
    (engine/dm/narration.py `_ask_oracle`). The claimed value asked before: yes supports it, no contradicts it;
    another value is unsettled (None). ponytail: no antonyms ("open" after "closed? no" is asked anew)."""
    if not pred_slug:
        return None
    for f in ctx.state.facts.values():
        if f.subject == c.subject and isinstance(f.value, bool) and f.predicate.startswith(pred_slug + "_"):
            asked = f.predicate[len(pred_slug) + 1:].replace("_", " ")
            if tx.covers(c.value, asked, ratio=1.0):
                return _v(c, i, "supported") if f.value else _v(
                    c, i, "contradicted", f"not {asked}", reason=f"the Oracle settled {c.predicate}: not {asked}")
    return None


def _quantity_name(ctx: _Ctx, subject: str, text: str) -> str | None:
    qs = ctx.state.quantities.get(subject, {})
    for q in qs:
        names = [q, *_QTY_SYNONYMS.get(q, [])]
        if any(tx.has_phrase(text, n) or tx.overlap(n, text) for n in names):
            return q
    return None


def _quantity(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.3.1
    q = _quantity_name(ctx, c.subject, c.text)
    n = tx.number_in(c.value)
    if n is None:
        n = tx.number_in(c.predicate)
    if q is None:
        fid = ctx.state.current_fact_id(c.subject, "_".join(tx.words(c.predicate)))
        if fid is not None and n is not None:
            stored = tx.number_in(_flat(ctx.state.facts[fid].value))
            return _v(c, i, "supported") if stored == n else _v(c, i, "contradicted", ctx.state.facts[fid].value)
        if c.asserts_change:
            return _v(c, i, "unsourced_change", reason="no quantity in the store changed")
        return _v(c, i, "undetermined", reason="no such quantity in the store")
    cur = ctx.state.quantities[c.subject][q].current
    if c.asserts_change and not ctx.backed(c.subject, "quantity_changed", "quantity_defined", key=q):
        return _v(c, i, "unsourced_change", cur, reason=f"no write this turn changed {q}")
    if n is None:
        empty = _has(c.text, ["out of", "empty", "none left", "no more", "spent"])
        if empty != (cur == 0):
            return _v(c, i, "contradicted", cur)
        return _v(c, i, "supported")
    return _v(c, i, "supported") if n == cur else _v(c, i, "contradicted", cur)


def _harm_words(ctx: _Ctx, subject: str) -> str:
    e = ctx.state.entities[subject]
    hs = ctx.state.fact_value(subject, "harm_state")
    if e.exists == "dead" or hs == "harm_state.dead":
        return "dead"
    if isinstance(hs, str) and hs != "harm_state.active":
        return hs.split(".")[-1]
    vit = ctx.state.quantities.get(subject, {}).get("vitality")
    if ctx.state.fact_value(subject, "down"):
        return "down"
    if vit is not None and vit.max:
        if vit.current <= 0:
            return "down"
        if vit.current * 2 <= vit.max:
            return "bloodied"
        if vit.current < vit.max:
            return "hurt"
    if any(inst.condition_id.startswith("cond.wound") or inst.condition_id == "cond.bleeding"
           for inst in ctx.state.conditions_on(subject)):
        return "hurt"
    return "unhurt"


def _claimed_conditions(ctx: _Ctx, text: str) -> list[str]:
    out = []
    for cid, cond in ctx.conditions().items():
        words = [str(cond.get("name", "")), cid.split(".")[-1].replace("_", " "), *_COND_WORDS.get(cid, [])]
        if any(w and tx.has_phrase(text, w) for w in words):
            out.append(cid)
    return out


def _harm(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.3.1
    s, text = ctx.state, c.text
    state_words = _harm_words(ctx, c.subject)
    have = {inst.condition_id for inst in s.conditions_on(c.subject)}
    harm_write = ctx.backed(c.subject, "quantity_changed", "condition_applied", "condition_removed", "fact_set")
    if _has(text, _DEAD):  # a death only with harm_state.dead (07)
        if state_words == "dead":
            return _v(c, i, "supported")
        if c.asserts_change and not harm_write:
            return _v(c, i, "unsourced_change", state_words)
        return _v(c, i, "contradicted", state_words)
    removal = _has(text, _REMOVED)
    claimed = _claimed_conditions(ctx, text)
    if claimed:
        held = [cid for cid in claimed if cid in have]
        names = ", ".join(sorted(str(ctx.conditions()[x].get("name", x)) for x in have)) or "no conditions"
        if removal:
            if held:
                return _v(c, i, "unsourced_change" if c.asserts_change and not harm_write else "contradicted", names)
            if c.asserts_change and not ctx.backed(c.subject, "condition_removed"):
                return _v(c, i, "unsourced_change", names, reason="no condition was removed this turn")
            return _v(c, i, "supported")
        if held:
            return _v(c, i, "supported")
        if c.asserts_change and not ctx.backed(c.subject, "condition_applied"):
            return _v(c, i, "unsourced_change", names, reason="no condition was applied this turn")
        return _v(c, i, "contradicted", names)
    if _has(text, _UNHURT):
        return _v(c, i, "supported") if state_words == "unhurt" else _v(c, i, "contradicted", state_words)
    if _has(text, _HURT):
        if state_words == "unhurt":
            return _v(c, i, "unsourced_change" if c.asserts_change else "contradicted", state_words)
        if c.asserts_change and not harm_write:
            return _v(c, i, "unsourced_change", state_words, reason="no harm was written this turn")
        return _v(c, i, "supported")
    return _v(c, i, "undetermined", state_words, fix="cut", reason="harm words the store cannot settle")


def _position(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.3.1
    s = ctx.state
    if c.asserts_change:
        if ctx.backed(c.subject, "position_set", "time_advanced") or (
                c.subject == ctx.pc and any(b.positions for b in ctx.record.beats)):
            return _v(c, i, "supported")
        return _v(c, i, "unsourced_change", reason="no position was written this turn")
    pos = s.positions.get(c.subject)
    place = ctx.entity_named(c.value, kinds=("place",))
    if place is not None and place != c.subject:
        loc = pos.location if pos else None
        here = s.scene.place_id if s.scene else None
        actual = loc or (here if ctx.present(c.subject) else None)
        if actual is not None and actual != place:
            return _v(c, i, "contradicted", ctx.name(actual))
        return _v(c, i, "supported")
    other = ctx.entity_named(c.value)
    if other is not None and other != c.subject:
        pa, pb = s.positions.get(c.subject), s.positions.get(other)
        if pa and pb and pa.location and pb.location and pa.location != pb.location:
            return _v(c, i, "contradicted", ctx.name(pa.location))
    if pos is not None and ctx.pc and ctx.pc in pos.band_to:
        band = pos.band_to[ctx.pc]
        near = band in ("engaged", "close", "melee", "adjacent")
        if (_has(c.value, _NEAR) and not near) or (_has(c.value, _FAR) and near):
            return _v(c, i, "contradicted", band)
    if not ctx.present(c.subject):
        return _v(c, i, "contradicted", "not in this scene")
    return _v(c, i, "supported")


def _holdings(ctx: _Ctx, subject: str) -> list[str]:
    s = ctx.state
    out: list[str] = []
    for eid in s.entities:
        if eid != subject and ctx.holder(eid) == subject:
            out += [eid, s.entities[eid].name]
    for f in s.facts.values():
        if f.subject == subject and any(tx.same(f.predicate, p) for p in _POSSESS_PREDICATES):
            vals = f.value if isinstance(f.value, list) else [f.value]
            for v in vals:
                out += [str(v), ctx.name(v) if isinstance(v, str) else str(v)]
    for q, qty in s.quantities.get(subject, {}).items():
        if qty.current > 0:
            out += [q, *_QTY_SYNONYMS.get(q, [])]
    return out


def _possession(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.3.1
    item = ctx.entity_named(c.value, kinds=("item", "object", "clue"))
    held = _holdings(ctx, c.subject)
    has_it = (item is not None and item in held) or any(
        tx.content(h) and (tx.covers(h, c.value, ratio=1.0) or tx.covers(c.value, h, ratio=1.0)) for h in held)
    lose = _has(c.text, _LOSE) or _negated(c.text)
    q = _quantity_name(ctx, c.subject, c.text)
    n = tx.number_in(c.value)
    if q is not None and n is not None and not c.asserts_change:  # "a purse of twelve silver": a count held
        cur = ctx.state.quantities[c.subject][q].current
        return _v(c, i, "supported") if n == cur else _v(c, i, "contradicted", cur)
    if c.asserts_change:
        if ctx.backed(c.subject, "fact_set", "position_set", "quantity_changed", "entity_created") or (
                item is not None and ctx.backed(item, "fact_set", "position_set", "entity_created")):
            return _v(c, i, "supported") if has_it != lose else _v(c, i, "contradicted", ", ".join(held[1::2]) or "nothing")
        return _v(c, i, "unsourced_change", reason="no write this turn moved it")
    if lose:
        return _v(c, i, "supported") if not has_it else _v(c, i, "contradicted", "still held")
    if has_it:
        return _v(c, i, "supported")
    if item is not None:
        holder = ctx.holder(item)
        if holder is not None and holder != c.subject:
            return _v(c, i, "contradicted", f"held by {ctx.name(holder)}")
    return _v(c, i, "undetermined", reason="the store does not say whether they carry it")


def _location_time(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.3.1
    s, text = ctx.state, c.text
    watch = s.time.now.watch
    for w, names in _WATCH_WORDS.items():
        hit = tx.any_phrase(text, names)
        if hit:
            ok = _WATCH_EDGES.get(hit, {w})
            if watch not in ok:
                return _v(c, i, "contradicted", _WATCH_NAMES.get(watch, str(watch)))
            if c.asserts_change and not any(wr.type == "time_advanced" for wr in ctx.record.writes) and hit not in _WATCH_EDGES:
                return _v(c, i, "unsourced_change", _WATCH_NAMES.get(watch), reason="no time passed this turn")
            return _v(c, i, "supported")
    if _has(text, _ELAPSED):  # "an hour goes by": time passed this turn beyond the beat itself
        passed = any(w.type == "time_advanced" and set((w.key or "").split()) - {"beat_end", "round"}
                     for w in ctx.record.writes)
        if passed:  # ponytail: the span is not compared with the clock's step; compare to.from_ when it matters
            return _v(c, i, "supported")
        if c.asserts_change:
            return _v(c, i, "unsourced_change", reason="no time passed this turn")
    place = ctx.entity_named(text, kinds=("place",))
    if place is not None:
        subj = s.entities.get(c.subject)
        if subj is not None and subj.kind == "place":
            return _v(c, i, "supported")  # a place described or a landmark named: nobody's whereabouts
        who = c.subject if c.subject in s.entities else ctx.pc
        loc = s.positions[who].location if who in s.positions and s.positions[who].location else None
        here = loc or (s.scene.place_id if s.scene else None)
        if here is not None and place not in _within(s, here):
            return _v(c, i, "contradicted", ctx.name(here), reason=f"the store places them at {ctx.name(here)}")
        return _v(c, i, "supported")
    return _v(c, i, "undetermined", fix="cut", reason="a time or place the store cannot compute")


_ELAPSED = ["hour", "minute", "goes by", "go by", "went by", "passes", "time passes", "elapsed", "a while",
            "the morning wears", "wears on", "moved on"]


def _within(s: WorldState, place: str) -> list[str]:
    """`place` and the places it lies within (`data.parent`, 00.11), innermost first."""
    out = [place]
    while (e := s.entities.get(out[-1])) is not None and isinstance(e.data.get("parent"), str) \
            and e.data["parent"] not in out:
        out.append(e.data["parent"])
    return out


def _knowledge(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.3.1
    s = ctx.state
    known = s.knowledge.get(c.subject, {})
    pool = []
    for fid in known:
        f = s.facts.get(fid)
        if f is not None:
            pool.append(f"{ctx.name(f.subject)} {f.predicate} {_flat(f.value)}")
    match = any(tx.covers(c.value or c.text, p, ratio=0.5) for p in pool)
    if any(tx.covers(c.value or c.text, w, ratio=0.5) for b in ctx.record.beats for w in b.learned):
        return _v(c, i, "supported")  # delivered by this turn's learning beat (12.10.5)
    # "did not see" / "knows him by name": "no" (a negated value inside a positive claim is not a denial)
    negative = _has(c.text, _KNOW_NEGATIVE) or _negated(c.predicate) or tx.words(c.value)[:1] in (
        ["no"], ["not"], ["nothing"], ["never"])
    settled = _settled_question(ctx, c)
    if settled is not None:  # a yes/no the Oracle settled about this subject (01.15.7)
        pred, value = settled
        if value != negative:
            return _v(c, i, "supported")
        return _v(c, i, "contradicted", f"{pred}: {'yes' if value else 'no'}")
    if negative:
        return _v(c, i, "contradicted", "known") if match else _v(c, i, "supported")
    if match:
        return _v(c, i, "supported")
    if c.asserts_change and ctx.backed(c.subject, "knowledge_recorded"):
        return _v(c, i, "supported")
    if _learning_success(ctx, c.subject) and not any(w in c.text.lower() for w in _FORBIDDEN_NEW["clue"]):
        # what a successful Talk/Observe was after and the store lacks: settled now (12.3.2 undetermined -> Oracle)
        return _v(c, i, "undetermined", reason="what the PC asked to learn, not yet settled: the Oracle settles it")
    if c.asserts_change:
        return _v(c, i, "unsourced_change", "not known", reason="no knowledge was recorded this turn")
    return _v(c, i, "contradicted", "not known")


_LEARN_VERBS = ("verb.talk", "verb.observe", "verb.recall")


def _learning_success(ctx: _Ctx, subject: str) -> bool:  # rule: 12.10.5
    """A Talk, Observe or Recall succeeded this turn on `subject` (or `subject` is the PC who made it)."""
    for b in ctx.record.beats:
        if not any(v in (b.approach_words or "") for v in _LEARN_VERBS) or not _beat_success(b):
            continue
        if b.degree is None and not (b.gate_words or "").startswith("no roll"):
            continue
        if subject in (ctx.pc, *b.targets) or ("verb.talk" not in b.approach_words and ctx.present(subject)):
            return True
    return False


def _settled_question(ctx: _Ctx, c: Claim) -> tuple[str, bool] | None:  # rule: 01.15.7
    """A yes/no fact on the claim's subject whose question the claim states ("saw who started the quarrel")."""
    for f in ctx.state.facts.values():
        if f.subject == c.subject and isinstance(f.value, bool) and f.visibility != "sealed":
            pred = f.predicate.replace("_", " ").replace(".", " ")
            if len(tx.content(pred)) >= 2 and tx.covers(pred, c.text, ratio=0.75):
                return pred, f.value
    return None


def _capability(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.3.1
    s, text = ctx.state, c.text
    negative = _negated(text)
    held = s.licenses.get(c.subject, [])
    for inst in held:
        lic = ctx.license(inst.license_id)
        names = [inst.license_id.split(".")[-1].replace("_", " ")]
        scope = ""
        if lic is not None:
            names.append(str(lic.get("name", "")))
            scope = str(lic.get("scope", "")) + " " + " ".join(
                str(g.get("scope", "")) for g in lic.get("grades", ()) if g.get("grade") == inst.grade)
        if any(n and (tx.has_phrase(text, n) or tx.overlap(n, text)) for n in names):
            if negative or not scope or tx.covers(c.value or text, scope, ratio=0.34):
                return _v(c, i, "supported")
            return _v(c, i, "overreach", scope[:200], reason="more than the licence's scope")
    e = s.entities[c.subject]
    if e.kind in ("item", "object"):
        scope = _flat({k: e.data.get(k) for k in ("does", "scope", "properties", "tags") if k in e.data})
        if negative or (scope and tx.covers(c.value or text, scope, ratio=0.34)):
            return _v(c, i, "supported")
        return _v(c, i, "overreach", scope or "no recorded properties")
    if negative:
        return _v(c, i, "supported")
    have = ", ".join(x.license_id for x in held) or "no licences"
    return _v(c, i, "overreach", have, reason="no held licence, ability or item grants this")


def _clock(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.3.1
    s, text = ctx.state, c.text
    found = None
    for cid, clk in s.clocks.items():
        if tx.covers(clk.name, text, ratio=0.5) or (clk.owner and clk.owner == c.subject):
            found = (cid, clk)
            break
    omens = [o for o in ctx.record.omens if found is None or o.clock_id == found[0]]
    if found is None:
        for o in ctx.record.omens:
            if o.omen and tx.covers(o.omen, text, ratio=0.4):
                return _v(c, i, "supported")
        if c.asserts_change:
            return _v(c, i, "unsourced_change", reason="no clock ticked this turn")
        return _v(c, i, "new_element", fix="cut", reason="a pressure the store does not hold")
    cid, clk = found
    if clk.visibility == "hidden" and not omens:
        return _v(c, i, "leak", fix="cut", reason="a hidden clock")
    if _has(text, _CLOCK_DONE):
        done = clk.status == "completed" or any(o.completed for o in omens)
        return _v(c, i, "supported") if done else _v(c, i, "contradicted", f"{clk.name}: not complete")
    if c.asserts_change or _has(text, _CLOCK_MOVE):
        if any(o.ticked for o in omens) or ctx.backed(cid, "clock_ticked") or any(
                w.type == "clock_ticked" and w.key == cid for w in ctx.record.writes):
            return _v(c, i, "supported")
        return _v(c, i, "unsourced_change", clk.name, reason="the clock did not tick this turn")
    return _v(c, i, "supported")


def _attitude_sign(text: str) -> int:
    pos, neg = _has(text, _POS_ATT), _has(text, _NEG_ATT)
    if pos == neg:
        return 0
    return (1 if pos else -1) * (-1 if _negated(text) else 1)  # "not your friend" reads as negative [P-036]


def _attitude(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.3.1
    sign = _attitude_sign(c.text)
    if c.asserts_change:
        sourced = ctx.backed(c.subject, "relationship_set") or any(
            c.subject in b.targets and b.degree is not None for b in ctx.record.beats) or any(
            a.npc == c.subject for a in ctx.record.npc_actions)
        return _v(c, i, "supported") if sourced else _v(c, i, "unsourced_change", reason="no standing changed")
    rel = ctx.state.relationships.get(f"{c.subject}|{ctx.pc}|standing")
    value = rel.value if rel else 0
    rung = min(ctx.standings(), key=lambda r: abs(r[0] - value))[1]
    have = (value > 0) - (value < 0)
    if sign and have and sign != have:
        return _v(c, i, "contradicted", rung)
    if sign and not have and _has(c.text, _STRONG_ATT):
        return _v(c, i, "contradicted", rung)
    return _v(c, i, "supported")


def _beat_for(ctx: _Ctx, text: str) -> BeatEntry | None:
    beats = [b for b in ctx.record.beats if b.degree is not None or b.gate]
    if not beats:
        return None
    scored = [(len(tx.overlap(text, " ".join([b.restatement, *b.reach_words]))), n, b) for n, b in enumerate(beats)]
    return max(scored, key=lambda x: (x[0], x[1]))[2]


def _beat_success(b: BeatEntry) -> bool:
    if b.degree is None and b.gate_words and b.gate != "G0" and not b.gate_words.startswith("no roll"):
        return False  # refused or withdrawn before any result (pipeline `_entry` gate words)
    if b.degree is not None:
        return b.degree in ("success", "critical_success") or b.success_at_cost
    return not (b.gate or "").lower().startswith(("g3", "g4", "redirect", "refus"))


def _outcome(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.3.1
    text = c.text
    b = _beat_for(ctx, text)
    if b is None:
        return _v(c, i, "unsourced_change", reason="no resolved beat this turn")
    degree_words = (b.degree or "no roll").replace("_", " ")
    failed_claim = _has(text, _FAILURE) or (_negated(text) and not _has(text, _COST))
    ok = _beat_success(b)
    if failed_claim and ok:
        return _v(c, i, "contradicted", degree_words, reason=f"the attempt's result was {degree_words}")
    if not failed_claim and not ok and (_has(text, _SUCCESS) or not _has(text, _COST)):
        return _v(c, i, "contradicted", degree_words, reason=f"the attempt's result was {degree_words}")
    if _has(text, _BIG) and b.degree != "critical_success":
        return _v(c, i, "overreach", ", ".join(b.reach_words) or degree_words, reason="beyond the delivered reach")
    if _has(text, _COST):
        if not b.costs:
            return _v(c, i, "overreach", "no cost was applied")
        forms = " ".join(f"{x.menu_id} {x.form}" for x in b.costs)
        extra = tx.content(c.value) - tx.content(forms) - tx.content("cost costs you price pay it but")
        if extra and not tx.overlap(c.value, forms):
            return _v(c, i, "overreach", "; ".join(x.form or x.menu_id for x in b.costs),
                      reason="a cost of another entry")
    return _v(c, i, "supported")


def _action(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.2.9
    text = c.text
    if c.subject == ctx.pc:  # the PC's acts are the player's: judged by the pc_words_or_feelings flag (12.14.3)
        return _v(c, i, "supported")
    if not c.asserts_change:  # an ongoing description ("she watches you"), not an act this turn
        if ctx.state.entities[c.subject].exists != "exists" or not ctx.present(c.subject):
            return _v(c, i, "contradicted", "not in this scene")
        return _v(c, i, "supported")
    rows = [a for a in ctx.record.npc_actions if a.npc == c.subject]
    for a in rows:
        if tx.overlap(text, " ".join([a.action, *a.tags])):
            return _v(c, i, "supported")
    for b in ctx.record.beats:
        if (b.actor == c.subject or c.subject in b.targets) and tx.overlap(text, " ".join([b.restatement, *b.reach_words])):
            return _v(c, i, "supported")
    for o in ctx.record.omens:
        if o.omen and tx.overlap(text, o.omen) and tx.covers(ctx.name(c.subject), o.omen, ratio=0.5):
            return _v(c, i, "supported")
    if not _deed(text) and _addressed(ctx, c.subject) and ctx.present(c.subject):
        # 12.2.9 (2): the PC's beat, question or words are the source of the response; "the DM chooses the words",
        # so speech and manner pass; a deed (giving, leaving, attacking, changing a state) still needs its source
        return _v(c, i, "supported", reason="a response in words and manner to the PC (12.2.9)")
    if ctx.present(c.subject) and _reacts_to_incident(ctx, c):  # the cast present witness the incident
        return _v(c, i, "supported", reason="a reaction to the inciting incident (12.16.16)")
    store = "; ".join(a.action for a in rows) or None
    return _v(c, i, "unsourced_change", store, reason="no source for this act in the adjudication record")


def _sealed(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 00.6.5
    # A sealed-class claim that matched no sealed item (the leak test ran first): a shown fact, or an invented secret.
    for f in ctx.state.facts.values():
        if f.visibility != "sealed" and (c.subject in (f.subject, UNKNOWN)) and tx.covers(c.value or c.text, _flat(f.value)):
            return _v(c, i, "supported")
    return _v(c, i, "new_element", fix="cut", reason="a hidden truth the store does not hold")


_CLASS_CHECKS = {
    "existence": _existence, "identity": _identity, "quantity": _quantity, "harm_condition": _harm,
    "position": _position, "possession": _possession, "location_time": _location_time, "knowledge": _knowledge,
    "capability": _capability, "clock": _clock, "attitude": _attitude, "outcome": _outcome, "action": _action,
    "sealed": _sealed,
}


# ------------------------------------------------------------------------------------------- owed blocks

OWED_BLOCKS = {"trg.lethal_warning": "[WARNING]", "trg.exits": "[STATUS]"}


def owed_blocks(triggers: Iterable[Any], response: str) -> list[str]:  # rule: 12.3.2
    """Labels of blocks the turn owes (a lethal warning, the exits status) that `response` lacks; a missing one
    fails the check as if a claim were contradicted."""
    ids = {t if isinstance(t, str) else getattr(t, "id", "") for t in triggers}
    return [label for trg, label in OWED_BLOCKS.items() if trg in ids and label not in response]


def failing(verdicts: Iterable[Verdict]) -> list[Verdict]:
    """The verdicts that need a fix (anything but supported, 12.3.3)."""
    return [v for v in verdicts if v.verdict != "supported"]
