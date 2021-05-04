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
from aqt.utils import openLink

from .config import config

ADDON_NAME = "AJT Flexible Grading"
GITHUB = "https://github.com/Ajatt-Tools"
STYLING = """
<style>
a { color: SteelBlue; }
h2 { text-align: center; }
</style>
"""
ABOUT_MSG = STYLING + f"""\
<h2>{ADDON_NAME}</h2>
<p>An <a href="{GITHUB}">Ajatt-Tools</a> add-on for fast, smooth and efficient reviewing.</p>
<p>Copyright © Ren Tatsumoto</p>
<p>
This software is licensed under <a href="{GITHUB}/FlexibleGrading/blob/main/LICENSE">GNU AGPL version 3</a>.
Source code is available on <a href="{GITHUB}/FlexibleGrading">GitHub</a>.
</p>
<p>For the list of colors, see <a href="https://www.w3schools.com/colors/colors_groups.asp">w3schools.com</a>.</p>
<p>A big thanks to all the people who donated to make this project possible.</p>
"""
DONATE_LINK = "https://tatsumoto-ren.github.io/blog/donating-to-tatsumoto.html"
COMMUNITY_LINK = "https://tatsumoto-ren.github.io/blog/join-our-community.html"


def make_color_line_edits() -> Dict[str, QLineEdit]:
    d = {}
    for label, color in config.get_buttons().items():
        d[label] = QLineEdit(color)
    return d


def make_toggleables() -> Dict[str, QCheckBox]:
    d = {}
    for toggleable in config.get_toggleables():
        d[toggleable] = QCheckBox(toggleable.replace('_', ' ').capitalize())
        d[toggleable].setChecked(config[toggleable])
    return d


class SettingsMenuUI(QDialog):
    def __init__(self, *args, **kwargs):
        super(SettingsMenuUI, self).__init__(*args, **kwargs)
        self.setWindowTitle(ADDON_NAME)
        self.setMinimumSize(480, 320)
        self.colors = make_color_line_edits()
        self.toggleables = make_toggleables()
        self.ok_button = QPushButton("Ok")
        self.cancel_button = QPushButton("Cancel")
        self.community_button = QPushButton("Join our community")
        self.donate_button = QPushButton("Donate")
        self.setLayout(self.setup_layout())

    def setup_layout(self) -> QBoxLayout:
        layout = QVBoxLayout(self)
        layout.addWidget(self.make_tabs())
        layout.addLayout(self.make_bottom_buttons())
        return layout

    def make_tabs(self) -> QTabWidget:
        tabs = QTabWidget()

        tab1 = QWidget()
        tab2 = QWidget()

        tabs.addTab(tab1, "Settings")
        tabs.addTab(tab2, "About")

        tab1.setLayout(self.make_settings_layout())
        tab2.setLayout(self.make_about_layout())

        return tabs

    def make_settings_layout(self) -> QBoxLayout:
        layout = QVBoxLayout()
        layout.addWidget(self.make_button_colors_group())
        layout.addWidget(self.make_toggleables_group())
        return layout

    def make_button_colors_group(self) -> QGroupBox:
        gbox = QGroupBox("Colors")
        # gbox.setCheckable(True)
        # gbox.setChecked(False)
        grid = QGridLayout()
        for y_index, label in enumerate(self.colors.keys()):
            grid.addWidget(QLabel(label), y_index, 0)
            grid.addWidget(self.colors[label], y_index, 1)

        gbox.setLayout(grid)
        return gbox

    def make_toggleables_group(self) -> QGroupBox:
        gbox = QGroupBox("Toggleables")
        layout = QVBoxLayout()
        for _, checkbox in self.toggleables.items():
            layout.addWidget(checkbox)
        gbox.setLayout(layout)
        return gbox

    def make_bottom_buttons(self) -> QBoxLayout:
        layout = QHBoxLayout()
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)
        layout.addStretch()
        return layout

    def make_about_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.make_about_text())
        layout.addLayout(self.make_social_buttons())
        return layout

    @staticmethod
    def make_about_text():
        textedit = QTextBrowser()
        textedit.setReadOnly(True)
        textedit.insertHtml(ABOUT_MSG)
        textedit.setOpenExternalLinks(True)
        return textedit

    def make_social_buttons(self) -> QHBoxLayout:
        self.add_button_icons()
        layout = QHBoxLayout()
        layout.addWidget(self.community_button)
        layout.addWidget(self.donate_button)
        return layout

    def add_button_icons(self):
        chat_icon_path = os.path.join(os.path.dirname(__file__), 'img', 'element.svg')
        donate_icon_path = os.path.join(os.path.dirname(__file__), 'img', 'patreon_logo.svg')

        self.community_button.setIcon(QIcon(chat_icon_path))
        self.donate_button.setIcon(QIcon(donate_icon_path))


class SettingsMenuDialog(SettingsMenuUI):
    def __init__(self, *args, **kwargs):
        super(SettingsMenuDialog, self).__init__(*args, **kwargs)
        self.connect_buttons()

    def connect_buttons(self):
        self.ok_button.clicked.connect(self.on_confirm)
        self.cancel_button.clicked.connect(self.reject)
        self.community_button.clicked.connect(lambda: openLink(COMMUNITY_LINK))
        self.donate_button.clicked.connect(lambda: openLink(DONATE_LINK))

    def on_confirm(self):
        for label, lineedit in self.colors.items():
            config.set_color(label, lineedit.text())
        for key, checkbox in self.toggleables.items():
            config[key] = checkbox.isChecked()
        config.write_config()
        self.accept()


def on_open_settings():
    dialog = SettingsMenuDialog(mw)
    dialog.exec_()


def setup_settings_action():
    action_settings = QAction(f"{ADDON_NAME} Options...", mw)
    qconnect(action_settings.triggered, on_open_settings)
    return action_settings


def main():
    mw.form.menuTools.addAction(setup_settings_action())
