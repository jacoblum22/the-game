"""NPCs and their social record (12.11, 15.1-15.2, 15.7.6; T061), and the cast and thread lists (12.6.6).

    npc = meet_npc(ctx, "the ferryman", "loc.x")      # PR-12-5: the roster first, else a walk-on (fixed identity)
    first_interaction(ctx, npc)                       # 12.11.2: the reaction roll -> standing toward the PC
    step_standing(ctx, npc, +1, "win over", cap="warm")          # 15.1.5
    record_memory(ctx, npc, "Wren paid the toll for the boy", "helped")   # committed at scene_end (h.12.npc_memory)
    record_commitment(ctx, npc, by="npc", act="ferry Wren at dawn", due_day=day_index(now) + 1)

Storage. NPCs are `npc` entities whose `data` holds the walk-on fields (name, pronouns and descriptors are fixed
at creation, PR-12-5); later depths write facts on the NPC (`wants`, `fears`, `refusals`, `secrets` sealed;
`voice`, `knowledge_scope`, `depth` background). Standing is the relationship `npc|pc|standing`. Memories are
facts `memory.<n>` on the NPC, value {deed, valence, salience, how, status: active|archived, scene, time}.
Commitments are facts of kind `commitment`, predicate `commitment.<fact id>`. Meta: `cast_list` {npc: weight},
`thread_list` {thread: weight}, `last_featured` {id: scene number}, `featured` {scene_id, ids},
`pending_memories` [...], `patience` {npc: left}, `closed_talk` [npc], `thread_progress` {thread: scene}.
"""

from __future__ import annotations

from collections.abc import Iterable, MutableSequence, Sequence
from typing import Any, Literal, TypeVar

from engine.data.loader import Rules
from engine.gen import npc as gen_npc
from engine.rng import Rng
from engine.store.events import EntityRecord, Event
from engine.store.projection import WorldState
from engine.time import clock
from engine.time.handlers import HandlerResult
from engine.time.scheduler import TimeContext
from engine.world.common import WorldError, active_pc, fact, meta, scene_number, stage

T = TypeVar("T")
Valence = Literal["helped", "harmed", "lied_to", "caught_lying", "impressed", "insulted", "owed", "owes",
                  "promised", "betrayed", "spared", "threatened"]
_PRESENCE_WEIGHT = {"common": 3, "uncommon": 2, "rare": 1}  # the region's peoples (12.16.7), for a walk-on's folk
_SEALED_FIELDS = ("wants", "fears", "refusals", "secrets")
_RUNGS = {"hostile": -3, "unfriendly": -2, "wary": -1, "neutral": 0, "warm": 1, "friendly": 2, "devoted": 3}
SECRET_GATE = "learned in play (15.2.1)"


class LoggedSeedRng:
    """`engine.gen`'s SeedRng over the game's logged RNG (stream `npc`): every draw is logged with `purpose`."""

    def __init__(self, rng: Rng, purpose: str, stream: str = "npc") -> None:
        self.rng, self.purpose, self.stream = rng, purpose, stream

    def randint(self, a: int, b: int) -> int:
        return a - 1 + self.rng.draw(b - a + 1, self.purpose, stream=self.stream)

    def random(self) -> float:
        return (self.rng.draw(1_000_000, self.purpose, stream=self.stream) - 1) / 1_000_000

    def randrange(self, start: int, stop: int | None = None, step: int = 1) -> int:
        lo, hi = (0, start) if stop is None else (start, stop)
        n = (hi - lo + step - 1) // step
        return lo + step * (self.randint(1, n) - 1)

    def choice(self, seq: Sequence[T]) -> T:
        return seq[self.randint(1, len(seq)) - 1]

    def choices(self, population: Sequence[T], weights: Sequence[float] | None = None, *,
                cum_weights: Sequence[float] | None = None, k: int = 1) -> list[T]:
        if cum_weights is not None:
            weights = [c - (cum_weights[i - 1] if i else 0) for i, c in enumerate(cum_weights)]
        if weights is None:
            return [self.choice(population) for _ in range(k)]
        out = []
        for _ in range(k):
            r, total = self.random() * sum(weights), 0.0
            pick = population[-1]
            for item, w in zip(population, weights, strict=True):
                total += w
                if r < total:
                    pick = item
                    break
            out.append(pick)
        return out

    def sample(self, population: Sequence[T], k: int, *, counts: Any = None) -> list[T]:
        pool = list(population)
        self.shuffle(pool)
        return pool[:k]

    def shuffle(self, x: MutableSequence[Any]) -> None:
        for i in range(len(x) - 1, 0, -1):
            j = self.randint(0, i)
            x[i], x[j] = x[j], x[i]


def _rng(ctx: TimeContext) -> Rng:
    if ctx.rng is None:
        raise WorldError("this step rolls: ctx.rng is required")
    return ctx.rng


# ------------------------------------------------------------------------------------------ the lists


def cast_list(state: WorldState) -> dict[str, int]:  # rule: 12.6.6
    """Every NPC the PC has met who still exists and has not departed, with its weight 1-3."""
    raw = state.meta.get("cast_list") or {}
    return {n: int(w) for n, w in raw.items() if n in state.entities and state.entities[n].exists == "exists"}


def thread_list(state: WorldState) -> list[dict[str, Any]]:  # rule: 12.6.6
    """Every thread entity: {id, name, text, thread_kind, points_to, status, stalled, weight} (weight 0 when off
    the list)."""
    weights = state.meta.get("thread_list") or {}
    out = []
    for eid, e in state.entities.items():
        if e.kind != "thread":
            continue
        status = str(state.fact_value(eid, "status") or e.data.get("status", "active"))
        out.append({"id": eid, "name": e.name, "text": e.data.get("text", e.name),
                    "thread_kind": e.data.get("thread_kind"), "points_to": e.data.get("points_to"),
                    "status": status, "stalled": bool(state.fact_value(eid, "stalled")),
                    "weight": int(weights.get(eid, 1 if status == "active" else 0))})
    return out


def set_thread_status(ctx: TimeContext, thread: str, status: str) -> None:
    """active | resolved | failed | abandoned (a resolved, failed or abandoned thread leaves the list)."""
    stage(ctx, fact(ctx.tx, thread, "status", status, rule_id="12.6.6", source="ruling", visibility="available"))


def mark_progress(ctx: TimeContext, thread: str) -> None:  # rule: 12.6.5
    """The PC progressed `thread` this scene (protects it from off-screen resolution for 12 scenes)."""
    prog = dict(ctx.tx.state.meta.get("thread_progress") or {})
    prog[thread] = _scene_no(ctx.tx.state)
    stage(ctx, meta("thread_progress", prog, "12.6.5"))


def protected_threads(state: WorldState, rules: Rules) -> set[str]:  # rule: 12.6.5
    """Threads the PC vowed to (fact `vow`) or progressed within `events.offscreen_resolution_protect_scenes`."""
    n = int(rules.pacing["events"]["offscreen_resolution_protect_scenes"])
    now = _scene_no(state)
    prog = state.meta.get("thread_progress") or {}
    return {t["id"] for t in thread_list(state)
            if state.fact_value(t["id"], "vow") or (t["id"] in prog and now - int(prog[t["id"]]) <= n)}


def feature(ctx: TimeContext, ids: Iterable[str]) -> None:  # rule: 12.6.6
    """Note entries featured in the current scene (its agenda, acted in it, named in a delivered lead)."""
    sc = ctx.tx.state.scene
    if sc is None:
        return
    cur = ctx.tx.state.meta.get("featured") or {}
    have = list(cur.get("ids", [])) if cur.get("scene_id") == sc.scene_id else []
    new = list(dict.fromkeys([*have, *ids]))
    if new != have:
        stage(ctx, meta("featured", {"scene_id": sc.scene_id, "ids": new}, "12.6.6"))


def update_lists(ctx: TimeContext, rules: Rules) -> str:  # rule: 12.6.6
    """12.4.8 step 3 at scene_end: +1 (max 3) for each entry featured this scene (the agenda's thread, the cast
    present, a lead's source); -1 (min 1) for each not featured in the last six scenes; drop dead or departed
    NPCs and threads no longer active."""
    from engine.world.scenes import cast_present, scene_info
    state = ctx.tx.state
    sc = state.scene
    cfg = rules.pacing["lists"]
    lo, hi, stale = int(cfg["weight_min"]), int(cfg["weight_max"]), int(cfg["lower_after_scenes_unfeatured"])
    now = _scene_no(state)
    fe = state.meta.get("featured") or {}
    featured = set(fe.get("ids", [])) if sc and fe.get("scene_id") == sc.scene_id else set()
    featured |= set(cast_present(state))
    if scene_info(state).get("thread"):
        featured.add(scene_info(state)["thread"])
    last = dict(state.meta.get("last_featured") or {})
    for i in featured:
        last[i] = now
    out = {}
    for key, entries in (("cast_list", cast_list(state)),
                         ("thread_list", {t["id"]: t["weight"] for t in thread_list(state) if t["status"] == "active"})):
        new = {}
        for i, w in entries.items():
            if i in featured:
                w = min(hi, w + 1)
            elif now - int(last.get(i, 0)) >= stale:
                w = max(lo, w - 1)
            new[i] = w
        out[key] = new
        if new != (state.meta.get(key) or {}):
            stage(ctx, meta(key, new, "12.6.6"))
    stage(ctx, meta("last_featured", last, "12.6.6"))
    return f"cast {len(out['cast_list'])}, threads {len(out['thread_list'])}"


def _scene_no(state: WorldState) -> int:
    return scene_number(state.scene.scene_id) if state.scene else int(state.counters.get("scn", 0))


# --------------------------------------------------------------------------------------- generating NPCs


def npc_field(state: WorldState, npc: str, key: str, default: Any = None) -> Any:
    """An NPC field: a later depth's fact if written, else the creation record's."""
    v = state.fact_value(npc, key)
    if v is not None:
        return v
    e = state.entities.get(npc)
    return e.data.get(key, default) if e else default


def find_npc(state: WorldState, role: str, place: str | None) -> str | None:  # rule: PR-12-5
    """PR-12-5 step 1, the deterministic part: an existing NPC with this role (case-insensitive, exact) living
    at or positioned at `place`. Whether a looser match fits is the DM's [J:flag]."""
    want = role.strip().lower().removeprefix("the ").removeprefix("a ").removeprefix("an ")
    for eid, e in state.entities.items():
        if e.kind != "npc" or e.exists != "exists":
            continue
        r = str(e.data.get("role", "")).lower().removeprefix("the ")
        pos = state.positions.get(eid)
        if r == want and place in (e.data.get("home"), pos.location if pos else None):
            return eid
    return None


def meet_npc(ctx: TimeContext, role: str | None, place: str | None, *, people: str | None = None,
             reuse: bool = True, alias: str | None = None) -> str:  # rule: PR-12-5
    """PR-12-5 steps 1-2: the roster first (`find_npc`), else a walk-on (12.11.1): role (else `tbl.npc_role`),
    name (the region's table for its people, else the generic tables), gender and pronouns, age, detail and
    demeanor, all rolled and written at once (`create_entity`), positioned at `place`, added to the cast list
    at weight 1. Returns the NPC's entity id."""
    state = ctx.tx.state
    if reuse and role and (found := find_npc(state, role, place)):
        _add_to_cast(ctx, found)
        return found
    rng = _rng(ctx)
    peoples = state.meta.get("world.peoples") or []
    if people is None and peoples:
        weights = [(p["origin"], _PRESENCE_WEIGHT.get(str(p.get("present")), 1)) for p in peoples]
        people = rng.weighted(weights, "walk-on people (12.16.7)", stream="npc")
    used = {str(e.name).split()[0] for e in state.entities.values() if e.kind == "npc" and e.name}
    n = gen_npc.walk_on(LoggedSeedRng(rng, "walk-on (PR-12-5)"), role=role, home=place, people=people,
                        name_tables=state.meta.get("world.names") or [], given_used=used,
                        existing_ids=state.entities.keys())
    data = n.model_dump(exclude={"id", "name", "sealed_fields", "wants", "fears", "refusals", "secrets", "voice",
                                 "knowledge_scope", "ties", "licenses"}, by_alias=True)
    data["name_known"] = False  # 12.10.2: a walk-on's name is learned in play
    if alias and alias.lower() != str(data.get("role", "")).lower():
        data["aliases"] = [alias]  # the narration's words for them: the label every screen uses (P-095)
    stage(ctx, Event.of("entity_created", rule_id="PR-12-5", source="npc_generation",
                        entity=EntityRecord(id=n.id, kind="npc", name=n.name, visibility="shown", data=data)))
    if place is not None and place in state.entities:
        stage(ctx, Event.of("position_set", rule_id="PR-12-5", entity=n.id, location=place))
    _add_to_cast(ctx, n.id)
    return n.id


def _add_to_cast(ctx: TimeContext, npc: str) -> None:  # rule: 12.6.6
    cl = dict(ctx.tx.state.meta.get("cast_list") or {})
    if npc not in cl:
        cl[npc] = 1
        stage(ctx, meta("cast_list", cl, "12.6.6"))
    feature(ctx, [npc])


def promote_npc(ctx: TimeContext, npc: str, depth: Literal["recurring", "principal"]) -> list[str]:  # rule: PR-12-5
    # rule: 15.2.1
    """PR-12-5 steps 4-5: roll the next depth's fields (engine.gen.npc) and write them as facts on the NPC
    (wants, fears, refusals, secrets sealed until learned). Returns the fields written."""
    state = ctx.tx.state
    e = state.entities.get(npc)
    if e is None or e.kind != "npc":
        raise WorldError(f"{npc} is not an NPC")
    cur = str(npc_field(state, npc, "depth", "walk-on"))
    order = ("walk-on", "minor", "recurring", "principal")
    if order.index(cur) >= order.index(depth):
        return []
    rec = {**e.data, **{k: npc_field(state, npc, k) for k in ("wants", "fears", "refusals", "secrets", "voice",
                                                              "knowledge_scope", "ties", "depth")
                        if npc_field(state, npc, k) is not None}}
    base = gen_npc.NPC.model_validate({**rec, "id": npc, "name": e.name,
                                       "depth": "walk-on" if rec.get("depth") == "minor" else rec.get("depth")})
    srng = LoggedSeedRng(_rng(ctx), f"promote {npc} to {depth} (PR-12-5)")
    if depth == "recurring":
        new = gen_npc.promote_recurring(srng, base)
    else:
        home = state.entities.get(str(e.data.get("home") or ""))
        new = gen_npc.promote_principal(srng, base, home_band=int((home.data.get("band") if home else 1) or 1))
    before, after = base.model_dump(by_alias=True), new.model_dump(by_alias=True)
    written = []
    for k in ("wants", "fears", "refusals", "secrets", "voice", "knowledge_scope", "ties", "depth", "band"):
        if after.get(k) != before.get(k):
            sealed = k in _SEALED_FIELDS
            stage(ctx, fact(ctx.tx, npc, k, after[k], rule_id="PR-12-5", visibility="sealed" if sealed else "background",
                            gate=SECRET_GATE if sealed else None))
            written.append(k)
    return written


# ------------------------------------------------------------------------------------------- standing


def standing(state: WorldState, npc: str, toward: str | None = None) -> int | None:  # rule: 15.1.1
    pc = toward or active_pc(state)
    r = state.relationships.get(f"{npc}|{pc}|standing")
    return r.value if r else None


def standing_effects(rules: Rules, value: int) -> dict[str, Any]:  # rule: T-15-1
    """The `social.yaml#standing_effects` row (rung name, patience, ceiling, behavior) for a standing value."""
    return dict(next(r for r in rules.social["standing_effects"] if int(r["standing"]) == value))


def first_interaction(ctx: TimeContext, npc: str, *, modifiers: int = 0,
                      faction_status: int | None = None) -> int:  # rule: 12.11.2
    # rule: 15.1.4
    """12.11.2 / 15.1.4: at the NPC's first interaction with the PC, roll the starting standing (a faction member:
    status + tbl.npc_reaction_member; anyone else: tbl.npc_reaction + cited modifiers, clamped +-2; never Devoted)
    and write it. Returns the standing (the existing one if already set)."""
    state = ctx.tx.state
    pc = active_pc(state)
    if pc is None:
        raise WorldError("no PC")
    have = standing(state, npc, pc)
    if have is not None:
        return have
    if faction_status is None and npc_field(state, npc, "member_of"):
        for fac in npc_field(state, npc, "member_of") or []:
            rel = state.relationships.get(f"{fac}|{pc}|status")
            if rel is not None:
                faction_status = rel.value
                break
    react = gen_npc.reaction_roll(LoggedSeedRng(_rng(ctx), f"reaction roll {npc} (12.11.2)"),
                                  modifiers=modifiers, faction_status=faction_status)
    stage(ctx, Event.of("relationship_set", rule_id="12.11.2", a=npc, b=pc, kind="standing", value=react.standing,
                        new_value=react.standing, reason=f"reaction roll ({react.table} {react.roll}"
                        f"{react.modifier:+d})"))
    _add_to_cast(ctx, npc)
    return react.standing


def step_standing(ctx: TimeContext, npc: str, steps: int, reason: str, *, cap: str | None = None,
                  toward: str | None = None) -> int:  # rule: 15.1.5
    # rule: 12.11.6
    """Move standing by `steps` from a 15.1.5 source, clamped -3..+3 and, for a raise, never above `cap` (a rung
    name: warm, friendly, devoted). Returns the new standing."""
    state = ctx.tx.state
    pc = toward or active_pc(state)
    if pc is None:
        raise WorldError("no PC")
    cur = standing(state, npc, pc)
    if cur is None:
        cur = first_interaction(ctx, npc)
    new = max(-3, min(3, cur + steps))
    if steps > 0 and cap is not None:
        new = min(new, max(cur, _RUNGS[cap]))
    if new != cur:
        stage(ctx, Event.of("relationship_set", rule_id="15.1.5", a=npc, b=pc, kind="standing", steps=new - cur,
                            new_value=new, reason=reason))
    return new


def memory_step(rules: Rules, valence: str, severity: str | None = None) -> tuple[int, str | None]:  # rule: T-15-2
    # rule: 15.1.6
    """(step, cap rung) for a memory valence (T-15-2); `harmed` reads its step from the severity."""
    for row in rules.social["memory_steps"]["rows"]:
        if row["valence"] != valence:
            continue
        if "step_by_severity" in row:
            return int(row["step_by_severity"].get(severity or "S1", -1)), None
        cap = row.get("cap")
        return int(row.get("step", 0)), (None if cap in (None, "none") else str(cap))
    return 0, None


# -------------------------------------------------------------------------------------------- memories


def record_memory(ctx: TimeContext, npc: str, deed: str, valence: Valence, *,
                  how: Literal["did", "witnessed", "told"] = "did", standing_changed: bool = False,
                  harm: bool = False, apply_step: bool = False, severity: str | None = None) -> dict[str, Any]:
    # rule: 12.11.7
    """12.11.7: a memory written at RECORD, committed at scene_end by `h.12.npc_memory`. Salience 3 when standing
    changed or harm or a cost touched them, 2 for a promise, debt or detected lie, else 1. `apply_step` also
    moves standing by T-15-2's step for the valence (15.1.6)."""
    if valence not in ctx.rules.pacing["npc"]["memory"]["valences"]:
        raise WorldError(f"{valence!r} is not a memory valence (12.11.7)")
    if apply_step:
        step, cap = memory_step(ctx.rules, valence, severity)
        if step:
            before = standing(ctx.tx.state, npc)
            standing_changed = step_standing(ctx, npc, step, f"memory: {valence}", cap=cap) != before or standing_changed
    sal = ctx.rules.pacing["npc"]["memory"]["salience"]
    salience = (sal["standing_changed_or_harm_or_cost"] if standing_changed or harm
                else sal["promise_debt_or_lie_detected"] if valence in ("promised", "owed", "owes", "caught_lying")
                else sal["other"])
    st = ctx.tx.state
    mem = {"npc": npc, "deed": deed, "valence": valence, "salience": int(salience), "how": how,
           "scene": st.scene.scene_id if st.scene else None, "time": clock.fmt(st.time.now), "seq": ctx.tx.peek_seq()}
    pending = [*(st.meta.get("pending_memories") or []), mem]
    stage(ctx, meta("pending_memories", pending, "12.11.7"))
    if st.scene is None:  # outside a scene there is no scene_end to wait for
        commit_memories(ctx)
    return mem


def memories(state: WorldState, npc: str, *, active_only: bool = True) -> list[dict[str, Any]]:  # rule: 12.11.7
    """The NPC's memories of the PC, most salient then most recent first."""
    out = [dict(f.value) | {"fact_id": f.id} for f in state.facts.values()
           if f.subject == npc and f.predicate.startswith("memory.") and isinstance(f.value, dict)]
    if active_only:
        out = [m for m in out if m.get("status") == "active"]
    return sorted(out, key=lambda m: (-int(m["salience"]), -int(m["seq"])))


def commit_memories(ctx: TimeContext) -> HandlerResult:  # rule: 12.11.7
    """`h.12.npc_memory` (scene_end, phase 9): write the scene's pending memories; keep at most `active_cap`
    active per NPC by salience then recency, archiving the rest (never lost)."""
    tx = ctx.tx
    pending = list(tx.state.meta.get("pending_memories") or [])
    if not pending:
        return HandlerResult(summary="no memories")
    cap = int(ctx.rules.pacing["npc"]["memory"]["active_cap"])
    touched: set[str] = set()
    for m in pending:
        npc = m["npc"]
        if npc not in tx.state.entities:
            continue
        n = 1 + sum(1 for f in tx.state.facts.values() if f.subject == npc and f.predicate.startswith("memory."))
        stage(ctx, fact(tx, npc, f"memory.{n}", {**m, "status": "active"}, rule_id="12.11.7", source="ruling"))
        touched.add(npc)
    archived = 0
    for npc in sorted(touched):
        for m in memories(tx.state, npc)[cap:]:
            f = tx.state.facts[m["fact_id"]]
            val = {k: v for k, v in m.items() if k != "fact_id"} | {"status": "archived"}
            stage(ctx, fact(tx, npc, f.predicate, val, rule_id="12.11.7", source="ruling"))
            archived += 1
    stage(ctx, meta("pending_memories", [], "12.11.7"))
    return HandlerResult(summary=f"memories {len(pending)}, archived {archived}")


def record_knowledge(ctx: TimeContext, knower: str, fact_id: str, how: str) -> int:  # rule: 12.10.6
    """`record_knowledge` (00.14.2): `knower` learned `fact_id` (witnessed, told, read, overheard, ...)."""
    return stage(ctx, Event.of("knowledge_recorded", rule_id="12.10.6", knower=knower, fact_id=fact_id, how=how))[0]


def learn_name(ctx: TimeContext, knower: str, npc: str, how: str = "told") -> None:  # rule: 12.10.2
    """`knower` learns `npc`'s name (15.9.17 write point "every name learned"): their `name` fact, known."""
    state = ctx.tx.state
    fid = state.current_fact_id(npc, "name")
    if fid is None or state.facts[fid].value != state.entities[npc].name:
        ev = fact(ctx.tx, npc, "name", state.entities[npc].name, rule_id="12.10.2", source="ruling",
                  visibility="shown")
        stage(ctx, ev)
        fid = ev.payload.fact_id  # type: ignore[attr-defined]
    record_knowledge(ctx, knower, fid, how)


def knows(state: WorldState, knower: str, fact_id: str) -> str | None:
    k = state.knowledge.get(knower, {}).get(fact_id)
    return k.how if k else None


# -------------------------------------------------------------------------------------------- patience


def patience(state: WorldState, rules: Rules, npc: str) -> int | None:  # rule: 15.2.6
    """Patience left this scene (None = unlimited, Devoted); starts at the standing's maximum (T-15-1)."""
    left = (state.meta.get("patience") or {}).get(npc)
    if left is not None:
        return int(left)
    s = standing(state, npc)
    mx = standing_effects(rules, 0 if s is None else s)["patience"]
    return None if mx == "unlimited" else int(mx)


def talk_closed(state: WorldState, npc: str) -> bool:  # rule: 15.2.6
    return npc in (state.meta.get("closed_talk") or [])


def spend_patience(ctx: TimeContext, npc: str, amount: int = 1) -> int | None:  # rule: 15.2.6
    """Spend patience (a failed Talk beat 1, a critical failure 2, a refusal or ceiling, an insult). At 0 the NPC
    ends the exchange: `closed.<npc>.talk` until scene_end (no standing loss). Returns what is left."""
    left = patience(ctx.tx.state, ctx.rules, npc)
    if left is None:
        return None
    left = max(0, left - amount)
    pat = dict(ctx.tx.state.meta.get("patience") or {})
    pat[npc] = left
    stage(ctx, meta("patience", pat, "15.2.6"))
    if left == 0 and not talk_closed(ctx.tx.state, npc):
        stage(ctx, meta("closed_talk", [*(ctx.tx.state.meta.get("closed_talk") or []), npc], "15.2.6"))
    return left


def patience_reset(ctx: TimeContext) -> HandlerResult:  # rule: 15.2.6
    """`h.15.patience_reset` (scene_end, phase 9): every NPC's patience back to its maximum; closed talk cleared."""
    st = ctx.tx.state
    n = len(st.meta.get("patience") or {}) + len(st.meta.get("closed_talk") or [])
    if n:
        stage(ctx, meta("patience", {}, "15.2.6"), meta("closed_talk", [], "15.2.6"))
    return HandlerResult(summary=f"reset {n}")


# ------------------------------------------------------------------------------------------ commitments


def record_commitment(ctx: TimeContext, npc: str, *, by: Literal["npc", "pc"], act: str, due_day: int,
                      coerced: bool = False, oath: bool = False, impossible_if: str | None = None) -> str:
    # rule: 15.7.6
    """One side of a deal (15.7.6): the NPC's agreed act or the PC's obligation, due at the start of `due_day`
    (`clock.day_index`). `impossible_if`: a predicate on the NPC whose truthy fact makes the act impossible.
    Returns the commitment's fact id."""
    tx = ctx.tx
    fid = tx.mint("fact")
    pred = f"commitment.{fid}"
    value = {"npc": npc, "by": by, "act": act, "due_day": int(due_day), "status": "open", "coerced": coerced,
             "oath": oath, "impossible_if": impossible_if}
    stage(ctx, Event.of("fact_set", {"source": "ruling"}, rule_id="15.7.6", fact_id=fid, subject=npc,
                        predicate=pred, value=value, kind="commitment", visibility="available"))
    return fid


def commitments(state: WorldState, *, status: str | None = "open") -> list[dict[str, Any]]:
    out = [dict(f.value) | {"fact_id": f.id, "predicate": f.predicate} for f in state.facts.values()
           if f.kind == "commitment" and f.predicate.startswith("commitment.") and isinstance(f.value, dict)]
    return [c for c in out if status is None or c.get("status") == status]


def _settle(ctx: TimeContext, c: dict[str, Any], status: str) -> None:
    val = {k: v for k, v in c.items() if k not in ("fact_id", "predicate")} | {"status": status}
    stage(ctx, Event.of("fact_set", {"source": "ruling"}, rule_id="15.7.6", fact_id=ctx.tx.mint("fact"),
                        subject=c["npc"], predicate=c["predicate"], value=val, kind="commitment",
                        visibility="available", supersedes=c["fact_id"]))


def keep_commitment(ctx: TimeContext, fact_id: str) -> None:  # rule: 15.7.6
    """The PC kept an obligation: settled `kept`; the NPC remembers a promise kept (+1, cap Friendly)."""
    c = next((x for x in commitments(ctx.tx.state) if x["fact_id"] == fact_id), None)
    if c is None or c["by"] != "pc":
        raise WorldError(f"{fact_id} is not an open PC obligation")
    _settle(ctx, c, "kept")
    record_memory(ctx, c["npc"], f"kept their word: {c['act']}", "promised", standing_changed=True)
    step_standing(ctx, c["npc"], 1, "promise kept (15.7.6)", cap="friendly")


def commitments_due(ctx: TimeContext) -> HandlerResult:  # rule: 15.7.6
    """`h.15.commitments_due` (day, phase 6): an NPC's due act is performed unless coerced, the NPC is now
    Hostile (it reneges; the NPC owes the PC), or a fact makes it impossible. A PC obligation due and unmet is
    broken: the NPC remembers `betrayed` (-3) and the advance halts (interrupting)."""
    st = ctx.tx.state
    today = clock.day_index(ctx.now)
    out: list[str] = []
    broken = []
    for c in sorted(commitments(st), key=lambda x: (x["due_day"], x["fact_id"])):
        if int(c["due_day"]) > today:
            continue
        npc = c["npc"]
        if c["by"] == "npc":
            if c.get("coerced"):
                status = "reneged_coerced"
            elif standing(st, npc) == -3:
                status = "reneged"
                record_memory(ctx, npc, f"broke faith: {c['act']}", "owes")
                broken.append(c["act"])
            elif c.get("impossible_if") and st.fact_value(npc, str(c["impossible_if"])):
                status = "impossible"
            else:
                status = "performed"
            _settle(ctx, c, status)
        else:
            status = "broken"
            _settle(ctx, c, status)
            record_memory(ctx, npc, f"broke their word: {c['act']}", "betrayed", standing_changed=True)
            step_standing(ctx, npc, -3, "obligation broken (15.7.6)")
            broken.append(c["act"])
        out.append(f"{npc}:{status}")
    return HandlerResult(summary=", ".join(out) or "none due",
                         interrupt=f"a deal fell due unkept: {broken[0]}" if broken else None)
