# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import json
import re
from typing import Callable

from anki.cards import Card
from anki.hooks import wrap
from aqt import gui_hooks, tr
from aqt.reviewer import Reviewer

from .config import config

_ans_buttons_default = Reviewer._answerButtons


def only_pass_fail(buttons: tuple, default_ease: int) -> tuple[tuple[int, str], ...]:
    def is_again_or_good(ease: int, _label: str) -> bool:
        return ease in (1, default_ease)

    return tuple(button for button in buttons if is_again_or_good(*button))


def apply_label_colors(buttons: tuple, default_ease: int) -> tuple[tuple[int, str], ...]:
    def color_label(ease: int, label: str) -> tuple[int, str]:
        return ease, f"<font color=\"{config.get_color(ease, default_ease)}\">{label}</font>"

    return tuple(color_label(*button) for button in buttons)


def filter_answer_buttons(buttons: tuple, self: Reviewer, _: Card) -> tuple[tuple[int, str], ...]:
    # Called by _answerButtonList, before _answerButtons gets called
    if config['pass_fail'] is True:
        buttons = only_pass_fail(buttons, self._defaultEase())

    if config['color_buttons'] is True:
        buttons = apply_label_colors(buttons, self._defaultEase())

    return buttons


def make_stat_txt(self: Reviewer):
    def _padding_top():
        return '5px' if config['remove_buttons'] is True else '4px'

    return f'<div style="padding: {_padding_top()} 5px 0px;">{self._remaining()}</div>'


def get_ease_row_css() -> str:
    return """
    <style>
    .ease_row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        max-width: 450px;
        min-width: 200px;
        user-select: none;
        margin-inline: auto;
    }
    .ease_row > div {
        padding-top: 1px;
    }
    </style>
    """


def button_time(self: Reviewer, ease: int) -> str:
    if config['color_buttons'] is True:
        return f'<div style="color: {config.get_color(ease, self._defaultEase())};">{self._buttonTime(ease)}</div>'
    else:
        return f'<div>{self._buttonTime(ease)}</div>'


def make_buttonless_ease_row(self: Reviewer, front: bool = False) -> str:
    """Returns ease row html when config.remove_buttons is true"""

    if front is True and config['flexible_grading'] is False:
        return make_stat_txt(self)
    else:
        ease_row = []
        ans_buttons = self._answerButtonList()

        for idx, (ease, _label) in enumerate(ans_buttons):
            if front and idx == len(ans_buttons) // 2:
                ease_row.append(make_stat_txt(self))
            ease_row.append(button_time(self, ease))

        return get_ease_row_css() + f'<div class="ease_row">{"".join(ease_row)}</div>'


def disable_buttons(html: str) -> str:
    return html.replace('<button', '<button disabled')


def make_backside_answer_buttons(self: Reviewer, _old: Callable) -> str:
    if config['remove_buttons'] is True:
        return make_buttonless_ease_row(self)
    elif config['prevent_clicks'] is True:
        return disable_buttons(_old(self))
    else:
        return _old(self)


def make_show_ans_table_cell(self: Reviewer):
    """Creates html code with a table data-cell holding the "Show answer" button."""
    def make_show_ans_button() -> str:
        """Copypasted from Reviewer._showAnswerButton, removed id to fix margin-bottom."""
        return """
        <button title="{}" onclick='pycmd("ans");'>{}<span class=stattxt>{}</span></button>
        """.format(
            tr.actions_shortcut_key(val=tr.studying_space()),
            tr.studying_show_answer(),
            self._remaining(),
        )

    return f'<td align=center>{make_show_ans_button()}</td>'


def fix_spacer_padding(html: str) -> str:
    return '<style>.spacer{padding-top: 4px;}</style>' + html


def calc_middle_insert_pos(buttons_html_table: str) -> int:
    cell_positions = [m.start() for m in re.finditer(r'<td', buttons_html_table)]
    return cell_positions[:len(cell_positions) // 2 + 1][-1]


def make_flexible_front_row(self: Reviewer) -> str:
    ans_buttons = _ans_buttons_default(self)
    insert_pos = calc_middle_insert_pos(ans_buttons)
    html = ans_buttons[:insert_pos] + make_show_ans_table_cell(self) + ans_buttons[insert_pos:]
    if not self.mw.col.conf["estTimes"]:
        # If Prefs > Scheduling > Show next review time is False
        # Move answer buttons down a bit.
        html = fix_spacer_padding(html)
    return html


def make_frontside_answer_buttons(self: Reviewer) -> None:
    html = None
    if config['remove_buttons'] is True:
        html = make_buttonless_ease_row(self, front=True)
    elif config['flexible_grading'] is True:
        html = make_flexible_front_row(self)
        if config['prevent_clicks'] is True:
            html = disable_buttons(html)
    if html is not None:
        self.bottom.web.eval("showAnswer(%s);" % json.dumps(html))
        self.bottom.web.adjustHeightToFit()


def main():
    # (*) Create html layout for the answer buttons on the back side.
    # Buttons are either removed, disabled or left unchanged depending on config options.
    # noinspection PyProtectedMember
    Reviewer._answerButtons = wrap(Reviewer._answerButtons, make_backside_answer_buttons, "around")

    # Wrap front side button(s).
    # noinspection PyProtectedMember
    Reviewer._showAnswerButton = wrap(Reviewer._showAnswerButton, make_frontside_answer_buttons, "after")

    # Edit (ease, label) tuples which are used to create answer buttons.
    # If `color_buttons` is true, labels are colored.
    # If `pass_fail` is true, "Hard" and "Easy" buttons are removed.
    # This func gets called inside _answerButtonList, which itself gets called inside _answerButtons (*)
    gui_hooks.reviewer_will_init_answer_buttons.append(filter_answer_buttons)
