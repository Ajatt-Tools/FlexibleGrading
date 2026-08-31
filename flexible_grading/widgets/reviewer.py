# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import enum
import typing
from collections.abc import Mapping
from functools import partial
from typing import Any, Literal, Optional, Union, cast

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

from ..config import FlexibleGradingConfig, RemainingCountType
from ..consts import BOTTOM_WEB_CLEAR_HTML, EMPTY_PLACEHOLDER, STATES_MUTATED_RETRY_MS
from .utils import studied_today_count
from .widgets import FlexiblePushButton, FlexibleTimerLabel, get_flexible_bottom_bar

# Maps Anki queue types to their human-readable answer labels for coloring.
QUEUE_TO_LABEL: typing.Final[Mapping[int, str]] = {
    QueuedCards.NEW: "Easy",
    QueuedCards.LEARNING: "Again",
    QueuedCards.REVIEW: "Good",
}


class NoQueue(enum.Enum):
    """Sentinel indicating a summed count that does not correspond to any single Anki queue."""

    SENTINEL = enum.auto()


NO_QUEUE = NoQueue.SENTINEL


class FlexibleReviewer(Reviewer):
    """Card reviewer that renders answer buttons as native Qt widgets instead of HTML."""

    timer: FlexibleTimerLabel | None = None

    def __init__(self, mw: AnkiQt, config: FlexibleGradingConfig) -> None:
        """Initialize the flexible reviewer with the given config."""
        super().__init__(mw)
        self.timer = None
        self._config = config
        self._bar = get_flexible_bottom_bar()

    def cleanup(self) -> None:
        """Hide all bottom bar buckets when leaving the reviewer."""
        super().cleanup()
        self._bar.middle_bucket.reset(is_visible=False)
        self._bar.left_bucket.reset(is_visible=False)
        self._bar.right_bucket.reset(is_visible=False)

    def _bottomHTML(self) -> str:
        """Return minimal HTML since the bottom bar is rendered with native Qt widgets."""
        return "<style></style>"

    def _create_side_buttons(self) -> None:
        """Add the Edit button (left) and More button (right) to the bottom bar."""
        # Left side
        self._bar.left_bucket.reset(is_visible=True)
        self._bar.left_bucket.add_button(
            FlexiblePushButton(text=tr.studying_edit()),
            on_clicked=partial(self.mw.onEditCurrent),
        )
        # Right side
        self._bar.right_bucket.reset(is_visible=True)
        self._bar.right_bucket.add_button(
            FlexiblePushButton(text=tr.studying_more()),
            on_clicked=partial(self.showContextMenu),
        )

    def browse_queue(self, queue_type: int | NoQueue) -> None:
        """Open the card browser filtered to the given queue type."""
        if queue_type == QueuedCards.LEARNING:
            queue_type = "learn"
        elif queue_type == QueuedCards.NEW:
            queue_type = "new"
        else:
            queue_type = "due"
        self.browse_query(f"is:{queue_type}")

    def browse_query(self, query: str) -> None:
        """Open the card browser and execute the given search query."""
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
        """Populate the middle bucket with colored answer buttons (Again, Hard, Good, Easy)."""
        self._bar.middle_bucket.reset(is_visible=True)
        for ease, label in self._answerButtonList():
            self._bar.middle_bucket.add_button(
                FlexiblePushButton(
                    text=(
                        f"{self._answer_button_label(ease, label)}"
                        f"[{self._config.get_answer_key(ease, default_ease=self._defaultEase())}]"
                    ),
                    text_color=self._config.get_ease_color(ease, default_ease=self._defaultEase()),
                ),
                on_clicked=partial(self._answerCard, cast(Literal[1, 2, 3, 4], ease)),
            )

    def _get_counts(self) -> dict[int | NoQueue, int | str]:
        """Return remaining card counts keyed by queue type.

        The keys are QueuedCards int constants when showing per-queue counts,
        or NO_QUEUE when all queues are summed into a single number.
        """
        if self._config.remaining_count_type == RemainingCountType.none:
            return {
                QueuedCards.NEW: EMPTY_PLACEHOLDER,
                QueuedCards.LEARNING: EMPTY_PLACEHOLDER,
                QueuedCards.REVIEW: EMPTY_PLACEHOLDER,
            }
        elif self._config.remaining_count_type == RemainingCountType.single:
            return {
                NO_QUEUE: (
                    self._v3.queued_cards.new_count
                    + self._v3.queued_cards.learning_count
                    + self._v3.queued_cards.review_count
                ),
            }
        else:
            return {
                QueuedCards.NEW: self._v3.queued_cards.new_count,
                QueuedCards.LEARNING: self._v3.queued_cards.learning_count,
                QueuedCards.REVIEW: self._v3.queued_cards.review_count,
            }

    def _create_middle_buttons_for_question_side(self) -> None:
        """
        Show the number of remaining cards in three queues: New, Learning, Review.
        """
        self._bar.middle_bucket.reset(is_visible=True)

        if self.mw.col.conf["dueCounts"]:
            this_card = self._v3.top_card()
            for queue_type, button_text in self._get_counts().items():
                self._bar.middle_bucket.add_button(
                    FlexiblePushButton(
                        text=f"{button_text}",
                        text_color=self._config.get_label_color(QUEUE_TO_LABEL.get(queue_type, EMPTY_PLACEHOLDER)),
                        text_underline=(this_card.queue == queue_type),
                    ),
                    on_clicked=partial(self.browse_queue, queue_type),
                )

        # show reps done today
        if self._config.show_reps_done_today:
            assert self.mw.col, "collection should be available"
            self._bar.middle_bucket.add_button(
                FlexiblePushButton(text=f"Reps: {studied_today_count(self.mw.col)}"),
                on_clicked=partial(self.browse_query, "rated:1"),
            )

    def _clear_bottom_web(self) -> None:
        """Collapse the bottom web view so only the native Qt bar is visible."""
        self.bottom.web.setHtml(BOTTOM_WEB_CLEAR_HTML)

    def _max_time(self) -> int:
        """Return the card's time limit in seconds, or 0 if the timer is disabled."""
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
            self.timer = timer = self._bar.right_bucket.add_widget(widget=FlexibleTimerLabel())  # type: ignore
            timer.start(max_time=max_time)

    def _should_stop_timer_on_answer(self) -> bool:
        """Return True if the deck config says to stop the timer when an answer is shown."""
        conf = self.mw.col.decks.config_dict_for_deck_id(self.card.current_deck_id())
        return bool(conf["stopTimerOnAnswer"])

    def _showEaseButtons(self) -> None:
        """
        Show Back side (Answer side). Buttons: Again, Hard, Good, Easy
        """
        if not self._states_mutated:
            self.mw.progress.single_shot(STATES_MUTATED_RETRY_MS, self._showEaseButtons)
            return
        self._create_middle_buttons_for_answer_side()
        self._clear_bottom_web()

        if self.timer and self._should_stop_timer_on_answer():
            self.timer.stop()

    def onEnterKey(self) -> None:
        """Handle Enter/Space key: flip card on question side, answer on answer side."""
        if self.state == "question":
            self._getTypedAnswer()
        elif self.state == "answer" and aqt.mw.pm.spacebar_rates_card():
            self._answerCard(self._defaultEase())
