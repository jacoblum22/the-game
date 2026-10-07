"""Builds a game state from a small declarative spec (cases.yaml `fixtures` / `extra`) and runs a case's turn.

    store = new_store(tmp_path)
    build(store, spec)                                  # entities, licences, facts, positions, ... then the scene
    record = turn(store, events_spec, record_spec)      # "this turn's" writes, recorded in the adjudication record

Ids: entities get name ids (`npc.mara_voss`); `fact_id: auto` and condition instances are minted; a knowledge
entry names its fact as "<subject>|<predicate>".
"""

from __future__ import annotations

from typing import Any

from engine import ids
from engine.dm.adjudication import AdjudicationRecord
from engine.store.events import ClockRecord, ConditionInstance, Event, LicenseInstance, SceneRecord
from tests.fixtures.game import entity


def _ent(tx: Any, e: dict[str, Any]) -> Event:
    q = {k: tuple(v) for k, v in (e.get("quantities") or {}).items()}
    return entity(e["kind"], e["name"], tx=tx, visibility=e.get("visibility", "shown"), sealed=e.get("sealed"),
                  slices=e.get("slices"), data=e.get("data"), quantities=q, gate=e.get("gate"))  # type: ignore[arg-type]


def _fact(tx: Any, f: dict[str, Any]) -> Event:
    return Event.of("fact_set", {"source": f.get("source", "narration")}, source="test", rule_id="00.14.2",
                    fact_id=tx.mint(ids.FACT), subject=f["subject"], predicate=f["predicate"], value=f["value"],
                    visibility=f.get("visibility", "shown"), gate=f.get("gate"),
                    supersedes=tx.state.current_fact_id(f["subject"], f["predicate"]))


def build(store: Any, spec: dict[str, Any], turn_id: str | None = "turn.0") -> None:
    with store.transaction(turn_id) as tx:
        for e in spec.get("entities", []):
            tx.add(_ent(tx, e))
        for lic in spec.get("licenses", []):
            tx.add(Event.of("license_granted", source="test", entity=lic["entity"],
                            license=LicenseInstance(license_id=lic["license_id"], grade=lic.get("grade", "trained"))))
        for f in spec.get("facts", []):
            tx.add(_fact(tx, f))
        for p in spec.get("positions", []):
            tx.add(Event.of("position_set", source="test", entity=p["entity"], location=p.get("location"),
                            flags_add=p.get("flags", []), band_to=p.get("band_to", {})))
        for r in spec.get("relationships", []):
            tx.add(Event.of("relationship_set", source="test", a=r["a"], b=r["b"], kind=r.get("kind", "standing"),
                            new_value=r["value"], reason="fixture"))
        for k in spec.get("knowledge", []):
            subject, _, predicate = k["fact"].partition("|")
            fid = tx.state.current_fact_id(subject, predicate)
            tx.add(Event.of("knowledge_recorded", source="test", knower=k["knower"], fact_id=fid,
                            how=k.get("how", "witnessed")))
        for c in spec.get("clocks", []):
            cid = ids.clock_id(c["name"], tx.state.clocks)
            rec = ClockRecord(id=cid, name=c["name"], kind=c.get("kind", "danger"), segments=c.get("segments", 6),
                              filled=c.get("filled", 0), visibility=c.get("visibility", "public"),
                              omens=c.get("omens", {}), owner=c.get("owner", ""))
            tx.add(Event.of("clock_created", source="test", clock=rec))
        for c in spec.get("conditions", []):
            iid = tx.mint(ids.CONDITION_INSTANCE)
            inst = ConditionInstance(instance_id=iid, condition_id=c["condition_id"], target=c["target"],
                                     severity=c.get("severity", "S1"), remaining=c.get("remaining", "scene"))
            tx.add(Event.of("condition_applied", source="test", instance_id=iid, target=c["target"], instance=inst))
        for m in spec.get("meta", []):
            tx.add(Event.of("meta_set", source="test", key=m["key"], value=m["value"]))
        sc = spec.get("scene")
        if sc:
            sid = tx.mint(ids.SCENE)
            rec = SceneRecord(scene_id=sid, place_id=sc.get("place"), cast_present=sc.get("cast", []))
            tx.add(Event.of("scene_started", source="test", scene_id=sid, scene=rec))


def _event(tx: Any, spec: dict[str, Any]) -> Event:
    spec = dict(spec)
    etype = spec.pop("type")
    if etype == "fact_set":
        return _fact(tx, spec)
    if etype == "condition_applied":
        iid = tx.mint(ids.CONDITION_INSTANCE)
        inst = ConditionInstance(instance_id=iid, condition_id=spec["condition_id"], target=spec["target"],
                                 severity=spec.get("severity", "S1"), remaining=spec.get("remaining", "scene"))
        return Event.of("condition_applied", source="test", instance_id=iid, target=spec["target"], instance=inst)
    if etype == "condition_removed" and spec.get("condition_id"):
        inst = next(c for c in tx.state.conditions.values()
                    if c.condition_id == spec["condition_id"] and c.target == spec["target"])
        return Event.of("condition_removed", source="test", instance_id=inst.instance_id, reason="test")
    if etype == "entity_created":
        return _ent(tx, spec)
    return Event.of(etype, source="test", **spec)


def turn(store: Any, events: list[dict[str, Any]], record: dict[str, Any] | None = None,
         turn_id: str = "turn.1") -> AdjudicationRecord:
    """Write this turn's events and return the adjudication record (its `writes` filled from them)."""
    rec = AdjudicationRecord.model_validate({"turn_id": turn_id, **(record or {})})
    seqs: list[int] = []
    if events:
        with store.transaction(turn_id) as tx:
            seqs = [tx.add(_event(tx, spec)) for spec in events]
    rec.add_writes(ev for ev in (store.event(s) for s in seqs) if ev is not None)
    return rec
