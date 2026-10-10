"""Hook terms (11.5.6, PR-11-5 step 1, 12.16.16; DL-12-109, DL-12-135; specs 025 and 029, T2): when a hook is made, code
decides what the mechanics and the threads read, and writes it as unsealed knowledge of the people who would know.

    write_terms(tx, rec)            # at the seed's store write (and for a case built in play): terms, facts, people
    hook_terms(state)               # {thread id or case id: terms} as written (meta `world.hook_terms`)
    kinds()                         # every lead and incident kind the game's data has, by family (the tests walk it)
    write_injection(ctx, ...)       # a lead injected in play (`tbl.lead_injection`): the same terms, by form
    write_creation(tx, pc)          # the PC's creation hooks (02.9.7), bound to their bond people

**Every kind** [revision: R2-L; DL-12-135]: the terms are decided for every lead and incident kind the data has, not
only the jobs and notices. Kind by kind they are **who** (people by id: bound, cast or created), **what** (the act or
event, as data), **where** (a place), the **words** of any document or message (a `text` fact on a document entity
made at the same time, so reading it delivers them) and the **pay** where one is offered (a job fee from
`economy.yaml#job_fees` by the job's band; economy AI-6: coin never from narration). The entries are
`world_seed.yaml#terms`, one per kind, filled here from ids and names. A term the case seals (a node's answer: the
offer's issuer, the challenger's name) is never written. Everything else about the hook is improvised in character and
stored as testimony (PR-12-12).

The terms are computed from the region record only, on streams keyed by the seed and the hook, so a load writes the
same terms every time and the seed record itself (draw-for-draw with `12-world-seed.py`) is untouched.
"""

from __future__ import annotations

import re
from typing import Any

from engine import ids
from engine.gen import _data
from engine.gen._seed_lib import Rec, data, slug
from engine.gen._seed_packs import cast_pick, in_haven, keyed, pack_data, walk_on
from engine.store.events import EntityRecord, Event
from engine.world.common import fact, meta

TERMS = "world.hook_terms"  # meta {hook id: terms}
CARD = "topic.hook.terms"  # the knowers' fact predicate (the speaker card shows a `topic.` fact's value as is)
BOUNTY_BAND = 1  # a reward for word of someone: the lowest job band (08.8.8)
FAMILIES = ("incident", "situation", "lead", "document", "lead_form", "rumor", "creation")


def terms_data() -> Rec:
    """`world_seed.yaml#terms`: one entry per kind."""
    return dict(_data.load("world_seed.yaml")["terms"])


def kinds() -> dict[str, list[str]]:
    """Every lead and incident kind the game's data has, by family, read from the tables themselves."""
    D = data()
    lead_tbl = next(t for t in _data.load("oracles.yaml")["tables"] if t["id"] == "tbl.lead_injection")
    return {"incident": [r["option"] for r in D.TAB["tbl.12.seed.inciting"]["results"]],
            "situation": [k.removeprefix("sit_t.") for k in D.SITT],
            "lead": ["hire"],
            "document": [r["option"] for r in pack_data().DOCT["results"]],
            "lead_form": [str(r["range"]) for r in lead_tbl["results"]],
            "rumor": list(terms_data()["rumor"]),
            "creation": creation_kinds()}


def creation_kinds() -> list[str]:
    """The creation-hook kinds (02.9.7): the prefixes the origins' `hooks` micro-format uses."""
    found: list[str] = []

    def walk(x: Any) -> None:
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "hooks" and isinstance(v, list):
                    found.extend(str(h).split(":", 1)[0] for h in v)
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    walk(_data.load("origins.yaml"))
    return sorted(set(found))


def job_fee(band: int) -> int:  # rule: 08.8.8
    """`economy.yaml#job_fees` for a challenge band (clamped to the table)."""
    rows = sorted(_data.load("economy.yaml")["job_fees"], key=lambda r: int(r["band"]))
    band = max(int(rows[0]["band"]), min(int(rows[-1]["band"]), band))
    return int(next(r["fee"] for r in rows if int(r["band"]) == band))


def hook_terms(state: Any) -> dict[str, Rec]:
    return dict(state.meta.get(TERMS) or {})


def _a(noun: str) -> str:
    return ("an " if noun[:1].lower() in "aeiou" else "a ") + noun


def _plain(name: str) -> str:
    """A faction's name inside a sentence ("the kin of Swancrag")."""
    return name[0].lower() + name[1:] if name.startswith("The ") else name


# ------------------------------------------------------------------------------------------- the builder


class _Tok(dict[str, str]):
    """The tokens one hook's templates may use; a holder (`watch`, `clerk`, `witness`, ...) is found, or made, the
    first time a template names it, and recorded in `who` (token -> entity id)."""

    def __init__(self, b: _Builder, hook: str, place: str, base: dict[str, str]):
        super().__init__(base)
        self.b, self.hook, self.place = b, hook, place
        self.who: dict[str, str] = {}
        self.reserved: set[str] = set()

    def __missing__(self, key: str) -> str:
        n = self.b.resolve(key, self)
        if n is None:
            raise KeyError(key)
        self[key], self.who[key] = n["name"], n["id"]
        return self[key]

    def fill(self, template: str) -> str:
        return re.sub(r"\{(\w+)\}", lambda m: self[m.group(1)], template)


class _Builder:
    """Terms over one region record (the seed's, or `case.world_rec` for a case built in play)."""

    def __init__(self, rec: Rec, seed: Any, scene_place: str | None = None):
        self.rec, self.seed, self.T = rec, seed, terms_data()
        self.view: Rec = {**rec, "walk_ons": []}  # new walk-ons land here; the seed record is never touched
        self.P = {p["id"]: p for p in rec["places"]}
        self.hav = rec["region"]["haven"]
        self.locals = sorted((n for n in rec["npcs"] if in_haven(rec, n["home"]) and n.get("depth") != "walk_on"),
                             key=lambda n: n["id"])
        self.F = {f["id"]: f for f in rec["factions"]["instances"]}
        self.scene_place = scene_place
        self.docs: list[Rec] = []

    # ---- places and names
    def building(self, kind: str) -> str:
        want = {"temple": ("temple", "shrine")}.get(kind, (kind,))
        return next((f"{self.hav}.{k}" for k in want if f"{self.hav}.{k}" in self.P), self.hav)

    def pname(self, pid: str | None) -> str:
        return str(self.P[pid]["name"]) if pid in self.P else str(self.P[self.hav]["name"])

    def place(self, key: str, *, start: str | None = None, area: str | None = None, site: str | None = None) -> str:
        if key == "start":
            return start or self.start()
        if key == "scene":
            return self.scene_place or self.start()
        return {"haven": self.hav, "area": area or self.hav, "site": site or self.hav}.get(key) or self.building(key)

    def start(self) -> str:
        return str(((self.rec.get("opening") or {}).get("start") or {}).get("place") or self.hav)

    def fname(self, fid: str | None) -> str:
        return _plain(str(self.F[fid]["name"])) if fid in self.F else "the faction"

    def base(self) -> dict[str, str]:
        cal = str((self.rec.get("calendar") or {}).get("opening_date") or "the quarter day")
        rul = next((f for f in self.F.values() if str(f["id"]).endswith(".rulers")), None)
        links = self.P[self.hav].get("links") or []
        link = keyed(self.seed, "terms", "road").pick(links) if links else None
        keepers = self.rec.get("keepers") or [{"name": "the keeper"}]
        return {"haven": self.pname(self.hav), "date": cal.split(",")[0].strip(), "year": cal.split(",")[-1].strip(),
                "when": "last night", "keeper": str(keepers[0]["name"]).split(",")[0],
                "issuer": _plain(str(rul["name"])) if rul else "the rulers",
                "route": f"{link['route_kind']} to {self.pname(link['to'])}" if link else "road out of town",
                "route_to": self.pname(link["to"]) if link else "the next town",
                "opposition": next((self.fname(f) for f in self.F if str(f).endswith(".threat")), "the enemy")}

    # ---- people
    def resolve(self, key: str, tok: _Tok) -> Rec | None:
        holders = self.T["holders"]
        if key in holders:
            return self._holder(holders[key], key, tok)
        if key == "witness":
            return self._witness(tok)
        if key in ("contact_old", "seeker", "bond"):
            return self._local(tok, key, lambda n: 1)
        return None

    def _used(self, tok: _Tok) -> set[str]:
        return {*tok.who.values()}

    def _holder(self, spec: Rec, key: str, tok: _Tok) -> Rec:
        """The cast person of that trade at that place (the case's own reporter may be the watch), else a walk-on."""
        home = tok.place if spec["at"] == "area" else self.building(spec["at"])
        used = {v for k, v in tok.who.items() if k not in ("reporter", "witness")}
        cands = [n for n in self.locals if n["id"] not in used
                 and any(w in str(n["role"]).lower() for w in spec["roles"])]
        pick = next((n for n in cands if n["home"] == home), None)
        return pick or walk_on(self.view, self.seed, f"{slug(tok.hook)}_{key}", spec["role"], home)

    def _witness(self, tok: _Tok) -> Rec:
        used = self._used(tok)
        pool = [n for n in self.locals if n["id"] not in used]
        d = keyed(self.seed, "terms", tok.hook, "witness")
        pick = cast_pick(d, pool, lambda n: 3 if n["home"] == tok.place else 1)
        return pick or walk_on(self.view, self.seed, f"{slug(tok.hook)}_witness", "witness", tok.place)

    def _local(self, tok: _Tok, key: str, weight: Any) -> Rec:
        pool = [n for n in self.locals if n["id"] not in self._used(tok)]
        pick = cast_pick(keyed(self.seed, "terms", tok.hook, key), pool, weight)
        return pick or walk_on(self.view, self.seed, f"{slug(tok.hook)}_{key}", "local", tok.place)

    # ---- one entry
    def entry(self, hook: str, kind: str, family: str, entry: Rec, place: str, base: dict[str, str], *,
              reserved: dict[str, tuple[str, str]] | None = None, know: list[str] | None = None) -> Rec:
        """The terms of one hook from its data entry: fields, people made, a document made, and who knows."""
        tok = _Tok(self, hook, place, {**self.base(), **base, "place": self.pname(place)})
        for k, (rid, rname) in (reserved or {}).items():  # people the case already named: not made again
            tok[k], tok.who[k] = rname, rid
            tok.reserved.add(rid)
        d = keyed(self.seed, "terms", hook)
        for name, opts in (entry.get("pick") or {}).items():  # drawn in the data's order, on the hook's own stream
            tok[name] = d.pick(pack_data().DOCT["fields"]["reason"] if opts == "doc:reason" else opts)
        for token, role in (entry.get("people") or {}).items():
            n = walk_on(self.view, self.seed, f"{slug(hook)}_{token}", role, place)
            tok[token], tok.who[token] = n["name"], n["id"]
        doc: Rec | None = None
        dtext = ""
        if entry.get("doc"):
            spec = entry["doc"]
            dtext = re.sub(r"(^|[.!?:] )([a-z])", lambda m: m.group(1) + m.group(2).upper(), tok.fill(spec["text"]))
            at = self.place(spec["at"], start=place) if spec["at"] != "scene" else place
            doc = next((d for d in self.docs if d["name"] == spec["name"] and d["at"] == at), None)
            if doc is not None:  # one gate log, one road board: a second entry is written in the same document
                doc["text"] += " " + dtext
            else:
                doc = {"id": f"doc.{slug(hook)}_{slug(spec['name'])}", "kind": "document", "option": spec["kind"],
                       "name": spec["name"], "aliases": list(spec.get("aliases") or []), "text": dtext, "at": at,
                       "table": "terms"}
                self.docs.append(doc)
            tok["doc_text"] = dtext
        holders = [t for t in (entry.get("know") or []) if t not in ("reporter", "subject", "contact")]
        for t in holders:
            tok[t]  # noqa: B018 -- resolving a holder records who it is
        fields = [(k, tok.fill(str(v))) for k, v in (entry.get("fields") or {}).items()]
        who = dict(tok.who)
        knowers = list(dict.fromkeys([*(know or []), *(who[t] for t in entry.get("know") or [] if t in who)]))
        return {"hook": hook, "kind": kind, "family": family, "label": tok.fill(str(entry.get("label") or kind)),
                "where": place, "who": who, "fields": [list(f) for f in fields],
                "what": next((v for k, v in fields if k.startswith("what")), ""),
                "words": dtext if doc else None, "doc": doc["id"] if doc else None, "know": knowers,
                "pay": None, "away": [who[a] for a in entry.get("away") or [] if a in who]}

    # ---- the opening's hooks
    def all(self, threads: dict[str, str]) -> list[Rec]:
        out: list[Rec] = []
        out += self._incidents(threads)
        out += self._leads(threads)
        out += self._situations(threads)
        out += self._documents()
        out += self._rumors()
        return out

    def _incidents(self, threads: dict[str, str]) -> list[Rec]:
        out: list[Rec] = []
        rul = next((f for f in self.F.values() if str(f["id"]).endswith(".rulers")), None)
        for c in self.rec.get("seed_cases") or []:
            n1 = c["nodes"][0]
            reporter = next(p["holder"] for p in n1["placements"] if p["access"] == "core")
            witness = next((p["holder"] for p in n1["placements"] if p["holder_kind"] == "person"
                            and p["holder"] != reporter), None)
            notice = next((p["holder"] for p in n1["placements"] if p["holder_kind"] == "document"), None)
            hook = threads.get("lead.1") if c["trigger"] == "incident" else c["id"]
            hook = hook or c["id"]
            kind, sub = c["option"], c["solution"]["subject"]
            ent = self.T["incident"][kind]
            place = str(c["opening_place"])
            known = {n["id"]: n for n in [*self.rec["npcs"], *(self.rec.get("walk_ons") or [])]}
            base = {"reporter": str(known[reporter]["name"]) if reporter in known else "a local",
                    "subject_label": str((ent.get("stage") or {}).get("label") or "the one concerned"),
                    "subject_role": str(known.get(sub["id"], {}).get("role") or "person"),
                    "subject_a": _a(str(known.get(sub["id"], {}).get("role") or "person")),
                    "last_seen": self.pname(next((p["at"] for p in n1["placements"] if p["holder"] == witness
                                                  and p.get("at")), place))}
            reserved = {"reporter": (reporter, base["reporter"])}
            if witness:
                reserved["witness"] = (witness, str(known[witness]["name"]) if witness in known else "a local")
            t = self.entry(hook, kind, "incident", ent, place, base, reserved=reserved,
                           know=[reporter, *(witness_k for witness_k in [witness] if witness_k)])
            t |= {"case": c["id"], "reporter": reporter, "contact": reporter, "issuer": None, "people": [],
                  "notice": notice}
            if "subject" in (ent.get("know") or []) and sub["id"] in known:
                t["know"] = list(dict.fromkeys([*t["know"], sub["id"]]))
            if ent.get("stage"):
                t["stage"] = {"subject": sub["id"], "label": base["subject_label"],
                              "dead": bool(ent["stage"].get("dead"))}
                if t["stage"]["dead"]:  # the rider is a body on stage (an entity, dead), not a person to invent
                    rider = walk_on(self.view, self.seed, f"{slug(hook)}_rider", "rider", place)
                    rider["exists"] = "dead"
                    t["who"]["rider"] = t["stage"]["actor"] = rider["id"]
            if kind == "offer":  # the issuer is the case's sealed subject: never a term
                t |= self._job(hook, c["solution"]["leads_to"], None)
            elif kind == "missing":  # the bounty notice: its reward is the job fee of the lowest band
                t |= {"pay": job_fee(BOUNTY_BAND), "band": BOUNTY_BAND, "issuer": rul["id"] if rul else None}
            elif kind == "refugees":  # the refugees exist: a group at the place they arrived (12.14.13 T1a)
                t |= {"group": "the refugees", "at": c["opening_place"]}
            out.append(t)
        return out

    def _leads(self, threads: dict[str, str]) -> list[Rec]:
        out: list[Rec] = []
        docs = {d["id"]: d for d in self.rec.get("documents") or []}
        for i, ld in enumerate((self.rec.get("opening") or {}).get("leads") or []):
            fac = next((f for f in self.F.values() if ld["points_to"] == (f.get("goal") or {}).get("clock")), None)
            if fac is None or not ld.get("document"):
                continue  # only the hire lead is a job; the situation lead's terms are its situation's
            members = [n for n in self.rec["npcs"] if fac["id"] in (n.get("member_of") or [])
                       and n.get("depth") != "walk_on"]
            head = next((n for n in members if str(n["role"]).startswith("head of")), None)
            hook = threads.get(f"lead.{i + 1:d}") or f"lead.{i + 1:d}"
            job = self._job(hook, None, docs.get(ld["document"]))
            ent = self.T["hire"]
            t = self.entry(hook, "hire", "lead", ent, self.hav, {
                "issuer_name": _plain(str(fac["name"])), "contact": str(head["name"]) if head else "the hiring agent"},
                know=[n["id"] for n in members])
            t |= {"issuer": fac["id"], "contact": head["id"] if head else None,
                  "people": [head["id"]] if head else [], "notice": ld["document"]} | job
            t["know"] = list(dict.fromkeys([*t["know"], *([head["id"]] if head else [])]))
            out.append(t)
        return out

    def _situations(self, threads: dict[str, str]) -> list[Rec]:
        out: list[Rec] = []
        leads = (self.rec.get("opening") or {}).get("leads") or []
        for s in self.rec.get("situations") or []:
            tmpl = str(s.get("template") or "")
            kind = tmpl.removeprefix("sit_t.")
            ent = self.T["situation"].get(kind)
            if ent is None:
                continue
            idx = next((i for i, ld in enumerate(leads) if ld["points_to"] == s["id"]
                        and not str(ld["lead"]).startswith("the incident itself")), None)
            hook = (threads.get(f"lead.{idx + 1:d}") if idx is not None else None) or threads.get(s["id"]) or s["id"]
            place = self.place(ent["at"], area=s.get("region"))
            base = {role: self.fname(fid) for role, fid in (s.get("roles") or {}).items()}
            base["missing_person"] = base.get("missing_person", "a household")
            t = self.entry(hook, kind, "situation", ent, place, base)
            t |= {"situation": s["id"], "reporter": None, "contact": None, "issuer": None, "people": []}
            out.append(t)
        return out

    def _documents(self) -> list[Rec]:
        """A seeded notice no case holds (warning, charter or bounty): its terms; a bounty's reward is a job fee."""
        out: list[Rec] = []
        in_case = {p["holder"] for c in self.rec.get("seed_cases") or [] for n in c["nodes"] for p in n["placements"]}
        rul = next((f for f in self.F.values() if str(f["id"]).endswith(".rulers")), None)
        for d in self.rec.get("documents") or []:
            if d["id"] in in_case or d.get("option") not in ("warning", "charter", "bounty"):
                continue
            ent = self.T["document"][d["option"]]
            capt = next((n for n in self.rec["npcs"] if n["home"] == self.hav + ".gate" and n.get("depth") != "walk_on"),
                        None)
            contact = next((n for n in self.rec["npcs"] if n["name"] in str(d.get("text") or "")), capt)
            site = next((p for p in self.rec["places"] if p["place_kind"] == "site" and p.get("ring") == 1), None)
            flds = _doc_fields(self.seed, d["id"].removeprefix("doc."))
            base = {"contact": str(contact["name"]) if contact else "the watch",
                    "contact_place": self.pname(contact["home"]) if contact else self.pname(self.hav),
                    "target": str(site["name"]) if site else "the road", "reason": flds.get("reason", ""),
                    "right": flds.get("right", ""), "reward": flds.get("reward", "")}
            t = self.entry(d["id"], d["option"], "document", ent, str(d.get("at") or self.hav), base,
                           know=[contact["id"]] if contact else [])
            t |= {"kind": d["option"], "issuer": rul["id"] if rul else None, "contact": contact["id"] if contact else None,
                  "people": [], "notice": d["id"], "reporter": None}
            if d["option"] == "bounty":
                t |= {"pay": job_fee(BOUNTY_BAND), "band": BOUNTY_BAND}
            out.append(t)
        return out

    def _rumors(self) -> list[Rec]:
        """Each seeded rumor a cast NPC carries (their `rumor` pack slot): what it says and where it points, held by
        those who carry it (11.6.4). Its truth stays sealed."""
        out: list[Rec] = []
        rows = {(t["id"], r["range"]): r for t in self.rec.get("rumor_tables") or [] for r in t["results"]}
        holders: dict[tuple[str, str], list[str]] = {}
        for n in self.rec["npcs"]:
            for k in n.get("knowledge") or []:
                if k.get("slot") == "rumor" and (k["rumor"]["table"], k["rumor"]["range"]) in rows:
                    holders.setdefault((k["rumor"]["table"], k["rumor"]["range"]), []).append(n["id"])
        for (tbl, rng), who in sorted(holders.items()):
            r = rows[(tbl, rng)]
            to = str(r.get("points_to") or "")
            kind = ("faction_goal" if to.startswith("clk.") else "situation" if to.startswith("sit.")
                    else "site" if to in self.P and self.P[to]["place_kind"] != "building" else "dream")
            target = self._target(to)
            hook = f"rumor.{slug(tbl.rsplit('.', 2)[-2])}_{rng}"
            t = self.entry(hook, kind, "rumor", self.T["rumor"][kind], self.hav, {"text": str(r["text"]).rstrip("."),
                                                                                  "target": target}, know=who)
            t |= {"reporter": None, "contact": None, "issuer": None, "people": [], "points_to": to}
            out.append(t)
        return out

    def _target(self, to: str) -> str:
        """Where a rumor's `points_to` is: a place's name, a situation's area, a faction goal's seat, a faith's shrine."""
        if to in self.P:
            return self.pname(to)
        sit = next((s for s in self.rec.get("situations") or [] if s["id"] == to), None)
        if sit:
            return self.pname(sit.get("region"))
        fac = next((f for f in self.F.values() if to == (f.get("goal") or {}).get("clock")), None)
        if fac:
            return f"{self.fname(fac['id'])}, seated at {self.pname(fac.get('seat'))}"
        return self.pname(self.building("temple"))

    # ---- the old job terms (spec 025)
    def _job(self, hook: str, target: Any, doc: Rec | None) -> Rec:
        dest = _destination(self.rec, self.seed, hook, target)
        band = int(dest.get("ring") or 1) if dest else 1
        return {"task": _task(self.rec, self.seed, hook, doc), "destination": dest["id"] if dest else None,
                "band": band, "pay": job_fee(band)}


def _doc_fields(seed: Any, tag: str) -> dict[str, str]:
    """The fields `make_document` drew for the document tagged `tag` (the same stream, so the same draws)."""
    d = keyed(seed, "doc", tag)
    return {k: d.pick(v) for k, v in pack_data().DOCT["fields"].items()}


def _sites(rec: Rec) -> list[Rec]:
    return [p for p in rec["places"] if p.get("place_kind") == "site" and p.get("ring") in (1, 2)]


def _destination(rec: Rec, seed: Any, hook: str, target: Any) -> Rec | None:
    """The job's place: the hook's target when it is a site, else a ring-1 or ring-2 site keyed by the hook."""
    P = {p["id"]: p for p in rec["places"]}
    if isinstance(target, str) and P.get(target, {}).get("place_kind") in ("site", "site_area", "area"):
        return P[target]
    sites = _sites(rec)
    return keyed(seed, "hook", hook, "destination").pick(sites) if sites else None


def _task(rec: Rec, seed: Any, hook: str, doc: Rec | None) -> str:
    """The work: the task the hook's notice already names, else one of the notice table's tasks, keyed."""
    tasks = list(pack_data().DOCT["fields"]["task"])
    named = next((t for t in tasks if doc and t in str(doc.get("text") or "")), None)
    return named or keyed(seed, "hook", hook, "task").pick(tasks)


def terms_for(rec: Rec, seed: Any, threads: dict[str, str]) -> list[Rec]:  # rule: 11.5.6
    """Every hook's terms from a region record (the seed's, or `case.world_rec` for a case built in play): the
    incident's case, the opening's hire lead and situations, a seeded notice, and the rumors the cast carry.
    `threads`: the seed's thread ids (`lead.1` -> `thr.lead_1`). Each term carries `new`: the people and documents
    it makes (written by `write_terms`)."""
    b = _Builder(rec, seed)
    out = b.all(threads)
    made = {n["id"]: n for n in b.view["walk_ons"]}
    docs = {d["id"]: d for d in b.docs}
    for t in out:
        t["new"] = {"people": [made[i] for i in t["who"].values() if i in made],
                    "docs": [docs[t["doc"]]] if t.get("doc") in docs else []}
    return out


def _name(rec: Rec, eid: Any) -> str:
    for coll in (rec["places"], rec["npcs"], rec["factions"]["instances"], rec.get("walk_ons") or []):
        hit = next((x for x in coll if x["id"] == eid), None)
        if hit:
            return str(hit["name"])
    return str(eid)


def _bits(rec: Rec, t: Rec) -> list[str]:
    flds = t.get("fields") or []
    named = any(k in ("posted by", "held by") for k, _ in flds)  # the entry already says who posted it
    bits = [f"{k}: {v}" for k, v in flds]
    bits += [f"work: {t['task']}" if t.get("task") else "",
             f"pay: {t['pay']:d} coins (a job fee)" if t.get("pay") else "",
             f"where: {_name(rec, t['destination'])}" if t.get("destination") else "",
             f"posted by: {_name(rec, t['issuer'])}" if t.get("issuer") and t["kind"] != "hire" and not named else "",
             f"where they are now: {_name(rec, t['at'])}" if t.get("at") else ""]
    return [b for b in bits if b]


def card_value(rec: Rec, t: Rec) -> str:  # rule: 12.16.16
    """The terms as one data line (fields, never a sentence to repeat)."""
    return f"{t.get('label') or t['kind']}: " + "; ".join(_bits(rec, t))


CARD_LINE = 150  # a knower's card cuts a line at 160 characters (packet._short): a term line stays inside it


def card_lines(rec: Rec, t: Rec) -> list[str]:  # rule: 12.16.16
    """The terms as the lines a knower's card shows, each inside `CARD_LINE` characters so no field is cut: the
    fields in order, packed greedily; a line after the first repeats the label's first words. A field longer than a
    line (a document's text, which reading delivers whole) is shortened at a word."""
    label = str(t.get("label") or t["kind"])
    more = label[:30].rstrip() + ": "
    out: list[str] = []
    cur: list[str] = []

    def prefix() -> str:
        return more if out else f"{label}: "

    for bit in _bits(rec, t):
        room = CARD_LINE - max(len(more), len(label) + 2)
        if len(bit) > room:
            bit = bit[: bit.rfind(" ", 0, room - 1)] + "…"
        if cur and len(prefix() + "; ".join([*cur, bit])) > CARD_LINE:
            out.append(prefix() + "; ".join(cur))
            cur = [bit]
        else:
            cur.append(bit)
    if cur:
        out.append(prefix() + "; ".join(cur))
    return out


def _commit(tx: Any, rec: Rec, new: list[Rec], source: str) -> None:  # rule: PR-11-5
    """Write terms: the people and documents they make, the refugees as a group, one data fact per card line that each
    knower knows, and meta `world.hook_terms`."""
    from engine.gen.case import write_documents, write_walk_ons

    st = tx.state
    have = hook_terms(st)
    for t in new:
        made = t.pop("new", None) or {"people": [], "docs": []}
        write_walk_ons(tx, made["people"], source=source, unplaced=t.get("away") or ())
        write_documents(tx, made["docs"], source=source)
        if t.get("group"):
            gid = ids.entity_id("npc", f"{slug(t['case'])} refugees", st.entities)
            tx.add(Event.of("entity_created", source=source, rule_id="12.14.13", entity=EntityRecord(
                id=gid, kind="npc", name=t["group"], visibility="background",
                data={"group": True, "role": "refugees", "name_known": False, "pronouns": "they/them",
                      "home": t["at"], "depth": "walk_on"})))
            if t["at"] in st.entities:
                tx.add(Event.of("position_set", source=source, rule_id="12.14.13", entity=gid, location=t["at"]))
            t["people"] = [gid]
        know = [k for k in t["know"] if k in st.entities]
        if not know or not t.get("fields"):
            continue
        for n, line in enumerate(card_lines(rec, t)):  # a line a card shows whole (CARD_LINE)
            ev = fact(tx, t["hook"] if t["hook"] in st.entities else "world", f"{CARD}.{slug(t['hook'])}"[:55] + f".{n}",
                      line, rule_id="11.5.6", source="generation", visibility="background", event_source=source)
            tx.add(ev)
            for k in know:
                tx.add(Event.of("knowledge_recorded", source=source, rule_id="11.5.6", knower=k,
                                fact_id=ev.payload.fact_id, how="told"))  # type: ignore[attr-defined]
    if new:
        tx.add(meta(TERMS, have | {t["hook"]: t for t in new}, "11.5.6", source))


def _seed_of(rec: Rec, st: Any) -> Any:
    seed = (rec.get("seed") or {}).get("seed") if isinstance(rec.get("seed"), dict) else None
    return seed if seed is not None else (st.meta.get("world.seed") or {}).get("seed")


def write_terms(tx: Any, rec: Rec, *, source: str = "seed") -> list[Rec]:  # rule: PR-11-5
    """PR-11-5 step 1: each hook's terms in meta `world.hook_terms`, one data fact per card line that each knower knows
    (`knowledge_recorded`), the people and documents the terms make, and the refugees as a group entity where they
    arrived. Hooks already written are kept."""
    st = tx.state
    have = hook_terms(st)
    new = [t for t in terms_for(rec, _seed_of(rec, st), dict(st.meta.get("world.threads") or {}))
           if t["hook"] not in have]
    _commit(tx, rec, new, source)
    return new


# ------------------------------------------------------------------------------------------- in play


def _form_row(roll: int | None, form: str) -> str | None:
    """The `lead_form` entry key of a `tbl.lead_injection` result: its roll, else the row whose words the fallback form
    repeats."""
    if roll is not None:
        return str(roll)
    rows = next(t for t in _data.load("oracles.yaml")["tables"] if t["id"] == "tbl.lead_injection")["results"]
    return next((str(r["range"]) for r in rows if str(r.get("result")) == form), None)


def write_injection(tx: Any, *, roll: int | None, form: str, thread: str | None, src: str | None,
                    source_text: str = "", source: str = "engine") -> Rec | None:  # rule: 12.8.2
    """A lead injected in play (PR-12-3, `tbl.lead_injection`): the form's terms, by form, like any other hook's: who
    brings, overhears or is found (a person made here if none fits), what, where the PC is, and the words of anything
    found (a letter, a token: a document made now). `thread`: the thread the lead belongs to; `source_text`: the
    matter in words (the thread's text, an omen, a want, a rumor), never a sealed clue's answer."""
    from engine.gen.case import world_rec

    st = tx.state
    key = _form_row(roll, form)
    entry = terms_data()["lead_form"].get(key or "")
    rec = world_rec(st)
    if entry is None or rec["region"]["haven"] not in {p["id"] for p in rec["places"]}:
        return None
    pc = next((i for i, e in st.entities.items() if e.kind == "pc"), None)
    place = st.positions[pc].location if pc in st.positions else None
    n = 1 + sum(1 for t in hook_terms(st).values() if t.get("family") == "lead_form")
    ent = st.entities.get(thread or "")
    matter = (source_text or (str(ent.data.get("text") or ent.name) if ent is not None else "") or "a matter at hand")
    matter = matter.rstrip(".")
    b = _Builder(rec, _seed_of(rec, st), scene_place=place)
    hook = f"inj.{n:d}"
    t = b.entry(hook, str(key), "lead_form", entry, b.place("scene"), {"matter": matter})
    t |= {"thread": thread, "reporter": None, "contact": None, "issuer": None, "people": []}
    made = {n["id"]: n for n in b.view["walk_ons"]}
    docs = {d["id"]: d for d in b.docs}
    t["new"] = {"people": [made[i] for i in t["who"].values() if i in made],
                "docs": [docs[t["doc"]]] if t.get("doc") in docs else []}
    _commit(tx, rec, [t], source)
    return t


def write_creation(tx: Any, pc: str, hooks: list[str], anchor: Any = None, *, source: str = "creation") -> list[Rec]:
    # rule: 02.9.7
    """The PC's creation hooks (`kind: text`, 02.9.7) get their terms like any hook (11.5.6): the text as data, the
    person it binds (the anchor bond for `npc`, else a cast person of the haven) and where. The people who would know
    hold them; with no one to bind, the hook is the PC's own note."""
    from engine.gen.case import world_rec

    st = tx.state
    rec = world_rec(st)
    if rec["region"]["haven"] not in {p["id"] for p in rec["places"]}:
        return []
    place = str(((st.meta.get("world.opening") or {}).get("start") or {}).get("place") or rec["region"]["haven"])
    b = _Builder(rec, _seed_of(rec, st), scene_place=place)
    out: list[Rec] = []
    for i, h in enumerate(hooks):
        kind, _, text = str(h).partition(":")
        entry = terms_data()["creation"].get(kind.strip())
        if entry is None or f"hook.{slug(pc)}_{i:d}" in hook_terms(st):
            continue
        hook = f"hook.{slug(pc)}_{i:d}"
        bond = anchor.get("npc") if kind.strip() == "npc" and isinstance(anchor, dict) else None
        reserved = ({"bond": (bond, str(st.entities[bond].name))} if isinstance(bond, str) and bond in st.entities
                    else None)
        t = b.entry(hook, kind.strip(), "creation", entry, place, {"text": text.strip().rstrip(".")}, reserved=reserved)
        t |= {"reporter": None, "contact": None, "issuer": None, "people": [], "pc": pc}
        made = {n["id"]: n for n in b.view["walk_ons"]}
        t["new"] = {"people": [made[x] for x in t["who"].values() if x in made], "docs": []}
        _commit(tx, rec, [t], source)
        out.append(t)
    return out


__all__ = ["CARD", "FAMILIES", "TERMS", "card_lines", "card_value", "creation_kinds", "hook_terms", "job_fee",
           "kinds", "terms_data", "terms_for", "write_creation", "write_injection", "write_terms"]
