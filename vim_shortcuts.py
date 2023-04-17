# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import functools
from typing import Callable, Literal, cast, Iterable

from anki.hooks import wrap
from aqt.reviewer import Reviewer

from .config import config
from .top_toolbar import LastEase


def answer_card(self: Reviewer, grade: str):
    try:
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


def new_shortcuts(self: Reviewer) -> list[tuple[str, Callable]]:
    return [
        *number_shortcuts(self),
        *[
            (config.get_key(answer), functools.partial(answer_card, self, grade=answer))
            for answer in enabled_answer_buttons()
        ],
        (config.get_key("undo"), self.mw.undo),
        (config.get_key("last_card"), LastEase.open_last_card),
    ]


def old_shortcuts(self: Reviewer, _old: Callable[[Reviewer], list]) -> list[tuple[str, Callable]]:
    # Filter out default number-keys.
    return [(key, func) for key, func in _old(self) if key not in ('1', '2', '3', '4',)]


def is_key_set(shortcut_key: tuple[str, Callable]) -> bool:
    return bool(shortcut_key[0])


def add_vim_shortcuts(self: Reviewer, _old: Callable[[Reviewer], list]) -> list[tuple[str, Callable]]:
    # Credit: https://ankiweb.net/shared/info/1197299782
    return list(dict([
        *old_shortcuts(self, _old),
        *filter(is_key_set, new_shortcuts(self)),
    ]).items())


def activate_vim_keys(self: Reviewer, ease: Literal[1, 2, 3, 4], _old: Callable) -> None:
    # Allows answering from the front side.
    # Reviewer._answerCard() is called when pressing default and configured keys.
    if config['flexible_grading'] is True and self.state == "question":
        self.state = "answer"

    # min() makes sure the original _answerCard() never skips
    _old(self, min(self.mw.col.sched.answerButtons(self.card), ease))


def disable_grading_with_space(self: Reviewer, _old: Callable) -> None:
    """
    By default, Anki will answer the card "Good" if Space or Enter are pressed.
    If enabled, don't do anything.
    """
    if config['disable_grading_with_space'] and self.state == "answer":
        return
    _old(self)


def main():
    # Add vim answer shortcuts
    # noinspection PyProtectedMember
    Reviewer._shortcutKeys = wrap(Reviewer._shortcutKeys, add_vim_shortcuts, "around")

    # Activate Vim shortcuts on the front side, if enabled by the user.
    # noinspection PyProtectedMember
    Reviewer._answerCard = wrap(Reviewer._answerCard, activate_vim_keys, "around")

    # Optionally disable grading with Space and Enter keys
    # noinspection PyProtectedMember
    Reviewer.onEnterKey = wrap(Reviewer.onEnterKey, disable_grading_with_space, "around")
