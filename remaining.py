# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import re
from typing import Callable, Optional

from anki.collection import Collection
from anki.consts import REVLOG_RESCHED
from anki.hooks import wrap
from aqt.reviewer import Reviewer

from .config import RemainingCountType, config

HTML_TAG = re.compile(r"<[^<>]+>", flags=re.IGNORECASE | re.MULTILINE)


def strip_html_tags(s: str) -> str:
    return re.sub(HTML_TAG, "", s)


def to_number(s: str) -> Optional[int]:
    try:
        return int(s.strip())
    except ValueError:
        return None


def sum_remaining(html: str) -> int:
    return sum(n for split in strip_html_tags(html).split("+") if (n := to_number(split)) is not None)


def format_remaining_cards(self: Reviewer, get_default_html: Callable[[Reviewer], str]):
    if config.remaining_count_type == RemainingCountType.none:
        return ""
    elif config.remaining_count_type == RemainingCountType.single:
        return f'<span class="ajt__total-count">Left: {sum_remaining(get_default_html(self))}</span>'
    else:
        return get_default_html(self).strip()


def prev_day_cutoff_ms(col: Collection) -> int:
    return (col.sched.day_cutoff - 86_400) * 1000


def studied_today_count(col: Collection) -> int:
    return col.db.scalar(
        """ SELECT COUNT(*) FROM revlog WHERE type != ? AND id > ? """,
        REVLOG_RESCHED,
        prev_day_cutoff_ms(col),
    )


def format_studied_today(col: Collection) -> str:
    return f'<span class="ajt__studied-today">Reps: {studied_today_count(col)}</span>'


def wrap_remaining(self: Reviewer, _old: Callable[[Reviewer], str]) -> str:
    return format_remaining_cards(self, _old) + format_studied_today(self.mw.col)


def init():
    # noinspection PyProtectedMember
    Reviewer._remaining = wrap(Reviewer._remaining, wrap_remaining, "around")
