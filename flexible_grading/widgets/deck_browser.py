# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from copy import deepcopy

from aqt.deckbrowser import DeckBrowser


class FlexibleDeckBrowser(DeckBrowser):
    """
    Adds *Flexible Grading* features to Anki as a separate Reviewer.
    The idea is that Anki can have many Reviewer classes, and the user can choose which they prefer.

    Initially, Flexible Grading was implemented as an add-on.
    However, add-ons require patching every time Anki introduces a change that breaks add-on compatibility.
    Thus, it proves better to add new features directly to Anki.
    """

    def add_bottom_buttons(self) -> None:
        self.mw.bottomWidget.left_bucket.reset(is_visible=False)
        self.mw.bottomWidget.right_bucket.reset(is_visible=False)
        self.mw.bottomWidget.middle_bucket.reset(is_visible=True)

        draw_links = deepcopy(self.drawLinks)
        pycmds = {
            "shared": self._onShared,
            "create": self._on_create,
            "import": self.mw.onImport,
        }
        for keyboard_shortcut, pycmd, button_text in draw_links:
            button = self.mw.bottomWidget.middle_bucket.add_button(
                FlexiblePushButton(text=button_text),
                on_clicked=functools.partial(pycmds[pycmd]),
            )
            if keyboard_shortcut:
                button.setToolTip(
                    tr.actions_shortcut_key(val=shortcut(keyboard_shortcut))
                )

    def _clear_bottom_web(self) -> None:
        self.bottom.web.setHtml("<style>body {margin:0;} html {height:0;}</style>")

    def _drawButtons(self) -> None:
        self._clear_bottom_web()
        self.add_bottom_buttons()
