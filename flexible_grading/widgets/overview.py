# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

class FlexibleOverview(Overview):
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

    def _renderBottom(self) -> None:
        self._clear_bottom_web()
        self.add_bottom_buttons()
