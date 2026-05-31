# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import functools

from aqt import tr
from aqt.deckoptions import display_options_for_deck
from aqt.overview import Overview
from aqt.utils import shortcut

from ..consts import BOTTOM_WEB_CLEAR_HTML
from .widgets import FlexiblePushButton, get_flexible_bottom_bar


class FlexibleOverview(Overview):
    def add_bottom_buttons(self) -> None:
        bar = get_flexible_bottom_bar()
        bar.left_bucket.reset(is_visible=False)
        bar.right_bucket.reset(is_visible=False)
        bar.middle_bucket.reset(is_visible=True)

        links = self._make_bottom_links()
        pycmds = {
            "opts": lambda: display_options_for_deck(self.mw.col.decks.current()),
            "refresh": lambda: self.rebuild_current_filtered_deck(),
            "empty": lambda: self.empty_current_filtered_deck(),
            "studymore": lambda: self.onStudyMore(),
            "unbury": lambda: self.on_unbury(),
            "description": lambda: self.edit_description(),
        }
        for keyboard_shortcut, pycmd, button_text in links:
            if len(keyboard_shortcut) == 1:
                # if shortcut is one letter
                button_text += f"[{keyboard_shortcut}]"
            button = bar.middle_bucket.add_button(
                FlexiblePushButton(text=button_text),
                on_clicked=functools.partial(pycmds[pycmd]),
            )
            if keyboard_shortcut:
                button.setToolTip(tr.actions_shortcut_key(val=shortcut(keyboard_shortcut)))

    def _clear_bottom_web(self) -> None:
        self.bottom.web.setHtml(BOTTOM_WEB_CLEAR_HTML)

    def _renderBottom(self) -> None:
        self._clear_bottom_web()
        self.add_bottom_buttons()

    def _make_bottom_links(self) -> list[list[str]]:
        """
        Create a list of lists, each holding [shortcut, pycmd, button text]
        NOTE: copied from the Anki Overview class, method _renderBottom()
        """
        links = [
            ["O", "opts", tr.actions_options()],
        ]
        is_dyn = self.mw.col.decks.current()["dyn"]
        if is_dyn:
            links.append(["R", "refresh", tr.actions_rebuild()])
            links.append(["E", "empty", tr.studying_empty()])
        else:
            links.append(["C", "studymore", tr.actions_custom_study()])
            # links.append(["F", "cram", _("Filter/Cram")])
        if self.mw.col.sched.have_buried():
            links.append(["U", "unbury", tr.studying_unbury()])
        if not is_dyn:
            links.append(["", "description", tr.scheduling_description()])
        return links
