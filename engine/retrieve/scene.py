"""The scene's slice of state, shared by the packet view and the schema enums (12.2.4 item 3; FR-029, SC-002).

    scope = scene_scope(state)            # the PC, the scene's cast, its place, the things lying there
    facts = scene_facts(state, scope, focus=focus_ids(state, message, target))   # pins, then the ranked fill

Both are bounded by token budgets (`pacing.yaml#packet.view_budget`) so that a packet (and a schema) does not
grow with the length of the game: everything else lives in state and reaches a call only through these slices.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from typing import Any, TypeVar

from engine.data.loader import load_rules
from engine.store.details import active_details
from engine.store.projection import FactRecord, WorldState
from engine.store.views import display_name

T = TypeVar("T")
VALUE_CHARS = 160  # a fact value as the view shows it (packet.MAX_VALUE_CHARS)
READING = re.compile(r"\b(read|reads|reading|wording|inscription|lettering|what (?:does|do|did) (?:it|the \w+|they) "
                     r"say|what it says|what's written|what is written)\b", re.I)  # the player reads something
CAST_KINDS = ("npc", "companion", "adversary")  # people who can be present (as engine.world.places.cast_at)
WRITTEN = ("text","inscription", "reads", "words", "says", "wording", "writing")  # a thing's written words (P-110)


def written_words(state: WorldState, eid: str) -> Any:
    """The words written on a thing, as stored (its `text` fact or a synonym), else None."""
    return next((v for k in WRITTEN if (v := state.fact_value(eid, k)) is not None), None)


def cannot_read(state: WorldState, pc: str | None, eid: str | None) -> str:  # rule: 02.4.6
    """Why the PC cannot read what is written on `eid` (plain words), or "" when they can. Letters lets a character
    read every tongue they hold at accented or native; writing with no recorded tongue is in the common speech.
    `eid` None asks only whether the PC reads at all."""
    held = {x.license_id: x.grade for x in state.licenses.get(pc or "", [])}
    if not any(k.startswith("lic.lang.") for k in held):
        return ""  # no tongues recorded (a bare test PC): literacy is not known to be lacking
    if "lic.lang.letters" not in held:
        return "they never learned their letters"
    lang = next((str(v) for k in ("language", "tongue", "script")
                 if eid and (v := state.fact_value(eid, k)) is not None), "")
    if not lang or re.search(r"\bcommon\b|-speech\b", lang, re.I):
        lic = "lic.lang.common"
    else:
        want = f" {re.sub(r'[^a-z]+', ' ', lang.lower())} "  # "the Old Tongue" -> lic.lang.old_tongue
        lic = next((k for k in held if k.startswith("lic.lang.") and f" {k[9:].replace('_', ' ')} " in want), "")
    return "" if held.get(lic) in ("accented", "native") else f"it is written in {lang or 'the common speech'}, which they do not read"


def pc_id(state: WorldState) -> str | None:
    """The player character's entity id (the first `pc` entity)."""
    return next((eid for eid, e in state.entities.items() if e.kind == "pc"), None)


def tokens(text: str) -> int:
    """The rough token count the view budgets use (about four characters a token, as rule cards count)."""
    return (len(text) + 3) // 4


def view_budget(rules: Any = None) -> dict[str, int]:  # rule: 12.2.4
    """Tokens per view section (`pacing.yaml#packet.view_budget`)."""
    rules = rules if rules is not None else load_rules()
    return {k: int(v) for k, v in rules.pacing["packet"]["view_budget"].items()}


def fit(rows: Iterable[T], cost: Callable[[T], int], room: int) -> list[T]:  # rule: 12.2.4
    """The rows, in order, that fit in `room` tokens (a row too big for what is left is skipped)."""
    out: list[T] = []
    for r in rows:
        c = cost(r)
        if c <= room:
            out.append(r)
            room -= c
    return out


def _entity_tokens(state: WorldState, eid: str) -> int:
    e = state.entities[eid]
    data = "".join(f"\n  {k}: {str(v)[:VALUE_CHARS]}" for k, v in list(e.data.items())[:12])
    return tokens(f"{eid}: {e.name}\n  name: {e.name}{data}")


def scene_scope(state: WorldState, budget: dict[str, int] | None = None) -> list[str]:  # rule: 12.2.4
    """Entity ids in the current scene: the PC, the cast present, the place and the things lying there. Existing
    entities only. Things with written words are pinned; the other things fill `view_budget.things`, newest
    first."""
    ids: list[str] = []
    pc = pc_id(state)
    if pc:
        ids.append(pc)
    if state.scene is not None:
        ids.extend(state.scene.cast_present)
        if state.scene.place_id:
            ids.append(state.scene.place_id)
            here = [eid for eid, p in state.positions.items() if p.location == state.scene.place_id
                    and eid in state.entities and state.entities[eid].kind in ("object", "item")
                    and state.entities[eid].exists == "exists"]
            pinned = {i for i in here if written_words(state, i) is not None}
            room = (budget or view_budget())["things"]
            kept = set(fit([i for i in reversed(here) if i not in pinned], lambda i: _entity_tokens(state, i), room))
            ids.extend(i for i in here if i in pinned or i in kept)
    return [i for i in dict.fromkeys(ids) if i in state.entities]


def cast_order(state: WorldState, people: Iterable[str], focus: Iterable[str] = ()) -> list[str]:  # rule: 12.2.4
    """The people present, most deserving of a full profile first (12.2.4 item 3): the beat's target and anyone
    the message names (`focus`), then those the PC dealt with most recently (the newest fact about them the PC
    learned, or memory of the PC they hold), then by 12.6.6 weight, newest introduced first."""
    want = set(focus)
    last: dict[str, int] = {}
    for fid, k in state.knowledge.get(pc_id(state) or "", {}).items():
        if (f := state.facts.get(fid)) is not None:
            last[f.subject] = max(last.get(f.subject, 0), k.seq)
    for f in state.facts.values():
        if f.predicate.startswith("memory."):
            last[f.subject] = max(last.get(f.subject, 0), f.valid_from_seq)
    weights = state.meta.get("cast_list") or {}
    order = {eid: n for n, eid in enumerate(state.entities)}
    return sorted(people, key=lambda i: (i not in want, -last.get(i, 0), -int(weights.get(i, 1)), -order.get(i, 0)))


def also_here(labels: dict[str, str], room: int, *, ids: bool = True) -> str:  # rule: 12.2.4
    """One compact line naming the people present without a full profile (`id label`, or the label alone), within
    `room` tokens; the ones that do not fit are counted ("and N more"), so nobody present vanishes from sight."""
    words = {i: f"{i} {v}" if ids else v for i, v in labels.items()}
    kept = fit(list(words), lambda i: tokens(words[i] + "; "), room)
    more = len(words) - len(kept)
    return "also here: " + "; ".join([*(words[i] for i in kept), *([f"and {more} more"] if more else [])])


def _sealed(state: WorldState, f: FactRecord) -> bool:
    if f.id in state.seals or f.visibility == "sealed":
        return True
    return f.subject in state.seals and not state.seals[f.subject].slice


def focus_ids(state: WorldState, text: str = "", target: str | None = None) -> list[str]:  # rule: 12.2.4
    """What the call is about, for `scene_facts`' relevance: the beat's target and every entity named in `text`
    (the player's message) by the name the PC knows it by."""
    low = text.lower()
    named = [eid for eid in state.entities if eid not in state.seals
             and len(n := display_name(state, eid).lower()) > 2 and re.search(rf"\b{re.escape(n)}\b", low)]
    return list(dict.fromkeys([*([target] if target in state.entities else []), *named]))


SPOT_KINDS = ("npc", "companion", "adversary", "faction", "place", "item", "object")  # what can be named and shown
_PROPER_RUN = re.compile(r"\b[A-Z][\w'’-]+(?:\s+[A-Z][\w'’-]+)+")  # "Joss Fenn": a full name the index may not hold


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w'’ -]+", " ", text.lower())).strip()


def _nameable(state: WorldState, eid: str) -> bool:
    e = state.entities.get(eid)
    seal = state.seals.get(eid)
    return e is not None and e.kind in SPOT_KINDS and (seal is None or bool(seal.slice))


def alias_index(state: WorldState) -> tuple[dict[str, list[str]], dict[str, list[str]]]:  # rule: 12.2.4
    """(strong, weak) key -> ids. Strong: the name the PC knows (the full name once learned, else the unnamed
    label, 12.10.2), the narration's aliases, a sealed thing's permitted slice. Weak: the given and family names of
    a person whose name is known. A true name the PC has not learned is never a key, so a match cannot leak it."""
    from engine.store.views import name_known

    strong: dict[str, list[str]] = {}
    weak: dict[str, list[str]] = {}
    for eid, e in state.entities.items():
        if not _nameable(state, eid):
            continue
        seal = state.seals.get(eid)
        keys = [seal.slice] if seal is not None and seal.slice else [display_name(state, eid)]
        keys += [a for a in e.data.get("aliases") or [] if isinstance(a, str)] if seal is None else []
        for k in {_norm(str(x)) for x in keys if x}:
            if len(k) > 2:
                strong.setdefault(k, []).append(eid)
        if seal is None and e.kind in CAST_KINDS and name_known(state, eid):
            for part in {_norm(w) for w in str(e.name).split()}:
                if len(part) > 2:
                    weak.setdefault(part, []).append(eid)
    return strong, weak


def resolve_names(state: WorldState, text: str, index: Any = None) -> list[str]:  # rule: 12.2.4
    """Ids named in `text`, in order of mention. Full names and aliases first (longest key first; a matched span is
    used once); then a lone given or family name, only when one person carries it and it is not part of a longer
    proper name ("Joss Fenn" names neither Joss Dunmere nor Pell Fenn). Ambiguous keys name nobody."""
    strong, weak = index or alias_index(state)
    low = text.lower()
    hits: list[tuple[int, str]] = []
    for key in sorted(strong, key=len, reverse=True):
        if len(strong[key]) != 1:
            continue
        for m in re.finditer(rf"(?<![\w]){re.escape(key)}(?![\w])", low):
            hits.append((m.start(), strong[key][0]))
            low = low[:m.start()] + " " * len(key) + low[m.end():]
    runs = [(m.start(), m.end()) for m in _PROPER_RUN.finditer(text)]
    for key, eids in weak.items():
        if len(eids) != 1:
            continue
        for m in re.finditer(rf"(?<![\w]){re.escape(key)}(?![\w])", low):
            if not any(a <= m.start() < b for a, b in runs):
                hits.append((m.start(), eids[0]))
    return list(dict.fromkeys(i for _, i in sorted(hits)))


def beat_target(beat: Any) -> str | None:
    """A Reader beat's (dict or object) target id, or None ("none" included)."""
    t = beat.get("target") if isinstance(beat, dict) else getattr(beat, "target", None)
    return t if isinstance(t, str) and t not in ("", "none") else None


def spotlight(state: WorldState, message: str = "", last_delivery: str = "", beat: Any = None, *,
              k: int | None = None, scope: Iterable[str] | None = None, rules: Any = None) -> list[str]:  # rule: 12.2.4
    """Up to `packet.spotlight_k` entities outside the scene (12.2.4 item 3), in order: named or aliased in the
    player's message; the beat's target; named in the last delivery; the scene agenda's thread's linked entities;
    then one relationship hop from those. Never the PC, never one sealed without a permitted slice."""
    rules = rules if rules is not None else load_rules()
    k = int(rules.pacing["packet"].get("spotlight_k", 4)) if k is None else k
    skip = set(scope if scope is not None else scene_scope(state)) | {pc_id(state)}
    out: list[str] = []

    def add(ids: Iterable[str | None]) -> None:
        for i in ids:
            if len(out) < k and i and i not in skip and i not in out and _nameable(state, i):
                out.append(i)

    index = alias_index(state)
    add(resolve_names(state, message, index))
    add([beat_target(beat)])
    add(resolve_names(state, last_delivery, index))
    info = state.meta.get("scene")
    thread = info.get("thread") if isinstance(info, dict) and state.scene and \
        info.get("scene_id") == state.scene.scene_id else None
    if isinstance(thread, str) and thread in state.entities:
        te = state.entities[thread]
        add([te.data.get("points_to") if isinstance(te.data.get("points_to"), str) else None])
        add(str(f.value) for f in state.facts.values() if f.subject == thread and isinstance(f.value, str)
            and f.value in state.entities)
    for i in list(out):  # one hop (World Info "recursion", bounded)
        add(sorted(y for r in state.relationships.values() for x, y in ((r.a, r.b), (r.b, r.a)) if x == i))
    return out


def scene_starts(state: WorldState) -> list[int]:  # rule: 12.2.4
    """The start seqs of the current (or, between scenes, the last) scene and the one before it, newest first: what
    recency counts (2 / 1 / 0). Read from the scene cards, so the scene before last is known between scenes."""
    starts = sorted({c.started_seq for c in state.scene_cards.values()}, reverse=True)
    if not starts:  # a projection folded before scene cards existed
        starts = [s.started_seq for s in (state.scene, state.last_scene) if s is not None]
    return starts[:2]


def shown_details(state: WorldState, ids: Iterable[str]) -> tuple[set[str], set[str]]:  # rule: 00.6.6a
    """(detail fact ids a view may show, detail fact ids it never shows) for `ids`: `beat` details are never shown
    (00.6.6a item 1)."""
    shown: set[str] = set()
    hidden: set[str] = set()
    for eid in ids:
        refs = state.details.get(eid)
        if not refs:
            continue
        act = {f.id for f in active_details(state, eid)}
        shown |= act
        hidden |= {r.fact_id for r in refs.values() if r.fact_id not in act}
    return shown, hidden


def _line_tokens(f: FactRecord) -> int:
    return tokens(f"  {f.id} about {f.subject}: {f.predicate} = {str(f.value)[:VALUE_CHARS]}")


def scene_facts(state: WorldState, scope: list[str] | None = None, *,  # rule: 12.2.4
                focus: Iterable[str] = (), budget: dict[str, int] | None = None) -> list[FactRecord]:
    """The view's facts: the pins, then the ranked fill, each within its `view_budget` (12.2.4 item 3).

    Pinned: every open commitment (each involves the PC), and about the scope's entities their written words
    and the NPCs' active memories. Archived memories never reach a packet (12.11.7). Ranked: the other
    narrator-visible facts about the scope, by salience + recency + relevance + adjacency, newest first on a tie.
    Trigger flags (`trg.*` predicates) are engine state, not fiction, and are left out.
    """
    budget = budget or view_budget()
    keep = set(scope if scope is not None else scene_scope(state, budget))
    hidden = shown_details(state, keep)[1]
    pins: list[tuple[int, FactRecord]] = []
    pool: list[FactRecord] = []
    for f in state.facts.values():
        if f.predicate.startswith("trg.") or _sealed(state, f) or (f.value is None and f.predicate.startswith("detail.")):
            continue
        val = f.value if isinstance(f.value, dict) else {}
        if f.kind == "commitment" and val.get("status") == "open":
            pins.append((1, f))
        elif f.subject not in keep:
            continue
        elif f.predicate.startswith("memory."):
            if val.get("status") != "archived":  # rule: 12.11.7
                pins.append((2, f))
        elif f.predicate in WRITTEN:
            pins.append((0, f))
        else:
            pool.append(f)
    pins.sort(key=lambda p: (p[0], -p[1].valid_from_seq, p[1].id))
    pool = [f for f in pool if f.id not in hidden]
    want = set(focus)
    present = {i for i in [pc_id(state), *(state.scene.cast_present if state.scene else [])] if i}
    linked = {x for r in state.relationships.values() for x, y in ((r.a, r.b), (r.b, r.a)) if y in present and x != y}
    starts = scene_starts(state)

    def score(f: FactRecord) -> int:
        val, text = f.value if isinstance(f.value, dict) else {}, str(f.value)
        salience = 3 if f.kind == "commitment" else val["salience"] if isinstance(val.get("salience"), int) else \
            2 if f.persistence == "scene" else 1  # a scene detail while its scene runs (00.6.6a)
        recency = sum(1 for s in starts if f.valid_from_seq >= s)
        relevance = 2 if f.subject in want or any(i in text for i in want) else 0
        adjacency = 1 if f.subject in linked or any(i in text for i in present - {f.subject}) else 0
        return salience + recency + relevance + adjacency

    pool.sort(key=lambda f: (-score(f), -f.valid_from_seq, f.id))
    return fit([f for _, f in pins], _line_tokens, budget["pinned"]) + fit(pool, _line_tokens, budget["facts"])


def entity_names(state: WorldState, ids: list[str]) -> dict[str, Any]:
    """id -> display name for the ids that exist (sealed entities show their slice or nothing)."""
    out: dict[str, Any] = {}
    for i in ids:
        e = state.entities.get(i)
        if e is None:
            continue
        seal = state.seals.get(i)
        if seal is not None:
            if seal.slice:
                out[i] = seal.slice
            continue
        out[i] = display_name(state, i)  # 12.10.2: as the PC knows them
    return out
