from dm import lore as notebook
from dm import names


def dm(text: str) -> dict:
    return {"kind": "dm", "text": text}


def test_capitalised_runs_that_dont_start_a_sentence_or_quotation() -> None:
    text = ('You kneel by the old man. "Odo," he rasps. "Odo Fenwick." He says the thief ran toward the Quarry Road, '
            "past Wat and Ned's stall. You cast Cure Wounds and roll Hit Dice; Mother Edda Thorne watches. GO AWAY, says "
            "a sign. I'll wait, says the Widow Harrow's boy.")
    assert names.phrases(text) == ["Fenwick", "Quarry Road", "Wat", "Ned", "Mother Edda Thorne", "Widow Harrow"]


def test_unknown_until_in_an_entry_or_dismissed() -> None:
    lore = notebook.new()
    t = [dm("He gives his name as Odo Fenwick, and points toward the Quarry Road. Kaeris nods.")]
    assert names.unknown(lore, t, ("Kaeris Dawnvow",)) == ["Odo Fenwick", "Quarry Road"]
    lore, _ = notebook.write(lore, {"create": "the old caretaker", "kind": "person", "description": "x"}, 1)
    lore, _ = notebook.write(lore, {"entry": "the old caretaker", "rename": "Odo Fenwick"}, 1)
    t.append(dm("Later, Odo coughs."))
    assert names.unknown(lore, t, ("Kaeris Dawnvow",)) == ["Quarry Road"]
    t.append({"kind": "call", "tool": "dismiss_name", "input": {"names": ["quarry road"]}, "result": "", "error": False})
    assert names.unknown(lore, t) == [] and names.warning(lore, t) == ""


def test_the_warning_lists_the_names() -> None:
    w = names.warning(notebook.new(), [dm("She looks at the Long House.")])
    assert w.startswith("[Names not in your notebook] ") and "Long House" in w and "dismiss_name" in w


def test_character_creation_is_left_out() -> None:
    t = [dm("Pick a race: Half-Elves are good Bards."), {"kind": "call", "tool": "finish_character", "input": {}},
         dm("You walk into Millbrook at dawn.")]
    assert names.unknown(notebook.new(), t) == ["Millbrook"]
