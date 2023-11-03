# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import time
from gettext import gettext as _

import aqt
from anki.cards import Card
from aqt import mw, gui_hooks
from aqt.reviewer import Reviewer
from aqt.toolbar import Toolbar

from .config import config


def handle_due(card: Card) -> str:
    days = card.ivl
    months = days / (365 / 12)
    years = days / 365
    if years >= 1:
        return f"{years:.2f}y"
    elif months >= 1:
        return f"{months:.2f}mo"
    else:
        return f"{days:.0f}d"


def handle_learn(card: Card) -> str:
    minutes = (card.due - time.time()) / 60
    hours = minutes / 60
    if minutes < 0:
        return "unknown"
    elif hours >= 1:
        return f"{hours:.1f}h"
    else:
        return f"{minutes:.0f}m"


def human_ivl(card: Card) -> str:
    # https://github.com/ankidroid/Anki-Android/wiki/Database-Structure

    if card.queue <= -2:
        return "buried"
    elif card.queue == -1:
        return "suspended"
    elif card.queue == 1 and (card.type == 3 or card.type == 1):
        return handle_learn(card)
    elif card.queue == 3 and (card.type == 3 or card.type == 1):
        return "tomorrow"
    elif card.queue == 4:
        return "preview"
    elif card.type == 2:
        return handle_due(card)
    else:
        return "unknown"


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
        """Called after a card was answered."""
        if config['show_last_review'] is False:
            return

        label = config.get_label(ease, cls._last_default_ease)
        color = config.get_color(label)
        status = f"{_(label)[:1]}: {human_ivl(card)}"

        reviewer.mw.toolbar.web.eval("""\
        {{
            const elem = document.getElementById("{}");
            elem.innerHTML = "{}";
            elem.style.color = "{}";
            elem.style.display = "inline";
        }};
        """.format(cls._html_link_id, status, color))

        cls._browser_query = f"cid:{card.id}"

    @classmethod
    def hide(cls, _=None) -> None:
        mw.toolbar.web.eval("""\
        {
            const elem = document.getElementById("%s");
            elem.innerHTML = "";
            elem.style.color = "";
            elem.style.display = "none";
        };
        """ % cls._html_link_id)


def main():
    # Remember if all 4 buttons are shown for the card.
    gui_hooks.reviewer_did_show_question.append(LastEase.set_last_default_ease)

    # When Reviewer is open, print the last card's stats on the top toolbar.
    gui_hooks.top_toolbar_did_init_links.append(LastEase.append_link)
    gui_hooks.reviewer_did_answer_card.append(LastEase.update)

    # Don't show the last card's stats when Reviewer is not open.
    gui_hooks.collection_did_load.append(LastEase.hide)
    gui_hooks.reviewer_will_end.append(LastEase.hide)
