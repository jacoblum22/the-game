"""The opening (12.16.16; PR-12-8 session open; T069): after creation writes the character, play begins with a
scene framed at the seed's inciting incident and an open prompt. The work is `engine.dm.session.opening` (the
Director frames the scene at `world.opening`, the Narrator writes the opening through the checker like any
narration); this module is the game's entry point and the hand-over from creation.

    resp = begin_play(ctx, creation_resp)   # creation's last blocks ("Wren is ready"), then the opening
    needs_opening(state)                    # the active character has not had its opening yet (resume, a new PC)
"""

from __future__ import annotations

from engine.dm import oof
from engine.dm.context import TurnContext
from engine.dm.response import Response
from engine.dm.session import needs_opening, opening


def begin_play(ctx: TurnContext, before: Response | None = None) -> Response:  # rule: 12.16.16
    """The opening for the active character, after whatever creation said last (its blocks come first)."""
    resp = opening(ctx)
    if before is not None and before.oof_blocks:
        resp.oof_blocks = oof.ordered([*before.oof_blocks, *resp.oof_blocks])
    return resp


__all__ = ["begin_play", "needs_opening"]
