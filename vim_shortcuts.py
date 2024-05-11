# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import functools
from collections.abc import Iterable
from typing import Callable, Literal, cast

from anki.hooks import wrap
from aqt import gui_hooks, mw
from aqt.main import MainWindowState
from aqt.reviewer import Reviewer

from .config import config
from .top_toolbar import LastEase


def answer_card(self: Reviewer, grade: str):
    try:
        if (
                self.state == "question"
                and grade
                and config["press_answer_key_to_flip_card"] is True
        ):
            return self._getTypedAnswer()
        if grade == 'again':
            return self._answerCard(1)
        if grade == 'hard' and self._defaultEase() == 3:
            return self._answerCard(2)
        if grade == 'good':
            return self._answerCard(self._defaultEase())
        if grade == 'easy':
            return self._answerCard(cast(Literal[3, 4], self._defaultEase() + 1))
    except IndexError as e:
        raise RuntimeError("Flexible grading error: Couldn't answer card due to a bug in Anki.") from e


def enabled_answer_buttons() -> Iterable[str]:
    # In PassFail mode pressing 'Hard' and 'Easy' is not allowed.
    return ('again', 'good') if config['pass_fail'] is True else ('again', 'hard', 'good', 'easy')


def enabled_number_keys() -> Iterable[str]:
    # In PassFail mode pressing 'Hard' and 'Easy' is not allowed.
    return ('1', '3') if config['pass_fail'] is True else ('1', '2', '3', '4')


def number_shortcuts(self: Reviewer):
    return [
        (key, func)
        for key, func
        in [
            ("1", lambda: answer_card(self, grade='again')),
            ("2", lambda: answer_card(self, grade='hard')),
            ("3", lambda: answer_card(self, grade='good')),
            ("4", lambda: answer_card(self, grade='easy')),
        ]
        if key in enabled_number_keys()
    ]


def scroll_webpage(self: Reviewer, amount_hor: int = 0, amount_vert: int = 0) -> None:
    self.web.eval(f"  window.scrollBy({amount_hor}, {amount_vert});  ")


def new_shortcuts(self: Reviewer) -> list[tuple[str, Callable]]:
    return [
        *number_shortcuts(self),
        *[
            (config.get_key(answer), functools.partial(answer_card, self, grade=answer))
            for answer in enabled_answer_buttons()
        ],
        (config.get_key("undo"), self.mw.undo),
        (config.get_key("last_card"), LastEase.open_last_card),
        ("Shift+k", functools.partial(scroll_webpage, self=self, amount_vert=-100)),
        ("Shift+j", functools.partial(scroll_webpage, self=self, amount_vert=100)),
        ("Shift+h", functools.partial(scroll_webpage, self=self, amount_hor=-100)),
        ("Shift+l", functools.partial(scroll_webpage, self=self, amount_hor=100)),
    ]


def is_not_ease_key(shortcut: tuple[str, Callable]) -> bool:
    """ Filter out all keys that are used to rate cards by default. """
    return bool(shortcut[0] not in ('1', '2', '3', '4', 'h', 'j', 'k', 'l',))


def is_key_set(shortcut: tuple[str, Callable]) -> bool:
    return bool(shortcut[0])


def add_vim_shortcuts(state: MainWindowState, shortcuts: list[tuple[str, Callable]]) -> None:
    if state != "review":
        return
    # Reviewer shortcuts are defined in Reviewer._shortcutKeys
    default_shortcuts = shortcuts.copy()
    shortcuts.clear()
    shortcuts.extend(dict([
        *filter(is_not_ease_key, default_shortcuts),
        *filter(is_key_set, new_shortcuts(mw.reviewer)),
    ]).items())


def activate_vim_keys(self: Reviewer, ease: Literal[1, 2, 3, 4], _old: Callable) -> None:
    # Allows answering from the front side.
    # Reviewer._answerCard() is called when pressing default and configured keys.
    if config['flexible_grading'] is True and self.state == "question":
        self.state = "answer"

    # min() makes sure the original _answerCard() never skips
    _old(self, min(self.mw.col.sched.answerButtons(self.card), ease))


def main():
    # Add vim answer shortcuts
    gui_hooks.state_shortcuts_will_change.append(add_vim_shortcuts)

    # Activate Vim shortcuts on the front side, if enabled by the user.
    # noinspection PyProtectedMember
    Reviewer._answerCard = wrap(Reviewer._answerCard, activate_vim_keys, "around")
