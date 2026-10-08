"""The one packet builder every role uses (contracts/model-calls.md "Packet order"; 12.2.4; FR-029; T106).

    packet = build_packet(Role.READER, instructions=text, cards=load_cards_for(...), view=state,
                          exchanges=last_exchanges, message=player_text, triggers=active, quiet_turns=2)

Order: role instructions -> always-loaded core (00.15.4 cards + the active-trigger list) -> loaded cards
(at most `pacing.yaml#packet.max_loaded_cards`, 12; more is a caller error) -> narrator view -> the last
`packet.verbatim_exchanges` (4) exchanges verbatim -> this message verbatim. Stable sections come first, for
prompt caching.

`view` may be a `WorldState` (rendered with `scene_view` + `render_view`), a narrator-view dict (rendered), or a
pre-rendered string. The rendered view is scene-scoped and capped (scene facts, clocks, threads, known
cast, data keys), so the packet does not grow with the length of the game (SC-002). Each entity is rendered
as `<id>: <name>` and then a `name: <name>` line: the offline model reads names from `name:` lines and entity
aliases from the text after an id.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from engine.build.compile_cards import CardIndex, RuleCard
from engine.data.loader import load_rules
from engine.llm.base import Packet, Role
from engine.retrieve.cards import core_cards, max_cards
from engine.retrieve.scene import entity_names, scene_facts, scene_scope
from engine.retrieve.triggers import ActiveTrigger
from engine.store.projection import WorldState
from engine.store.views import narrator_view

VERBATIM_EXCHANGES = 4  # fallback; the rules value is pacing.yaml#packet.verbatim_exchanges
MAX_VIEW_CLOCKS = 8
MAX_VIEW_THREADS = 8
MAX_VIEW_KNOWN = 12  # the cast list beyond the scene: most recently introduced first
MAX_DATA_KEYS = 12
MAX_VALUE_CHARS = 160
WATCHES = ("morning", "afternoon", "evening", "night")
_DESCRIPTIVE_KEYS = ("pronouns", "desc", "landmarks", "hazards", "openness", "role", "detail", "demeanor")  # first under the cap


class PacketError(ValueError):
    """A packet that breaks the 00.15.4 caps (a caller bug, never a model failure)."""


# ---------------------------------------------------------------- view


def scene_view(state: WorldState) -> dict[str, Any]:  # rule: 12.2.4
    """The narrator view of the current scene, bounded (12.2.4 item 3). Nothing sealed is in it (INV-10)."""
    scope = scene_scope(state)
    nv = narrator_view(state, scope)
    visible_facts = nv["facts"]
    facts = [visible_facts[f.id] for f in scene_facts(state, scope) if f.id in visible_facts]
    clocks = [c for c in nv["clocks"].values() if c.get("status") == "active"][-MAX_VIEW_CLOCKS:]
    others = [eid for eid, e in state.entities.items() if eid not in scope]
    threads = [i for i in others if state.entities[i].kind == "thread"][-MAX_VIEW_THREADS:]
    known = [i for i in others if state.entities[i].kind in ("npc", "companion", "faction")][-MAX_VIEW_KNOWN:]
    return {
        "time": nv["time"],
        "scene": nv["scene"],
        "entities": [nv["entities"][i] for i in scope if i in nv["entities"]],
        "quantities": nv["quantities"],
        "conditions": list(nv["conditions"].values()),
        "licenses": nv["licenses"],
        "positions": nv["positions"],
        "facts": facts,
        "clocks": clocks,
        "threads": entity_names(state, list(reversed(threads))),
        "known": entity_names(state, list(reversed(known))),
        "open_pause": nv["open_pause"],
    }


def _bare(tag: Any) -> str:
    return str(tag).rsplit(".", 1)[-1].replace("_", " ")


def scene_setting(state: WorldState) -> str:  # rule: 12.4.3
    """Material for describing the place, in words (never ids): the place and its desc, landmarks and openness, the
    town or region around it, the places beside it, who is here, and the hour, season and weather. Seed facts only:
    nothing here is invented, and the narrator may name ordinary furniture of such a place [revision: I-127]."""
    sc = state.scene
    place = state.entities.get(sc.place_id) if sc and sc.place_id else None
    if place is None or place.id in state.seals:
        return ""
    d = place.data
    lines = ["SCENE SETTING (what the character sees here; describe the place from this, naming ordinary furniture "
             "of such a place as needed; people here act only as the record says, so show how they look and stand):"]
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
    lines.append("- place: " + "; ".join(bits))
    parent = state.entities.get(d.get("parent") or "")
    while parent is not None and parent.id not in state.seals:
        pd = parent.data
        lines.append(f"- within: {parent.name}" + (f", {pd['desc']}" if pd.get("desc") else ""))
        parent = state.entities.get(pd.get("parent") or "") if pd.get("place_kind") != "settlement" else None
    near = [e for e in state.entities.values() if e.kind == "place" and e.id != place.id and e.id not in state.seals
            and e.data.get("parent") == d.get("parent") and e.exists == "exists" and e.data.get("known", True)]
    if near:
        lines.append("- nearby: " + "; ".join(e.data.get("desc") or e.name for e in near[:8]))
    from engine.world.scenes import cast_present

    here = [state.entities[i] for i in cast_present(state) if i not in state.seals]  # met mid-scene too (P-056)
    for e in here:
        ed = e.data
        look = ", ".join(str(ed[k]) for k in ("age", "detail", "demeanor") if ed.get(k))
        lines.append(f"- present: {e.name}" + (f", the {ed['role']}" if ed.get("role") else "") + (f" ({look})" if look else ""))
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
    lines: list[str] = []
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
        eid = e["id"]
        if "slice" in e:
            lines.append(f"{eid}: {e['slice']}")
            continue
        lines.append(f"{eid}: {e.get('name', '')}")
        lines.append(f"  name: {e.get('name', '')}")
        if e.get("exists") not in (None, "exists"):
            lines.append(f"  state: {e['exists']}")
        if e.get("tags"):
            lines.append(f"  tags: {_short(e['tags'])}")
        data = e.get("data") or {}
        keys = [k for k in _DESCRIPTIVE_KEYS if k in data] + [k for k in data if k not in _DESCRIPTIVE_KEYS]
        for k, v in [(k, data[k]) for k in keys][:MAX_DATA_KEYS]:
            if k != "name":
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
    if view.get("facts"):
        lines.append("facts:")
        lines.extend(f"  {f['id']} about {f['subject']}: {f['predicate']} = {_short(f['value'])}"
                     + (f" ({f['certainty']})" if f.get("certainty") not in (None, "established") else "")
                     for f in view["facts"])
    if view.get("clocks"):
        lines.append("clocks:")
        for c in view["clocks"]:
            fill = f" {c['filled']}/{c['segments']}" if "filled" in c else ""
            lines.append(f"  {c['id']}: {c['name']} ({c['kind']}){fill}")
    for key, label in (("threads", "open threads"), ("known", "cast list")):
        if view.get(key):
            lines.append(f"{label}: " + "; ".join(f"{i} {n}" for i, n in view[key].items()))
    pause = view.get("open_pause")
    if pause:
        choices = ", ".join(c.get("id", "") for c in pause.get("choices", []))
        lines.append(f"open pause: {pause.get('pause_id')} {pause.get('kind')}: {pause.get('prompt', '')}"
                     + (f" (choices: {choices})" if choices else ""))
    return "\n".join(lines)


# ---------------------------------------------------------------- packet


def render_card(card: RuleCard | str) -> str:
    return card if isinstance(card, str) else card.body.strip()


def render_core(index: CardIndex | None, triggers: Iterable[ActiveTrigger | str]) -> str:  # rule: 00.15.4
    """The always-loaded core: the 00.15.4 cards and the active-trigger list."""
    parts = [c.body.strip() for c in core_cards(index)]
    lines = [t if isinstance(t, str) else t.line() for t in triggers]
    parts.append("Active triggers: " + ("none" if not lines else "\n" + "\n".join(f"- {x}" for x in lines)))
    return "\n\n".join(parts)


def render_exchange(ex: str | tuple[str, str] | Sequence[str]) -> str:
    if isinstance(ex, str):
        return ex
    player, dm = (list(ex) + ["", ""])[:2]
    return f"Player: {player}\nDM: {dm}"


def verbatim_exchanges(rules: Any = None) -> int:  # rule: 12.2.4
    rules = rules if rules is not None else load_rules()
    return int(rules.pacing.get("packet", {}).get("verbatim_exchanges", VERBATIM_EXCHANGES))


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
    rules: Any = None,
    index: CardIndex | None = None,
) -> Packet:
    """One call's packet in contract order. Raises PacketError over the card cap.

    `notes` are extra per-call lines shown after the view (e.g. the Framer's anchor menu); `quiet_turns`
    adds a `quiet_turns: N` line for the Director.
    """
    rules = rules if rules is not None else load_rules()
    cap = max_cards(rules)
    if len(cards) > cap:
        raise PacketError(f"{role.value}: {len(cards)} cards, the cap is {cap} plus the core (00.15.4)")
    if isinstance(view, WorldState):
        view_text = render_view(scene_view(view))
    elif isinstance(view, Mapping):
        view_text = render_view(view)
    else:
        view_text = view
    extra = list(notes)
    if quiet_turns is not None:
        extra.append(f"quiet_turns: {quiet_turns}")
    if extra:
        view_text = "\n".join([view_text, *extra]) if view_text else "\n".join(extra)
    keep = verbatim_exchanges(rules)
    recent = list(exchanges)[-keep:] if keep > 0 else []
    return Packet(
        instructions=instructions,
        core=render_core(index, triggers),
        cards=[render_card(c) for c in cards],
        view=view_text,
        exchanges=[render_exchange(e) for e in recent],
        message=message,
    )
