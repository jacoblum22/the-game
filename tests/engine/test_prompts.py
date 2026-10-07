"""Role prompts exist, are non-empty and stay within their word budgets (T-prompts)."""

import pytest

from engine.dm.roles.prompts import PROMPT_DIR, ROLES, WORD_BUDGET, load_prompt
from engine.llm.base import Role


def test_every_role_has_a_prompt_file() -> None:
    assert set(ROLES) == {r.value for r in Role}
    assert {p.stem for p in PROMPT_DIR.glob("*.md")} == set(ROLES)


@pytest.mark.parametrize("role", ROLES)
def test_prompt_is_nonempty_and_within_budget(role: str) -> None:
    text = load_prompt(role)
    assert text.startswith("# Role:")
    words = len(text.split())
    assert 100 < words <= WORD_BUDGET[role], f"{role}: {words} words (budget {WORD_BUDGET[role]})"


def test_load_prompt_is_cached_and_accepts_role_enum() -> None:
    assert load_prompt("reader") is load_prompt("reader")
    assert load_prompt(Role.NARRATOR) == load_prompt("narrator")


def test_unknown_role_raises() -> None:
    with pytest.raises(KeyError):
        load_prompt("bard")


def test_persona_free_roles_have_no_voice_section() -> None:
    # model-calls.md: only the Narrator has a voice; Reader and Framer are persona-free.
    for role in ("reader", "framer"):
        assert "## Voice" not in load_prompt(role)
