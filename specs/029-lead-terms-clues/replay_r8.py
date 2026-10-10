"""Spec 029: the round-8 gates on scratch copies of the saves (read-only on the originals).

    py -3.12 specs/029-lead-terms-clues/replay_r8.py [--model haiku|offline] > replay_r8.txt

Each save is cut at the end of the turn before the one traced (spec 024's `_cut`), the seed's hook terms are written
(the saves predate them: `write_terms` on the rebuilt seed record, as a new game writes them), and the traced
message is put again through the new code:
1. talker turn.4: the gate log's last entry ("what does it say about the cart?", read with Letters, a no-roll Observe):
   round 8 stalled "waiting on your reading" and marked the question answered;
2. explorer turn.3: Betric (core holder of "who the challenger is") asked about the banners and "who the young man
   really is": round 8 judged only the first part (the cap), so the clue was dropped;
3. explorer turn.4: "what do I know about the Long Downs and the winter that brought the realm down?";
4. fighter: a new opening on the fighter's world: the challenger is the person on stage.
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

from engine.dm import testimony as tm  # noqa: E402
from engine.dm import world_step  # noqa: E402
from engine.dm.adjudication import AdjudicationRecord, BeatEntry, NpcActionEntry, PartEntry  # noqa: E402
from engine.dm.codex import what_you_know  # noqa: E402
from engine.dm.context import TurnContext  # noqa: E402
from engine.dm.incident import incident_line, stage_info  # noqa: E402
from engine.dm.roles.narrator import speaker_cards  # noqa: E402
from engine.dm.seed_flow import rebuild_seed  # noqa: E402
from engine.dm.session import opening  # noqa: E402
from engine.gen.case import cases  # noqa: E402
from engine.gen.hooks import write_terms  # noqa: E402
from engine.llm.offline import OfflineModel  # noqa: E402
from engine.retrieve.scene import written_words  # noqa: E402
from engine.store.db import Store  # noqa: E402
from engine.store.events import Event  # noqa: E402

SAVES = Path(r"C:\Users\Nelly\Documents\the-game\saves")
_spec = importlib.util.spec_from_file_location("r24", ROOT / "specs/024-texture-outcome/replay_r7.py")
assert _spec and _spec.loader
_r24 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_r24)


def _open(save: str, turn: str, tmp: Path) -> Store:
    tmp.mkdir(parents=True, exist_ok=True)
    return Store.open(_r24._cut(SAVES / f"playtest-20261010-{save}.db", turn, tmp))


def _npc(store: Store, name: str) -> str:
    return next(i for i, e in store.state.entities.items() if e.kind == "npc" and e.name.startswith(name))


def _terms(ctx: TurnContext) -> None:
    ws = rebuild_seed(ctx.state)
    assert ws is not None
    write_terms(ctx.need_tx(), ws.world().record)


def _card(st: Any, npc: str) -> list[str]:
    rec = AdjudicationRecord(pc="pc")
    rec.npc_actions.append(NpcActionEntry(npc=npc, action="answers", source="talk_outcome", source_ref="PR-12-10",
                                          tags=[f"ask:{npc}|what_happened|local_news"]))
    return [ln for ln in speaker_cards(st, rec) if "knows" in ln]


def talker(model: Any, tmp: Path, out: list[str]) -> None:
    store = _open("013206-talker", "turn.3", tmp)
    ctx = TurnContext.for_store(store, model=model)
    out.append("== talker turn.4: 'I look at the last entry at the foot of the page. Who signed it, and what does it say "
               "about the cart?' (a no-roll Observe with Letters)")
    with store.transaction() as tx:
        ctx.tx = tx
        _terms(ctx)
        st = tx.state
        pc = next(i for i, e in st.entities.items() if e.kind == "pc")
        log = next((i for i, e in st.entities.items() if e.name == "gate log" and e.data.get("document")), None)
        out.append(f"  the gate log (a document made with the cart lead): {log}; its text: {written_words(st, log)!r}")
        at = st.positions[log].location
        if st.positions[pc].location != at:
            tx.add(Event.of("position_set", source="replay", rule_id="10.1.1", entity=pc, location=at))
        old = next((i for i, e in st.entities.items() if e.name.lower() == "gate log" and i != log), None)
        parts = [PartEntry.model_validate({"text": "Who signed it,", "class": "FICTION_QUESTION",
                                           "question_kind": "who_is", "topic": "the signer of the last entry"}),
                 PartEntry.model_validate({"text": "and what does it say about the cart?", "class": "FICTION_QUESTION",
                                           "question_kind": "what_like", "topic": "what the last entry says"})]
        e = BeatEntry(restatement="I look at the last entry at the foot of the page.", targets=[old or log],
                      approach_words="lic.lang.letters", verb="verb.observe", reach="standard")
        verb = world_step.beat_verb(e)
        items = world_step._look(ctx, e, verb or "verb.observe", 2, pc, parts)
        out.append(f"  typed verb of a beat done with the licence: {verb}  (round 8: None, so nothing was delivered)")
        out += [f"  delivered: {a.line!r}" for a in items]
        rec = AdjudicationRecord(pc=pc, parts=parts)
        world_step._give(rec, e, None, items, parts, look=True)
        out.append(f"  GATE real words delivered: {any('cart' in a.line for a in items)}; "
                   f"parts marked answered only if a fact came: {[p.handled for p in parts]}")
        cap = next(i for i, x in st.entities.items() if x.kind == "npc" and "captain" in str(x.data.get("role")))
        out += ["  the captain's card: " + ln[:170] for ln in _card(st, cap)][:4]
        ctx.tx = None
    store.close()


def explorer(model: Any, tmp: Path, out: list[str]) -> None:
    store = _open("013246-explorer", "turn.2", tmp)
    ctx = TurnContext.for_store(store, model=model)
    out.append("== explorer turn.3: Betric asked 'what she meant about the two banners in the hall, and who the young man "
               "really is' (round 8: only the banners part reached the clue check; the clue was dropped by the cap)")
    with store.transaction() as tx:
        ctx.tx = tx
        _terms(ctx)
        st = tx.state
        pc = next(i for i, e in st.entities.items() if e.kind == "pc")
        betric = _npc(store, "Betric")
        case = next(c for c in cases(st).values() if c.get("trigger") == "incident")
        out.append(f"  Betric holds the core clue of '{case['nodes'][0]['fact'].split(':')[0]}': "
                   f"{any(p['holder'] == betric and p['access'] == 'core' for p in case['nodes'][0]['placements'])}")
        asked = [PartEntry.model_validate({"text": "ask what she meant about the two banners in the hall",
                                           "class": "SPEECH", "question_kind": "what_like",
                                           "topic": "the two banners hung in the hall"}),
                 PartEntry.model_validate({"text": "and who the young man really is", "class": "SPEECH",
                                           "question_kind": "who_is", "topic": "the young man at the hearth"})]
        rec = AdjudicationRecord(pc=pc, parts=asked)
        res = world_step._speech_answers(ctx, rec, [], asked, [betric], pc)
        out.append(f"  parts judged together; answers: {[(a[1], a[3]) for a in res[0]['answers']]}")
        out.append(f"  record.learned (the clue, a fact with no speaker): {rec.learned}")
        out.append("  NPC lines for this turn: " + str([(a.npc == betric, a.action[:60]) for a in rec.npc_actions]))
        out.append(f"  parts answered: {[p.handled for p in asked]}")
        found = cases(tx.state)[case["id"]]["nodes"][0].get("found")
        out.append(f"  GATE challenger clue delivered (not dropped by the cap): {bool(rec.learned) and bool(found)}")
        sub = case["solution"]["subject"]["id"]
        out.append(f"  the challenger the clue names is the case's subject {tx.state.entities[sub].name} "
                   f"({tx.state.entities[sub].data.get('role')})")
        ctx.tx = None
    store.close()
    store = _open("013246-explorer", "turn.3", tmp / "j")
    out.append("== explorer turn.4: 'What do I know about the Long Downs and the winter that brought the realm down?' "
               "(round 8: one line, nothing of what Betric said)")
    told = [r["words"][:80] for r in tm.records(store.state)]
    out.append(f"  said records in the save at turn.3: {told}")
    out.append(what_you_know(store.state, "the Long Downs and the winter that brought the realm down").text)
    out.append("  GATE includes what people said: " + str("told you" in what_you_know(
        store.state, "the Long Downs and the winter that brought the realm down").text))
    store.close()


def fighter(model: Any, tmp: Path, out: list[str]) -> None:
    store = _open("013226-fighter", "turn.1", tmp)
    ws = rebuild_seed(store.state)
    assert ws is not None
    world = ws.world()
    case0 = next(c for c in world.record["seed_cases"] if c["trigger"] == "incident")
    sub = case0["solution"]["subject"]
    out.append(f"== fighter: the duel. The sealed case's challenger is {sub['words']} ({sub['id']}); in the save the "
               "opening staged a different youth")
    store.close()
    from tests.fixtures.seeded import store_for_world

    fresh = store_for_world(tmp / "fresh", world)
    ctx = TurnContext.for_store(fresh, model=OfflineModel())
    resp = opening(ctx)
    st = fresh.state
    out.append(f"  stage: {stage_info(st)}; note: {incident_line(st)}")
    out.append(f"  scene cast present: {[st.entities[i].name for i in st.scene.cast_present]}")
    out.append(f"  GATE the challenger is the person on stage: {sub['id'] in st.scene.cast_present} "
               f"(opening narrated: {bool(resp.fiction)})")
    fresh.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="haiku")
    args = ap.parse_args()
    if args.model == "offline":
        model: Any = OfflineModel()
    else:
        from evals.playtest import ClaudeModel

        model = ClaudeModel(args.model)
    out: list[str] = [f"spec 029 round-8 gates (clue judgment on {args.model})"]
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        for f in (talker, explorer, fighter):
            f(model, Path(d) / f.__name__, out)
    print("\n".join(out))


if __name__ == "__main__":
    main()
