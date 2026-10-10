"""What the engine hands a front end after every step (contracts/engine-api.md `Response`, `Pause`).

    resp = Response(phase="seed", oof_blocks=[OofBlock(kind="SEED", text=block)], pause=Pause.of(record))
    resp.model_dump()        # the contract's shape: oof_blocks [{kind, text}], pause {kind, prompt, choices [{id, label}]}

`Pause.of(PauseRecord)` turns a stored pause (engine/store/events.py) into the API shape, so resume re-presents
exactly what was stored.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from engine.store.events import PauseRecord

Phase = Literal["seed", "creation", "play", "ending"]
OofKind = Literal["SEED", "CREATE", "OFFER", "RESULT", "STATUS", "WARNING", "REDIRECT", "CLARIFY", "NEAR_MISS", "LAST_CHANCE",
                  "RECAP", "NOTE", "EPILOGUE", "SHEET", "RULES"]
PauseKind = Literal["seed_step", "create_step", "offer", "clarify", "redirect", "near_miss", "last_chance",
                    "yield_terms", "ending", "budget"]


class OofBlock(BaseModel):
    """One out-of-fiction block (12.15). SHEET and RULES are PR-02-6/PR-02-7's creation blocks."""

    kind: OofKind
    text: str


class Choice(BaseModel):
    id: str
    label: str


class Pause(BaseModel):
    kind: PauseKind
    prompt: str = ""
    choices: list[Choice] = Field(default_factory=list)  # seed_step / create_step: the block's options, rules' order
    default_choice: str | None = None  # what "move on without choosing" means (PR-02-7, 12.16.2)
    frame_summary: dict[str, Any] | None = None  # OfferView for offers
    pause_id: str | None = None

    @classmethod
    def of(cls, rec: PauseRecord) -> Pause:
        return cls(kind=rec.kind, prompt=rec.prompt, choices=[Choice(id=c["id"], label=c.get("label", c["id"]))
                                                            for c in rec.choices],
                   default_choice=rec.default_choice, frame_summary=rec.detail.get("offer"), pause_id=rec.pause_id)


class Flags(BaseModel):
    fallback_used: bool = False
    review_flag: bool = False


class Response(BaseModel):
    turn_id: str | None = None  # null during seed and creation
    phase: Phase
    fiction: str = ""
    oof_blocks: list[OofBlock] = Field(default_factory=list)
    pause: Pause | None = None
    scene_ended: bool = False
    budget_notice: str | None = None
    flags: Flags = Field(default_factory=Flags)

    def split(self) -> tuple[list[OofBlock], list[OofBlock]]:  # rule: 12.15.2
        """(blocks shown above the passage, blocks after it). An auto-committed OFFER and the RESULT blocks right after
        it lead: the roll came first and the passage narrates its outcome (DL-12-124; printed below the passage, a
        critical success read as never narrated, spec 023 live [25]). Everything else follows the passage (12.15)."""
        bs = self.oof_blocks
        i = next((n for n, b in enumerate(bs) if b.text.startswith("[OFFER — auto]")), None)
        if i is None or not self.fiction:
            return [], list(bs)
        j = i + 1
        while j < len(bs) and bs[j].kind == "RESULT":
            j += 1
        return bs[i:j], bs[:i] + bs[j:]

    def text(self) -> str:
        """Everything shown, in order (an auto roll, the fiction, then the blocks; a pause block is always last, 12.15)."""
        lead, rest = self.split()
        return "\n\n".join([b.text for b in lead] + [self.fiction] * bool(self.fiction) + [b.text for b in rest])
