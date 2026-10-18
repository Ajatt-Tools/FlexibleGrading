# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import json
import pathlib

from flexible_grading.config import FlexibleGradingConfig


class NoAnkiConfigView(FlexibleGradingConfig):
    """
    Loads the default config without starting Anki.
    """

    config_json_path = pathlib.Path(__file__).parent.parent / "flexible_grading" / "config.json"

    def _set_underlying_dicts(self) -> None:
        with open(self.config_json_path) as f:
            self._default_config = self._config = json.load(f)

    def write_config(self) -> None:
        pass
