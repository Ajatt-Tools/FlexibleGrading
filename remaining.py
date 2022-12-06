# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import re
from typing import Callable, Optional

from anki.hooks import wrap
from aqt.reviewer import Reviewer

from .config import config

HTML_TAG = re.compile(r'<[^<>]+>', flags=re.IGNORECASE | re.MULTILINE)


def strip_html_tags(s: str) -> str:
    return re.sub(HTML_TAG, '', s)


def to_number(s: str) -> Optional[int]:
    try:
        return int(s.strip())
    except ValueError:
        return None


def sum_remaining(html: str) -> int:
    return sum(n for split in strip_html_tags(html).split('+') if (n := to_number(split)) is not None)


def wrap_remaining(self: Reviewer, _old: Callable[[Reviewer], str]):
    if config["hide_card_type"] is True:
        return f'<span class="total-count">Left: {sum_remaining(_old(self))}</span>'
    else:
        return _old(self)


def init():
    # noinspection PyProtectedMember
    Reviewer._remaining = wrap(Reviewer._remaining, wrap_remaining, "around")
