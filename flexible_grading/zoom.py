# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from typing import Optional

from aqt import gui_hooks, mw
from aqt.qt import *
from aqt.utils import tooltip

from .config import config


def relevant_states() -> tuple[str, ...]:
    return "deckBrowser", "overview", "review"


def set_zoom_shortcuts():
    mw.form.actionZoomIn.setShortcuts([
        QKeySequence("Ctrl++"),
        QKeySequence("Ctrl+="),
    ])
    mw.form.actionZoomOut.setShortcuts([
        QKeySequence("Ctrl+-"),
    ])


def remove_zoom_shortcuts():
    mw.form.actionZoomIn.setShortcuts([])
    mw.form.actionZoomOut.setShortcuts([])


def set_zoom_factor(state: str, factor: float):
    mw.web.setZoomFactor(factor)
    config.set_zoom_state(state, round(factor, 2))
    if config["tooltip_on_zoom_change"]:
        tooltip(f"{state.capitalize()} zoom: {mw.web.zoomFactor() * 100:.0f}%", period=1000)


def on_state_change(new_state: Optional[str], _old_state: Optional[str]) -> None:
    if config["set_zoom_shortcuts"]:
        set_zoom_shortcuts()
    else:
        remove_zoom_shortcuts()

    if config["remember_zoom_level"] and new_state in relevant_states():
        config.write_config()  # Write previously set values
        saved_factor = config.get_zoom_state(new_state)
        if mw.web.zoomFactor() != saved_factor:
            set_zoom_factor(new_state, saved_factor)


def reconnect_zoom_actions():
    z_in, z_out, z_reset = mw.form.actionZoomIn, mw.form.actionZoomOut, mw.form.actionResetZoom

    z_in.triggered.disconnect()
    z_out.triggered.disconnect()
    z_reset.triggered.disconnect()

    qconnect(z_in.triggered, lambda: set_zoom_factor(mw.state, mw.web.zoomFactor() + 0.1))
    qconnect(z_out.triggered, lambda: set_zoom_factor(mw.state, mw.web.zoomFactor() - 0.1))
    qconnect(z_reset.triggered, lambda: set_zoom_factor(mw.state, 1))


def init():
    if config["set_zoom_shortcuts"]:
        set_zoom_shortcuts()
    reconnect_zoom_actions()

    gui_hooks.state_did_change.append(on_state_change)
    gui_hooks.profile_will_close.append(lambda: on_state_change(None, mw.state))
    gui_hooks.deck_browser_did_render.append(lambda *_: on_state_change(mw.state, None))
