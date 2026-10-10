"""Hook terms (11.5.6, PR-11-5 step 1, 12.16.16; DL-12-109; spec 025, T2): when a hook is made, code decides what the
mechanics and the threads read, and writes it as unsealed knowledge of the people who would know.

    write_terms(tx, rec)            # at the seed's store write (and for a case built in play): terms, facts, a group
    hook_terms(state)               # {thread id or case id: terms} as written (meta `world.hook_terms`)

A hook's terms: the **pay** (a job fee from `economy.yaml#job_fees` by the job's band; economy AI-6: coin never comes
from narration), the **destination** (a place), the **task**, the **issuer**, the **contact** and the **people**
involved. A term a case seals is never a term: the offer's issuer is the case's node-1 answer (who makes the offer),
so the reporter's card has the work, the pay and the place, and "who is paying?" goes to the clue judgment.
Everything else about the hook is improvised in character and stored as testimony (PR-12-12).

The terms are computed from the region record only, on streams keyed by the seed and the hook, so a load writes the
same terms every time and the seed record itself (draw-for-draw with `12-world-seed.py`) is untouched.
"""

from __future__ import annotations

from typing import Any

from engine import ids
from engine.gen import _data
from engine.gen._seed_lib import Rec, slug
from engine.gen._seed_packs import keyed, pack_data
from engine.store.events import EntityRecord, Event
from engine.world.common import fact, meta

TERMS = "world.hook_terms"  # meta {hook id: terms}
CARD = "topic.hook.terms"  # the knowers' fact predicate (the speaker card shows a `topic.` fact's value as is)
BOUNTY_BAND = 1  # a reward for word of someone: the lowest job band (08.8.8)


def job_fee(band: int) -> int:  # rule: 08.8.8
    """`economy.yaml#job_fees` for a challenge band (clamped to the table)."""
    rows = sorted(_data.load("economy.yaml")["job_fees"], key=lambda r: int(r["band"]))
    band = max(int(rows[0]["band"]), min(int(rows[-1]["band"]), band))
    return int(next(r["fee"] for r in rows if int(r["band"]) == band))


def hook_terms(state: Any) -> dict[str, Rec]:
    return dict(state.meta.get(TERMS) or {})


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


def _job(rec: Rec, seed: Any, hook: str, target: Any, doc: Rec | None) -> Rec:
    dest = _destination(rec, seed, hook, target)
    band = int(dest.get("ring") or 1) if dest else 1
    return {"task": _task(rec, seed, hook, doc), "destination": dest["id"] if dest else None, "band": band,
            "pay": job_fee(band)}


def terms_for(rec: Rec, seed: Any, threads: dict[str, str]) -> list[Rec]:  # rule: 11.5.6
    """Every hook's terms from a region record (the seed's, or `case.world_rec` for a case built in play): the
    incident's case (offer, missing, refugees carry terms; the other incidents carry their reporter only) and the
    opening's hire lead. `threads`: the seed's thread ids (`lead.1` -> `thr.lead_1`)."""
    out: list[Rec] = []
    docs = {d["id"]: d for d in rec.get("documents") or []}
    rul = next((f for f in rec["factions"]["instances"] if str(f["id"]).endswith(".rulers")), None)
    for c in rec.get("seed_cases") or []:
        n1 = c["nodes"][0]
        reporter = next(p["holder"] for p in n1["placements"] if p["access"] == "core")
        notice = next((p["holder"] for p in n1["placements"] if p["holder_kind"] == "document"), None)
        hook = threads.get("lead.1") if c["trigger"] == "incident" else c["id"]
        t: Rec = {"hook": hook or c["id"], "case": c["id"], "kind": c["option"], "reporter": reporter,
                  "contact": reporter, "issuer": None, "people": [], "know": [reporter]}
        if c["option"] == "offer":  # the issuer is the case's sealed subject: never a term
            t |= _job(rec, seed, t["hook"], c["solution"]["leads_to"], None)
        elif c["option"] == "missing":  # the bounty notice: its reward is the job fee of the lowest band
            t |= {"pay": job_fee(BOUNTY_BAND), "band": BOUNTY_BAND, "issuer": rul["id"] if rul else None,
                  "notice": notice}
        elif c["option"] == "refugees":  # the refugees exist: a group at the place they arrived (12.14.13 T1a)
            t |= {"group": "the refugees", "at": c["opening_place"]}
        out.append(t)
    in_case = {p["holder"] for c in rec.get("seed_cases") or [] for n in c["nodes"] for p in n["placements"]}
    for d in docs.values():  # a seeded bounty notice no case holds: its reward is a job fee, its contact knows it
        if d.get("option") != "bounty" or d["id"] in in_case:
            continue
        contact = next((n for n in rec["npcs"] if n["name"] in str(d.get("text") or "")), None)
        out.append({"hook": d["id"], "kind": "bounty", "issuer": rul["id"] if rul else None,
                    "contact": contact["id"] if contact else None, "people": [], "notice": d["id"],
                    "know": [contact["id"]] if contact else [], "pay": job_fee(BOUNTY_BAND), "band": BOUNTY_BAND})
    for i, ld in enumerate((rec.get("opening") or {}).get("leads") or []):
        fac = next((f for f in rec["factions"]["instances"] if ld["points_to"] == (f.get("goal") or {}).get("clock")),
                   None)
        if fac is None or not ld.get("document"):
            continue  # only the hire lead is a job; the situation lead's place is its thread's `points_to`
        members = [n for n in rec["npcs"] if fac["id"] in (n.get("member_of") or []) and n.get("depth") != "walk_on"]
        head = next((n for n in members if str(n["role"]).startswith("head of")), None)
        hook = threads.get(f"lead.{i + 1:d}") or f"lead.{i + 1:d}"
        t = {"hook": hook, "kind": "hire", "issuer": fac["id"], "contact": head["id"] if head else None,
             "people": [head["id"]] if head else [], "know": [n["id"] for n in members], "notice": ld["document"]}
        out.append(t | _job(rec, seed, hook, None, docs.get(ld["document"])))
    return out


def _name(rec: Rec, eid: Any) -> str:
    for coll in (rec["places"], rec["npcs"], rec["factions"]["instances"], rec.get("walk_ons") or []):
        hit = next((x for x in coll if x["id"] == eid), None)
        if hit:
            return str(hit["name"])
    return str(eid)


def card_value(rec: Rec, t: Rec) -> str:  # rule: 12.16.16
    """The terms as one data line for the knowers' cards (fields, never a sentence to repeat)."""
    label = {"offer": "the offer of work", "missing": "the reward for word of the missing",
             "bounty": "the bounty notice's reward",
             "refugees": "the refugees who came in", "hire": f"the hiring by {_name(rec, t.get('issuer'))}"}
    bits = [f"work: {t['task']}" if t.get("task") else "",
            f"pay: {t['pay']:d} coins (a job fee)" if t.get("pay") else "",
            f"where: {_name(rec, t['destination'])}" if t.get("destination") else "",
            f"posted by: {_name(rec, t['issuer'])}" if t.get("issuer") and t["kind"] != "hire" else "",
            f"ask for: {_name(rec, t['contact'])}" if t.get("contact") and t["kind"] == "hire" else "",
            f"where they are now: {_name(rec, t['at'])}" if t.get("at") else ""]
    return f"{label.get(t['kind'], t['kind'])}: " + "; ".join(b for b in bits if b)


def write_terms(tx: Any, rec: Rec, *, source: str = "seed") -> list[Rec]:  # rule: PR-11-5
    """PR-11-5 step 1: each hook's terms in meta `world.hook_terms`, one data fact per hook that each knower knows
    (`knowledge_recorded`), and the refugees as a group entity where they arrived. Hooks already written are kept."""
    st = tx.state
    seed = (rec.get("seed") or {}).get("seed") if isinstance(rec.get("seed"), dict) else None
    seed = seed if seed is not None else (st.meta.get("world.seed") or {}).get("seed")
    have = hook_terms(st)
    new = [t for t in terms_for(rec, seed, dict(st.meta.get("world.threads") or {})) if t["hook"] not in have]
    for t in new:
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
        if not know or not any(t.get(k) for k in ("pay", "destination", "at")):
            continue
        ev = fact(tx, t["hook"] if t["hook"] in st.entities else "world", f"{CARD}.{slug(t['hook'])}"[:60],
                  card_value(rec, t), rule_id="11.5.6", source="generation", visibility="background",
                  event_source=source)
        tx.add(ev)
        for k in know:
            tx.add(Event.of("knowledge_recorded", source=source, rule_id="11.5.6", knower=k,
                            fact_id=ev.payload.fact_id, how="told"))  # type: ignore[attr-defined]
    if new:
        tx.add(meta(TERMS, have | {t["hook"]: t for t in new}, "11.5.6", source))
    return new


__all__ = ["CARD", "TERMS", "card_value", "hook_terms", "job_fee", "terms_for", "write_terms"]
