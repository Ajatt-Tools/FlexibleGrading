# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from typing import Dict, Iterable

from aqt import mw


class ConfigManager:
    def __init__(self):
        self._config = mw.addonManager.getConfig(__name__)

    def __getitem__(self, key: str) -> bool:
        assert type(self._config[key]) == bool
        return self._config[key]

    def __setitem__(self, key, value):
        assert type(self._config[key]) == bool
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

    @property
    def colors(self) -> Dict[str, str]:
        """Returns a dict mapping buttons' labels to their colors."""
        return dict(self._config['colors'])

    def get_toggleables(self) -> Iterable[str]:
        return (key for key, value in self._config.items() if isinstance(value, bool))

    def set_color(self, btn_label: str, color: str):
        self._config['colors'][btn_label] = color

    def get_zoom_state(self, state: str) -> float:
        return self._config.setdefault('zoom_states', {}).get(state, 1)

    def set_zoom_state(self, state: str, value: float) -> None:
        self._config.setdefault('zoom_states', {})[state] = value

    def write_config(self):
        mw.addonManager.writeConfig(__name__, self._config)


config = ConfigManager()
