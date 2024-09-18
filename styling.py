# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
from typing import Optional, Any

from aqt import gui_hooks, mw
from aqt.reviewer import ReviewerBottomBar
from aqt.webview import WebContent


def on_webview_will_set_content(web_content: WebContent, context: Optional[Any]) -> None:
    if not isinstance(context, ReviewerBottomBar):
        # not bottom bar, do not modify content
        return

    assert mw
    addon_package = mw.addonManager.addonFromModule(__name__)
    web_content.css.append(f"/_addons/{addon_package}/web/ajt__reviewer.css")


def init() -> None:
    assert mw
    mw.addonManager.setWebExports(__name__, r"web/.+\.(css|js)$")
    gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
