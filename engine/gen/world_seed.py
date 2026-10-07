"""The world seed (PR-12-9, 12.16) as a stepped procedure, and its output `SeededWorld`.

    ws = WorldSeed.from_seed(1234, mode="mixed")          # or WorldSeed(rng, era_rng=..., powers_rng=..., ...)
    ws.answer("ws.q.wound", "long_winter")                # a player's option, any time before its step runs
    ws.answer("ws.q.arcane_source", "order_only", words="only the old families do magic")   # own words, classified
    step = ws.run_step()                                  # -> SeedStep(n, summary "[SEED n/14] ...", answers)
    step = ws.veto()                                      # once per step: re-roll that step's oracle answers
    ...                                                   # steps 1-13; then
    check = ws.run_check()                                # step 14 (12.16.17); a failing step re-runs
    world = ws.world()                                    # SeededWorld

    world = build_rolled(seed)                            # oracle mode, no vetoes: the reference's output exactly

`build_rolled(seed).record` equals `_process/simulation/12-world-seed.py#build_seed(seed)` (T052). Randomness is
three streams: the main one (every step, in the reference's order) and two the reference derives from the seed
number (the wound's age, `seed * 1013 + 69`; the far powers, `seed * 1009 + 83`) so they never move a main draw.
A veto or a check re-run continues the main stream (snapshots never copy a stream), so a vetoed step rolls anew.
"""

from __future__ import annotations

import copy
import random
from typing import Any, Literal

from pydantic import BaseModel, Field

from engine.gen import _seed_steps as steps
from engine.gen._rng import SeedRng
from engine.gen._seed_check import check_seed
from engine.gen._seed_lib import Answers, Dice, Names, Rec, data
from engine.gen.npc import NPC

Mode = Literal["guided", "oracle", "mixed"]
Source = Literal["player", "player_words", "oracle"]
LAST_STEP = 13
CHECK_STEP = 14
ORACLE = object()        # answer(qid, ORACLE): in guided mode, the player hands this question to the oracle


class SeedError(RuntimeError):
    """A seed step was run out of order, an answer is missing in guided mode, or a veto is not allowed."""


# --------------------------------------------------------------------------------------------- output models


class SeedAnswer(BaseModel):
    question: str
    answer: Any
    source: Source
    words: str | None = None


class SeedStep(BaseModel):
    n: int
    name: str
    rule: str
    answers: list[SeedAnswer]
    summary: str
    vetoed: bool = False


class CheckResult(BaseModel):
    requirement: str
    ok: bool
    note: str = ""


class Region(BaseModel):
    id: str
    name: str
    climate: str
    wound: str
    pitch: str
    truths: list[str]
    haven: str


class Place(BaseModel):
    id: str
    name: str
    kind: str                       # place_kind (10.1.1)
    parent: str | None
    ring: int | None
    band: int | None
    danger: str | None
    terrain: list[str]
    known: bool
    discovered: bool
    safe: bool
    desc: str


class Route(BaseModel):
    """A two-way route link (10.1): `watches` is its length in travel watches."""

    id: str
    a: str
    b: str
    kind: str                       # road | track | trackless
    watches: int
    terrain: str
    known: bool


class FactionBrief(BaseModel):
    """A faction as the table may know it: its goal, clock and linchpin fates are sealed and left out."""

    id: str
    name: str
    tier: int
    seat: str | None
    full: bool
    temperament: str
    officers: list[str]
    relations: dict[str, int]


class Thread(BaseModel):
    id: str
    kind: Literal["situation", "lead"]
    text: str
    points_to: str


class Incident(BaseModel):
    option: str
    text: str
    scene: str
    place: str
    date: str
    watch: str
    leads: list[Thread]


class SeededWorld(BaseModel):
    """The world seed's output. `record` is the full region record (SCHEMAS.md#region_yaml), sealed parts included;
    the typed fields are views of it."""

    seed: int | None
    mode: Mode
    answers: list[SeedAnswer]
    region: Region
    places: list[Place]
    routes: list[Route]
    factions: list[FactionBrief]
    cast: list[NPC]
    threads: list[Thread]
    incident: Incident
    check: list[CheckResult] = Field(default_factory=list)
    record: dict[str, Any]

    @classmethod
    def from_record(cls, reg: Rec, check: list[CheckResult] | None = None, mode: Mode | None = None) -> SeededWorld:
        """# rule: 12.16.1 -- the typed views of a region record (a generated seed or a pre-made one)."""
        r = reg["region"]
        places = [Place(id=p["id"], name=p["name"], kind=p["place_kind"], parent=p["parent"], ring=p["ring"],
                        band=p["band"], danger=p["danger"], terrain=p["terrain"], known=p["known"],
                        discovered=p["discovered"], safe=p["safe"], desc=p["desc"]) for p in reg["places"]]
        routes: dict[str, Route] = {}
        for p in reg["places"]:
            for x in p["links"]:
                if x["route"] not in routes:
                    routes[x["route"]] = Route(id=x["route"], a=p["id"], b=x["to"], kind=x["route_kind"],
                                               watches=x["travel_watches"], terrain=x["terrain"][0], known=x["known"])
        facs = [FactionBrief(id=f["id"], name=f["name"], tier=f["tier"], seat=f["seat"], full=f["full"],
                             temperament=f["temperament"], officers=f["officers"], relations=f["relations"])
                for f in reg["factions"]["instances"]]
        o = reg["opening"]
        leads = [Thread(id=f"lead.{i + 1:d}", kind="lead", text=x["lead"], points_to=x["points_to"])
                 for i, x in enumerate(o["leads"])]
        sits = [Thread(id=s["id"], kind="situation", text=s["what"], points_to=s["region"]) for s in reg["situations"]]
        inc = o["inciting"]
        seed = reg.get("seed") or {}
        return cls(
            seed=seed.get("seed"), mode=mode or seed.get("mode", "oracle"),
            answers=[SeedAnswer.model_validate(a) for a in seed.get("answers", [])],
            region=Region(id=r["id"], name=r["name"], climate=r["climate"], wound=r["wound"], pitch=r["pitch"],
                          truths=r["truths"], haven=r["haven"]),
            places=places, routes=list(routes.values()), factions=facs,
            cast=[NPC.from_record(n) for n in reg["npcs"]], threads=sits + leads,
            incident=Incident(option=inc["option"], text=inc["text"], scene=inc["scene"], place=o["start"]["place"],
                              date=o["start"]["date"], watch=o["start"]["watch"], leads=leads),
            check=check or [], record=reg)


# --------------------------------------------------------------------------------------------- the procedure


def step_info(n: int) -> Rec:
    return next(s for s in data().WS["steps"] if s["n"] == n)


def questions(n: int) -> list[Rec]:
    """The questions step n asks (T-12-15), with their options: what a guided or mixed player answers."""
    QS, TAB = data().QS, data().TAB
    out = []
    for qid in steps.STEP_QUESTIONS.get(n, []):
        q = QS[qid]
        if "options" in q:
            opts = [o["id"] if isinstance(o, dict) else o for o in q["options"]]
        elif "options_from" in q and q["options_from"] in TAB:
            opts = [r["option"] for r in TAB[q["options_from"]].get("results", []) if "option" in r]
        else:
            opts = []
        out.append({"id": qid, "ask": q["ask"], "options": opts})
    return out


class WorldSeed:
    """PR-12-9 run step by step. Every step can take the player's answers, roll, or be vetoed once."""

    def __init__(self, rng: SeedRng, *, era_rng: SeedRng, powers_rng: SeedRng, mode: Mode = "mixed",
                 seed: int | None = None):
        self.dice, self.era_dice, self.powers_dice = Dice(rng), Dice(era_rng), Dice(powers_rng)
        self.mode: Mode = mode
        self.seed = seed
        self.st: Rec = steps.new_state()
        self.given: dict[str, Any] = {}
        self.sources: dict[str, str] = {}
        self.words: dict[str, str] = {}
        self.next_step = 1
        self.history: list[SeedStep] = []
        self._before: dict[int, Rec] = {}       # state snapshot before each step ran
        self._vetoed: set[int] = set()
        self._check: list[CheckResult] | None = None

    @classmethod
    def from_seed(cls, seed: int, mode: Mode = "oracle") -> WorldSeed:
        """The reference's streams for one seed number (`random.Random`)."""
        return cls(random.Random(seed), era_rng=random.Random(seed * 1013 + 69),
                   powers_rng=random.Random(seed * 1009 + 83), mode=mode, seed=seed)

    # ------------------------------------------------------------------------------------ answers

    def answer(self, qid: str, value: Any, *, words: str | None = None) -> None:
        """# rule: 12.16.2 -- the player's option (or own words classified to `value`) for a question not yet run."""
        if self.mode == "oracle":
            raise SeedError("oracle mode: the engine rolls every question (veto instead)")
        if qid not in data().QS:
            raise SeedError(f"unknown seed question {qid}")
        n = next(k for k, qs in steps.STEP_QUESTIONS.items() if qid in qs)
        if n < self.next_step:
            raise SeedError(f"{qid} belongs to step {n:d}, which has already run")
        if value is ORACLE:
            self.given.pop(qid, None)
            self.sources[qid] = "oracle_requested"
            return
        self.given[qid] = value
        self.sources[qid] = "player_words" if words else "player"
        if words:
            self.words[qid] = words

    def missing(self, n: int | None = None) -> list[str]:
        """Guided mode: the step's questions the player has neither answered nor handed to the oracle."""
        n = self.next_step if n is None else n
        if self.mode != "guided":
            return []
        return [q for q in steps.STEP_QUESTIONS.get(n, []) if q not in self.given and q not in self.sources]

    # ------------------------------------------------------------------------------------ steps

    def run_step(self) -> SeedStep:
        """# rule: PR-12-9 step 2-3 -- run the next of steps 1-13 and return its `[SEED n/14]` summary."""
        n = self.next_step
        if n > LAST_STEP:
            raise SeedError("steps 1-13 are done; run the check")
        if self.missing(n):
            raise SeedError("guided mode: step {:d} needs answers for {}".format(n, ", ".join(self.missing(n))))
        self._before[n] = copy.deepcopy(self.st)
        self._run(n, self.given)
        self.next_step = n + 1
        self._check = None
        rec = self._record_step(n, vetoed=False)
        self.history.append(rec)
        return rec

    def veto(self, question: str | None = None) -> SeedStep:
        """# rule: 12.16.2 -- re-roll the last step's oracle answers once (only `question`'s, if named).

        The player's own answers stand. Allowed once per step, before the next step runs.
        """
        n = self.next_step - 1
        if n < 1 or n in self._vetoed:
            raise SeedError("no step to veto" if n < 1 else f"step {n:d} was already vetoed once")
        prev = [a for a in self.st["log"][len(self._before[n]["log"]):]]
        rolled = [a["question"] for a in prev if a["source"] == "oracle"]
        if steps.STEP_QUESTIONS[n] and not rolled:
            raise SeedError(f"step {n:d} has no oracle answer to veto")
        if question is not None and question not in rolled:
            raise SeedError(f"{question} was not rolled by the oracle in step {n:d}")
        pinned = dict(self.given)
        pinned_src = dict(self.sources)
        if question is not None:
            for a in prev:
                if a["question"] != question and a["source"] == "oracle":
                    pinned[a["question"]] = a["answer"]
                    pinned_src[a["question"]] = "oracle"
        self.st = copy.deepcopy(self._before[n])
        self._run(n, pinned, pinned_src)
        self._vetoed.add(n)
        self._check = None
        rec = self._record_step(n, vetoed=True)
        self.history.append(rec)
        return rec

    def _run(self, n: int, given: dict[str, Any], sources: dict[str, str] | None = None) -> None:
        src = {k: v for k, v in (sources or self.sources).items() if k in given}
        A = Answers(given, src, log=self.st["log"])
        names = Names(self.dice, self.st["names_used"])
        if n == 1:
            steps.step1_premise(self.st, self.dice, A, names, self.era_dice)
        elif n == LAST_STEP:
            steps.step13_opening(self.st, self.dice, A, names, self.powers_dice)
        else:
            steps.STEPS[n](self.st, self.dice, A, names)

    def _record_step(self, n: int, vetoed: bool) -> SeedStep:
        info = step_info(n)
        new = self.st["log"][len(self._before[n]["log"]):]
        answers = [SeedAnswer(question=a["question"], answer=a["answer"], source=a["source"],
                              words=self.words.get(a["question"])) for a in new]
        return SeedStep(n=n, name=info["name"], rule=info["rule"], answers=answers,
                        summary=summary(n, self.st, answers), vetoed=vetoed)

    # ------------------------------------------------------------------------------------ check and output

    def run_all(self) -> SeededWorld:
        while self.next_step <= LAST_STEP:
            self.run_step()
        self.run_check()
        return self.world()

    def record(self) -> Rec:
        """# rule: 12.16.1 -- the region record from the steps' writes (a fresh deep copy)."""
        if self.next_step <= LAST_STEP:
            raise SeedError(f"the record exists after step 13 (next step: {self.next_step:d})")
        st = copy.deepcopy(self.st)
        # the record's mode is the reference's: "guided" when any answer came from the player, else "oracle"
        reg = steps.assemble(st, self.seed, "guided" if self.given else "oracle")
        _apply_words(reg, self.words)
        return reg

    def run_check(self, max_reruns: int = 3) -> list[CheckResult]:
        """# rule: 12.16.17 -- step 14: every T-12-16 requirement; a failure re-runs the step writing its key."""
        for _ in range(max_reruns + 1):
            res = [CheckResult(requirement=r, ok=o, note=nt) for r, o, nt in check_seed(self.record())]
            failed = [c for c in res if not c.ok]
            if not failed:
                self._check = res
                return res
            n = min(_step_for(c.requirement) for c in failed)
            self.st = copy.deepcopy(self._before[n])
            for k in range(n, LAST_STEP + 1):
                self._before[k] = copy.deepcopy(self.st)
                self._run(k, self.given)
            self.history.append(SeedStep(n=CHECK_STEP, name="The seed check", rule="12.16.17", answers=[],
                                         summary="[SEED 14/14] {:d} requirement(s) failed ({}); steps {:d}-13 re-run.".format(len(failed), ", ".join(c.requirement for c in failed), n)))
        raise SeedError(f"the seed check still fails after {max_reruns:d} re-runs")

    def world(self) -> SeededWorld:
        """The seeded world; the check must have passed (PR-12-9 step 4: the seed is used only then)."""
        if self._check is None:
            self.run_check()
        return SeededWorld.from_record(self.record(), self._check, self.mode)


def build_rolled(seed: int) -> SeededWorld:
    """# rule: PR-12-9 -- oracle mode, no vetoes, every step rolled: the reference script's output for `seed`."""
    ws = WorldSeed.from_seed(seed, mode="oracle")
    while ws.next_step <= LAST_STEP:
        ws.run_step()
    return SeededWorld.from_record(ws.record())


def build_answered(seed: int, given: dict[str, Any]) -> SeededWorld:
    """Mixed mode with `given` answers and no vetoes: the reference's `build_seed(seed, given)`."""
    ws = WorldSeed.from_seed(seed, mode="mixed")
    for q, v in given.items():
        ws.answer(q, v)
    while ws.next_step <= LAST_STEP:
        ws.run_step()
    return SeededWorld.from_record(ws.record())


def _step_for(requirement: str) -> int:
    """The step that writes a requirement's key (world_seed.yaml#requirements key vs #steps writes)."""
    D = data()
    rq = next(r for r in D.WS["requirements"] if r["id"] == requirement)
    head = str(rq["key"]).split("/")[0].split("[")[0].split(" ")[0]
    for s in D.WS["steps"]:
        if any(str(w).split("/")[0].split("[")[0].split(" ")[0] == head for w in s["writes"]) and s["n"] <= LAST_STEP:
            return s["n"]
    return 1


def _apply_words(reg: Rec, words: dict[str, str]) -> None:
    """# rule: 12.16.2 -- a player's own words are kept as the description, never as a mechanic."""
    if "ws.q.wound" in words:
        reg["region"]["pitch"] = words["ws.q.wound"]
    if "ws.q.arcane_source" in words:
        for f in reg["canon"]["facts"]:
            if f["id"] == "canon.arcane_source":
                f["text"] = words["ws.q.arcane_source"]
        reg["canon"]["magic"]["item_2_sources"]["arcane"] = words["ws.q.arcane_source"]
    for q in ("ws.q.haven_site", "ws.q.haven_tier"):
        if q in words:
            hav = next(p for p in reg["places"] if p["id"] == reg["region"]["haven"])
            hav["desc"] = words[q]
    for a in reg["seed"]["answers"]:
        if a["question"] in words:
            a["words"] = words[a["question"]]


# --------------------------------------------------------------------------------------------- summaries


def summary(n: int, st: Rec, answers: list[SeedAnswer]) -> str:
    """# rule: 12.16.3 -- a step's `[SEED n/14]` block: what was answered or rolled and what it wrote, shown parts only."""
    head = "[SEED {:d}/14] {}".format(n, step_info(n)["name"])
    got = "; ".join("{}: {} ({})".format(a.question.split(".")[-1], _fmt(a.answer), "you" if a.source != "oracle" else "rolled")
                    for a in answers)
    lines = [head] + (["  answers: " + got] if got else []) + ["  " + x for x in _SUMMARY[n](st)]
    return "\n".join(lines)


def _fmt(v: Any) -> str:
    if isinstance(v, dict):
        return ", ".join("{} {}".format(str(k).split(".")[-1], _fmt(x)) for k, x in v.items())
    if isinstance(v, list):
        return ", ".join(_fmt(x) for x in v) or "none"
    return str(v)


def _places(st: Rec) -> Rec:
    return st["S"]["_places"]


def _s1(st: Rec) -> list[str]:
    return ["{}: {}".format(st["region_name"][0].upper() + st["region_name"][1:], st["wound"]["text"]),
            "climate {}; the trouble began {:d} years ago".format(st["climate"], st["ctx"]["era_age"])]


def _s2(st: Rec) -> list[str]:
    return ["impossible here: " + "; ".join(c["text"] for c in st["ci"]),
            "magic {}, {}; arcane: {}; spirits {}".format(st["lvl"], st["law"], st["arc_text"], st["spirits"])]


def _s3(st: Rec) -> list[str]:
    return ["keepers: " + "; ".join("{} ({})".format(k["name"], k["what"]) for k in st["keepers"]),
            "at death's door: " + st["bargainer"]["text"]]


def _s4(st: Rec) -> list[str]:
    pres = ", ".join("{} {}".format(p["origin"].split(".")[-1].replace("_", "-"), p["present"]) for p in st["peoples"]
                     if p["present"] != "absent")
    return ["peoples: " + pres, "tongues: " + ", ".join(t["license"].split(".")[-1] for t in st["tongues"]["list"])]


def _s5(st: Rec) -> list[str]:
    P = _places(st)
    out = []
    for ring in range(1, 6):
        out.append("ring {:d}: {}".format(ring, ", ".join("{} ({})".format(P[a]["name"], P[a]["terrain"][0].split(".")[-1])
                                                    for a in st["areas_by_ring"][ring] if P[a]["known"]) or "unknown country"))
    return out


def _s6(st: Rec) -> list[str]:
    P = _places(st)
    return ["{}: {}".format(P[st["hid"]]["name"], P[st["hid"]]["desc"]),
            "in it: " + ", ".join(P[b]["name"] for b in st["blds"].values()),
            "place of acceptance: {}".format(P[st["acc_id"]]["name"])]


def _s7(st: Rec) -> list[str]:
    return ["{} (tier {:d})".format(f["name"], f["tier"]) for f in st["factions"]]


def _s8(st: Rec) -> list[str]:
    return ["{:d} people: ".format(len(st["S"]["npcs"])) + "; ".join("{}, {}".format(n["name"], n["role"]) for n in st["S"]["npcs"][:12])]


def _s9(st: Rec) -> list[str]:
    P = _places(st)
    known = [P[s]["name"] for s in st["sites"] if P[s]["known"]]
    return ["known sites: " + ", ".join(known), "troubles: " + "; ".join(s["title"] for s in st["situations"])]


def _s10(st: Rec) -> list[str]:
    return ["{:d} encounter tables built (PR-10-10) and audited (PR-10-8)".format(len(st["enc_tables"]))]


def _s11(st: Rec) -> list[str]:
    return ["{:d} rumors told in the haven (whether they are true is not shown)".format(len(st["rumor_tables"][0]["results"]))]


def _s12(st: Rec) -> list[str]:
    c = st["calendar"]
    return ["months: " + ", ".join(c["months"]), "era: {}; festivals: {}".format(c["era"]["name"],
                                                                           ", ".join(f["name"] for f in c["festivals"]))]


def _s13(st: Rec) -> list[str]:
    o = st["opening"]
    P = _places(st)
    return ["{}, {}, {}: {}".format(o["start"]["date"], o["start"]["watch"], P[o["start"]["place"]]["name"],
                                o["inciting"]["text"]),
            "pregens: " + "; ".join(p["sentence"] for p in st["pregens"])]


_SUMMARY: dict[int, Any] = {1: _s1, 2: _s2, 3: _s3, 4: _s4, 5: _s5, 6: _s6, 7: _s7, 8: _s8, 9: _s9, 10: _s10,
                            11: _s11, 12: _s12, 13: _s13}
