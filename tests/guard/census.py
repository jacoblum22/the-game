"""Spec 033 P0: play the offline dm-tools games under the VIII.9 guard.

    PYTHONUTF8=1 py -3.12 -m tests.guard.census            # prints the reach summary (log mode)

`play_recorded` is the `offline_seed11_dmtools` recipe (`tests/replay/record_games.py`) on a temp path. `play_probe`
is a short scripted game whose DM uses the tools the offline DM never calls (move, read, persuade, force, grapple,
fight, costs, walk-ons, speech, recall, clue, mood, end_scene), so the census shows what a real DM could reach.
"""

from __future__ import annotations

import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from tests.guard.scan import REACHED
from tests.guard.viii9 import AUDIT_TEXT, DENY, WATCH, Guard


def play_recorded(guard: Guard | None = None) -> Guard:
    """The recorded offline game (24 turns, a retirement, a new character) under the guard."""
    from tests.replay.record_games import offline_seed11_dmtools

    g = guard or Guard()
    with tempfile.TemporaryDirectory(prefix="viii9-") as tmp, g:
        offline_seed11_dmtools(Path(tmp) / "g.db")
    return g


def roll(**kw: Any) -> dict[str, Any]:
    base = {"tool": "propose_roll", "goal": "hit it", "verb": "verb.strike", "target": "", "how": "swing hard",
            "attribute": "might", "difficulty": "hard", "why_uncertain": "it is quick", "stakes": "risky",
            "nonlethal": False, "fail_cost": "none", "change_kind": "none", "change_what": "", "change_whom": ""}
    return {**base, **kw}


def sure(**kw: Any) -> dict[str, Any]:
    """A roll offer that is easy and safe, so it resolves at once (the resolve path runs, no pause)."""
    return roll(difficulty="easy", stakes="safe", **kw)


def change(**kw: Any) -> dict[str, Any]:
    return {"tool": "change", "kind": "", "who": "", "what": "", "to": "", "amount": 0, "note": "", **kw}


def dm(*calls: dict[str, Any], passage: str = "It happens.", said: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return {"calls": list(calls), "passage": passage, "said": said or [], "asks": []}


def _note(game: Any, label: str, r: Any) -> str:
    st = (game.store.turn(str(r.turn_id)).screen or {}).get("dm_tools", {}) if r.turn_id else {}  # type: ignore[union-attr]
    return (f"{label[:40]!r}: calls={st.get('tool_calls')} steps={st.get('steps')} pause={r.pause.kind if r.pause else None} rolls={st.get('rolls')} "
            f"refused={[(x['tool'], x['kind'], x['why'][:90]) for x in st.get('refusals', [])]}")


def elsewhere(game: Any) -> str:
    """Some place the character can walk to from here."""
    from engine.world.places import location, reachable

    st = game.store.state
    here = location(st)
    return next((x.to for x in reachable(st, here) if x.to != here), "") if here else ""


def play_probe(tmp: Path, guard: Guard | None = None) -> Guard:
    """Scripted DM turns over seed 7 (the `to_play` setup of the dm-tools tests). Pauses are answered `commit`."""
    from engine.llm.base import Role
    from engine.world.scenes import cast_present
    from tests.engine.test_dm_tools import to_play

    g = guard or Guard()
    game, model = to_play(tmp)
    npc = cast_present(game.store.state)[0]
    steps: list[tuple[str, list[Any]]] = [  # (the player's message, the DM's step responses)
        ("I read the notice on the wall.",
         [dm(sure(verb="verb.observe", goal="read the notice", target="the notice", how="read the inscription",
                  attribute="mind", change_kind="learn"))]),
        ("I step away from them and retreat to the door.",
         [dm(sure(verb="verb.move", goal="withdraw", target=npc, how="I retreat away from them", attribute="body",
                  change_kind="move_to", change_what="far"))]),
        ("I grab the person and hold them.",
         [dm(sure(verb="verb.grapple", goal="hold", target=npc, how="grab and restrain", change_kind="restrain"))]),
        ("I free myself, wriggling out.",
         [dm(sure(verb="verb.exert", goal="break free", target="pc", how="wriggle free and escape",
                  change_kind="free"))]),
        ("I shove them down, tripping them to the floor.",
         [dm(sure(verb="verb.force", goal="trip them", target=npc, how="trip and sweep them to the floor"))]),
        ("I talk them round.",
         [dm(sure(verb="verb.talk", goal="persuade them", target=npc, how="I speak plainly", attribute="presence",
                  change_kind="persuade_to", change_what="help me", change_whom=npc))]),
        ("I sneak past.", [dm(roll(verb="verb.sneak", goal="slip by", how="creep past", fail_cost="cost.exposure",
                                  difficulty="moderate"))]),
        ("I climb the wall.", [dm(roll(verb="verb.exert", goal="climb", how="hand over hand", fail_cost="cost.gear",
                                      difficulty="very_hard"))]),
        ("I force the door.", [dm(roll(verb="verb.force", goal="force the door", how="shoulder it", target="the door",
                                      fail_cost="cost.footing", difficulty="very_hard"))]),
        ("I lift the heavy crate and carry it.",
         [dm(sure(verb="verb.exert", goal="carry the crate", how="lift and carry it"))]),
        ("Someone new arrives.",
         [dm(change(kind="new_npc", what="an old woman"), change(kind="new_item", what="a brass key", to="pc"),
             change(kind="coin", who="pc", to="Edda Brightcote", amount=1)),
          dm(change(kind="fact", what="the dog is hungry", who="the pale dog"),
             passage="Edda Brightcote hands you a brass key.",
             said=[{"npc": "Edda Brightcote", "words": "Mind the dog."}, {"npc": npc, "words": "Mind the dog."}])]),
        ("I attack the pale beast.", [dm(change(kind="fight", who="the pale beast"), passage="It crouches.")]),
        ("I keep fighting.",
         [dm(roll(verb="verb.strike", goal="strike", target=npc, how="stab them", nonlethal=True,
                  change_kind="harm", change_what=npc, difficulty="easy"))]),
        ("I rest for the night.", [dm(change(kind="rest", what="rest_long"), passage="You sleep.")]),
        ("I give them my coin and ask them to go.",
         [dm(change(kind="condition_add", who=npc, what="cond.frightened"), change(kind="npc_leaves", who=npc),
             change(kind="give_item", what="item.no_such_thing", to=npc), passage="They flinch.")]),
        ("We set off together.", [lambda schema, packet: dm(change(kind="travel", to=elsewhere(game), who=npc),
                                                           passage="You go.")]),
        ("Where is the old road?",
         [dm({"tool": "recall", "query": "what do I know about the road"}, {"tool": "state", "about": "people"},
             {"tool": "reveal_clue", "npc": npc, "question": "who did it?"}),
          dm({"tool": "mood", "npc": npc, "mood": "open"}, {"tool": "end_scene", "why": "cut"},
             passage="He points.")]),
    ]
    with g:
        for message, script in steps:
            model.push(Role.DM, *script)
            r = game.submit(message)
            g.trace.append(_note(game, message, r))
            for _ in range(4):
                if r.pause is None:
                    break
                ids = [c.id for c in r.pause.choices]
                r = game.answer("commit" if "commit" in ids else ids[0])
                g.trace.append(_note(game, "  answer", r))
        for i in range(8):  # quiet exchanges: the inconclusive streak (12.8.1) may raise a lead
            game.submit(f"I wait and watch {i}.")
    game.close()
    return g


def paths(g: Guard, name: str) -> dict[str, int]:
    """For a denied name: how often it was reached, by the innermost dm-tools/dm-world function and scope."""
    c = Counter(f"{h['scope']}:{(h['path'] or ['?'])[-1]}" for h in g.hits if h["name"] == name)
    return dict(c.most_common())


def summary(g: Guard) -> dict[str, Any]:
    hit = Counter(h["name"] for h in g.hits)
    watched = {n: g.reached(n) for n in WATCH}
    shell = {n: g.reach[("shell", n)] for n in DENY if g.reach[("shell", n)]}  # outside a turn: setup, opening, menus
    return {"hits": len(g.hits),
            "denied_reached": {n.removeprefix("engine."): (hit[n], paths(g, n)) for n in DENY if hit[n]},
            "denied_shell_only": {n.removeprefix("engine."): c for n, c in shell.items() if not hit[n]},
            "denied_unreached": [n.removeprefix("engine.") for n in DENY if not hit[n] and n not in shell],
            "watched_reached": {n.removeprefix("engine."): c for n, c in watched.items() if c},
            "watched_unreached": [n.removeprefix("engine.") for n, c in watched.items() if not c]}


def table(rec: Guard, probe: Guard) -> list[str]:
    """One line per denied or watched name: calls in the recorded game / in the probe game, and the paths that reach
    it (the innermost dm-tools function and the verb or tool of the call, top three over both games)."""
    lines = []
    for label, names in (("DENY", DENY), ("WATCH", WATCH)):
        for n in names:
            counts = [sum(h["name"] == n for h in g.hits) if label == "DENY" else g.reach[("turn", n)] for g in (rec, probe)]
            shell = [g.reach[("shell", n)] for g in (rec, probe)]
            by = Counter(f"{h['scope']}:{(h['path'] or ['?'])[-1]}" for g in (rec, probe) for h in g.hits
                         if h["name"] == n)
            lines.append(f"{label:5} {n.removeprefix('engine.'):42} rec={counts[0]:<5} probe={counts[1]:<5}"
                         f" shell={shell[0]}/{shell[1]} {dict(by.most_common(3)) if by else ''}")
    for label, g in (("rec", rec), ("probe", probe)):
        for (scope, caller, callee), c in sorted(g.edges.items()):
            if scope == "turn" and (callee.startswith(AUDIT_TEXT) or callee in WATCH):
                lines.append(f"EDGE  {label:5} {caller.removeprefix('engine.')} -> {callee.removeprefix('engine.')} x{c}")
    return lines


def write_reached(*games: Guard) -> list[str]:
    """`tests/guard/reached.txt`: every top-level engine function the games reached during a dm-tools turn."""
    from tests.guard.scan import toplevel

    found = {f"{mod} {toplevel(q)}" for g in games for (scope, name) in g.reach if scope == "turn"
             for mod, q in [g.parts[name]]}
    lines = sorted(found)
    head = "# functions reached in a dm-tools turn by tests/guard/census.py (the recorded game + the probe)"
    REACHED.write_text("\n".join([head, *lines]) + "\n", encoding="utf-8")
    return lines


def main() -> None:
    which = sys.argv[1] if len(sys.argv) > 1 else "table"
    with tempfile.TemporaryDirectory(prefix="viii9p-") as tmp:
        if which == "reached":
            lines = write_reached(play_recorded(), play_probe(Path(tmp)))
            print(f"{len(lines)} functions -> {REACHED}")
        elif which == "table":
            print("\n".join(table(play_recorded(), play_probe(Path(tmp)))))
        else:
            g = play_recorded() if which == "recorded" else play_probe(Path(tmp))
            print(json.dumps(summary(g), indent=1))
            print("\n".join(g.trace))


if __name__ == "__main__":
    main()
