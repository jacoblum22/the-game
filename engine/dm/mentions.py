"""Write-on-mention (00.6.6, PR-00-7 steps 2-3; 12.11.1; T047): the Narrator's `mentions` become store entries
before the draft is checked and delivered.

    res = write_mentions(narrator["mentions"], tx=tx, rules=rules, rng=rng)
    record.add_writes(...)  # res.seqs are the staged events' seqs; res.created maps mention name -> entity id

Per mention: an existing entity with that name or alias is reused (nothing written); otherwise it is created
with only the properties the draft implies (`entity_created` + one `fact_set` per implied property). An NPC is
generated per PR-12-5 (walk-on fields rolled and written at once, the draft's implied ones kept): through
`engine.world.social.meet_npc` (the roster first) when the draft implies nothing about who they are, else from
`engine.gen.npc.walk_on` with the implied fields fixed. Unsettled properties are settled now: a data table
`tbl.<kind>_<property>` when one exists, else the Oracle (Even odds: the draft's facts set no other) — or by an
injected `settle(entity_id, property) -> value | None`. Kinds that are never created by mention (a foe, an ally,
a clue, a faction, a thread, a rumor: 12.14.13; the Narrator prompt) are refused, and the draft cuts them.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from engine import ids
from engine.store.events import EntityRecord, Event

MENTIONABLE = ("npc", "item", "object", "place")
DEFAULT_ODDS = "even"
_ARTICLE = re.compile(r"^(?:the|a|an|some|one|this|that)\s+", re.IGNORECASE)
_NPC_KEYS = {  # implied predicate words -> walk-on field (12.11.1)
    "gender": "gender", "sex": "gender", "pronoun": "pronouns", "pronouns": "pronouns", "age": "age",
    "role": "role", "profession": "role", "job": "role", "occupation": "role", "trade": "role", "title": "role",
    "detail": "detail", "appearance": "detail", "look": "detail", "demeanor": "demeanor", "demeanour": "demeanor",
    "manner": "demeanor", "people": "people", "species": "people", "folk": "people",
}
_PRONOUNS = {"woman": "she/her", "female": "she/her", "girl": "she/her", "man": "he/him", "male": "he/him",
             "boy": "he/him"}
_GENDERS = {"she/her": "woman", "she": "woman", "her": "woman", "he/him": "man", "he": "man", "him": "man",
            "they/them": "person", "they": "person"}

Settle = Callable[[str, str], Any]


class Implied(BaseModel):
    predicate: str
    value: str


class Mention(BaseModel):
    """contracts/model-calls.md NarratorOutput.mentions item."""

    model_config = ConfigDict(extra="ignore")

    kind: str
    name: str
    implied: list[Implied] = Field(default_factory=list)
    unsettled: list[str] = Field(default_factory=list)


class Settled(BaseModel):
    entity: str
    property: str
    value: Any
    how: str  # "table:<id>" | "oracle" | "injected"
    fact_id: str | None = None


class MentionResult(BaseModel):
    created: dict[str, str] = Field(default_factory=dict)  # mention name -> new entity id
    reused: dict[str, str] = Field(default_factory=dict)  # mention name -> existing entity id
    refused: list[str] = Field(default_factory=list)  # mention names not written (the draft cuts them)
    settled: list[Settled] = Field(default_factory=list)
    unsettled: list[tuple[str, str]] = Field(default_factory=list)  # (entity, property) left open
    seqs: list[int] = Field(default_factory=list)

    @property
    def ids(self) -> list[str]:
        return [*self.created.values(), *self.reused.values()]


def bare(name: str) -> str:
    return _ARTICLE.sub("", name.strip()).strip()


def _proper(name: str) -> bool:
    """A personal name ("Bessa Crane"), not a description ("the ferryman", "an old woman")."""
    n = name.strip()
    return bool(n) and not _ARTICLE.match(n) and n[0].isupper()


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def find_existing(state: Any, name: str, kind: str | None = None) -> str | None:  # rule: 00.6.6
    """An entity whose name, alias or id tail equals the mention's name (articles and case ignored)."""
    want = bare(name).lower()
    if not want:
        return None
    for eid, e in state.entities.items():
        if kind and e.kind != kind and not (kind in ("item", "object") and e.kind in ("item", "object")):
            continue
        names = [e.name, eid.split(".", 1)[-1].replace("_", " ")]
        names += [a for a in e.data.get("aliases", []) if isinstance(a, str)]
        if kind == "npc":
            names.append(str(e.data.get("role", "")))
        if any(bare(n).lower() == want for n in names if n):
            return eid
    if kind == "npc" and _proper(name) and " " not in want:  # "Edda" is the one NPC named "Edda Brightcote"
        given = [eid for eid, e in state.entities.items()
                 if e.kind == "npc" and e.name and str(e.name).split()[0].lower() == want]
        if len(given) == 1:  # given names are kept unique (walk-on `given_used`); two matches stay ambiguous
            return given[0]
    return None


def _place(state: Any) -> str | None:
    sc = state.scene
    return sc.place_id if sc is not None and sc.place_id in state.entities else None


def write_mentions(mentions: Iterable[Mention | dict[str, Any]], *, tx: Any, rules: Any, rng: Any = None,
                   settle: Settle | None = None, place: str | None = None,
                   turn_id: str | None = None) -> MentionResult:  # rule: PR-00-7
    """Stage each mention's writes in `tx` (PR-00-7 step 2) and settle its unsettled properties (step 3)."""
    res = MentionResult()
    for raw in mentions:
        m = raw if isinstance(raw, Mention) else Mention.model_validate(raw)
        _one(m, tx=tx, rules=rules, rng=rng, settle=settle, place=place or _place(tx.state), res=res)
    return res


def _one(m: Mention, *, tx: Any, rules: Any, rng: Any, settle: Settle | None, place: str | None,
         res: MentionResult) -> None:  # rule: 00.6.6
    kind = m.kind if m.kind in MENTIONABLE else None
    if kind is None:
        res.refused.append(m.name)
        return
    found = find_existing(tx.state, m.name, kind)
    if found is not None:
        res.reused[m.name] = found
        return
    if kind == "npc":
        known = set(tx.state.entities)
        eid, implied = _npc(m, tx=tx, rules=rules, rng=rng, place=place, res=res)
        if eid in known:  # the roster held them (PR-12-5 step 1)
            res.reused[m.name] = eid
            return
    else:
        eid = ids.entity_id(kind, bare(m.name), tx.state.entities)
        rec = EntityRecord(id=eid, kind=kind, name=bare(m.name), visibility="shown")  # type: ignore[arg-type]
        res.seqs.append(tx.add(Event.of("entity_created", source="mention", rule_id="00.6.6", entity=rec)))
        if place is not None and kind != "place":
            res.seqs.append(tx.add(Event.of("position_set", source="mention", rule_id="00.6.6", entity=eid,
                                            location=place)))
        implied = m.implied
    res.created[m.name] = eid
    for imp in implied:
        res.seqs.append(tx.add(_fact(tx, eid, _slug(imp.predicate), imp.value, "narration", "00.6.6")))
    for prop in m.unsettled:
        _settle(eid, kind, prop, tx=tx, rules=rules, rng=rng, settle=settle, res=res)


def _fact(tx: Any, subject: str, predicate: str, value: Any, source: str, rule_id: str) -> Event:
    return Event.of("fact_set", {"source": source}, source="mention", rule_id=rule_id, fact_id=tx.mint(ids.FACT),
                    subject=subject, predicate=predicate, value=value, visibility="shown",
                    supersedes=tx.state.current_fact_id(subject, predicate))


def _npc(m: Mention, *, tx: Any, rules: Any, rng: Any, place: str | None,
         res: MentionResult) -> tuple[str, list[Implied]]:  # rule: 12.11.1
    """Create an NPC (PR-12-5). Returns its id and the implied properties still to write as facts."""
    fixed: dict[str, str] = {}
    rest: list[Implied] = []
    for imp in m.implied:
        key = _NPC_KEYS.get(_slug(imp.predicate).split("_")[0])
        if key and key not in fixed:
            fixed[key] = imp.value
        else:
            rest.append(imp)
    role = fixed.get("role") or (None if _proper(m.name) else bare(m.name)) or None
    if not _proper(m.name) and not (set(fixed) - {"role"}):
        meet = _meet_npc()
        if meet is not None and rng is not None:
            from engine.time.scheduler import TimeContext

            before, known = tx.peek_seq(), set(tx.state.entities)
            eid = meet(TimeContext(tx=tx, rules=rules, rng=rng), role, place)
            res.seqs += list(range(before, tx.peek_seq()))
            return eid, ([] if eid in known else rest)
    if rng is None:
        raise ValueError("an NPC mention needs `rng` (12.11.1: walk-on fields are rolled)")
    from engine.gen import npc as gen_npc

    seed_rng = _seed_rng(rng, f"walk-on on mention: {bare(m.name)} (PR-12-5)")
    used = {str(e.name).split()[0] for e in tx.state.entities.values() if e.kind == "npc" and e.name}
    n = gen_npc.walk_on(seed_rng, role=role, home=place, name_tables=tx.state.meta.get("world.names") or [],
                        given_used=used, existing_ids=tx.state.entities.keys())
    name = bare(m.name) if _proper(m.name) else n.name
    data = n.model_dump(exclude={"id", "name", "sealed_fields", "wants", "fears", "refusals", "secrets", "voice",
                                 "knowledge_scope", "ties", "licenses"}, by_alias=True)
    data.update(fixed)
    if "gender" in fixed and "pronouns" not in fixed:
        data["pronouns"] = _PRONOUNS.get(fixed["gender"].lower(), data.get("pronouns"))
    if "pronouns" in fixed and "gender" not in fixed:
        data["gender"] = _GENDERS.get(fixed["pronouns"].lower(), data.get("gender"))
    if not _proper(m.name) and bare(m.name).lower() != str(data.get("role", "")).lower():
        data["aliases"] = [bare(m.name)]
    eid = ids.entity_id("npc", name, tx.state.entities)
    rec = EntityRecord(id=eid, kind="npc", name=name, visibility="shown", data=data)
    res.seqs.append(tx.add(Event.of("entity_created", source="npc_generation", rule_id="PR-12-5", entity=rec)))
    if place is not None:
        res.seqs.append(tx.add(Event.of("position_set", source="mention", rule_id="PR-12-5", entity=eid,
                                        location=place)))
    cast = dict(tx.state.meta.get("cast_list") or {})  # 12.6.6: the cast list, weight 1 (as meet_npc does)
    if eid not in cast:
        cast[eid] = 1
        res.seqs.append(tx.add(Event.of("meta_set", source="mention", rule_id="12.6.6", key="cast_list",
                                        value=cast)))
    return eid, rest


def _meet_npc() -> Callable[..., str] | None:
    try:
        from engine.world.social import meet_npc
    except ImportError:  # engine/world not built
        return None
    return meet_npc


def _seed_rng(rng: Any, purpose: str) -> Any:
    try:
        from engine.world.social import LoggedSeedRng
    except ImportError:
        return rng  # assume a SeedRng was injected
    return LoggedSeedRng(rng, purpose) if hasattr(rng, "draw") else rng


def _settle(eid: str, kind: str, prop: str, *, tx: Any, rules: Any, rng: Any, settle: Settle | None,
            res: MentionResult) -> None:  # rule: 00.6.6
    """Settle one unsettled property now (PR-00-7 step 3): injected, else a table, else the Oracle."""
    pred = _slug(prop)
    if not pred or tx.state.current_fact_id(eid, pred) is not None:
        return
    if settle is not None:
        value = settle(eid, prop)
        if value is None:
            res.unsettled.append((eid, prop))
            return
        ev = _fact(tx, eid, pred, value, "oracle", "00.12.7")
        res.seqs.append(tx.add(ev))
        res.settled.append(Settled(entity=eid, property=prop, value=value, how="injected",
                                   fact_id=ev.payload.fact_id))  # type: ignore[attr-defined]
        return
    if rng is None:
        res.unsettled.append((eid, prop))
        return
    table = next((t for t in (f"tbl.{kind}_{pred}", f"tbl.{pred}") if rules.has(t)), None)
    if table is not None:
        from engine.resolve.tables import roll_table

        tr = roll_table(table, rules=rules, state=tx.state, rng=rng, purpose=f"settle {eid}.{pred} (00.6.6)")
        res.seqs += tx.add_all(tr.events)
        ev = _fact(tx, eid, pred, tr.entry, "generation", "00.6.6")
        res.seqs.append(tx.add(ev))
        res.settled.append(Settled(entity=eid, property=prop, value=tr.entry, how=f"table:{table}",
                                   fact_id=ev.payload.fact_id))  # type: ignore[attr-defined]
        return
    from engine.resolve.oracle import OracleQuestion, ask_oracle

    name = tx.state.entities[eid].name
    q = OracleQuestion(subject=eid, predicate=pred, question=f"{name}: {prop}?", odds=DEFAULT_ODDS)
    out = ask_oracle(q, state=tx.state, rules=rules, rng=rng, mint=tx.mint, store=getattr(tx, "store", None),
                     staged=getattr(tx, "events", ()))
    res.seqs += tx.add_all(out.events)
    if out.answer is None:
        res.unsettled.append((eid, prop))
        return
    res.settled.append(Settled(entity=eid, property=prop, value=out.answer, how="oracle", fact_id=out.fact_id))
