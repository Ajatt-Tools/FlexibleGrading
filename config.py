# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from typing import Dict, Iterable

from aqt import mw


class ConfigManager:
    def __init__(self):
        self._config = mw.addonManager.getConfig(__name__)

    def __getitem__(self, key) -> bool:
        assert key != 'colors' and key != 'buttons'
        return self._config[key]

    def __setitem__(self, key, value):
        assert key != 'colors' and key != 'buttons'
        self._config[key] = value

    @staticmethod
    def get_label(ease: int, default_ease: int = 3) -> str:
        if ease == 1:
            return "Again"
        if ease == default_ease:
            return "Good"
        if ease == 2:
            return "Hard"
        if ease > default_ease:
            return "Easy"
        return "Unknown"

    def get_color(self, ease: int, default_ease: int = 3) -> str:
        return self._config['colors'][self.get_label(ease, default_ease)]

    def get_colors(self) -> Dict[str, str]:
        return self._config['colors']

    def get_toggleables(self) -> Iterable[str]:
        return (key for key, value in self._config.items() if isinstance(value, bool))

    def set_color(self, btn_label: str, color: str):
        self._config['colors'][btn_label] = color

    def write_config(self):
        mw.addonManager.writeConfig(__name__, self._config)


config = ConfigManager()
