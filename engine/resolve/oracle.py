"""The World-Fact Oracle (01.15; PR-01-4; T-01-10) with the engine-side free-question cap (I-038 stopgap).

    res = ask_oracle(OracleQuestion(subject="npc.tam", predicate="has_sister", odds="unlikely", asker="pc.wren"),
                     state=tx.state, rules=rules, rng=rng, mint=tx.mint, store=store, staged=tx.events,
                     free_cap=config["oracle_free_cap_per_scene"])
    tx.add_all(res.events)

Events, in order: the meaning roll's `table_rolled` (yes-and / no-and), `fact_set` (source oracle) for the answer
and for its "and" / "but", `oracle_answered` (event `source` = the asker: a PC id for a player's question, "dm"
otherwise), and `meta_set` logs: `oracle.free_questions.<scene>` (count) and `oracle.free_facts` (the fact ids a
player's question wrote, read by frame_check's free-fact lever caps, 01.15.8). Over the cap a player's question
is refused and `oracle.free_cap_hit.<scene>` is logged.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from engine import ids
from engine.resolve.rulings import RulingRecord, find_rulings, oracle_signature
from engine.resolve.tables import roll_table
from engine.rng import Rng
from engine.store.events import Event, Visibility

Shape = Literal["yes_and", "yes", "yes_but", "no_but", "no", "no_and"]
DM = "dm"
FREE_FACTS_KEY = "oracle.free_facts"
_POSSESS = frozenset({"carries", "carry", "carrying", "has", "have", "having", "holds", "hold", "holding", "wields",
                      "wielding", "owns", "possesses", "wears", "wearing", "armed"})


class OracleQuestion(BaseModel):
    subject: str  # entity id, or "world"
    predicate: str  # with subject, the fact_key (01.15.7)
    question: str = ""
    odds: str  # resolution.yaml#oracle.rungs id, chosen (and logged) before rolling
    asker: str = DM  # the asking PC's id for a player's question (a free fact, 01.15.8), else "dm"
    qualifier: str | None = None  # yes-but / no-but qualifier [J:enum]; default from data
    sealed: bool = False  # a discovery question (01.15.6)
    gate: str | None = None  # what unseals a sealed answer
    visibility: Visibility = "shown"
    place_kind: str | None = None  # for the precedent signature


class OracleResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    status: Literal["answered", "read", "refused"]
    reason: str = ""
    odds: str | None = None
    d100: int | None = None
    shape: Shape | None = None
    answer: Any = None  # a rolled answer is a bool; a "read" is whatever the store holds (a list, a str, ...)
    extreme: bool = False
    twist: bool = False  # a "but" answer
    qualifier: str | None = None
    meaning: list[Any] = Field(default_factory=list)  # the "and" words (tbl.meaning)
    fact_id: str | None = None
    precedent: list[RulingRecord] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)


class OracleRefused(ValueError):
    pass


def _cfg(rules: Any) -> Any:
    return rules.resolution["oracle"]


def _rung(rules: Any, odds: str) -> Any:
    for r in _cfg(rules)["rungs"]:
        if r["id"] == odds:
            return r
    raise OracleRefused(f"unknown odds rung {odds!r}")


def oracle_shape(yes_on: int, d100: int, doubles: Sequence[int] = (11, 22, 33, 44, 55, 66, 77, 88, 99, 100),
                 but_band: int = 5) -> Shape:  # rule: 01.15.3
    """Yes at or above the threshold; doubles make it extreme (and); within 5 of it, a but; else plain."""
    if not 1 <= d100 <= 100:
        raise ValueError(f"d100 out of range: {d100}")
    yes = d100 >= yes_on
    if d100 in doubles:
        return "yes_and" if yes else "no_and"
    if yes and d100 <= yes_on + but_band - 1:
        return "yes_but"
    if not yes and d100 >= yes_on - but_band:
        return "no_but"
    return "yes" if yes else "no"


def shape_for(rules: Any, odds: str, d100: int) -> Shape:  # rule: T-01-10
    cfg = _cfg(rules)
    return oracle_shape(int(_rung(rules, odds)["yes_on"]), d100, tuple(cfg["doubles"]["faces"]))


def free_count(state: Any) -> int:
    """Player (free) Oracle questions asked in the current scene."""
    return int(state.meta.get(f"oracle.free_questions.{_scene(state)}", 0))


def _scene(state: Any) -> str:
    return state.scene.scene_id if state.scene is not None else "none"


# NPC record fields that hold lists (engine/gen/npc.py); an Oracle answer stored under one would replace the list
RECORD_LISTS = frozenset({"wants", "refusals", "fears", "secrets", "knowledge", "ties"})


def _fact(state: Any, mint: Callable[[str], str], subject: str, predicate: str, value: Any, q: OracleQuestion,
          rule_id: str) -> Event:
    vis: Visibility = "sealed" if q.sealed else q.visibility
    return Event.of("fact_set", {"source": "oracle"}, source=q.asker, rule_id=rule_id, fact_id=mint(ids.FACT),
                    subject=subject, predicate=predicate, value=value, visibility=vis,
                    supersedes=state.current_fact_id(subject, predicate), gate=q.gate if q.sealed else None)


def ask_oracle(q: OracleQuestion, *, state: Any, rules: Any, rng: Rng, mint: Callable[[str], str],
               store: Any = None, staged: Sequence[Event] = (), free_cap: int | None = None) -> OracleResult:
    # rule: PR-01-4
    """PR-01-4 steps 1, 3-8 (step 2, an actor attempting it, is the caller's: a fortune check instead)."""
    if q.predicate in RECORD_LISTS:  # a yes/no never shadows an NPC's list field (playtest crash, P-084)
        q = q.model_copy(update={"predicate": f"asked_{q.predicate}"})
    # 1 / 3. the subject's sheet already answers a possession ("carries_a_rapier"): read it, never roll (P-090)
    verb, _, thing = q.predicate.removeprefix("is_").removeprefix("does_").partition("_")
    if verb in _POSSESS and thing:
        from engine.store.views import sheet_holds

        fid = sheet_holds(state, q.subject, thing)
        if fid is not None:
            return OracleResult(status="read", reason=f"on the sheet: {fid} (02.8.1)", fact_id=fid, answer=True)
    # established answer → read it; never re-ask the same key (01.15.7)
    existing = state.current_fact_id(q.subject, q.predicate)
    if existing is not None:
        return OracleResult(status="read", reason=f"already established: {existing} (01.15.7)", fact_id=existing,
                            answer=state.facts[existing].value)
    rung = _rung(rules, q.odds)
    free = q.asker != DM
    scene = _scene(state)
    events: list[Event] = []
    if free and free_cap is not None and free_count(state) >= free_cap:  # rule: 01.15.8
        hit = Event.of("meta_set", source="oracle", rule_id="01.15.8", key=f"oracle.free_cap_hit.{scene}",
                       value={"question": q.question or f"{q.subject}.{q.predicate}", "cap": free_cap,
                              "asker": q.asker})
        return OracleResult(status="refused", odds=q.odds, events=[hit],
                            reason=f"free Oracle questions this scene reached the cap ({free_cap}; I-038 stopgap)")
    # 4. precedent (00.15.6)
    precedent = find_rulings(store, oracle_signature(q.predicate, q.place_kind), staged=staged)
    res = OracleResult(status="answered", odds=q.odds, precedent=precedent)
    written: list[str] = []
    if not rung.get("roll", True):  # Certain / Impossible: no roll (01.15.2)
        res.answer = bool(rung["answer"])
        res.shape = "yes" if res.answer else "no"
        ev = _fact(state, mint, q.subject, q.predicate, res.answer, q, "01.15.2")
        events.append(ev)
        res.fact_id = ev.payload.fact_id  # type: ignore[attr-defined]
        written.append(res.fact_id)  # type: ignore[arg-type]
    else:
        # 6. d100 → shape (T-01-10)
        res.d100 = rng.d100(f"oracle: {q.question or q.subject + '.' + q.predicate} ({q.odds})", stream="oracle")
        res.shape = shape_for(rules, q.odds, res.d100)
        res.answer = res.shape.startswith("yes")
        res.extreme = res.shape in ("yes_and", "no_and")
        res.twist = res.shape in ("yes_but", "no_but")
        extra: list[tuple[str, Any]] = []
        # 7. the "and" from tbl.meaning; the "but" from its closed list
        if res.extreme:
            meaning = roll_table("tbl.meaning", {"meaning_kind": "action"}, rules=rules, state=state, rng=rng,
                                 purpose=f"oracle and: {q.subject}.{q.predicate}")
            events += meaning.events
            res.meaning = list(meaning.words)
            extra.append((f"{q.predicate}.and", res.meaning))
        if res.twist:
            quals = _cfg(rules)["qualifiers"][res.shape]
            res.qualifier = q.qualifier if q.qualifier in quals["options"] else quals["default"]
            extra.append((f"{q.predicate}.but", res.qualifier))
        # 8. the fact first, then the log entry
        ev = _fact(state, mint, q.subject, q.predicate, res.answer, q, "01.15.5")
        events.append(ev)
        res.fact_id = ev.payload.fact_id  # type: ignore[attr-defined]
        written.append(res.fact_id)  # type: ignore[arg-type]
        for pred, val in extra:
            e2 = _fact(state, mint, q.subject, pred, val, q, "01.15.4")
            events.append(e2)
            written.append(e2.payload.fact_id)  # type: ignore[attr-defined]
        events.append(Event.of("oracle_answered", source=q.asker, rule_id="PR-01-4",
                               question=q.question or f"{q.subject}.{q.predicate}?", odds=q.odds, d100=res.d100,
                               answer="yes" if res.answer else "no", extreme=res.extreme, twist=res.twist,
                               fact_id=res.fact_id))
    if free:  # the log that tells a free fact from the rest (01.15.5, I-038)
        events.append(Event.of("meta_set", source="oracle", rule_id="01.15.8",
                               key=f"oracle.free_questions.{scene}", value=free_count(state) + 1))
        events.append(Event.of("meta_set", source="oracle", rule_id="01.15.8", key=FREE_FACTS_KEY,
                               value=[*state.meta.get(FREE_FACTS_KEY, []), *written]))
    res.events = events
    return res
