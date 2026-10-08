"""T5 WORLD of PR-12-1 (12.2.9): the world responds in a fixed order, each only from its closed source (01.11.3).

    world_step(ctx, record, beats=outcomes)      # fills record.npc_actions / omens / triggers / notes

1. Adversaries in conflict — Milestone 1 has no round-by-round conflict (coarse).
2. NPCs present: the default NPC layer (12.11.9, engine/dm/npc_layer.py): activities, the practice, each engaged
   NPC's response (a resolved Talk frame, a recorded refusal or want, the action row clamped to the practice).
3. Clocks that ticked this turn render their omens (INV-14).
4. Fired triggers in 12.2.3's order (owed blocks for the narration; a due lethal warning is delivered).
5. Time: each resolved beat's cost by the scene's mode (00.7.3) through `advance_time` (boundaries run).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from engine.audit import text as words
from engine.dm.adjudication import AdjudicationRecord, NpcActionEntry, OmenEntry
from engine.dm.answer import name as _name
from engine.dm.context import TurnContext
from engine.dm.npc_layer import ensure_activities, respond
from engine.resolve.pipeline import BeatOutcome
from engine.resolve.types import REACH_VALUE
from engine.retrieve.scene import READING, WRITTEN, cannot_read
from engine.retrieve.triggers import get_active_triggers
from engine.time.clock import beat_cost
from engine.time.scheduler import advance_time
from engine.world.social import record_knowledge

NPC_TABLE = "tbl.npc_action"
RESOLVED = ("resolved", "no_roll")


def happened_text(record: AdjudicationRecord) -> str:
    """THIS MESSAGE for the World role: what just happened this turn, in words."""
    lines = [f"player: {p.text} ({p.cls})" for p in record.parts]
    for b in record.beats:
        res = b.degree or b.gate_words or "no roll"
        lines.append(f"beat: {b.restatement} -> {res}" + (f"; target {', '.join(b.targets)}" if b.targets else ""))
    return "\n".join(lines)


def world_step(ctx: TurnContext, record: AdjudicationRecord, *, beats: Sequence[BeatOutcome],
               oof: list[dict[str, str]] | None = None) -> None:
    # rule: 12.2.9
    # coarse: PR-06-6
    answered = [x["knower"] for x in deliver_learning(ctx, record, beats) if x["speech"]]  # PR-12-10
    acted = foes_act(ctx, record, oof)
    ensure_activities(ctx, record)  # 12.11.9 step 1
    npcs_respond(ctx, record, beats, skip=[*acted, *answered], oof=oof)
    clock_omens(ctx, record)
    fired_triggers(ctx, record)
    beat_time(ctx, record, beats, fought=bool(acted))


def _foe_turn(ctx: TurnContext, record: AdjudicationRecord, foe: str, oof: list[dict[str, str]] | None) -> None:
    # rule: 06.9.2
    """One foe's beat (engine/resolve/conflict.py), its act for the narration and its RESULT line for the player."""
    from engine.dm.oof import changed_line
    from engine.resolve.conflict import foe_beat

    tx = ctx.need_tx()
    start = len(tx.events)
    said, res = foe_beat(ctx.time_ctx(), ctx.rng, foe, record.pc or "")
    record.npc_actions.append(NpcActionEntry(npc=foe, action=said, source="behavior", source_ref="beh.default_melee"))
    if res is not None and oof is not None:
        changed = changed_line(ctx.state, record.pc or "", tx.events[start:])
        oof.append({"kind": "RESULT", "text": f"[RESULT] {_name(ctx.state, foe)} strikes · hit"
                                              + (f" · {changed}" if changed else "")})
    if res is not None and res.threshold and oof is not None:  # rule: PR-07-5
        from engine.dm.turn import _env, _harm_followups

        env = _env(ctx)
        env.threshold_due.append(record.pc or "")
        _harm_followups(ctx, env, record, oof)


def foes_act(ctx: TurnContext, record: AdjudicationRecord, oof: list[dict[str, str]] | None = None) -> list[str]:
    # rule: 06.9.2
    """Step 1: in conflict mode each foe still able answers by its behavior row (06.9.4), then the end test
    (06.13.1). Returns the foes that acted (they draw no social table row this turn)."""
    from engine.resolve.conflict import able, check_end
    from engine.resolve.conflict import record as conflict

    rec = conflict(ctx.state)
    if not rec or not record.pc or ctx.state.open_pause() is not None:
        return []
    acted = []
    for foe in rec.get("foes", []):
        if able(ctx.state, foe) and conflict(ctx.state):
            _foe_turn(ctx, record, foe, oof)
            acted.append(foe)
    check_end(ctx.time_ctx(), record.pc)
    return acted


def npcs_respond(ctx: TurnContext, record: AdjudicationRecord, beats: Sequence[BeatOutcome], *,
                 skip: Sequence[str] = (), oof: list[dict[str, str]] | None = None) -> None:
    # rule: 12.2.9
    """Step 2: only when something happened that an NPC present could respond to (a beat or speech): the default
    NPC layer decides (12.11.9, engine/dm/npc_layer.py); the World role is asked only about candidate motives."""
    respond(ctx, record, beats, skip=skip, oof=oof)


LEARN_VERBS = {"verb.talk": "told", "verb.observe": "witnessed", "verb.recall": "recalled"}
PEOPLE = ("npc", "companion", "adversary")
NONE = "none"


def _learnable(state: Any, f: Any, pc: str) -> bool:
    return (isinstance(f.value, str | bool | int | float) and f.visibility != "sealed" and f.id not in state.seals
            and f.subject not in state.seals and f.subject != pc and f.id not in state.knowledge.get(pc, {})
            and f.predicate != "name" and not f.predicate.endswith((".but", ".and"))
            and not f.predicate.startswith(("knows_", "points_to.")))


def _ok(b: BeatOutcome) -> bool:
    e = b.entry
    return b.status == "no_roll" or (b.status == "resolved" and (e.degree in ("success", "critical_success")
                                                                 or e.success_at_cost))


def deliver_learning(ctx: TurnContext, record: AdjudicationRecord, beats: Sequence[BeatOutcome]
                     ) -> list[dict[str, Any]]:
    # rule: PR-12-10
    # rule: 12.10.5
    """A successful Talk that asks (a part with a `question_kind`), Observe or Recall is answered by the answer ladder
    (engine/dm/answer.py) before the draft: of N questions `deliver_count(N, reach)` (T-01-6), each at the ladder depth
    of the delivered reach (a no-roll beat runs at Standard), plus a volunteered extra at Great; each answer is a
    `BeatEntry.learned` line (a record line with a handle). A plain SPEECH question with no Talk beat is answered at
    Standard as the addressed NPC's act. Never empty: an answer is a fact, a placement, a record answer or a
    pointer (DL-12-44). A Talk that asks nothing is a request (T-15-5 "yes, as asked"), not a learning beat.
    Returns one summary per learning beat ({beat, verb, knower, speech, answers: [(fact id, pointer, line)]})."""
    from engine.dm import answer as ans
    from engine.dm.npc_layer import addressed
    from engine.dm.roles.world import present_npcs

    st = ctx.state
    pc = record.pc
    if pc is None:
        return []
    asked = [p for p in record.parts if p.question_kind not in (None, NONE) and p.cls in ("DECLARATION", "SPEECH")]
    present = present_npcs(st)
    out: list[dict[str, Any]] = []
    for b in beats:
        e = b.entry
        verb = next((v for v in LEARN_VERBS if v in (e.approach_words or "")), None)
        if b.status == "resolved" and not _ok(b):
            _stalled(st, record, e, b.frame_id)
        if verb is None or not _ok(b):
            continue
        reach = 2 if b.status == "no_roll" else REACH_VALUE.get(e.reach or "standard", 2)
        rungs = ans.rungs_for(ctx.rules, reach)
        knower = None
        if verb == "verb.talk":
            if not asked or (e.targets and e.targets[0] in st.entities and st.entities[e.targets[0]].kind not in PEOPLE):
                continue  # a request (T-15-5 "yes, as asked"), or words to a thing: no one to answer
            people = [t for t in e.targets if t in st.entities and st.entities[t].kind in PEOPLE]
            knower = people[0] if people else next(iter(addressed(st, record, present)), None) or (
                present[0] if len(present) == 1 else None)
            if knower is None:  # asked of no one here: who would know (never empty, DL-12-44)
                items = _look(ctx, e, verb, reach, pc, asked)
            else:
                items = [ans.ask(ctx, knower, p.question_kind, p.topic, p.text, rungs, pc=pc)
                         for p in asked[:ans.deliver_count(len(asked), reach)]]
                extra = ans.volunteer(ctx, knower, pc) if "volunteer" in rungs else None
                items += [extra] if extra else []
        else:
            items = _look(ctx, e, verb, reach, pc, asked)
        e.learned += [a.line for a in items]
        out.append({"beat": e.beat_id, "verb": verb, "knower": knower, "speech": False,
                    "answers": [(a.fact_id, a.pointer, a.line) for a in items]})
    if not any("verb.talk" in (b.entry.approach_words or "") for b in beats):
        out += _speech_answers(ctx, record, [p for p in asked if p.cls == "SPEECH"], present, pc)
    return out


def _speech_answers(ctx: TurnContext, record: AdjudicationRecord, speech: list[Any], present: list[str],
                    pc: str) -> list[dict[str, Any]]:  # rule: PR-12-10
    """A plain SPEECH question (no Talk beat, 15.3.10) to a present NPC: answered at Standard, as their act."""
    from engine.dm import answer as ans
    from engine.dm.npc_layer import addressed

    if not speech:
        return []
    out = []
    for npc in addressed(ctx.state, record, present)[:1]:
        rungs = ans.rungs_for(ctx.rules, 2)
        items = [ans.ask(ctx, npc, p.question_kind, p.topic, p.text, rungs, pc=pc)
                 for p in speech[:ans.deliver_count(len(speech), 2)]]
        for a in items:
            record.npc_actions.append(NpcActionEntry(npc=npc, action=a.said, source="talk_outcome",
                                                     source_ref="PR-12-10"))
        out.append({"beat": None, "verb": "speech", "knower": npc, "speech": True,
                    "answers": [(a.fact_id, a.pointer, a.line) for a in items]})
    return out


def _look(ctx: TurnContext, e: Any, verb: str, reach: int, pc: str, asked: list[Any]) -> list[Any]:
    # rule: PR-12-10
    # rule: 15.9.5
    """Observe or Recall: a placement held here (a search at a holder place, object or document: the node is found,
    15.9.5); else what the store holds here, ranked by the words the beat shares with it, `deliver_count`'s many
    (Observe and Recall draw on what is here); else the place's seeded furniture (Observe); else who would know."""
    from engine.audit.fallback import fact_sentence
    from engine.dm import answer as ans
    from engine.gen.case import cases

    st = ctx.state
    place = st.positions[pc].location if pc in st.positions else st.scene.place_id if st.scene else None
    here = {*(st.scene.cast_present if st.scene else ()), place, *e.targets, "world"} | {
        i for i, p in st.positions.items() if place and p.location == place}
    if verb == "verb.observe":
        for case in cases(st).values():
            node = ans.open_node(case, False)
            p = next((p for p in node["placements"] if not node.get("found") and p["method"] == "search"
                      and p.get("status") not in ("found", "lost")
                      and (p["holder"] in here or (p["holder"] not in st.entities and p.get("at") == place))), None)
            if p is not None:
                how = "read" if p["holder_kind"] == "document" else "witnessed"
                fid = ans.deliver_node(ctx, case, node, p["id"], pc, how)
                return [ans.Answer("", f"You make out {node['fact']}", fid)]
    pool = {f.id for f in st.facts.values() if f.subject in here}
    names = " ".join(st.entities[i].name for i in [e.actor, *e.targets] if i and i in st.entities)
    said = " ".join([e.restatement, *(p.text for p in asked)])
    want = words.content(said) - words.content(names)
    ranked = sorted(((len(want & words.content(ans.fact_words(st, st.facts[fid]))), fid) for fid in pool
                     if fid in st.facts and _learnable(st, st.facts[fid], pc)
                     and fact_sentence(st, st.facts[fid])), reverse=True)  # only what can be told plainly
    ranked = [fid for score, fid in ranked if score][:5]  # resolution.yaml delivery_rules.max_items
    written = next((f for k in WRITTEN if e.targets and (f := st.current_fact_id(e.targets[0], k))), None)
    if written in pool and READING.search(e.restatement) and not cannot_read(st, pc, e.targets[0]):
        ranked = [written] + [f for f in ranked if f != written][:4]  # reading it delivers its words first (P-110)
    out = []
    for fid in ranked[:ans.deliver_count(len(ranked), reach)]:
        record_knowledge(ctx.time_ctx(), pc, fid, LEARN_VERBS[verb])
        out.append(ans.Answer("", fact_sentence(st, st.facts[fid]), fid))
    if out:
        return out
    if verb == "verb.observe" and place in st.entities:  # the place's seeded furniture (12.16.9): what is here
        for i, item in enumerate(st.entities[place].data.get("furniture") or []):
            pred = f"furniture.{i}"
            cur = st.current_fact_id(place, pred)
            if cur is None or cur not in st.knowledge.get(pc, {}):
                fid = cur or ans._write(ctx, place, pred, str(item), rule="12.16.9", source="data")
                record_knowledge(ctx.time_ctx(), pc, fid, "witnessed")
                return [ans.Answer("", f"You make out {item}", fid)]
    q = asked[0] if asked else None
    topic, about = ans.topic_of(st, q.topic if q else None, said, pc)
    about = about or next((t for t in e.targets if t in st.entities), None)
    fid, ref = ans.point(ctx, pc, topic, pc, about=about)
    what = f"about {ans.name(st, about) if about else topic.replace('_', ' ')}"
    head = {"verb.recall": "You recall nothing more", "verb.talk": "No one here can tell you more"}.get(
        verb, "You find nothing more here")
    who = ans.name(st, ref) if ref in st.entities and st.entities[ref].kind in PEOPLE else \
        f"someone at {ans.name(st, ref)}"
    return [ans.Answer("", f"{head} {what}, but {who} would know", fid, ref)]


STALLED = "cannot make out: "
_FAILED = ("failure", "critical_failure")


def _looked(f: dict[str, Any]) -> bool:
    """A frame that tried to learn something: a hidden roll, or an Observe or Recall."""
    return bool(f.get("secret")) or (f.get("gate") or {}).get("verb") in ("verb.observe", "verb.recall")


def _stalled(st: Any, record: AdjudicationRecord, e: Any, frame_id: str | None) -> None:
    # rule: 12.14.8
    """P-086: the second failed attempt in this scene to make out the same target says so plainly and points to
    another way, instead of a third vague glimpse (failure is the world's answer, not a loop)."""
    fs = st.frames.get(frame_id) if frame_id else None
    if fs is None or not e.targets or e.targets[0] not in st.entities or not _looked(fs.frame):
        return
    target = e.targets[0]
    failed = [x for x in st.frames.values() if x.resolved and x.resolved.get("degree") in _FAILED
              and (x.frame.get("beat") or {}).get("target") == target and _looked(x.frame)]
    if len(failed) >= 2:
        # said plainly, in player-facing words (the plain fallback prints it as is)
        record.notes.append(f"{STALLED}You cannot make out {_name(st, target)} from here, not this way. Another "
                            "approach might: ask someone who knows, get it out into the open, or come back with "
                            "better means.")


def clock_omens(ctx: TurnContext, record: AdjudicationRecord) -> None:  # rule: 00.8.4
    """Step 3: every clock that ticked this turn, with the omen the tick selected (INV-14)."""
    st = ctx.state
    for ev in ctx.need_tx().events:
        if ev.type != "clock_ticked":
            continue
        p: Any = ev.payload
        clock = st.clocks.get(p.clock_id)
        omen = ""
        if clock is not None and p.omen_key:
            stage, _, idx = str(p.omen_key).partition(":")
            texts = clock.omens.get(stage) or []
            if idx.isdigit() and int(idx) < len(texts):
                omen = texts[int(idx)]
        record.omens.append(OmenEntry(clock_id=p.clock_id, stage=p.stage, omen=omen, completed=p.completed))


def fired_triggers(ctx: TurnContext, record: AdjudicationRecord) -> None:  # rule: 12.2.3
    """Step 4: the raised triggers, in handling order, for the narration's owed blocks; a lethal warning that a
    boundary raised (`h.07.lethal_scan`) and no beat delivered is delivered now (PR-07-4)."""
    from engine.harm.ctx import HarmCtx
    from engine.harm.lethal import LethalTrigger, active_triggers, record_warning, warning_block

    st = ctx.state
    for t in active_triggers(st):
        trig = LethalTrigger(pc=str(t.get("pc")), source=str(t.get("source")), cause=str(t.get("cause")),
                             detail=dict(t.get("detail") or {}))
        if trig.pc not in st.entities:
            continue
        name = st.entities[trig.source].name if trig.source in st.entities else trig.source
        fate = st.quantities.get(trig.pc, {}).get("fate")
        record.notes.append(warning_block(ctx.rules, trig, source_name=name, fate=fate.current if fate else 0,
                                          yield_text="give up on terms they will take",
                                          retreat_text="break away and run"))
        ctx.need_tx().add_all(record_warning(HarmCtx(state=st, mint=ctx.mint, rules=ctx.rules, rng=ctx.rng), trig,
                                             sign=f"{name} could kill you"))
        record.triggers.append("trg.lethal_warning")
    for t in get_active_triggers(ctx.state, ctx.rules):
        if t.id not in record.triggers:
            record.triggers.append(t.id)


def beat_time(ctx: TurnContext, record: AdjudicationRecord, beats: Sequence[BeatOutcome], *,
              fought: bool = False) -> None:
    # rule: 00.7.3
    """Step 5: each resolved beat costs its mode's time; boundaries crossed run their handlers (INV-15). In
    conflict mode a beat costs nothing and the turn (the PC, then each foe) is one round (06.2.3)."""
    from engine.resolve.pipeline import _mode

    st = ctx.state
    if _mode(st) == "conflict":
        if fought or any(b.status in RESOLVED for b in beats):
            # ponytail: one PC turn + the foes' answers = one round; no tempo order (06.2.2) yet
            advance_time(ctx.time_ctx(), 1, "round", "round end (06.2.3)")
        return
    mode = st.scene.mode if st.scene else str(st.time.mode)
    for b in beats:
        if b.status not in RESOLVED:
            continue
        amount, unit = beat_cost(mode, significant=True)
        if amount <= 0:
            continue
        res = advance_time(ctx.time_ctx(), amount, unit, f"beat {b.entry.beat_id}")
        if res.interrupt:  # 00.7.8: halt and frame a new moment
            record.notes.append(f"interrupted: {res.interrupt}")
            break
