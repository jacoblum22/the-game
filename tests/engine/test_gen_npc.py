"""PR-12-5 NPC generation and the first meeting (T057)."""

from __future__ import annotations

import random
from typing import Any

from engine.gen import _data
from engine.gen.npc import NPC, promote_principal, promote_recurring, reaction_roll, walk_on
from engine.gen.world_seed import build_rolled

TABLES = {t["id"]: t for t in _data.load("oracles.yaml")["tables"]}


class Dice2:
    """A stand-in stream whose 2d6 come out as the given pair."""

    def __init__(self, a: int, b: int):
        self.vals = [a, b]

    def randint(self, lo: int, hi: int) -> int:
        return self.vals.pop(0)


def results(tid: str) -> set[str]:
    return {r["result"] for r in TABLES[tid]["results"]}


def test_walk_on_fixes_identity_from_the_tables() -> None:
    n = walk_on(random.Random(1), home="loc.x")
    assert n.depth == "walk-on" and n.home == "loc.x" and n.id.startswith("npc.")
    assert n.role in results("tbl.npc_role")
    assert (n.gender, n.pronouns) in {(r["result"], r["pronouns"]) for r in TABLES["tbl.npc_gender"]["results"]}
    assert n.age in results("tbl.npc_age") and n.detail in results("tbl.npc_detail")
    assert n.demeanor in results("tbl.npc_demeanor")
    given, family = n.name.split(" ", 1)
    assert given in results("tbl.name_given") and family in results("tbl.name_family")
    assert walk_on(random.Random(1), home="loc.x") == n                      # rolled, so reproducible
    assert walk_on(random.Random(1), role="the innkeeper").role == "the innkeeper"   # the narration's role


def test_walk_on_uses_the_region_name_table() -> None:
    reg = build_rolled(1).record
    used: set[str] = set()
    n = walk_on(random.Random(3), people="orig.people.human", name_tables=reg["names"], given_used=used,
                existing_ids=[x["id"] for x in reg["npcs"]])
    human = [t for t in reg["names"] if t["people"] == "orig.people.human"]
    assert n.name.split(" ")[0] in {g["result"] for t in human for g in t["given"]}
    assert n.people == "creature.folk.human" and used == {n.name.split(" ")[0]}


def test_names_never_run_out() -> None:
    """A long campaign's walk-ons (the spec 005 harness hit "names exhausted" after ~220 lines): once a people's 20
    given names are spent, fresh ones are composed from its syllables."""
    reg = build_rolled(1).record
    used: set[str] = set()
    rng = random.Random(4)
    names = [walk_on(rng, people="orig.people.halfling", name_tables=reg["names"], given_used=used).name
             for _ in range(300)]
    givens = [n.split(" ")[0] for n in names]
    assert len(names) == 300 and len(set(givens)) >= 140  # the halfling syllables give 150 given names, not 20


def test_promotions_add_fields_and_keep_identity() -> None:
    n = walk_on(random.Random(2), role_tags=["deed.martial.blade"])
    r = promote_recurring(random.Random(5), n)
    ident = ("id", "name", "gender", "pronouns", "age", "detail", "demeanor", "role")
    assert all(getattr(r, k) == getattr(n, k) for k in ident)
    assert r.depth == "recurring" and len(r.wants) == 1 and r.fears and r.voice and r.refusals and r.knowledge_scope
    assert promote_recurring(random.Random(9), r) == r                      # never re-rolled
    p = promote_principal(random.Random(6), r, home_band=3, oracle=lambda q, odds: odds in ("even", "likely"),
                          tie_candidates=[("fac.x.rulers", "likely"), ("fac.x.threat", "unlikely")])
    assert p.depth == "principal" and [w.rank for w in p.wants] == [1, 2, 3] and p.band == 3
    assert p.secrets and p.secrets[0].sealed and p.ties == ["fac.x.rulers"] and "fac.x.rulers" in p.member_of
    assert all(getattr(p, k) == getattr(n, k) for k in ident) and p.wants[0] == r.wants[0]


def test_rolls_that_must_fit() -> None:
    """12.11.1: a want's verb takes its object; a martial NPC never refuses to fight."""
    verbs = {r["result"]: r for r in TABLES["tbl.npc_want_verb"]["results"]}
    objs = {r["result"]: int(r["range"]) for r in TABLES["tbl.npc_want_object"]["results"]}
    for s in range(300):
        n = promote_recurring(random.Random(s), walk_on(random.Random(s), role_tags=["deed.martial.polearm"]))
        verb = next(v for v in verbs if n.wants[0].text.startswith(v + " "))
        obj = n.wants[0].text[len(verb) + 1:]
        assert objs[obj] in verbs[verb].get("takes", [objs[obj]])
        assert n.refusals[0].kind != "refusal.fight"


def test_reaction_roll_rungs() -> None:
    seen: dict[int, Any] = {}
    for a in range(1, 7):
        for b in range(1, 7):
            seen[a + b] = reaction_roll(Dice2(a, b)).standing  # type: ignore[arg-type]
    assert seen[2] == -3 and seen[7] == 0 and seen[12] == 2 and max(seen.values()) < 3   # never Devoted
    assert reaction_roll(Dice2(6, 6), modifiers=5).modifier == 2                          # clamped to +-2  # type: ignore[arg-type]
    assert reaction_roll(Dice2(1, 1), modifiers=-1).rung == "hostile"                     # type: ignore[arg-type]
    m = reaction_roll(Dice2(6, 6), faction_status=3)                                      # type: ignore[arg-type]
    assert m.table == "tbl.npc_reaction_member" and m.standing == 3                       # clamped -3..+3
    assert reaction_roll(Dice2(1, 2), faction_status=0).standing == -1                    # type: ignore[arg-type]


def test_seed_cast_reads_as_npcs() -> None:
    reg = build_rolled(2).record
    cast = [NPC.from_record(n) for n in reg["npcs"]]
    assert all(c.pronouns and c.voice and c.wants and c.refusals for c in cast)
    assert cast[0].voice and cast[0].model_dump(by_alias=True)["voice"]["register"] == reg["npcs"][0]["voice"]["register"]
