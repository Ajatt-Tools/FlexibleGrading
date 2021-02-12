# -*- coding: utf-8 -*-
#
# AJT Flexible Grading add-on for Anki 2.1
# Copyright (C) 2021  Ren Tatsumoto. <tatsu at autistici.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Any modifications to this file must keep this entire header intact.

import time
from typing import Callable

import aqt
from anki.cards import Card
from anki.hooks import wrap
from anki.lang import _
from aqt import mw, gui_hooks
from aqt.reviewer import Reviewer
from aqt.toolbar import Toolbar

global_query = ""
LAST_EASE_ID = "last_ease"

config = {
    'buttons': {
        1: {"label": "Again", "color": "red"},
        2: {"label": "Hard", "color": "orange"},
        3: {"label": "Good", "color": "green"},
        4: {"label": "Easy", "color": "blue"},
    },
    'remove_buttons': False,
    'prevent_clicks': True,
    'pass_fail': False,
    'flexible_grading': True,
    'color_buttons': True,
}


def edit_button_label(ease: int, label: str = None) -> str:
    if label is None:
        label = _(config['buttons'][ease]['label'])

    if config['color_buttons'] is True:
        label = f"<font color=\"{config['buttons'][ease]['color']}\">{label}</font>"

    return label


def add_vim_shortcuts(self: Reviewer, _old):
    # Credit: https://ankiweb.net/shared/info/1197299782
    class VimShortcuts:
        _shortcuts = {
            "u": lambda: mw.onUndo(),  # undo
            "h": lambda: self._answerCard(1),  # fail
            "j": lambda: self._answerCard(2),  # hard
            "k": lambda: self._answerCard(3),  # normal
            "l": lambda: self._answerCard(4),  # easy
        }

        @classmethod
        def default(cls):
            return [(k, v) for k, v in cls._shortcuts.items()]

        @classmethod
        def pass_fail(cls):
            return [(k, v) for k, v in cls._shortcuts.items() if k != 'j' and k != 'l']

    if config['pass_fail'] is True:
        # PassFail mode. Pressing 'Hard' and 'Easy' is not allowed.
        # '2' and '4' from the original _shortcutKeys() should be filtered as well.
        return VimShortcuts.pass_fail() + [(k, v) for k, v in _old(self) if k != '2' and k != '4']
    else:
        # Default shortcuts.
        return VimShortcuts.default() + _old(self)


def answer_card(self: Reviewer, ease, _old):
    # Allows answering from the front side
    if config['flexible_grading'] is True and self.state == "question":
        self.state = 'answer'

    # min() makes sure the original _answerCard() never skips
    _old(self, min(self.mw.col.sched.answerButtons(self.card), ease))


def only_pass_fail(buttons: tuple) -> tuple:
    edited_buttons = []
    for button in buttons:
        ease = button[0]
        label = button[1]
        if ease == 1 or ease == 3:
            edited_buttons.append((ease, label))

    return tuple(edited_buttons)


def filter_answer_buttons(buttons: tuple, _: Reviewer, __: Card) -> tuple:
    if config['remove_buttons'] is True:
        return ()

    edited_buttons = []

    if config['pass_fail'] is True:
        buttons = only_pass_fail(buttons)

    for button in buttons:
        ease = button[0]
        label = button[1]
        edited_buttons.append((ease, edit_button_label(ease, label)))

    return tuple(edited_buttons)


def answer_buttons(self: Reviewer, _old: Callable):
    if config['prevent_clicks'] is True:
        html: str = _old(self)
        return html.replace('<button', '<button disabled')
    else:
        return _old(self)


def append_last_card_ease(links: list, toolbar: Toolbar):
    def last_ease_click_handler():
        browser: aqt.browser = aqt.dialogs.open('Browser', mw)
        browser.activateWindow()
        browser.form.searchEdit.lineEdit().setText(global_query)
        if hasattr(browser, 'onSearch'):
            browser.onSearch()
        else:
            browser.onSearchActivated()

    link = toolbar.create_link(
        LAST_EASE_ID,
        "Last Ease",
        last_ease_click_handler,
        id=LAST_EASE_ID,
    )
    links.insert(0, link)


def handle_due(card: Card):
    days = card.ivl
    months = days / (365 / 12)
    years = days / 365
    if years >= 1:
        ivl = '%.1fy' % years
    elif months >= 1:
        ivl = '%.1fmo' % months
    else:
        ivl = '%dd' % days
    return ivl


def handle_learn(card: Card):
    minutes = (card.due - time.time()) / 60
    hours = minutes / 60
    if hours >= 1:
        ivl = '%.1fh' % hours
    else:
        ivl = '%dm' % minutes
    return ivl


def human_ivl(card: Card) -> str:
    # https://github.com/ankidroid/Anki-Android/wiki/Database-Structure

    ivl = "unknown"

    print(card.due, card.queue, card.type, card.ivl) # TODO remove
    if card.queue <= -2:
        ivl = "buried"
    elif card.queue == -1:
        ivl = "suspended"
    elif card.type == 2:
        ivl = handle_due(card)
    elif card.queue == 1 and (card.type == 3 or card.type == 1):
        ivl = handle_learn(card)
    elif card.queue == 3 and card.type == 3:
        ivl = "tomorrow"

    return ivl


def update_last_ease(reviewer: Reviewer, card: Card, ease: int):
    label = _(config['buttons'][ease]['label'])
    color = config['buttons'][ease]['color']
    label = f"{label[:1]}: {human_ivl(card)}"

    reviewer.mw.toolbar.web.eval(f"""
            elem = document.getElementById("{LAST_EASE_ID}");
            elem.innerHTML = "{label}";
            elem.style.color = "{color}";
            elem.style.display = "inline";
    """)

    global global_query
    global_query = f"cid:{card.id}"


def erase_last_ease():
    mw.toolbar.web.eval(f"""
            elem = document.getElementById("{LAST_EASE_ID}");
            elem.innerHTML = "";
            elem.style.color = "";
            elem.style.display = "none";
    """)


def main():
    # hooks / wraps
    Reviewer._shortcutKeys = wrap(Reviewer._shortcutKeys, add_vim_shortcuts, "around")
    Reviewer._answerCard = wrap(Reviewer._answerCard, answer_card, "around")
    Reviewer._answerButtons = wrap(Reviewer._answerButtons, answer_buttons, "around")
    gui_hooks.reviewer_will_init_answer_buttons.append(filter_answer_buttons)
    gui_hooks.top_toolbar_did_init_links.append(append_last_card_ease)
    gui_hooks.reviewer_did_answer_card.append(update_last_ease)

    # Don't show the last ease stats when Reviewer is not open.
    gui_hooks.reviewer_will_end.append(erase_last_ease)
    gui_hooks.main_window_did_init.append(erase_last_ease)


main()
