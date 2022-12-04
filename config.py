# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from typing import Dict, Iterable, Union, overload

from aqt import mw


class ConfigManager:
    @staticmethod
    def _get_default_config():
        manager = mw.addonManager
        addon = manager.addonFromModule(__name__)
        return manager.addonConfigDefaults(addon)

    @staticmethod
    def _get_config():
        return mw.addonManager.getConfig(__name__)

    def __init__(self, default: bool = False):
        self._default_config = self._get_default_config()
        self._config = self._default_config if default else self._get_config()

    def _get(self, key: str):
        return self._config.get(key, self._default_config[key])

    def __getitem__(self, key: str) -> bool:
        assert type(val := self._get(key)) == bool
        return val

    def __setitem__(self, key, value):
        assert type(self._get(key)) == bool
        self._config[key] = value

    @property
    def default(self) -> bool:
        return self._default_config is self._config

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

    @overload
    def get_color(self, ease: int, default_ease: int) -> str:
        ...

    @overload
    def get_color(self, label: str) -> str:
        ...

    def get_color(self, ease_or_label: Union[int, str], default_ease: int = 3) -> str:
        label = (
            ease_or_label
            if type(ease_or_label) == str
            else self.get_label(ease_or_label, default_ease)
        ).lower()
        return self._config['colors'].get(label, self._default_config['colors'].get(label, "Pink"))

    @property
    def colors(self) -> Dict[str, str]:
        """Returns a dict mapping buttons' labels to their colors."""
        return {
            label.lower(): self._config['colors'].get(label.lower(), color_text)
            for label, color_text in
            self._default_config['colors'].items()
        }

    def get_toggleables(self) -> Iterable[str]:
        """Returns an iterable of boolean keys in the config."""
        return (key for key, value in self._default_config.items() if isinstance(value, bool))

    def set_color(self, btn_label: str, color: str):
        self._config['colors'][btn_label.lower()] = color

    def get_zoom_state(self, state: str) -> float:
        return self._config.setdefault('zoom_states', {}).get(state, 1)

    def set_zoom_state(self, state: str, value: float) -> None:
        self._config.setdefault('zoom_states', {})[state] = value

    def write_config(self):
        if self.default:
            raise RuntimeError("Can't write default config.")
        mw.addonManager.writeConfig(__name__, self._config)


config = ConfigManager()
