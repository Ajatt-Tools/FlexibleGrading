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

from typing import Callable

from anki.cards import Card
from anki.hooks import wrap
from aqt import gui_hooks
from aqt.reviewer import Reviewer

from .config import config
from .toolbar import LastEase


def add_vim_shortcuts(self: Reviewer, _old: Callable):
    # Credit: https://ankiweb.net/shared/info/1197299782
    class VimShortcuts:
        _shortcuts = {
            "u": lambda: self.mw.onUndo(),  # undo
            "i": lambda: self.mw.onEditCurrent(),  # edit
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
        # '2' and '4' from the original _shortcutKeys() should be filtered out as well.
        return VimShortcuts.pass_fail() + [(k, v) for k, v in _old(self) if k != '2' and k != '4']
    else:
        # Default shortcuts.
        return VimShortcuts.default() + _old(self)


def answer_card(self: Reviewer, ease, _old: Callable):
    # Allows answering from the front side
    if config['flexible_grading'] is True and self.state == "question":
        self.state = "answer"

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


def apply_label_colors(buttons: tuple) -> tuple:
    def color_label(ease, label):
        label = f"<font color=\"{config.get_color(ease)}\">{label}</font>"
        return ease, label

    edited_buttons = [color_label(button[0], button[1]) for button in buttons]
    return tuple(edited_buttons)


def filter_answer_buttons(buttons: tuple, _: Reviewer, __: Card) -> tuple:
    # Called by _answerButtonList, before _answerButtons is called
    if config['pass_fail'] is True:
        buttons = only_pass_fail(buttons)

    if config['color_buttons'] is True:
        buttons = apply_label_colors(buttons)

    return buttons


def make_buttonless_ease_row(self: Reviewer) -> str:
    ease_row = []
    for ease, label in self._answerButtonList():
        if config['color_buttons'] is True:
            color = config.get_color(ease)
            attrs = f' style="color: {color};"'
        else:
            attrs = ''
        ease_row.append(f'<div{attrs}>{self._buttonTime(ease)}</div>')

    return ''.join(ease_row)


def wrap_buttonless_ease_row(html: str) -> str:
    return f'<div ' \
           f'style="' \
           f'display: flex;' \
           f'justify-content: space-between;' \
           f'max-width: 400px;' \
           f'user-select: none;"' \
           f'>{html}</div>'


def make_answer_buttons(self: Reviewer, _old: Callable):
    if config['remove_buttons'] is True:
        html = make_buttonless_ease_row(self)
        html = wrap_buttonless_ease_row(html)
    elif config['prevent_clicks'] is True:
        html: str = _old(self).replace('<button', '<button disabled')
    else:
        html: str = _old(self)

    return html


def main():
    # Add vim answer shortcuts
    Reviewer._shortcutKeys = wrap(Reviewer._shortcutKeys, add_vim_shortcuts, "around")

    # Activate flexible grading, if enabled by the user
    Reviewer._answerCard = wrap(Reviewer._answerCard, answer_card, "around")

    # Create html layout for the answer buttons.
    # Buttons are either removed, disabled or left unchanged depending on config options.
    Reviewer._answerButtons = wrap(Reviewer._answerButtons, make_answer_buttons, "around")

    # Edit (ease, label) tuples which are used to create answer buttons later.
    # Depending on the settings labels are colored and Hard and Easy buttons are removed.
    gui_hooks.reviewer_will_init_answer_buttons.append(filter_answer_buttons)

    # When Reviewer is open, print the last card's stats on the top toolbar.
    gui_hooks.top_toolbar_did_init_links.append(LastEase.append_link)
    gui_hooks.reviewer_did_answer_card.append(LastEase.update)

    # Don't show the last card's stats when Reviewer is not open.
    gui_hooks.reviewer_will_end.append(LastEase.hide)
    gui_hooks.main_window_did_init.append(LastEase.hide)


main()
