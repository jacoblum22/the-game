"""Autonomous test games (owner, 2026-10-14): a Claude player makes a character with the DM, then plays N rounds; run
again to play N more of the same game (same save, same player conversation).
    py -3.12 evals/autoloop/run.py <name> <rounds>        # from the worktree; the brief for <name> is in BRIEFS
Saves and logs go to evals/autoloop/games/ (not committed)."""
import asyncio
import contextlib
import io
import json
import sys
import time
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
)

from dm import play

HERE = Path(__file__).parent
GAMES = HERE / "games"
PLAYER_MODEL = "claude-sonnet-5-5"

BRIEFS = {
    "cleric": ("a hill dwarf cleric (Life domain)",
               "You play carefully and kindly: you talk to people, help the hurt, ask questions, keep promises, and "
               "think before you fight, though you will fight to protect others."),
    "barbarian": ("a half-orc barbarian",
                  "You play boldly: you like a fight, take physical risks, intimidate people, and charge in, but you "
                  "have a soft spot for the underdog and a code of honour."),
    "bard": ("a tiefling bard (College of Lore)",
             "You play as a curious trickster: you explore, poke at strange things, lie and bluff, try clever or odd "
             "uses of your spells and skills, and sometimes test the edges of the rules."),
}

PLAYER = """You are a human player in a solo D&D 5e game (2014 rules) run by a DM. {style}
Each message you get is what the DM just said (with any dice or game lines in brackets). Reply with only your next
line as the player, the way a real player types: one to three sentences, in character or describing what you do. No
narration of outcomes, no DM voice, no headings.
Care about continuity: every few turns refer back to a person, place, item, promise or detail from earlier in the game
by name. Now and then (every ten turns or so) ask the DM a short out-of-character question starting with "DM:" about
something established earlier (who someone was, what was said, your money or gear, a rule). Pursue the story's goals,
and make your own when there are none. Don't stall: if a scene is done, move on."""

CREATE = """You are about to make a new level-1 character with the DM. You want {what}. Answer the DM's questions and
make the choices it offers, decisively; when it asks what you'd like, pick something fitting rather than asking it to
choose for you. Give your character a name, a short past, and a personality."""


async def player_line(p: ClaudeSDKClient, text: str) -> str:
    await p.query(text)
    out, sid = "", None
    async for m in p.receive_response():
        if isinstance(m, AssistantMessage):
            out += "".join(b.text for b in m.content if isinstance(b, TextBlock))
        elif isinstance(m, ResultMessage):
            sid = m.session_id
    player_line.session_id = sid or getattr(player_line, "session_id", None)  # type: ignore[attr-defined]
    return out.strip()


def shown(entries: list[dict]) -> str:
    """What the player saw: the DM's text and the game's lines (dice, sheet, clock)."""
    return "\n\n".join(f"[{e['text']}]" if e["kind"] == "tool" else e["text"] for e in entries if e["kind"] in ("dm", "tool"))


async def main(name: str, rounds: int) -> None:
    GAMES.mkdir(exist_ok=True)
    play.SAVES = GAMES
    meta_path = GAMES / f"{name}.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    what, style = BRIEFS[name]
    p = ClaudeSDKClient(ClaudeAgentOptions(
        tools=[], setting_sources=[], model=PLAYER_MODEL, cwd=str(GAMES), resume=meta.get("player_session"),
        system_prompt=PLAYER.format(style=style),
        env={"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1", "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1"}))
    s = play.Session(play.MODEL, "sdk")
    times: list[dict] = meta.get("times", [])
    await p.connect()
    try:
        if meta.get("save"):
            path = (GAMES / Path(meta["save"]).name)
            await s.play(play.Game(json.loads(path.read_text(encoding="utf-8")), path))
            g = s.game
            seen = max(i for i, e in enumerate(g.transcript) if e["kind"] == "player") + 1  # the reply not yet read
        else:  # make the character first
            await s.new("new")
            text = CREATE.format(what=what) + "\n\nThe DM says:\n\n" + shown(s.creation.transcript)
            for _ in range(40):
                if s.game:
                    break
                c = s.creation
                k = len(c.transcript)
                await s.line(await player_line(p, text))
                text = shown((s.game or c).transcript[k:]) if not s.game else ""
            assert s.game, "character creation didn't finish in 40 lines"
            g = s.game
            meta["save"] = g.path.name
            seen = max(i for i, e in enumerate(g.transcript) if e["kind"] == "player") + 1
            meta["play_starts"] = seen
        for _ in range(rounds):
            text = shown(g.transcript[seen:])
            line = await player_line(p, text)
            seen = len(g.transcript)
            with open(GAMES / f"{name}.states.jsonl", "a", encoding="utf-8") as f:  # the game before this round, for replays
                f.write(json.dumps({"round": len(times) + 1, "sheet": g.sheet, "companions": g.companions, "fight": g.fight,
                                    "clock": g.clock, "lore": g.lore}, ensure_ascii=False) + "\n")
            t0 = time.time()
            await s.line(line)
            times.append({"turn": play.notebook.now(g.transcript), "seconds": round(time.time() - t0, 1)})
            meta.update(player_session=player_line.session_id, times=times)  # type: ignore[attr-defined]
            meta_path.write_text(json.dumps(meta, indent=1), encoding="utf-8")
        g.save()
    finally:
        meta["player_session"] = getattr(player_line, "session_id", None) or meta.get("player_session")
        meta["times"] = times
        meta_path.write_text(json.dumps(meta, indent=1), encoding="utf-8")
        await s.close()
        await p.disconnect()


if __name__ == "__main__":
    with contextlib.redirect_stdout(io.StringIO()):
        asyncio.run(main(sys.argv[1], int(sys.argv[2])))
    print(f"{sys.argv[1]}: done", file=sys.stderr)
