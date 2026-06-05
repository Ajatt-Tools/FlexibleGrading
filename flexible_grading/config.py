# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import enum

from .ajt_common.addon_config import AddonConfigManager, ConfigSubViewBase
from .consts import DEFAULT_TEXT_COLOR


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


class RemainingCountType(enum.Enum):
    """
    How to display remaining cards on the bottom toolbar.
    By default, new+learn+due are separate. Single number sums all queues. None prints nothing.
    """

    default = enum.auto()
    single = enum.auto()
    none = enum.auto()


def get_label(ease: int, default_ease: int = 3) -> str:
    """Map a numeric ease value to its human-readable label.

    Returns one of 'Again', 'Hard', 'Good', 'Easy', or 'Unknown'.
    The mapping depends on the number of answer buttons available for the card,
    which is indicated by default_ease (typically 3 or 4).
    """
    if ease == 1:
        return "Again"
    if ease == default_ease:
        return "Good"
    if ease == 2:
        return "Hard"
    if ease > default_ease:
        return "Easy"
    return "Unknown"


class FlexibleGradingConfig(AddonConfigManager):
    def __init__(self, default: bool = False) -> None:
        super().__init__(default)
        self._scroll = ScrollKeysConfig(self)

    @property
    def remaining_count_type(self) -> RemainingCountType:
        return RemainingCountType[self["remaining_count_type"]]

    @remaining_count_type.setter
    def remaining_count_type(self, value: RemainingCountType) -> None:
        self["remaining_count_type"] = value.name

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
            for key, default_value in self._default_config[sub_key].items()
        }

    def get_ease_color(self, ease: int, default_ease: int) -> str:
        return self._config["colors"][get_label(ease, default_ease).lower()]

    def get_label_color(self, label: str) -> str:
        """Returns color for answer button, e.g. 'again'=>'red', 'hard'=>'yellow'."""
        return self._config["colors"].get(label.lower(), DEFAULT_TEXT_COLOR)

    @property
    def colors(self) -> dict[str, str]:
        """Returns a dict mapping buttons' labels to their colors."""
        return self._get_sub("colors")

    @property
    def buttons(self) -> dict[str, str]:
        """Returns a dict mapping buttons' labels to their key bindings."""
        return self._get_sub("buttons")

    def get_key(self, answer: str) -> str:
        """Returns shortcut key for answer button, e.g. 'again'=>'h'."""
        return self._config["buttons"].get(answer.lower(), "").lower()

    def get_answer_key(self, ease: int, default_ease: int) -> str:
        """Returns keyboard shortcut key for ease, e.g. 1=>'h', 2=>'j', 3=>'k', 4=>'l'."""
        return self._config["buttons"].get(get_label(ease, default_ease).lower(), "error").lower()

    def set_key(self, answer: str, letter: str) -> None:
        """Sets shortcut key for answer button, e.g. 'again'=>'h'."""
        self._config["buttons"][answer.lower()] = letter.lower()

    def set_color(self, btn_label: str, color: str) -> None:
        """Sets color for answer button, e.g. 'again'=>'FireBrick'."""
        self._config["colors"][btn_label.lower()] = color

    def get_zoom_state(self, state: str) -> float:
        return self._config.setdefault("zoom_states", {}).get(state, 1)

    def set_zoom_state(self, state: str, value: float) -> None:
        self._config.setdefault("zoom_states", {})[state] = value

    @property
    def show_last_review(self) -> bool:
        return bool(self["show_last_review"])

    @property
    def show_reps_done_today(self) -> bool:
        return bool(self["show_reps_done_today"])

    @property
    def flexible_reviewer(self) -> bool:
        """Return True if the native Qt flexible reviewer is enabled."""
        return bool(self["flexible_reviewer"])


config = FlexibleGradingConfig()
