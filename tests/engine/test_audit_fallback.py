"""The plain fallback (12.3.3): built from the adjudication record only, no invented content, no mechanics."""

from __future__ import annotations

import re

from engine.audit import text as tx
from engine.audit.claims import Verdict
from engine.audit.fallback import plain_fallback
from engine.audit.screen import mechanics_in_fiction
from engine.dm.adjudication import (
    AdjudicationRecord,
    BeatEntry,
    CostEntry,
    NpcActionEntry,
    OmenEntry,
    PauseEntry,
    PositionEntry,
    SceneEntry,
)

NAMES = {"pc.wren": "Wren", "npc.tam_harlan": "Tam"}


def _record(**kw: object) -> AdjudicationRecord:
    beat = BeatEntry(restatement="Wren forces the hasp with the iron bar (verb.force)", actor="pc.wren",
                     degree="success", near_miss=True, success_at_cost=True, rolled=True,
                     costs=[CostEntry(menu_id="cost.noise", severity="S2", form="the bar shrieks against the iron")],
                     positions=[PositionEntry(entity="pc.wren", words="inside the archive")])
    return AdjudicationRecord(
        turn_id="turn.4", pc="pc.wren", beats=[beat], scene=SceneEntry(header="The old archive, morning"),
        npc_actions=[NpcActionEntry(npc="npc.tam_harlan", action="turns toward the noise", source="table_row")],
        omens=[OmenEntry(clock_id="clk.alarm", omen="boots on the upper stairs")], **kw)  # type: ignore[arg-type]


def _vocab(rec: AdjudicationRecord) -> set[str]:
    allowed = tx.content(" ".join(map(str, rec.dump().values())) + " " + " ".join(NAMES.values()))
    return allowed | tx.content("it works at a cost what do you does not go goes better than hoped badly wrong "
                                "falls just short comes someone are is yes no")


def test_built_only_from_the_record() -> None:
    rec = _record()
    fb = plain_fallback(rec, names=NAMES, verdicts=[Verdict(claim=0, verdict="contradicted", fix="redraft_to_store")])
    assert tx.content(fb.fiction) <= _vocab(rec), tx.content(fb.fiction) - _vocab(rec)
    for piece in ("forces the hasp", "It works, at a cost", "The bar shrieks", "Boots on the upper stairs",
                  "Tam turns toward the noise", "The old archive, morning."):
        assert piece in fb.fiction
    assert fb.fiction.endswith("What do you do?")
    assert not re.search(r"\d|verb\.", fb.fiction)
    assert mechanics_in_fiction(fb.fiction) == []
    assert fb.review_flag and fb.ruling.kind == "rule_conflict" and fb.ruling.review_flag
    assert fb.ruling.result["verdicts"][0]["verdict"] == "contradicted"


def test_pause_and_owed_warning() -> None:
    rec = _record(pause=PauseEntry(kind="offer"), triggers=["trg.lethal_warning"])
    fb = plain_fallback(rec, names=NAMES)
    assert not fb.fiction.endswith("?")  # the pause block follows instead (12.14.9)
    assert fb.owed_blocks == ["[WARNING]"]


def test_empty_record_invents_nothing() -> None:
    fb = plain_fallback(AdjudicationRecord(pc="pc.wren"))
    assert fb.fiction == "What do you do?"
