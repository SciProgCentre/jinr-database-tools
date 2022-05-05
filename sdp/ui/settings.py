import dataclasses
from typing import Optional

from PySide2.QtCore import QSettings, QSize, QObject, Signal
from PySide2.QtWidgets import QDockWidget, QVBoxLayout, QLabel, QWidget, QDesktopWidget

from sdp.database import DatabaseSettings
from sdp.ui.utils import hbox, FieldEditor, button


def default_size():
    desktop = QDesktopWidget()
    size = desktop.availableGeometry().size()
    width = min(size.width() * 0.8, 1280)
    height = min(size.height() * 0.8, 720)
    size = QSize(width, height)
    return size


@dataclasses.dataclass
class ApplicationSettings:
    window_size : QSize = dataclasses.field(default_factory=default_size)
    database_settings_visible : bool = True


class Settings(QObject):

    update_database = Signal()

    def __init__(self, database_settings: DatabaseSettings = DatabaseSettings()):
        super(Settings, self).__init__()
        self.database_settings = database_settings
        self.app_settings = ApplicationSettings()
        self.settings = QSettings()
        self.load_settings()

    # def reset_settings(self):
    #     for field in dataclasses.fields(self.database_settings):
    #         self.database_settings.__setattr__(field.name, field.default)

    def load_settings(self):

        def _load_settings(obj, section):
            for field in dataclasses.fields(obj):
                default = obj.__getattribute__(field.name)
                value = self.settings.value(section + "/" + field.name, default)
                if field.type == int or field.type == Optional[int]:
                    if value is not None:
                        value = int(value)
                elif field.type == bool:
                    if not isinstance(value, bool):
                        value = value.lower() in ("true",)
                obj.__setattr__(field.name, value)

        _load_settings(self.app_settings, "Application")
        _load_settings(self.database_settings, "Database")

    def update_database_settings(self):
        for field in dataclasses.fields(self.database_settings):
            self.settings.setValue("Database/" + field.name, self.database_settings.__getattribute__(field.name))
        self.update_database.emit()

    def update_application_settings(self):
        for field in dataclasses.fields(self.app_settings):
            self.settings.setValue("Application/" + field.name, self.app_settings.__getattribute__(field.name))


class ConnectionDock(QDockWidget):
    def __init__(self, parent, settings: Settings):
        super().__init__("Database settings", parent)
        self.init_UI(settings)

    def init_UI(self, settings):
        database_settings : DatabaseSettings = settings.database_settings
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        self.setWidget(widget)

        for field in dataclasses.fields(database_settings):
            editor = FieldEditor.create_field_editor(database_settings, field)
            hbox((QLabel(self.tr(field.name).title() + ":"), 1), editor.widget, parent=vbox)
            editor.updated.connect(lambda : settings.update_database_settings())
        vbox.addStretch()