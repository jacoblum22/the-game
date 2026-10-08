"""The default NPC layer (12.11.9; DL-12-43): code decides what each present NPC is doing and how an engaged one
responds; the narrator voices it.

    ensure_activities(ctx, record)          # step 1: every present NPC's activity this scene (T1c), as record lines
    respond(ctx, record, beats, skip=foes)  # steps 2-5: the practice, each engaged NPC's response, as record lines

Every response is an `NpcActionEntry` (a must-name record line with a handle, engine/dm/handles.py), so the
narration cites it instead of inventing an act. Draws go through the game's RNG, so a seeded replay reproduces
them. The World role is asked only when an NPC's recorded motive may match the event (12.2.9's `[J:flag]`).
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from engine.audit import text as tx
from engine.dm.adjudication import AdjudicationRecord, NpcActionEntry
from engine.dm.context import TurnContext

ACTIVITY = "activity"  # the detail slot (00.6.6a): the NPC's activity, a scene slot cleared at scene end
SPOKEN = "npc.spoken"  # meta {scene, npcs}: who the PC has spoken with this scene (greeting vs conversation)
NPC_TABLE = "tbl.npc_action"
WATCHES = ("morning", "afternoon", "evening", "night")
REFUSING_ROWS = (1, 2, 3, 5)  # escalates, ends the exchange, hinders, carries on: what was asked is not given
_FIGHT_VERBS = ("verb.strike", "verb.grapple", "verb.force")
_TRADE = re.compile(r"\b(buy|buys|sell|sells|price|prices|cost|costs|coin|coins|pay|pays|trade|trades|wares|goods|"
                    r"haggle|bargain|silver|gold|copper|deal)\b", re.I)


# ------------------------------------------------------------------------------------------- step 1: activity


def current_activity(state: Any, npc: str) -> str | None:  # rule: 12.11.9
    """The NPC's activity this scene, or None (the `activity` detail; cleared at scene end, 12.4.8 step 8)."""
    from engine.store.details import current

    f = current(state, npc, ACTIVITY) if state.scene is not None else None
    return str(f.value) if f is not None and f.value else None


def role_key(rules: Any, role: Any) -> str:  # rule: 12.11.9
    """`tbl.npc_activity.by_role`'s key for a role: the role itself, else the first word of the `tbl.npc_role` row
    that names it ("smith" → crafter), else `other`."""
    cells = rules.table("tbl.npc_activity")["by_role"]
    words = re.findall(r"[a-z]+", str(role or "").lower())
    if not words:
        return "other"
    if " ".join(words) in cells:
        return " ".join(words)
    if words[0] in cells:
        return words[0]
    for row in rules.table("tbl.npc_role")["results"]:
        row_words = re.findall(r"[a-z]+", str(row["result"]).lower())
        if row_words and row_words[0] in cells and any(w in row_words for w in words):
            return row_words[0]
    return "other"


def ensure_activities(ctx: TurnContext, record: AdjudicationRecord) -> None:  # rule: 12.11.9
    """Step 1: each present NPC without an activity this scene gets one rolled on `tbl.npc_activity` (role × watch,
    d6 pairs) and written as its `activity` detail (a scene slot, 00.6.6a); then the record's scene-state lines are
    rebuilt for whoever is present now (T-12-18: activity, posture, hold, manner, band to the PC), so a person who
    left the scene this turn drops out."""
    from engine.dm.roles.world import present_npcs
    from engine.dm.scene_state import lines
    from engine.store.details import write_detail
    from engine.world.social import npc_field

    tx_ = ctx.need_tx()
    st = tx_.state
    if st.scene is None:
        record.activities = []
        return
    start = len(tx_.events)
    cells = ctx.rules.table("tbl.npc_activity")["by_role"]
    present = present_npcs(st)
    for npc in present:
        if current_activity(tx_.state, npc) is None:
            key = role_key(ctx.rules, npc_field(st, npc, "role"))
            options = list(cells[key][WATCHES[st.time.now.watch % 4]])
            roll = ctx.rng.draw(6, f"activity of {npc} (12.11.9)", stream="npc", table_id="tbl.npc_activity")
            act = str(options[min((roll - 1) // 2, len(options) - 1)])
            tx_.add_all(write_detail(tx_.state, tx_.mint, npc, ACTIVITY, act, source="generation", because="12.11.9",
                                     rules=ctx.rules, visibility="shown").events)
    record.add_writes(tx_.events[start:])
    record.activities = lines(tx_.state, record.pc, present)


# ------------------------------------------------------------------------------------------- step 2: practice


def _names(state: Any, npc: str) -> list[str]:
    from engine.store.views import unnamed_label

    e = state.entities[npc]
    out = [e.name, unnamed_label(e), *(a for a in e.data.get("aliases") or [] if isinstance(a, str))]
    if e.name and len(e.name.split()) > 1:
        out.append(e.name.split()[0])
    role = re.findall(r"[a-z]+", str(e.data.get("role") or "").split(" or ")[0].lower())
    if role:
        out.append(role[-1])  # "the attendant" for a shrine attendant. ponytail: the head noun of the role
    return [n for n in out if n and len(n) > 2]


def _named(state: Any, npc: str, text: str) -> bool:
    return any(tx.has_phrase(text, n) for n in _names(state, npc))


def addressed(state: Any, record: AdjudicationRecord, present: Sequence[str]) -> list[str]:  # rule: 12.11.9
    """NPCs the PC addressed this turn: a talk beat on them, a spoken or asked part naming them, or the one NPC here
    when the PC speaks to no one by name ("talk with no target speaks to the only NPC", P-056)."""
    out = [t for b in record.beats if (b.verb == "verb.talk" or "talk" in (b.approach_words or ""))
           for t in b.targets if t in present]
    spoken = [p.text for p in record.parts if p.cls in ("SPEECH", "FICTION_QUESTION", "DECLARATION")]
    out += [n for n in present for t in spoken if _named(state, n, t)]
    if not out and present and any(p.cls == "SPEECH" for p in record.parts):
        # spoken to no one by name: the one last spoken with this scene, else the first present (cast order).
        # ponytail: nearness and who would answer are not modelled
        last = [n for n in spoken_with(state) if n in present]
        out.append(last[-1] if last else present[0])
    return list(dict.fromkeys(out))


def spoken_with(state: Any) -> list[str]:
    v = state.meta.get(SPOKEN) or {}
    sc = state.scene
    return list(v.get("npcs") or []) if sc is not None and v.get("scene") == sc.scene_id else []


def practice_for(state: Any, record: AdjudicationRecord, npc: str | None, addressed_ids: Sequence[str]) -> str:
    # rule: 12.11.9
    """The first `tbl.npc_practice` row (select_order) whose test holds this turn; greeting and conversation are
    per NPC (no exchange with them yet this scene, or one already)."""
    from engine.resolve.pipeline import _mode

    if _mode(state) == "conflict" or any(b.verb in _FIGHT_VERBS and any(
            t in state.entities and state.entities[t].kind in ("npc", "companion", "adversary") for t in b.targets)
            for b in record.beats):
        return "fight"
    talk = " ".join([p.text for p in record.parts if p.cls in ("SPEECH", "DECLARATION", "FICTION_QUESTION")]
                    + [b.restatement for b in record.beats if b.verb == "verb.talk"])
    if npc in addressed_ids and _TRADE.search(talk):
        return "trade"
    if npc in addressed_ids:
        return "conversation" if npc in spoken_with(state) else "greeting"
    public = any(n.startswith(("a lead", "the inciting incident")) for n in record.notes)
    if public and not addressed_ids:
        return "crowd"
    return "work"


def clamp_row(row: int, allowed: Sequence[int], hostile: bool) -> int:  # rule: 12.11.9
    """A rolled `tbl.npc_action` row the practice does not allow moves to the nearest row it does, toward row 5 on
    a tie; row 1 is legal in every practice for an NPC at Hostile standing."""
    rows: list[int] = sorted({*allowed, *([1] if hostile else [])})
    if row in rows:
        return row
    return min(rows, key=lambda r: (abs(r - row), abs(r - 5)))


# ------------------------------------------------------------------------------------------- steps 3-5: response


def _event_words(record: AdjudicationRecord) -> str:
    return " ".join([p.text for p in record.parts] + [b.restatement for b in record.beats])


def candidates(state: Any, npc: str, record: AdjudicationRecord) -> dict[str, str]:  # rule: 12.2.9
    """The NPC's recorded wants and refusals, best word overlap with the event first. Wants and refusals carry no
    tags, so whether one is engaged is the World role's `[J:flag]`; the order is only the fallback's pick when
    `world_judge` is off. ponytail: content-word overlap."""
    from engine.dm.roles.world import npc_motives

    said = tx.content(_event_words(record))
    motives = npc_motives(state, npc)
    return dict(sorted(motives.items(), key=lambda kv: -len(tx.content(kv[1]) & said)))


def _voice(ctx: TurnContext, npc: str) -> str:  # rule: 12.11.9
    """The NPC's voice register and habit; a walk-on's are rolled on first answer (12.11.1's tables)."""
    from engine.world.common import fact
    from engine.world.social import npc_field

    v = npc_field(ctx.state, npc, "voice")
    if not isinstance(v, dict) or not v.get("register"):
        tbl = ctx.rules.table
        reg = tbl("tbl.npc_voice_register")["results"]
        hab = tbl("tbl.npc_voice_habit")["results"]
        r = ctx.rng.draw(len(reg), f"voice register of {npc} (12.11.9)", stream="npc", table_id="tbl.npc_voice_register")
        h = ctx.rng.draw(len(hab), f"voice habit of {npc} (12.11.9)", stream="npc", table_id="tbl.npc_voice_habit")
        v = {"register": str(reg[r - 1]["result"]), "habit": str(hab[h - 1]["result"])}
        tx_ = ctx.need_tx()
        tx_.add(fact(tx_, npc, "voice", v, rule_id="12.11.9", visibility="background"))
    return f"{v.get('register')}, {v.get('habit')}"


REACH_YES = {"limited": "grants a lesser version of what you ask", "standard": "agrees to what you ask",
             "great": "agrees to what you ask, and more", "exceptional": "agrees to what you ask, and more"}


def talk_outcome(e: Any) -> str:  # rule: T-15-5
    """A successful Talk's act: the question answered (its PR-12-10 lines are the record's), else T-15-5's yes by the
    delivered reach (a certain beat, no roll, is a yes as asked)."""
    if e.learned:
        return "answers what you asked"
    return REACH_YES.get(e.reach or "standard", REACH_YES["standard"])


def voiced_refusal(ctx: TurnContext, npc: str, reason: str) -> str:  # rule: 12.11.9
    """Step 4: a refusal spoken in the NPC's own voice: the reason said through their register and habit."""
    return f"refuses, in their own voice ({_voice(ctx, npc)}): {reason}"


def _judge_motive(ctx: TurnContext, npc: str, cands: dict[str, str], happened: str) -> tuple[str | None, list[str]]:
    """(want/refusal id engaged or None, tags): the World role over the candidates only; without it, the best
    overlap."""
    if (ctx.config or {}).get("world_judge", True):
        from engine.dm.roles.world import npc_responses

        for r in npc_responses(ctx, happened, only={npc: list(cands)}):
            if r.npc == npc:
                return r.refusal_engaged or r.want_engaged, r.tags
        return None, []
    said = tx.content(happened)
    return next((k for k, v in cands.items() if tx.content(v) & said), None), []


def respond(ctx: TurnContext, record: AdjudicationRecord, beats: Sequence[Any], *, skip: Sequence[str] = (),
            oof: list[dict[str, str]] | None = None) -> None:
    # rule: 12.11.9
    # rule: 12.2.9
    """Steps 2-5 for every engaged or addressed present NPC (addressed, or a resolved beat's target): (a) a resolved
    Talk frame's outcome; (b) a recorded refusal or want the World role finds engaged; (c) `tbl.npc_action` by
    standing, clamped to the practice's rows. An addressed NPC always answers: a refusing source is voiced."""
    from engine.dm.roles.world import npc_motives, present_npcs
    from engine.dm.scene_state import response_values, write
    from engine.dm.world_step import RESOLVED, _foe_turn, happened_text
    from engine.resolve.tables import roll_table
    from engine.world.common import meta
    from engine.world.social import first_interaction, standing

    if not beats and not any(p.cls in ("SPEECH", "DECLARATION", "FICTION_QUESTION") for p in record.parts):
        return
    tx_ = ctx.need_tx()
    st = ctx.state
    present = present_npcs(st)
    spoke_to = addressed(st, record, present)
    talks = {t: b for b in beats if b.status in RESOLVED and "talk" in (b.entry.approach_words or "")
             for t in (b.entry.targets or (present if len(present) == 1 else []))}
    unresolved = {t for b in beats if b.status not in RESOLVED for t in b.entry.targets}
    targets = [t for b in beats if b.status in RESOLVED for t in b.entry.targets if t in present]
    engaged = [n for n in dict.fromkeys([*talks, *spoke_to, *targets])
               if n in st.entities and st.entities[n].kind in ("npc", "companion", "adversary")]
    practice_rows = {r["range"]: r for r in ctx.rules.table("tbl.npc_practice")["results"]}
    # the PC asked for something (a question, a request, a Talk): a refusing source is then said as a refusal
    asked = any(b.verb == "verb.talk" for b in record.beats) or any(
        p.cls == "FICTION_QUESTION" or (p.cls == "SPEECH" and "?" in p.text) for p in record.parts)
    for npc in engaged:
        if npc in skip or (npc in unresolved and npc not in talks):
            continue
        n_acts = len(record.npc_actions)
        is_addressed = npc in spoke_to or npc in talks
        practice = practice_for(ctx.state, record, npc, spoke_to)
        if npc in talks:  # (a) a resolved Talk frame's delivered outcome (a certain talk, no roll, is a yes)
            b = talks[npc]
            degree = b.entry.degree or "success"
            action = talk_outcome(b.entry)
            if degree in ("failure", "critical_failure"):
                action = voiced_refusal(ctx, npc, f"the talk did not move them ({degree.replace('_', ' ')})")
            record.npc_actions.append(NpcActionEntry(npc=npc, action=action, source="talk_outcome",
                                                     source_ref=b.frame_id, tags=[practice]))
        else:
            cands = candidates(ctx.state, npc, record)
            motive, tags = _judge_motive(ctx, npc, cands, happened_text(record)) if cands else (None, [])
            motives = npc_motives(ctx.state, npc)
            if motive is not None and "/refusal." in motive:  # (b) a recorded refusal outranks everything else
                record.npc_actions.append(NpcActionEntry(npc=npc, action=voiced_refusal(ctx, npc, motives[motive]),
                                                         source="refusal", source_ref=motive, tags=[practice, *tags]))
            elif motive is not None:
                record.npc_actions.append(NpcActionEntry(npc=npc, action=f"acts on a want: {motives[motive]}",
                                                         source="want", source_ref=motive, tags=[practice, *tags]))
            else:  # (c) the action table by standing, clamped to the practice (12.11.5)
                value = standing(ctx.state, npc)
                if value is None:  # PR-12-5 step 3: the first interaction's reaction roll
                    value = first_interaction(ctx.time_ctx(), npc)
                value = int(value or 0)
                res = roll_table(NPC_TABLE, {"standing_modifier": value}, rules=ctx.rules, state=ctx.state,
                                 rng=ctx.rng, purpose=f"npc action {npc} (12.11.5)")
                tx_.add_all(res.events)
                row_def = practice_rows[practice]
                row = clamp_row(int(res.roll or 5), [int(x) for x in row_def["action_rows"]], value <= -3)
                if row == 1 and value <= -3 and record.pc:  # rule: 06.2.1
                    from engine.resolve.conflict import start

                    start(ctx.time_ctx(), record.pc, [npc], "a hostile NPC attacks (06.2.1)")
                    _foe_turn(ctx, record, npc, oof)
                    continue
                gist = str((row_def.get("responses") or {}).get(str(row)) or res.entry)
                refuses = is_addressed and asked and row in REFUSING_ROWS  # what was asked is not given
                action = voiced_refusal(ctx, npc, gist) if refuses else gist
                record.npc_actions.append(NpcActionEntry(npc=npc, action=action, source="table_row",
                                                         source_ref=f"{NPC_TABLE}:{row}", tags=[practice]))
        for a in record.npc_actions[n_acts:]:  # T-12-18: the response sets their activity and manner
            src, ref = a.source, a.source_ref or "12.11.9"
            row = int(ref.rsplit(":", 1)[1]) if src == "table_row" else None
            degree = talks[npc].entry.degree if src == "talk_outcome" else None
            write(ctx, record, npc, response_values(ctx.rules, src, practice=practice, row=row, degree=degree),
                  because=ref)
        if is_addressed and npc not in spoken_with(ctx.state):
            sc = ctx.state.scene
            if sc is not None:
                tx_.add(meta(SPOKEN, {"scene": sc.scene_id, "npcs": [*spoken_with(ctx.state), npc]}, "12.11.9"))


__all__ = ["ACTIVITY", "addressed", "candidates", "clamp_row", "current_activity", "ensure_activities",
           "practice_for", "respond", "role_key", "voiced_refusal"]
