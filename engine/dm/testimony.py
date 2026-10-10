"""Testimony (12.3.1b, 12.10.8, PR-12-12; spec 013): what a character says is a `said` record on the speaker, fed
back on their speaker card, never a world fact until it matters.

    add_said(ctx, [{"speaker": "npc.nibwen", "words": "...", "about": [...], "question": "npc.nibwen|what_is|folk"}])
    said_by(state, "npc.nibwen", topic="folk")      # recent lines + every one on the topic (`answer_ladder.said_shown`)
    is_repeat(state, rules, "npc.nibwen", words)     # `not_a_repeat`: overlap above `narration.freshness.said_overlap`
    settle_triggered(ctx, reader, record)            # PR-12-12 step 1's triggers: settle once, before framing

Records live in meta `npc.said` {"n": int, "records": [{id, speaker, turn, words, about, question, settled, fact}]}:
`settled` is None (open), True / False (the fact or the speaker's error), or "none" (the words claimed nothing about
the world: a refusal, opinion, want, feeling, intention or question; nothing written). The record is the settled
fact's `said_by` / `said_turn` (PR-12-12 step 4; `said_for`).
The asked-and-answered index (meta `answers.index`, `"<npc>|<kind>|<topic>" -> {willingness, reason, said}`) is the
NPC's memory; it never supplies words.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from engine import ids
from engine.audit import text as words
from engine.world.common import active_pc, fact, meta

SAID = "npc.said"
INDEX = "answers.index"
KEEP = 120  # ponytail: the newest records only; an archive if long games need older testimony
PEOPLE = ("npc", "companion", "adversary")


def records(state: Any) -> list[dict[str, Any]]:
    return list((state.meta.get(SAID) or {}).get("records") or [])


def get(state: Any, said_id: str) -> dict[str, Any] | None:
    return next((r for r in records(state) if r["id"] == said_id), None)


def said_by(state: Any, npc: str, *, topic: str | None = None, about: str | None = None,
            k: int = 6) -> list[dict[str, Any]]:  # rule: PR-12-10
    """PR-12-10 step 3: the speaker's `k` most recent `said` records plus every one on the asked topic (the
    question's topic key, or the entity asked about), oldest first."""
    mine = [r for r in records(state) if r.get("speaker") == npc]
    on = [r for r in mine if (topic and str(r.get("question") or "").endswith(f"|{topic}"))
          or (about and (about in (r.get("about") or []) or str(r.get("question") or "").endswith(f"|{about}")))]
    keep = {r["id"] for r in [*mine[-k:], *on]}
    return [r for r in mine if r["id"] in keep]


def said_by_others(state: Any, npc: str, *, topic: str | None = None, about: str | None = None,
                   k: int = 4) -> list[dict[str, Any]]:  # rule: PR-12-12
    """PR-12-12 step 1's guard (DL-12-109): what *other* speakers said on the same topic (the question's topic key, or
    the entity asked about), the newest `k`, oldest first, so a speaker's improvised details agree or knowingly
    differ (R1 risk 4: a speaker never saw another's lines). Never the PC's own words."""
    def on(r: dict[str, Any]) -> bool:
        q = str(r.get("question") or "")
        return bool((topic and q.endswith(f"|{topic}")) or (about and (about in (r.get("about") or [])
                                                                       or q.endswith(f"|{about}"))))

    pc = active_pc(state)
    return [r for r in records(state) if r.get("speaker") not in (npc, pc, None) and on(r)][-k:]


def overlap(a: str, b: str) -> float:
    """The share of `a`'s content words already in `b` (0 when `a` has fewer than three)."""
    wa, wb = words.content(a), words.content(b)
    return len(wa & wb) / len(wa) if len(wa) >= 3 else 0.0


def is_repeat(state: Any, rules: Any, speaker: str | None, said: str) -> str | None:  # rule: 12.14.11
    # rule: 12.3.1b
    """`not_a_repeat` (`claim_check.speech_checks`): the speaker's own earlier line this one repeats (content-word
    overlap above `narration.freshness.said_overlap`), else None."""
    if not speaker:
        return None
    limit = float((((rules.pacing.get("narration") or {}).get("freshness") or {}).get("said_overlap")) or 0.6)
    return next((r["words"] for r in records(state)
                 if r.get("speaker") == speaker and overlap(said, r["words"]) > limit), None)


def add_said(ctx: Any, entries: Sequence[dict[str, Any]]) -> list[str]:  # rule: PR-12-10
    # rule: 12.3.1b
    """PR-12-10 step 5: each spoken line as a `said` record; the index entry of the question it answers gets its id.
    No world fact is written."""
    if not entries:
        return []
    tx = ctx.need_tx()
    cur = dict(tx.state.meta.get(SAID) or {})
    n, recs = int(cur.get("n") or 0), list(cur.get("records") or [])
    idx = dict(tx.state.meta.get(INDEX) or {})
    out = []
    st, now = tx.state, tx.state.time.now
    place = st.scene.place_id if st.scene is not None else None
    for e in entries:
        n += 1
        sid = f"said.{n}"
        recs.append({"id": sid, "speaker": e.get("speaker"), "turn": e.get("turn") or ctx.turn_id,
                     "words": str(e.get("words") or ""), "about": list(e.get("about") or []),
                     "question": e.get("question"), "settled": None, "fact": None,
                     "place": place, "day": [now.week, now.day, now.watch]})  # where and when (the journal's told)
        q = e.get("question")
        if q and q in idx:
            idx[q] = {**idx[q], "said": [*(idx[q].get("said") or []), sid]}
        out.append(sid)
    tx.add(meta(SAID, {"n": n, "records": recs[-KEEP:]}, "PR-12-10"))
    if idx != (tx.state.meta.get(INDEX) or {}):
        tx.add(meta(INDEX, idx, "PR-12-10"))
    return out


# ------------------------------------------------------------------------------------------- PR-12-12


def _named(state: Any, r: dict[str, Any], eid: str) -> bool:
    e = state.entities.get(eid)
    return bool(e) and (eid in (r.get("about") or []) or bool(
        e.name and re.search(rf"\b{re.escape(e.name.lower())}\b", str(r.get("words") or "").lower())))


def _known_only_from_testimony(state: Any, pc: str, eid: str) -> bool:  # rule: PR-12-12
    """The PC knows `eid` only from what someone said: a person whose name they only heard, or a place no record of
    theirs is about."""
    e = state.entities[eid]
    known = state.knowledge.get(pc, {})
    if e.kind in PEOPLE:
        fid = state.current_fact_id(eid, "name")
        return fid is not None and fid in known and known[fid].how == "heard"
    if e.kind == "place":
        here = state.scene.place_id if state.scene else None
        return eid != here and not any(fid in state.facts and state.facts[fid].subject == eid for fid in known)
    return False


def _premise(assertion: str, r: dict[str, Any]) -> bool:
    """The beat's stated premise restates the said words: most of the shorter one's content words are in the other
    (two at least), so "the guard sleeps at noon, as Dunwen said" cites her line and "I don't believe you" does not."""
    a, w = words.content(assertion), words.content(r.get("words") or "")
    small = min(len(a), len(w))
    return small >= 2 and len(a & w) >= max(2, 0.6 * small)


def triggered(state: Any, beats: Sequence[Any]) -> list[str]:  # rule: PR-12-12
    """PR-12-12 step 1 over the open `said` records, only when the player acts on a specific claim (DL-12-102):
    (a) travel / (c) a target: a beat's target (a person, or a place a Move or travel sets out for) that a record
    names and the PC knows only from testimony; (b) cited in the roll: the beat's stated premise (the Reader's
    `assertion`) restates a record. Hearing, repeating, asking about or arguing with testimony settles nothing.
    Retires the Reader's `rests_on`, which fired on 64% of turns (I2 §1).
    ponytail: (c)'s other frame inputs (a gate, tier or cost taken from a claim) are not derived; no field carries
    them (revisit per DL-12-102)."""
    open_ = [r for r in records(state) if r.get("settled") is None and r.get("speaker")]
    pc = active_pc(state)
    out: list[str] = []
    for b in beats:
        t = str(getattr(b, "target", None) or "")
        if pc is not None and t in state.entities and _known_only_from_testimony(state, pc, t):
            out += [r["id"] for r in open_ if _named(state, r, t)][-1:]  # the latest line that named it
        claim = str(getattr(b, "assertion", None) or "")
        if claim:
            out += [r["id"] for r in open_ if _premise(claim, r)][-1:]
    return list(dict.fromkeys(out))


# 12.14.13's question ("would it help or hinder the PC beyond what any such place ordinarily offers?") as a word
# test on the stated claim. ponytail: a word list; a typed claim kind would replace it
_BEYOND = re.compile(r"\b(secret\w*|hidden|treasure\w*|hoard|weak(?:ness|\s+spot)|cure\w*|passage|tunnel|key|"
                     r"magic\w*|enchant\w*|cursed|haunted|ambush\w*|traitor|spy|smuggl\w*|vault|map)\b", re.I)


def _claim(ctx: Any, r: dict[str, Any]) -> dict[str, str]:  # rule: PR-12-12
    """Step 2: one `[J:enum]` call reads the said words with the speaker, the exchange they were said in and the
    identity lines (name, pronouns, bond) of everyone they name (12.2.4 item 3), and states them as `{kind, subject,
    predicate, value}`; `kind` is `claim`, or why there is none (a refusal, opinion, want, feeling, intention or
    question). It judges nothing else. Names, never ids, so no id lands in a value (I2 §1)."""
    from engine.dm.packet import identity_lines, render_exchange
    from engine.dm.roles.prompts import load_prompt
    from engine.dm.schemas import build_schema, schema_context
    from engine.llm.base import Packet, Role, call_role
    from engine.store.views import display_name

    st = ctx.need_tx().state
    schema = build_schema(Role.TESTIMONY, schema_context(st, ctx.rules))
    speaker = str(r.get("speaker") or "")
    about = [a for a in r.get("about") or [] if a in st.entities and a not in st.seals]
    # rule: 12.2.4
    people = identity_lines(st, [speaker, *about], str(r.get("words") or ""))
    view = ("people (name: pronouns; their tie to the player's character, who is \"you\"):\n" + "\n".join(people)
            ) if people else ""
    turn = ctx.store.turn(r["turn"]) if getattr(ctx, "store", None) is not None and r.get("turn") else None
    who = display_name(st, speaker) if speaker in st.entities and speaker not in st.seals else "someone"
    packet = Packet(instructions=load_prompt("testimony"), core="", cards=[], view=view,
                    exchanges=[render_exchange((turn.input_verbatim, turn.delivered_verbatim))] if turn else [],
                    message=f"{who} said: \"{r['words']}\"")
    default = {"kind": "none", "subject": "", "predicate": "", "value": ""}  # no claim stated: nothing is written
    res = call_role(ctx.model, Role.TESTIMONY, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call,
                    default=default)
    return {k: str(res.data.get(k) or default[k]).strip() for k in default}


# a claim about the speaker's own will is an intention or a refusal, never a world fact (PR-12-12 step 2): "will give
# no word", "won't say", "refuses" (233000 t7: the refusal written as fact.103 and cited as a -2 snag)
_OWN_WILL = re.compile(r"^(?:will|won'?t|would|wouldn'?t|shall|shan'?t|refuses?|wants?|wishes|intends?|means to|"
                       r"is (?:not )?willing|is unwilling|declines?)\b", re.I)


def _subject(st: Any, name: str) -> str:
    """The claim's subject as an id: an id in the store, the PC for "you", else the one entity the name names."""
    from engine.retrieve.scene import resolve_names

    if name in st.entities:
        return name
    if name.lower() in ("you", "yourself", "the player's character"):
        return active_pc(st) or "world"
    hits = [i for i in resolve_names(st, name) if i not in st.seals]
    return hits[0] if len(hits) == 1 else "world"


def said_for(state: Any, fact_id: str) -> dict[str, Any] | None:  # rule: PR-12-12
    """Step 4's `said_by` / `said_turn`: the `said` record a settled fact came from (it holds speaker and turn)."""
    return next((r for r in records(state) if r.get("fact") == fact_id), None)


def _case_route(st: Any, subject: str, text: str) -> bool | None:  # rule: PR-12-12
    """Step 3's consequential tier: the claim touches a case (its subject, or most of a node's words) or a sealed
    fact. True when the case holds it, False when it does not; None when it is not consequential."""
    from engine.dm.answer import fact_words
    from engine.gen.case import cases

    have = words.content(text)
    for c in cases(st).values():
        sub = c["solution"]["subject"]
        nodes = [n for n in c["nodes"] if words.covers(n["fact"].split(":", 1)[-1], text, ratio=0.6)]
        if nodes:
            return True
        if subject == sub["id"] or have & words.content(sub["words"]):
            return False  # about the case's subject, and no node of it says so
    for f in st.facts.values():
        if (f.visibility == "sealed" or f.id in st.seals) and words.covers(fact_words(st, f), text, ratio=0.6):
            return True
    return None


def settle(ctx: Any, said_id: str, record: Any = None) -> str | None:  # rule: PR-12-12
    """Steps 2-4 for one unsettled `said` record: state the claim, route it (the case; the Oracle at Likely beyond
    the ordinary; else accepted), write a fact (`source: testimony | oracle`) or the speaker's error
    (`wrong_about`), and mark the record settled with the fact id. Never delivers a clue. Returns the fact id."""
    from engine.resolve.oracle import OracleQuestion, ask_oracle
    from engine.world.social import record_knowledge

    tx = ctx.need_tx()
    st = tx.state
    r = get(st, said_id)
    if r is None or r.get("settled") is not None:
        return None
    c = _claim(ctx, r)
    subject = _subject(st, c["subject"])
    speaker = r.get("speaker") or "world"
    if c["kind"] != "claim" or not c["predicate"] or (subject == speaker and _OWN_WILL.match(c["predicate"])):
        # step 2: no world claim (a refusal, opinion, want, feeling, intention, question): nothing is written
        _mark(tx, said_id, settled="none", fact=None, route=c["kind"] if c["kind"] != "claim" else "own_will")
        if record is not None:
            record.notes.append(f"testimony settled (none: {c['kind']}): nothing written")
        return None
    text = f"{c['subject'] if subject == 'world' else st.entities[subject].name} {c['predicate']} {c['value']}"
    if _FIGURE.search(f"{c['predicate']} {c['value']}"):
        # a price spoken outside a hook (DL-12-109): the deal's typed price comes from the band (15.7.1), never the
        # words; the figure stays testimony and never reaches the purse
        _mark(tx, said_id, settled="none", fact=None, route="price_band")
        if record is not None:
            record.notes.append(f"testimony settled (price band): {text}: the figure is not written")
        return None
    pred = (ids.slug(c["predicate"]) or "is")[:60]  # the claim's own predicate; the value stays the value (I2 §1)
    route, true = "accepted", True
    case = _case_route(st, subject, text)
    fid: str | None = None
    if case is not None:
        route, true = "case", case
    elif _BEYOND.search(text):
        res = ask_oracle(OracleQuestion(subject=subject, predicate=pred, question=f"Is it true that {text}?",
                                        odds="likely"), state=st, rules=ctx.rules, rng=ctx.rng, mint=tx.mint,
                         store=ctx.store, staged=tx.events)
        tx.add_all(res.events)
        route, true, fid = "oracle", res.answer is True, (res.fact_id if res.answer is True else None)
    if route == "case" and true:
        pass  # the case already holds it: nothing is written or told (a clue comes only by its placement, 15.9)
    elif true and fid is None:
        ev = fact(tx, subject, pred, c["value"], rule_id="PR-12-12", source="testimony", visibility="shown")
        tx.add(ev)
        fid = str(ev.payload.fact_id)  # type: ignore[attr-defined]
        _place_there(tx, subject, c["value"])
    elif not true:
        ev = fact(tx, speaker if speaker in st.entities else "world", "wrong_about", text, rule_id="PR-12-12",
                  source="ruling", visibility="shown")
        tx.add(ev)
        fid = str(ev.payload.fact_id)  # type: ignore[attr-defined]
    pc = active_pc(tx.state)
    if pc and fid and fid in tx.state.facts and fid not in tx.state.knowledge.get(pc, {}):
        record_knowledge(ctx.time_ctx(), pc, fid, "told")
    _mark(tx, said_id, settled=bool(true), fact=fid, route=route)
    if record is not None:
        record.notes.append(f"testimony settled ({route}): {text} -> {'true' if true else 'false'}")
    return fid


# a coin figure in a claim ("ten silver", "5 coins", "a hundred gold"): a price, settled by the band, never the words
_FIGURE = re.compile(r"\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|twenty|fifty|a hundred|hundred)\s+"
                     r"(?:\w+\s+)?(?:coins?|silver|gold|copper|crowns?|marks?)\b", re.I)


def _place_there(tx: Any, subject: str, value: str) -> None:  # rule: PR-12-12
    """A true claim that a person or group is at a known place puts them there (DL-12-109: the refugees "up at the
    healer's house" are present on arrival; round 7 wrote it to `world`, where it changed nothing)."""
    from engine.dm.mentions import find_existing

    st = tx.state
    e = st.entities.get(subject)
    if e is None or e.kind not in PEOPLE:
        return
    m = re.search(r"\b(?:at|in|by|near|inside)\s+(.+)$", value, re.I)
    place = find_existing(st, value.strip(" ."), "place") or (find_existing(st, m.group(1).strip(" ."), "place")
                                                              if m else None)
    if place is not None and (st.positions.get(subject) is None or st.positions[subject].location != place):
        from engine.store.events import Event

        tx.add(Event.of("position_set", source="engine", rule_id="PR-12-12", entity=subject, location=place))


def _mark(tx: Any, said_id: str, **fields: Any) -> None:
    cur = dict(tx.state.meta.get(SAID) or {})
    recs = [dict(x, **fields) if x["id"] == said_id else x for x in cur.get("records") or []]
    tx.add(meta(SAID, {**cur, "records": recs}, "PR-12-12"))


def settle_triggered(ctx: Any, reader: Any, record: Any = None) -> list[str]:  # rule: PR-12-12
    """At T4, before the beats frame: settle every `said` record a trigger names, so a true claim is citable from
    this beat on (the words were said before the declaration, 01.6.8). Returns the `said` ids settled."""
    st = ctx.need_tx().state
    if not records(st):
        return []
    out = triggered(st, getattr(reader, "beats", []))
    for sid in out:
        settle(ctx, sid, record)
    return out


__all__ = ["INDEX", "SAID", "add_said", "get", "is_repeat", "overlap", "records", "said_by", "said_by_others",
           "said_for", "settle", "settle_triggered", "triggered"]
