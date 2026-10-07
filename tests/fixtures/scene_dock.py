"""T030: the dock at night. A scene to play turns in, built only through store events.

    dock = build_dock(tmp_path)              # store, rng, rules and the ids below
    dock.pc, dock.ferryman, dock.watch, dock.place, dock.clock, dock.facts["lantern"]

- The place `loc.the_night_dock` (site mode, night watch), with three shown facts (lantern, fog, the moored ferry).
- Wren (`pc.wren`): attributes, two licences (`lic.training.guile_stealth`, `lic.training.guile_thievery`), one
  starting ability (`ab.soft_step`), Vitality, Fate and Focus.
- Two NPCs present, each with sealed wants and refusals (12.11; sealed from the narrator, read by the World role):
  Tam Harlan the ferryman and Sela Vey of the harbour watch (a named `guard` defense).
- One public scene clock, `clk.the_watch_makes_its_round` (4 segments), listening to exposure and time costs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from engine import ids
from engine.data.loader import Rules, load_rules
from engine.rng import Rng
from engine.store.clocks import create_clock
from engine.store.db import Store
from engine.store.events import EntityRecord, Event, LicenseInstance, Quantity, SceneRecord
from engine.time.scheduler import TimeContext, advance_time, set_mode
from tests.fixtures.game import new_store

WREN = {"might": 1, "agility": 3, "endurance": 1, "wits": 2, "intellect": 0, "presence": 1, "resolve": 0}
LICENCES = ("lic.training.guile_stealth", "lic.training.guile_thievery")
ABILITY = "ab.soft_step"

WATCH_CLOCK = {
    "kind": "danger", "segments": 4, "visibility": "public", "direction": "fill",
    "tick_sources": [{"on": "cost.exposure", "ticks": "U(severity)", "condition": None},
                     {"on": "cost.time", "ticks": "U(severity)", "condition": None},
                     {"on": "trait.sense.loud", "ticks": 1, "condition": None}],
    "omens": {"stirring": ["a lantern bobs at the far end of the quay", "boots on wet planks, unhurried"],
              "building": ["a whistle answered from the harbour wall", "the lantern turns your way"],
              "imminent": ["torches gather at the stair", "a voice calls the watch to the dock"]},
    "on_complete": {"effects": [{"effect_id": "eff.write_fact",
                                 "params": {"subject": "world", "predicate": "watch_on_the_dock", "value": True}}]},
}


@dataclass
class DockScene:
    store: Store
    rules: Rules
    rng: Rng
    pc: str = ""
    ferryman: str = ""
    watch: str = ""
    place: str = ""
    clock: str = ""
    scene: str = ""
    facts: dict[str, str] = field(default_factory=dict)

    @property
    def state(self) -> Any:
        return self.store.state


def _entity(tx: Any, kind: str, name: str, *, data: dict[str, Any], sealed: dict[str, Any] | None = None,
            quantities: dict[str, tuple[int, int, int]] | None = None, licences: tuple[str, ...] = ()) -> str:
    eid = ids.entity_id(kind, name, tx.state.entities)
    rec = EntityRecord(id=eid, kind=kind, name=name, data={**data, **(sealed or {})},  # type: ignore[arg-type]
                       sealed_fields=sorted(sealed or {}))
    qs = {k: Quantity(current=c, min=lo, max=hi) for k, (c, lo, hi) in (quantities or {}).items()}
    tx.add(Event.of("entity_created", source="fixture", rule_id="PR-12-5", entity=rec, quantities=qs,
                    licenses=[LicenseInstance(license_id=lic) for lic in licences]))
    return eid


def _fact(tx: Any, subject: str, predicate: str, value: Any) -> str:
    fid = tx.mint(ids.FACT)
    tx.add(Event.of("fact_set", {"source": "narration"}, source="fixture", rule_id="00.6.6", fact_id=fid,
                    subject=subject, predicate=predicate, value=value, visibility="shown"))
    return fid


def build_dock(tmp_path: Path, *, seed: int = 1234, rng: Rng | None = None) -> DockScene:
    store = new_store(tmp_path, seed=seed)
    rules = load_rules()
    dock = DockScene(store=store, rules=rules, rng=rng or Rng.for_store(store))
    with store.transaction("turn.0") as tx:
        tctx = TimeContext(tx, rules, dock.rng)
        advance_time(tctx, 3, "watch", "the fixture opens at night")  # morning → night
        dock.place = _entity(tx, "place", "The Night Dock", data={"place_kind": "landmark"})
        dock.pc = _entity(tx, "pc", "Wren", data={"attributes": WREN, "competence": {}, "abilities": [ABILITY],
                                                   "pronouns": "she/her"},
                          quantities={"vitality": (13, 0, 13), "fate": (1, 0, 3), "focus": (4, 0, 4)},
                          licences=LICENCES)
        dock.ferryman = _entity(
            tx, "npc", "Tam Harlan",
            data={"role": "ferryman", "pronouns": "he/him", "demeanor": "taciturn",
                  "attributes": {"wits": 1, "presence": 0, "resolve": 1}, "defenses": {"notice": 11}},
            sealed={"wants": ["to get the last ferry across before the tide turns", "to be paid in silver"],
                    "refusals": ["will not carry anyone the harbour watch is looking for"]})
        dock.watch = _entity(
            tx, "npc", "Sela Vey",
            data={"role": "harbour watch", "pronouns": "she/her", "demeanor": "alert",
                  "attributes": {"wits": 2, "presence": 1, "resolve": 1}, "defenses": {"guard": 13}},
            sealed={"wants": ["to catch the smuggler before dawn"],
                    "refusals": ["will not take a bribe in front of witnesses"]})
        for e in (dock.pc, dock.ferryman, dock.watch):
            tx.add(Event.of("position_set", source="fixture", rule_id="10.1.1", entity=e, location=dock.place))
        dock.scene = tx.mint(ids.SCENE)
        tx.add(Event.of("scene_started", source="fixture", rule_id="PR-12-7", scene_id=dock.scene,
                        scene=SceneRecord(scene_id=dock.scene, place_id=dock.place, mode="site",
                                          agenda="Does Wren get across the water tonight?", hoped_answer="yes",
                                          cast_present=[dock.ferryman, dock.watch], started_seq=tx.state.last_seq)))
        set_mode(tctx, "site", "the dock is a site")
        dock.facts["lantern"] = _fact(tx, dock.place, "light", "one hooded lantern at the stair")
        dock.facts["fog"] = _fact(tx, "world", "weather", "a low fog on the water")
        dock.facts["ferry"] = _fact(tx, dock.place, "ferry", "moored at the far end of the quay")
        ev = create_clock(tx.state, WATCH_CLOCK, name="The watch makes its round", owner="12", rule_id="PR-12-7")
        tx.add(ev)
        dock.clock = ev.payload.clock.id  # type: ignore[attr-defined]
    return dock
