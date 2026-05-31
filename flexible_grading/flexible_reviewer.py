# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import aqt.webview
from anki.scheduler.v3 import Scheduler as V3Scheduler
from aqt import gui_hooks, mw
from aqt.utils import showWarning
from aqt.webview import AnkiWebViewKind

from .config import config
from .widgets.deck_browser import FlexibleDeckBrowser
from .widgets.overview import FlexibleOverview
from .widgets.reviewer import FlexibleReviewer
from .widgets.widgets import get_flexible_bottom_bar


def on_card_review_webview_did_init(_web: aqt.webview.AnkiWebView, kind: aqt.webview.AnkiWebViewKind) -> None:
    """Create the flexible bottom bar widget when the main review webview initializes."""
    if kind != AnkiWebViewKind.MAIN:
        return
    if config.flexible_reviewer:
        get_flexible_bottom_bar()


def on_main_window_did_init() -> None:
    """Replace Anki's default deck browser, reviewer, and overview with flexible variants.

    Called after mw.setupUI completes.
    Does nothing if the flexible reviewer feature is disabled in config
    or if the V3 scheduler is not active.
    """
    if not config.flexible_reviewer:
        return
    assert mw.col, "collection should be available"
    if not isinstance(mw.col.sched, V3Scheduler):
        showWarning("Flexible Reviewer requires the V3 scheduler. Feature disabled.")
        return
    mw.deckBrowser = FlexibleDeckBrowser(mw)
    mw.reviewer = FlexibleReviewer(mw, config)
    mw.overview = FlexibleOverview(mw)


def main() -> None:
    """Register Anki hooks for the flexible reviewer feature."""
    gui_hooks.card_review_webview_did_init.append(on_card_review_webview_did_init)
    gui_hooks.main_window_did_init.append(on_main_window_did_init)
