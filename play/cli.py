"""`python -m play`: the terminal front end over the game API (contracts/cli.md, contracts/engine-api.md).

    python -m play                       # the menu: New game, Continue, Replay, Report, Quit
    python -m play new "The Salt Road"   # saves/The Salt Road.db
    python -m play continue [name]       # the named game, or the most recently played one
    python -m play replay <name>         # rebuild from events with recorded model outputs
    python -m play report <name>         # per-turn classes, gates, degrees, verdicts, cost, latency
    --offline                            # any command: the free stand-in model, no key, no cost

`engine.game` is imported only when a game starts, so this module imports without it. Tests pass `game_cls`
and `config` to `main` to drive a fake game.
"""

from __future__ import annotations

import argparse
import importlib
import re
import sqlite3
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, TextIO

from engine.llm.base import MissingKey, ModelRefused, ModelUnavailable
from play.render import ascii_safe, render_response, terminal_width, wrap

REPO_ROOT = Path(__file__).resolve().parents[1]
SAVES = REPO_ROOT / "saves"

KEY_HELP = ("No Gemini API key was found. Put it in a file named .env at the repo root, as one line:\n"
            "  GEMINI_API_KEY=your-key-here\n"
            "(or set GEMINI_API_KEY in the environment). To play free with the plain stand-in model instead, add\n"
            "--offline, e.g. `python -m play --offline new \"My game\"`.")
UNAVAILABLE = "The model is unavailable right now. Your message is kept; try again."
REFUSED = ("The model refused to answer that (a provider safety refusal; it is logged). Your message is kept; "
           "try again, or put it another way.")
# Pauses that sit inside a turn: the budget prompt waits until the turn is over (cli.md "never mid-turn").
MID_TURN = frozenset({"offer", "clarify", "redirect", "near_miss", "last_chance", "yield_terms"})
CODEX_SECTIONS = ("sheet", "abilities", "conditions", "journal", "threads")
HELP = """Commands (out of fiction; never sent to a model):
  /sheet /abilities /conditions /journal /threads   your codex pages
  /rules <id>          a rule card by id
  /turn [n]            the turn record (the last turn, or turn n)
  /spend               turn, session and game cost against the budget
  /branch <label>      a save point to return to
  /budget <usd>|off    the session budget for warnings
  /autocommit on|off   auto-commit safe offers (a lethal frame never is)
  /fix <what>          dispute something: the DM checks the record and corrects a seen error
  /quit                save and exit (nothing is ever lost)
At a pause, a number (or letter) picks that choice; any other text is what your character does or says."""


class Quit(Exception):
    """The player is done: leave the play loop (the store is already durable)."""


@dataclass
class Saved:
    path: Path
    title: str
    pc: str | None
    turns: int
    last_played: date

    def line(self) -> str:
        bits = ", ".join([*([self.pc] if self.pc else []), f"turn {self.turns}",
                          f"last played {self.last_played.isoformat()}"])
        return f'"{self.title}" ({bits})'


# ------------------------------------------------------------------------------------------- saves


def save_path(saves: Path, name: str) -> Path:
    """saves/<name>.db, with characters a file name cannot hold replaced."""
    stem = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "_", name.strip()).strip(". ") or "game"
    return saves / f"{stem}.db"


def _mtime(path: Path) -> float:
    return max((p.stat().st_mtime for p in (path, Path(f"{path}-wal")) if p.exists()), default=0.0)


def describe(path: Path) -> Saved:
    """Title, PC, turn count and last-played date, read straight from the save file (read-only, no replay)."""
    title, pc, turns = path.stem, None, 0
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            row = conn.execute("SELECT json_extract(payload, '$.entity.name') FROM events WHERE type='entity_created'"
                               " AND json_extract(payload, '$.entity.kind')='pc' ORDER BY seq DESC LIMIT 1").fetchone()
            pc = row[0] if row else None
            row = conn.execute("SELECT json_extract(payload, '$.value') FROM events WHERE type='meta_set'"
                               " AND json_extract(payload, '$.key')='title' ORDER BY seq DESC LIMIT 1").fetchone()
            if row and isinstance(row[0], str) and row[0].strip():
                title = row[0].strip()
            turns = int(conn.execute("SELECT COUNT(*) FROM turns").fetchone()[0])
        finally:
            conn.close()
    except sqlite3.Error:
        pass
    return Saved(path, title, pc, turns, date.fromtimestamp(_mtime(path)))


def list_saves(saves: Path) -> list[Path]:
    """Every save, most recently played first."""
    return sorted(saves.glob("*.db"), key=_mtime, reverse=True) if saves.is_dir() else []


def find_save(saves: Path, name: str) -> Path | None:
    """A save by name: the exact file, else a case-insensitive match on the stem."""
    exact = save_path(saves, name)
    if exact.exists():
        return exact
    p = Path(name)
    if p.suffix == ".db" and p.exists():
        return p
    want = exact.stem.casefold()
    return next((s for s in list_saves(saves) if s.stem.casefold() == want), None)


# ------------------------------------------------------------------------------------------- the app


@dataclass
class App:
    stdin: TextIO
    stdout: TextIO
    saves: Path
    offline: bool = False
    game_cls: Any = None
    config: Callable[[bool], Any] | None = None
    width: int = field(default_factory=terminal_width)

    # ---- io
    def say(self, text: str = "") -> None:
        enc = getattr(self.stdout, "encoding", None)
        self.stdout.write(ascii_safe(wrap(text, self.width), enc) + "\n")
        self.stdout.flush()

    def ask(self, prompt: str = "> ") -> str | None:
        """One line of input; None at end of input."""
        self.stdout.write(prompt)
        self.stdout.flush()
        line = self.stdin.readline()
        return None if line == "" else line.rstrip("\r\n")

    # ---- engine
    def _game(self) -> Any:
        if self.game_cls is None:
            self.game_cls = importlib.import_module("engine.game").Game
        return self.game_cls

    def _config(self) -> Any:
        if self.config is not None:
            return self.config(self.offline)
        # offline=True swaps every model role for the free stand-in (contracts/model-calls.md "Offline stand-in")
        return importlib.import_module("engine.game").GameConfig(offline=self.offline)

    def start(self, path: Path, *, new: bool) -> int:
        try:
            game, resp = (self._game().new if new else self._game().open)(path, self._config())
        except MissingKey:
            self.say(KEY_HELP)
            return 2
        except (ModelUnavailable, ModelRefused) as e:
            self.say(UNAVAILABLE if isinstance(e, ModelUnavailable) else REFUSED)
            return 1
        try:
            Session(self, game).run(resp)
        finally:
            close = getattr(game, "close", None)
            if callable(close):
                close()
        return 0

    # ---- commands
    def new(self, name: str | None) -> int:
        while not name:
            name = self.ask("Name this game: ")
            if name is None:
                return 0
            name = name.strip()
        path = save_path(self.saves, name)
        if path.exists():
            self.say(f'There is already a game called "{path.stem}". Continue it, or pick another name.')
            return 1
        self.saves.mkdir(parents=True, exist_ok=True)
        return self.start(path, new=True)

    def resume(self, name: str | None) -> int:
        path = find_save(self.saves, name) if name else next(iter(list_saves(self.saves)), None)
        if path is None:
            self.say(f'No saved game called "{name}".' if name else "There are no saved games yet.")
            return 1
        return self.start(path, new=False)

    def replay(self, name: str | None) -> int:
        from play.report import replay

        path = self._pick(name, "Replay which game?")
        return 1 if path is None else replay(path, self.say, self._game())

    def report(self, name: str | None) -> int:
        from play.report import report

        path = self._pick(name, "Report on which game?")
        return 1 if path is None else report(path, self.say)

    def _pick(self, name: str | None, question: str) -> Path | None:
        if name:
            path = find_save(self.saves, name)
            if path is None:
                self.say(f'No saved game called "{name}".')
            return path
        saves = list_saves(self.saves)
        if not saves:
            self.say("There are no saved games yet.")
            return None
        self.say(question)
        for i, p in enumerate(saves, 1):
            self.say(f"  {i}) {describe(p).line()}")
        ans = (self.ask() or "").strip()
        if ans.isdigit() and 1 <= int(ans) <= len(saves):
            return saves[int(ans) - 1]
        return find_save(self.saves, ans) if ans else None

    def menu(self) -> int:
        while True:
            saves = list_saves(self.saves)
            cont = f"Continue: {describe(saves[0]).line()}" if saves else "Continue (no saved games yet)"
            self.say("\n  THE GAME" + ("  [offline stand-in]" if self.offline else ""))
            for i, label in enumerate(["New game", cont, "Replay a game", "Report on a game", "Quit"], 1):
                self.say(f"  {i}) {label}")
            ans = self.ask()
            if ans is None:
                return 0
            pick = ans.strip().lower()
            if pick in ("1", "new"):
                code = self.new(None)
            elif pick in ("2", "continue"):
                code = self.resume(None)
            elif pick in ("3", "replay"):
                code = self.replay(None)
            elif pick in ("4", "report"):
                code = self.report(None)
            elif pick in ("5", "quit", "q", "/quit"):
                return 0
            else:
                self.say("Pick 1-5.")
                continue
            if pick in ("1", "new", "2", "continue") and code in (0, 2):
                return code  # the sitting is over (/quit exits); or no key: the explanation is the last thing shown


# ------------------------------------------------------------------------------------------- the play loop


class Session:
    """One sitting at one game: show a response, read a line, send it, repeat."""

    def __init__(self, app: App, game: Any) -> None:
        self.app, self.game = app, game
        self.pause: Any = None
        self.last_turn: str | None = None
        self.notice: str | None = None  # a budget notice held until the turn is over

    def run(self, first: Any) -> None:
        try:
            self.show(first)
            while True:
                line = self.app.ask()
                if line is None:
                    raise Quit
                self.handle(line.strip())
        except (Quit, KeyboardInterrupt):
            self.app.say("\nSaved. Until next time.")

    def handle(self, text: str) -> None:
        if not text:
            return
        if text.startswith("/"):
            self.command(text)
            return
        choices = self.pause.choices if self.pause is not None else []
        if choices and len(text) == 1 and "a" <= text.lower() <= "z" and ord(text.lower()) - 96 <= len(choices):
            text = str(ord(text.lower()) - 96)  # a letter picks too: a is 1)
        if not choices and text.isdigit():
            self.app.say("Nothing to pick by number here: answer in words (or /help).")
            return
        if choices and text.isdigit():
            n = int(text)
            if not 1 <= n <= len(choices):
                self.app.say(f"Pick 1-{len(choices)}, or say what you do.")
                return
            self.pick(choices[n - 1].id)
            return
        self.send(self.game.submit, text)

    def pick(self, choice_id: str) -> None:
        if choice_id in ("quit", "stop_here"):  # an ending's quit, the budget pause's stop: the game stays open
            raise Quit
        if choice_id == "new_world":
            self.app.say("A new world is a new game. Pick New game from the menu.")
            raise Quit
        if choice_id == "new_character":
            self.send(self.game.new_character)
            return
        self.send(self.game.answer, choice_id)

    def send(self, fn: Callable[..., Any], *args: Any) -> None:
        try:
            resp = fn(*args)
        except MissingKey:
            self.app.say(KEY_HELP)
            raise Quit from None
        except ModelUnavailable:
            self.app.say(UNAVAILABLE)
            return
        except ModelRefused:
            self.app.say(REFUSED)
            return
        except ValueError as e:  # e.g. a choice the open pause does not have
            self.app.say(str(e))
            return
        self.show(resp)

    def show(self, resp: Any) -> None:
        self.pause = resp.pause
        if resp.turn_id:
            self.last_turn = resp.turn_id
        self.app.say(render_response(resp, self.app.width))
        self.budget_check(resp)

    def budget_check(self, resp: Any) -> None:
        """cli.md: after the budget is passed, between turns, "Keep playing? 1) Yes 2) Stop here"."""
        if resp.budget_notice:
            self.notice = resp.budget_notice
        pause_kind = resp.pause.kind if resp.pause is not None else None
        if not self.notice or pause_kind in MID_TURN or pause_kind == "budget":
            return  # mid-turn: wait; a budget pause asks with its own choices
        notice, self.notice = self.notice, None
        self.app.say(notice)
        while True:
            ans = self.app.ask("Keep playing? 1) Yes 2) Stop here\n> ")
            if ans is None or ans.strip() in ("2", "stop", "no", "n"):
                raise Quit
            if ans.strip() in ("1", "yes", "y", ""):
                return

    # ---- slash commands: out of fiction, never sent to a model
    def command(self, text: str) -> None:
        name, _, arg = text[1:].partition(" ")
        name, arg = name.lower(), arg.strip()
        if name == "quit":
            raise Quit
        if name in ("help", "?"):
            self.app.say(HELP)
        elif name in CODEX_SECTIONS:
            self.app.say(self.game.codex(name).text)
        elif name == "rules":
            self.app.say(self.game.codex(f"rules {arg}").text if arg else "Usage: /rules <id>, e.g. /rules 01.7.1")
        elif name == "turn":
            self.turn(arg)
        elif name == "spend":
            self.app.say(spend_line(self.game.spend()))
        elif name == "branch":
            self.app.say(f"Branch saved: {self.game.branch(arg)}" if arg else "Usage: /branch <label>")
        elif name == "budget":
            self.budget(arg)
        elif name == "autocommit":
            if arg.lower() not in ("on", "off"):
                self.app.say("Usage: /autocommit on|off")
                return
            self.game.set_pref("autocommit", arg.lower() == "on")
            self.app.say(f"Auto-commit of safe offers is {arg.lower()} (a lethal frame is never auto-committed).")
        elif name == "fix":
            if not arg:
                self.app.say("Usage: /fix <what you think is wrong>")
            elif callable(getattr(self.game, "dispute", None)):
                self.send(self.game.dispute, arg)
            else:  # the Reader classifies this as a DISPUTE part (12.3.6)
                self.send(self.game.submit, f"(Out of character: I dispute this - {arg})")
        else:
            self.app.say(f"Unknown command /{name}. /help lists them.")

    def turn(self, arg: str) -> None:
        turn_id = f"turn.{arg}" if arg.isdigit() else (arg or self.last_turn)
        if not turn_id:
            self.app.say("No turn has been played yet.")
            return
        rec = self.game.turn_record(turn_id)
        self.app.say(turn_text(rec) if rec is not None else f"No record of {turn_id}.")

    def budget(self, arg: str) -> None:
        if arg.lower() in ("off", "none"):
            self.game.set_pref("budget_usd", None)
            self.app.say("No budget warnings this session.")
            return
        try:
            usd = float(arg.removeprefix("$"))
        except ValueError:
            usd = -1.0
        if usd < 0:
            self.app.say("Usage: /budget <usd> (e.g. /budget 2.50), or /budget off")
            return
        self.game.set_pref("budget_usd", usd)
        self.app.say(f"Session budget set to ${usd:.2f} (a warning between turns, never a stop).")


def _get(obj: Any, key: str, default: Any = None) -> Any:
    return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)


def spend_line(s: Any) -> str:
    budget = _get(s, "budget_usd")
    return (f"This turn ${_get(s, 'turn_usd', 0.0):.4f} | this session ${_get(s, 'session_usd', 0.0):.4f} | "
            f"this game ${_get(s, 'game_usd', 0.0):.4f} | budget "
            + (f"${budget:.2f}" if budget is not None else "off"))


def turn_text(rec: Any) -> str:
    """The turn record in short (data-model.md §4): input, classes, frames, writes, verdicts, cost."""
    parts = _get(rec, "parts", []) or []
    classes = [str(_get(p, "cls", None) or _get(p, "class", "?")) for p in parts]
    verdicts = [str(_get(v, "verdict", "?")) for v in (_get(rec, "verdicts", []) or [])]
    pause = _get(rec, "pause")
    lines = [f"[TURN] {_get(rec, 'turn_id', '?')}",
             f"  You said: {_get(rec, 'input_verbatim', '')}",
             f"  Classes: {', '.join(classes) or '-'}",
             f"  Frames: {', '.join(_get(rec, 'beats', []) or []) or '-'}",
             f"  Oracle calls: {len(_get(rec, 'oracle_calls', []) or [])} | writes: "
             f"{len(_get(rec, 'writes', []) or [])}",
             f"  Verdicts: {', '.join(verdicts) or '-'}"
             + (" | plain fallback used" if _get(rec, "fallback_used", False) else ""),
             f"  Pause: {_get(pause, 'kind', '-') if pause else '-'}",
             f"  Model calls: {len(_get(rec, 'model_calls', []) or [])} | cost ${_get(rec, 'cost_usd', 0.0):.4f}"
             f" | {_get(rec, 'latency_ms', 0)} ms"]
    return "\n".join(lines)


# ------------------------------------------------------------------------------------------- entry point


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m play", description="Play the game in the terminal.",
                                epilog="--offline (any command) plays with the free stand-in model: no key, no cost.")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("new", help="start a new game").add_argument("name", nargs="?")
    sub.add_parser("continue", help="continue a game (the latest if no name)").add_argument("name", nargs="?")
    sub.add_parser("replay", help="replay a game and check it is identical").add_argument("name", nargs="?")
    sub.add_parser("report", help="per-turn report of a game").add_argument("name", nargs="?")
    return p


def main(argv: Sequence[str] | None = None, *, stdin: TextIO | None = None, stdout: TextIO | None = None,
         saves: Path | None = None, game_cls: Any = None, config: Callable[[bool], Any] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    offline = "--offline" in args
    ns = _parser().parse_args([a for a in args if a != "--offline"])
    app = App(stdin or sys.stdin, stdout or sys.stdout, saves or SAVES, offline=offline, game_cls=game_cls,
              config=config)
    try:
        if ns.cmd == "new":
            return app.new(ns.name)
        if ns.cmd == "continue":
            return app.resume(ns.name)
        if ns.cmd == "replay":
            return app.replay(ns.name)
        if ns.cmd == "report":
            return app.report(ns.name)
        return app.menu()
    except KeyboardInterrupt:
        app.say("")
        return 0
