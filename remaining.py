import re
from typing import Callable
from .config import config
from anki.hooks import wrap
from aqt.reviewer import Reviewer


def strip_html_tags(s: str) -> str:
    return re.sub(r'<[^<>]+>', '', s, flags=re.IGNORECASE | re.MULTILINE)


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
    Reviewer._remaining = wrap(Reviewer._remaining, wrap_remaining, "around")
