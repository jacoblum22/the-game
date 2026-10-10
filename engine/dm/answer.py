"""Answering a question (PR-12-10, 12.10.8; spec 013): consequential answers by the case, willingness by code, the
words by the narrator from the speaker card and the NPC's own testimony.

    a = ask(ctx, npc, "where_is", topic, "where does the north road go?", pc=pc, record=rec, beats=outcomes)
    a.willingness   # "willing" | "guarded" | "unwilling" for an ordinary question (the narrator voices it)
    a.line          # the record line the narration must name
    a.fact_id       # the fact told on the consequential route or by casting
    who = who_answer(ctx, "who is missing")      # the DM-side "who is X?" (a FICTION_QUESTION): (words, fact id)

    answers = ask_message(ctx, npc, parts, reach, pc=pc, record=rec, beats=outcomes)   # one message, P9 (spec 029)

Route (PR-12-10 step 1), per **message** [P9; DL-15-45]: their own name or a person asked about by name (typed);
then **one** clue judgment over all the remaining questions (`clue_judgment`, one small model call; D2 A) -> the case
graph (a holder delivers its placement as a learned fact and the node is found; anyone else names the holder of the
node's core placement); then "who is <role>" (a story role -> the case graph, building the reduced case when none is
behind it; any other role -> casting); everything else is the NPC's to answer in words: code gives only the
willingness (step 2), decided when the talk starts and held for the scene (D3 A), an unwilling answer with one pointer
onward. `deliver_count` (T-15-5) caps these ordinary answers only, after the judgment, so a clue is never dropped by
the cap. R2-D's rungs (the store, the knowledge pack, propose-and-ratify, the pointer) are retired as sources of
speech (DL-12-90).
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

from engine import ids
from engine.audit import text as words
from engine.dm.adjudication import effective_degree
from engine.dm.testimony import INDEX
from engine.gen._seed_packs import pack_data
from engine.gen.case import case_covering, case_for_question, cases, mark_found, pointer, story_option
from engine.gen.cast import cast, home_of, settlement_of
from engine.store.events import WORLD
from engine.world.common import active_pc, fact, meta
from engine.world.social import learn_name, record_knowledge

NPC_TABLE = "tbl.npc_action"
# "who is X?" with X one of these (stems) is a story role: the case graph answers it (PR-12-10 step 1)
STORY_ROLES = words.content("missing enemy rival challenger stranger thief culprit killer messenger refugee arrival "
                            "behind responsible traitor taken kidnapper attacker")
_WHO = re.compile(r"\bwho(?:'s|’s|\s+(is|was|are|were|took|has|had|did|sent|would|might|could))?\s+([^?!.;,\"”]+)",
                  re.IGNORECASE)
# asked of the one answering ("who she is"); never "they" ("who are they?" got the knower's own name, I2 §3)
_SELF = re.compile(r"^(?:you|he|she|your(?: own)? name)\b", re.IGNORECASE)
_OWN_NAME = re.compile(r"\b(?:your|his|her|their)(?: own)? name\b", re.IGNORECASE)  # never "the name of X" (P-113)
PEOPLE = ("npc", "companion", "adversary")
# the willingness line's words (PR-12-10 step 2); the narrator chooses the NPC's words within it (step 4)
# (the question itself is the record's part line; never quoted here, so no words read as the PC's, 12.14.3)
WILL_WORDS = {
    "willing": "answers what you asked, willingly ({why}): in their own words, from what they know or have heard",
    "guarded": "answers what you asked, guardedly ({why}): a part of it, short, in their own words",
    "unwilling": "refuses to answer what you asked ({why}): a refusal in their own voice, never a stock formula",
}


def will_words(st: Any, npc: str, band: str, why: str) -> str:  # rule: PR-12-10
    """The willingness line in the NPC's own pronouns ("in his own words"; DL-12-114: round 7's sellsword, he/him,
    drifted to "they" beside "in their own words")."""
    from engine.dm.packet import own_words, pronoun_words

    return own_words(WILL_WORDS[band].format(why=why), pronoun_words(st, npc))


@dataclass
class Answer:
    said: str  # the knower's act in words, after their name ("tells you: ...", "answers ... willingly")
    line: str  # the record line (BeatEntry.learned or the NPC's act)
    fact_id: str | None = None
    pointer: str | None = None  # the holder a non-holder named on the consequential route
    willingness: str | None = None  # an ordinary question's willingness (PR-12-10 step 2); None: a fact answer
    key: str | None = None  # the asked-and-answered index key `<npc>|<kind>|<topic>`
    learned: str = ""  # a clue or pointer as the fact the PC learns, naming no speaker (DL-15-44)
    part: int | None = None  # the index of the question part this answers (the message's parts)


def deliver_count(n: int, reach: int) -> int:  # rule: T-01-6
    """DL-01-12: of N items, Limited max(1, N // 3); Standard ceil(N / 2); Great N (ponytail: no Exceptional bonus)."""
    if n <= 0 or reach <= 0:
        return 0
    return {1: max(1, n // 3), 2: -(-n // 2)}.get(reach, n)


def name(st: Any, eid: str | None) -> str:
    """The entity as the narration may call it (`name_of`), with an article for a description."""
    from engine.dm.roles.narrator import name_of

    if not eid:
        return "someone"
    n = name_of(st, eid)
    return f"the {n}" if n[:1].islower() and not n.startswith(("the ", "a ", "an ", "your ")) else n


def _cap(s: str) -> str:
    return s[:1].upper() + s[1:]


def _key(knower: str, kind: str, topic: str) -> str:
    return f"{knower}|{kind}|{topic}"


def _tell(ctx: Any, pc: str, fid: str | None, how: str = "told") -> None:
    st = ctx.need_tx().state
    if fid and fid in st.facts and fid not in st.knowledge.get(pc, {}):
        record_knowledge(ctx.time_ctx(), pc, fid, how)


def _write(ctx: Any, subject: str, predicate: str, value: Any, *, rule: str, source: str = "ruling") -> str:
    """The current fact (subject, predicate) when it already holds `value`, else a new one."""
    tx = ctx.need_tx()
    cur = tx.state.current_fact_id(subject, predicate)
    if cur is not None and tx.state.facts[cur].value == value:
        return cur
    ev = fact(tx, subject, predicate, value, rule_id=rule, source=source, visibility="shown")
    tx.add(ev)
    return str(ev.payload.fact_id)  # type: ignore[attr-defined]


# ------------------------------------------------------------------------------------------- topics


def topic_of(st: Any, topic: str | None, text: str, knower: str | None = None) -> tuple[str, str | None]:
    # rule: 12.2.2
    """(topic key, entity asked about). The Reader's topic is an entity id or a closed topic key; an entity resolves
    by `common_knowledge.entity_topics`; a null topic is read from the question's words (names first, then the
    topic keys and gists), else `local_news`."""
    ck = pack_data().CK
    if topic in ck["topics"]:
        return str(topic), None
    about = topic if topic in st.entities and topic != knower else None
    if about is None:
        from engine.retrieve.scene import resolve_names

        have = words.content(text)  # a name word, never a stop word ("who" in "Brugra Who Came Back")
        about = next((i for i in resolve_names(st, text) if i not in (knower, active_pc(st))
                      and have & words.content(st.entities[i].name)), None)
    if about is not None:
        e = st.entities[about]
        haven = (st.meta.get("world.region") or {}).get("haven")
        if e.kind == "place":
            kind = "place_in_settlement" if settlement_of(st, about) == haven else "place_beyond"
        elif e.kind == "object":
            kind = "document" if e.data.get("document") else "item"
        else:
            kind = {"faction": "faction", "adversary": "creature"}.get(e.kind, "npc")
        return str((ck["entity_topics"].get(kind) or ["folk"])[0]), about
    have = words.content(text)
    best, score = "local_news", 0
    for k, t in ck["topics"].items():
        s = len(have & words.content(f"{k.replace('_', ' ')} {t['gist']}"))
        if s > score:
            best, score = str(k), s
    return best, None


# ------------------------------------------------------------------------------------------- the case graph


def open_node(case: dict[str, Any], who: bool) -> dict[str, Any]:
    """The node a question reaches: "who is <role>" asks node 1; anything else the first unfound necessary node
    whose predecessors are found (15.9.5's prerequisites), else the last one."""
    nodes = [n for n in case["nodes"] if n["necessary"]]
    if who:
        return nodes[0]
    for i, n in enumerate(nodes):
        if not n.get("found"):
            return n if all(m.get("found") for m in nodes[:i]) else nodes[i - 1]
    return nodes[-1]


def deliver_node(ctx: Any, case: dict[str, Any], node: dict[str, Any], placement: str | None, pc: str,
                 how: str = "told") -> str:  # rule: 15.9.5
    """A placement's content reaches the PC: the node's fact (a person subject's `who_is_*` fact names them, so the
    name is learned, 12.10.2), the PC's knowledge record, and the node found (`mark_found`)."""
    st = ctx.need_tx().state
    sub = case["solution"]["subject"]
    if node is case["nodes"][0] and sub["id"] in st.entities:
        role = node["fact"].split(":", 1)[0]
        fid = _write(ctx, WORLD, ("who_is_" + ids.slug(role))[:58], sub["id"], rule="PR-15-6", source="generation")
    else:
        fid = _write(ctx, WORLD, f"case.{ids.slug(node['id'])}"[:60], node["fact"], rule="PR-15-6",
                     source="generation")
    _tell(ctx, pc, fid, how)
    mark_found(ctx.need_tx(), case["id"], node["id"], placement, fact_id=fid)
    return fid


def _from_case(ctx: Any, knower: str, case: dict[str, Any], who: bool, pc: str, first: bool) -> Answer | None:
    # rule: PR-12-10
    """The consequential route: a holder of a live placement on the node delivers it; anyone else says so and names
    the holder of the node's core placement (the one that cannot fail), else of a live one. None when the node is
    already found (an NPC never re-delivers it: 232941 t5, I1 §5a) or the case names no one to send the PC to (the
    knower then answers in words, within their willingness)."""
    st = ctx.need_tx().state
    node = open_node(case, who)
    if node.get("found") and knower != pc:
        return None  # a found clue is never delivered or pointed at again: the NPC speaks of it in words (DL-12-103)
    held = next((p for p in node["placements"] if p["holder"] == knower and p.get("status") != "lost"), None)
    if held is not None or (node.get("found") and node.get("fact_id") in st.knowledge.get(pc, {})):
        fid = deliver_node(ctx, case, node, held["id"] if held else None, pc)
        said = f"{'remember' if first else 'tells you'} {node['fact']}"
        return Answer(said, "", fid, learned=str(node["fact"]))
    ref = pointer(case, node["id"], asked=knower, state=st)
    pred = f"points_to.{ids.slug(node['id'])}"[:60]
    if ref is None or (knower != pc and any(  # the PC already has this lead: the knower answers in words
            f in st.facts and st.facts[f].predicate == pred and st.facts[f].subject != knower
            for f in st.knowledge.get(pc, {}))):
        return None
    if ref not in st.entities:  # a trace left at a place: the place
        p = next(p for p in node["placements"] if p["holder"] == ref)
        ref = p.get("at") or ref
    elif st.entities[ref].kind != "place" and st.entities[ref].kind not in PEOPLE:  # a document or thing
        ref = home_of(st, ref) or ref
    if ref in st.entities and st.entities[ref].kind in PEOPLE:
        learn_name(ctx.time_ctx(), pc, ref, "told")
    fid = _write(ctx, knower, f"points_to.{ids.slug(node['id'])}"[:60], ref, rule="PR-12-10")
    _tell(ctx, pc, fid)
    what = node["fact"].split(":", 1)[0]
    dont = "do not know" if first else "does not know"
    where = name(st, ref) if ref in st.entities and st.entities[ref].kind in PEOPLE else f"someone at {name(st, ref)}"
    return Answer(f"{dont} {what}, but {where} would", "", fid, ref,
                  learned=f"{_cap(name(st, knower))} {dont} {what}, but {where} would")


def clue_judgment(ctx: Any, knower: str, texts: Sequence[str], abouts: Sequence[str | None] = ()
                  ) -> tuple[dict[str, Any] | None, int | None]:
    # rule: PR-12-10
    # rule: 15.9.5
    """The case a **message** is about (PR-12-10 step 1, D2 A; DL-12-112; P9, DL-15-45) and the question that asks it:
    the case whose subject any question asks about by id (typed, no call), else **one** small model call
    (`Role.CLUE`) over all the questions together and the about lines of each case's open node, the ones `knower`
    holds a live placement on marked and listed first. (None, None): not about a clue (the questions are ordinary).
    Retires `case_about`'s word overlap (round 7: 0 clues in 38 questions; "signed" matched "a sign of the rite") and
    the per-part call (round 8: the cap dropped Betric's clue before the second question was judged)."""
    from engine.dm.roles.clue import MAX_ITEMS, judge
    from engine.gen.case import about_line

    st = ctx.need_tx().state
    pc = active_pc(st)
    open_: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any] | None]] = []
    for c in cases(st).values():
        for i, about in enumerate(abouts):
            if about is not None and about == c["solution"]["subject"]["id"]:
                return c, i
        node = open_node(c, False)
        if node.get("found") and knower != pc:
            continue  # a found clue is never delivered or pointed at again (DL-12-103)
        held = next((p for p in node["placements"] if p["holder"] == knower and p.get("status") not in ("lost", "found")),
                    None)
        open_.append((c, node, held))
    open_.sort(key=lambda x: x[2] is None)  # held first
    open_ = open_[:MAX_ITEMS]
    pick, part = judge(ctx, list(texts), [(about_line(st, c, n, p), p is not None) for c, n, p in open_])
    return (open_[pick][0], part) if pick is not None else (None, None)


def clue_case(ctx: Any, knower: str, text: str, about: str | None = None) -> dict[str, Any] | None:
    # rule: PR-12-10
    """`clue_judgment` over one question: the case it is about, else None."""
    return clue_judgment(ctx, knower, [text], [about])[0]


def fact_words(st: Any, f: Any) -> str:
    who = name(st, f.subject) if f.subject in st.entities else ""
    value = {True: "yes", False: "no"}.get(f.value, f.value) if isinstance(f.value, bool) else f.value
    return f"{who} {f.predicate.replace('_', ' ').replace('.', ' ')} {value}"


def _sentence(st: Any, f: Any) -> str:
    from engine.audit.fallback import fact_sentence

    if f.predicate.startswith("topic.") and isinstance(f.value, str):
        return f.value
    return fact_sentence(st, f).rstrip(".")


# ------------------------------------------------------------------------------------------- willingness


HELD = "answers.willingness"  # meta {"scene": scene id, "npcs": {npc: {"band", "why"}}} (PR-12-10 step 2)


def held(st: Any, npc: str) -> dict[str, str] | None:
    """The band held for `npc` in the current scene, else None (a new scene decides afresh)."""
    m = st.meta.get(HELD) or {}
    sc = st.scene.scene_id if st.scene is not None else None
    return (m.get("npcs") or {}).get(npc) if m.get("scene") == sc else None


def _hold(ctx: Any, npc: str, band: str, why: str) -> tuple[str, str]:
    st = ctx.need_tx().state
    sc = st.scene.scene_id if st.scene is not None else None
    m = st.meta.get(HELD) or {}
    npcs = dict(m.get("npcs") or {}) if m.get("scene") == sc else {}
    if npcs.get(npc) != {"band": band, "why": why}:
        npcs[npc] = {"band": band, "why": why}
        ctx.need_tx().add(meta(HELD, {"scene": sc, "npcs": npcs}, "PR-12-10"))
    return band, why


def _standing_moved(ctx: Any, npc: str) -> bool:
    """An insult, a threat or a harm this turn: the NPC's standing toward the PC was stepped (15.1.5)."""
    return any(e.type == "relationship_set" and getattr(e.payload, "a", None) == npc
               and getattr(e.payload, "kind", None) == "standing" and getattr(e.payload, "steps", None)
               for e in getattr(ctx.need_tx(), "events", ()))


def willingness(ctx: Any, npc: str, record: Any = None, beats: Sequence[Any] = ()) -> tuple[str, str]:
    # rule: PR-12-10
    # rule: 12.11.9
    """PR-12-10 step 2, first that applies: a recorded refusal whose tags match the event -> `unwilling` for that
    topic only (the refusal its reason; nothing held); a resolved Talk on the NPC this turn -> its outcome by the
    effective degree (a won persuasion, an accepted payment or a threat that worked holds `willing` for the scene; a
    failed one refuses this ask only); else the band **held for the scene** (DL-12-118) unless the NPC's standing
    moved this turn; else decided now and held: 15.3.10's certainty test (a Neutral or warmer listener) -> `willing`,
    else `tbl.npc_action` by standing read only as a band (`answer_ladder.willingness_by_row`). Returns (band,
    reason in words). Retires per-topic re-rolls (round 7: unwilling at turn 10, fully willing at turn 11)."""
    from engine.dm.npc_layer import event_tags, motive_tags
    from engine.dm.roles.world import npc_motives
    from engine.resolve.tables import roll_table
    from engine.world.social import _RUNGS, first_interaction, standing

    st = ctx.state
    if record is not None and npc in st.entities:
        ev = event_tags(st, record, beats, npc)
        for m, tags in motive_tags(st, ctx.rules, npc).items():
            if "/refusal." in m and tags & ev:
                return "unwilling", str(npc_motives(st, npc).get(m) or "a refusal of theirs")
    talk = next((b for b in beats if b.status in ("resolved", "no_roll") and npc in (b.entry.targets or [])
                 and (b.entry.verb == "verb.talk" or "talk" in (b.entry.approach_words or ""))), None)
    if talk is not None:
        if effective_degree(talk.entry) in ("failure", "critical_failure"):  # DL-01-48
            return "unwilling", "the talk did not move them"
        return _hold(ctx, npc, "willing", "the talk moved them")
    have = held(st, npc)
    if have and not _standing_moved(ctx, npc):
        return str(have["band"]), str(have["why"])
    sv = standing(st, npc)
    if sv is None:
        sv = first_interaction(ctx.time_ctx(), npc)
    sv = int(sv or 0)
    rung = {v: k for k, v in _RUNGS.items()}.get(sv, "neutral")
    if sv >= 0:
        return _hold(ctx, npc, "willing", f"a plain question to a {rung} listener")
    res = roll_table(NPC_TABLE, {"standing_modifier": sv}, rules=ctx.rules, state=st, rng=ctx.rng,
                     purpose=f"willingness of {npc} (PR-12-10)")
    ctx.need_tx().add_all(res.events)
    band = str(ctx.rules.pacing["answer_ladder"]["willingness_by_row"].get(str(res.roll), "guarded"))
    return _hold(ctx, npc, band, f"{rung} toward you")


def refused_on(st: Any, topic: str) -> set[str]:
    """Everyone who refused the PC on `topic` (the asked-and-answered index: an `unwilling` answer filed under it)."""
    idx = st.meta.get(INDEX) or {}
    return {k.split("|", 1)[0] for k, v in idx.items() if k.rsplit("|", 1)[-1] == topic
            and (v or {}).get("willingness") == "unwilling"}


def refusal_pointer(ctx: Any, knower: str, topic: str, about: str | None) -> str | None:  # rule: PR-12-10
    """A refusal points onward (DL-12-119): someone new who would know the topic (a cast person whose role or pack
    knows it, in the settlement where it is asked), never the one asked or anyone who already refused the PC on it.
    None: no one (the stuck answer, 12.8.5; nothing written)."""
    from engine.gen.cast import cast

    st = ctx.need_tx().state
    pc = active_pc(st)
    skip = refused_on(st, about or topic) | {knower, *([about] if about else [])}
    here = home_of(st, pc) if pc in st.entities else None
    return cast(st, None, scope=here, topic=topic, asker=knower, exclude=skip)


# ------------------------------------------------------------------------------------------- asking


def ask(ctx: Any, knower: str, kind: str, topic: str | None, text: str, *, pc: str, record: Any = None,
        beats: Sequence[Any] = ()) -> Answer:  # rule: PR-12-10
    """One question put to `knower` (an NPC): a one-part message (`ask_message`)."""
    part = SimpleNamespace(question_kind=kind, topic=topic, text=text)
    return ask_message(ctx, knower, [part], 2, pc=pc, record=record, beats=beats)[0]


def ask_message(ctx: Any, knower: str, parts: Sequence[Any], reach: int, *, pc: str, record: Any = None,
                beats: Sequence[Any] = ()) -> list[Answer]:  # rule: PR-12-10
    # rule: T-15-5
    """The questions of **one message** put to `knower` (P9; DL-15-45; DL-15-39 as amended). `parts` carry
    `question_kind`, `topic` and `text`; `reach` is the delivered reach (T-01-6).
    1. A part that asks for the knower's own name, or a named person's, is answered at once (typed; no call).
    2. **One** clue judgment reads every other part together (`clue_judgment`) *before* any cap: a clue it finds is
       delivered as a fact (`Answer.learned`, no speaker), or the knower points to its holder; the part that asked it
       is done. A clue is never dropped by the cap.
    3. A "who is <role>" part still left goes to the case graph or to casting (typed; a fact too).
    4. `deliver_count` caps the ordinary parts that remain (the willingness line the narrator voices; the index
       remembers it, so asking twice draws nothing).
    Facts first, in the order of the parts, then the ordinary answers. Each answer carries its `part`."""
    st = ctx.need_tx().state
    info: dict[int, tuple[str, str, str | None, str]] = {}  # part -> (kind, key, about, topic key)
    for i, p in enumerate(parts):
        kind = "who_knows" if p.question_kind == "who_is" and re.search(
            r"\b(?:would|might|could)\s+know\b", p.text, re.IGNORECASE) else p.question_kind
        key_topic, about = topic_of(st, p.topic, p.text, knower)
        info[i] = (kind, _key(knower, kind, about or key_topic), about, key_topic)
    k_name = _cap(name(st, knower))
    facts: list[Answer] = []
    left: list[int] = []
    for i, p in enumerate(parts):
        kind, key, about, _ = info[i]
        a = _who_identity(ctx, knower, p.text, about, pc, p.topic) if (
            kind == "who_is" or about == knower or _OWN_NAME.search(p.text)) else None
        if a is not None:
            facts.append(_fact(a, i, key, f"{k_name} {a.said}"))
        else:
            left.append(i)
    clue_part: int | None = None
    if left:
        case, hit = clue_judgment(ctx, knower, [parts[i].text for i in left], [info[i][2] for i in left])
        if case is not None:
            a = _from_case(ctx, knower, case, False, pc, False)
            if a is not None:
                clue_part = left[hit] if hit is not None else (left[0] if len(left) == 1 else None)
                facts.append(_fact(a, clue_part, info[clue_part][1] if clue_part is not None else None,
                                   a.learned or f"{k_name} {a.said}"))
    ordinary: list[int] = []
    for i in left:
        if i == clue_part:
            continue
        kind, key, about, _ = info[i]
        a = _who_role(ctx, knower, parts[i].text, pc) if kind == "who_is" else None
        if a is not None and a.said:
            facts.append(_fact(a, i, key, f"{k_name} {a.said}"))
        else:
            ordinary.append(i)
    facts.sort(key=lambda a: -1 if a.part is None else a.part)
    out = list(facts)
    for i in ordinary[:deliver_count(len(ordinary), reach)]:  # the cap counts ordinary answers only
        kind, key, about, key_topic = info[i]
        out.append(_ordinary(ctx, knower, key, about, key_topic, i, pc=pc, record=record, beats=beats))
    return out


def _fact(a: Answer, part: int | None, key: str | None, line: str) -> Answer:
    a.part, a.key, a.line = part, key, line
    return a


def _ordinary(ctx: Any, knower: str, key: str, about: str | None, key_topic: str, part: int, *, pc: str,
              record: Any, beats: Sequence[Any]) -> Answer:  # rule: PR-12-10
    """An ordinary question: the willingness line the narrator voices (held for the scene, DL-12-118), and one
    pointer onward when the answer is a refusal (DL-12-119)."""
    st = ctx.need_tx().state
    k_name = _cap(name(st, knower))
    band, why = willingness(ctx, knower, record, beats)  # held for the scene (DL-12-118): no per-topic re-roll
    idx = dict(st.meta.get(INDEX) or {})
    hit = idx.get(key) or {}
    if hit.get("willingness") != band or hit.get("reason") != why:
        idx[key] = {**hit, "willingness": band, "reason": why, "said": list(hit.get("said") or [])}
        ctx.need_tx().add(meta(INDEX, idx, "PR-12-10"))
    said = will_words(st, knower, band, why)
    ref = refusal_pointer(ctx, knower, key_topic, about) if band == "unwilling" else None
    if ref is not None:  # the one pointer onward (DL-12-119): a person the narrator names, never a loop
        learn_name(ctx.time_ctx(), pc, ref, "told")
        at = home_of(st, ref)  # where to find them, so the pointer leads somewhere (live 025: "where is Yipoo?")
        said += f"; and names one person who would know: {name(st, ref)}" + (
            f", found at {st.entities[at].name}" if at in st.entities else "")
    return Answer(said, f"{k_name} {said}", willingness=band, key=key, pointer=ref, part=part)


def _role_words(text: str) -> str | None:
    m = _WHO.search(text.replace("_", " "))
    return m.group(2).strip(" ?.") if m else None


def _who_verb(text: str) -> str:
    m = _WHO.search(text.replace("_", " "))
    return (m.group(1) or "is").lower() if m else "is"


def _who_identity(ctx: Any, knower: str, text: str, about: str | None, pc: str, given: str | None = None
                  ) -> Answer | None:  # rule: PR-12-10
    """"Who are you?" / "who is Bran?": their own name (12.10.2), or a person asked about by name. Typed; None when the
    question is neither (a story role or another role is `_who_role`'s, after the clue judgment)."""
    st = ctx.need_tx().state
    role = _role_words(text) or ""
    if about == knower or _SELF.match(role) or (not role and _OWN_NAME.search(text)):
        if st.entities[knower].kind not in PEOPLE:
            return None
        learn_name(ctx.time_ctx(), pc, knower, "told")
        return Answer(f"gives their name, in their own words: {st.entities[knower].name}", "",
                      st.current_fact_id(knower, "name"))
    asked = words.content(role)  # "who is Bran?" names them; "who is the old enemy?" does not name Old Power
    named = about is not None and (about == given or bool(asked) and asked <= words.content(st.entities[about].name))
    if about is not None and named and st.entities[about].kind == "npc" and about not in st.seals:
        learn_name(ctx.time_ctx(), pc, about, "told")
        return Answer(f"tells you who that is: {st.entities[about].name}", "", st.current_fact_id(about, "name"))
    return None


def _who_role(ctx: Any, knower: str, text: str, pc: str) -> Answer | None:  # rule: PR-12-10
    """"Who is <role>?": a story role -> the case graph (the reduced case built now when none is behind it); any
    other role -> casting. `Answer("", "")`: nothing found, the NPC answers in words (DL-12-103); None: no role."""
    role = _role_words(text) or ""
    if not words.content(role):
        return None
    found = who_case(ctx, role, pc)
    if found is not None:
        return _from_case(ctx, knower, found, True, pc, False) or Answer("", "")  # "": the ordinary route
    cast_ = cast_who(ctx, role, story=bool(words.content(role) & STORY_ROLES), exclude=(knower,))
    if cast_ is None:
        return Answer("", "")  # no one cast: nothing written; the NPC answers in words (DL-12-103)
    fid, who = cast_
    _tell(ctx, pc, fid)
    return Answer(f"tells you who {_who_verb(text)} {role}: {who}", "", fid)


def who_case(ctx: Any, role: str, pc: str) -> dict[str, Any] | None:  # rule: PR-12-10
    """The case behind a story-role question, built now (PR-15-6's reduced profile, DL-15-38) when none is."""
    st = ctx.need_tx().state
    if not (words.content(role) & STORY_ROLES or story_option(role)):
        return None
    here = home_of(st, pc) if pc in st.entities else None
    return case_covering(st, role) or case_for_question(ctx.need_tx(), role, here)


def cast_who(ctx: Any, role: str, *, story: bool, exclude: Sequence[str] = ()) -> tuple[str, str] | None:
    # rule: 00.11.1
    """"Who is <role>?" (not a story role a case answers): a stored `who_is_*` fact naming a person, else an existing
    person by casting (`social.yaml#cast`), written as a fact. Returns (fact id, their name); None when no one is
    cast: a failed cast writes nothing (PR-12-10 step 1, DL-12-103; retires the "no one you know" fact, I2 §3)."""
    st = ctx.need_tx().state
    pred = ("who_is_" + ids.slug(role))[:57]
    cur = st.current_fact_id(WORLD, pred)
    v = st.facts[cur].value if cur is not None else None
    if not (isinstance(v, str) and v in st.entities):  # nothing stored, or a pre-021 "no one you know": cast again
        pc = active_pc(st)
        here = home_of(st, pc) if pc in st.entities else None
        v = cast(st, role, scope=here, exclude=exclude, gate=not story)
        if v is None:
            return None
        cur = _write(ctx, WORLD, pred, v, rule="00.11.1", source="generation")
    return str(cur), st.entities[str(v)].name


def who_answer(ctx: Any, text: str) -> tuple[str, str] | None:  # rule: PR-12-10
    """A "who is X?" put to the DM (a FICTION_QUESTION, 01.3.8): the PC is the knower. A story role is answered from
    the case only when the PC has been told it, else with who would know (the core holder); any other role by
    casting. None when the text is not a who-question (the caller's Oracle asks it); ("", "") when no one is cast
    (nothing is written or told: the narration answers in words, DL-12-103)."""
    role = _role_words(text)
    if not role or not words.content(role) or _SELF.match(role):
        return None
    st = ctx.need_tx().state
    pc = active_pc(st)
    if pc is None:
        return None
    case = who_case(ctx, role, pc)
    if case is not None:
        a = _from_case(ctx, pc, case, True, pc, True)
        if a is None:
            return "no one has told you", ""
        if a.pointer is None:
            v = st.facts[a.fact_id].value if a.fact_id else None
            return (st.entities[v].name if isinstance(v, str) and v in st.entities else str(v)), str(a.fact_id)
        return f"no one has told you; {name(st, a.pointer)} would know", str(a.fact_id)
    cast_ = cast_who(ctx, role, story=bool(words.content(role) & STORY_ROLES))
    if cast_ is None:
        return "", ""
    fid, who = cast_
    _tell(ctx, pc, fid)
    return who, fid


# the seed's stance reasons that are bookkeeping, in the words the NPC would use (12.16.11's stance)
_WHY = {"holds a placement of the incident's case": "they know something of it and want it settled",
        "of the threat faction": "they would rather you left it alone"}


def _why(stance: dict[str, Any]) -> str:
    return _WHY.get(str(stance["why"]), str(stance["why"]))


def _pack_fact(ctx: Any, knower: str, k: dict[str, Any]) -> str:  # rule: 12.16.11
    """A seeded knowledge-pack item as a fact (`source: data`) the knower knows."""
    st = ctx.need_tx().state
    fid = _write(ctx, k.get("about") or WORLD, f"topic.{k['topic']}.{ids.slug(k['fact'])}"[:60], k["text"],
                 rule="12.16.11", source="data")
    if fid not in st.knowledge.get(knower, {}):
        record_knowledge(ctx.time_ctx(), knower, fid, "recalled")
    return fid


def volunteer(ctx: Any, knower: str, pc: str) -> Answer | None:  # rule: T-15-5
    """Great reach or better: one extra the NPC chooses from their record (a tie or another pack fact the PC has
    not heard, else their stance), told unasked."""
    st = ctx.need_tx().state
    e = st.entities.get(knower)
    if e is None or e.kind not in PEOPLE:
        return None
    for k in sorted((k for k in e.data.get("knowledge") or [] if k.get("text")), key=lambda k: k.get("slot") != "tie"):
        fid = st.current_fact_id(k.get("about") or WORLD, f"topic.{k['topic']}.{ids.slug(k['fact'])}"[:60])
        if fid is None or fid not in st.knowledge.get(pc, {}):
            fid = _pack_fact(ctx, knower, k)
            _tell(ctx, pc, fid)
            said = f"adds, unasked: {_sentence(st, st.facts[fid])}"
            return Answer(said, f"{_cap(name(st, knower))} {said}", fid)
    stance = e.data.get("stance") or {}
    if stance.get("why") and st.current_fact_id(knower, "stance.said") is None:
        fid = _write(ctx, knower, "stance.said", f"{stance.get('stance')}: {stance['why']}", rule="12.11.4",
                     source="data")
        _tell(ctx, pc, fid)
        said = f"lets slip where they stand: {_why(stance)}"
        return Answer(said, f"{_cap(name(st, knower))} {said}", fid)
    return None


__all__ = ["HELD", "INDEX", "STORY_ROLES", "WILL_WORDS", "Answer", "ask", "ask_message", "cast_who", "clue_case",
           "clue_judgment", "deliver_count", "deliver_node", "held", "name", "refusal_pointer", "refused_on", "topic_of",
           "volunteer", "who_answer", "willingness"]
