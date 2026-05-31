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
    def add_bottom_buttons(self) -> None:
        bar = get_flexible_bottom_bar()
        bar.left_bucket.reset(is_visible=False)
        bar.right_bucket.reset(is_visible=False)
        bar.middle_bucket.reset(is_visible=True)

        draw_links = deepcopy(self.drawLinks)
        pycmds = {
            "shared": self._onShared,
            "create": self._on_create,
            "import": self.mw.onImport,
        }
        for keyboard_shortcut, pycmd, button_text in draw_links:
            button = bar.middle_bucket.add_button(
                FlexiblePushButton(text=button_text),
                on_clicked=functools.partial(pycmds[pycmd]),
            )
            if keyboard_shortcut:
                button.setToolTip(tr.actions_shortcut_key(val=shortcut(keyboard_shortcut)))

    def _clear_bottom_web(self) -> None:
        self.bottom.web.setHtml(BOTTOM_WEB_CLEAR_HTML)

    def _drawButtons(self) -> None:
        self._clear_bottom_web()
        self.add_bottom_buttons()
