"""The default NPC layer (12.11.9; DL-12-43, DL-12-93): code decides what each present NPC is doing and how an
addressed or concerned one responds; the narrator voices it.

    ensure_activities(ctx, record)          # step 1: activities rolled once per scene (optional material)
    respond(ctx, record, beats, skip=foes)  # steps 2-5: the practice, each addressed or concerned NPC's response

An addressed NPC's response is an `NpcActionEntry` (a must-name record line with a handle, engine/dm/handles.py);
a concerned bystander's is tagged `optional` (12.14.12). For speech the response is willingness only (PR-12-10
step 2): the narrator chooses the words. Draws go through the game's RNG, so a seeded replay reproduces
them. Wants and refusals are matched to the event by closed tags (social.yaml#event_tags; DL-12-87, I-176); the
World role is only the fallback, when no tag matches and the NPC's motives point to opposite rows. A crowd's
response that changes something is a scene fact `crowd_response` on the place, with a record line.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from engine.audit import text as tx
from engine.dm.adjudication import AdjudicationRecord, NpcActionEntry
from engine.dm.context import TurnContext

ACTIVITY = "activity"  # the detail slot (00.6.6a): the NPC's activity, a scene slot cleared at scene end
SPOKEN = "npc.spoken"  # meta {scene, npcs}: who the PC has spoken with this scene (greeting vs conversation)
NPC_TABLE = "tbl.npc_action"
WATCHES = ("morning", "afternoon", "evening", "night")
REFUSING_ROWS = (1, 2, 3, 5)  # escalates, ends the exchange, hinders, carries on: what was asked is not given
_FIGHT_VERBS = ("verb.strike", "verb.grapple", "verb.force")
_TRADE = re.compile(r"\b(buy|buys|sell|sells|price|prices|cost|costs|coin|coins|pay|pays|trade|trades|wares|goods|"
                    r"haggle|bargain|silver|gold|copper|deal)\b", re.I)
# a creature, not a person: no activity from the people's tables, never addressed (12.11.9 is for people).
# ponytail: a word list; a creature-kind field on mentioned entities would replace it
ANIMAL = re.compile(r"^(?:[\w'-]+\s+){0,2}?(?:dogs?|hounds?|curs?|pupp(?:y|ies)|cats?|kittens?|horses?|ponies|pony|"
                    r"mules?|donkeys?|goats?|sheep|cows?|oxen|ox|pigs?|hens?|chickens?|geese|goose|ducks?|birds?|"
                    r"crows?|ravens?|rats?|mice|mouse|wolf|wolves|hawks?|falcons?|owls?)"
                    r"(?:$|[,;]|\s+(?:at|of|with|in|on|by|from|that|who|always)\b)", re.I)  # the head noun only


def is_animal(state: Any, eid: str) -> bool:  # rule: 12.11.9
    """A creature rather than a person: marked `mind: animal` (adversaries.yaml's field), or named or described
    only by an animal word ("the dog at Nero's heel")."""
    e = state.entities.get(eid)
    if e is None:
        return False
    if e.data.get("mind") == "animal":
        return True
    labels = [str(x) for x in (e.data.get("role"), *(e.data.get("aliases") or [])) if x]
    return any(ANIMAL.match(re.sub(r"^(?:the|a|an)\s+", "", x.strip(), flags=re.I)) for x in labels)


# ------------------------------------------------------------------------------------------- step 1: activity


def current_activity(state: Any, npc: str) -> str | None:  # rule: 12.11.9
    """The NPC's activity this scene, or None (the `activity` detail; cleared at scene end, 12.4.8 step 8)."""
    from engine.store.details import current

    f = current(state, npc, ACTIVITY) if state.scene is not None else None
    return str(f.value) if f is not None and f.value else None


def role_key(rules: Any, role: Any) -> str:  # rule: 12.11.9
    """`tbl.npc_activity.by_role`'s key for a role: the role itself or its first word, else the first word of the
    `tbl.npc_role` row that shares a content word with it ("smith" → crafter), else `other`; never another role's
    cell (DL-12-93: "of" once matched "servant of a great house", so guild officers beat rugs in the hall)."""
    from engine.audit.text import content

    cells = rules.table("tbl.npc_activity")["by_role"]
    words = re.findall(r"[a-z]+", str(role or "").lower())
    if not words:
        return "other"
    if " ".join(words) in cells:
        return " ".join(words)
    if words[0] in cells:
        return words[0]
    have = content(" ".join(words))
    for row in rules.table("tbl.npc_role")["results"]:
        row_words = re.findall(r"[a-z]+", str(row["result"]).lower())
        if row_words and row_words[0] in cells and have & content(" ".join(row_words)):
            return row_words[0]
    return "other"


ROLLED = "npc.activity_rolled"  # meta {scene, npcs}: whose activity was rolled this scene (rolled once, DL-12-93)


def rolled_this_scene(state: Any) -> list[str]:
    v = state.meta.get(ROLLED) or {}
    return list(v.get("npcs") or []) if state.scene is not None and v.get("scene") == state.scene.scene_id else []


def ensure_activities(ctx: TurnContext, record: AdjudicationRecord) -> None:  # rule: 12.11.9
    """Step 1: each present NPC whose activity has not been rolled this scene gets one on `tbl.npc_activity` (their
    own role's cell, else `other`, × watch, d6 pairs), written as its `activity` detail (a scene slot, 00.6.6a);
    never re-rolled that scene, so an activity ended by engagement stays ended. Then the record's scene-state lines
    are rebuilt for whoever is present now (T-12-18): optional material (12.14.12), never a must-name line."""
    from engine.dm.roles.world import present_npcs
    from engine.dm.scene_state import lines
    from engine.store.details import write_detail
    from engine.world.common import meta
    from engine.world.social import npc_field

    tx_ = ctx.need_tx()
    st = tx_.state
    if st.scene is None:
        record.activities = []
        return
    start = len(tx_.events)
    cells = ctx.rules.table("tbl.npc_activity")["by_role"]
    present = present_npcs(st)
    done = rolled_this_scene(st)
    new = [n for n in present if n not in done and not is_animal(st, n)]  # people's tables, people only
    for npc in new:
        if current_activity(tx_.state, npc) is None:
            key = role_key(ctx.rules, npc_field(st, npc, "role"))
            options = list(cells[key][WATCHES[st.time.now.watch % 4]])
            roll = ctx.rng.draw(6, f"activity of {npc} (12.11.9)", stream="npc", table_id="tbl.npc_activity")
            act = str(options[min((roll - 1) // 2, len(options) - 1)])
            tx_.add_all(write_detail(tx_.state, tx_.mint, npc, ACTIVITY, act, source="generation", because="12.11.9",
                                     rules=ctx.rules, visibility="shown").events)
    if new:
        tx_.add(meta(ROLLED, {"scene": st.scene.scene_id, "npcs": [*done, *new]}, "12.11.9"))
    record.add_writes(tx_.events[start:])
    record.activities = lines(tx_.state, record.pc, present)


def end_activity(ctx: TurnContext, record: AdjudicationRecord, npc: str) -> None:  # rule: 12.11.9
    """Step 1: an activity ends when the NPC engages (talks with or fights the PC, or responds with a deed); the slot
    is cleared, so it is no longer scene state and never a lever (01.6.8). A response that writes a new activity
    (T-12-18) supersedes it afterwards."""
    from engine.store.details import write_detail

    tx_ = ctx.need_tx()
    if current_activity(tx_.state, npc) is None:
        return
    res = write_detail(tx_.state, tx_.mint, npc, ACTIVITY, None, source="ruling", because="12.11.9",
                       rules=ctx.rules, visibility="shown")
    tx_.add_all(res.events)
    record.add_writes(res.events)
    record.activities = [a for a in record.activities if not (a.npc == npc and a.slot == ACTIVITY)]


def said_words(ctx: TurnContext) -> str:
    """The player's message this turn, verbatim (T1 stores it before anything else, 12.2.5)."""
    tr = ctx.store.turn(ctx.turn_id) if ctx.turn_id else None
    return str(getattr(tr, "input_verbatim", "") or "")


# ------------------------------------------------------------------------------------------- step 2: practice


def _names(state: Any, npc: str) -> list[str]:
    from engine.store.views import unnamed_label

    e = state.entities[npc]
    out = [e.name, unnamed_label(e), *(a for a in e.data.get("aliases") or [] if isinstance(a, str))]
    if e.name and len(e.name.split()) > 1:
        out.append(e.name.split()[0])
    role = re.findall(r"[a-z]+", str(e.data.get("role") or "").split(" or ")[0].split(" of ")[0].lower())
    if role:
        # "the attendant" for a shrine attendant, "the head" for the head of a guild (never the guild's name).
        # ponytail: the head noun of the role
        out.append(f"the {role[-1]}")
    return [n for n in out if n and len(n) > 2]


def _spans(text: str, phrase: str) -> list[tuple[int, int]]:
    """Where `phrase` stands in `text` as whole words (engine.audit.text.has_phrase's match)."""
    ws = [re.escape(w) for w in tx.words(phrase)]
    if not ws:
        return []
    pat = r"\b" + r"\W+".join(w + r"(?:s|es|ed|ing|d)?" for w in ws) + r"\b"
    return [m.span() for m in re.finditer(pat, text, re.IGNORECASE)]


# words that turn the PC's words to someone: "ask the neighbour", "turn to Nero", "walk over to the officer"
_ADDRESS = re.compile(r"\b(?:ask|asks|asking|tell|tells|say to|says to|question|questions|greet|greets|address|"
                      r"addresses|call to|calls to|(?:turn|turns|walk|walks|step|steps|go|goes|come|comes|head|heads|"
                      r"lean|leans|cross|crosses)(?:\s+(?:back|over|up|across))?\s+to(?:ward)?)\s+$", re.I)


def named_in(state: Any, text: str, present: Sequence[str]) -> list[str]:  # rule: 12.11.9
    """The present NPCs `text` names, the one it addresses first (a name right after "ask", "turn to", ...), then
    by first mention. A name inside a longer name of someone else here does not count ("Collegium" in "the officer
    of the Swanley Collegium" is not the Collegium's head)."""
    hits = [(s, e, n) for n in present if not is_animal(state, n) for name in _names(state, n)
            for s, e in _spans(text, name)]
    hits = [h for h in hits if not any(o[2] != h[2] and o[0] <= h[0] and h[1] <= o[1] and (o[1] - o[0]) > (h[1] - h[0])
                                       for o in hits)]
    first: dict[str, tuple[int, int]] = {}
    for s, _, n in hits:
        k = (0 if _ADDRESS.search(text[:s]) else 1, s)
        first[n] = min(first.get(n, k), k)
    return sorted(first, key=lambda n: first[n])


def addressed(state: Any, record: AdjudicationRecord, present: Sequence[str], message: str = "") -> list[str]:
    # rule: 12.11.9
    """NPCs the PC addressed this turn: a talk beat on them; else the one the player's words turn to (`named_in`'s
    first: a name right after "ask", "turn to", ..., else the first named; the message as typed first, then the
    parts); else the one last spoken with or the only NPC here when the PC speaks to no one by name ("talk with no
    target speaks to the only NPC", P-056). Naming someone else ("Ysrion's gone cold on me") does not address them:
    they are at most concerned (`concerns_self`, 12.11.9 step 3; DL-12-93)."""
    out = [t for b in record.beats if (b.verb == "verb.talk" or "talk" in (b.approach_words or ""))
           for t in b.targets if t in present]
    spoken = [p.text for p in record.parts if p.cls in ("SPEECH", "FICTION_QUESTION", "DECLARATION")]
    for t in [message, *spoken] if not out else []:
        out += named_in(state, t, present)[:1]
        if out:
            break
    present = [n for n in present if not is_animal(state, n)]
    if not out and present and any(p.cls == "SPEECH" for p in record.parts):
        # spoken to no one by name: the one last spoken with this scene, else the first present (cast order).
        # ponytail: nearness and who would answer are not modelled
        last = [n for n in spoken_with(state) if n in present]
        out.append(last[-1] if last else present[0])
    return list(dict.fromkeys(out))


def spoken_with(state: Any) -> list[str]:
    v = state.meta.get(SPOKEN) or {}
    sc = state.scene
    return list(v.get("npcs") or []) if sc is not None and v.get("scene") == sc.scene_id else []


def practice_for(state: Any, record: AdjudicationRecord, npc: str | None, addressed_ids: Sequence[str]) -> str:
    # rule: 12.11.9
    """The first `tbl.npc_practice` row (select_order) whose test holds this turn; greeting and conversation are
    per NPC (no exchange with them yet this scene, or one already)."""
    from engine.resolve.pipeline import _mode

    if _mode(state) == "conflict" or any(b.verb in _FIGHT_VERBS and any(
            t in state.entities and state.entities[t].kind in ("npc", "companion", "adversary") for t in b.targets)
            for b in record.beats):
        return "fight"
    talk = " ".join([p.text for p in record.parts if p.cls in ("SPEECH", "DECLARATION", "FICTION_QUESTION")]
                    + [b.restatement for b in record.beats if b.verb == "verb.talk"])
    if npc in addressed_ids and _TRADE.search(talk):
        return "trade"
    if npc in addressed_ids:
        return "conversation" if npc in spoken_with(state) else "greeting"
    public = any(n.startswith(("a lead", "the inciting incident")) for n in record.notes)
    if public and not addressed_ids:
        return "crowd"
    return "work"


def clamp_row(row: int, allowed: Sequence[int], hostile: bool) -> int:  # rule: 12.11.9
    """A rolled `tbl.npc_action` row the practice does not allow moves to the nearest row it does, toward row 5 on
    a tie; row 1 is legal in every practice for an NPC at Hostile standing."""
    rows: list[int] = sorted({*allowed, *([1] if hostile else [])})
    if row in rows:
        return row
    return min(rows, key=lambda r: (abs(r - row), abs(r - 5)))


# ------------------------------------------------------------------------------------------- steps 3-5: response


def _event_words(record: AdjudicationRecord) -> str:
    return " ".join([p.text for p in record.parts] + [b.restatement for b in record.beats])


# ------------------------------------------------------------------------------------------- step 3(b): tags

_PEOPLE = ("npc", "companion", "adversary", "pc")
_HARM_VERBS = ("verb.strike", "verb.grapple")
_TOPIC_TAGS = {  # social.yaml#event_tags: concerns_* by the topic's words. ponytail: a word list per tag
    "concerns_trade": re.compile(r"\b(prices?|goods|wares|craft|trade|buy|sell|cost)\b", re.I),
    "concerns_travel": re.compile(r"\b(roads?|travell?\w*|arriv\w*|water|river|ferry|boats?|crossing)\b", re.I),
    "concerns_faith": re.compile(r"\b(faith|gods?|temple|shrine|pray\w*|priest\w*)\b", re.I),
    "concerns_healing": re.compile(r"\b(sick\w*|heal\w*|cure|fever|wound\w*|plague|ill(ness)?)\b", re.I),
    "concerns_standing": re.compile(r"\b(reputation|title|good name|standing|honou?r)\b", re.I),
}


def _tag_data(rules: Any) -> dict[str, Any]:
    return dict(rules.social.get("event_tags") or {})


def event_tags(state: Any, record: AdjudicationRecord, beats: Sequence[Any], npc: str,
               practice: str = "") -> set[str]:  # rule: 12.11.9
    # rule: 12.2.9
    """The event's closed tags as they bear on `npc` (social.yaml#event_tags; DL-12-87, I-176), from each beat's
    verb, facets, target and pressure mark, the Framer's `asks` tag on a Talk request, the request's terms, and the
    topic words. ponytail: `names_object`, `asks_truce`/`asks_surrender` and recorded wrongdoing are not derived
    yet (no want-object entity, no parley beat, no crime record): those tags never fire."""
    from engine.world.social import npc_field

    tags: set[str] = set()
    ties = [str(t) for t in npc_field(state, npc, "ties") or []]
    kin = [t for t in ties if not t.startswith("fac.")]
    masters = [t for t in ties if t.startswith("fac.")] + [str(m) for m in npc_field(state, npc, "member_of") or []]
    for o in beats:
        e = o.entry
        fr = state.frames[o.frame_id].frame if o.frame_id and o.frame_id in state.frames else {}
        b = fr.get("beat") or {}
        verb = e.verb or b.get("verb")
        target = next(iter(e.targets), None)
        held_by = None
        if target in state.entities:
            held_by = state.entities[target].data.get("holder") or state.fact_value(target, "holder")
        harms = bool(b.get("against_will")) or verb in _HARM_VERBS
        if harms and (target == npc or held_by == npc):
            tags.add("harms")
        if harms and target in state.entities and state.entities[target].kind in ("npc", "companion"):
            tags.add("harms_innocent")  # ponytail: no record of wrongdoing or arms is read yet
        if target in kin:
            tags.add("concerns_kin")
            if harms or b.get("pressure") == "threat":
                tags.add("against_kin")
        if target in masters:
            tags.add("concerns_master")
        if verb in ("verb.help", "verb.setup") and target == npc:
            tags.add("offers_help")
        if verb == "verb.talk" and target == npc:
            pressure = str(b.get("pressure") or "none")
            asks = str(fr.get("asks") or "none")
            if pressure == "threat":
                tags.add("threatens")
            if asks != "none":
                tags.add(asks)
            if pressure != "none" or asks != "none":
                tags.add("pc_request")
            terms = f"{b.get('method') or ''} {b.get('intent') or ''} {e.restatement}"
            if pressure == "offer" and _TRADE.search(terms):
                tags.add("offers_payment")
    if "offers_payment" in tags and tags & {"asks_breach", "asks_lawbreak"}:
        tags.add("offers_bribe")
    topics = " ".join(p.topic or "" for p in record.parts) + " " + _event_words(record)
    tags |= {t for t, rx in _TOPIC_TAGS.items() if rx.search(topics)}
    if practice == "trade":
        tags.add("concerns_trade")
    name = state.entities[npc].name.lower() if npc in state.entities else ""
    if any(p.question_kind == "what_happened" and name and name in (p.topic or p.text).lower() for p in record.parts):
        tags.add("concerns_past")
    targets = {t for o in beats for t in o.entry.targets}
    held = {t for t in targets if t in state.entities and (state.entities[t].data.get("holder")
                                                           or state.fact_value(t, "holder")) == npc}
    if npc in targets or held or (npc in state.entities and named_in(state, _event_words(record), [npc])):
        tags.add("concerns_self")  # [revision: R2-H] the beat or the words name the NPC or what they hold
    return tags


# event tags that bear on the NPC by construction (computed against them); the topic-word tags and harms_innocent
# bear on a bystander only through a refusal or want of theirs (12.11.9 step 3)
_RELATIVE = frozenset({"harms", "against_kin", "threatens", "offers_payment", "offers_bribe", "offers_help",
                       "pc_request", "concerns_kin", "concerns_master", "concerns_past", "concerns_secret",
                       "names_object", "concerns_self"})


def concerned(state: Any, rules: Any, record: AdjudicationRecord, beats: Sequence[Any], npc: str) -> set[str]:
    # rule: 12.11.9
    """12.11.9 step 3: the event's tags in `social.yaml#event_tags.concerns` that bear on `npc` (computed against
    them, or matching one of their recorded refusals or wants). Empty: the NPC does nothing new and says nothing."""
    ev = event_tags(state, record, beats, npc) & set(_tag_data(rules).get("concerns") or [])
    mine = set().union(*motive_tags(state, rules, npc).values()) if motive_tags(state, rules, npc) else set()
    return {t for t in ev if t in _RELATIVE or t in mine}


def motive_tags(state: Any, rules: Any, npc: str) -> dict[str, set[str]]:  # rule: 12.11.9
    """Each recorded refusal (by kind) and want (by its object, the end of its text) with its tags, keyed like
    `npc_motives` ("<npc>/want.1"). A motive with no listed kind or object has none (it never matches)."""
    et = _tag_data(rules)
    out: dict[str, set[str]] = {}
    e = state.entities.get(npc)
    if e is None:
        return out
    for key, kind in (("wants", "want"), ("refusals", "refusal")):
        v = state.fact_value(npc, key)
        for i, item in enumerate(v if isinstance(v, list) else (e.data.get(key) or [])):
            d = item if isinstance(item, dict) else {"text": str(item)}
            if kind == "refusal":
                tags = set((et.get("refusals") or {}).get(str(d.get("kind") or ""), []))
            else:
                text = str(d.get("text") or d.get("want") or "").lower().strip()
                obj = max((k for k in (et.get("wants") or {}) if text.endswith(str(k).lower())), key=len, default=None)
                tags = set((et.get("wants") or {}).get(obj, [])) if obj else set()
            out[f"{npc}/{kind}.{i + 1}"] = tags
    return out


def want_row(rules: Any, matched: set[str], *, request: bool, hostile: bool) -> int:  # rule: 12.11.9
    """A matched want's `tbl.npc_action` row before the practice clamp: served 9 (a request) or 8, defeated 2
    (1 at Hostile), engaged 6."""
    et = _tag_data(rules)
    if matched & set(et.get("serves") or []):
        return 9 if request else 8
    if matched & set(et.get("defeats") or []):
        return 1 if hostile else 2
    return 6


def candidates(state: Any, npc: str, record: AdjudicationRecord) -> dict[str, str]:  # rule: 12.2.9
    """The NPC's recorded wants and refusals, best word overlap with the event first (the World fallback's
    candidates, and its order when `world_judge` is off). ponytail: content-word overlap."""
    from engine.dm.roles.world import npc_motives

    said = tx.content(_event_words(record))
    motives = npc_motives(state, npc)
    return dict(sorted(motives.items(), key=lambda kv: -len(tx.content(kv[1]) & said)))


def _voice(ctx: TurnContext, npc: str) -> str:  # rule: 12.11.9
    """The NPC's voice register and habit; a walk-on's are rolled on first answer (12.11.1's tables)."""
    from engine.world.common import fact
    from engine.world.social import npc_field

    v = npc_field(ctx.state, npc, "voice")
    if not isinstance(v, dict) or not v.get("register"):
        tbl = ctx.rules.table
        reg = tbl("tbl.npc_voice_register")["results"]
        hab = tbl("tbl.npc_voice_habit")["results"]
        r = ctx.rng.draw(len(reg), f"voice register of {npc} (12.11.9)", stream="npc", table_id="tbl.npc_voice_register")
        h = ctx.rng.draw(len(hab), f"voice habit of {npc} (12.11.9)", stream="npc", table_id="tbl.npc_voice_habit")
        v = {"register": str(reg[r - 1]["result"]), "habit": str(hab[h - 1]["result"])}
        tx_ = ctx.need_tx()
        tx_.add(fact(tx_, npc, "voice", v, rule_id="12.11.9", visibility="background"))
    return f"{v.get('register')}, {v.get('habit')}"


REACH_YES = {"limited": "grants a lesser version of what you ask", "standard": "agrees to what you ask",
             "great": "agrees to what you ask, and more", "exceptional": "agrees to what you ask, and more"}


_OFFER = re.compile(r"\b(?:offer\w*|giv(?:e|es|ing)|hand(?:s|ing)?\s+(?:over|you|them|him|her)|pay(?:s|ing)?)\b", re.I)


def talk_outcome(e: Any, offered: bool = False) -> str:  # rule: T-15-5
    """A successful Talk's act: the question answered (its PR-12-10 lines are the record's), else T-15-5's yes by the
    delivered reach (a certain beat, no roll, is a yes as asked). Something offered with it (a pie, a coin: the
    beat's pressure `offer`) is taken."""
    act = "answers what you asked" if e.learned else REACH_YES.get(e.reach or "standard", REACH_YES["standard"])
    return f"takes what you offer and {act}" if offered else act


def voiced_refusal(ctx: TurnContext, npc: str, reason: str) -> str:  # rule: 12.11.9
    """Step 4: a refusal spoken in the NPC's own voice: the reason said through their register and habit."""
    return f"refuses, in their own voice ({_voice(ctx, npc)}): {reason}"


def _judge_motive(ctx: TurnContext, npc: str, cands: dict[str, str], happened: str) -> tuple[str | None, list[str]]:
    """The World fallback (12.11.9 step 3(b)): (want/refusal id engaged or None, tags), the World role over the
    candidates only; with `world_judge` off, the best overlap."""
    if (ctx.config or {}).get("world_judge", True):
        from engine.dm.roles.world import npc_responses

        for r in npc_responses(ctx, happened, only={npc: list(cands)}):
            if r.npc == npc:
                return r.refusal_engaged or r.want_engaged, r.tags
        return None, []
    said = tx.content(happened)
    return next((k for k, v in cands.items() if tx.content(v) & said), None), []


def _speech_only(record: AdjudicationRecord, beats: Sequence[Any], npc: str) -> bool:
    """The PC only spoke to `npc` this turn (plain speech or a question): no beat other than a Talk acts on them."""
    return not any(npc in b.entry.targets and "talk" not in (b.entry.approach_words or "") for b in beats)


def respond(ctx: TurnContext, record: AdjudicationRecord, beats: Sequence[Any], *, skip: Sequence[str] = (),
            oof: list[dict[str, str]] | None = None) -> None:
    # rule: 12.11.9
    # rule: 12.2.9
    """Steps 2-5 for the NPCs who respond this turn (step 3): those the PC addressed or acted on, and those the
    event concerns (`concerned`); every other present NPC does nothing new and says nothing. Sources, first that
    applies: (a) a resolved Talk frame's outcome; (b) a recorded refusal or want whose tags match the event (a want
    served takes row 9 for a request, else 8; defeated 2, 1 at Hostile; engaged 6; then the practice clamp), the
    World role only when no tag matches and the motives point to opposite rows; (c) `tbl.npc_action` by standing,
    clamped to the practice's rows. For plain speech or a question to an addressed NPC the source gives willingness
    only (PR-12-10 step 2): no talk wording is a record line; an NPC already answered this turn (PR-12-10) adds no
    row. A refusing source to an addressed NPC is voiced. A concerned bystander's response is a deed tagged
    `optional` (12.14.12: optional material). Engaging ends the NPC's activity (step 1). With nobody responding and
    the crowd practice, the crowd's response (`crowd_response`)."""
    from engine.dm import answer as ans
    from engine.dm.roles.world import npc_motives, present_npcs
    from engine.dm.scene_state import response_values, write
    from engine.dm.world_step import RESOLVED, _foe_turn, answer_line, happened_text
    from engine.resolve.tables import roll_table
    from engine.world.common import meta
    from engine.world.social import first_interaction, standing

    if not beats and not any(p.cls in ("SPEECH", "DECLARATION", "FICTION_QUESTION") for p in record.parts):
        return
    tx_ = ctx.need_tx()
    st = ctx.state
    present = present_npcs(st)
    spoke_to = addressed(st, record, present, said_words(ctx))
    talks = {t: b for b in beats if b.status in RESOLVED and "talk" in (b.entry.approach_words or "")
             for t in (b.entry.targets or (present if len(present) == 1 else spoke_to[:1]))}
    unresolved = {t for b in beats if b.status not in RESOLVED for t in b.entry.targets}
    targets = [t for b in beats if b.status in RESOLVED for t in b.entry.targets if t in present]

    def person(n: str) -> bool:
        return n in st.entities and st.entities[n].kind in ("npc", "companion", "adversary") \
            and not (st.entities[n].kind == "npc" and is_animal(st, n))  # a beast foe still answers by its row

    engaged = [n for n in dict.fromkeys([*talks, *spoke_to, *targets]) if person(n)]
    bystanders = [n for n in present if n not in engaged and n not in skip and person(n)
                  and concerned(st, ctx.rules, record, beats, n)]
    answered = {a.npc for a in record.npc_actions if a.source_ref == "PR-12-10"}
    practice_rows = {r["range"]: r for r in ctx.rules.table("tbl.npc_practice")["results"]}
    # the PC asked for something (a question, a request, a Talk): a refusing source is then said as a refusal
    asked = any(b.verb == "verb.talk" for b in record.beats) or any(
        p.cls == "FICTION_QUESTION" or (p.cls == "SPEECH" and "?" in p.text) for p in record.parts)
    for npc in [*engaged, *bystanders]:
        if npc in skip or (npc in unresolved and npc not in talks):
            continue
        n_acts = len(record.npc_actions)
        wrow: int | None = None  # a tag-matched want's row (12.11.9 step 3(b))
        is_addressed = npc in spoke_to or npc in talks
        optional = npc in bystanders
        practice = practice_for(ctx.state, record, npc, spoke_to)
        if npc in answered:
            pass  # PR-12-10 answered them this turn: that line is their response
        elif npc in talks:  # (a) a resolved Talk frame's delivered outcome (a certain talk, no roll, is a yes)
            b = talks[npc]
            degree = b.entry.degree or "success"
            fr = st.frames[b.frame_id].frame if b.frame_id and b.frame_id in st.frames else {}
            offered = (fr.get("beat") or {}).get("pressure") == "offer" or bool(_OFFER.search(b.entry.restatement))
            action = talk_outcome(b.entry, offered)
            if degree in ("failure", "critical_failure"):
                action = voiced_refusal(ctx, npc, f"the talk did not move them ({degree.replace('_', ' ')})")
            record.npc_actions.append(NpcActionEntry(npc=npc, action=action, source="talk_outcome",
                                                     source_ref=b.frame_id, tags=[practice]))
        elif is_addressed and _speech_only(record, beats, npc):
            # plain speech or a question: willingness only, the words are the narrator's (PR-12-10 step 2)
            band, why = ans.willingness(ctx, npc, record, beats)
            said = ans.WILL_WORDS[band].format(why=why)
            if not asked:  # plain speech asks nothing: they reply (12.11.9 step 4), within the same willingness
                said = said.replace("answers what you asked", "replies").replace("refuses to answer what you asked",
                                                                                 "turns you away")
            answer_line(record, npc, ans.Answer(said, said, willingness=band))
        else:
            row_def = practice_rows[practice]
            allowed = [int(x) for x in row_def["action_rows"]]
            ev = event_tags(ctx.state, record, beats, npc, practice)
            mtags = motive_tags(ctx.state, ctx.rules, npc)
            matched = {m: t & ev for m, t in mtags.items() if t & ev}
            sv = standing(ctx.state, npc)
            hostile = sv is not None and int(sv) <= -3
            motive = next((m for m in matched if "/refusal." in m), None) or next(iter(matched), None)
            tags = sorted(matched.get(motive or "", set()))
            if motive is not None and "/want." in motive:
                wrow = clamp_row(want_row(ctx.rules, matched[motive], request="pc_request" in ev or asked,
                                          hostile=hostile), allowed, hostile)
            if motive is None and {m.split("/")[1].split(".")[0] for m in mtags} == {"want", "refusal"}:
                # no tag matches and the motives point to opposite rows: the World fallback (12.11.9 step 3(b))
                cands = candidates(ctx.state, npc, record)
                motive, tags = _judge_motive(ctx, npc, cands, happened_text(record))
                tags = [*tags, "world_fallback"]
            motives = npc_motives(ctx.state, npc)
            extra = ["optional"] if optional else []
            if motive is not None and "/refusal." in motive:  # (b) a recorded refusal outranks everything else
                act = voiced_refusal(ctx, npc, motives[motive]) if is_addressed else f"bristles: {motives[motive]}"
                record.npc_actions.append(NpcActionEntry(npc=npc, action=act, source="refusal", source_ref=motive,
                                                         tags=[practice, *tags, *extra]))
            elif motive is not None:
                gist = str((row_def.get("responses") or {}).get(str(wrow)) or "") if wrow is not None else ""
                action = f"acts on a want: {motives[motive]}" + (f"; {gist}" if gist else "")
                if wrow is not None and is_addressed and asked and wrow in REFUSING_ROWS:
                    action = voiced_refusal(ctx, npc, gist or motives[motive])
                record.npc_actions.append(NpcActionEntry(npc=npc, action=action, source="want", source_ref=motive,
                                                         tags=[practice, *tags, *([f"row:{wrow}"] if wrow else []),
                                                               *extra]))
            else:  # (c) the action table by standing, clamped to the practice (12.11.5)
                value = standing(ctx.state, npc)
                if value is None:  # PR-12-5 step 3: the first interaction's reaction roll
                    value = first_interaction(ctx.time_ctx(), npc)
                value = int(value or 0)
                res = roll_table(NPC_TABLE, {"standing_modifier": value}, rules=ctx.rules, state=ctx.state,
                                 rng=ctx.rng, purpose=f"npc action {npc} (12.11.5)")
                tx_.add_all(res.events)
                row = clamp_row(int(res.roll or 5), allowed, value <= -3)
                if row == 1 and value <= -3 and record.pc:  # rule: 06.2.1
                    from engine.resolve.conflict import start

                    start(ctx.time_ctx(), record.pc, [npc], "a hostile NPC attacks (06.2.1)")
                    _foe_turn(ctx, record, npc, oof)
                    continue
                gist = str((row_def.get("responses") or {}).get(str(row)) or res.entry)
                refuses = is_addressed and asked and row in REFUSING_ROWS  # what was asked is not given
                action = voiced_refusal(ctx, npc, gist) if refuses else gist
                record.npc_actions.append(NpcActionEntry(npc=npc, action=action, source="table_row",
                                                         source_ref=f"{NPC_TABLE}:{row}", tags=[practice, *extra]))
        end_activity(ctx, record, npc)  # step 1: engaging ends the activity; a response may write a new one
        for a in record.npc_actions[n_acts:]:  # T-12-18: the response sets their activity and manner
            src, ref = a.source, a.source_ref or "12.11.9"
            row = int(ref.rsplit(":", 1)[1]) if src == "table_row" else wrow if src == "want" else None
            degree = talks[npc].entry.degree if src == "talk_outcome" and npc in talks else None
            write(ctx, record, npc, response_values(ctx.rules, "table_row" if row is not None else src,
                                                    practice=practice, row=row, degree=degree), because=ref)
        if is_addressed and npc not in spoken_with(ctx.state):
            sc = ctx.state.scene
            if sc is not None:
                tx_.add(meta(SPOKEN, {"scene": sc.scene_id, "npcs": [*spoken_with(ctx.state), npc]}, "12.11.9"))
    if not engaged and not bystanders and any(b.status in RESOLVED for b in beats) \
            and practice_for(ctx.state, record, None, spoke_to) == "crowd":
        crowd_response(ctx, record, [int(x) for x in practice_rows["crowd"]["action_rows"]])


CROWD = "crowd_response"  # the scene fact on the place (12.11.9 step 1)


def crowd_response(ctx: TurnContext, record: AdjudicationRecord, allowed: Sequence[int]) -> None:  # rule: 12.11.9
    """12.11.9 step 1: an unnamed crowd's collective reaction is atmosphere unless it changes something the PC could
    act on; then it is the crowd practice's row (`tbl.npc_action` at standing 0, clamped), written as a scene fact
    `crowd_response` on the scene's place, with a record line. The crowd is never a person and has no profile."""
    from engine import ids
    from engine.dm.scene_state import response_values
    from engine.resolve.tables import roll_table
    from engine.store.events import Event

    tx_ = ctx.need_tx()
    sc = tx_.state.scene
    if sc is None or not sc.place_id:
        return
    res = roll_table(NPC_TABLE, {"standing_modifier": 0}, rules=ctx.rules, state=tx_.state, rng=ctx.rng,
                     purpose="the crowd's response (12.11.9)")
    tx_.add_all(res.events)
    row = clamp_row(int(res.roll or 5), allowed, False)
    act = response_values(ctx.rules, "table_row", practice="crowd", row=row).get("activity")
    if not act:
        return  # heads turn, talk stops: atmosphere (12.3.1)
    place = sc.place_id
    ev = Event.of("fact_set", {"source": "ruling"}, source=f"{NPC_TABLE}:{row}", rule_id="12.11.9",
                  fact_id=tx_.mint(ids.FACT), subject=place, predicate=CROWD, value=act, visibility="shown",
                  persistence="scene", supersedes=tx_.state.current_fact_id(place, CROWD))
    tx_.add(ev)
    record.add_writes([ev])
    record.npc_actions.append(NpcActionEntry(npc=place, action=f"the crowd: {act}", source="table_row",
                                             source_ref=f"{NPC_TABLE}:{row}", tags=["crowd"]))


__all__ = ["ACTIVITY", "ANIMAL", "CROWD", "ROLLED", "addressed", "candidates", "clamp_row", "concerned",
           "crowd_response", "current_activity", "end_activity", "ensure_activities", "event_tags", "is_animal",
           "motive_tags", "named_in", "practice_for", "respond", "role_key", "rolled_this_scene", "said_words",
           "voiced_refusal", "want_row"]
