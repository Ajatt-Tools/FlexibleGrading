# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

ADDON_NAME = "Flexible Grading"
HTML_COLORS_LINK = "https://www.w3schools.com/colors/colors_groups.asp"
SCHED_NAG_MSG = """
<font color="gray">
You are still using the old scheduler.
Please enable the V2 scheduler in Preferences.
</font>
"""

# Flexible bottom bar widget dimensions and styling.
FLEXIBLE_BUTTON_HEIGHT = 16
FLEXIBLE_BUTTON_FONT_SIZE = FLEXIBLE_BUTTON_HEIGHT - 4
FLEXIBLE_BUTTONS_SPACING = 8
DEFAULT_TEXT_COLOR = "palette(button-text)"
HOVER_BG_COLOR = "#d0d0d0"
PRESSED_BG_COLOR = "#b8b8b8"
TIMER_EXPIRED_COLOR = "red"

# Timer tick interval in milliseconds.
TIMER_INTERVAL_MS = 1000

# Delay before retrying _showEaseButtons when states have not been mutated yet.
STATES_MUTATED_RETRY_MS = 50

# Placeholder for empty queue counts in the reviewer bottom bar.
EMPTY_PLACEHOLDER = "・"

# HTML injected into the bottom web view to collapse it when using native Qt widgets.
BOTTOM_WEB_CLEAR_HTML = "<style>body {margin:0;padding:0;height:0;} html {height:0;}</style>"

# Font family list for the flexible push button stylesheet.
FLEXIBLE_BUTTON_FONT_FAMILY = (
    '"Noto Sans Mono", "Liberation Mono", "DejaVu Sans Mono", "Courier New", "Lucida Console",'
    ' Courier, Consolas, "Noto Sans Mono CJK JP", monospace'
)

# Qt stylesheet template for FlexiblePushButton.
# Placeholders: text_color, font_size, font_family, underline_rule, hover_bg, pressed_bg.
FLEXIBLE_BUTTON_STYLESHEET = """\
FlexiblePushButton {{
    border: none;
    background: transparent;
    color: {text_color};
    margin: 0;
    padding: 0;
    font-size: {font_size}px;
    min-width: 0;
    qproperty-flat: true;
    font-family: {font_family};
    {underline_rule}
}}
FlexiblePushButton:hover {{
    background: {hover_bg};
    color: #000;
}}
FlexiblePushButton:pressed {{
    background: {pressed_bg};
}}"""
