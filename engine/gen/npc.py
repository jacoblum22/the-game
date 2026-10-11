"""NPC generation and the first meeting (PR-12-5, 12.11.1-12.11.2).

Three depths, each promoted by a trigger and each field rolled and written at once, never chosen:

    npc = walk_on(rng, home="loc.x", role="the innkeeper")            # PR-12-5 step 2
    standing = reaction_roll(rng, modifiers=+1).standing             # step 3, at the first interaction
    npc = promote_recurring(rng, npc)                                 # step 4
    npc = promote_principal(rng, npc, home_band=2)                    # step 5

Name, gender, pronouns and the descriptors are fixed at walk-on and never re-rolled; promotion only adds fields.
Tables are `data/oracles.yaml`'s `tbl.npc_*`, `tbl.name_*`; a region's name tables (the seed's) replace the
generic names when given. Recency (`recency: true` tables) is the caller's `roll_table` concern: these
functions roll the table plainly. The yes/no Oracle (a principal's secret, ties) is injectable (`oracle=`);
the default rolls d100 against `resolution.yaml#oracle` without extremes.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Sequence
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from engine.gen import _data
from engine.gen._rng import SeedRng
from engine.gen._seed_lib import Dice, by_range, person_name, role_license, roll_refusal, roll_want, slug

Depth = Literal["walk-on", "recurring", "principal", "minor"]
Oracle = Callable[[str, str], bool]          # (question, odds rung id) -> yes


class Want(BaseModel):
    text: str
    tags: list[str] = Field(default_factory=list)
    rank: int = 1


class Fear(BaseModel):
    text: str
    tags: list[str] = Field(default_factory=list)


class Refusal(BaseModel):
    kind: str
    text: str
    strength: str | None = None


class Secret(BaseModel):
    fact: str
    text: str
    gate: str
    sealed: bool = True


class Voice(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    register_: str = Field(alias="register")     # `register` would shadow ABCMeta.register
    habit: str


class NPC(BaseModel):
    """An NPC record (12.11.1). Identity fields are written at walk-on and never change."""

    id: str
    name: str
    role: str
    people: str | None = None                 # creature.folk.* tag
    gender: str
    pronouns: str
    age: str
    detail: str
    demeanor: str
    depth: Depth = "walk-on"
    home: str | None = None
    member_of: list[str] = Field(default_factory=list)
    band: int = 1
    role_tags: list[str] = Field(default_factory=list)
    wants: list[Want] = Field(default_factory=list)
    fears: list[Fear] = Field(default_factory=list)
    refusals: list[Refusal] = Field(default_factory=list)
    voice: Voice | None = None
    knowledge_scope: list[str] = Field(default_factory=list)
    secrets: list[Secret] = Field(default_factory=list)
    ties: list[str] = Field(default_factory=list)
    licenses: list[dict[str, Any]] = Field(default_factory=list)
    sealed_fields: list[str] = Field(default_factory=lambda: ["wants", "fears", "refusals", "secrets", "knowledge"])

    @classmethod
    def from_record(cls, rec: dict[str, Any]) -> NPC:
        """A seed cast record (12.16.11) as an NPC."""
        return cls.model_validate({k: v for k, v in rec.items() if k in cls.model_fields})


class Reaction(BaseModel):
    table: str
    roll: int
    modifier: int
    standing: int
    rung: str


def _tables() -> dict[str, dict[str, Any]]:
    return {t["id"]: t for t in _data.load("oracles.yaml")["tables"]}


def _roll(dice: Dice, tid: str) -> dict[str, Any]:
    t = _tables()[tid]
    return by_range(t["results"], dice.die(t["die"]))


def default_oracle(rng: SeedRng) -> Oracle:
    """# rule: PR-01-4 -- a plain yes/no Oracle: d100 at or above the rung's yes_on is yes (no extremes, no twist).

    Stand-in until the engine's logged Oracle is passed as `oracle=`; odds from `resolution.yaml#oracle`."""
    rungs = {r["id"]: r for r in _data.load("resolution.yaml")["oracle"]["rungs"]}

    def ask(question: str, odds: str) -> bool:
        r = rungs[odds]
        if r.get("roll") is False:
            return bool(r["answer"])
        return rng.randint(1, 100) >= r["yes_on"]
    return ask


def generic_name(dice: Dice) -> str:
    """# rule: 12.11.1 -- tbl.name_given + tbl.name_family when no region name table applies."""
    return "{} {}".format(_roll(dice, "tbl.name_given")["result"], _roll(dice, "tbl.name_family")["result"])


_ROLE_AGE = ((r"child|children|kid|urchin|boy|girl|lad|lass|youngster", "a child"),
             (r"old|elderly|aged|crone|grandmother|grandfather|granny", "old"),
             (r"youth|teen|teenager|young", "young (in their teens)"))
_ROLE_GENDER = ((r"girl|lass|woman|women|mother|wife|widow|daughter|sister|crone|grandmother|granny|lady|maid",
                 ("woman", "she/her")),
                (r"boy|lad|man|men|father|husband|widower|son|brother|grandfather|lord", ("man", "he/him")))
_NEGATED = re.compile(r"\bnot an?\s+\w+", re.I)  # "a child who is not a boy" implies no sex


def role_implies(role: str | None) -> tuple[str | None, tuple[str, str] | None]:  # rule: PR-12-5
    """(age, (gender, pronouns)) the role's own words state ("child by the pilings" -> a child), else None each:
    a walk-on never contradicts the words it was written from."""
    text = _NEGATED.sub(" ", role or "")

    def hit(table: Any) -> Any:
        return next((v for pat, v in table if re.search(rf"(?<![\w-])(?:{pat})(?![\w-])", text, re.I)), None)

    return hit(_ROLE_AGE), hit(_ROLE_GENDER)


def walk_on(rng: SeedRng, *, role: str | None = None, home: str | None = None, people: str | None = None,
            name_tables: Sequence[dict[str, Any]] = (), given_used: set[str] | None = None,
            existing_ids: Iterable[str] = (), member_of: Sequence[str] = (), role_tags: Sequence[str] = (),
            name: str | None = None, pronouns: str | None = None) -> NPC:
    """# rule: PR-12-5 step 2 -- role, name, gender and pronouns, age band, one detail, demeanor.

    `role` is the narration's ("the innkeeper"); else tbl.npc_role. `people` is an origin id
    (orig.people.*): its region name table is used when `name_tables` (the seed's `names`) holds one.
    [spec 033 R6] `name` and `pronouns` ("she/her", "he/him", "they/them") are the dm-tools DM's own words: given, they
    are kept as stated and the role is never read for age or pronouns (`role_implies` is the pipeline's).
    """
    dice = Dice(rng)
    origins = _origins()
    if role is None:
        role = str(_roll(dice, "tbl.npc_role")["result"])
    tabs = [t for t in name_tables if people and t["people"] == people]
    used = given_used if given_used is not None else set()
    rolled_name = person_name(dice, list(tabs), people or "", used) if tabs else generic_name(dice)
    g = _roll(dice, "tbl.npc_gender")
    age = _roll(dice, "tbl.npc_age")["result"]
    if pronouns:  # [spec 033 R6] stated by the DM (`as`), never implied by the role's words
        g = {"result": {"she/her": "woman", "he/him": "man"}.get(pronouns, "person"), "pronouns": pronouns}
    else:
        implied_age, implied_g = role_implies(role)  # the role's own words win over the rolls (PR-12-5: implied kept)
        age = implied_age or age
        if implied_g:
            g = {"result": implied_g[0], "pronouns": implied_g[1]}
    name = name or rolled_name
    detail = _roll(dice, "tbl.npc_detail")["result"]
    demeanor = _roll(dice, "tbl.npc_demeanor")["result"]
    taken = set(existing_ids)
    nid = f"npc.{slug(name)}"
    while nid in taken:
        nid += f"_{dice.d(9):d}"
    folk = None
    if people and people in origins:
        folk = next((t for t in origins[people]["tags"] if t.startswith("creature.folk")), None)
    return NPC(id=nid, name=name, role=role, people=folk, gender=g["result"], pronouns=g["pronouns"], age=age,
               detail=detail, demeanor=demeanor, home=home, member_of=list(member_of), role_tags=list(role_tags))


def promote_recurring(rng: SeedRng, npc: NPC, *, knowledge_scope: Sequence[str] = ()) -> NPC:
    """# rule: PR-12-5 step 4 -- want, fear, voice register and habit, one refusal, knowledge scope."""
    if npc.depth in ("recurring", "principal"):
        return npc
    dice = Dice(rng)
    want = roll_want(dice)
    fear = _roll(dice, "tbl.npc_fear")["result"]
    register = _roll(dice, "tbl.npc_voice_register")["result"]
    habit = _roll(dice, "tbl.npc_voice_habit")["result"]
    r = roll_refusal(dice, npc.role_tags)
    return npc.model_copy(update={
        "depth": "recurring", "wants": [Want(text=want, tags=npc.role_tags[:1] or ["conduct.loyalty"], rank=1)],
        "fears": [Fear(text=fear)], "voice": Voice(register=register, habit=habit),
        "refusals": [Refusal(kind=r.get("kind", "refusal.self"), text=r["result"])],
        "knowledge_scope": list(knowledge_scope) or [npc.role] + ([npc.people] if npc.people else [])})


def promote_principal(rng: SeedRng, npc: NPC, *, home_band: int = 1, oracle: Oracle | None = None,
                      tie_candidates: Sequence[tuple[str, str]] = ()) -> NPC:
    """# rule: PR-12-5 step 5 -- a sealed secret (Oracle, Even), two more ranked wants, ties; band from home.

    `tie_candidates`: (faction or NPC id, odds rung) -- "likely" for the NPC's own trade's institutions,
    "unlikely" otherwise (12.11.1). The band becomes the home area's band, never lower (I-089).
    """
    npc = promote_recurring(rng, npc)
    if npc.depth == "principal":
        return npc
    dice = Dice(rng)
    ask = oracle or default_oracle(rng)
    secrets = list(npc.secrets)
    if ask("does this person keep a secret that matters here?", "even"):
        secrets.append(Secret(fact="sec.{}.1".format(npc.id.split(".", 1)[1]), text=_roll(dice, "tbl.npc_secret")["result"],
                              gate="standing Devoted, or a clue found by play (15.9)"))
    wants = list(npc.wants)
    for rank in (2, 3):
        wants.append(Want(text=roll_want(dice), tags=npc.role_tags[:1] or ["conduct.loyalty"], rank=rank))
    ties = list(npc.ties) + [cid for cid, odds in tie_candidates if ask(f"is {npc.id} tied to {cid}?", odds)]
    return npc.model_copy(update={"depth": "principal", "secrets": secrets, "wants": wants, "ties": ties,
                                  "member_of": list(dict.fromkeys(npc.member_of + [t for t in ties if t.startswith("fac.")])),
                                  "band": max(npc.band, home_band),
                                  "licenses": npc.licenses or [{"id": lid, "grade": "trained"} for t in npc.role_tags
                                                               if (lid := role_license(t))]})


def reaction_roll(rng: SeedRng, *, modifiers: int = 0, faction_status: int | None = None) -> Reaction:
    """# rule: 12.11.2 -- starting standing at the first interaction (2d6; never Devoted).

    `faction_status`: a faction member's base (the faction's status toward the PC): tbl.npc_reaction_member's
    individual step, clamped -3..+3. Otherwise tbl.npc_reaction + `modifiers` (each a cited +1/-1 flag), the
    modifiers clamped to +-2.
    """
    t = _tables()
    roll = rng.randint(1, 6) + rng.randint(1, 6)
    if faction_status is not None:
        tab = t["tbl.npc_reaction_member"]
        row = by_range(tab["results"], roll)
        lo, hi = tab["clamp"]
        standing = max(lo, min(hi, faction_status + row["standing_delta"]))
        return Reaction(table=tab["id"], roll=roll, modifier=0, standing=standing, rung=_rung(standing))
    tab = t["tbl.npc_reaction"]
    lo, hi = tab["modifier"]["total_clamp"]
    mod = max(lo, min(hi, modifiers))
    total = roll + mod
    row = next(r for r in tab["results"] if _in(r["range"], total))
    return Reaction(table=tab["id"], roll=roll, modifier=mod, standing=row["standing"], rung=row["result"])


def _in(rng_s: str, v: int) -> bool:
    s = str(rng_s)
    if s.endswith(" or less"):
        return v <= int(s.split()[0])
    if s.endswith(" or more"):
        return v >= int(s.split()[0])
    a, _, b = s.partition("-")
    return int(a) <= v <= int(b or a)


def _rung(standing: int) -> str:
    names = {-3: "hostile", -2: "unfriendly", -1: "wary", 0: "neutral", 1: "warm", 2: "friendly", 3: "devoted"}
    return names[standing]


def _origins() -> dict[str, dict[str, Any]]:
    o = _data.load("origins.yaml")
    out = {x["id"]: x for x in o["origins"]}
    out.update({e["id"]: e for b in o.get("blocks") or [] for e in b.get("entries") or []})
    return out
