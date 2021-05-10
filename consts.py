from anki.lang import _

ADDON_NAME = "AJT Flexible Grading"
GITHUB = "https://github.com/Ajatt-Tools"
DONATE_LINK = "https://tatsumoto-ren.github.io/blog/donating-to-tatsumoto.html"
COMMUNITY_LINK = "https://tatsumoto-ren.github.io/blog/join-our-community.html"
HTML_COLORS_LINK = "https://www.w3schools.com/colors/colors_groups.asp"
YT_LINK = "https://www.youtube.com/c/MATTvsJapan"
STYLING = """
<style>
a { color: SteelBlue; }
h2 { text-align: center; }
</style>
"""
ABOUT_MSG = STYLING + f"""
<h2>{ADDON_NAME}</h2>
<p>An <a href="{GITHUB}">Ajatt-Tools</a> add-on for fast, smooth and efficient reviewing.</p>
<p>Copyright © Ren Tatsumoto</p>
<p>
This software is licensed under <a href="{GITHUB}/FlexibleGrading/blob/main/LICENSE">GNU AGPL version 3</a>.
Source code is available on <a href="{GITHUB}/FlexibleGrading">GitHub</a>.
</p>
<p>For the list of colors, see <a href="{HTML_COLORS_LINK}">w3schools.com</a>.</p>
<p>
A big thanks to all the people who donated to make this project possible
and <a href="{YT_LINK}">mattvsjapan</a> for the idea for this add-on.
</p>
"""
SCHED_NAG_MSG = """
<font color="%s">
You are still using the old scheduler.
The add-on is disabled.<br>
Please upgrade the scheduler and restart Anki.
</font>
"""
SCHED_UP_WARN_MSG = _(
    f"You've installed {ADDON_NAME}, " +
    "but you're still using the outdated V1 scheduler. "
    "Upgrading the scheduler to V2 will reset any cards in learning and clear filtered decks. "
    "Proceed?"
)
