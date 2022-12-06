# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import re
from typing import Callable

from anki.hooks import wrap
from aqt.reviewer import Reviewer

from .config import config

HTML_TAG = re.compile(r'<[^<>]+>', flags=re.IGNORECASE | re.MULTILINE)


def strip_html_tags(s: str) -> str:
    return re.sub(HTML_TAG, '', s)


def wrap_remaining(self: Reviewer, _old: Callable[[Reviewer], str]):
    if config["hide_card_type"] is True:
        html = _old(self)
        html = strip_html_tags(html)
        numbers = html.split('+')
        result = sum(int(n.strip()) for n in numbers)
        return f'<span class="total-count">Left: {result}</span>'
    else:
        return _old(self)


def init():
    # noinspection PyProtectedMember
    Reviewer._remaining = wrap(Reviewer._remaining, wrap_remaining, "around")
