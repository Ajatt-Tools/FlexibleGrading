# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import sys

from aqt import mw

try:
    # https://github.com/beartype/beartype
    from beartype.claw import beartype_this_package

    beartype_this_package()
except ImportError:
    pass


def start_addon() -> None:
    from . import (
        bottom_toolbar,
        flexible_reviewer,
        gui,
        remaining,
        styling,
        top_toolbar,
        vim_shortcuts,
        zoom,
    )

    styling.init()
    top_toolbar.main()
    bottom_toolbar.main()
    gui.main()
    vim_shortcuts.main()
    zoom.init()
    remaining.init()
    flexible_reviewer.main()


if mw and "pytest" not in sys.modules:
    start_addon()
