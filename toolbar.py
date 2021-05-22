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

import aqt
from anki.cards import Card
from anki.lang import _
from aqt import mw, gui_hooks
from aqt.reviewer import Reviewer
from aqt.toolbar import Toolbar

from .config import config


def handle_due(card: Card) -> str:
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


def handle_learn(card: Card) -> str:
    minutes = (card.due - time.time()) / 60
    hours = minutes / 60
    if minutes < 0:
        ivl = "unknown"
    elif hours >= 1:
        ivl = '%.1fh' % hours
    else:
        ivl = '%dm' % minutes
    return ivl


def human_ivl(card: Card) -> str:
    # https://github.com/ankidroid/Anki-Android/wiki/Database-Structure

    ivl = "unknown"

    if card.queue <= -2:
        ivl = "buried"
    elif card.queue == -1:
        ivl = "suspended"
    elif card.queue == 1 and (card.type == 3 or card.type == 1):
        ivl = handle_learn(card)
    elif card.queue == 3 and (card.type == 3 or card.type == 1):
        ivl = "tomorrow"
    elif card.queue == 4:
        ivl = "preview"
    elif card.type == 2:
        ivl = handle_due(card)

    return ivl


class LastEase:
    _html_link_id = "last_ease"
    _browser_query = ""
    _last_default_ease = 0

    @classmethod
    def set_last_default_ease(cls, _: Card):
        cls._last_default_ease = mw.reviewer._defaultEase()

    @classmethod
    def open_last_card(cls):
        browser: aqt.browser = aqt.dialogs.open('Browser', mw)
        browser.activateWindow()
        browser.form.searchEdit.lineEdit().setText(cls._browser_query)
        if hasattr(browser, 'onSearch'):
            browser.onSearch()
        else:
            browser.onSearchActivated()

    @classmethod
    def append_link(cls, links: list, toolbar: Toolbar) -> None:
        link = toolbar.create_link(
            cls._html_link_id,
            "Last Ease",
            cls.open_last_card,
            id=cls._html_link_id,
            tip="Last Ease",
        )
        links.insert(0, link)

    @classmethod
    def update(cls, reviewer: Reviewer, card: Card, ease: int) -> None:
        label = config.get_label(ease, cls._last_default_ease)
        color = config.get_colors().get(label.capitalize(), 'Pink')
        label = f"{_(label)[:1]}: {human_ivl(card)}"

        reviewer.mw.toolbar.web.eval(f"""
                elem = document.getElementById("{cls._html_link_id}");
                elem.innerHTML = "{label}";
                elem.style.color = "{color}";
                elem.style.display = "inline";
        """)

        cls._browser_query = f"cid:{card.id}"

    @classmethod
    def hide(cls, _=None) -> None:
        mw.toolbar.web.eval(f"""
                elem = document.getElementById("{cls._html_link_id}");
                elem.innerHTML = "";
                elem.style.color = "";
                elem.style.display = "none";
        """)


def main():
    # Remember if all 4 buttons are shown for the card.
    gui_hooks.reviewer_did_show_question.append(LastEase.set_last_default_ease)

    # When Reviewer is open, print the last card's stats on the top toolbar.
    gui_hooks.top_toolbar_did_init_links.append(LastEase.append_link)
    gui_hooks.reviewer_did_answer_card.append(LastEase.update)

    # Don't show the last card's stats when Reviewer is not open.
    gui_hooks.collection_did_load.append(LastEase.hide)
    gui_hooks.reviewer_will_end.append(LastEase.hide)
