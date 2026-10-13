"""The game in the browser page (dm/page.html), under Pyodide. The page calls these; what the game prints reaches the
page through Pyodide's stdout, as it reached the old web page through the terminal. The model call goes from the page
straight to Anthropic with the player's key, kept in the browser's localStorage. Saves are kept by the page
(storeSave), each time the game writes one."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import js  # type: ignore[import-not-found]  # Pyodide's bridge to the page
from pyodide.http import pyfetch  # type: ignore[import-not-found]

from dm import model, play

API = "https://api.anthropic.com/v1/messages"
KEY = "anthropic-key"  # the localStorage entry the page keeps the key in
RETRY = (0, 429, 500, 502, 503, 504, 529)  # 0: no answer at all (the network)

session: play.Session | None = None


async def send(request: dict[str, Any]) -> dict[str, Any]:
    try:
        key = js.localStorage.getItem(KEY)
    except Exception:  # noqa: BLE001 - storage blocked (a private window, say)
        key = None
    if not key:
        raise model.Failed("no API key: add yours on the start screen")
    for attempt in range(3):  # as Anthropic's Python library does: two retries for overload and network trouble
        status, why = 0, ""
        try:
            r = await pyfetch(API, method="POST", body=json.dumps(request), headers={
                "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json",
                "anthropic-dangerous-direct-browser-access": "true"})  # Anthropic's switch for keys used in a page
            if r.ok:
                return await r.json()
            status, text = r.status, await r.text()
            try:
                why = json.loads(text)["error"]["message"]
            except (ValueError, KeyError, TypeError):
                why = text[:300]
        except Exception as e:  # noqa: BLE001 - the request never got an answer
            why = f"couldn't reach Anthropic ({e})"
        if status not in RETRY or attempt == 2:
            raise model.Failed(f"{status}: {why}" if status else why)
        await asyncio.sleep(2 * 2 ** attempt)
    raise AssertionError


model.send = send
play.on_save = lambda path, text: js.storeSave(path.name, text)


async def new(character: str) -> None:
    global session
    session = play.Session(backend="api")
    await session.new(character)


async def resume(name: str, text: str) -> str:
    """Continue a save the page kept. Returns why it can't be continued, or ""."""
    global session
    data = json.loads(text)
    if why := play.resumable(data, "api"):
        return why
    path = play.SAVES / name
    path.parent.mkdir(exist_ok=True)
    path.write_text(text, encoding="utf-8")
    session = play.Session(backend="api")
    await session.play(play.Game(data, path))
    return ""


def history(text: str) -> str:
    """A save's game so far, as the terminal printed it (the page shows it before resume() goes on)."""
    return play.history(json.loads(text))


async def line(text: str) -> bool:
    """The player's line. False once the game is over (the player quit)."""
    assert session
    return await session.line(text)


def sheet() -> str:
    """The sheet for the panel, without going through the game's output."""
    return play.sheet_report(session.game) if session and session.game else ""
