"""The shared Mourhold campaign for the synthetic tests (owner, 2026-10-13): Shae, a level-5 Fiend warlock, with Rhylla
and Elara as companions, built and checked by the game's own code."""
from pathlib import Path

from dm import create

HERE = Path(__file__).parent

SHAE = {"name": "Shaedryn Velaris", "race": "half-elf", "class": "warlock", "ability_method": "standard_array",
        "base_scores": {"STR": 8, "DEX": 14, "CON": 13, "INT": 12, "WIS": 10, "CHA": 15},
        "choices": {"race.ability_bonuses": ["b", "c"], "race.languages": ["Infernal"],
                    "trait.skill-versatility": ["Skill: Persuasion", "Skill: Perception"],
                    "class.proficiencies.1": ["Skill: Deception", "Skill: Intimidation"],
                    "class.equipment.1": ["a"], "class.equipment.2": ["a"], "class.equipment.3": ["a"],
                    "class.equipment.4": ["Dagger"], "background.languages": ["Celestial", "Sylvan"],
                    "background.equipment.1": ["Amulet"], "background.equipment.prayer": ["a"]},
        "cantrips": ["Eldritch Blast", "Minor Illusion"], "spells": ["Charm Person", "Hellish Rebuke"],
        "alignment": "Lawful Evil",
        "personality": {"traits": ["Charming and witty, drawn to beauty in all its forms: art, poetry, even violence.",
                                   "Uses charm as a tool, but her admiration is never insincere."],
                        "ideal": "Power. House Velaris will rise, and Mourhold with it, by her hand.",
                        "bond": "The Ascendant Circle: Elara, Rhylla, Galen, Eira and Koryth, bound to her across "
                                "lifetimes.",
                        "flaw": "Cold and ruthless the moment she is disrespected."},
        "appearance": "Average height, slender, silvery-pale skin, jet-black hair to mid-back with silver Velaris "
                      "pins, grey eyes flecked with silver; always gloved, over scars from forbidden magic."}

SHAE_LEVELS = [
    {"hp": "fixed", "invocations": ["Agonizing Blast", "Mask of Many Faces"], "spells": ["Command"]},
    {"hp": "fixed", "choices": {"feature.pact-boon": ["Pact of the Blade"]}, "spells": ["Suggestion"]},
    {"hp": "fixed", "asi": {"CHA": 2}, "cantrips": ["Prestidigitation"], "spells": ["Invisibility"]},
    {"hp": "fixed", "invocations": ["Devil's Sight"], "spells": ["Hypnotic Pattern"]},
]

RHYLLA = {"name": "Rhylla Greysong", "race": "human", "class": "rogue", "ability_method": "standard_array",
          "base_scores": {"STR": 10, "DEX": 15, "CON": 13, "INT": 12, "WIS": 14, "CHA": 8},
          "choices": {"race.languages": ["Elvish"],
                      "class.proficiencies.1": ["Skill: Stealth", "Skill: Perception", "Skill: Deception",
                                                "Skill: Intimidation"],
                      "feature.rogue-expertise-1": [{"option": "a", "picks": ["Skill: Stealth", "Skill: Perception"]}],
                      "class.equipment.1": ["a"], "class.equipment.2": ["b"], "class.equipment.3": ["a"],
                      "background.languages": ["Infernal", "Sylvan"], "background.equipment.1": ["Emblem"],
                      "background.equipment.prayer": ["a"]},
          "alignment": "Neutral Evil",
          "personality": {"traits": ["Says little and watches everything.",
                                     "Dry, cutting humour, and only for those she trusts."],
                          "ideal": "Loyalty. Shae is the one constant; everything else is a tool.",
                          "bond": "Shae's sister in all but blood: they clawed their way up together.",
                          "flaw": "Jealous of anyone who gets too close to Shae."},
          "appearance": "Lean, dark-eyed, a silver-threaded braid; knives always visible, never flaunted."}

ELARA = {"name": "Elara Velaris", "race": "elf", "class": "bard", "ability_method": "standard_array",
         "base_scores": {"STR": 8, "DEX": 14, "CON": 12, "INT": 13, "WIS": 10, "CHA": 15},
         "choices": {"trait.high-elf-cantrip": ["Message"], "trait.extra-language": ["Celestial"],
                     "class.proficiencies.1": ["Skill: Persuasion", "Skill: Deception", "Skill: History"],
                     "class.proficiencies.2": ["Lute", "Viol", "Flute"],
                     "class.equipment.1": ["a"], "class.equipment.2": ["a"], "class.equipment.3": ["a"],
                     "background.languages": ["Infernal", "Sylvan"], "background.equipment.1": ["Emblem"],
                     "background.equipment.prayer": ["a"]},
         "cantrips": ["Vicious Mockery", "Minor Illusion"],
         "spells": ["Charm Person", "Healing Word", "Sleep", "Disguise Self"],
         "alignment": "Neutral",
         "personality": {"traits": ["Socially effortless; reads a room in a glance.",
                                    "Ambitious, and honest about it."],
                         "ideal": "Ambition. Mourhold belongs to those who shape it.",
                         "bond": "Shae, her betrothed: partners in love and in politics.",
                         "flaw": "Confident to the point of watchfulness: she notices every rival."},
         "appearance": "Tall, graceful, dark hair worn up; midnight blue and silver."}


def base_game(path: Path):
    """The base campaign as a Game: Shae, then Rhylla and Elara joined and levelled to 5 through the game's own tools."""
    import asyncio

    from dm import play
    from tests.autochar import auto_levels
    sheet, errs = create.build(SHAE, None, SHAE_LEVELS)
    assert sheet, errs
    g = play.Game({"sheet": sheet, "backend": "sdk"}, path)
    tools = {t.name: t.handler for t in g.tools()}

    def call(name: str, **a):
        res = asyncio.run(tools[name](a))
        assert not res.get("is_error"), res["content"][0]["text"]
    for ch in (RHYLLA, ELARA):
        call("change_party", add=ch)
        for rec in auto_levels(ch, 5):
            call("level_up", who=ch["name"], record=rec)
    return g


if __name__ == "__main__":
    g = base_game(HERE / "out" / "base.json")
    print(g.status())
