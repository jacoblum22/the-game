"""Spec 025: the round-7 gates on scratch copies of the saves (read-only on the originals).

    py -3.12 specs/025-hooks-clues-willingness/replay_r7.py [--model haiku|offline] > replay_r7.txt

Each save is cut at the end of the turn before the one traced (spec 024's `_cut`), the seed's hook terms are written
(the saves predate them: `write_terms` on the rebuilt seed record, as a new game writes them), and the traced
question is put again through the new `answer.ask` (the clue judgment on `--model`), or the Director's cast:
1. fighter turn.2-4: Magby's speaker card (the offer's pay and place) before and after;
2. explorer turn.2: Branine asked about the refugees (round 7: not routed); turn.8: Roswen's answer and its pointer
   (round 7: the narrator's redirect to Morga, the only other person present); the refugees cast by description;
3. talker turn.9: the sellsword asked "Have you signed with Morri's Wolves" (round 7: a misrouted case pointer).
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.dm import answer as ans  # noqa: E402
from engine.dm.adjudication import AdjudicationRecord, NpcActionEntry  # noqa: E402
from engine.dm.context import TurnContext  # noqa: E402
from engine.dm.roles.director import DirectorDecision, NextScene, frame_scene  # noqa: E402
from engine.dm.roles.narrator import speaker_cards  # noqa: E402
from engine.dm.seed_flow import rebuild_seed  # noqa: E402
from engine.gen.hooks import write_terms  # noqa: E402
from engine.llm.offline import OfflineModel  # noqa: E402
from engine.store.db import Store  # noqa: E402

SAVES = Path(r"C:\Users\Nelly\Documents\the-game\saves")
_spec = importlib.util.spec_from_file_location("r24", ROOT / "specs/024-texture-outcome/replay_r7.py")
assert _spec and _spec.loader
_r24 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_r24)


def _open(save: str, turn: str, tmp: Path) -> Store:
    tmp.mkdir(parents=True, exist_ok=True)
    return Store.open(_r24._cut(SAVES / f"playtest-20261009-{save}.db", turn, tmp))


def _ctx(store: Store, model: Any) -> TurnContext:
    return TurnContext.for_store(store, model=model)


def _npc(store: Store, name: str) -> str:
    return next(i for i, e in store.state.entities.items() if e.kind == "npc" and e.name.startswith(name))


def _terms(ctx: TurnContext) -> None:
    ws = rebuild_seed(ctx.state)
    assert ws is not None
    write_terms(ctx.need_tx(), ws.world().record)


def _card(st: Any, npc: str, key: str) -> list[str]:
    rec = AdjudicationRecord()
    rec.npc_actions.append(NpcActionEntry(npc=npc, action="answers", source="talk_outcome", source_ref="PR-12-10",
                                          tags=[f"ask:{key}"]))
    return [ln for ln in speaker_cards(st, rec) if "knows" in ln or "others have said" in ln]


def _ask(ctx: TurnContext, npc: str, kind: str, topic: str | None, text: str) -> ans.Answer:
    from engine.world.common import active_pc

    return ans.ask(ctx, npc, kind, topic, text, pc=str(active_pc(ctx.state)))


def fighter(model: Any, tmp: Path, out: list[str]) -> None:
    store = _open("160622-fighter", "turn.1", tmp)
    ctx = _ctx(store, model)
    magby = _npc(store, "Magby")
    key = f"{magby}|what_like|factions"
    out.append("== fighter turn.2-4: Magby (the offer's reporter, core holder of 'who makes the offer')")
    out += ["  before: " + ln for ln in _card(store.state, magby, key)]
    with store.transaction() as tx:
        ctx.tx = tx
        _terms(ctx)
        after = _card(tx.state, magby, key)
        out += ["  after:  " + ln for ln in after]
        for q, kind in (("Where's the danger worst?", "where_is"), ("What does the job pay?", "what_like"),
                        ("Who is really making this offer?", "who_knows")):
            a = _ask(ctx, magby, kind, None, q)
            out.append(f"  ask {q!r}: {a.line}")
        ctx.tx = None
    out.append(f"  GATE pay and place on Magby's card: {any('pay:' in x and 'where:' in x for x in after)}")
    store.close()


def explorer(model: Any, tmp: Path, out: list[str]) -> None:
    store = _open("160642-explorer", "turn.1", tmp)
    ctx = _ctx(store, model)
    bran = _npc(store, "Branine")
    out.append("== explorer turn.2: Branine asked about the refugees (round 7: not routed, no clue)")
    with store.transaction() as tx:
        ctx.tx = tx
        _terms(ctx)
        a = _ask(ctx, bran, "where_is", None, "ask Branine what he knows about the refugees and where they are now")
        out.append(f"  {a.line} | fact {a.fact_id} | GATE clue delivered: {a.fact_id is not None}")
        ctx.tx = None
    store.close()
    store = _open("160642-explorer", "turn.7", tmp / "e8")
    ctx = _ctx(store, model)
    roswen, morga = _npc(store, "Roswen"), _npc(store, "Morga")
    out.append("== explorer turn.8: Roswen refused (round 7: redirect to Morga, the loop)")
    with store.transaction() as tx:
        ctx.tx = tx
        _terms(ctx)
        ans._hold(ctx, roswen, "unwilling", "unfriendly toward you")  # round 7's dice: Unfriendly, d10=4
        a = _ask(ctx, roswen, "what_happened", None, "I ask Roswen what he's heard about the road and the refugees, "
                                                      "and whether he saw any of them himself.")
        who = tx.state.entities[a.pointer].name if a.pointer in tx.state.entities else a.pointer
        out.append(f"  {a.line}")
        out.append(f"  pointer: {who} | GATE never Morga or Roswen: {a.pointer not in (morga, roswen)}")
        group = next((i for i, e in tx.state.entities.items() if e.data.get("group")), None)
        here = tx.state.positions[next(i for i, e in tx.state.entities.items() if e.kind == "pc")].location
        out.append(f"  the refugees exist: {group} at {tx.state.positions[group].location if group else None}")
        frame_scene(ctx, DirectorDecision(next_scene=NextScene(place=here, agenda="Is the refugees' story true?",
                                                               cast=["new_npc"], cast_described=["the refugees"])),
                    reason="replay")
        present = list(tx.state.scene.cast_present) if tx.state.scene else []
        out.append(f"  Director cast_described ['the refugees'] -> present: {[tx.state.entities[i].name for i in present]}"
                   f" | GATE refugees present: {group in present}")
        ctx.tx = None
    store.close()


def talker(model: Any, tmp: Path, out: list[str]) -> None:
    store = _open("160602-talker", "turn.8", tmp)
    ctx = _ctx(store, model)
    sell = _npc(store, "Dilie")
    out.append("== talker turn.9: the sellsword asked about Morri's Wolves (round 7: 'does not know what the omen "
               "shows, but Kerric Hartsmith would')")
    with store.transaction() as tx:
        ctx.tx = tx
        _terms(ctx)
        a = _ask(ctx, sell, "what_happened", None, "Have you signed with Morri's Wolves, or thought about it?")
        out.append(f"  {a.line}")
        out.append(f"  GATE no case pointer: {'does not know' not in a.line and a.fact_id is None}")
        ctx.tx = None
    store.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="haiku")
    args = ap.parse_args()
    if args.model == "offline":
        model: Any = OfflineModel()
    else:
        from evals.playtest import ClaudeModel

        model = ClaudeModel(args.model)
    out: list[str] = [f"spec 025 round-7 gates (clue judgment on {args.model})"]
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        for f in (fighter, explorer, talker):
            f(model, Path(d) / f.__name__, out)
    print("\n".join(out))


if __name__ == "__main__":
    main()
