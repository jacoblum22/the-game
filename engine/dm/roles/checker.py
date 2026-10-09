"""The Checker role (C; contracts/model-calls.md C): the sampled audit of one delivered passage (12.3.1 source 2,
DL-12-71). A separate call with only its own prompt (FR-034): it never sees the Narrator's prompt, earlier drafts or
reasoning, only the passage, its side list in words, and the last exchange as conversation (12.2.4).

    out = check_draft(ctx, "", player_message="I wave him off.", sentences=texts, passage=p, items=items,
                      created=["npc.bessa_crane"])
    out.claims        # assertions beyond the side list: Claims for engine.audit.claims.check_claims
    out.undeclared    # addressable things the passage introduces that the side list does not name (12.14.13 tiers)
    out.unexpressed   # record lines the side list covers that the passage does not say, or says otherwise
    out.screen        # flags for engine.audit.screen

THIS MESSAGE holds the passage, its sentences numbered from 0 (`[n] text`, code's split, so a claim can say where it
is), then the side list in words, then the player's message. `full=True` withholds the side list (the full
extraction that measures what the diff misses). The view lists the ids a claim may name: the scene scope, the
spotlight (absent people the turn speaks of) and every id created this turn, each as `<id>: <names>; <here | not here
| new this turn>`; the PC as `pc.x: Name, you, your` so pronoun claims resolve.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from pydantic import BaseModel, Field

from engine.audit.claims import Claim
from engine.audit.declare import Passage
from engine.dm.context import TurnContext
from engine.dm.handles import RecordItem
from engine.dm.packet import build_packet
from engine.dm.roles.prompts import load_prompt
from engine.dm.schemas import build_schema, schema_context
from engine.llm.base import Role, call_role
from engine.llm.offline import sentences as _sentences
from engine.retrieve.cards import load_cards_for
from engine.retrieve.scene import pc_id, scene_scope, spotlight
from engine.store.projection import WorldState
from engine.store.views import display_name, name_known, unnamed_label

ALIAS_KEYS = ("role", "aliases", "pronouns", "people", "detail")
FULL_HEADER = "FULL EXTRACTION: the declarations are withheld this time; report every assertion as a claim."


class CheckerOutput(BaseModel):
    sentences: list[str] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    undeclared: list[dict[str, Any]] = Field(default_factory=list)
    unexpressed: list[dict[str, Any]] = Field(default_factory=list)
    screen: dict[str, Any] = Field(default_factory=dict)
    scene_ids: list[str] = Field(default_factory=list)
    call_id: str | None = None


def split_sentences(text: str) -> list[str]:  # rule: 12.3.1
    """The draft's sentences (quoted speech kept whole); numbered from 0 for the Checker."""
    return _sentences(text)


def checker_ids(state: WorldState, created: Iterable[str] = (), *, message: str = "", last_delivery: str = "",
                rules: Any = None) -> list[str]:  # rule: 12.3.1
    # rule: 12.2.4
    """Every id a claim may name: the scene scope, the spotlight (12.2.4 item 3: absent people the player or the
    last delivery names, so a sentence about one is judged as about them, P-085) and ids created this turn (that
    exist and are not sealed)."""
    out = list(scene_scope(state))
    spot = spotlight(state, message, last_delivery, rules=rules) if state.scene is not None else []
    for eid in [*spot, *created]:
        if eid in state.entities and eid not in out and not (eid in state.seals and not state.seals[eid].slice):
            out.append(eid)
    return out


def entity_lines(state: WorldState, ids: Sequence[str], created: Iterable[str] = ()) -> list[str]:  # rule: 12.3.1
    """`<id>: <name>, <aliases>; <scope>` per id; the PC as `pc.x: Name, you, your`. Sealed entities show only their
    slice. Someone not here keeps only the names nobody here has ("the child" is the one here)."""
    pc = pc_id(state)
    here = set(scene_scope(state))
    new = set(created)
    names_of: dict[str, list[str]] = {}
    for eid in ids:
        e = state.entities.get(eid)
        if e is None or eid in state.seals:
            continue
        names = [e.name]
        if not name_known(state, eid):  # 12.10.2: as the narration calls them; the name stays to catch slips
            names = [unnamed_label(e), e.name]
        if eid == pc:
            names += ["you", "your"]
        for k in ALIAS_KEYS:
            v = e.data.get(k)
            vals = v if isinstance(v, list) else [v]
            names += [str(x) for x in vals if isinstance(x, str) and x]
        names_of[eid] = list(dict.fromkeys(n for n in names if n))
    taken = {n.lower() for eid, ns in names_of.items() if eid in here for n in ns}
    lines: list[str] = []
    for eid in ids:
        seal = state.seals.get(eid)
        if seal is not None and eid in state.entities:
            lines.append(f"{eid}: {seal.slice}")
            continue
        if eid not in names_of:
            continue
        scope = "here" if eid in here else "new this turn" if eid in new else "not here"
        names = names_of[eid] if eid in here else [n for n in names_of[eid] if n.lower() not in taken]
        lines.append(f"{eid}: " + ", ".join(names or [eid]) + f"; {scope}")
    return lines


def side_list_words(state: WorldState, p: Passage, items: Mapping[str, RecordItem]) -> list[str]:  # rule: 12.3.1
    """The passage's side list in words: each speech with its speaker, each new element with the properties it
    states, each covered record line by handle."""
    out = []
    for sp in p.speech:
        who = display_name(state, sp.speaker) if sp.speaker in state.entities else "someone"
        out.append(f'- {who} says ({sp.form}): "{sp.words}"')
    for el in p.new:
        props = "; ".join(f"{x.predicate}: {x.value}" for x in el.implied)
        out.append(f'- new {el.element_kind or "element"} "{el.name}"' + (f" ({props})" if props else ""))
    for h in p.covers:
        it = items.get(h)
        if it is not None:
            out.append(f"- covers {h}: {it.render or it.text}")
    return out or ["- nothing"]


def checker_message(sents: Sequence[str], player_message: str, side: Sequence[str] | None = None,
                    full: bool = False) -> str:  # rule: 12.3.1
    """The passage's sentences `[n] text`, then its side list in words (none in a full extraction), then the
    player's message (12.14.3's comparison)."""
    lines = [FULL_HEADER, ""] if full else []
    lines += [f"[{i}] {s}" for i, s in enumerate(sents)]
    if side is not None and not full:
        lines += ["", "THE SIDE LIST:", *side]
    lines.append("")
    lines.append(f'THE PLAYER\'S MESSAGE: "{player_message}"' if player_message else "THE PLAYER'S MESSAGE: (none)")
    return "\n".join(lines)


def check_draft(ctx: TurnContext, fiction: str, *, player_message: str = "", created: Iterable[str] = (),
                exchanges: Sequence[str | tuple[str, str]] = (), sentences: Sequence[str] | None = None,
                passage: Passage | None = None, items: Sequence[RecordItem] = (),
                full: bool = False) -> CheckerOutput:  # rule: PR-12-2
    # rule: 12.2.4
    """One Checker call. Raises ModelInvalid after a failed re-ask. `sentences`: the delivered passage's sentences,
    numbered as given, instead of splitting `fiction`; `passage`: its side list, shown in words so the audit reports
    only what it does not cover (12.3.1's diff); `full`: withhold it (a full extraction). The conversation is the last
    exchange only (12.2.4's Checker row)."""
    st = ctx.state
    created = list(created)
    sents = list(sentences) if sentences is not None else split_sentences(fiction)
    last = list(exchanges)[-1] if exchanges else ""
    dm = last if isinstance(last, str) else (list(last) + ["", ""])[1]
    ids = checker_ids(st, created, message=player_message, last_delivery=str(dm or ""), rules=ctx.rules)
    by_handle = {it.handle: it for it in items}
    side = side_list_words(st, passage, by_handle) if passage is not None else None
    sctx = schema_context(st, ctx.rules, draft_sentences=sents)
    sctx.scene_ids = ids
    if passage is not None and not full:
        sctx.checker_refs = [h for h in passage.covers if h in by_handle]
    schema = build_schema(Role.CHECKER, sctx)
    cards = load_cards_for(Role.CHECKER, (), None, (), rules=ctx.rules)
    packet = build_packet(Role.CHECKER, instructions=load_prompt("checker"), cards=cards,
                          view="\n".join(entity_lines(st, ids, created)), exchanges=list(exchanges)[-1:],
                          message=checker_message(sents, player_message, side, full), rules=ctx.rules)
    res = call_role(ctx.model, Role.CHECKER, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call)
    data = dict(res.data)

    def ok(x: Mapping[str, Any]) -> bool:
        return int(x.get("sentence", 0)) < len(sents)

    claims = [Claim.model_validate(c) for c in data.get("claims") or [] if ok(c)]
    return CheckerOutput(sentences=sents, claims=claims, screen=dict(data.get("screen") or {}), scene_ids=ids,
                         undeclared=[dict(x) for x in data.get("undeclared") or [] if ok(x)],
                         unexpressed=[dict(x) for x in data.get("unexpressed") or []],
                         call_id=res.record.call_id)


__all__ = ["CheckerOutput", "check_draft", "checker_ids", "checker_message", "entity_lines", "side_list_words",
           "split_sentences"]
