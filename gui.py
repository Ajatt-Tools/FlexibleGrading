# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from gettext import gettext as _
from typing import Dict

from aqt import mw
from aqt.qt import *
from aqt.utils import restoreGeom, saveGeom

from .ajt_common import menu_root_entry, ADDON_SERIES
from .config import config, ConfigManager
from .consts import *


def make_color_line_edits() -> Dict[str, QLineEdit]:
    d = {}
    for label, color_text in config.colors.items():
        d[label] = QLineEdit(color_text)
    return d


def make_toggleables() -> Dict[str, QCheckBox]:
    d = {}
    for toggleable in config.get_toggleables():
        if toggleable == 'color_buttons':
            continue
        d[toggleable] = QCheckBox(toggleable.replace('_', ' ').capitalize())
    return d


class SettingsMenuUI(QDialog):
    name = "FlexibleGradingSettingsDialog"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(f'{ADDON_SERIES} {ADDON_NAME}')
        self.setMinimumSize(320, 400)
        self.colors = make_color_line_edits()
        self.toggleables = make_toggleables()
        self.color_buttons_gbox = QGroupBox("Color buttons")
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        self.restore_settings_button = self.button_box.addButton(
            _("Restore &Defaults"), QDialogButtonBox.ButtonRole.ResetRole
        )
        self.setLayout(self.setup_layout())
        self.add_tooltips()

    def setup_layout(self) -> QBoxLayout:
        layout = QVBoxLayout(self)
        layout.addLayout(self.make_settings_layout())
        layout.addWidget(self.button_box)
        return layout

    def make_settings_layout(self) -> QBoxLayout:
        layout = QVBoxLayout()
        layout.addWidget(self.make_button_colors_group())
        layout.addWidget(self.make_buttons_group())
        layout.addWidget(self.make_features_group())
        layout.addWidget(self.make_zoom_group())
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
        gbox = self.color_buttons_gbox
        gbox.setCheckable(True)
        form = QFormLayout()
        for label, lineedit in self.colors.items():
            form.addRow(label.capitalize(), lineedit)
        vbox = QVBoxLayout()
        vbox.addLayout(form)
        vbox.addWidget(self.make_colors_link())
        gbox.setLayout(vbox)
        return gbox

    def make_buttons_group(self) -> QGroupBox:
        gbox = QGroupBox("Buttons")
        layout = QHBoxLayout()
        layout.addWidget(self.toggleables['remove_buttons'])
        layout.addWidget(self.toggleables['prevent_clicks'])
        layout.setAlignment(Qt.AlignLeft)
        gbox.setLayout(layout)
        return gbox

    def make_features_group(self) -> QGroupBox:
        gbox = QGroupBox("Features")
        layout = QHBoxLayout()
        layout.addWidget(self.toggleables['pass_fail'])
        layout.addWidget(self.toggleables['flexible_grading'])
        layout.addWidget(self.toggleables['show_last_review'])
        layout.addWidget(self.toggleables['hide_card_type'])
        layout.setAlignment(Qt.AlignLeft)
        gbox.setLayout(layout)
        return gbox

    def make_zoom_group(self) -> QGroupBox:
        gbox = QGroupBox("Zoom")
        layout = QHBoxLayout()
        layout.addWidget(self.toggleables['set_zoom_shortcuts'])
        layout.addWidget(self.toggleables['remember_zoom_level'])
        layout.addWidget(self.toggleables['tooltip_on_zoom_change'])
        layout.setAlignment(Qt.AlignLeft)
        gbox.setLayout(layout)
        return gbox

    def add_tooltips(self):
        self.toggleables['pass_fail'].setToolTip(
            '"Hard" and "Easy" buttons will be hidden.'
        )
        self.toggleables['flexible_grading'].setToolTip(
            "Grade cards from their front side\nwithout having to reveal the answer."
        )
        self.toggleables['remove_buttons'].setToolTip(
            "Remove answer buttons.\nOnly the corresponding intervals will be visible."
        )
        self.toggleables['prevent_clicks'].setToolTip(
            "Make answer buttons disabled.\n"
            "Disabled buttons are visible but unusable and un-clickable."
        )
        self.toggleables['show_last_review'].setToolTip(
            "Print the result of the last review on the toolbar."
        )
        self.toggleables['set_zoom_shortcuts'].setToolTip(
            "Change zoom value by pressing Ctrl+Plus and Ctrl+Minus."
        )
        self.toggleables['remember_zoom_level'].setToolTip(
            "Remember last zoom level and restore it on state change."
        )
        self.toggleables['tooltip_on_zoom_change'].setToolTip(
            "Show a tooltip when zoom level changes."
        )
        self.toggleables['hide_card_type'].setToolTip(
            "Turn off the indicator that tells you whether a card is new, review, or again."
        )


class SettingsMenuDialog(SettingsMenuUI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connect_buttons()
        if mw.col.schedVer() < 2:
            self.layout().addWidget(QLabel(SCHED_NAG_MSG))
        self.restore_values()
        restoreGeom(self, self.name)

    def restore_values(self, cm: ConfigManager = config):
        self.color_buttons_gbox.setChecked(cm['color_buttons'])
        for key, checkbox in self.toggleables.items():
            checkbox.setChecked(cm[key])
        for label, color_text in cm.colors.items():
            self.colors[label].setText(color_text)

    def connect_buttons(self):
        qconnect(self.restore_settings_button.clicked, lambda: self.restore_values(ConfigManager(default=True)))
        qconnect(self.button_box.accepted, self.accept)
        qconnect(self.button_box.rejected, self.reject)

    def accept(self) -> None:
        config['color_buttons'] = self.color_buttons_gbox.isChecked()
        for label, lineedit in self.colors.items():
            config.set_color(label, lineedit.text())
        for key, checkbox in self.toggleables.items():
            config[key] = checkbox.isChecked()
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
