# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from functools import partial
from functools import partial
from typing import Any, Literal, Optional, cast

import aqt
import aqt.browser
import aqt.operations
from anki.scheduler.v3 import (
    QueuedCards,
)
from anki.scheduler.v3 import Scheduler as V3Scheduler
from anki.utils import html_to_text_line
from aqt import AnkiQt
from aqt.qt import *
from aqt.reviewer import Reviewer
from aqt.utils import (
    tr,
)

from flexible_grading.widgets.utils import ease_to_answer_key_short, studied_today_count
from flexible_grading.widgets.widgets import FlexibleTimerLabel, FlexiblePushButton


class FlexibleReviewer(Reviewer):
    """
    Adds *Flexible Grading* features to Anki as a separate Reviewer.
    The idea is that Anki can have many Reviewer classes, and the user can choose which they prefer.

    Initially, Flexible Grading was implemented as an add-on.
    However, add-ons require patching every time Anki introduces a change that breaks add-on compatibility.
    Thus, it proves better to add new features directly to Anki.
    """

    _ease_to_color = {
        1: "FireBrick",
        2: "DarkGoldenRod",
        3: "ForestGreen",
        4: "DodgerBlue",
    }
    _queue_to_color = {
        QueuedCards.NEW: "DodgerBlue",
        QueuedCards.LEARNING: "FireBrick",
        QueuedCards.REVIEW: "ForestGreen",
    }

    timer: Optional[FlexibleTimerLabel] = None

    def __init__(self, mw: AnkiQt) -> None:
        super().__init__(mw)
        self.timer = None

    def cleanup(self) -> None:
        super().cleanup()
        self.mw.bottomWidget.middle_bucket.reset(is_visible=False)
        self.mw.bottomWidget.left_bucket.reset(is_visible=False)
        self.mw.bottomWidget.right_bucket.reset(is_visible=False)

    def _bottomHTML(self) -> str:
        return "<style></style>"

    def _create_side_buttons(self) -> None:
        # Left side
        self.mw.bottomWidget.left_bucket.reset(is_visible=True)
        self.mw.bottomWidget.left_bucket.add_button(
            FlexiblePushButton(text=tr.studying_edit()),
            on_clicked=partial(self.mw.onEditCurrent),
        )
        # Right side
        self.mw.bottomWidget.right_bucket.reset(is_visible=True)
        self.mw.bottomWidget.right_bucket.add_button(
            FlexiblePushButton(text=tr.studying_more()),
            on_clicked=partial(self.showContextMenu),
        )

    def browse_queue(self, queue_type: Union[str, Any]) -> None:
        if queue_type == QueuedCards.LEARNING:
            queue_type = "learn"
        elif queue_type == QueuedCards.NEW:
            queue_type = "new"
        else:
            queue_type = "due"
        self.browse_query(f"is:{queue_type}")

    def browse_query(self, query: str) -> None:
        browser: aqt.browser.Browser = aqt.dialogs.open("Browser", self.mw)
        browser.activateWindow()
        browser.form.searchEdit.lineEdit().setText(query)  # search_for
        if hasattr(browser, "onSearch"):
            browser.onSearch()
        else:
            browser.onSearchActivated()

    def _answer_button_label(self, ease: int, label: str) -> str:
        """
        If estTimes (showEstimates) are enabled, return the estimate as string.
        Otherwise, return the first letter of the text label.
        """
        if self.mw.col.conf["estTimes"]:
            assert isinstance(self.mw.col.sched, V3Scheduler)
            button_times = self.mw.col.sched.describe_next_states(self._v3.states)
            return button_times[ease - 1]
        else:
            return html_to_text_line(label)[:1].upper()

    def _create_middle_buttons_for_answer_side(self) -> None:
        self.mw.bottomWidget.middle_bucket.reset(is_visible=True)
        for ease, label in self._answerButtonList():
            self.mw.bottomWidget.middle_bucket.add_button(
                FlexiblePushButton(
                    text=f"{self._answer_button_label(ease, label)}[{ease_to_answer_key_short(ease)}]",
                    text_color=self._ease_to_color[ease],
                ),
                on_clicked=partial(self._answerCard, cast(Literal[1, 2, 3, 4], ease)),
            )

    def _create_middle_buttons_for_question_side(self) -> None:
        """
        Show the number of remaining cards in three queues: New, Learning, Review.
        """
        self.mw.bottomWidget.middle_bucket.reset(is_visible=True)

        if self.mw.col.conf["dueCounts"]:
            counts = {
                QueuedCards.NEW: self._v3.queued_cards.new_count,
                QueuedCards.LEARNING: self._v3.queued_cards.learning_count,
                QueuedCards.REVIEW: self._v3.queued_cards.review_count,
            }
            this_card = self._v3.top_card()
            for queue_type, count in counts.items():
                self.mw.bottomWidget.middle_bucket.add_button(
                    FlexiblePushButton(
                        text=f"{count}",
                        text_color=self._queue_to_color[queue_type],
                        text_underline=(this_card.queue == queue_type),
                    ),
                    on_clicked=partial(self.browse_queue, queue_type),
                )

        # show reps done today
        if self.mw.pm.reviewer_show_reps_done_today():
            self.mw.bottomWidget.middle_bucket.add_button(
                FlexiblePushButton(text=f"Reps: {studied_today_count(self.mw.col)}"),
                on_clicked=partial(self.browse_query, "rated:1"),
            )

    def _clear_bottom_web(self) -> None:
        self.bottom.web.setHtml("<style>body {margin:0;} html {height:0;}</style>")

    def _max_time(self) -> int:
        if self.card.should_show_timer():
            return self.card.time_limit() // 1000
        else:
            return 0

    def _showAnswerButton(self) -> None:
        """
        Show Front side (Question side). Button: Flip card
        """
        self._create_side_buttons()
        self._create_middle_buttons_for_question_side()
        self._clear_bottom_web()

        # Right side: add timer
        if (max_time := self._max_time()) > 0:
            self.timer = self.mw.bottomWidget.right_bucket.add_widget(
                widget=FlexibleTimerLabel()
            )  # type: ignore
            self.timer.start(max_time=max_time)

    def _should_stop_timer_on_answer(self) -> bool:
        conf = self.mw.col.decks.config_dict_for_deck_id(self.card.current_deck_id())
        return bool(conf["stopTimerOnAnswer"])

    def _showEaseButtons(self) -> None:
        """
        Show Back side (Answer side). Buttons: Again, Hard, Good, Easy
        """
        if not self._states_mutated:
            self.mw.progress.single_shot(50, self._showEaseButtons)
            return
        self._create_middle_buttons_for_answer_side()
        self._clear_bottom_web()

        if self.timer and self._should_stop_timer_on_answer():
            self.timer.stop()

    def onEnterKey(self) -> None:
        if self.state == "question":
            self._getTypedAnswer()
        elif self.state == "answer" and aqt.mw.pm.spacebar_rates_card():
            self._answerCard(self._defaultEase())
