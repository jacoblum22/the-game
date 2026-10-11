"""NECESSITY (01.4.1's computation line, `[D]`): which beats roll, decided by code, never proposed by a role.

    reason = necessity(beat, decision, state=tx.state, rules=rules)   # "uncertain_and_costly" -> frame and roll
    if trivial_class(proposed, rules, verb): ...                       # the Framer's class base is trivial

Before framing (the Framer is not called): an accepted crude fallback always rolls; reading words on record in a
tongue the PC reads is trivial (P-110); a Talk that asks a Neutral-or-warmer listener a plain question is certain
(15.3.10, T-15-3: an R1 request; reason `trivial`, so no evidence); a Move to the place the mover is in is a look
(DL-12-98); a change already true is certain (DL-01-36). After framing: a rubric class whose base is
`trivial` does not roll (01.4.1 decision 1; a nudge never crosses that line, 01.6.5). Every other beat rolls.

`parties_who_would_act` is 01.4.1's COSTLY test and 01.6.9's stakes source: an aware party counts only if it would
act on a failure (hostile, or the act is against its wishes); mere presence is not enough.
"""

from __future__ import annotations

from typing import Any

from engine.resolve.types import Beat

ROLLS = "uncertain_and_costly"
TRIVIAL = "trivial"
PEOPLE = ("npc", "companion", "adversary")
WOULD_ACT_STANDING = -2  # Unfriendly or worse (T-15-1): would act against the PC on a failure


def _standing(state: Any, npc: str, toward: str) -> int | None:
    r = state.relationships.get(f"{npc}|{toward}|standing")
    return r.value if r else None


def _present(state: Any, actor: str) -> list[str]:
    cast = state.scene.cast_present if state.scene is not None else []
    return [i for i in cast if i != actor and i in state.entities and state.entities[i].kind in PEOPLE]


def parties_who_would_act(state: Any, actor: str, beat: Beat | None = None) -> list[str]:  # rule: 01.4.1
    # rule: 01.6.9
    """Present parties who would act on a failure: adversaries, NPCs Unfriendly or worse toward the actor, everyone
    present while a fight runs, the beat's target when the act is against its will, and every observer of a Sneak
    (being noticed is what a failed Sneak costs; 01.18 Sneak: "no observer: not costly")."""
    fight = str(state.time.mode) == "conflict"
    sneak = beat is not None and beat.verb == "verb.sneak"
    out = []
    tgt = beat.target if beat is not None else None
    near = _present(state, actor)
    if tgt and tgt not in near and tgt in state.entities and state.entities[tgt].kind in PEOPLE and tgt != actor:
        near.append(tgt)  # the one the beat is aimed at is there to act, listed or not
    for i in near:
        ent = state.entities[i]
        st = _standing(state, i, actor)
        if (fight or sneak or ent.kind == "adversary" or (st is not None and st <= WOULD_ACT_STANDING)
                or (beat is not None and beat.against_will and beat.target == i)):
            out.append(i)
    return out


SOCIAL_GOALS = ("learn", "persuade_to", "none")


def certain_talk(beat: Beat, verb: str | None, state: Any) -> bool:  # rule: 15.3.10
    """A plain question (R1: "what anyone in their role would say", 15.3.2) to a present person Neutral or warmer
    toward the actor (never met counts Neutral, T-15-3's first contact), not against their will. Whether the
    NPC answers, and what, stays the NPC's (12.2.9, the World step): a refusal is an answer, not a roll.
    Keyed on the words and the goal, whatever the verb label (DL-15-41: a Help that asks is still talk).
    ponytail: 15.3.10's hesitation test (a watcher, a superior, a fear) is not read here; an adversary always
    rolls. Add the cited-reason check when the NPC layer records hesitations."""
    tgt = beat.target
    kind = beat.change.kind if beat.change is not None else "none"
    if not beat.speech or kind not in SOCIAL_GOALS or not beat.asks or beat.against_will or not tgt \
            or tgt not in _present(state, beat.actor):
        return False
    if state.entities[tgt].kind == "adversary":
        return False
    st = _standing(state, tgt, beat.actor)
    return st is None or st >= 0


def plain_reading(beat: Beat, verb: str | None, state: Any) -> bool:  # rule: 01.4.1
    """P-110: reading words already on record (a notice's legible part) in a tongue the PC reads is not COSTLY:
    failure leaves things as they were and can be retried at leisure."""
    from engine.resolve.gate import reads_writing
    from engine.retrieve.scene import cannot_read, written_words

    tgt = beat.target
    reads = beat.stated.reads if beat.stated is not None else reads_writing(beat, verb, state)  # [spec 033 R7] the DM's field
    return (reads and tgt is not None and tgt in state.entities
            and written_words(state, tgt) is not None and not cannot_read(state, beat.actor, tgt))


def necessity(beat: Beat, decision: Any, *, state: Any, rules: Any) -> str:  # rule: 01.4.1
    """The roll test's reason before framing: `uncertain_and_costly` (frame it; `costly` may still take the time
    after framing), or a no-roll class code can see."""
    if decision.mode == "fallback":
        return ROLLS  # an accepted crude fallback is framed on its own scope (01.3.5), then meets `costly` (DL-01-46)
    verb = decision.verb or beat.verb
    if plain_reading(beat, verb, state) or certain_talk(beat, verb, state) or looks_here(beat, verb, state):
        return TRIVIAL
    from engine.resolve.change import already_true

    return TRIVIAL if already_true(state, beat) else ROLLS  # DL-01-36: already so is certain, no OFFER


TAKE_THE_TIME = "take_the_time"
LISTENS = ("cost.time", "cost.exposure")  # a clock ticked by time passing or by being noticed (`structural_fit`)


def costly(frame: Any, *, state: Any, rules: Any, source: str = "none") -> list[str]:  # rule: 01.4.1
    # rule: 01.4.4
    """01.4.1 decision 2 on the typed frame, after framing, for every verb (DL-01-44): why a failure would cost
    something; [] means it would not, and the beat takes the time (01.4.4). Costly: a conflict; stakes above Safe
    or lethal; a contest (a person resists: an opposed or defense DC); a final DC at Very hard or beyond (a
    fallback's shift included: `take_the_time.forbidden_tiers`); a clock listening; an attack on someone (06.2.1:
    it starts a fight); a cost cited to a fact (except time, which taking the time already pays). The stakes field
    is checked against the frame's own costs: a listening clock or a cited cost makes a Safe frame costly whatever
    its source says. Whether an onlooker would act on this failure is the Framer's stakes source (01.6.9: "an
    onlooker counts only if they would act"), not code's coarser `parties_who_would_act` (explorer t12: an Unfriendly
    bystander does not make sitting down to listen costly)."""
    why = [f"a stakes source ({source})"] if source != "none" else []
    if str(state.time.mode) == "conflict" or (state.scene is not None and state.scene.mode == "conflict"):
        why.append("a conflict")
    if frame.stakes != "safe" or frame.lethal:
        why.append(f"{frame.stakes} stakes")
    if frame.dc_source not in ("tier", "stored"):
        why.append(f"contested ({frame.dc_source})")
    elif frame.beat.change is not None and frame.beat.change.kind == "persuade_to":
        why.append("contested (their will decides)")  # people named only by a description ("the refugees")
    tt = rules.resolution.get("take_the_time") or {}
    hard = min((int(t["dc"]) for t in rules.resolution["dc_tiers"]
                if t["id"] in (tt.get("forbidden_tiers") or ("very_hard", "legendary")) and t.get("dc")), default=25)
    if frame.dc is not None and frame.dc >= hard:
        why.append(f"DC {frame.dc}: Very hard or beyond")
    if any(c.status == "active" and any(str(r.get("on")) in LISTENS for r in c.tick_sources)
           for c in state.clocks.values()):
        why.append("a clock listens")
    verb = frame.gate.verb or frame.beat.verb
    traits = {*frame.traits, *frame.beat.traits, *((rules.basic_verbs.get(verb or "") or {}).get("traits") or ())}
    tgt = state.entities.get(frame.beat.target or "")
    if "trait.action.attack" in traits and tgt is not None and tgt.kind in PEOPLE:  # 06.2.1: it starts a fight
        why.append("an attack on someone")
    why += [f"{c.menu_id} cited to {c.source_fact}" for c in (frame.threatened_cost, frame.alternate_cost)
            if c is not None and c.source_fact and c.menu_id != "cost.time"]
    return why


def looks_here(beat: Beat, verb: str | None, state: Any) -> bool:  # rule: 01.4.1
    """DL-12-98: a Move to the place the mover is already in is looking around for something (the fighter run's four
    turns of "keep hunting for the refugees"): ordinary, so no roll unless a party would act on a failure."""
    if verb != "verb.move" or not beat.target or beat.target not in state.entities:
        return False
    pos = state.positions.get(beat.actor)
    here = (pos.location if pos else None) or (state.scene.place_id if state.scene is not None else None)
    return beat.target == here and not parties_who_would_act(state, beat.actor, beat)


def class_base(rules: Any, verb: str | None, obstacle_class: str | None) -> str | None:  # rule: 01.6.5
    entry = rules.basic_verbs.get(verb or "") or {}
    for c in (entry.get("anchor") or {}).get("obstacle_classes") or ():
        if c.get("id") == obstacle_class:
            return str(c.get("base"))
    return None


def trivial_class(proposed: Any, rules: Any, verb: str | None) -> bool:  # rule: 01.4.1
    """After framing: the Framer's rubric class has a `trivial` base (decision 1 false): no roll."""
    ob = proposed.obstacle
    return ob.kind == "tier" and class_base(rules, verb, ob.obstacle_class) == TRIVIAL
