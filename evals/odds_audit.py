"""Odds audit over the Reader golden set's rolled beats (spec 007 gate; lane D P2 test).

    py -3.12 evals/odds_audit.py

Every golden line labelled as rolling (`necessity: uncertain_and_costly`) is framed by `frame_check` on the dock
fixture, the way the Framer could frame it: each of its verb's rolling obstacle classes (class `other` at Easy,
Moderate and Hard when the verb has none) with 0, 1 and 2 hindering facts, or, for a talk or an attack on a person,
that person's defense; for three PCs (attributes -1, +0 and the dock's Wren). It counts the OFFERs a player would
see with critical failure above success that are not Dire, not opposed, not secret and not labelled long shot
(target 0, 01.6.13), and the share of frames with >= 3 distinct odds across the frame and its computed
alternatives (12.15.2 "Another way").
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.resolve.frame import frame_check, opposed_by, verb_classes  # noqa: E402
from engine.resolve.types import Beat, Frame, ProposedFrame  # noqa: E402
from engine.retrieve.anchors import verb_anchor  # noqa: E402
from engine.store.events import EntityRecord, Event  # noqa: E402
from evals import reader_golden as rg  # noqa: E402
from tests.fixtures.scene_dock import build_dock  # noqa: E402

ATTRS = ("might", "agility", "endurance", "wits", "intellect", "presence", "resolve")


def _pcs(dock: Any) -> list[str]:
    out = [dock.pc]
    with dock.store.transaction() as tx:
        for n, v in (("Weak", -1), ("Plain", 0)):
            eid = f"pc.{n.lower()}"
            tx.add(Event.of("entity_created", source="audit", entity=EntityRecord(
                id=eid, kind="pc", name=n, data={"attributes": dict.fromkeys(ATTRS, v)})))
            out.append(eid)
    return out


def _proposals(dock: Any, beat: Beat, verb: str) -> list[ProposedFrame]:
    rules = dock.rules
    attr = str((rules.basic_verbs.get(verb) or {}).get("attribute") or "wits")
    attr = attr if attr in rules.attributes else "wits"
    base: dict[str, Any] = {"anchor": verb_anchor(verb, rules), "attribute": attr, "stakes_source": "none",
                            "threatened_cost": {"menu_id": "cost.time"}}  # the dock clock listens to time
    opp = opposed_by(dock.state, beat, verb)
    if opp:
        sizes = ["R1", "R2"] if verb == "verb.talk" else [None]
        return [ProposedFrame(**base, obstacle={"kind": "opposed", "entity": opp[0],  # type: ignore[arg-type]
                                                "request_size": r}) for r in sizes]
    classes = [c for c, b in verb_classes(rules, verb).items() if b != "trivial"]
    obstacles = ([{"kind": "tier", "id": "obs", "obstacle_class": c} for c in classes] or
                 [{"kind": "tier", "id": "obs", "obstacle_class": "other", "tier": t}
                  for t in ("easy", "moderate", "hard")])
    hinder = [[], [dock.facts["fog"]], [dock.facts["fog"], dock.facts["lantern"]]]
    return [ProposedFrame(**{**base, "obstacle": ob, "snags": sn,  # type: ignore[arg-type]
                             "alternate_cost": {"menu_id": "cost.shortfall"} if len(sn) > 1 else None})
            for ob in obstacles for sn in hinder]


def audit() -> str:
    dock = build_dock(Path(tempfile.mkdtemp()))
    pcs = _pcs(dock)
    rolled = [g for g in rg.load() if g["labels"].get("necessity") == "uncertain_and_costly" and g["labels"]["verb"]]
    frames: list[Frame] = []
    refused = 0
    for g in rolled:
        verb = g["labels"]["verb"]
        person = verb in ("verb.talk", "verb.strike", "verb.grapple", "verb.force") and (
            g["labels"]["against_will"] or verb == "verb.talk")
        for pc in pcs:
            beat = Beat(id="beat.audit", actor=pc, intent=g["line"][:60], method=g["line"][:120], verb=verb,
                        target=dock.ferryman if person else None, against_will=g["labels"]["against_will"],
                        declared_seq=dock.state.last_seq)
            for p in _proposals(dock, beat, verb):
                f = frame_check(p, beat, state=dock.state, rules=dock.rules)
                if isinstance(f, Frame):
                    frames.append(f)
                else:
                    refused += 1
    harsh = [f for f in frames if f.stakes != "dire" and f.dc_source not in ("opposed", "effect") and not f.secret
             and f.odds.critical_failure > max(5, f.odds.success_or_better)]
    unlabelled = [f for f in harsh if not f.long_shot]
    spread = [f for f in frames if len({f.odds.success_or_better, *(a.chance for a in f.alternatives)}) >= 3]
    guard = sum(1 for f in frames if f.guard)

    def share(fs: list[Frame]) -> str:
        n = sum(1 for f in fs if len({f.odds.success_or_better, *(a.chance for a in f.alternatives)}) >= 3)
        return f"{n}/{len(fs)} ({100 * n / max(1, len(fs)):.1f}%)"

    wren = [f for f in frames if f.beat.actor == dock.pc]
    fights = [f for f in frames if f.beat.verb in ("verb.strike", "verb.grapple", "verb.force") and f.defender]
    return "\n".join([
        f"# Odds audit: {len(rolled)} rolled golden beats x {len(pcs)} PCs -> {len(frames)} frames "
        f"({refused} proposals refused by frame_check)",
        f"- non-Dire unopposed OFFERs with critical failure above success: {len(harsh)}, of them not labelled long "
        f"shot: {len(unlabelled)} (target 0)",
        f"- frames where the guard turned a Precision snag Protective: {guard}",
        f"- frames with >= 3 distinct odds (the frame and its alternatives): {len(spread)}/{len(frames)} "
        f"({100 * len(spread) / max(1, len(frames)):.1f}%); Wren (uneven attributes) {share(wren)}; attacks on a "
        f"person {share(fights)}; the -1 and +0 PCs have equal attributes, so only a sibling verb can differ",
    ])


if __name__ == "__main__":
    print(audit())
