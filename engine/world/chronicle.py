"""The chronicle (11.12; T061): the append-only true history of the world, for recaps, the journal and the
epilogue.

    cid = chronicle_append(ctx, "Wren carried the bell back to Ravenford.", kind="thread",
                           entities=["pc.wren", "thr.lead_2"], source="12.4.8")
    for entry in chronicle(store.state): ...

Each entry is a fact on `world`, predicate `chronicle.<chr id>`, value the 11.12.1 ChronicleEntry. Entries are
never edited or deleted: a correction is a new entry whose `supersedes` names the wrong one (11.12.3), and
`chronicle(state)` drops superseded entries unless asked for them. The wording is the DM's ([N]); the occasions
are 11.12.2's closed list (`SOURCES`), and the scene-end line is offered by `h.12.bookkeeping` as meta
`chronicle_offer` when a scene answered a thread's agenda (12.4.8 step 8).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, Field

from engine.store.events import WORLD, Event
from engine.store.projection import WorldState
from engine.time import clock
from engine.time.scheduler import TimeContext
from engine.world.common import WorldError, meta, stage

PREFIX = "chronicle."
MAX_WORDS = 30  # 11.12.1
KINDS = ("prologue", "deed", "thread", "defeat", "death", "faction", "situation", "world_change", "recognition",
         "holding", "season", "year", "legend", "retirement")
# 11.12.2: who writes it (rule ids of the occasions; closed list).
SOURCES = ("02.11.2", "12.4.8", "12.4.9", "07.5.9", "07.5.12", "07.6.2", "h.11.world_record", "11.12.2",
           "04.7.8", "11.11.3", "11.11.5", "11.13.3")


class ChronicleEntry(BaseModel):  # 11.12.1
    id: str
    time: str
    text: str
    kind: str
    entities: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    scope: str | list[str] = "public"
    source: str
    supersedes: str | None = None
    seq: int = 0


def chronicle_append(ctx: TimeContext, text: str, *, kind: str, entities: Sequence[str] = (),
                     tags: Sequence[str] = (), scope: str | list[str] = "public", source: str = "12.4.8",
                     supersedes: str | None = None, time: str | None = None) -> str:  # rule: 11.12.1
    # rule: 11.12.3
    # rule: 11.12.2
    """`chronicle_append` (00.14.2): add one entry (<= 30 words, one of 11.12.1's kinds, from one of 11.12.2's
    occasions). Returns its id (`chr.<n>`)."""
    state = ctx.tx.state
    if kind not in KINDS:
        raise WorldError(f"{kind!r} is not a chronicle kind (11.12.1)")
    if source not in SOURCES:
        raise WorldError(f"{source!r} is not a chronicle occasion (11.12.2)")
    if len(text.split()) > MAX_WORDS:
        raise WorldError(f"a chronicle line is at most {MAX_WORDS} words (11.12.1)")
    if supersedes is not None and state.current_fact_id(WORLD, PREFIX + supersedes) is None:
        raise WorldError(f"{supersedes} is not a chronicle entry")
    cid = f"chr.{_count(state) + 1}"
    entry = {"id": cid, "time": time or clock.fmt(state.time.now), "text": text, "kind": kind,
             "entities": [e for e in entities if e in state.entities], "tags": list(tags), "scope": scope,
             "source": source, "supersedes": supersedes}
    stage(ctx, Event.of("fact_set", {"source": "narration"}, rule_id="11.12.1", fact_id=ctx.tx.mint("fact"),
                        subject=WORLD, predicate=PREFIX + cid, value=entry, visibility="available"))
    if ctx.tx.state.meta.get("chronicle_offer") and source == "12.4.8":
        stage(ctx, meta("chronicle_offer", None, "12.4.8"))
    return cid


def _count(state: WorldState) -> int:
    return sum(1 for k in state.fact_keys if k.startswith(f"{WORLD}|{PREFIX}"))


def chronicle(state: WorldState, *, include_superseded: bool = False, entity: str | None = None,
              since_seq: int = 0) -> list[ChronicleEntry]:  # rule: 11.12.4
    """The chronicle in the order it was written; by default without entries a correction superseded.
    `entity` filters by id (11.12.4 (2) continuity queries); `since_seq` gives the entries for a recap."""
    rows: list[ChronicleEntry] = []
    for key, fid in state.fact_keys.items():
        if not key.startswith(f"{WORLD}|{PREFIX}"):
            continue
        f = state.facts[fid]
        rows.append(ChronicleEntry.model_validate({**f.value, "seq": f.valid_from_seq}))
    rows.sort(key=lambda e: e.seq)
    if not include_superseded:
        gone = {e.supersedes for e in rows if e.supersedes}
        rows = [e for e in rows if e.id not in gone]
    if entity is not None:
        rows = [e for e in rows if entity in e.entities]
    return [e for e in rows if e.seq > since_seq]


def scene_offer(state: WorldState) -> dict[str, Any] | None:  # rule: 12.4.8
    """12.4.8 step 8: when the ending scene answered an agenda attached to a thread, the line ch.11 is offered."""
    from engine.world.scenes import agenda_answer, scene_info
    sc = state.scene
    thread = scene_info(state).get("thread")
    answered = agenda_answer(state)
    if sc is None or not thread or answered is None:
        return None
    return {"scene_id": sc.scene_id, "thread": thread, "agenda": sc.agenda, "answered": answered,
            "kind": "thread", "source": "12.4.8"}
