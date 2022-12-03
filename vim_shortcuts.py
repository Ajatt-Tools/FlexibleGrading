# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from typing import Callable, Literal, cast, List, Tuple

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


def new_shortcuts(self: Reviewer) -> List[Tuple[str, Callable]]:
    return [
        ("h", lambda: answer_card(self, grade='again')),
        ("j", lambda: answer_card(self, grade='hard')),
        ("k", lambda: answer_card(self, grade='good')),
        ("l", lambda: answer_card(self, grade='easy')),

        ("1", lambda: answer_card(self, grade='again')),
        ("2", lambda: answer_card(self, grade='hard')),
        ("3", lambda: answer_card(self, grade='good')),
        ("4", lambda: answer_card(self, grade='easy')),

        ("u", self.mw.undo),
        (":", LastEase.open_last_card),
    ]


def old_shortcuts(self: Reviewer, _old: Callable[[Reviewer], List]) -> List[Tuple[str, Callable]]:
    return [(k, v) for k, v in _old(self) if k not in ('1', '2', '3', '4',)]


def add_vim_shortcuts(self: Reviewer, _old: Callable[[Reviewer], List]) -> List[Tuple[str, Callable]]:
    # Credit: https://ankiweb.net/shared/info/1197299782
    shortcuts = list(dict([*old_shortcuts(self, _old), *new_shortcuts(self)]).items())

    if config['pass_fail'] is True:
        # PassFail mode. Pressing 'Hard' and 'Easy' is not allowed.
        return [(k, v) for k, v in shortcuts if k not in ('j', 'l', '2', '4',)]
    else:
        return shortcuts


def main():
    # Add vim answer shortcuts
    Reviewer._shortcutKeys = wrap(Reviewer._shortcutKeys, add_vim_shortcuts, "around")
