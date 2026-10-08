"""The player-text sanitizer (engine/dm/player_text.py) and the terminal renderer's reflow and choice list
(play/render.py), on the exact strings a smoke game showed the player."""

from __future__ import annotations

import pytest

from engine.data.loader import load_rules
from engine.dm.player_text import clean, clean_response
from engine.dm.response import Choice, OofBlock, Pause, Response
from play.render import reflow, render_response, strip_listing

SEEN = [  # (what the smoke game showed, what the player should see)
    ("(a) the player answers every question from its options (or states a custom answer the DM classifies to "
     "the nearest option, 12.16.2)",
     "(a) the player answers every question from its options (or states a custom answer the DM classifies to "
     "the nearest option)"),
    ("Where the game begins, is working magic in the open lawful, licensed, or feared? (05.7.10 item 6)",
     "Where the game begins, is working magic in the open lawful, licensed, or feared?"),
    ("How common are spirits of place? (the Oracle's odds, 05.7.10 item 5)",
     "How common are spirits of place? (the Oracle's odds)"),
    ("Does someone who refuses magic (15's `magic` refusal) also refuse relics and enchanted things?",
     "Does someone who refuses magic also refuse relics and enchanted things?"),
    ("Do the four hybrid pairs chapter 04 leaves empty stay empty here (T-04-x: e.g. divine × primal)?",
     "Do the four hybrid pairs the rules leave empty stay empty here (e.g. divine × primal)?"),
    ("Besides the Common tongue, what is the land's second tongue? (02.2.2's creation default reads it)",
     "Besides the Common tongue, what is the land's second tongue?"),
    ("13 encounter tables built (PR-10-10) and audited (PR-10-8)", "13 encounter tables built and audited"),
    ("lead into gold, stone into bread); 08.6's crafting, not magic, changes what a thing is made of.",
     "lead into gold, stone into bread); crafting, not magic, changes what a thing is made of."),
    ("verb.grapple with might; on failure cost.gear none", "Grapple with might; on failure Gear none"),
    ("+1 edge on checks whose primary deed tag is at or under deed.influence.trade.",
     "+1 edge on checks whose primary deed tag is at or under Trade."),
    ("terrain: 1 terrain.plains.farmland, terrain.forest.woodland", "terrain: 1 Farmland, Woodland"),
    ("rulers: org.faith.shrine (rolled); fourth_faction: org.crown.civic (rolled)",
     "rulers: Shrine (rolled); fourth faction: Civic (rolled)"),
    ("keepers: kf.justice, kf.saint (rolled)", "keepers: justice, saint (rolled)"),
    ("any lic.* you hold", "any licences you hold"),
]


@pytest.mark.parametrize(("seen", "want"), SEEN)
def test_clean_strips_citations_and_names_ids(seen: str, want: str) -> None:
    rules = load_rules()
    assert clean(seen, rules) == want
    assert clean(want, rules) == want  # idempotent


def test_clean_leaves_numbers_spacing_and_plain_words_alone() -> None:
    rules = load_rules()
    for text in ("Success or better 50% · critical failure 5% · near miss 15% (need 11+ on the die).",
                 "  Good at (+2): blade, shield      Also trained: polearm", "Vitality 14/14 · Focus 4/4 · fate 1",
                 "e.g. the dock, at 12 coin"):
        assert clean(text, rules) == text


def test_clean_response_cleans_blocks_prompt_labels_but_not_play_fiction() -> None:
    rules = load_rules()
    resp = Response(phase="play", fiction="The verb.strike lands (01.8.1).",
                    oof_blocks=[OofBlock(kind="NOTE", text="[NOTE] uses verb.observe (01.8.1)")],
                    pause=Pause(kind="offer", prompt="cost.gear (PR-01-3)",
                                choices=[Choice(id="x", label="pay cost.drain")]))
    out = clean_response(resp, rules)
    assert out.fiction == resp.fiction  # the narrator's words are the screen's business, never touched here
    assert out.oof_blocks[0].text == "[NOTE] uses Observe"
    assert out.pause is not None and out.pause.prompt == "Gear" and out.pause.choices[0].label == "pay Drain"
    seed = clean_response(resp.model_copy(update={"phase": "creation"}), rules)
    assert seed.fiction == "The Strike lands."  # engine text before play


def test_reflow_joins_hard_wraps_but_keeps_items_fields_and_paragraphs() -> None:
    welcome = ("Welcome. This is an adventure told in words. You say what your character does, in your own words,\n"
               "and I tell you what happens.\n\nNext paragraph.")
    assert reflow(welcome) == ("Welcome. This is an adventure told in words. You say what your character does, in "
                               "your own words, and I tell you what happens.\n\nNext paragraph.")
    rules = ('[RULES] Say what you do in your own words. You can always ask "what are my options?" or "what do\n'
             '        I know?" and I will answer plainly.')
    assert reflow(rules).count("\n") == 0
    sheet = ("[SHEET] Bram (he/him) — Human\n  Carries: clothing, cloak, footwear, pack and bedroll, food, light, "
             "leather, dagger, sword\n  Wants: home")
    assert reflow(sheet) == sheet
    seed = ("  The Quiet Downs: a fallen realm: a kingdom broke two generations ago; its roads, keeps and heirs remain\n"
            "  climate highland; the trouble began 60 years ago\n  (a) keep it")
    assert reflow(seed) == seed


def test_choices_once_numbered_one_per_line() -> None:
    pause = Pause(kind="seed_step", prompt="Keep this?", choices=[Choice(id="keep", label="keep it"),
                                                                    Choice(id="veto", label="veto: roll it again")])
    block = "[SEED 6/14] The haven\n  in it: a smithy\n  (a) keep it\n  (b) veto: roll it again\n  If you move on: keep."
    assert strip_listing(block, pause) == "[SEED 6/14] The haven\n  in it: a smithy\n  If you move on: keep."
    out = render_response(Response(phase="seed", oof_blocks=[OofBlock(kind="SEED", text=block)], pause=pause), 80)
    assert out.endswith("Keep this?\n\n  1) keep it\n  2) veto: roll it again")
    assert "(a)" not in out
    # sub-questions that are not the choices become bullets, so letters never compete with the numbers
    c0 = Pause(kind="create_step", choices=[Choice(id="fast", label="Quick start"), Choice(id="full", label="workshop")])
    text = strip_listing("[CREATE 1/5] Before we begin\n  (a) What do you like?\n  (b) Anything to avoid?", c0)
    assert text == "[CREATE 1/5] Before we begin\n  - What do you like?\n  - Anything to avoid?"
    # an OFFER block's own inline numbered line is dropped; the menu line (12.15.2) is printed once
    offer = Pause(kind="offer", choices=[Choice(id="commit", label="Do it"), Choice(id="withdraw", label="Back off")])
    r = render_response(Response(phase="play", oof_blocks=[OofBlock(kind="OFFER", text="[OFFER] Climb.\n  1) Do it"
                                                                    "   2) Back off")], pause=offer), 80)
    assert "1) Do it" not in r and r.endswith("[OFFER] Climb.\n\n[Enter] Do it   [w] Back off   [?] Explain")


def test_the_pc_as_subject_takes_a_second_person_verb() -> None:
    """Playtest 20261007-212917: the OFFER read "you finds out who in Garford would talk to them"."""
    assert clean("the PC finds out who would talk") == "you find out who would talk"
    assert clean("The PC goes, and the PC tries; the PC has it") == "You go, and you try; you have it"
    assert clean("a stranger asks after the PC by name") == "a stranger asks after you by name"
