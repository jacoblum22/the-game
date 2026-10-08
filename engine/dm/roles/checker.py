"""The Checker role (C; contracts/model-calls.md C): the diff audit of one draft (12.3.1 source 2, DL-12-71). A
separate call with only its own prompt (FR-034): it never sees the Narrator's prompt, earlier drafts or reasoning,
only the sentences and what each declares, rendered in words.

    out = check_draft(ctx, "", player_message="I wave him off.", sentences=texts, decls=decls, items=items,
                      created=["npc.bessa_crane"])
    out.claims        # assertions beyond the declarations: Claims for engine.audit.claims.check_claims
    out.undeclared    # addressable things a sentence introduces but does not declare, typed (12.14.13 tiers)
    out.unexpressed   # declarations a sentence does not say, or says otherwise
    out.screen        # flags for engine.audit.screen

THIS MESSAGE holds the draft's sentences numbered from 0 (`[n] text`), each followed by an indented `declares:`
line, then the player's message. `full=True` withholds the declarations (the 1-in-10 full extraction that measures
what the diff misses). The view lists the ids a claim may name: the scene scope, the spotlight (absent people the
turn speaks of) and every id created this turn, each as `<id>: <names>; <here | not here | new this turn>`; the PC
as `pc.x: Name, you, your` so pronoun claims resolve.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from pydantic import BaseModel, Field

from engine.audit.claims import Claim
from engine.audit.declare import DeclaredSentence
from engine.dm.context import TurnContext
from engine.dm.handles import RecordItem
from engine.dm.packet import build_packet
from engine.dm.roles.prompts import load_prompt
from engine.dm.schemas import build_schema, schema_context
from engine.llm.base import Role, call_role
from engine.llm.offline import sentences as _sentences
from engine.retrieve.cards import load_cards_for
from engine.retrieve.scene import pc_id, scene_scope, spotlight
from engine.store.projection import DETAIL, WorldState
from engine.store.views import display_name, name_known, unnamed_label
from engine.text.render import relation

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


def _fact_words(state: WorldState, fid: str) -> str:
    f = state.facts.get(fid)
    if f is None:
        return fid
    who = display_name(state, f.subject) if f.subject in state.entities else f.subject
    if f.predicate.startswith(DETAIL):
        return f"{who}'s {f.predicate[len(DETAIL):].replace('_', ' ')}: {f.value}"
    try:
        return relation(who, f.predicate, None if f.value is None else str(f.value)) or f"{who} {f.predicate}"
    except KeyError:  # a verb outside the closed list: the predicate's words as they are
        return f"{who} {f.predicate.replace('_', ' ')}: {f.value}"


def declaration_words(state: WorldState, d: DeclaredSentence, items: Mapping[str, RecordItem]) -> str:
    # rule: 12.3.1
    """What one sentence declares, in words (B P2, P4): each cited line or view fact by handle, who it is about,
    each new element with the properties it states, or the atmosphere flag."""
    parts: list[str] = []
    for r in d.refs:
        it = items.get(r)
        parts.append(f"{r} ({(it.render or it.text) if it is not None else _fact_words(state, r)})")
    if d.about:
        parts.append("about " + ", ".join(f"{display_name(state, a) if a in state.entities else a} ({a})"
                                          for a in d.about))
    for el in d.new:
        props = "; ".join(f"{p.predicate}: {p.value}" for p in el.implied)
        parts.append(f'new {el.element_kind or "element"} "{el.name}"' + (f" ({props})" if props else ""))
    if d.atmosphere:
        parts.append("atmosphere")
    return "; ".join(parts) or "nothing"


def checker_message(sents: Sequence[str], player_message: str, declares: Sequence[str] | None = None,
                    full: bool = False) -> str:  # rule: 12.3.1
    """The draft's sentences `[n] text`, each with its `declares:` line (none in a full extraction), then the
    player's message (12.14.3's comparison)."""
    lines = [FULL_HEADER, ""] if full else []
    for i, s in enumerate(sents):
        lines.append(f"[{i}] {s}")
        if declares is not None and not full and i < len(declares):
            lines.append(f"    declares: {declares[i]}")
    lines.append("")
    lines.append(f'THE PLAYER\'S MESSAGE: "{player_message}"' if player_message else "THE PLAYER'S MESSAGE: (none)")
    return "\n".join(lines)


def check_draft(ctx: TurnContext, fiction: str, *, player_message: str = "", created: Iterable[str] = (),
                exchanges: Sequence[str | tuple[str, str]] = (), sentences: Sequence[str] | None = None,
                decls: Sequence[DeclaredSentence] | None = None, items: Sequence[RecordItem] = (),
                full: bool = False) -> CheckerOutput:  # rule: PR-12-2
    """One Checker call. Raises ModelInvalid after a failed re-ask. `sentences`: the narrator's own sentences (spec
    006), numbered as given, instead of splitting `fiction`; `decls`: their declarations, shown in words so the
    audit reports only what they do not cover (12.3.1's diff); `full`: withhold them (a full extraction)."""
    st = ctx.state
    created = list(created)
    sents = list(sentences) if sentences is not None else split_sentences(fiction)
    last = list(exchanges)[-1] if exchanges else ""
    dm = last if isinstance(last, str) else (list(last) + ["", ""])[1]
    ids = checker_ids(st, created, message=player_message, last_delivery=str(dm or ""), rules=ctx.rules)
    by_handle = {it.handle: it for it in items}
    declares = [declaration_words(st, d, by_handle) for d in decls] if decls is not None else None
    sctx = schema_context(st, ctx.rules, draft_sentences=sents)
    sctx.scene_ids = ids
    if decls is not None and not full:
        sctx.checker_refs = list(dict.fromkeys(r for d in decls for r in [*d.refs, *d.about]))
    schema = build_schema(Role.CHECKER, sctx)
    cards = load_cards_for(Role.CHECKER, (), None, (), rules=ctx.rules)
    packet = build_packet(Role.CHECKER, instructions=load_prompt("checker"), cards=cards,
                          view="\n".join(entity_lines(st, ids, created)), exchanges=list(exchanges),
                          message=checker_message(sents, player_message, declares, full), rules=ctx.rules)
    res = call_role(ctx.model, Role.CHECKER, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call)
    data = dict(res.data)

    def ok(x: Mapping[str, Any]) -> bool:
        return int(x.get("sentence", 0)) < len(sents)

    claims = [Claim.model_validate(c) for c in data.get("claims") or [] if ok(c)]
    return CheckerOutput(sentences=sents, claims=claims, screen=dict(data.get("screen") or {}), scene_ids=ids,
                         undeclared=[dict(x) for x in data.get("undeclared") or [] if ok(x)],
                         unexpressed=[dict(x) for x in data.get("unexpressed") or [] if ok(x)],
                         call_id=res.record.call_id)


__all__ = ["CheckerOutput", "check_draft", "checker_ids", "checker_message", "declaration_words", "entity_lines",
           "split_sentences"]
