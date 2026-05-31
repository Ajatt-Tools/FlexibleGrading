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
    """Initialize all addon modules and register Anki hooks.

    Imports are deferred to avoid loading Anki-dependent modules at package import time.
    This is required because the addon package is imported by Anki before the main window
    and collection are fully initialized, and also allows pytest to import the package
    without triggering Anki UI initialization.
    """
    from . import (  # noqa: PLC0415 (deferred imports, see docstring)
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
