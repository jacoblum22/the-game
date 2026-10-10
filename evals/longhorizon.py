"""Long-horizon harness (spec 005, US3; research notes A P8): an aged synthetic store and a scripted player.

    py -3.12 evals/longhorizon.py                          # both modes, offline model, seed 7
    py -3.12 evals/longhorizon.py --mode aged --scenes 300
    py -3.12 evals/longhorizon.py --mode scripted --lines 300
    py -3.12 evals/longhorizon.py --model gemini           # owner-run only: needs GEMINI_API_KEY, costs money

`aged` plays the setup, then appends seeded synthetic scenes straight to the event log (one new NPC each, three
facts, one of them known to the PC, a commitment every 10th scene) and, at each checkpoint, plays a look and
recall probes. `scripted` plays ~300 lines from templates (revisits, absent NPCs, recall and promise probes,
scuffles, notices) through the e2e `Driver`. With the offline model the prose is canned: the numbers measure
the pipeline (packet size, caching, retrieval), not the writing.
"""

from __future__ import annotations

import argparse
import copy
import random
import re
import shutil
import sys
import tempfile
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine import ids  # noqa: E402
from engine.dm.dispute import dispute_stats  # noqa: E402
from engine.game import GameConfig  # noqa: E402
from engine.store.events import Event  # noqa: E402
from engine.world.common import active_pc  # noqa: E402
from evals.replay_bench import sections  # noqa: E402
from tests.e2e.driver import Driver  # noqa: E402

CHECKPOINTS = (50, 200, 300)
CONFIG = GameConfig(offline=True)  # main() sets the engine (spec 031: --engine dm-tools) and the secrets arm
_STOP = {"the", "and", "with", "that", "this", "from", "into", "for", "has", "have", "was", "are", "her", "his",
         "their", "they", "them", "you", "your", "not", "but", "who", "what"}


# ------------------------------------------------------------------------------------------------ metrics


def tokens(text: str) -> int:
    """≈ tokens as characters / 4. ponytail: no tokenizer dependency; swap in Gemini's count_tokens if needed."""
    return (len(text) + 3) // 4


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def novelty4(deliveries: list[str], window: int = 10) -> float:
    """Mean share of a delivery's word 4-grams absent from the previous `window` deliveries (A P8)."""
    grams = [{tuple(w[i:i + 4]) for i in range(len(w) - 3)} for w in map(_words, deliveries)]
    shares = []
    for i, g in enumerate(grams):
        if not g or i == 0:
            continue
        seen = set().union(*grams[max(0, i - window):i])
        shares.append(len(g - seen) / len(g))
    return sum(shares) / len(shares) if shares else 1.0


def prefix_share(packets: Iterable[tuple[str, str]]) -> dict[str, float]:
    """{role: mean share of each packet that repeats the role's previous packet from the start}: what an implicit
    prefix cache could reuse (A P6)."""
    last: dict[str, str] = {}
    shares: dict[str, list[float]] = {}
    for role, p in packets:
        prev = last.get(role)
        if prev is not None and p:
            n = 0
            for a, b in zip(prev, p, strict=False):
                if a != b:
                    break
                n += 1
            shares.setdefault(role, []).append(n / len(p))
        last[role] = p
    return {r: sum(v) / len(v) for r, v in sorted(shares.items())}


def _content(text: str) -> set[str]:
    return {w for w in _words(text) if len(w) > 2 and w not in _STOP}


def matches(value: Any, text: str, need: float = 0.6) -> bool:
    want = _content(str(value))
    return bool(want) and len(want & _content(text)) >= need * len(want)


def recall_score(answer: str, known: list[str], stored: list[str], name: str) -> tuple[float | None, float | None]:
    """(precision, coverage) of a "what do I know about X?" answer. Coverage: share of the PC-known values about X
    that the answer states. Precision: share of the answer's lines about X (naming X or stating a value) that
    state something the store holds about X (no invention). ponytail: word-overlap matching; an LLM judge would
    catch paraphrase."""
    if not known:
        return None, None
    lines = [s for s in answer.splitlines() if len(_content(s)) >= 2 and not s.rstrip().endswith(":")]
    hits = [s for s in lines if any(matches(t, s) for t in stored)]
    about = [s for s in lines if name.split()[0].lower() in s.lower() or s in hits]
    covered = sum(1 for t in known if matches(t, answer))
    return (len(hits) / len(about) if about else None), covered / len(known)


def contradictions(turn_records: Iterable[dict[str, Any]]) -> tuple[int, Counter[str]]:
    """(narrated turns, `contradicted` claim-log entries by claim class; spec 011: the claim log holds the sampled
    audit's verdicts, a certain subject only)."""
    n = 0
    by: Counter[str] = Counter()
    for r in turn_records:
        if not r.get("draft_versions"):
            continue
        n += 1
        by.update(str(e.get("class")) for e in r.get("claim_log") or [] if e.get("verdict") == "contradicted")
    return n, by


def claim_log_lines(turns: list[dict[str, Any]]) -> list[str]:  # rule: OEQ-12-23
    """Spec 011 item 12: claim-log entries per 100 narrated turns by class, and the sampled audit's blocking-list
    misses per 100 narrated turns (OEQ-12-23: more than 1 per 100 adds a code scan, DL-12-83)."""
    narrated = [t for t in turns if t.get("draft_versions")]
    n = len(narrated)
    if not n:
        return []
    log = [e for t in narrated for e in t.get("claim_log") or []]
    by = Counter(f"{e.get('class')}/{e.get('verdict')}" for e in log)
    sampled = sum(1 for t in narrated if any(e.get("source") == "sample" for e in t.get("claim_log") or [])
                  or any("sample" in v for v in t["draft_versions"]))
    misses = sum(1 for e in log if e.get("blocking_miss"))
    return [f"- claim log per 100 narrated turns: {100 * len(log) / n:.1f} ("
            + ", ".join(f"{k} {100 * v / n:.1f}" for k, v in by.most_common()) + ")",
            f"- sampled audit: {sampled} of {n} narrated turns sampled; blocking-list misses {misses} "
            f"({100 * misses / n:.1f} per 100 narrated turns)"]


def growth(first: dict[str, int], last: dict[str, int], limit: float = 0.10) -> list[str]:
    """Sections whose token count grew by more than `limit` (SC-002: nothing grows with game length)."""
    return [f"{k} {first.get(k, 0)}->{v}" for k, v in last.items() if v > (1 + limit) * first.get(k, 0) and v > 20]


def view_tokens(calls: list[dict[str, Any]]) -> dict[str, tuple[int, int]]:
    """{role: (packet tokens, view-section tokens)} for one turn's calls (largest call per role)."""
    out: dict[str, tuple[int, int]] = {}
    for row in calls:
        p = (row.get("request") or {}).get("packet") or ""
        view = sum(tokens(t) for name, t in sections(p) if "VIEW" in name)
        role = str(row["role"])
        if tokens(p) > out.get(role, (0, 0))[0]:
            out[role] = (tokens(p), view)
    return out


# ------------------------------------------------------------------------------------------------ helpers


def _ev(kind: str, payload: dict[str, Any]) -> Event:
    return Event.model_validate({"type": kind, "payload": payload})


class _NarrationOnly:
    """Claude (the CLI, the owner's subscription) as Narrator and Checker; every other role offline (spec 006)."""

    provider = "claude-narration"

    def __init__(self) -> None:
        from engine.llm.offline import OfflineModel
        from evals.playtest import ClaudeModel

        self.claude, self.offline = ClaudeModel("haiku"), OfflineModel()

    def fill(self, role: Any, schema: Any, packet: Any, **kw: Any) -> Any:
        from engine.llm.base import Role

        return (self.claude if role in (Role.NARRATOR, Role.CHECKER) else self.offline).fill(role, schema, packet, **kw)


def _model(name: str) -> Any:
    from engine.llm.offline import OfflineModel

    if name == "claude-narration":
        return _NarrationOnly()
    if name == "claude":  # every role on Claude Haiku through the CLI (spec 031's head-to-head)
        from evals.playtest import ClaudeModel

        return ClaudeModel("haiku")
    return OfflineModel() if name == "offline" else GameConfig(offline=False).model()


def narration_loop(turns: list[dict[str, Any]]) -> str:
    """Spec 006's gate measures on the turns played: first drafts delivered as drafted, turns where a sentence was
    cut or a line rendered, narrator calls per narrated turn (from each turn's draft versions)."""
    narrated = [t for t in turns if t.get("draft_versions")]
    if not narrated:
        return "- narration loop: no narrated turns"
    kinds = [[v.get("kind") for v in t["draft_versions"]] for t in narrated]
    first = sum(1 for k in kinds if k == ["draft"])
    cut = sum(1 for k in kinds if any(x in ("cut", "render", "fallback") for x in k))
    calls = sum(sum(1 for x in k if x in ("draft", "repair", "redraft", "revision")) for k in kinds)
    stats = Counter[str]()
    for t in narrated:
        for v in t["draft_versions"]:
            stats.update({k: n for k, n in (v.get("stats") or {}).items() if k not in ("rounds", "revisions")})
    n = len(narrated)
    return (f"- narration loop ({n} narrated): first draft delivered as drafted {first}/{n} ({100 * first / n:.1f}%); "
            f"turns with a cut, rendered line or fallback {cut}/{n} ({100 * cut / n:.1f}%); narrator calls per "
            f"narrated turn {calls / n:.2f}; per narrated turn: " + ", ".join(f"{k} {v / n:.2f}" for k, v in
                                                                               sorted(stats.items())))


def _npcs(st: Any) -> list[str]:
    return [i for i, e in st.entities.items() if e.kind == "npc" and e.exists == "exists"]


def _known_values(st: Any, pc: str, subject: str, kind: str | None = None) -> list[str]:
    out = []
    for fid in (st.knowledge.get(pc) or {}):
        f = st.facts.get(fid)
        if f is not None and f.subject == subject and (kind is None or f.kind == kind):
            out.append(str(f.value))
    return out


def _stored_values(st: Any, subject: str) -> list[str]:
    """Everything the store holds about `subject` that is not sealed: fact values and the entity's role."""
    vals = [str(f.value) for f in st.facts.values() if f.subject == subject and f.visibility != "sealed"]
    e = st.entities.get(subject)
    return vals + ([str(e.data["role"])] if e is not None and e.data.get("role") else [])


def _probe(d: Driver, pc: str, npc: str, name: str, question: str, kind: str | None = None) -> tuple[Any, Any]:
    r = d.settle(d.call("submit", question))
    st = d.game.store.state
    return recall_score(r.text(), _known_values(st, pc, npc, kind), _stored_values(st, npc), name)


def _fmt_views(label: str, v: dict[str, tuple[int, int]]) -> str:
    return f"- view tokens at {label}: " + ", ".join(f"{r} {p} (view {w})" for r, (p, w) in sorted(v.items()))


# ------------------------------------------------------------------------------------------------ aged store

FIRST = ["Ada", "Bram", "Cael", "Dena", "Edrin", "Fala", "Garr", "Hesk", "Ilsa", "Joss", "Kira", "Lorn", "Mira",
         "Nesh", "Orla", "Pell", "Quin", "Rhea", "Sorn", "Tova"]
LAST = ["Ashby", "Brook", "Coldwell", "Dunmere", "Elkin", "Fenn", "Greave", "Holt", "Ivers", "Juniper", "Kell",
        "Lark", "Marsh", "Nettle", "Oakes", "Penrose", "Quarry", "Reed", "Stone", "Thorne"]
JOBS = ["a ferryman", "a tanner", "a wool merchant", "a lamplighter", "a gravedigger", "a reeve's clerk",
        "a beekeeper", "a rope maker", "a herbalist", "a bargeman"]
MARKS = ["a burn scar on the left hand", "a copper earring", "a limp in the right leg", "grey-streaked braids",
         "ink-stained fingers", "a broken nose", "a green wool hood", "a missing front tooth"]
NEWS = ["saw lights over the marsh", "lost a brother on the north road", "owes money to the mill",
        "heard bells under the hill", "found a dead hound by the ford", "sells charms against the fog"]


def _age(d: Driver, rng: random.Random, start: int, stop: int, truth: dict[str, dict[str, Any]]) -> None:
    """Append scenes `start`..`stop-1`, then reopen a scene at the home place with the original cast."""
    store = d.game.store
    st = store.state
    pc = active_pc(st)
    assert pc is not None
    home = st.scene.place_id if st.scene else None
    cast = list(st.scene.cast_present) if st.scene else []
    template = next(copy.deepcopy(st.entities[i].data) for i in _npcs(st))
    template.update(secrets=[], knowledge=[], wants=[], fears=[])
    places = sorted(i for i, e in st.entities.items() if e.kind == "place")
    with store.transaction() as tx:
        if st.scene:
            tx.add(_ev("scene_ended", {"scene_id": st.scene.scene_id, "reason": "aged"}))
    for k in range(start, stop):
        npc = f"npc.aged_{k}"
        name = f"{FIRST[k % 20]} {LAST[(k * 7 + k // 20) % 20]}"
        place = places[rng.randrange(len(places))]
        with store.transaction() as tx:
            sid = tx.mint(ids.SCENE)
            tx.add(_ev("scene_started", {"scene_id": sid, "scene": {
                "scene_id": sid, "place_id": place, "cast_present": [npc], "agenda": f"aged scene {k}"}}))
            tx.add(_ev("entity_created", {"entity": {
                "id": npc, "kind": "npc", "name": name, "visibility": "shown",
                "data": {**template, "role": rng.choice(JOBS), "home": place}}}))
            facts = [("occupation", rng.choice(JOBS)), ("detail.mark", rng.choice(MARKS)), ("said", rng.choice(NEWS))]
            if k % 10 == 0:
                facts.append(("promise", f"to carry a sealed letter to {st.entities[place].name}"))
            for n, (pred, value) in enumerate(facts):
                fid = tx.mint(ids.FACT)
                tx.add(_ev("fact_set", {
                    "fact_id": fid, "subject": npc, "predicate": pred, "value": value, "source": "narration",
                    "visibility": "shown", "kind": "commitment" if pred == "promise" else "fact"}))
                if n != 1:  # the PC heard what was said and the promise; the mark is only on record
                    tx.add(_ev("knowledge_recorded", {"knower": pc, "fact_id": fid, "how": "told"}))
            tx.add(_ev("relationship_set", {
                "a": npc, "b": pc, "kind": "standing", "value": 0, "new_value": rng.randint(-1, 2), "reason": "aged"}))
            tx.add(_ev("position_set", {"entity": npc, "location": place}))
            tx.add(_ev("scene_ended", {"scene_id": sid, "reason": "aged"}))
        truth[npc] = {"name": name, "scene": k}
    with store.transaction() as tx:
        sid = tx.mint(ids.SCENE)
        tx.add(_ev("scene_started", {"scene_id": sid, "scene": {
            "scene_id": sid, "place_id": home, "cast_present": cast, "agenda": "home again"}}))


def run_aged(seed: int, scenes: int, model: str, tmp: Path) -> list[str]:
    rng = random.Random(seed)
    d = Driver.start(tmp / "aged.db", seed=seed, model=_model(model), config=CONFIG)
    truth: dict[str, dict[str, Any]] = {}
    pc = active_pc(d.game.store.state)
    assert pc is not None
    out = [f"## Aged store (seed {seed}, {scenes} synthetic scenes)"]
    marks = [c for c in CHECKPOINTS if c <= scenes] or [scenes]
    done = 0
    rec_p: list[float] = []
    rec_c: list[float] = []
    by_age: dict[str, list[float]] = {}
    promise_c: list[float] = []
    narrator_sections: list[dict[str, int]] = []
    spot_sections: list[dict[str, int]] = []
    for mark in marks:
        _age(d, rng, done, mark, truth)
        done = mark
        r = d.settle(d.call("submit", "I look around."))
        calls = d.game.store.model_calls(r.turn_id) if r.turn_id else []
        out.append(_fmt_views(f"scene {mark}", view_tokens(calls)))
        narrator = next(((c.get("request") or {}).get("packet") or "" for c in calls if c["role"] == "narrator"), "")
        narrator_sections.append({name: tokens(t) for name, t in sections(narrator)})
        absent = truth.get(f"npc.aged_{mark // 2}")  # an absent NPC named: the spotlight and scene cards fill (12.2.4)
        if absent:
            r = d.settle(d.call("submit", f"I ask around about {absent['name']}."))
            calls = d.game.store.model_calls(r.turn_id) if r.turn_id else []
            out.append(_fmt_views(f"scene {mark}, an absent NPC named", view_tokens(calls)))
            narrator = next(((c.get("request") or {}).get("packet") or "" for c in calls if c["role"] == "narrator"),
                            "")
            spot_sections.append({name: tokens(t) for name, t in sections(narrator)})
        for label, k in (("oldest", 1), ("middle", mark // 2), ("newest", mark - 1)):
            npc = f"npc.aged_{k}"
            if npc not in truth:
                continue
            name = truth[npc]["name"]
            p, c = _probe(d, pc, npc, name, f"What do I know about {name}?")
            if c is not None:
                rec_c.append(c)
                by_age.setdefault(label, []).append(c)
            if p is not None:
                rec_p.append(p)
        npc = f"npc.aged_{(mark // 20) * 10}"  # a scene with a promise
        if npc in truth:
            name = truth[npc]["name"]
            _, c = _probe(d, pc, npc, name, f"What did I promise {name}?", "commitment")
            promise_c.append(c or 0.0)
    st = d.game.store.state
    out.append(f"- store size: {len(st.entities)} entities, {len(st.facts)} facts, "
               f"{sum(len(v) for v in st.knowledge.values())} knowledge records")
    out.append(f"- recall probes: {len(rec_c)}; precision {_mean(rec_p)}, coverage {_mean(rec_c)} "
               f"(by NPC age: " + ", ".join(f"{k} {_mean(v)}" for k, v in by_age.items()) + ")")
    out.append("- boundedness, narrator sections growing > 10% from first to last checkpoint: "
               + (", ".join(growth(narrator_sections[0], narrator_sections[-1])) or "none"))
    if spot_sections:
        out.append("- boundedness with the spotlight and scene cards on (an absent NPC named), sections growing > 10%: "
                   + (", ".join(growth(spot_sections[0], spot_sections[-1])) or "none"))
    out.append(f"- promise probes: {len(promise_c)}; coverage {_mean(promise_c)}")
    d.game.close()
    return out


def _mean(xs: list[float]) -> str:
    return f"{sum(xs) / len(xs):.2f}" if xs else "n/a"


# ------------------------------------------------------------------------------------------------ scripted

CYCLE = ("look", "talk", "absent", "recall", "scuffle", "notice", "who_knows", "travel", "look2", "promise",
         "revisit", "options", "ask_twice")


def script_line(kind: str, st: Any, rng: random.Random, met: list[str], home_name: str) -> str | None:
    """One scripted player line of `kind`, filled from the live state (None: the driver travels instead)."""
    present = [i for i in (st.scene.cast_present if st.scene else []) if i in st.entities]
    absent = [i for i in met if i not in present]
    who = st.entities[rng.choice(present)].name if present else "the nearest person"
    if kind == "look":
        return rng.choice(["I look around.", "I study the faces here.", "I look for anything out of place."])
    if kind == "look2":
        return "I look closely at the ground and the walls."
    if kind == "talk":
        return f'I ask {who} what is going on here.'
    if kind == "absent":
        return f"Where is {st.entities[rng.choice(absent)].name}?" if absent else "Is anyone missing from here?"
    if kind == "recall":
        return f"What do I know about {st.entities[rng.choice(met)].name}?" if met else "What do I know?"
    if kind == "promise":
        return f"What did I promise {st.entities[rng.choice(met)].name}?" if met else "What have I promised?"
    if kind == "scuffle":
        return rng.choice([f"I shove {who} back a step.", f"I grab {who} by the arm.", f"I swing at {who}."])
    if kind == "notice":
        return "I look for a notice and read it."
    if kind == "who_knows":
        return f'"Who around here would know about the trouble?" I ask {who}.'
    if kind == "revisit":
        return f"I head back to {home_name}."
    if kind == "options":
        return "What are my options?"
    if kind == "ask_twice":  # PR-12-10's index: the same question to the same NPC, twice (spec 008 part B)
        return f'"What are the roads like around here?" I ask {who}.'
    return None  # travel


def ladder_lines(learned: list[dict[str, Any]], twice: tuple[int, int]) -> list[str]:
    """PR-12-10 (spec 013): successful learning beats with no answer (target 0: a fact, a case pointer or a
    willingness line), case-route pointers, and the same question to the same NPC answered the same way (the same
    fact or the same willingness; target 100%)."""
    n = len(learned)
    empty = sum(1 for x in learned if not x["answers"] or not all(a[0] or a[1] or a[3] for a in x["answers"]))
    items = [a for x in learned for a in x["answers"]]
    ptr = sum(1 for a in items if a[1])
    same, asked = twice
    return [f"- learning beats answered (PR-12-10): {n}; empty successes {empty} "
            f"({100 * empty / n if n else 0:.1f}%); items {len(items)}, case pointers {ptr}, willingness lines "
            f"{sum(1 for a in items if a[3])}",
            f"- ask-twice consistency: {same}/{asked} ({100 * same / asked if asked else 0:.0f}%)"]


_DONT = re.compile(r"\b(?:i (?:don'?t|do not) know|no idea|can'?t say|couldn'?t say)\b", re.IGNORECASE)
_REDIRECT = re.compile(r"\b(?:but|ask|try)\b[^.?!]*\b(?:would|knows?|ask)\b", re.IGNORECASE)


def dialogue_lines(turns: list[dict[str, Any]]) -> list[str]:  # rule: 12.10.8
    """OEQ-12-25 (spec 013): per 100 NPC lines (the turn records' `said` spans with a speaker), self-repeats (content
    overlap above `said_overlap` with the same speaker's earlier line), "I don't know" lines, runarounds (an "I don't
    know" with a redirect to someone else), and self-contradictions (a speaker denying knowing a name they said
    earlier; a proxy)."""
    from engine.dm.testimony import overlap

    said = [(str(x.get("speaker")), str(x.get("words") or "")) for t in turns for x in t.get("said") or []
            if x.get("speaker")]
    seen: dict[str, list[str]] = {}
    rep = dont = run = contra = 0
    for sp, w in said:
        prior = seen.setdefault(sp, [])
        rep += any(overlap(w, x) > 0.6 for x in prior)
        if _DONT.search(w):
            dont += 1
            run += bool(_REDIRECT.search(w))
            names = set(re.findall(r"\b[A-Z][a-z]{2,}\b", w))
            contra += any(nm in x for nm in names for x in prior)
        prior.append(w)
    n = len(said)

    def per(k: int) -> str:
        return f"{100 * k / n if n else 0:.1f}"

    return [f"- NPC lines {n}; per 100: repeats {per(rep)}, \"I don't know\" {per(dont)}, runarounds {per(run)}, "
            f"self-contradictions {per(contra)} (OEQ-12-25)"]


FIX_REPORTS = ("My vitality is wrong: I was not hurt.", "I still have my lantern.", "That's not what I meant.",
               "You said earlier the road north was open.")  # --fix-every: planted /fix reports (spec 012)


def dispute_lines(stats: dict[str, Any], narrated: int) -> str:
    """OEQ-12-24 (pacing.yaml#feedback.metric): disputes per 100 narrated turns, all and upheld, by category."""
    def per(n: int) -> str:
        return f"{100 * n / narrated if narrated else 0:.1f}"

    by = ", ".join(f"{k} {v}" for k, v in sorted(stats["by_category"].items()))
    return f"- disputes per 100 narrated turns: {per(stats['all'])} (upheld {per(stats['upheld'])})" + (
        f" ({by})" if by else "")


def run_scripted(seed: int, lines: int, model: str, tmp: Path, fix_every: int = 0) -> list[str]:
    import engine.dm.world_step as ws

    learned: list[dict[str, Any]] = []
    real = ws.deliver_learning

    def spy(ctx: Any, record: Any, beats: Any) -> list[dict[str, Any]]:
        out = real(ctx, record, beats)
        learned.extend(out)
        return out

    ws.deliver_learning = spy  # type: ignore[assignment]  # the measure only reads what the ladder returns
    try:
        return _run_scripted(seed, lines, model, tmp, learned, fix_every)
    finally:
        ws.deliver_learning = real  # type: ignore[assignment]


def _run_scripted(seed: int, lines: int, model: str, tmp: Path, learned: list[dict[str, Any]],
                  fix_every: int = 0) -> list[str]:
    rng = random.Random(seed)
    d = Driver.start(tmp / "scripted.db", seed=seed, model=_model(model), config=CONFIG)
    st = d.game.store.state
    pc = active_pc(st)
    assert pc is not None
    home = st.scene.place_id if st.scene and st.scene.place_id else None
    home_name = st.entities[home].name if home else "the town"
    met: list[str] = []
    turn_at: dict[int, str] = {}
    deliveries: list[str] = []
    rec_p: list[float] = []
    rec_c: list[float] = []
    kinds: Counter[str] = Counter()
    errors: list[str] = []
    streak = 0
    twice = [0, 0]
    for i in range(lines):
        st = d.game.store.state
        met += [x for x in (st.scene.cast_present if st.scene else []) if x not in met and x in st.entities]
        kind = CYCLE[i % len(CYCLE)]
        line = script_line(kind, st, rng, met, home_name)
        kinds[kind] += 1
        n_learned = len(learned)
        try:
            if kind == "recall" and line and line.startswith("What do I know about "):
                name = line.removeprefix("What do I know about ").rstrip("?")
                npc = next(x for x in met if st.entities[x].name == name)
                p, c = _probe(d, pc, npc, name, line)
                if c is not None:
                    rec_c.append(c)
                if p is not None:
                    rec_p.append(p)
                r = d.last
            elif kind == "ask_twice" and line:
                n0 = len(learned)
                d.settle(d.call("submit", line))
                n1 = len(learned)
                r = d.settle(d.call("submit", line))
                first, again = learned[n0:n1], learned[n1:]
                for x in again:
                    x["kind"] = "repeat"  # the index answers it again: not a new ask (the sim's "repeat")
                if first and again and first[-1]["answers"] and again[-1]["answers"]:
                    twice[1] += 1
                    a0, a1 = first[-1]["answers"][0], again[-1]["answers"][0]
                    twice[0] += (a0[0], a0[3]) == (a1[0], a1[3])
            else:
                r = d.travel() if line is None else d.settle(d.call("submit", line))
            if fix_every and (i + 1) % fix_every == 0 and r.pause is None:  # a planted /fix report (spec 012)
                r = d.settle(d.call("dispute", FIX_REPORTS[(i // fix_every) % len(FIX_REPORTS)]))
        except Exception as e:  # noqa: BLE001 - an engine error is a finding: counted, and the run goes on
            errors.append(f"line {i + 1} ({kind}): {type(e).__name__}: {e}"[:160])
            streak += 1
            if streak >= 5:
                break  # five failures in a row: the game is stuck
            continue
        finally:
            for x in learned[n_learned:]:
                x.setdefault("kind", kind)
        streak = 0
        if r.turn_id:
            turn_at.setdefault(i + 1, r.turn_id)
        if r.fiction:
            deliveries.append(r.fiction)
        if r.phase == "ending":
            break
    store = d.game.store
    turns = [t.model_dump(mode="json") for t in (store.turn(tid) for tid in _turn_ids(store)) if t is not None]
    narrated, by = contradictions(turns)
    rows = store.model_calls()
    play = [(str(r["role"]), (r.get("request") or {}).get("packet") or "") for r in rows
            if str(r.get("turn_id") or "").startswith("turn.")]
    out = [f"## Scripted player (seed {seed}, {sum(kinds.values())} lines, {len(turns)} turns, {narrated} narrated)"]
    total = sum(by.values())
    out.append(f"- contradictions per 100 narrated turns: {100 * total / narrated if narrated else 0:.1f}"
               + (" (" + ", ".join(f"{k} {v}" for k, v in by.most_common()) + ")" if by else ""))
    out.append(dispute_lines(dispute_stats(store.state), narrated))
    out.append(f"- recall probes: {len(rec_c)} scored of {kinds['recall']}; precision {_mean(rec_p)}, "
               f"coverage {_mean(rec_c)}")
    loop = [f"- novelty-4 over the previous 10 deliveries: {novelty4(deliveries):.2f} ({len(deliveries)} deliveries)",
            narration_loop(turns)]
    if model == "offline":  # P6 (round 7, R7-I1 §6): the stub's canned prose, not a narration measure
        loop = [f"- [offline stub: plumbing only, NOT a narration measure; judge narration on live saves] "
                f"{x.removeprefix('- ')}" for x in loop]
    out += loop
    out += claim_log_lines(turns)
    out += ladder_lines(learned, (twice[0], twice[1]))
    out += dialogue_lines(turns)
    for mark in CHECKPOINTS:
        near = min(turn_at, key=lambda k: (abs(k - mark), k), default=None)  # an OOF line makes no turn
        tid = turn_at.get(near) if near is not None and abs(near - mark) <= 5 else None
        if tid:
            out.append(_fmt_views(f"line {mark}", view_tokens(store.model_calls(tid))))
    out.append("- cached-prefix share per role: " + ", ".join(f"{r} {s:.2f}" for r, s in prefix_share(play).items()))
    out.append(f"- engine errors: {len(errors)}" + "".join(f"\n  - {e}" for e in errors[:20]))
    d.game.close()
    return out


def _turn_ids(store: Any) -> list[str]:
    return [r[0] for r in store.conn.execute("SELECT turn_id FROM turns ORDER BY rowid")]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--mode", choices=("aged", "scripted", "both"), default="both")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--scenes", type=int, default=300)
    ap.add_argument("--lines", type=int, default=300)
    ap.add_argument("--fix-every", type=int, default=0, help="plant a /fix report every N scripted lines (spec 012)")
    ap.add_argument("--model", choices=("offline", "gemini", "claude-narration", "claude"), default="offline")
    ap.add_argument("--engine", choices=("pipeline", "dm-tools"), default="pipeline",
                    help="the play engine (spec 031: dm-tools is one DM model with tools)")
    ap.add_argument("--dm-secrets", choices=("hidden", "visible"), default="hidden",
                    help="dm-tools only: show the DM each present NPC's private case knowledge")
    ap.add_argument("--keep", type=Path, help="copy the run's stores to this folder (for diagnosis)")
    args = ap.parse_args(argv)
    global CONFIG
    CONFIG = GameConfig(offline=True, engine=args.engine, dm_secrets=args.dm_secrets)
    arm = "" if args.engine == "pipeline" else f"; engine: {args.engine}, secrets {args.dm_secrets}"
    out = [f"# Long-horizon harness (model: {args.model}{arm})", ""]
    with tempfile.TemporaryDirectory(prefix="longhorizon-") as tmp:
        if args.mode in ("aged", "both"):
            out += run_aged(args.seed, args.scenes, args.model, Path(tmp)) + [""]
        if args.mode in ("scripted", "both"):
            out += run_scripted(args.seed, args.lines, args.model, Path(tmp), args.fix_every)
        if args.keep:
            args.keep.mkdir(parents=True, exist_ok=True)
            for db in Path(tmp).glob("*.db"):
                shutil.copy2(db, args.keep / db.name)
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
