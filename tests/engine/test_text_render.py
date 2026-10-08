"""B P4: the typed renderer (engine/text/render.py). A golden list of rendered sentences (irregular verbs, "you" vs
the third person, negation, unnamed NPCs), and a sweep that the old fallback garbles never come back."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from engine import ids
from engine.audit.fallback import fact_sentence, plain_fallback
from engine.dm.adjudication import AdjudicationRecord, BeatEntry, CostEntry, OracleEntry, PositionEntry
from engine.store.events import EntityRecord, Event
from engine.text.render import BEAT_VERBS, VERBS, clause, degree_words, forms, np, relation, sentence
from tests.fixtures.game import new_store

N = {"pc.wren": "Wren", "npc.tam": "Tam", "npc.driver": "the wagon driver", "npc.ferry": "ferryman"}

GOLDEN = [  # (rendered, expected)
    (clause("pc.wren", "be", "inside", names=N, pc="pc.wren"), "you are inside"),
    (clause("npc.tam", "be", "inside", names=N, pc="pc.wren"), "Tam is inside"),
    (clause("pc.wren", "be", "inside", neg=True, names=N, pc="pc.wren"), "you are not inside"),
    (clause("npc.tam", "be", "inside", neg=True, tense="past", names=N), "Tam was not inside"),
    (clause("pc.wren", "be", "inside", tense="past", names=N, pc="pc.wren"), "you were inside"),
    (clause("npc.tam", "hold", "the lamp", names=N), "Tam holds the lamp"),
    (clause("npc.tam", "hold", "the lamp", tense="past", names=N), "Tam held the lamp"),
    (clause("npc.tam", "hold", "the lamp", neg=True, tense="past", names=N), "Tam did not hold the lamp"),
    (clause("pc.wren", "hold", "the lamp", names=N, pc="pc.wren"), "you hold the lamp"),
    (clause("npc.tam", "have", "a knife", names=N), "Tam has a knife"),
    (clause("pc.wren", "have", "a knife", neg=True, names=N, pc="pc.wren"), "you do not have a knife"),
    (clause("npc.tam", "carry", "the pack", names=N), "Tam carries the pack"),
    (clause("npc.tam", "watch", "the door", names=N), "Tam watches the door"),
    (clause("npc.tam", "go", names=N), "Tam goes"),
    (clause("npc.tam", "try", names=N), "Tam tries"),
    (clause("npc.tam", "see", "you", tense="past", names=N), "Tam saw you"),
    (clause("npc.tam", "strike at", "you", names=N), "Tam strikes at you"),
    (clause("npc.tam", "can", "see the gate", neg=True, names=N), "Tam cannot see the gate"),
    (clause("pc.wren", "would", "know", tense="past", names=N, pc="pc.wren"), "you would know"),
    (clause("npc.driver", "speak to", "you", names=N), "the wagon driver speaks to you"),  # unnamed: by role
    (clause("npc.ferry", "wait", names=N), "the ferryman waits"),
    (clause("npc.ghost", "wait", names=N), "someone waits"),  # an id with no name is never printed
    (clause("the guards", "bar", "the gate", plural=True), "the guards bar the gate"),
    (np("owl"), "an owl"), (np("unicorn"), "a unicorn"), (np("hour"), "an hour"), (np("lantern"), "a lantern"),
    (np("wolf", 3), "three wolves"), (np("knife", 2), "two knives"), (np("rusty key", 20), "many rusty keys"),
    (np("man", 2, definite=True), "the men"), (np("box", 4), "four boxes"), (np("ferry", 2), "two ferries"),
    (relation("the cart", "held_by", "Tam"), "the cart is held by Tam"),
    (relation("the bill", "location", "within Cornburn"), "the bill is within Cornburn"),
    (relation("the bill", "location", "the mill"), "the bill is at the mill"),
    (relation("the shape", "kind", "owl"), "the shape is an owl"),
    (relation("the bill", "text", "the Wolves are hiring"), "the bill reads: the Wolves are hiring"),
    (relation("Betey", "was_last_seen_at", "the mill"), "Betey was last seen at the mill"),
    (relation("Tam", "knows_the_old_enemy_by_name", neg=True), "Tam does not know the old enemy by name"),
    (relation("the letter", "addressed_to", "Tobett"), "the letter is addressed to Tobett"),
    (relation("Edda", "answered", "your question"), "Edda answered your question"),
    (relation("the houses", "have", "shuttered windows"), "the houses have shuttered windows"),
    (relation("the cart", "colour", "red"), "the cart's colour: red"),
    (relation("Tam", "fingers_ink_stained"), ""),  # a noun head: never guessed into a verb
    (relation("the door", "open_or_shut"), ""),  # the question's options, not a statement
    (relation("Calbert", "notices_the_pc_coming_does_not"), ""),
    (degree_words("critical_failure"), "it goes badly"),
    (degree_words("success", success_at_cost=True), "it works, at a cost"),
    (degree_words(None), ""),
    (sentence("it works"), "It works."), (sentence('you say, "go"'), 'You say, "go"'),
]


@pytest.mark.parametrize(("got", "want"), GOLDEN, ids=[w or "(empty)" for _, w in GOLDEN])
def test_golden(got: str, want: str) -> None:
    assert got == want


def test_the_verb_list_is_closed() -> None:
    for with_target, alone in BEAT_VERBS.values():
        for phrase in (with_target, alone):
            assert phrase.split(" ", 1)[0] in VERBS, phrase
    with pytest.raises(KeyError):
        clause("npc.tam", "frobnicate", names=N)
    assert forms("lie") == ("lies", "lay", "lain") and forms("occupy") == ("occupies", "occupied", "occupied")


# --- the old garbles (P-003, P-040, P-077, the "( intervals)" cost) never reach rendered text
GARBLE = re.compile(r"You try to [A-Z]|\bis at within\b|\(\s*intervals?\s*\)|\bdoes not (?:is|are|has)\b")
SHAPES = Path(__file__).resolve().parents[1] / "fixtures" / "fact_shapes.json"


def _fallbacks() -> list[str]:
    from engine.resolve.pipeline import _span_words

    names = {"pc.geria": "Geria Salier", "npc.gerella": "Gerella Vasois", "loc.gate": "the gate"}
    recs = [
        AdjudicationRecord(pc="pc.geria", beats=[
            BeatEntry(restatement="Gerella is pinned against the gatepost", actor="pc.geria", verb="verb.grapple",
                      targets=["npc.gerella"], degree="success", rolled=True),
            BeatEntry(restatement="Learn whether tracks lead away", actor="pc.geria", rolled=True,
                      degree="critical_failure", costs=[CostEntry(menu_id="cost.time", severity="S2",
                                                                  form=_span_words(6, "intervals"))]),
            BeatEntry(restatement="Tikka walks to the gate", actor="npc.gerella", verb="verb.move",
                      targets=["loc.gate"], positions=[PositionEntry(entity="npc.gerella", words="within the gate")])],
            oracle=[OracleEntry(question="Gerella knows where the hiring can be found?", answer="no"),
                    OracleEntry(question="Is anyone watching?", answer="yes")]),
        AdjudicationRecord(pc="pc.geria", beats=[BeatEntry(restatement=r, actor="pc.geria", gate=g, gate_words=w)
                                                 for r, g, w in (("Learn whether the gate is barred", "G1",
                                                                  "no roll: trivial"),
                                                                 ("Gerella names who is hiring", "G3", "beyond you"))]),
    ]
    return [plain_fallback(r, names=names).fiction for r in recs]


def test_no_old_garble_in_rendered_text(tmp_path: Path) -> None:
    shapes = json.loads(SHAPES.read_text(encoding="utf-8"))
    st = new_store(tmp_path)
    with st.transaction() as tx:
        made: set[str] = set()
        for s in shapes:
            for e in [s["subject"], *s["refs"]]:
                if e and e["id"] not in made:
                    made.add(e["id"])
                    tx.add(Event.of("entity_created", source="test", entity=EntityRecord(**e)))
        fids, seen = [], set()
        for s in shapes:
            subject = s["subject"]["id"] if s["subject"] else "world"
            if (subject, s["predicate"]) not in seen:
                seen.add((subject, s["predicate"]))
                fids.append(fid := tx.mint(ids.FACT))
                tx.add(Event.of("fact_set", {"source": "generation"}, fact_id=fid, subject=subject,
                                predicate=s["predicate"], value=s["value"], visibility="shown"))
    rendered = [fact_sentence(st.state, st.state.facts[f]) for f in fids] + _fallbacks()
    bad = [s for s in rendered if GARBLE.search(s)]
    assert len(rendered) > 700 and not bad, bad[:10]
    fb = _fallbacks()
    assert fb[0].startswith("You grapple with Gerella Vasois. It works. You make the attempt. It goes badly.")
    assert "Is anyone" not in fb[0] and "Gerella knows" not in fb[0]
    assert "Gerella Vasois moves toward the gate. Gerella Vasois is within the gate." in fb[0]
