from anki.collection import Collection
from aqt import gui_hooks
from aqt.utils import askUser

from . import answer_buttons
from . import gui
from . import toolbar
from .consts import SCHED_UP_WARN_MSG


def init_answer_buttons(col: Collection):
    # Upgrade scheduler version, if outdated.

    if col.schedVer() != 2:
        if askUser(SCHED_UP_WARN_MSG) is True:
            col.changeSchedulerVer(2)
        else:
            return

    answer_buttons.main()


toolbar.main()
gui.main()
gui_hooks.collection_did_load.append(init_answer_buttons)
