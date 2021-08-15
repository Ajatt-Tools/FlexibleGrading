# -*- coding: utf-8 -*-
#
# AJT Flexible Grading add-on for Anki 2.1
# Copyright (C) 2021  Ren Tatsumoto. <tatsu at autistici.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Any modifications to this file must keep this entire header intact.

from typing import Dict

from aqt import mw
from aqt.qt import *

from .ajt_common import menu_root_entry, ADDON_SERIES
from .config import config
from .consts import *


def make_color_line_edits() -> Dict[str, QLineEdit]:
    d = {}
    for label, color in config.get_colors().items():
        d[label] = QLineEdit(color)
    return d


def make_toggleables() -> Dict[str, QCheckBox]:
    d = {}
    for toggleable in config.get_toggleables():
        if toggleable == 'color_buttons':
            continue
        d[toggleable] = QCheckBox(toggleable.replace('_', ' ').capitalize())
        d[toggleable].setChecked(config[toggleable])
    return d


class SettingsMenuUI(QDialog):
    def __init__(self, *args, **kwargs):
        super(SettingsMenuUI, self).__init__(*args, **kwargs)
        self.setWindowTitle(f'{ADDON_SERIES} {ADDON_NAME}')
        self.setMinimumSize(320, 400)
        self.colors = make_color_line_edits()
        self.toggleables = make_toggleables()
        self.color_buttons_gbox = QGroupBox("Color buttons")
        self.ok_button = QPushButton("Ok")
        self.cancel_button = QPushButton("Cancel")
        self.setLayout(self.setup_layout())
        self.add_tooltips()

    def setup_layout(self) -> QBoxLayout:
        layout = QVBoxLayout(self)
        layout.addLayout(self.make_settings_layout())
        layout.addLayout(self.make_bottom_buttons())
        return layout

    def make_settings_layout(self) -> QBoxLayout:
        layout = QVBoxLayout()
        layout.addWidget(self.make_button_colors_group())
        layout.addWidget(self.make_buttons_group())
        layout.addWidget(self.make_features_group())
        return layout

    @staticmethod
    def make_colors_link():
        label = QLabel()
        label.setText(
            f'For the list of colors, see <a style="color: SteelBlue;" href="{HTML_COLORS_LINK}">w3schools.com</a>.'
        )
        label.setOpenExternalLinks(True)
        return label

    def make_button_colors_group(self) -> QGroupBox:
        gbox = self.color_buttons_gbox
        gbox.setCheckable(True)
        gbox.setChecked(config['color_buttons'])

        grid = QGridLayout()
        for y_index, label in enumerate(self.colors.keys()):
            grid.addWidget(QLabel(label), y_index, 0)
            grid.addWidget(self.colors[label], y_index, 1)

        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addWidget(self.make_colors_link())

        gbox.setLayout(vbox)
        return gbox

    def make_buttons_group(self) -> QGroupBox:
        gbox = QGroupBox("Buttons")
        layout = QHBoxLayout()
        layout.addWidget(self.toggleables['remove_buttons'])
        layout.addWidget(self.toggleables['prevent_clicks'])
        layout.setAlignment(Qt.AlignLeft)
        gbox.setLayout(layout)
        return gbox

    def make_features_group(self) -> QGroupBox:
        gbox = QGroupBox("Features")
        layout = QHBoxLayout()
        layout.addWidget(self.toggleables['pass_fail'])
        layout.addWidget(self.toggleables['flexible_grading'])
        layout.addWidget(self.toggleables['show_last_review'])
        layout.setAlignment(Qt.AlignLeft)
        gbox.setLayout(layout)
        return gbox

    def make_bottom_buttons(self) -> QBoxLayout:
        layout = QHBoxLayout()
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)
        layout.addStretch()
        return layout

    def add_tooltips(self):
        self.toggleables['pass_fail'].setToolTip(
            '"Hard" and "Easy" buttons will be hidden.'
        )
        self.toggleables['flexible_grading'].setToolTip(
            "Grade cards from their front side\nwithout having to reveal the answer."
        )
        self.toggleables['remove_buttons'].setToolTip(
            "Remove answer buttons.\nOnly the corresponding intervals will be visible."
        )
        self.toggleables['prevent_clicks'].setToolTip(
            "Make answer buttons disabled.\n"
            "Disabled buttons are visible but unusable and un-clickable."
        )
        self.toggleables['show_last_review'].setToolTip(
            "Print the result of the last review on the toolbar."
        )


class SettingsMenuDialog(SettingsMenuUI):
    def __init__(self, *args, **kwargs):
        super(SettingsMenuDialog, self).__init__(*args, **kwargs)
        self.connect_buttons()
        if mw.col.schedVer() < 2:
            self.layout().addWidget(QLabel(SCHED_NAG_MSG))

    def connect_buttons(self):
        self.ok_button.clicked.connect(self.on_confirm)
        self.cancel_button.clicked.connect(self.reject)

    def on_confirm(self):
        config['color_buttons'] = self.color_buttons_gbox.isChecked()
        for label, lineedit in self.colors.items():
            config.set_color(label, lineedit.text())
        for key, checkbox in self.toggleables.items():
            config[key] = checkbox.isChecked()
        config.write_config()
        self.accept()


def on_open_settings():
    if mw.state != "deckBrowser":
        mw.moveToState("deckBrowser")
    dialog = SettingsMenuDialog(mw)
    dialog.exec_()


def setup_settings_action(parent: QWidget):
    action_settings = QAction(f"{ADDON_NAME} Options...", parent)
    qconnect(action_settings.triggered, on_open_settings)
    return action_settings


def main():
    root_menu = menu_root_entry()
    root_menu.addAction(setup_settings_action(root_menu))
