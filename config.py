# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from .ajt_common.addon_config import AddonConfigManager, ConfigSubViewBase


class ScrollKeysConfig(ConfigSubViewBase):
    _view_key: str = "scroll"

    @property
    def up(self) -> str:
        return self["up"]

    @property
    def down(self) -> str:
        return self["down"]

    @property
    def left(self) -> str:
        return self["left"]

    @property
    def right(self) -> str:
        return self["right"]


class FlexibleGradingConfig(AddonConfigManager):
    def __init__(self, default: bool = False) -> None:
        super().__init__(default)
        self._scroll = ScrollKeysConfig(self)

    @property
    def scroll(self) -> ScrollKeysConfig:
        return self._scroll

    @property
    def scroll_amount(self) -> int:
        return self["scroll_amount"]

    @scroll_amount.setter
    def scroll_amount(self, amount_px: int) -> None:
        self["scroll_amount"] = int(amount_px)

    def _get_sub(self, sub_key: str) -> dict[str, str]:
        return {
            key.lower(): self._config[sub_key].get(key.lower(), default_value)
            for key, default_value in
            self._default_config[sub_key].items()
        }

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

    def get_ease_color(self, ease: int, default_ease: int) -> str:
        return self._config['colors'][self.get_label(ease, default_ease).lower()]

    def get_label_color(self, label: str) -> str:
        return self._config['colors'][label.lower()]

    @property
    def colors(self) -> dict[str, str]:
        """Returns a dict mapping buttons' labels to their colors."""
        return self._get_sub('colors')

    @property
    def buttons(self) -> dict[str, str]:
        """Returns a dict mapping buttons' labels to their key bindings."""
        return self._get_sub('buttons')

    def get_key(self, answer: str) -> str:
        """Returns shortcut key for answer button, e.g. 'again'=>'h'."""
        return self._config['buttons'].get(answer.lower(), "").lower()

    def set_key(self, answer: str, letter: str):
        """Sets shortcut key for answer button, e.g. 'again'=>'h'."""
        self._config['buttons'][answer.lower()] = letter.lower()

    def set_color(self, btn_label: str, color: str):
        self._config['colors'][btn_label.lower()] = color

    def get_zoom_state(self, state: str) -> float:
        return self._config.setdefault('zoom_states', {}).get(state, 1)

    def set_zoom_state(self, state: str, value: float) -> None:
        self._config.setdefault('zoom_states', {})[state] = value


config = FlexibleGradingConfig()
