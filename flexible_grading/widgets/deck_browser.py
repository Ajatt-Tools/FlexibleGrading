# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import functools
from copy import deepcopy

from aqt import tr
from aqt.deckbrowser import DeckBrowser
from aqt.utils import shortcut

from ..consts import BOTTOM_WEB_CLEAR_HTML
from .widgets import FlexiblePushButton, get_flexible_bottom_bar


class FlexibleDeckBrowser(DeckBrowser):
    """Deck browser that uses native Qt buttons instead of the bottom web view."""

    def add_bottom_buttons(self) -> None:
        """Populate the flexible bottom bar with deck browser action buttons."""
        bar = get_flexible_bottom_bar()
        bar.left_bucket.reset(is_visible=False)
        bar.right_bucket.reset(is_visible=False)
        bar.middle_bucket.reset(is_visible=True)

        for keyboard_shortcut, pycmd, button_text in deepcopy(self.drawLinks):
            button = bar.middle_bucket.add_button(
                FlexiblePushButton(text=button_text),
                on_clicked=functools.partial(self._linkHandler, pycmd),
            )
            if keyboard_shortcut:
                button.setToolTip(tr.actions_shortcut_key(val=shortcut(keyboard_shortcut)))

    def _clear_bottom_web(self) -> None:
        """Collapse the bottom web view so only the native Qt bar is visible."""
        self.bottom.web.setHtml(BOTTOM_WEB_CLEAR_HTML)

    def _drawButtons(self) -> None:
        """Override the default button drawing to use native Qt widgets."""
        self._clear_bottom_web()
        self.add_bottom_buttons()
