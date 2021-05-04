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

from anki.consts import *
from anki.lang import _
from aqt import mw


class ConfigManager:
    _map = {
        BUTTON_ONE: "Again",
        BUTTON_TWO: "Hard",
        BUTTON_THREE: "Good",
        BUTTON_FOUR: "Easy",
    }

    def __init__(self):
        self._config = mw.addonManager.getConfig(__name__)

    def get_color(self, ease: int) -> str:
        return self._config['colors'][self._map[ease]]

    @classmethod
    def get_label(cls, ease: int) -> str:
        return _(cls._map[ease])

    def __getitem__(self, key) -> bool:
        assert key != 'colors' and key != 'buttons'
        return self._config[key]

    def __setitem__(self, key, value):
        assert key != 'colors' and key != 'buttons'
        self._config[key] = value

    def get_buttons(self) -> Dict[str, str]:
        return self._config['colors']

    def get_toggleables(self):
        return (key for key in self._config.keys() if key != 'colors')

    def set_color(self, btn_label: str, color: str):
        self._config['colors'][btn_label] = color

    def write_config(self):
        mw.addonManager.writeConfig(__name__, self._config)


config = ConfigManager()
