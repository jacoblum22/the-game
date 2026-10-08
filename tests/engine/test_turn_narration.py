"""T051: the narration pass (PR-12-1 T7–T12) with scripted bad drafts and the offline model on the dock fixture."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.dm.context import TurnContext
from engine.dm.narration import FRAME_NEXT
from engine.dm.schemas import prune
from engine.dm.turn import play_answer, play_turn
from engine.llm.base import Role
from engine.llm.offline import OfflineModel, ScriptedModel, enum_at
from engine.time.scheduler import TimeContext
from engine.world.scenes import mark_agenda_answered
from tests.engine.test_turn_adjudication import QUIET_WORLD, RISKY, SNEAK, beat, framer, reader, setup

GOOD_SCREEN = {"intent_acknowledged": True, "intent_substituted": False, "next_step_exists": True,
               "mechanics_in_fiction": [], "ends_on_prompt_or_one_pause": True}
LOOK = beat("look over the quay", "verb.observe", verbs=("look",))  # offline Framer: in plain view


def _decl(text: str, refs: list[str] | None = None, **kw: Any) -> dict[str, Any]:
    return {"text": text, "refs": refs or [], "about": [], "new": [], "atmosphere": False, **kw}


def narr(text: str, *, cite: bool = True) -> Any:
    """A scripted draft (spec 006: declared sentences). With `cite`, every sentence but a closing question cites
    every MUST line of the record, so coverage holds whatever the test cuts."""
    from engine.audit.declare import split

    def build(schema: Any, packet: Any) -> dict[str, Any]:
        import re

        must = re.findall(r"(?m)^- (R\d+) MUST:", packet.message) if cite else []
        return {"sentences": [_decl(s, [] if s.endswith("?") else list(must)) for s in split(text)]}
    return build


def _must(packet: Any) -> list[str]:
    import re

    return re.findall(r"(?m)^- (R\d+) MUST:", packet.message)


def rep(n: int | str, text: str, refs: list[str] | None = None) -> dict[str, Any]:
    """A scripted narrow repair (12.3.3): one replacement for sentence `n` ("add" adds one)."""
    return {"repairs": [{"replaces": str(n), **_decl(text, refs)}]}


def claim(n: int, subject: str, cls: str, predicate: str, value: str, change: bool = False) -> dict[str, Any]:
    return {"sentence": str(n), "subject": subject, "class": cls, "predicate": predicate, "value": value,
            "asserts_change": change, "pc_words_or_feelings": False}


def chk(*claims: dict[str, Any]) -> dict[str, Any]:
    return {"claims": list(claims), "screen": dict(GOOD_SCREEN)}


def look_model(**script: list[Any]) -> ScriptedModel:
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I look over the quay.", LOOK)],
                           Role.WORLD: [QUIET_WORLD]})
    for role, items in script.items():
        model.push(Role(role), *items)
    return model


def calls(model: ScriptedModel, role: Role) -> list[Any]:
    return [p for r, p in model.calls if r == role]


def test_contradiction_is_redrafted_to_the_store_value(tmp_path: Path) -> None:
    bad, good = "Tam Harlan, a woman, watches you. What do you do?", "Tam Harlan, a man, watches you. What do you do?"
    model = look_model(narrator=[narr(bad), lambda s, p: rep(0, good.split(". ")[0] + ".", _must(p))])
    dock, ctx = setup(tmp_path, model)
    model.push(Role.CHECKER, chk(claim(0, dock.ferryman, "identity", "gender", "woman")),
               chk(claim(0, dock.ferryman, "identity", "gender", "man")))
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == good and not out.response.flags.fallback_used
    repair = calls(model, Role.NARRATOR)[1].message
    assert "A REPAIR" in repair and "contradicted" in repair and "he/him" in repair
    assert "[0] Tam Harlan, a woman" in repair and "What do you do?" not in repair.split("A REPAIR")[1]
    assert [v["kind"] for v in out.turn_record.draft_versions] == ["draft", "repair"]
    assert out.turn_record.draft_versions[0]["verdicts"][0]["verdict"] == "contradicted"
    # the Checker never sees the Narrator's prompt or the record (FR-034)
    checker = calls(model, Role.CHECKER)[0]
    assert "Role: Narrator" not in checker.render() and "ADJUDICATION RECORD" not in checker.render()
    assert checker.message.startswith("[0] Tam Harlan") and "THE PLAYER'S MESSAGE" in checker.message
    assert f"{dock.pc}: Wren, you, your" in checker.view


def test_unsourced_change_is_cut(tmp_path: Path) -> None:
    draft = "Sela Vey draws her sword. The fog lies low on the water. What do you do?"
    model = look_model(narrator=[narr(draft)])
    dock, ctx = setup(tmp_path, model)
    model.push(Role.CHECKER, chk(claim(0, dock.watch, "possession", "draws", "her sword", change=True)))
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == "The fog lies low on the water. What do you do?"
    assert not out.response.flags.fallback_used and len(calls(model, Role.NARRATOR)) == 1  # a cut is code's
    kinds = [v["kind"] for v in out.turn_record.draft_versions]
    assert kinds == ["draft", "cut"] and out.turn_record.draft_versions[0]["verdicts"][0]["verdict"] == \
        "unsourced_change"
    assert not out.response.flags.review_flag  # cuts alone, every must-name line still cited: no ruling (12.3.3)


def test_two_failed_redrafts_fall_back_with_review_flag(tmp_path: Path) -> None:
    bad = "Tam Harlan, a woman, watches you. What do you do?"
    model = look_model(narrator=[narr(bad), rep(0, "Tam Harlan, a woman, watches you."),
                                 rep(0, "Tam Harlan, a woman, watches you.")])
    dock, ctx = setup(tmp_path, model)
    model.push(Role.CHECKER, *[chk(claim(0, dock.ferryman, "identity", "gender", "woman"))] * 3)
    out = play_turn(ctx, "I look over the quay.")
    r = out.response
    assert r.flags.fallback_used and r.flags.review_flag and out.turn_record.fallback_used
    assert "woman" not in r.fiction and r.fiction.endswith("What do you do?")
    assert [v["kind"] for v in out.turn_record.draft_versions] == ["draft", "repair", "repair", "fallback"]
    assert len(calls(model, Role.NARRATOR)) == 3
    rulings = [e.payload.ruling for e in dock.store.events(types=["ruling_logged"])  # type: ignore[attr-defined]
               if e.turn_id == out.turn_record.turn_id]
    assert any(x["kind"] == "rule_conflict" and x["review_flag"] for x in rulings)


def test_new_player_asking_for_options_and_the_scene_gets_both(tmp_path: Path) -> None:
    """Playtest 2026-10-07 (newcomer): "I'm new to this. What are my options? Can you describe what I see?" got
    "What do you do?" plus canned notes. Each part is answered: the help and the leads by their blocks, the scene
    by the fiction; past the redraft budget the checked sentences are kept and only the failing one is cut."""
    msg = "I'm new to this. What are my options? Can you describe what I see around me?"
    parts = [("OOF_QUESTION", "I'm new to this."), ("OOF_QUESTION", "What are my options?"),
             ("FICTION_QUESTION", "Can you describe what I see around me?")]
    data = {"parts": [{"text": t, "class": c, "question_kind": "none", "topic": None} for c, t in parts],
            "pending_answer": None, "fact_questions": [],
            "beats": [], "clarifying_question": None, "restatement": msg, "player_quantity": None}
    bad = "Fog lies low on the quay. Tam Harlan, a woman, mends a net. Do you go to the water or the town?"
    model = ScriptedModel({Role.READER: [lambda schema, packet: prune(data, schema)], Role.WORLD: [QUIET_WORLD],
                           Role.NARRATOR: [narr(bad)] + [rep(1, "Tam Harlan, a woman, mends a net.")] * 2})
    dock, ctx = setup(tmp_path, model)
    model.push(Role.CHECKER, chk(claim(1, dock.ferryman, "identity", "gender", "woman")),
               *[chk(claim(0, dock.ferryman, "identity", "gender", "woman"))] * 2)  # a repair checks [0] only
    out = play_turn(ctx, msg)
    r = out.response
    assert r.fiction == "Fog lies low on the quay. Do you go to the water or the town?", r.fiction
    assert not r.flags.fallback_used
    notes = [b.text for b in r.oof_blocks]
    assert any("[LEADS]" in t for t in notes) and any("You play by saying" in t for t in notes), notes
    assert not any("noted" in t for t in r.text().split("\n")), r.text()
    # the Checker screens the fiction against the in-fiction part only: the leads are not the narration's job
    checker = calls(model, Role.CHECKER)[0].message
    assert "describe what I see" in checker and "my options" not in checker


def test_offer_with_nothing_resolved_skips_the_narrator(tmp_path: Path) -> None:
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I slip past the watch.", SNEAK)],
                           Role.FRAMER: [framer(**RISKY)], Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I slip past the watch.")
    r = out.response
    assert r.pause is not None and r.pause.kind == "offer" and out.narration.skipped
    assert not calls(model, Role.NARRATOR) and not calls(model, Role.CHECKER)
    assert r.oof_blocks[-1].kind == "OFFER" and r.oof_blocks[-1].text.startswith("[OFFER]")
    assert "%" in r.oof_blocks[-1].text and not r.fiction  # the block restates the beat; no second copy
    assert out.turn_record.pause and out.turn_record.pause["kind"] == "offer"
    # the pick is narrated (the roll resolved something)
    model.push(Role.WORLD, QUIET_WORLD)
    ctx.rng.faces = [19]  # type: ignore[attr-defined]
    out2 = play_answer(ctx, "commit")
    assert out2.response.pause is None and calls(model, Role.NARRATOR) and out2.response.fiction


def test_scene_cut_frames_the_next_scene_next_turn(tmp_path: Path) -> None:
    model = look_model()
    dock, ctx = setup(tmp_path, model)
    with dock.store.transaction() as tx:
        mark_agenda_answered(TimeContext(tx, dock.rules, ctx.rng), "as_hoped")
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.scene_ended and dock.state.scene is None
    assert dock.state.meta.get(FRAME_NEXT, {}).get("reason") == "agenda_answered"

    def director(schema: dict[str, Any], packet: Any) -> dict[str, Any]:
        return prune({"cut_now": False, "next_scene": {
            "mode": "site", "place": dock.place, "agenda": "Who waits at the far end of the quay?",
            "hoped_answer": "none", "pillar": enum_at(schema, "next_scene", "pillar")[0], "challenge_type": None,
            "cast": [dock.ferryman]}, "push": "none", "lead": None}, schema)

    model.push(Role.DIRECTOR, director)
    model.push(Role.READER, reader("DECLARATION", "I walk to the far end.", LOOK))
    model.push(Role.WORLD, QUIET_WORLD)
    out2 = play_turn(ctx, "I walk to the far end.")
    st = dock.state
    assert st.scene is not None and st.scene.scene_id != dock.scene
    assert st.scene.agenda == "Who waits at the far end of the quay?" and not st.meta.get(FRAME_NEXT)
    assert out2.adjudication.record.scene.started == st.scene.scene_id
    assert "I walk to the far end." in calls(model, Role.DIRECTOR)[0].message
    assert "a new scene opens" in calls(model, Role.NARRATOR)[-1].message
    assert dock.store.rebuild() == dock.state


def test_the_players_cut_is_framed_this_turn(tmp_path: Path) -> None:
    def director(schema: dict[str, Any], packet: Any) -> dict[str, Any]:
        return prune({"cut_now": True, "next_scene": {
            "mode": "site", "place": dock.place, "agenda": "Does the ferryman take you across?",
            "hoped_answer": "yes", "pillar": enum_at(schema, "next_scene", "pillar")[0], "challenge_type": None,
            "cast": []}, "push": "none", "lead": None}, schema)

    model = ScriptedModel({Role.READER: [reader("DECLARATION", "Skip ahead to the ferry.", LOOK)],
                           Role.WORLD: [QUIET_WORLD], Role.DIRECTOR: [director]})
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "Skip ahead to the ferry.")
    rec = out.adjudication.record
    assert rec.scene.cut and rec.scene.ended == dock.scene and rec.scene.started == dock.state.scene.scene_id
    assert not out.response.scene_ended and not dock.state.meta.get(FRAME_NEXT)


def test_turn_record_is_complete(tmp_path: Path) -> None:
    dock, ctx = setup(tmp_path, OfflineModel())
    out = play_turn(ctx, "I look over the quay.")
    tr = dock.store.turn(out.turn_record.turn_id)
    assert tr is not None and tr == out.turn_record
    assert tr.input_verbatim == "I look over the quay." and tr.delivered_verbatim == out.response.text()
    assert tr.parts and tr.writes and tr.draft_versions and tr.model_calls
    assert set(tr.screen) == {"intent_acknowledged", "intent_substituted", "next_step_exists", "mechanics_in_fiction",
                              "ends_on_prompt_or_one_pause", "pc_agency_ok", "safety_ok"}
    roles = {c["role"] for c in dock.store.model_calls(tr.turn_id)}
    assert {"reader", "narrator", "checker"} <= roles
    assert all(cid in {c["call_id"] for c in dock.store.model_calls(tr.turn_id)} for cid in tr.model_calls)
    assert dock.store.rebuild() == dock.state


MESSAGES = [
    "I look over the quay.", "Is the ferry running tonight?", "\"Good evening,\" I say to the ferryman.",
    "I slip past the watch to the ferry.", "I wait in the shadows.", "I listen to the water.",
    "I ask the ferryman what the crossing costs.", "I check my pack.", "I climb onto the ferry.",
    "Who is the woman with the lantern?",
]


def test_fifty_offline_turns(tmp_path: Path) -> None:
    dock = setup(tmp_path, OfflineModel())[0]
    ctx = TurnContext(store=dock.store, rules=dock.rules, rng=dock.rng, model=OfflineModel())
    fallbacks = 0
    for i in range(50):
        pause = dock.state.open_pause()
        if pause is not None and pause.choices and i % 2:
            out = play_answer(ctx, pause.default_choice or pause.choices[0]["id"])
        else:
            out = play_turn(ctx, MESSAGES[i % len(MESSAGES)])
        r, tr = out.response, out.turn_record
        assert r.fiction or r.oof_blocks
        assert tr.delivered_verbatim == r.text()
        if r.flags.fallback_used:
            fallbacks += 1
        elif not out.narration.skipped:
            assert all(v["verdict"] == "supported" for v in tr.verdicts)
    rate = fallbacks / 50
    print(f"offline fallback rate: {rate:.2f} ({fallbacks}/50)")
    assert rate <= 0.5
    assert dock.store.rebuild() == dock.state


def test_dispute_and_rules_question_answer_out_of_fiction(tmp_path: Path) -> None:
    model = ScriptedModel({Role.READER: [reader("DISPUTE", "That's wrong, you never said that."),
                                         reader("OOF_QUESTION", "What does 12.2.6 say?")]})
    dock, ctx = setup(tmp_path, model)
    r = play_turn(ctx, "That's wrong, you never said that.").response
    assert any(b.kind == "NOTE" for b in r.oof_blocks) and r.pause is None
    r2 = play_turn(ctx, "What does 12.2.6 say?").response
    assert any("12.2.6" in b.text for b in r2.oof_blocks)


def test_freshness_lists_repeated_images_per_entity_and_recent_openings() -> None:  # 12.14.11 (P-030)
    from engine.dm.roles.narrator import freshness_lines

    d = ["Makul keeps his fingers on the ledger, eyes on you. The arrival stands still. What do you do?",
         "You ask again. Makul, fingers on the ledger, eyes on you, says nothing. What do you do?",
         "The lamp hisses. What do you do?"]
    lines = freshness_lines(d, ["Makul", "the arrival"], openings=2)
    text = "\n".join(lines)
    assert '"You ask again" / "The lamp hisses"' in text and "Makul keeps" not in lines[0]
    assert "- Makul: fingers on the ledger eyes on you" in text
    assert "what do you do" not in text.lower().replace("freshness", "")  # the hand-back is all stopwords
    assert freshness_lines(["One turn only. Nothing repeats here."], []) == ['FRESHNESS (12.14.11): do not open '
                                                                             'the way these recent turns opened: '
                                                                             '"One turn only"']


def test_freshness_lists_an_npcs_repeated_spoken_line() -> None:
    """Talker playtest 185715 inputs 21-26: Calbert opened every reply with "Mark me"; offer blocks never count."""
    from engine.dm.roles.narrator import freshness_lines

    d = ['Calbert frowns. "Mark me," he says. "I do not know."',
         'Calbert\'s jaw works. The lake slaps the posts. "Mark me," he says, low. "Leave it."',
         '"Mark me well," you say. Calbert waits.\n\n[OFFER] Evbert tries it\n        Success or better 85%']
    text = "\n".join(freshness_lines(d, ["Calbert Oakward", "lake"]))
    assert '- Calbert: "mark me"' in text and "success or better" not in text
    assert "- lake:" not in text.split("Lines these people")[1]  # a place never speaks; the PC's own line is not his


def test_the_narrator_is_told_what_it_already_used(tmp_path: Path) -> None:
    same = "Tam Harlan leans on his pole, rain beading on the brim. What do you do?"
    model = look_model(narrator=[narr(same), narr(same), narr(same)], checker=[chk(), chk(), chk()])
    model.push(Role.READER, reader("DECLARATION", "I look over the quay.", LOOK),
               reader("DECLARATION", "I look over the quay.", LOOK))
    model.push(Role.WORLD, QUIET_WORLD, QUIET_WORLD)
    dock, ctx = setup(tmp_path, model)
    for _ in range(3):
        play_turn(ctx, "I look over the quay.")
    msgs = [p.message for p in calls(model, Role.NARRATOR)]
    assert "Already used lately" not in msgs[0] and "Already used lately" not in msgs[1]
    assert "- Tam Harlan: leans on his pole rain beading on the brim" in msgs[2]


def test_redraft_and_screen_keep_the_bookkeeping_out_of_prose() -> None:  # P-045
    from engine.audit.screen import mechanics_in_fiction

    assert mechanics_in_fiction("It is unhurt, and the wound the record holds for it is there to be seen.")
    assert mechanics_in_fiction("Unhurt, as the store says.")
    assert not mechanics_in_fiction("You step into the store. The clerk keeps a record of every sale.")
    src = (Path(__file__).parents[2] / "engine" / "dm" / "narration.py").read_text(encoding="utf-8")
    assert "the store holds:" not in src


def test_two_beats_say_whose_result_and_redirect_they_are() -> None:
    """P-104 (playtest 20261007-202001 fighter, input 24): "[RESULT] ... success" then "[REDIRECT] ... Athletics"
    read as one contradicting the other. With two beats each block names its action; with one it does not."""
    from engine.dm.adjudication import AdjudicationRecord, BeatEntry
    from engine.dm.narration import turn_blocks

    items = [{"kind": "RESULT", "text": "[RESULT] d20 12 → 16 vs 15 · success", "beat": "Ask what was stolen"},
             {"kind": "REDIRECT", "text": "[REDIRECT] Not as tried: that needs Athletics.\n           - Look around",
              "beat": "Force the altar lid open (verb.force)"}]
    two = AdjudicationRecord(beats=[BeatEntry(restatement="Ask what was stolen"),
                                    BeatEntry(restatement="Force the altar lid open")])
    blocks, _ = turn_blocks(None, items, two, None)  # type: ignore[arg-type]
    assert [b.text.split("\n")[0] for b in blocks] == [
        "[RESULT] Ask what was stolen: d20 12 → 16 vs 15 · success",
        "[REDIRECT] Force the altar lid open: Not as tried: that needs Athletics."]
    one = AdjudicationRecord(beats=[BeatEntry(restatement="Ask what was stolen")])
    blocks, _ = turn_blocks(None, items[:1], one, None)  # type: ignore[arg-type]
    assert blocks[0].text == "[RESULT] d20 12 → 16 vs 15 · success"
