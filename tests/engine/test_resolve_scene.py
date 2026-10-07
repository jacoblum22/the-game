"""Builders shared by the engine/resolve tests and the ch.01 golden tests (plus a smoke test of them).

    s = Scene.new(tmp_path)                      # a game with a started scene and Wren (WE-01's PC)
    s.npc("Tam Harlan", attributes={"wits": 1}) # -> "npc.tam_harlan"
    fid = s.fact("world", "courtyard.floor", "grit")
    rng = FixedRng([12, 4])                      # scripted dice, in draw order
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from engine import ids
from engine.data.loader import Rules, load_rules
from engine.resolve.types import Beat
from engine.rng import Rng
from engine.store.db import Store
from engine.store.events import EntityRecord, Event, LicenseInstance, Quantity, SceneRecord
from tests.fixtures.game import new_store

WREN_ATTRS = {"might": 1, "agility": 3, "endurance": 1, "wits": 2, "intellect": 0, "presence": 0, "resolve": 0}


class FixedRng(Rng):
    """An Rng whose draws are scripted (fixed dice for worked examples); records every draw's purpose."""

    def __init__(self, faces: Iterable[int]) -> None:
        super().__init__(0)
        self.faces = deque(faces)
        self.drawn: list[tuple[str, int, int]] = []  # (purpose, sides, result)

    def draw(self, n: int, purpose: str, *, stream: str = "dice", table_id: str | None = None) -> int:
        if not self.faces:
            raise AssertionError(f"no scripted face left for {purpose!r}")
        face = self.faces.popleft()
        assert 1 <= face <= n, f"scripted face {face} outside 1..{n} for {purpose!r}"
        self.drawn.append((purpose, n, face))
        return face


class Scene:
    def __init__(self, store: Store, rules: Rules) -> None:
        self.store = store
        self.rules = rules
        self.pc = ""

    @classmethod
    def new(cls, tmp_path: Path, *, pc_attrs: dict[str, int] | None = None, pc_competence: dict[str, int] | None = None,
            pc_licenses: Iterable[str] = ("lic.lang.common",)) -> Scene:
        s = cls(new_store(tmp_path), load_rules())
        with s.store.transaction("turn.0") as tx:
            sid = tx.mint(ids.SCENE)
            tx.add(Event.of("scene_started", source="test", scene_id=sid, scene=SceneRecord(scene_id=sid)))
        s.pc = s.add("pc", "Wren", attributes=pc_attrs or WREN_ATTRS, competence=pc_competence or {},
                     licenses=pc_licenses, quantities={"vitality": (13, 0, 13), "focus": (4, 0, 4)})
        return s

    @property
    def state(self) -> Any:
        return self.store.state

    def add(self, kind: str, name: str, *, attributes: dict[str, int] | None = None,
            competence: dict[str, int] | None = None, licenses: Iterable[str] = (),
            quantities: dict[str, tuple[int, int, int | None]] | None = None, **data: Any) -> str:
        with self.store.transaction() as tx:
            eid = ids.entity_id(kind, name, tx.state.entities)
            rec = EntityRecord(id=eid, kind=kind, name=name,  # type: ignore[arg-type]
                               data={"attributes": attributes or {}, "competence": competence or {}, **data})
            qs = {k: Quantity(current=c, min=lo, max=hi) for k, (c, lo, hi) in (quantities or {}).items()}
            tx.add(Event.of("entity_created", source="test", entity=rec, quantities=qs,
                            licenses=[LicenseInstance(license_id=lic) for lic in licenses]))
        return eid

    def npc(self, name: str, **kw: Any) -> str:
        return self.add("npc", name, **kw)

    def fact(self, subject: str, predicate: str, value: Any = True, source: str = "narration") -> str:
        with self.store.transaction() as tx:
            fid = tx.mint(ids.FACT)
            tx.add(Event.of("fact_set", {"source": source}, fact_id=fid, subject=subject, predicate=predicate,
                            value=value, visibility="shown",
                            supersedes=tx.state.current_fact_id(subject, predicate)))
        return fid

    def apply(self, events: list[Event]) -> list[int]:
        with self.store.transaction() as tx:
            return tx.add_all(events)

    def beat(self, **kw: Any) -> Beat:
        base: dict[str, Any] = {"id": "beat.1", "actor": self.pc, "intent": "do it", "method": "do it",
                                "declared_seq": self.state.last_seq}
        return Beat(**{**base, **kw})


def test_scene_builder(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    tam = s.npc("Tam Harlan", attributes={"wits": 1})
    fid = s.fact("world", "courtyard.floor", "grit")
    assert s.pc == "pc.wren" and tam == "npc.tam_harlan"
    assert s.state.facts[fid].value == "grit" and s.state.scene is not None
    rng = FixedRng([7])
    assert rng.d(20, "x") == 7 and rng.drawn == [("x", 20, 7)]
    assert s.store.rebuild() == s.state
