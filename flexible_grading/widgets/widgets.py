# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import functools
from typing import Optional

import aqt
from aqt import mw
from aqt.qt import *

from ..consts import (
    DEFAULT_TEXT_COLOR,
    FLEXIBLE_BUTTON_FONT_FAMILY,
    FLEXIBLE_BUTTON_FONT_SIZE,
    FLEXIBLE_BUTTON_HEIGHT,
    FLEXIBLE_BUTTON_STYLESHEET,
    FLEXIBLE_BUTTONS_SPACING,
    HOVER_BG_COLOR,
    PRESSED_BG_COLOR,
    TIMER_EXPIRED_COLOR,
    TIMER_INTERVAL_MS,
)
from .utils import clear_layout


class FlexiblePushButton(QPushButton):
    """A compact, flat push button styled with a monospace font for the bottom bar."""

    _height: int = FLEXIBLE_BUTTON_HEIGHT
    _font_size: int = FLEXIBLE_BUTTON_FONT_SIZE

    def __init__(
        self,
        text: str = "",
        *,
        text_color: str = DEFAULT_TEXT_COLOR,
        text_underline: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(text, parent)
        # Fixed height 16px, let width be flexible
        self.setFixedHeight(self._height)
        # Remove extra spacing from focus/contents margins
        self.setContentsMargins(0, 0, 0, 0)
        self.set_text_style(text_color, text_underline)
        # Optional: ensure compact size hint
        self.setSizePolicy(
            self.sizePolicy().horizontalPolicy(),
            self.sizePolicy().Policy.Fixed,
        )

    def set_text_style(self, text_color: str = DEFAULT_TEXT_COLOR, text_underline: bool = False) -> None:
        """Apply color, underline, and font styling via a Qt stylesheet."""
        self.setStyleSheet(
            FLEXIBLE_BUTTON_STYLESHEET.format(
                text_color=text_color,
                font_size=self._font_size,
                font_family=FLEXIBLE_BUTTON_FONT_FAMILY,
                underline_rule="text-decoration: underline;" if text_underline else "",
                hover_bg=HOVER_BG_COLOR,
                pressed_bg=PRESSED_BG_COLOR,
            )
        )

    def sizeHint(self) -> QSize:
        """
        Ensure sizeHint respects fixed height and minimal width
        """
        hint = super().sizeHint()
        return QSize(max(hint.width(), 0), self._height)


class FlexibleHorizontalBar(QWidget):
    """
    A simple bucket-like widget that holds other widgets and places them in a horizontal line.
    """

    _height: int = 16
    _spacing: int = 0

    mw: aqt.AnkiQt

    def __init__(self, mw: aqt.AnkiQt) -> None:
        super().__init__(mw)
        self.mw = mw
        # Setup Layout
        self._layout = QHBoxLayout()
        self.setLayout(self._layout)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(self._spacing)
        self.setMaximumHeight(self._height)

    def add_stretch(self, stretch_value: int = 1) -> None:
        self._layout.addStretch(stretch_value)

    def add_widget(self, widget: QWidget) -> QWidget:
        self._layout.addWidget(widget)
        return widget

    def add_button(self, button: QPushButton, *, on_clicked: Callable) -> QPushButton:
        self.add_widget(button)
        qconnect(button.clicked, lambda button_checked=False: on_clicked())
        return button

    def clear_layout(self) -> None:
        clear_layout(self._layout)

    def reset(self, is_visible: bool) -> None:
        """
        Prepare to show a new set of buttons.
        """
        self.setHidden(not is_visible)
        self.clear_layout()


class FlexibleButtonsList(FlexibleHorizontalBar):
    _spacing: int = 8


class FlexibleBottomBar(FlexibleHorizontalBar):
    """
    Bottom bar. Shows answer buttons, answer timer, reps done today.
    """

    def __init__(self, mw: aqt.AnkiQt) -> None:
        super().__init__(mw)
        # Setup Buttons
        self.left_bucket = FlexibleButtonsList(self.mw)
        self.middle_bucket = FlexibleButtonsList(self.mw)
        self.right_bucket = FlexibleButtonsList(self.mw)
        # Setup UI
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.add_widget(self.left_bucket)
        self.add_stretch()
        self.add_widget(self.middle_bucket)
        self.add_stretch()
        self.add_widget(self.right_bucket)


class FlexibleTimerLabel(QLabel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._time = 0  # current time (seconds)
        self._max_time = 0  # maximum time (seconds); 0 means unset
        self._qtimer = QTimer(self)
        self._qtimer.setInterval(1000)
        qconnect(self._qtimer.timeout, self._on_tick)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def start(self, max_time: int) -> None:
        if max_time <= 0:
            raise ValueError("max time should be greater than 0")
        self._max_time = max_time
        self._time = 0
        self._update_display()
        if self._qtimer.isActive():
            self._qtimer.stop()
        self._qtimer.start()

    def stop(self) -> None:
        if self._qtimer.isActive():
            self._qtimer.stop()

    def _on_tick(self) -> None:
        self._time = min(self._time + 1, self._max_time)
        self._update_display()

    def _update_display(self) -> None:
        if self._max_time <= 0:
            raise ValueError("max time should be greater than 0")

        t = min(self._max_time, self._time)
        m, s = divmod(t, 60)
        s_str = f"{s:02d}"
        time_string = f"{m}:{s_str}"

        if t >= self._max_time > 0:
            self.setText(f"<font color='red'>{time_string}</font>")
            self.stop()
        else:
            self.setText(time_string)


def get_flexible_bottom_bar() -> FlexibleBottomBar:
    assert mw, "mw should be available"

    try:
        return mw.ajt__flexible_bottom_bar
    except AttributeError:
        mw.ajt__flexible_bottom_bar = bar = FlexibleBottomBar(mw)
        mw.mainLayout.addWidget(bar)
        return bar
