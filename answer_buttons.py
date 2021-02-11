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

from anki.cards import Card
from anki.hooks import wrap
from anki.lang import _
from aqt import mw, gui_hooks
from aqt.reviewer import Reviewer
from aqt.toolbar import Toolbar

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
    return [
               ("h", lambda: self._answerCard(1)),  # fail
               ("j", lambda: self._answerCard(2)),  # hard
               ("k", lambda: self._answerCard(3)),  # normal
               ("l", lambda: self._answerCard(4)),  # easy
               ("u", lambda: mw.onUndo()),  # undo
           ] + _old(self)


def answer_card(self: Reviewer, ease, _old):
    # Allows answering from the front side
    if config['flexible_grading'] is True and self.state == "question":
        self.state = 'answer'

    # min() makes sure the original _answerCard() never skips
    _old(self, min(self.mw.col.sched.answerButtons(self.card), ease))


def leave_pass_fail(buttons: tuple) -> tuple:
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
        buttons = leave_pass_fail(buttons)

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
    links.append("<span id=\"last_ease\"></span>")


def update_last_ease(reviewer, card, ease):
    reviewer.mw.toolbar.web.eval(f"""
            elem = document.getElementById("last_ease");
            elem.innerHTML = "{config['buttons'][ease]['label']}";
            elem.style.color = "{config['buttons'][ease]['color']}";
    """)


def main():
    # hooks / wraps
    Reviewer._shortcutKeys = wrap(Reviewer._shortcutKeys, add_vim_shortcuts, "around")
    Reviewer._answerCard = wrap(Reviewer._answerCard, answer_card, "around")
    Reviewer._answerButtons = wrap(Reviewer._answerButtons, answer_buttons, "around")
    gui_hooks.reviewer_will_init_answer_buttons.append(filter_answer_buttons)
    gui_hooks.top_toolbar_did_init_links.append(append_last_card_ease)
    gui_hooks.reviewer_did_answer_card.append(update_last_ease)


main()
