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
EASE_ROW_STYLE = """
<style>
.ajt__ease_row {
    display: flex;
    flex-flow: row nowrap;
    justify-content: space-between;
    align-items: flex-start;
    max-width: 450px;
    min-width: 200px;
    user-select: none;
    margin: -3px auto 0;
}
.ajt__ease_row > * {
    white-space: nowrap;
    font-size: small;
    font-weight: normal;
}
.ajt__ease_row > .ajt__stat_txt:only-child {
    margin: 0 auto;
}
</style>
"""
BOTTOM_TABLE_STYLE = """
<style>
#innertable tr {
    display: flex;
    flex-flow: row nowrap;
    justify-content: space-between;
}
#innertable td {
    flex: 2 0 100px;
}
.ajt__corner_stat:first-child,
.ajt__corner_stat:last-child {
    flex: 1 0 50px;
    display: flex;
}
.ajt__corner_stat:first-child {
    justify-content: flex-start;
}
.ajt__corner_stat:last-child {
    justify-content: flex-end;
}
.ajt__corner_button {
    display: block;
    font-weight: normal;
    font-size: small;
    white-space: nowrap;
    user-select: none;
    margin: -3px 0 0;
    padding: 0 5px;
}
.ajt__corner_button:hover {
    color: RoyalBlue;
}
</style>
"""
