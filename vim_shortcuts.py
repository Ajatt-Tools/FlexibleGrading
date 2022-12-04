# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import functools
from typing import Callable, Literal, cast, List, Tuple, Iterable

from anki.hooks import wrap
from aqt.reviewer import Reviewer

from .config import config
from .toolbar import LastEase


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


def new_shortcuts(self: Reviewer) -> List[Tuple[str, Callable]]:
    return [
        *number_shortcuts(self),
        *[
            (config.get_key(answer), functools.partial(answer_card, self, grade=answer))
            for answer in enabled_answer_buttons()
        ],
        (config.get_key("undo"), self.mw.undo),
        (config.get_key("last_card"), LastEase.open_last_card),
    ]


def old_shortcuts(self: Reviewer, _old: Callable[[Reviewer], List]) -> List[Tuple[str, Callable]]:
    # Filter out default number-keys.
    return [(key, func) for key, func in _old(self) if key not in ('1', '2', '3', '4',)]


def is_key_set(shortcut_key: Tuple[str, Callable]) -> bool:
    return bool(shortcut_key[0])


def add_vim_shortcuts(self: Reviewer, _old: Callable[[Reviewer], List]) -> List[Tuple[str, Callable]]:
    # Credit: https://ankiweb.net/shared/info/1197299782
    return list(dict([
        *old_shortcuts(self, _old),
        *filter(is_key_set, new_shortcuts(self)),
    ]).items())


def main():
    # Add vim answer shortcuts
    # noinspection PyProtectedMember
    Reviewer._shortcutKeys = wrap(Reviewer._shortcutKeys, add_vim_shortcuts, "around")
