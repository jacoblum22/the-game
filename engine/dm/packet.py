"""The one packet builder every role uses (contracts/model-calls.md "Packet order"; 12.2.4; FR-029; T106).

    packet = build_packet(Role.READER, instructions=text, cards=load_cards_for(...), view=state,
                          exchanges=last_exchanges, message=player_text, triggers=active, quiet_turns=2)

Order: role instructions -> the role's guidance digest (12.2.4 item 1, in the `core` slot, titled GUIDANCE; the
00.15.4 core is never sent, DL-00-07) -> the cards code knows apply, stable to volatile (at most
`pacing.yaml#packet.max_loaded_cards`, 12; more is a caller error) -> the active-trigger list, then the role's view
-> the role's exchanges verbatim (`ROLE_EXCHANGES`: Director 2, World 1, else `packet.verbatim_exchanges`, 4) -> this
message verbatim. Stable sections come first, for prompt caching: nothing volatile precedes the view (DL-12-38).

`view` may be a `WorldState` (rendered with `scene_view` + `render_view`), a narrator-view dict (rendered), or a
pre-rendered string. The rendered view is scene-scoped and held to per-section token budgets
(`pacing.yaml#packet.view_budget`: pinned and ranked facts, people present, things, clocks, threads, known cast),
so the packet does not grow with the length of the game (SC-002). People present beyond the `cast` budget share
one `also here:` line (R2-A2). Each entity is rendered
as `<id>: <name>` and then a `name: <name>` line: the offline model reads names from `name:` lines and entity
aliases from the text after an id.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from engine.build.compile_cards import RuleCard
from engine.data.loader import load_rules
from engine.llm.base import Packet, Role
from engine.retrieve.cards import guidance_digest, max_cards
from engine.retrieve.episodes import card_lines, cards_for
from engine.retrieve.scene import (
    CAST_KINDS,
    also_here,
    beat_target,
    calendar_line,
    cast_order,
    entity_names,
    fit,
    pc_id,
    scene_facts,
    scene_scope,
    shown_details,
    spotlight,
    tokens,
    view_budget,
)
from engine.retrieve.triggers import ActiveTrigger
from engine.store.projection import WorldState
from engine.store.views import display_name, name_known, narrator_view

VERBATIM_EXCHANGES = 4  # fallback; the rules value is pacing.yaml#packet.verbatim_exchanges
# 12.2.4's role table [DL-12-104]: the conversation a role's judgment needs (the Checker's is spec 019's)
ROLE_EXCHANGES = {Role.DIRECTOR: 2, Role.WORLD: 1}
MAX_DATA_KEYS = 12
MAX_VALUE_CHARS = 160
WATCHES = ("morning", "afternoon", "evening", "night")
_DESCRIPTIVE_KEYS = ("pronouns", "desc", "landmarks", "hazards", "openness", "role", "detail", "demeanor")  # first under the cap
# What drives a person, never the narrator's (12.10.1 world layer; 15.2.1 fields, 12.16.11 knowledge pack)
MOTIVES = frozenset({"wants", "refusals", "fears", "secrets", "knowledge", "beliefs", "ties", "knowledge_scope"})
CARD_CHARS = 600  # one scene card line, ~150 tokens (view_budget.scene_cards / max_scene_cards)


class PacketError(ValueError):
    """A packet that breaks the 00.15.4 caps (a caller bug, never a model failure)."""


# ---------------------------------------------------------------- view


def _listed(state: WorldState, ids: list[str], weights: Mapping[str, int], room: int) -> dict[str, Any]:  # rule: 12.6.6
    """id -> name for a view list: by 12.6.6 weight, then newest introduced, within `room` tokens."""
    order = {eid: n for n, eid in enumerate(state.entities)}
    ranked = sorted(ids, key=lambda i: (-weights.get(i, 1), -order[i]))
    names = entity_names(state, ranked)
    return {i: names[i] for i in fit(list(names), lambda i: tokens(f"{i} {names[i]}; "), room)}


def scene_view(state: WorldState, focus: Iterable[str] = (), *, spot: Sequence[str] = (),
               cards: bool = False) -> dict[str, Any]:  # rule: 12.2.4
    """The narrator view of the current scene, within `pacing.yaml#packet.view_budget` (12.2.4 item 3). `focus`
    (the beat's target, entities the message names) raises a fact's relevance and puts a present person first for
    a full profile. `spot` (the spotlight) adds the entities outside the scene as the PC knows them, within
    `view_budget.spotlight`; `cards` adds at most `packet.max_scene_cards` scene cards within
    `view_budget.scene_cards`. Nothing sealed is in it (INV-10)."""
    from engine.world.social import cast_list, thread_list

    focus = list(dict.fromkeys([*focus, *spot]))  # a spotlight entity counts for relevance (12.2.4)
    budget = view_budget()
    scope = scene_scope(state, budget)
    picked = scene_facts(state, scope, focus=focus, budget=budget)
    # rule: 12.3.6
    # a pinned correction is never archived: always in its subject's profile while the subject is in view
    picked += [f for f in state.facts.values() if f.pinned and f.subject in scope and f not in picked]
    nv = narrator_view(state, [*scope, *(f.subject for f in picked)])  # an open commitment's NPC may be away
    visible_facts = nv["facts"]
    facts = [visible_facts[f.id] for f in picked if f.id in visible_facts]
    active = [c for c in nv["clocks"].values() if c.get("status") == "active"]
    kept = fit(reversed(active), lambda c: tokens(f"  {c['id']}: {c['name']} ({c['kind']}) 00/00"), budget["clocks"])
    clocks = [c for c in active if c in kept]
    others = [eid for eid, e in state.entities.items() if eid not in scope]
    tl = {t["id"]: t["weight"] for t in thread_list(state) if t["status"] == "active" and t["id"] not in scope}
    known = [i for i in others if state.entities[i].kind in ("npc", "companion", "faction")
             and name_known(state, i)]  # people the PC knows by name (12.10.2)
    view: dict[str, Any] = {
        "calendar": calendar_line(state),  # 12.2.4 item 3: first in the scene header, outside every budget
        "time": nv["time"],
        "scene": nv["scene"],
        "entities": [nv["entities"][i] for i in scope if i in nv["entities"]],
        "quantities": nv["quantities"],
        "conditions": list(nv["conditions"].values()),
        "licenses": nv["licenses"],
        "positions": nv["positions"],
        "facts": facts,
        "clocks": clocks,
        "threads": _listed(state, list(tl), tl, budget["threads"]),
        "known": _listed(state, known, cast_list(state), budget["known"]),
        "open_pause": nv["open_pause"],
    }
    # The people present beyond the PC: full profiles within `cast`, everyone else on one capped line (R2-A2).
    by_id = {e["id"]: e for e in view["entities"] if e["id"] != pc_id(state)
             and state.entities[e["id"]].kind in CAST_KINDS}
    ranked = cast_order(state, by_id, focus)
    full = set(fit(ranked, lambda i: tokens("\n".join(_entity_lines(view, by_id[i]))), budget["cast"]))
    view["entities"] = [e for e in view["entities"] if e["id"] not in by_id or e["id"] in full]
    rest = {i: _label(by_id[i]) for i in ranked if i not in full}
    view["also_here"] = also_here(rest, budget["cast_line"]) if rest else ""
    view["also_here_ids"] = list(rest)  # their identity lines (12.2.4 item 3)
    view["spotlight"] = [ln for i in fit(list(spot), lambda i: tokens("\n".join(spot_lines(state, i))),
                                         budget.get("spotlight", 400)) for ln in spot_lines(state, i)]
    if cards:
        view["cards"] = scene_card_lines(state, spot, budget.get("scene_cards", 300))
    return view


def _pc_knows(state: WorldState, fid: str) -> bool:
    f = state.facts[fid]
    return f.visibility in ("shown", "available") or fid in state.knowledge.get(pc_id(state) or "", {})


def spot_lines(state: WorldState, eid: str, max_facts: int = 3) -> list[str]:  # rule: 12.2.4
    """A spotlight entity as the PC knows it (12.2.4 item 3): its name or unnamed label (a sealed one's slice and
    nothing more), then its details and the facts the PC perceived or learned about it, newest first. Never its
    world truth. Indented, so nobody reads it as present."""
    seal = state.seals.get(eid)
    if seal is not None:
        return [f"  {eid}: {seal.slice}"] if seal.slice else []
    e = state.entities[eid]
    role = e.data.get("role") if name_known(state, eid) else None
    out = [f"  {eid}: {display_name(state, eid)}" + (f" ({_short(role)})" if isinstance(role, str) and role else "")]
    shown = shown_details(state, [eid])[0]
    facts = [f for f in state.facts.values() if f.subject == eid and f.value is not None and _pc_knows(state, f.id)
             and f.id not in state.seals and f.visibility != "sealed" and f.predicate not in MOTIVES
             and not f.predicate.startswith("trg.") and (not f.predicate.startswith("detail.") or f.id in shown
                                                         or f.pinned)]
    facts.sort(key=lambda f: (not f.pinned, -f.valid_from_seq))  # a pinned correction first (12.3.6)
    out += [f"    {f.predicate}: {_short(f.value)}" for f in facts[:max_facts]]
    return out


def scene_card_lines(state: WorldState, spot: Sequence[str], room: int, rules: Any = None) -> list[str]:
    # rule: 12.2.4
    """At most `packet.max_scene_cards` cards (12.4.8 step 9) from ended scenes: each spotlight entity's latest
    first, then those of the people present, within `room` tokens."""
    rules = rules if rules is not None else load_rules()
    k = int(rules.pacing["packet"].get("max_scene_cards", 2))
    present = [i for i in (state.scene.cast_present if state.scene else []) if i in state.entities]
    picked: list[Any] = []
    for c in [*(c for i in spot for c in cards_for(state, [i], 1)), *cards_for(state, present, k)]:
        if c not in picked and len(picked) < k:
            picked.append(c)
    lines = [ln[:CARD_CHARS] for c in picked for ln in card_lines(state, c)]
    return fit(lines, lambda ln: tokens(ln), room)


# ---------------------------------------------------------------- per-role views (12.2.4 table, DL-12-75)

_PLAYER_SAID = re.compile(r"THE PLAYER'S MESSAGE: \"(.*)\"")


def view_ctx(message: str = "", exchanges: Sequence[Any] = (), focus: Iterable[str] = (),
             beat: Any = None, *, plain: bool = True) -> dict[str, Any]:
    """The `view_for` context from a packet's own parts: the player's words (the `THE PLAYER'S MESSAGE:` line of a
    Narrator or Director message; else the whole message when it is the player's own, `plain`), the last delivery
    (the last exchange's DM part), and the recent exchanges' text (`talk`: whom they name gets an identity line)."""
    said = _PLAYER_SAID.search(message)
    last = list(exchanges)[-1] if exchanges else ""
    dm = last if isinstance(last, str) else (list(last) + ["", ""])[1]
    words = said.group(1) if said else message if plain else ""  # a scene opening's setting names no one asked
    talk = "\n".join(render_exchange(e) for e in exchanges)
    return {"message": words, "last_delivery": str(dm or ""), "focus": list(focus), "beat": beat, "talk": talk}


def identity_lines(state: WorldState, ids: Iterable[str] = (), text: str = "") -> list[str]:  # rule: 12.2.4
    """12.2.4 item 3 (`pacing.yaml#packet.identity_lines: named_or_mentioned`): one line for each person in `ids` or
    named in `text`, present or absent: the name as the PC knows it, their pronouns and the PC's bond to them
    (02.9.2's `bond.` facts), so no call writes or reads around who someone is (I2 §2, §4). Never the PC, never a
    sealed person (INV-10).
    ponytail: capped at 12 lines; a budget key if casts grow past it"""
    from engine.retrieve.scene import resolve_names

    pc = pc_id(state)
    bonds = {f.value["npc"]: str(f.value.get("kind") or "bond") for f in state.facts.values()
             if f.subject == pc and f.predicate.startswith("bond.") and isinstance(f.value, dict)
             and f.value.get("npc") and state.current_fact_id(f.subject, f.predicate) == f.id}
    out: list[str] = []
    named: list[str] = [*ids, *(resolve_names(state, text) if text else [])]
    for eid in dict.fromkeys(named):
        e = state.entities.get(eid)
        if e is None or eid == pc or eid in state.seals or e.kind not in CAST_KINDS or len(out) >= 12:
            continue
        bits = [str(e.data.get("pronouns") or "pronouns not recorded")]
        if eid in bonds:
            bits.append(f"your {bonds[eid]}")
        out.append(f"  - {display_name(state, eid)}: {'; '.join(bits)}")
    return out


def _touched_threads(state: WorldState, threads: Mapping[str, Any], focus: Iterable[str], words: str) -> dict[str, Any]:
    # rule: 12.2.4
    """12.2.4 item 3 (`lead_line: when_new_or_relevant`): a thread's lead line only when the lead is new this turn
    or the turn touches it (it or the entity it points to is in focus or the spotlight, or the player's words share
    a content word with it); not in every packet (I1 §5: the levy line copied into 5 of 14 turns).
    ponytail: one shared content word counts as "asked about"; a stray match only costs one line of context"""
    from engine.audit.text import content

    near = set(focus)
    said = content(words)
    out: dict[str, Any] = {}
    for tid, name in threads.items():
        e = state.entities.get(tid)
        new = e is not None and e.introduced_at is not None and e.introduced_at == state.time.now
        points = (e.data.get("points_to") if e is not None else None) or None
        if new or tid in near or points in near or content(f"{name} {e.data.get('text', '') if e else ''}") & said:
            out[tid] = name
    return out


def _slim(e: Mapping[str, Any], keys: Iterable[str] = ("role", "aliases", "pronouns")) -> dict[str, Any]:
    """An entity block reduced to its name and the given data keys (names and aliases, 12.2.4 Reader row)."""
    out = {k: e[k] for k in ("id", "kind", "name", "name_unknown", "slice", "exists") if k in e}
    out["data"] = {k: v for k, v in (e.get("data") or {}).items() if k in keys}
    return out


def _no_motives(view: dict[str, Any]) -> dict[str, Any]:
    """The PC-knowledge layer (12.10.1): no motive keys on any entity, no motive facts (the seals and `truth` are
    already gone in `narrator_view`)."""
    view["entities"] = [{**e, "data": {k: v for k, v in (e.get("data") or {}).items() if k not in MOTIVES}}
                        for e in view.get("entities", [])]
    view["facts"] = [f for f in view.get("facts", []) if f.get("predicate") not in MOTIVES]
    return view


def view_for(role: Role, state: WorldState, ctx: Mapping[str, Any] | None = None) -> str:  # rule: 12.2.4
    """One role's projection of the turn's selection (12.2.4's per-role table): the same scope, ranking, spotlight
    and cards for every role, each reading only its columns.

    - Narrator: the PC-knowledge layer (no motives, `truth` or sealed content), the spotlight as the PC knows it,
      at most 2 scene cards.
    - Reader: names and aliases of the scene and spotlight entities, the PC's licences and conditions, the open
      pause (no facts, clocks, profiles or cards).
    - Framer: the target's and the place's records, positions and conditions, the facts about the target, the
      place and the PC (no PC sheet, cast list, threads or cards).
    - Director: threads, clocks, the cast list by weight, scene cards; the people present by name only.
    - World: the full selection plus cards (its motives are added by `roles/world.py`).
    Interpret and Checker read the plain scene view (the Checker's packet is built from strings)."""
    ctx = dict(ctx or {})
    focus = list(ctx.get("focus") or ())
    if role in (Role.INTERPRET, Role.CHECKER):
        return render_view(scene_view(state, focus))
    spot = spotlight(state, str(ctx.get("message") or ""), str(ctx.get("last_delivery") or ""), ctx.get("beat"))
    view = scene_view(state, focus, spot=spot, cards=role in (Role.NARRATOR, Role.DIRECTOR, Role.WORLD))
    pc = pc_id(state)
    if role in (Role.NARRATOR, Role.WORLD):  # the Director keeps every thread: picking leads is its job
        view["threads"] = _touched_threads(state, view["threads"], [*focus, *spot], str(ctx.get("message") or ""))
    if role == Role.NARRATOR:
        view = _no_motives(view)
    elif role == Role.READER:
        view = {"time": view["time"], "scene": view["scene"], "also_here": view["also_here"],
                "entities": [_slim(e) for e in view["entities"]],
                "licenses": {k: v for k, v in view["licenses"].items() if k == pc},
                "conditions": [c for c in view["conditions"] if c.get("target") == pc],
                "spotlight": [ln for ln in view["spotlight"] if not ln.startswith("    ")],
                "open_pause": view["open_pause"]}
    elif role == Role.FRAMER:
        target = beat_target(ctx.get("beat")) or next(iter(focus), None)
        place = state.scene.place_id if state.scene else None
        full = {target, place}
        view = _no_motives(view) | {
            "entities": [e if e["id"] in full else _slim(e, ()) for e in view["entities"]],
            "facts": [f for f in view["facts"] if f.get("subject") in {*full, pc}],
            "licenses": {}, "quantities": {k: v for k, v in view["quantities"].items() if k in full},
            "clocks": [], "threads": {}, "known": {}, "cards": [],
            "spotlight": spot_lines(state, target) if target in spot else []}
    elif role == Role.DIRECTOR:
        view = view | {"entities": [_slim(e, ()) for e in view["entities"]], "facts": [], "spotlight": [],
                       "positions": {k: v for k, v in view["positions"].items() if k == pc},
                       "licenses": {}, "quantities": {}, "conditions": []}
    text = render_view(view)
    if role == Role.NARRATOR:  # 12.2.4 item 3: who everyone here, in the spotlight or named is
        people = [e["id"] for e in view["entities"] if e["id"] in state.entities]
        lines = identity_lines(state, [*people, *spot, *(view.get("also_here_ids") or [])],
                               f"{ctx.get('message') or ''}\n{ctx.get('talk') or ''}")
        if lines:
            text += "\npeople here or named (name: pronouns; their tie to you):\n" + "\n".join(lines)
    if role == Role.READER:  # PR-12-12: testimony a beat may rest on (`rests_on`)
        from engine.dm.testimony import open_records

        recs = open_records(state)
        if recs:
            text += "\nTESTIMONY (unsettled; `rests_on` names the one the player's action relies on):\n" + "\n".join(
                f"{r['id']}: {display_name(state, r['speaker']) if r['speaker'] in state.entities else 'someone'}"
                f" said \"{_short(r['words'])}\"" for r in recs)
    return text




def _label(e: Mapping[str, Any]) -> str:
    """A present person in a few words: the name the PC knows them by (or a sealed one's slice), and the role."""
    if "slice" in e:
        return str(e["slice"])
    name, role = str(e.get("name", "")), (e.get("data") or {}).get("role")
    return f"{name} ({_short(role)})" if role and str(role) not in name else name


def _bare(tag: Any) -> str:
    return str(tag).rsplit(".", 1)[-1].replace("_", " ")


def _place_bits(place: Any) -> list[str]:
    d = place.data
    bits = [f"{place.name}" + (f", {d['desc']}" if d.get("desc") and d["desc"] != place.name else "")]
    for key, label in (("place_kind", "a"), ("openness", "openness")):
        if d.get(key):
            bits.append(f"{label} {d[key]}" if label == "a" else f"{d[key]} to the open air")
    terrain = [_bare(t) for t in (d.get("terrain") or [])]
    if terrain:
        bits.append("terrain: " + ", ".join(terrain))
    if d.get("climate"):
        bits.append(f"climate: {d['climate']}")
    for key in ("landmarks", "hazards"):
        if d.get(key):
            bits.append(f"{key}: " + ", ".join(str(x) for x in d[key]))
    return bits


def scene_setting(state: WorldState, *, full: bool = True) -> str:  # rule: 12.4.3
    # rule: 12.14.11
    """Material for describing the place, in words (never ids): the place and its desc, landmarks and openness, the
    town or region around it, the places beside it, who is here, and the hour, season and weather. Seed facts only:
    nothing here is invented, and the narrator may name ordinary furniture of such a place [revision: I-127].
    `full=False` (a later turn of the scene, DL-12-99): the look, furniture and description were given when the scene
    opened, so only the place's name and an "already described" line; people, exits and time stay."""
    sc = state.scene
    place = state.entities.get(sc.place_id) if sc and sc.place_id else None
    if place is None or place.id in state.seals:
        return ""
    d = place.data
    if not full:
        lines = ["SCENE SETTING (already described this scene: do not describe the place again unless the character "
                 "looks around or asks; people here act only as the record says):", f"- place: {place.name}"]
    else:
        lines = ["SCENE SETTING (what the character sees here; describe the place from this, naming ordinary "
                 "furniture of such a place as needed; people here act only as the record says, so show how they "
                 "look and stand):", "- place: " + "; ".join(_place_bits(place))]
        if d.get("look"):  # the seed pack (12.16.9): the layout is read from the store, never invented (12.4.3)
            lines.append(f"- look: {d['look']}")
        if d.get("furniture"):
            lines.append("- furniture: " + ", ".join(str(x) for x in d["furniture"]))
    exits = [state.entities[x].name for x in d.get("exits") or [] if x in state.entities and x not in state.seals]
    if exits:
        lines.append("- exits: toward " + ", ".join(exits))
    parent = state.entities.get(d.get("parent") or "") if full else None
    while parent is not None and parent.id not in state.seals:
        pd = parent.data
        lines.append(f"- within: {parent.name}" + (f", {pd['desc']}" if pd.get("desc") else ""))
        parent = state.entities.get(pd.get("parent") or "") if pd.get("place_kind") != "settlement" else None
    near = [e for e in state.entities.values() if full and e.kind == "place" and e.id != place.id
            and e.id not in state.seals and e.data.get("parent") == d.get("parent") and e.exists == "exists"
            and e.data.get("known", True)]
    if near:
        lines.append("- nearby: " + "; ".join(e.data.get("desc") or e.name for e in near[:8]))
    from engine.world.scenes import cast_present

    present: dict[str, str] = {}
    short: dict[str, str] = {}
    for i in cast_order(state, [i for i in cast_present(state) if i not in state.seals]):  # met mid-scene too (P-056)
        ed = state.entities[i].data
        # pronouns first: a person squeezed out of the view's full profiles keeps them (playtest 20261008-145410:
        # Ysrion, she/her, narrated "he" all game; the pronoun precision check, 12.3.2)
        look = ", ".join(str(ed[k]) for k in ("pronouns", "age", "detail", "demeanor") if ed.get(k))
        who = display_name(state, i)
        role = f", the {ed['role']}" if ed.get("role") and str(ed["role"]) not in who else ""
        call = "" if name_known(state, i) else f'; call them "{who}", as every other screen does'  # P-095
        present[i] = f"- present: {who}{role}" + (f" ({look})" if look else "") + call
        short[i] = who + (f" ({ed['role']})" if role else "")
    budget = view_budget()  # the cast budget, as the view's (R2-A2): the rest share one line
    shown = fit(list(present), lambda i: tokens(present[i]), budget["cast"])
    lines.extend(present[i] for i in cast_present(state) if i in shown)  # in the scene's order, as the view
    rest = {i: short[i] for i in present if i not in shown}
    if rest:
        lines.append("- " + also_here(rest, budget["cast_line"], ids=False))
    from engine.dm.incident import incident_line

    matter = incident_line(state)  # the opening incident's person, as the character knows it (P-067)
    if matter:
        lines.append(f"- the matter at hand (the character knows): {matter}")
    now = (state.time.model_dump(mode="json").get("now") or {})
    watch = now.get("watch")
    when = WATCHES[watch] if isinstance(watch, int) and 0 <= watch < len(WATCHES) else None
    weather = next((f for f in state.facts.values() if f.subject == "world" and f.predicate == "weather"), None)
    lines.append(f"- time: {when or 'now'}, season {now.get('season')}, day {now.get('day')}"
                 + ("; weather: " + str(weather.value) if weather is not None else ""))
    return "\n".join(lines)


def _short(v: Any) -> str:
    if isinstance(v, Mapping):
        text = ", ".join(f"{k}={_short(x)}" for k, x in v.items())
    elif isinstance(v, list | tuple):
        text = ", ".join(_short(x) for x in v)
    else:
        text = str(v)
    return text if len(text) <= MAX_VALUE_CHARS else text[: MAX_VALUE_CHARS - 1] + "…"


def _time_line(t: Mapping[str, Any]) -> str:
    now = t.get("now", {}) or {}
    watch = now.get("watch", 0)
    w = WATCHES[watch] if isinstance(watch, int) and 0 <= watch < len(WATCHES) else str(watch)
    return (f"time: year {now.get('year')}, season {now.get('season')}, week {now.get('week')}, "
            f"day {now.get('day')}, {w} (mode {t.get('mode')})")


def render_view(view: Mapping[str, Any]) -> str:
    """Compact text of a `scene_view` dict: one line per item, entity names on `name:` lines."""
    lines: list[str] = [view["calendar"]] if view.get("calendar") else []  # rule: 12.2.4 (pinned first)
    if view.get("time"):
        lines.append(_time_line(view["time"]))
    sc = view.get("scene")
    if sc:
        lines.append(f"scene: {sc.get('scene_id')} at {sc.get('place_id') or 'nowhere named'}; mode {sc.get('mode')}")
        for key in ("agenda", "hoped_answer"):
            if sc.get(key):
                lines.append(f"  {key}: {sc[key]}")
        if sc.get("situation_tags"):
            lines.append(f"  situation: {', '.join(sc['situation_tags'])}")
    else:
        lines.append("scene: none")
    for e in view.get("entities", []):
        lines.extend(_entity_lines(view, e))
    if view.get("also_here"):
        lines.append(view["also_here"])
    if view.get("facts"):
        lines.append("facts:")
        lines.extend(f"  {f['id']} about {f['subject']}: {f['predicate']} = {_short(f['value'])}"
                     + (f" ({f['certainty']})" if f.get("certainty") not in (None, "established") else "")
                     + (" (corrected by the player's report; keep it)" if f.get("pinned") else "")
                     for f in view["facts"])
    if view.get("clocks"):
        lines.append("clocks:")
        for c in view["clocks"]:
            fill = f" {c['filled']}/{c['segments']}" if "filled" in c else ""
            lines.append(f"  {c['id']}: {c['name']} ({c['kind']}){fill}")
    for key, label in (("threads", "open threads"), ("known", "cast list")):
        if view.get(key):
            lines.append(f"{label}: " + "; ".join(f"{i} {n}" for i, n in view[key].items()))
    if view.get("spotlight"):  # rule: 12.2.4
        lines.append("not here (named or linked; as the character knows them):")
        lines.extend(view["spotlight"])
    if view.get("cards"):  # rule: 12.4.8
        lines.append("earlier scenes (from the record):")
        lines.extend(f"  {c}" for c in view["cards"])
    pause = view.get("open_pause")
    if pause:
        choices = ", ".join(c.get("id", "") for c in pause.get("choices", []))
        lines.append(f"open pause: {pause.get('pause_id')} {pause.get('kind')}: {pause.get('prompt', '')}"
                     + (f" (choices: {choices})" if choices else ""))
    return "\n".join(lines)


def _entity_lines(view: Mapping[str, Any], e: Mapping[str, Any]) -> list[str]:
    """One entity's block in the view: `<id>: <name>`, its `name:` line, then its record."""
    eid = e["id"]
    if "slice" in e:
        return [f"{eid}: {e['slice']}"]
    lines = [f"{eid}: {e.get('name', '')}"]
    lines.append(f"  name: {e.get('name', '')}")
    if e.get("name_unknown"):  # rule: 12.10.2
        lines.append(f"  the character does not know their name: call them \"{e.get('name', '')}\" (the words "
                     "every other screen uses; add how they look if you like), never by a name (not even one "
                     "in the id) until the record says they gave it")
    if e.get("exists") not in (None, "exists"):
        lines.append(f"  state: {e['exists']}")
    if e.get("tags"):
        lines.append(f"  tags: {_short(e['tags'])}")
    data = e.get("data") or {}
    keys = [k for k in _DESCRIPTIVE_KEYS if k in data] + [k for k in data if k not in _DESCRIPTIVE_KEYS]
    for k, v in [(k, data[k]) for k in keys][:MAX_DATA_KEYS]:
        if k not in ("name", "name_known"):
            lines.append(f"  {k}: {_short(v)}")
    qs = (view.get("quantities") or {}).get(eid, {})
    if qs:
        lines.append("  quantities: " + "; ".join(
            f"{n} {q['current']}" + (f"/{q['max']}" if q.get("max") is not None else "") for n, q in qs.items()))
    conds = [c for c in view.get("conditions", []) if c.get("target") == eid]
    if conds:
        lines.append("  conditions: " + "; ".join(f"{c['condition_id']} {c['severity']}" for c in conds))
    lic = (view.get("licenses") or {}).get(eid, [])
    if lic:
        lines.append("  licences: " + ", ".join(f"{x['license_id']} ({x.get('grade', '')})" for x in lic))
    pos = (view.get("positions") or {}).get(eid)
    if pos and (pos.get("location") or pos.get("flags")):
        lines.append(f"  position: {pos.get('location') or ''} {_short(pos.get('flags') or [])}".rstrip())
    return lines


# ---------------------------------------------------------------- packet


def render_card(card: RuleCard | str) -> str:
    return card if isinstance(card, str) else card.body.strip()


def render_triggers(triggers: Iterable[ActiveTrigger | str]) -> str:  # rule: 12.2.4
    """The active-trigger list: travels with every call at the head of the view, not in the core (DL-12-38)."""
    lines = [t if isinstance(t, str) else t.line() for t in triggers]
    return "Active triggers: " + ("none" if not lines else "\n" + "\n".join(f"- {x}" for x in lines))


def render_exchange(ex: str | tuple[str, str] | Sequence[str]) -> str:
    if isinstance(ex, str):
        return ex
    player, dm = (list(ex) + ["", ""])[:2]
    return f"Player: {player}\nDM: {dm}"


def turn_exchanges(ctx: Any, n: int) -> list[tuple[str, str]]:  # rule: 12.2.4
    """The last `n` exchanges before this turn, from the turn log (12.2.4's role table: the Director 2, the World 1;
    DL-12-104), so a role whose prompt promises RECENT EXCHANGES gets them without its callers passing them."""
    from engine.dm.turn import recent_exchanges

    return recent_exchanges(ctx.store, ctx.turn_id, n) if ctx.turn_id else []


def verbatim_exchanges(rules: Any = None) -> int:  # rule: 12.2.4
    rules = rules if rules is not None else load_rules()
    return int(rules.pacing.get("packet", {}).get("verbatim_exchanges", VERBATIM_EXCHANGES))


def name_line(state: WorldState, eid: str) -> str:
    """`<id>: <name as the PC knows it>` (a sealed entity: its slice or "someone")."""
    e = state.entities.get(eid)
    if e is None:
        return f"{eid}: someone"
    seal = state.seals.get(eid)
    return f"{eid}: {seal.slice or 'someone'}" if seal is not None else f"{eid}: {display_name(state, eid)}"


_CARD_SKIP = ("name", "voice", "activity", "exists", "harm_state", "stance.said")
_CARD_SKIP_PREFIX = ("knows_", "points_to.", "trg.", "detail.", "asked_", "case.", "bond.", "memory.", "said.")


def _card_fact(state: WorldState, f: Any) -> bool:
    """A fact the speaker card may show: in the world, never sealed, never bookkeeping or a motive (INV-10)."""
    return (isinstance(f.value, str | bool | int | float) and f.visibility != "sealed" and f.id not in state.seals
            and f.subject not in state.seals and f.predicate not in _CARD_SKIP and f.predicate not in MOTIVES
            and not f.predicate.startswith(_CARD_SKIP_PREFIX) and not f.predicate.startswith("who_is_")
            and state.current_fact_id(f.subject, f.predicate) == f.id)


def speaker_card(state: WorldState, npc: str, *, topic: str | None = None, about: str | None = None,
                 rules: Any = None) -> list[str]:  # rule: PR-12-10
    # rule: 12.10.8
    """PR-12-10 step 3 (`answer_ladder.speaker_card`): for the asked or addressed NPC, what they know (their
    knowledge records and their seeded pack's ordinary facts, those on the topic first), their role's common
    knowledge topics, public news in their scope (open threads), and their recent `said` records
    (`answer_ladder.said_shown`) plus every one on the topic. Never a sealed fact, an undelivered placement (a case
    lives in meta, never here) or a motive (INV-10)."""
    from engine.dm.testimony import said_by
    from engine.gen._seed_packs import pack_data, role_key

    e = state.entities.get(npc)
    if e is None or npc in state.seals:
        return []
    rules = rules or load_rules()
    ck = pack_data().CK
    shown = int((rules.pacing.get("answer_ladder") or {}).get("said_shown", 6))

    def on(text_topic: str | None, subj: str | None) -> bool:
        return bool((topic and text_topic == topic) or (about and subj == about))

    mine = {fid for fid in state.knowledge.get(npc, {}) if fid in state.facts}  # 12.10.6 (a)-(b): records, own facts
    mine |= {f.id for f in state.facts.values() if f.subject == npc and f.visibility in ("shown", "available")}
    facts = sorted((state.facts[fid] for fid in sorted(mine) if _card_fact(state, state.facts[fid])),
                   key=lambda f: not on(f.predicate.split(".")[1] if f.predicate.startswith("topic.") else None,
                                        f.subject))
    known = [str(f.value) if f.predicate.startswith("topic.") and isinstance(f.value, str)
             else f"{display_name(state, f.subject) if f.subject in state.entities else ''} "
                  f"{f.predicate.replace('_', ' ').replace('.', ' ')} {f.value}".strip() for f in facts[:5]]
    pack = sorted((k for k in e.data.get("knowledge") or [] if k.get("text") and k.get("slot") != "rumor"),
                  key=lambda k: not on(k.get("topic"), k.get("about")))
    for k in pack[:4]:
        if str(k["text"]) not in known:
            known.append(str(k["text"]))
    roles = [f"{t} ({ck['topics'][t]['gist']})" for t in ck["by_role"].get(role_key({"role": e.data.get("role")}), [])
             if t in ck["topics"]]
    news = [str(t.data.get("text") or t.name) for t in state.entities.values()
            if t.kind == "thread" and t.data.get("status", "active") == "active"
            and t.visibility in ("shown", "available") and t.id not in state.seals][:3]
    said = said_by(state, npc, topic=topic, about=about, k=shown)
    out = [f"SPEAKER CARD for {display_name(state, npc)} (PR-12-10: answer from this first; beyond it, plainly, with "
           "ordinary confidence; a hedge only if they are cautious or gossipy; never open by saying their own name or "
           "title unless asked):"]
    out += [f"- knows: {_short(x)}" for x in known] or ["- knows: nothing on record (answer plainly about ordinary things)"]
    if roles:
        out.append("- their trade's common knowledge: " + "; ".join(roles))
    if news:
        out.append("- public news anyone here may know: " + "; ".join(_short(x) for x in news))
    if said:
        out.append("- they already said (never contradict or repeat these unprompted; build on them):")
        out += [f"  - \"{_short(r['words'])}\"" for r in said]
    return out


def build_packet(  # rule: 12.2.4
    role: Role,
    *,
    instructions: str,
    cards: Sequence[RuleCard | str],
    view: WorldState | Mapping[str, Any] | str,
    exchanges: Sequence[str | tuple[str, str]],
    message: str,
    triggers: Iterable[ActiveTrigger | str] = (),
    quiet_turns: int | None = None,
    notes: Iterable[str] = (),
    focus: Iterable[str] = (),
    rules: Any = None,
    beat: Any = None,
) -> Packet:
    """One call's packet in contract order. Raises PacketError over the card cap.

    `notes` are extra per-call lines shown after the view (e.g. the Framer's anchor menu); `quiet_turns`
    adds a `quiet_turns: N` line for the Director. `focus` (`focus_ids`) feeds a `WorldState` view's ranking;
    pass the same ids to `schema_context` so the fact enum is the view's.
    """
    rules = rules if rules is not None else load_rules()
    cap = max_cards(rules)
    if len(cards) > cap:
        raise PacketError(f"{role.value}: {len(cards)} cards, the cap is {cap} plus the core (00.15.4)")
    if isinstance(view, WorldState):  # one selection, this role's projection (12.2.4, DL-12-75)
        plain = role in (Role.READER, Role.FRAMER, Role.INTERPRET)  # their message is the player's (or beat's) words
        view_text = view_for(role, view, view_ctx(message, exchanges, focus, beat, plain=plain))
    elif isinstance(view, Mapping):
        view_text = render_view(view)
    else:
        view_text = view
    extra = list(notes)
    if quiet_turns is not None:
        extra.append(f"quiet_turns: {quiet_turns}")
    view_text = "\n".join(filter(None, [render_triggers(triggers), view_text, *extra]))
    keep = ROLE_EXCHANGES.get(role, verbatim_exchanges(rules))
    recent = list(exchanges)[-keep:] if keep > 0 else []
    return Packet(
        instructions=instructions,
        core=guidance_digest(role, rules),  # 12.2.4 item 1: the role's guidance, never the 00.15.4 core
        cards=[render_card(c) for c in cards],
        view=view_text,
        exchanges=[render_exchange(e) for e in recent],
        message=message,
    )
