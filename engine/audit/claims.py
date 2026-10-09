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

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from engine.audit import text as tx
from engine.dm.adjudication import AdjudicationRecord, BeatEntry
from engine.retrieve.scene import cannot_read
from engine.store.projection import WorldState
from engine.store.views import item_words, name_known, unnamed_label

ClaimClass = Literal["existence", "identity", "quantity", "harm_condition", "position", "possession",
                     "location_time", "knowledge", "capability", "clock", "attitude", "outcome", "action", "sealed"]
VerdictName = Literal["supported", "new_element", "undetermined", "contradicted", "unsourced_change", "overreach",
                      "leak", "pc_agency"]
Fix = Literal["write_on_mention", "oracle", "redraft_to_store", "cut", "replace_with_slice"]

UNKNOWN = "unknown"
_SCENE_STATE_KEYS = ("activity", "voice", "detail.activity", "detail.posture", "detail.held", "detail.manner")
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
    incidental: bool = False  # an `undetermined` property 12.3.2 writes as narrated (T1a), not one for the Oracle
    uncertain: bool = False  # 12.3.1b item 4: the subject is not certain, so the verdict counts for nothing (logged)

    @property
    def disposition(self) -> str:
        """The claim-log verdict: `no_verdict` for an uncertain subject (DL-12-82), else the verdict."""
        return "no_verdict" if self.uncertain else self.verdict


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
# coarse position (owner ruling, DL-12-77): a hold or its end, mounting, arriving or leaving; with a named place and a
# band to the PC, the only position a sentence is judged on. Fine placement is atmosphere (T0) [spec 010]
_HOLD = ["grab", "grabs", "seize", "seizes", "pin", "pins", "pinned", "restrain", "restrains", "let go", "lets go",
         "release", "releases", "breaks free", "pulls free", "twists free", "mount", "mounts", "dismount", "dismounts"]
_COME_GO = ["leave", "leaves", "left", "goes out", "walks out", "steps out", "slips out", "exits", "departs", "gone",
            "arrive", "arrives", "enters", "comes in", "walks in", "steps in"]
_TO_PC = ["you", "your", "reach"]  # a band is stated to the PC ("at your shoulder", "out of reach")
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
_PRESSURE = [*_CLOCK_MOVE, *_CLOCK_DONE, "mass", "brew", "loom", "approach", "storm", "threat", "alarm", "danger",
             "hunt", "search"]  # what makes a clock claim literal (12.3.1) [spec 009 B]
_POSSESS_PREDICATES = ("carries", "holds", "has", "equipped", "possessions", "inventory", "owns", "possession",
                       "wields", "wears")
# 12.3.2's enumerated consequential properties (locked, armed, present, knows) and what 12.14.13 names T2 (hidden,
# hazard, value); any other class than identity or possession is consequential too (uncertain -> consequential)
_CONSEQUENTIAL = ["lock", "locked", "unlocked", "armed", "weapon", "blade", "sword", "knife", "dagger", "bow", "spear",
                  "axe", "present", "absent", "alive", "dead", "know", "knows", "hidden", "secret", "trap", "poison",
                  "key", "guard", "magic", "enchanted", "valuable", "treasure"]
_REFUSE = ["refuse", "refuses", "refusal", "will not say", "won't say", "will not tell", "won't tell", "not say",
           "will not give", "won't give", "withhold", "withholds", "declines to", "not from me", "keeps the name",
           "not now", "says nothing", "gives you nothing", "gives nothing"]
_LOSE = ["drop", "lose", "lost", "give", "hand over", "hands over", "sold", "sell", "stolen", "no longer", "toss",
         "throw away", "surrender", "gone"]


def _has(text: str, phrases: Iterable[str]) -> bool:
    return tx.any_phrase(text, phrases) is not None


def _negated(text: str) -> bool:
    return _has(text, _NEGATION) or "n't" in text.lower()


# ------------------------------------------------------------------------------------------- context


class _Ctx:
    def __init__(self, state: WorldState, record: AdjudicationRecord, scene_ids: Sequence[str], rules: Any,
                 cited: Mapping[int, Sequence[Any]] | None = None) -> None:
        self.state = state
        self.record = record
        self.scene_ids = list(scene_ids)
        self.rules = rules
        self.cited = dict(cited or {})  # sentence index -> the record items it cites (engine/dm/handles.py)
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

    def holder(self, eid: str) -> str | None:  # rule: 01.2.7
        """The current `holder` fact (what a take or give wrote) before narrated holder facts and data keys."""
        from engine.resolve.change import holder_of

        return holder_of(self.state, eid)

    def backed(self, entity: str | None, *types: str, key: str | None = None) -> bool:
        """A write this turn touched `entity` (of one of `types`; with `key` when given)."""
        if entity is None:
            return False
        for w in self.record.writes_for(entity, *types):
            if w.key in _SCENE_STATE_KEYS:
                continue  # 12.11.9 scene state (an activity, a voice rolled on first answer) backs no change
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
                 scene_ids: Sequence[str] = (), *, rules: Any = None, cited: Mapping[int, Sequence[Any]] | None = None,
                 texts: Mapping[int, str] | None = None) -> list[Verdict]:  # rule: 12.3.2
    """One verdict per claim (12.3.2). `state`: a `WorldState` or a `Store` (its projection is read).
    `scene_ids`: the ids the Checker was offered (the schema's subject enum). Subjects are checked against the
    whole store; presence in the scene comes from the scene record and positions, not from this list. `cited`:
    per sentence index, the record items (engine/dm/handles.py) that sentence's declaration cites (12.3.1): a
    claim restating a cited line, or an act its subject's cited line sources, is supported. `texts`: per sentence
    index, its words; given, a claim about an entity whose subject the words do not make certain takes
    no verdict in either direction (`uncertain`, 12.3.1b item 4, DL-12-82)."""
    ws: WorldState = state.state if hasattr(state, "transaction") else state
    ctx = _Ctx(ws, record or AdjudicationRecord(), scene_ids, rules, cited)
    out = []
    for i, raw in enumerate(claims):
        c = raw if isinstance(raw, Claim) else Claim.model_validate(raw)
        v = _check(ctx, c, i)
        text = (texts or {}).get(c.sentence)
        if text is not None and v.verdict not in ("pc_agency", "leak") and c.subject in ws.entities \
                and not certain(ws, c.subject, text, pc=ctx.pc, scope=scene_ids, record=ctx.record):
            v = v.model_copy(update={"uncertain": True, "fix": None,
                                     "reason": f"the subject is not certain: no verdict, logged ({v.reason})"})
        out.append(v)
    return out


# ------------------------------------------------------------------------------------------- 12.3.1b

# a mechanically relevant possession (12.3.1b item 2.3): a weapon, armour, tool, key, consumable, coin, value
_RELEVANT = [*_CONSEQUENTIAL, "armour", "armor", "shield", "mail", "helm", "tool", "rope", "lantern", "torch",
             "potion", "salve", "ration", "rations", "arrow", "arrows", "coin", "coins", "silver", "gold", "copper",
             "purse", "money", "crossbow", "club", "mace", "hammer", "crowbar", "lockpick", "pick"]
_BLOCKING = {"outcome", "capability", "harm_condition", "quantity", "possession", "position", "existence", "sealed",
             "identity"}  # pacing.yaml#claim_check.blocking's classes (the default when no rules are given)


def relevant_item(text: str) -> bool:  # rule: 12.3.1b
    """A weapon, armour, tool, key, consumable, coin or a thing of value named in `text` (12.3.1b item 2.3)."""
    return _has(text, _RELEVANT)


def blocking(c: Claim, v: Verdict, rules: Any = None) -> bool:  # rule: 12.3.1b
    """Is this failing claim on the blocking list (12.3.1b item 2)? PC agency and sealed content always; a
    possession only of a relevant item; identity only for a name. The caller adds the narrator's voice and a
    certain subject; everything else is logged."""
    if v.verdict in ("pc_agency", "leak"):
        return True
    classes = _BLOCKING
    if rules is not None:
        rows = (rules.pacing.get("claim_check") or {}).get("blocking") or []
        classes = {cl for r in rows for cl in r.get("classes") or []} or _BLOCKING
    if c.cls not in classes:
        return False
    if c.cls == "possession":
        return _has(c.text, _RELEVANT)
    if c.cls == "identity":
        return _identity_key(c.predicate) == "name"
    return True


def _head(name: str) -> str | None:
    """The last content word of a name ("the red sword" -> "sword"; "shrine attendant" -> "attendant")."""
    words = [w for w in re.findall(r"[a-z]+", (name or "").lower()) if w not in ("the", "a", "an", "of", "and")]
    return words[-1] if words else None


def _forms(e: Any) -> tuple[list[str], str | None]:
    """(whole names and aliases, lower case; the head noun of the name or role)."""
    names = [e.name, *(a for a in e.data.get("aliases") or [] if isinstance(a, str))]
    if e.kind in ("npc", "pc", "companion", "adversary") and len(e.name.split()) > 1:
        names.append(e.name.split()[0])
    names = [re.sub(r"^(?:the|a|an)\s+", "", n.strip().lower()) for n in names if n and len(n) > 2]
    head = _head(e.name) if e.kind not in ("npc", "pc", "companion", "adversary") else _head(
        str(e.data.get("role") or "").split(" or ")[0])
    return names, head


def _proper(name: str) -> bool:
    return any(w[:1].isupper() for w in name.split() if w.lower() not in ("the", "a", "an"))


def certain(state: WorldState, subject: str, text: str, *, pc: str | None = None, scope: Iterable[str] = (),
            record: AdjudicationRecord | None = None) -> bool:  # rule: 12.3.1b
    """12.3.1b item 4: does `text` make `subject` the one entity it speaks of? The PC and this turn's beats'
    people are certain; else (a) a whole name or alias no other entity in scope shares (a place's common-noun
    name, "the hall", does not count); (b) a head noun ("the sword") that only one entity in scope fits; (c) no
    mention (a pronoun): the only candidate of its kind present."""
    from engine.retrieve.scene import scene_scope

    if subject == pc or (record is not None and any(subject in (b.actor, *b.targets) for b in record.beats)):
        return True
    e = state.entities.get(subject)
    if e is None:
        return False
    pool = [i for i in dict.fromkeys([*scope, *scene_scope(state), subject]) if i in state.entities and i != pc]
    low = text.lower()

    def said(n: str) -> bool:
        return bool(re.search(rf"\b{re.escape(n)}\b", low))

    names, head = _forms(e)
    whole = [n for n in names if said(n)]
    if whole and (e.kind != "place" or _proper(e.name)):
        return not any(said(n) for o in pool if o != subject for n in _forms(state.entities[o])[0] if n in whole)
    if head and said(head):
        return sum(1 for o in pool if _forms(state.entities[o])[1] == head or any(
            said(n) for n in _forms(state.entities[o])[0] if head in n.split())) == 1
    if whole:  # a common-noun place named alone: never certain (DL-12-82)
        return False
    people = ("npc", "companion", "adversary")
    group = [o for o in pool if (state.entities[o].kind in people) == (e.kind in people)
             and state.entities[o].kind != "place"]
    return group == [subject]


def _check(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: PR-12-2
    if c.pc_words_or_feelings and not _agency_licensed(ctx, c):  # rule: 12.14.3
        return _v(c, i, "pc_agency", reason="gives the PC words, choices or feelings the player did not state")
    leak = _leak(ctx, c)
    if leak is not None:
        return _v(c, i, "leak", leak or None, fix="replace_with_slice" if leak else "cut",
                  reason="matches sealed content")
    if _restates_cited(ctx, c):
        return _v(c, i, "supported", reason="restates a record line the sentence cites (12.3.1)")
    if _restates_lead(ctx, c):
        return _v(c, i, "supported", reason="restates an open lead the character knows (12.3.2 support scope)")
    subject = c.subject
    if subject != UNKNOWN and subject not in ctx.state.entities:
        subject = UNKNOWN  # an id the store does not hold is no better than unknown
    if subject == UNKNOWN:
        subject = _resolve_new(ctx, c) or UNKNOWN
    if subject == UNKNOWN and c.cls not in _FREE_SUBJECT:  # rule: 12.3.2 [revision: I-127; DL-12-37]
        if c.cls == "action" and not c.asserts_change and ctx.cited.get(c.sentence):
            # an unnamed bystander's reaction to a line the sentence cites (heads turn at the incident): its source
            return _v(c, i, "supported", reason="a reaction to a cited record line (12.3.1)")
        if c.cls == "action" and not c.asserts_change and _has(c.text, ["no one", "nobody", "none"]):
            return _v(c, i, "supported", reason="nobody acted: nothing to source (12.3.1)")  # [spec 009 B]
        if c.asserts_change or c.cls == "action":
            return _v(c, i, "unsourced_change", reason="an unidentified subject changed or acted; cut")
        if c.cls in ("knowledge", "sealed"):  # 12.14.13: knowledge beyond the view is T1b/T2, never written so
            return _v(c, i, "new_element", fix="cut", reason="undeclared knowledge may not be created by mention; cut")
        # an undeclared new element (spec 011: the sampled audit logs this verdict; nothing writes it after delivery)
        return _v(c, i, "new_element", fix="write_on_mention", reason="a new ordinary element: write it on mention")
    c = c.model_copy(update={"subject": subject})
    return _CLASS_CHECKS[c.cls](ctx, c, i)


def _incident_given(ctx: _Ctx) -> bool:  # rule: 12.16.16
    """This is the opening: the record carries the inciting incident as given."""
    return any(n.startswith("the inciting incident:") for n in ctx.record.notes)


def _cited(ctx: _Ctx, c: Claim) -> list[Any]:
    return list(ctx.cited.get(c.sentence, ()))


def _restates_cited(ctx: _Ctx, c: Claim) -> bool:  # rule: 12.3.1
    """The claim restates a record line its sentence cites (most of its content words are in that line), about the
    line's own subject (another person saying the same words is not sourced by it, P-118)."""
    return any(tx.covers(c.text, f"{it.text} {it.render}", ratio=0.6)
               and (not it.entities or c.subject in it.entities or c.subject in (UNKNOWN, ctx.pc))
               for it in _cited(ctx, c))


def _restates_lead(ctx: _Ctx, c: Claim) -> bool:  # rule: 12.3.2
    """The claim (with its subject's name) restates an active thread the character knows (an opening lead: "a
    quarrel in the inn turns to a challenge"; "two banners in the hall"): the view holds it, so it is supported as
    told, never re-judged as a clock tick or a position here [spec 009 B]."""
    named = f"{ctx.name(c.subject) if c.subject != UNKNOWN else ''} {c.text}"
    for e in ctx.state.entities.values():
        if e.kind != "thread" or e.visibility not in ("shown", "available") or e.id in ctx.state.seals:
            continue
        lead = f"{e.name} {e.data.get('text') or ''}"
        if any(len(tx.content(w)) >= 3 and tx.covers(w, lead, ratio=0.6) for w in (c.text, named)):
            return True
    return False


def _incidental(c: Claim) -> bool:  # rule: 12.3.2
    """An `undetermined` property 12.3.2 writes as narrated: identity (not name, sex or pronouns) or the possession
    of an ordinary thing, naming none of 12.3.2's consequential properties (locked, armed, present, knows, ...).
    Uncertain -> consequential."""
    if c.cls not in ("identity", "possession") or _identity_key(c.predicate) in ("name", "gender", "pronouns"):
        return False
    return not _has(c.text, _CONSEQUENTIAL)


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
    if pred_slug in ("voice", "tone", "speech"):  # how they speak is the narrator's, through their voice (12.11.9)
        return _v(c, i, "supported", reason="words and manner are the narrator's (12.11.9 step 4)")
    if key == "name":
        names = [e.name, *[a for a in e.data.get("aliases", []) if isinstance(a, str)]]
        if any(tx.same(c.value, n) or tx.covers(c.value, n, ratio=1.0) for n in names):
            # 12.10.2: a name the PC has not learned is a slip (one learned this turn is known by now)
            if not name_known(ctx.state, e.id) and tx.covers(e.name.split()[0], c.value, ratio=1.0):
                return _v(c, i, "contradicted", unnamed_label(e), reason="the PC has not learned this name")
            return _v(c, i, "supported")
        return _v(c, i, "contradicted", e.name)
    if key not in ("name", "gender", "pronouns", "age", "role", "people", "kin"):  # rule: 00.6.6a
        from engine.store.details import current, slot_of

        slot = slot_of(c.predicate, ctx._rules(), e.kind) or slot_of(c.value, ctx._rules(), e.kind)
        held = current(ctx.state, e.id, slot) if slot else None
        if held is not None and held.value is not None:  # the profile: same -> supported, else redraft to it
            if tx.same(c.value, held.value) or tx.covers(c.value, _flat(held.value), ratio=0.5) or tx.covers(
                    _flat(held.value), c.value):
                return _v(c, i, "supported", reason=f"restates the established {slot} (00.6.6a)")
            return _v(c, i, "contradicted", held.value, reason=f"its {slot} is established (00.6.6a)")
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
            why = cannot_read(ctx.state, ctx.pc, e.id)  # 02.4.6: words the PC cannot read reach them only aloud
            aloud = ctx.record.npc_actions or any("talk" in (b.approach_words or "") for b in ctx.record.beats)
            if why and not aloud:  # [P-110]
                return _v(c, i, "contradicted", "words the character cannot read",
                          reason=f"the character cannot read it ({why}); say so instead of quoting it")
            return _v(c, i, "supported")
    bond = ctx.state.fact_value(ctx.pc, "bond.anchor") if ctx.pc else None  # rule: 02.9.2 [P-036]
    if store is None and isinstance(bond, dict) and bond.get("npc") == e.id and _has(c.predicate, _BOND_WORDS):
        kind = str(bond.get("kind") or "friend")  # the PC's anchor bond is who this NPC is to them, never asked anew
        if _negated(c.value) or not tx.covers(c.value, kind, ratio=1.0):
            return _v(c, i, "contradicted", kind, reason=f"the PC's anchor bond: {kind}")
        return _v(c, i, "supported")
    if store is None and e.kind in ("object", "place") and key not in ("name", "gender", "pronouns") and (
            _incident_given(ctx) or ctx.backed(e.id, "entity_created")) and _incidental(c):
        # how ordinary furniture looks (wet staves, a curling notice, a stone base) is an implied property of an element
        # written on mention this turn (00.6.6), or the opening's scene dressing; the Oracle is not asked about it
        # [revision: I-127]. ponytail: not written back; write it as an implied property if later turns ask anew
        return _v(c, i, "supported", reason="furniture described as it is written (00.6.6; I-127)")
    if store is None:
        settled = _oracle_settled(ctx, c, i, pred_slug)
        if settled is not None:
            return settled
        v = _v(c, i, "undetermined", reason=f"{c.predicate or 'property'} not settled in the store")
        return v.model_copy(update={"incidental": _incidental(c)})
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
    look = " ".join(str(s.entities[c.subject].data.get(k) or "") for k in ("demeanor", "detail"))
    if claimed and tx.overlap(c.value or text, look):
        return _v(c, i, "supported", reason="their recorded demeanor, not a condition")  # "weary" (spec 006)
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
    if harm_write and state_words != "unhurt":  # harm written this turn (a foe's landed strike) in any words (P-116)
        return _v(c, i, "supported")
    # a look or manner the store has not settled ("a dry cough", "flustered"): an incidental property, written as
    # narrated (12.3.2's split, DL-12-40); the harm words above are the consequential ones
    if c.asserts_change or c.subject == ctx.pc:  # a blow landed, a change to the PC: nothing written backs it
        return _v(c, i, "undetermined", state_words, fix="cut", reason="harm words the store cannot settle")
    v = _v(c, i, "undetermined", state_words, fix="oracle", reason="a manner or look the store has not settled")
    return v.model_copy(update={"incidental": True})


_TOWARD = ("toward", "towards", "past", "beyond", "to", "from", "into", "for")  # a direction, not a location


def _not_located_at(ctx: _Ctx, c: Claim, place: str) -> bool:  # rule: 12.3.1
    """The place a position value names does not say the subject is there: it is named after a direction word ("the
    lane runs past the well toward the temple"), or its name is a common noun ("the hall") and the subject is here,
    where those words describe this place's own parts ("the fire at the far end of the hall" in an inn) [spec 010].
    ponytail: the head noun is not checked against this place's kind; a proper name ("the Old Goose") still binds"""
    name = re.sub(r"^(?:the|a|an)\s+", "", ctx.state.entities[place].name.strip(), flags=re.IGNORECASE)
    m = re.search(rf"\b{re.escape(name.lower())}\b", c.value.lower())
    if m is not None and any(w in _TOWARD for w in re.findall(r"[a-z]+", c.value.lower()[:m.start()])[-2:]):
        return True
    return not any(w[:1].isupper() for w in name.split()) and ctx.present(c.subject)


def _coarse(ctx: _Ctx, c: Claim) -> bool:  # rule: 12.3.1
    """The claim states coarse position (DL-12-77): a place by its name, a band to the PC, a hold or its end,
    mounting, arriving or leaving. Anything else ("by the hearth", "turns to the window") is atmosphere (T0)."""
    place = ctx.entity_named(c.value, kinds=("place",))
    return (place is not None and not _not_located_at(ctx, c, place)) or _has(c.text, [*_HOLD, *_COME_GO]) or (
        _has(c.value, _TO_PC) and _has(c.value, [*_NEAR, *_FAR]))


def _position(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.3.1
    s = ctx.state
    if c.asserts_change:
        if ctx.backed(c.subject, "position_set", "time_advanced") or (
                c.subject == ctx.pc and any(b.positions for b in ctx.record.beats)):
            return _v(c, i, "supported")
        # the resolved beat that moved them ("I shove him back a step"), or the cited response line for a turn or a
        # step in place (manner, 12.11.9 step 4); a move to another place still needs a write (spec 006)
        if any(c.subject in b.targets and (b.degree is not None or b.gate_words.startswith("no roll"))
               and _beat_success(b) and tx.overlap(c.text, b.restatement) for b in ctx.record.beats):
            return _v(c, i, "supported", reason="the resolved beat moved them")
        if ctx.entity_named(c.value, kinds=("place",)) is None and any(
                c.subject in getattr(it, "entities", ()) for it in _cited(ctx, c)):
            return _v(c, i, "supported", reason="manner in the cited record line (12.11.9)")
        if ctx.present(c.subject) and not _coarse(ctx, c):  # a turn, a lean, a step to the window
            return _v(c, i, "supported", reason="fine placement is atmosphere (T0, DL-12-77)")
        return _v(c, i, "unsourced_change", reason="no position was written this turn")
    pos = s.positions.get(c.subject)
    place = ctx.entity_named(c.value, kinds=("place",))
    if place is not None and _not_located_at(ctx, c, place):
        place = None
    if place is not None and place != c.subject:
        loc = pos.location if pos else None
        here = s.scene.place_id if s.scene else None
        actual = loc or (here if ctx.present(c.subject) else None)
        if actual is not None and actual != place:
            return _v(c, i, "contradicted", ctx.name(actual))
        return _v(c, i, "supported")
    # beside someone or something in the scene (another place's "hearth" is not this one's: spec 006)
    other = ctx.entity_named(c.value, among=ctx.scene_ids or None)
    if other is not None and other != c.subject:
        pa, pb = s.positions.get(c.subject), s.positions.get(other)
        if pa and pb and pa.location and pb.location and pa.location != pb.location:
            return _v(c, i, "contradicted", ctx.name(pa.location))
    if pos is not None and ctx.pc and ctx.pc in pos.band_to and _has(c.value, _TO_PC):  # a band is to the PC
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
            out += [eid, s.entities[eid].name, *(w for t in item_words(s, eid)[1:] for w in (t, t))]
    for f in s.facts.values():
        if f.subject == subject and any(tx.same(f.predicate, p) for p in _POSSESS_PREDICATES):
            vals = f.value if isinstance(f.value, list) else [f.value]
            for v in vals:
                out += [str(v), ctx.name(v) if isinstance(v, str) else str(v)]
                if isinstance(v, str):  # the sheet's rapier is also "a blade", "a weapon" (P-090)
                    out += [w for t in item_words(s, v)[1:] for w in (t, t)]
    for q, qty in s.quantities.get(subject, {}).items():
        if qty.current > 0:
            out += [q, *_QTY_SYNONYMS.get(q, [])]
    return out


def _possession(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.3.1
    subj = ctx.state.entities.get(c.subject)
    if subj is not None and subj.kind in ("item", "object", "clue") and not c.asserts_change:
        # the thing is the subject ("the bone: not in Falett's hand"): read its holder (P-073)
        holder, who = ctx.holder(c.subject), ctx.entity_named(c.text, kinds=("npc", "pc", "companion"))
        if holder is not None and who is not None:
            said = (who == holder) != (_negated(c.text) or _has(c.text, _LOSE))
            return _v(c, i, "supported") if said else _v(c, i, "contradicted", f"held by {ctx.name(holder)}")
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
    v = _v(c, i, "undetermined", reason="the store does not say whether they carry it")
    return v.model_copy(update={"incidental": _incidental(c)})


def _location_time(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.3.1
    s, text = ctx.state, c.text
    watch = s.time.now.watch
    if _has(text, _ANOTHER_TIME):  # "last night", "yesterday": another time's events, not the hour now (00.6.9e)
        return _v(c, i, "supported", reason="another time than now: not the store's hour")
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
        who = c.subject if c.subject in s.entities else None
        if who is None:
            return _v(c, i, "supported")  # where an event took place: nobody's whereabouts (spec 006)
        loc = s.positions[who].location if who in s.positions and s.positions[who].location else None
        here = loc or (s.scene.place_id if s.scene else None)
        if here is not None and place not in _within(s, here):
            return _v(c, i, "contradicted", ctx.name(here), reason=f"the store places them at {ctx.name(here)}")
        return _v(c, i, "supported")
    # 12.3.1: atmosphere is checked only against the hour, season, weather and place the store holds; with none of
    # those named there is nothing to contradict (spec 006: never cut as "undetermined")
    return _v(c, i, "supported", reason="names no hour or place the store holds: atmosphere")


_ANOTHER_TIME = ["last night", "yesterday", "ago", "the night before", "the day before", "tomorrow", "earlier",
                 "last week", "years", "once"]
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
    # the open matters any local may know (12.14.12's speech line: active, shown threads) are known to anyone
    pool += [str(e.data.get("text") or e.name) for e in s.entities.values() if e.kind == "thread"
             and e.data.get("status", "active") == "active" and e.visibility in ("shown", "available")
             and e.id not in s.seals]
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
    if c.asserts_change:
        return _v(c, i, "unsourced_change", "not known", reason="no knowledge was recorded this turn")
    return _v(c, i, "contradicted", "not known")


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
        if c.subject == UNKNOWN and not _has(text, _PRESSURE):  # "it is only the beginning": a figure of speech
            # naming no clock and no pressure building (12.3.1); "a storm is massing" is a pressure, and is cut
            return _v(c, i, "supported", reason="atmosphere: no addressable clock or omen is named (12.3.1)")
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


def _beat_for(ctx: _Ctx, text: str, subject: str | None = None) -> BeatEntry | None:
    beats = [b for b in ctx.record.beats if b.degree is not None or b.gate]
    if not beats:
        return None
    # ties go to a beat acting on the claim's subject, then to a rolled beat: an outcome no words tie to a later
    # redirect is the roll's, not the redirect's "no roll" [P-112]
    scored = [(len(tx.overlap(text, " ".join([b.restatement, *b.reach_words, b.change, b.changed]))),
               subject in b.targets,
               b.degree is not None, n, b) for n, b in enumerate(beats)]
    return max(scored, key=lambda x: x[:4])[4]


def _beat_success(b: BeatEntry) -> bool:
    if b.degree is None and b.gate_words and b.gate != "G0" and not b.gate_words.startswith("no roll"):
        return False  # refused or withdrawn before any result (pipeline `_entry` gate words)
    if b.degree is not None:
        return b.degree in ("success", "critical_success") or b.success_at_cost
    return not (b.gate or "").lower().startswith(("g3", "g4", "redirect", "refus"))


_PLAIN_FAIL = ["fail", "fails", "failed", "in vain", "no luck", "won't budge", "will not budge", "holds firm",
               "falls short", "fall short", "does not give", "doesn't give", "stays shut", "comes to nothing",
               # a blow or grip that does not land (playtest 20261008-135049: "the point stops a finger's width
               # short", "stops a finger's width from her", "the cloth slips through your grip")
               "stops short", "stop short", "width short", "width from", "breadth from", "goes wide", "go wide",
               "misses", "nothing but air", "slip through your grip", "slip from your grip"]
_PLAIN_WIN = ["you succeed", "it works", "you manage", "gives way", "you make it", "you do it", "it gives"]
UNDECIDED = "a near miss not yet decided"


def undecided(b: BeatEntry, pause: Any = None) -> bool:  # rule: 01.9.3
    """The beat waits on the near-miss choice (01.9.3): its recorded degree is `failure`, but whether it lands is
    the player's pick, so neither result may be narrated yet."""
    return bool(b.near_miss and not b.success_at_cost and pause is not None
                and getattr(pause, "kind", None) == "near_miss" and getattr(pause, "frame_id", None) == b.frame_id)


def passage_beat(beats: Iterable[BeatEntry]) -> BeatEntry | None:  # rule: 12.3.1
    # rule: 12.3.1b
    """The beat a passage's plain result words are judged against (12.3.1b item 1, outcome): the turn's one resolved
    beat, or the first of several that all went the same way; None when their results differ, since a passage
    declares no sentence's beat (12.3.1, the side list) and a guess would be a false block.
    ponytail: mixed results go unchecked; tie sentences to beats by their words if that ever lets one through."""
    done = [b for b in beats if b.degree is not None or (b.gate_words or "").startswith("no roll")]
    if not done or len({_beat_success(b) for b in done}) > 1:
        return None
    return done[0]


def beat_polarity(text: str, b: BeatEntry, pause: Any = None) -> str | None:  # rule: 12.3.1
    """A sentence citing a beat's line, against the beat's degree (P-112): the degree in words when the sentence
    plainly says the opposite, else None. Only plain result phrases count (a sentence is prose, not a claim). A
    success at a cost is a success (01.9.3); a near miss still waiting on its choice (`pause`, the turn's open
    pause) is neither, so a plain result either way contradicts it."""
    if b.degree is None and not (b.gate_words or "").startswith("no roll"):
        return None  # unresolved: the pause or the block says it
    said_fail, said_win = _has(text, _PLAIN_FAIL), _has(text, _PLAIN_WIN)
    if undecided(b, pause):
        return UNDECIDED if said_fail or said_win else None
    ok = _beat_success(b)
    if (ok and said_fail and not said_win) or (not ok and said_win and not said_fail):
        return (b.degree or "no roll").replace("_", " ")
    return None


def _outcome(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 12.3.1
    text = c.text
    b = _beat_for(ctx, text, c.subject)
    if b is None:
        return _v(c, i, "unsourced_change", reason="no resolved beat this turn")
    if undecided(b, ctx.record.pause):
        return _v(c, i, "contradicted", UNDECIDED, reason="the near-miss choice is still open (01.9.3)")
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
    if _has(text, _REFUSE) and any(c.subject in b.targets and "verb.talk" in (b.approach_words or "")
                                   and b.degree is not None and _beat_success(b) for b in ctx.record.beats):
        # P-120: T-15-5 "yes, as asked"; a refusal row or standing never outranks a resolved Talk (12.2.9 (a))
        return _v(c, i, "contradicted", "the Talk on them succeeded: they answer what was asked",
                  reason="a successful Talk is answered, never refused")
    if not c.asserts_change:  # an ongoing description ("she watches you"), not an act this turn
        if ctx.state.entities[c.subject].exists != "exists" or not ctx.present(c.subject):
            return _v(c, i, "contradicted", "not in this scene")
        return _v(c, i, "supported")
    # a deed this turn: its closed source is a record line (12.2.9). A sentence that cites the subject's response or
    # beat line declares that it narrates that line: its words and manner are the narrator's (12.11.9 step 4), and a
    # deed beyond the line shows as a possession or position change, which still needs a write. The activity line
    # holds a continuing activity (a `position` claim at heart, 12.11.9 step 1; I-128)
    if any(c.subject in getattr(it, "entities", ()) for it in _cited(ctx, c)):
        return _v(c, i, "supported", reason="the cited record line is its source (12.3.1)")
    if ctx.present(c.subject) and any(it.text.startswith("the inciting incident:") for it in _cited(ctx, c)):
        return _v(c, i, "supported", reason="a witness's reaction to the cited incident (12.16.16)")
    if any(a.npc == c.subject and tx.overlap(text, a.activity) for a in ctx.record.activities):
        return _v(c, i, "supported", reason="their activity this scene (12.11.9)")
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
    store = "; ".join(a.action for a in rows) or None
    return _v(c, i, "unsourced_change", store, reason="no source for this act in the adjudication record")


def _sealed(ctx: _Ctx, c: Claim, i: int) -> Verdict:  # rule: 00.6.5
    # A sealed-class claim that matched no sealed item (the leak test ran first): a shown fact, or an invented secret.
    for f in ctx.state.facts.values():
        if f.visibility != "sealed" and (c.subject in (f.subject, UNKNOWN)) and tx.covers(c.value or c.text, _flat(f.value)):
            return _v(c, i, "supported")
    if _talk_answer(ctx, c):
        # P-120: what a successful Talk asked about an ordinary thing and the store lacks is the NPC's answer, settled
        # and written like a look's (12.3.2); a clue toward a sealed fact or an open thread stays cut (12.14.13)
        return _v(c, i, "undetermined", reason="what the PC asked, not yet settled: the Oracle settles it")
    if c.subject == UNKNOWN and not c.asserts_change:  # "more than they seem", about no one: no leak matched above
        return _v(c, i, "supported", reason="atmosphere: names nothing addressable (12.3.1)")
    return _v(c, i, "new_element", fix="cut", reason="a hidden truth the store does not hold")


def _talk_answer(ctx: _Ctx, c: Claim) -> bool:  # rule: 12.14.13
    s = ctx.state
    talks = [b for b in ctx.record.beats if "verb.talk" in (b.approach_words or "") and b.degree is not None
             and _beat_success(b)]
    if not talks:
        return False
    if not (c.subject == UNKNOWN or any(c.subject in b.targets for b in talks)
            or (c.subject in s.entities and s.entities[c.subject].kind in ("object", "item") and ctx.present(c.subject))):
        return False
    said = c.value or c.text
    threads = [str(e.data.get("text") or e.name) for e in s.entities.values() if e.kind == "thread"]
    return not any(tx.covers(said, t, ratio=0.5) for t in threads)


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


# ------------------------------------------------------------------------------------------- precision checks

SEASONS = ("spring", "summer", "autumn", "winter")
_SEASON_FORMS = {"spring": ("spring", "springtime", "vernal"), "summer": ("summer", "summertime", "midsummer"),
                 "autumn": ("autumn", "autumnal"), "winter": ("winter", "wintertime", "midwinter", "wintry")}
_SEASON_OF = {w: s for s, ws in _SEASON_FORMS.items() for w in ws}
_SEASON_RE = re.compile(r"\b(" + "|".join(_SEASON_OF) + r")\b", re.I)
# "spring" the verb or the well, not the season: "spring to your feet", "the spring behind the mill"
_SPRING_VERB = re.compile(r"^\s+(?:to|up|into|back|forward|open|free|from|at|out|clear|aside|away|on|off|upon)\b", re.I)
_SPRING_THING = re.compile(r"\b(?:a|the|its|their|his|her|that|this old)\s+$", re.I)
_SPRING_SEASON_NEXT = re.compile(r"^\s+(?:rain|rains|air|morning|mornings|day|days|sun|wind|winds|thaw|flowers|planting|"
                                 r"quarter|festival|fair|light|green|night|nights|evening|evenings|weather|sowing)\b", re.I)
_CLAUSE_END = re.compile(r"[,;:()—–]|\s-\s")
# "fell in one bad winter", "that summer": a season other than now, said so by its determiner (replay corpus)
_SOME_SEASON = re.compile(r"\b(?:a|an|one|that|some|single)\s+(?:\w+\s+)?$", re.I)
_PRONOUN = {"he": "m", "him": "m", "his": "m", "himself": "m", "she": "f", "her": "f", "hers": "f", "herself": "f"}
_PRONOUN_RE = re.compile(r"\b(" + "|".join(_PRONOUN) + r")\b", re.I)
_PRONOUN_WORDS = {"f": "she/her", "m": "he/him"}
_NOT_PEOPLE = ("loc.", "obj.", "item.", "fac.", "thr.", "clk.", "rum.", "clu.", "world")  # id prefixes
# someone a pronoun could stand for that no stored name covers: the antecedent is then not certain (12.3.1b item 4)
_OTHER_ANTECEDENT = re.compile(
    r"\b(?:man|men|woman|women|boy|boys|girl|girls|lad|lass|child|children|baby|wife|husband|mother|father|son|"
    r"daughter|brother|sister|uncle|aunt|widow|widower|guard|guards|stranger|strangers|someone|somebody|anyone|"
    r"everyone|nobody|fellow|figure|rider|traveller|traveler|priest|priestess|merchant|clerk|servant|soldier|elder|"
    r"lord|lady|king|queen|god|goddess|dog|hound|horse|mare|stallion|pony|cat|ox|goat|bird|raven|crow|beast)\b", re.I)
_QUOTE_RE = re.compile(r"[\"“][^\"”]*[\"”]")


class PrecisionHit(BaseModel):
    """One precision check's hit (12.3.2 "Precision, not class"): logged always, with whether it blocked, so each
    check's precision can be measured (OEQ-12-27)."""

    check: str  # pronoun_certain_subject | season_words | outcome_words
    cls: str  # the claim class the check belongs to (pacing.yaml)
    voice: Literal["narrator", "speech"]
    words: str  # the word that hit
    store_value: str  # the subject's stored pronouns, or the calendar line's season
    subject: str | None = None
    blocks: bool = True  # False when the check's measured precision is below min_precision: logged only

    @property
    def why(self) -> str:
        if self.check == "pronoun_certain_subject":
            return f"{self.words!r} does not fit the person this speaks of, whose pronouns are {self.store_value}"
        if self.check == "outcome_words":
            return f"contradicts the attempt's result ({self.store_value})"
        return f"names the season {self.words!r}, but it is {self.store_value} now"


def _precision_cfg(rules: Any) -> tuple[float, dict[str, Any]]:
    pc = ((rules.pacing.get("claim_check") or {}).get("precision_checks") or {}) if rules is not None else {}
    checks = {str(c.get("id")): c for c in pc.get("checks") or []} if pc else {
        "pronoun_certain_subject": {"class": "identity", "voices": ["narrator"]},
        "season_words": {"class": "location_time", "voices": ["narrator", "speech"],
                         "time_shift_words": ["last", "next", "ago", "coming", "since", "until", "before", "after",
                                              "every", "each", "past", "previous"]}}
    return float(pc.get("min_precision") or 0.95), checks


def _clause(text: str, at: int, end: int) -> str:
    """The clause around `text[at:end]`: between the nearest clause marks (a comma, semicolon, dash, bracket)."""
    starts = [m.end() for m in _CLAUSE_END.finditer(text, 0, at)]
    stop = _CLAUSE_END.search(text, end)
    return text[starts[-1] if starts else 0: stop.start() if stop else len(text)]


def _season_hits(text: str, season: str, shift: Sequence[str]) -> list[str]:  # rule: 12.3.2
    out = []
    for m in _SEASON_RE.finditer(text):
        w = m.group(1)
        named = _SEASON_OF[w.lower()]
        if named == season:
            continue
        before = text[:m.start()].rstrip(" \"“”'‘’(")
        if w[0].isupper() and before and before[-1] not in ".!?:;":
            continue  # a capitalised season word mid-sentence is a name ("Winter's Rest")
        after = text[m.end():]
        if named == "spring" and (_SPRING_VERB.match(after) or (
                _SPRING_THING.search(text[:m.start()]) and not _SPRING_SEASON_NEXT.match(after))):
            continue
        clause = _clause(text, m.start(), m.end()).lower()
        if any(re.search(rf"\b{re.escape(s)}\b", clause) for s in shift) or _SOME_SEASON.search(text[:m.start()]):
            continue
        out.append(w)
    return out


def _pronoun_hit(text: str, before: Sequence[str], idx: Any, about: Iterable[str]) -> tuple[str, str] | None:
    # rule: 12.3.2
    # rule: 12.3.1b
    """(the pronoun, the person) when `text` (the narrator's words) uses a he/she pronoun whose antecedent is
    certain (12.3.1b item 4: the only person named before it in this sentence or in the one before, or the one
    person the sentence is declared about) and none of its pronouns fits that person's stored ones. No verdict when
    anyone else could be meant: two candidates, an unnamed man or woman (or animal) in either sentence, a pronoun
    in the sentence before that fits someone else, or another person named in this draft whose pronouns fit
    (or are not stored). `before`: the narrator's words of the sentences before, oldest first."""
    from engine.audit.declare import name_spans

    found = list(_PRONOUN_RE.finditer(text))
    if not found:
        return None
    prev = before[-1] if before else ""

    def named(t: str, upto: int | None = None) -> set[str]:  # the PC too when named ("a blow on Rosett as she …")
        return {eid for a, _, eid in name_spans(t, idx) if (upto is None or a < upto) and not eid.startswith(_NOT_PEOPLE)}

    people = {a for a in about if not a.startswith(_NOT_PEOPLE) and a != idx.pc} | named(prev) | named(
        text, found[0].start())  # an antecedent comes before its pronoun
    for t in (prev, text):
        rest = t
        for a, b, _ in reversed(name_spans(t, idx)):  # a stored name's own words ("the merchant") are that person
            rest = rest[:a] + " " + rest[b:]
        if _OTHER_ANTECEDENT.search(rest):
            return None
    if len(people) != 1:
        return None
    who = next(iter(people))
    g = idx.pronouns.get(who)
    used = {_PRONOUN[p.group(1).lower()] for p in found}
    if g not in _PRONOUN_WORDS or g in used:
        return None
    if any(_PRONOUN[p.lower()] != g for p in _PRONOUN_RE.findall(prev)):
        return None  # the sentence before already speaks of someone else unnamed ("Her glance ... the scribe")
    others = set().union(*(named(t) for t in [*before, text])) - {who}
    if any(idx.pronouns.get(o) in used or idx.pronouns.get(o) is None for o in others):
        return None  # "Ghazra ... Liso stands silent. Her hand stays raised": the earlier woman is meant
    return found[0].group(1), who


def precision_checks(text: str, *, idx: Any, before: Sequence[str] = (), speech: Sequence[str] = (),
                     about: Iterable[str] = (), season: str | None = None, rules: Any = None,
                     beat: BeatEntry | None = None, pause: Any = None) -> list[PrecisionHit]:  # rule: 12.3.2
    # rule: 12.3.1b
    # rule: OEQ-12-27
    """12.3.2's precision checks on one sentence, by code: `text` is its narrator's words, `speech` its speech spans,
    `before` the narrator's words of the draft's sentences before it (oldest first), `about` its declared ids, `idx`
    a `declare.SceneIndex` (names, stored pronouns), `season` the calendar line's (`SEASONS`), `beat` the turn's
    beat the passage's plain result words answer to (`passage_beat`; spec 019). Each check runs in the voices its data
    lists (`claim_check.precision_checks.checks`); a check whose measured `precision` is below `min_precision` still
    hits but does not block (logged only, OEQ-12-27)."""
    min_p, checks = _precision_cfg(rules)
    out: list[PrecisionHit] = []

    def hit(cid: str, voice: Literal["narrator", "speech"], words: str, value: str, subject: str | None = None) -> None:
        c = checks[cid]
        measured = c.get("precision")
        out.append(PrecisionHit(check=cid, cls=str(c.get("class") or ""), voice=voice, words=words, store_value=value,
                                subject=subject, blocks=measured is None or float(measured) >= min_p))

    pron = checks.get("pronoun_certain_subject")
    if pron is not None and "narrator" in (pron.get("voices") or ["narrator"]):
        h = _pronoun_hit(_QUOTE_RE.sub(" ", text), [_QUOTE_RE.sub(" ", b) for b in before], idx, about)
        if h is not None:
            hit("pronoun_certain_subject", "narrator", h[0], _PRONOUN_WORDS[idx.pronouns[h[1]]], h[1])
    sw = checks.get("season_words")
    if sw is not None and season is not None and season in SEASONS:
        voices_on = sw.get("voices") or ["narrator", "speech"]
        shift = [str(x) for x in sw.get("time_shift_words") or []]
        for voice, words in [*((("narrator", text),) if "narrator" in voices_on else ()),
                             *((("speech", sp) for sp in speech) if "speech" in voices_on else ())]:
            for w in _season_hits(words, season, shift):
                hit("season_words", "speech" if voice == "speech" else "narrator", w, season)
    if checks.get("outcome_words") is not None and beat is not None:
        degree = beat_polarity(_QUOTE_RE.sub(" ", text), beat, pause)
        if degree:
            hit("outcome_words", "narrator", degree, degree)
    return out


def calendar_season(state: Any) -> str:  # rule: 12.16.15
    """The calendar line's season word (`SEASONS`), from the store's clock."""
    s = int(getattr(state.time.now, "season", 1) or 1)
    return SEASONS[(s - 1) % 4]
