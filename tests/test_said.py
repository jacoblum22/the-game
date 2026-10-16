"""The DM_SAID trial: earlier sentences of the DM's own replies about names in the last turns."""
from dm import lore as notebook


def test_said_before() -> None:
    lore, _ = notebook.write(notebook.new(), {"create": "Hob", "kind": "person", "description": "the lamp-keeper"}, 1)
    t = [{"kind": "player", "text": "hi"}, {"kind": "dm", "text": "Hob sits with his unlit lantern. Rain falls."}]
    for i in range(4):
        t += [{"kind": "player", "text": f"line {i}"}, {"kind": "dm", "text": "Nothing."}]
    t += [{"kind": "player", "text": "I ask Hob for a light."}]
    assert notebook.said_before(lore, t, ["Hob"]) == ["Hob, turn 1: Hob sits with his unlit lantern."]
    assert notebook.said_before(lore, t[:4], ["Hob"]) == []  # too recent: still in the conversation
