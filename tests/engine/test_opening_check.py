"""The first opening passes the check (12.16.16): no player message means no 12.2.7 "part not answered", the inciting
incident sources the witnesses' reactions, and the opening's furniture is described without asking the Oracle.

Claims and screen flags are shaped on the playtest openings of 2026-10-07 that fell back to "The hall, morning. What
do you do?" (saves playtest-*-182337-talker, -185715-talker, -191540-breaker, -163940-breaker).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.audit.claims import check_claims
from engine.audit.screen import screen_draft
from engine.data.loader import load_rules
from engine.dm.adjudication import AdjudicationRecord, PartEntry
from engine.dm.context import TurnContext
from engine.dm.session import opening
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from tests.engine.test_incident import _world
from tests.engine.test_turn_narration import _must, calls, chk, claim, passage

OPENING = ("Gulls wheel over the market, and the stalls are wet from the night. "
           "Heads turn toward the gate, and the hands at the nets stop mid-lift. "
           "Someone near the well swears under their breath. "
           "Corra Pike looks round to see who heard. "
           "What do you do?")
INCIDENT = "the inciting incident: a child (or an elder, or a priest) is missing since last night"


def test_opening_with_crowd_reactions_passes_first_draft(tmp_path: Path) -> None:
    store = _world(tmp_path, option="omen")  # no bound person: the incident is the note alone
    def draft(schema: object, packet: object) -> dict[str, object]:
        """Spec 019: one passage; its side list covers the incident's line."""
        return passage(OPENING, _must(packet))
    model = ScriptedModel({Role.NARRATOR: [draft]})
    check = chk(claim(0, "loc.market", "identity", "appearance", "stalls wet from the night"),
                claim(1, "unknown", "action", "heads turn", "toward the gate", change=True),
                claim(1, "unknown", "action", "hands stop mid-lift", "stopped", change=True),
                claim(2, "unknown", "action", "swears", "under their breath", change=True),
                claim(3, "npc.corra_pike", "action", "looks round", "to see who heard", change=True))

    def checked(schema: Any, packet: Any) -> dict[str, Any]:
        out = check(schema, packet)
        out["screen"]["intent_acknowledged"] = False  # what the Checker said, shown "THE PLAYER'S MESSAGE: (none)"
        return out
    model.push(Role.CHECKER, checked)
    resp = opening(TurnContext.for_store(store, model=model))
    assert resp.fiction == OPENING and not resp.flags.fallback_used
    assert len(calls(model, Role.NARRATOR)) == 1  # the sampled audit (turn.1) runs after delivery, logs only
    assert len(calls(model, Role.CHECKER)) in (0, 2)


def test_incident_sources_reactions_not_deeds() -> None:
    """Spec 006: a sentence citing the incident's line sources an unnamed witness's reaction; a change still needs
    its own source; with nothing cited the same murmur has none."""
    store_rules = load_rules()
    from engine.dm.handles import items
    from engine.store.projection import WorldState

    cs = [{"subject": "unknown", "class": "action", "predicate": "murmur", "value": "goes through the crowd",
           "asserts_change": False},
          {"subject": "unknown", "class": "action", "predicate": "grabs", "value": "the purse and flees",
           "asserts_change": True},
          {"subject": "unknown", "class": "action", "predicate": "bandit lurks", "value": "by the gate",
           "asserts_change": True}]
    given = AdjudicationRecord(notes=[INCIDENT])
    vs = check_claims(cs, WorldState(), given, [], rules=store_rules, cited={0: items(given, names={})})
    assert [v.verdict for v in vs] == ["supported", "unsourced_change", "unsourced_change"]
    plain = check_claims(cs[:1], WorldState(), given, [], rules=store_rules)
    assert plain[0].verdict == "unsourced_change"


def test_screen_ignores_acknowledgement_flags_with_no_message() -> None:
    flags = {"intent_acknowledged": False, "intent_substituted": True}
    assert screen_draft("The market is loud. What do you do?", flags=flags, record=AdjudicationRecord()).passed
    asked = AdjudicationRecord(parts=[PartEntry(cls="DECLARATION", text="I look over the quay")])
    res = screen_draft("The market is loud. What do you do?", flags=flags, record=asked)
    assert not res.passed and sum("12.2.7" in r for r in res.reasons) == 2
