"""Registers ch.05's Milestone 1 boundary handlers with the time registry (see engine/harm/handlers.py).
The owner module `engine/time/handlers/h05.py` imports this module so the scheduler finds them."""

from __future__ import annotations

from engine.abilities.recharge import (
    h_05_day_recharge,
    h_05_focus_recover,
    h_05_rest_recharge,
    h_05_scene_recharge,
)
from engine.harm.handlers import HandlerBody, register_all

H05: dict[str, HandlerBody] = {
    "h.05.scene_recharge": h_05_scene_recharge,  # rule: 05.4.6
    "h.05.day_recharge": h_05_day_recharge,  # rule: 05.6.9
    "h.05.focus_recover": h_05_focus_recover,  # rule: PR-05-4
    "h.05.rest_recharge": h_05_rest_recharge,  # rule: PR-05-4
}

REGISTERED = register_all(H05)
