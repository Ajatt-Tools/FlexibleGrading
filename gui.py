# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from gettext import gettext as _

from aqt import mw
from aqt.qt import *
from aqt.utils import restoreGeom, saveGeom

from .ajt_common.about_menu import menu_root_entry
from .ajt_common.consts import ADDON_SERIES
from .ajt_common.grab_key import ShortCutGrabButton
from .ajt_common.monospace_line_edit import MonoSpaceLineEdit
from .ajt_common.utils import ui_translate
from .ajt_common.widget_placement import place_widgets_in_grid
from .config import config, FlexibleGradingConfig
from .consts import ADDON_NAME, HTML_COLORS_LINK, SCHED_NAG_MSG

as_label = ui_translate


class ColorEdit(MonoSpaceLineEdit):
    font_size = 14
    min_height = 24

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        color_regex = QRegularExpression(r'^#?\w+$')
        color_validator = QRegularExpressionValidator(color_regex, self)
        self.setValidator(color_validator)
        self.setPlaceholderText("HTML color code")


class ColorEditPicker(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._edit = ColorEdit()
        self.setLayout(layout := QHBoxLayout())
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._edit)
        layout.addWidget(b := QPushButton(_("Pick")))
        b.setMinimumSize(32, 16)
        b.setBaseSize(32, 22)
        qconnect(b.clicked, self.choose_color)

    def choose_color(self):
        color = QColorDialog.getColor(initial=QColor.fromString(self._edit.text()))
        if color.isValid():
            self._edit.setText(color.name())

    def setText(self, text: str):
        return self._edit.setText(text)

    def text(self):
        return self._edit.text()


class SimpleKeyEdit(MonoSpaceLineEdit):
    font_size = 14
    min_height = 24

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        key_regex = QRegularExpression(r'^[-a-z0-9:;<>=?@~|`_/&!#$%^*(){}"+\]\[\\\']?$')
        key_validator = QRegularExpressionValidator(key_regex, self)
        self.setValidator(key_validator)
        self.setPlaceholderText("Key letter")
        self.setToolTip("If a key is taken by something else, it will refuse to work.\nLeave empty to disable.")


class ScrollAmountSpinBox(QSpinBox):
    _default_allowed_range: tuple[int, int] = (10, 1000)
    _single_step_amount: int = 10

    def __init__(self, initial_value: int = None):
        super().__init__()
        self.setRange(*self._default_allowed_range)
        self.setSingleStep(self._single_step_amount)
        if initial_value:
            self.setValue(initial_value)


def make_color_line_edits() -> dict[str, ColorEditPicker]:
    d = {}
    for label in config.colors:
        d[label] = ColorEditPicker()
    return d


def make_answer_key_edits() -> dict[str, QLineEdit]:
    d = {}
    for label, button_key in config.buttons.items():
        d[label] = SimpleKeyEdit(button_key)
    return d


def make_toggleables() -> dict[str, QCheckBox]:
    """
    Automatically create QCheckBox instances for config keys with bool values.
    to avoid creating them by hand for each key.
    """
    d = {}
    for toggleable in config.bool_keys():
        if toggleable == 'color_buttons':
            # handled separately by a checkable groupbox
            continue
        d[toggleable] = QCheckBox(as_label(toggleable))
    return d


def make_scroll_shortcut_edits() -> dict[str, ShortCutGrabButton]:
    return {key: ShortCutGrabButton() for key in config.scroll.keys()}


class SettingsMenuUI(QDialog):
    name = f"{ADDON_SERIES} {ADDON_NAME} Settings Dialog"
    _n_columns = 2
    _scroll_shortcut_edits: dict[str, ShortCutGrabButton]
    _colors: dict[str, ColorEditPicker]
    _answer_keys: dict[str, QLineEdit]
    _toggleables: dict[str, QCheckBox]
    _color_buttons_gbox: QGroupBox  # if unchecked, buttons are not painted.
    _button_box: QDialogButtonBox
    _restore_settings_button: QPushButton
    _scroll_amount_spin: QSpinBox

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(f'{ADDON_SERIES} {ADDON_NAME}')
        self.setMinimumSize(640, 540)
        self._colors = make_color_line_edits()
        self._answer_keys = make_answer_key_edits()
        self._toggleables = make_toggleables()
        self._scroll_shortcut_edits = make_scroll_shortcut_edits()
        self._color_buttons_gbox = QGroupBox("Color buttons")
        self._scroll_amount_spin = ScrollAmountSpinBox()
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        self._restore_settings_button = self._button_box.addButton(
            _("Restore &Defaults"), QDialogButtonBox.ButtonRole.ResetRole
        )
        self.setup_layout()
        self.add_tooltips()

    def setup_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.addLayout(self.make_settings_layout())
        layout.addWidget(self._button_box)
        self.setLayout(layout)

    def make_settings_layout(self) -> QLayout:
        layout = QGridLayout()
        # row, col, row-span, col-span

        # Color buttons (pick colors)
        layout.addWidget(self.make_button_colors_group(), 0, 0, 1, 1)
        # Keys (assign letters)
        layout.addWidget(self.make_shortcuts_group(), 0, 1, 1, 1)
        # Buttons (remove, prevent clicks)
        layout.addWidget(self.make_buttons_group(), 1, 0, 1, 1)
        # Features (disable/enable pass-fail, flexible grading, etc.)
        layout.addWidget(self.make_features_group(), 1, 1, 1, 1)
        # Zoom behavior
        layout.addWidget(self.make_zoom_group(), 2, 0, 1, 1)
        # Scroll shortcuts and scroll amount
        layout.addWidget(self.make_scroll_group(), 2, 1, 1, 1)
        return layout

    @staticmethod
    def make_colors_link():
        label = QLabel()
        label.setText(
            f'For the list of colors, see <a style="color: SteelBlue;" href="{HTML_COLORS_LINK}">w3schools.com</a>.'
        )
        label.setOpenExternalLinks(True)
        return label

    def make_button_colors_group(self) -> QGroupBox:
        gbox = self._color_buttons_gbox
        gbox.setCheckable(True)
        form = QFormLayout()
        for key, lineedit in self._colors.items():
            form.addRow(as_label(key), lineedit)
        form.addWidget(self.make_colors_link())
        gbox.setLayout(form)
        return gbox

    def make_shortcuts_group(self) -> QGroupBox:
        gbox = QGroupBox("Keys")
        gbox.setCheckable(False)
        form = QFormLayout()
        for key, key_edit in self._answer_keys.items():
            form.addRow(as_label(key), key_edit)
        gbox.setLayout(form)
        return gbox

    def make_buttons_group(self) -> QGroupBox:
        keys = (
            'remove_buttons',
            'prevent_clicks',
        )
        gbox = QGroupBox("Buttons")
        gbox.setCheckable(False)
        gbox.setLayout(place_widgets_in_grid(
            (self._toggleables[key] for key in keys),
            n_columns=self._n_columns,
        ))
        return gbox

    def make_features_group(self) -> QGroupBox:
        keys = (
            'pass_fail',
            'flexible_grading',
            'show_last_review',
            'hide_card_type',
            'press_answer_key_to_flip_card',
        )
        gbox = QGroupBox("Features")
        gbox.setCheckable(False)
        gbox.setLayout(place_widgets_in_grid(
            (self._toggleables[key] for key in keys),
            n_columns=self._n_columns,
        ))
        return gbox

    def make_zoom_group(self) -> QGroupBox:
        keys = (
            'set_zoom_shortcuts',
            'remember_zoom_level',
            'tooltip_on_zoom_change',
        )
        gbox = QGroupBox("Zoom")
        gbox.setCheckable(False)
        gbox.setLayout(place_widgets_in_grid(
            (self._toggleables[key] for key in keys),
            n_columns=self._n_columns,
        ))
        return gbox

    def make_scroll_group(self):
        gbox = QGroupBox("Scroll")
        gbox.setCheckable(False)
        form = QFormLayout()
        for scroll_direction, key_edit_widget in self._scroll_shortcut_edits.items():
            form.addRow(as_label(scroll_direction), key_edit_widget)
        form.addRow("Scroll amount", self._scroll_amount_spin)
        gbox.setLayout(form)
        return gbox

    def add_tooltips(self):
        self._toggleables['pass_fail'].setToolTip(
            '"Hard" and "Easy" buttons will be hidden.'
        )
        self._toggleables['flexible_grading'].setToolTip(
            "Grade cards from their front side\nwithout having to reveal the answer."
        )
        self._toggleables['remove_buttons'].setToolTip(
            "Remove answer buttons.\nOnly the corresponding intervals will be visible."
        )
        self._toggleables['prevent_clicks'].setToolTip(
            "Make answer buttons disabled.\n"
            "Disabled buttons are visible but unusable and un-clickable."
        )
        self._toggleables['show_last_review'].setToolTip(
            "Print the result of the last review on the toolbar."
        )
        self._toggleables['set_zoom_shortcuts'].setToolTip(
            "Change zoom value by pressing Ctrl+Plus and Ctrl+Minus."
        )
        self._toggleables['remember_zoom_level'].setToolTip(
            "Remember last zoom level and restore it on state change."
        )
        self._toggleables['tooltip_on_zoom_change'].setToolTip(
            "Show a tooltip when zoom level changes."
        )
        self._toggleables['hide_card_type'].setToolTip(
            "Turn off the indicator that tells you whether a card is new, review, or learn."
        )
        self._toggleables['press_answer_key_to_flip_card'].setToolTip(
            "Answer keys ('h', 'j', 'k', 'l' by default) will be used\n"
            "to reveal the back side, similarly to the Space bar."
        )


class SettingsMenuDialog(SettingsMenuUI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connect_buttons()
        if mw.col.schedVer() < 2:
            self.layout().addWidget(QLabel(SCHED_NAG_MSG))
        self.restore_values(config)
        restoreGeom(self, self.name)

    def restore_values(self, cm: FlexibleGradingConfig):
        self._color_buttons_gbox.setChecked(cm['color_buttons'])
        for key, checkbox in self._toggleables.items():
            checkbox.setChecked(cm[key])
        for label, color_text in cm.colors.items():
            self._colors[label].setText(color_text)
        for label, key_letter in cm.buttons.items():
            self._answer_keys[label].setText(key_letter)
        for scroll_direction, shortcut_str in cm.scroll.items():
            self._scroll_shortcut_edits[scroll_direction].setValue(shortcut_str)
        self._scroll_amount_spin.setValue(config.scroll_amount)

    def connect_buttons(self):
        qconnect(
            self._restore_settings_button.clicked,
            lambda: self.restore_values(FlexibleGradingConfig(default=True)),
        )
        qconnect(self._button_box.accepted, self.accept)
        qconnect(self._button_box.rejected, self.reject)

    def accept(self) -> None:
        config['color_buttons'] = self._color_buttons_gbox.isChecked()
        for label, lineedit in self._colors.items():
            config.set_color(label, lineedit.text())
        for label, lineedit in self._answer_keys.items():
            config.set_key(label, lineedit.text())
        for key, checkbox in self._toggleables.items():
            config[key] = checkbox.isChecked()
        for scroll_direction, key_edit_widget in self._scroll_shortcut_edits.items():
            config.scroll[scroll_direction] = key_edit_widget.value()
        config.scroll_amount = self._scroll_amount_spin.value()
        config.write_config()
        return super().accept()

    def done(self, *args, **kwargs) -> None:
        saveGeom(self, self.name)
        return super().done(*args, **kwargs)


def on_open_settings():
    if mw.state != "deckBrowser":
        mw.moveToState("deckBrowser")
    dialog = SettingsMenuDialog(mw)
    dialog.exec()


def setup_settings_action(parent: QWidget) -> QAction:
    action_settings = QAction(f"{ADDON_NAME} Options...", parent)
    qconnect(action_settings.triggered, on_open_settings)
    return action_settings


def main():
    root_menu = menu_root_entry()
    root_menu.addAction(setup_settings_action(root_menu))
