import dataclasses
from typing import Optional

from PySide2.QtCore import QSettings, QSize, QObject, Signal
from PySide2.QtGui import QScreen
from PySide2.QtWidgets import QDockWidget, QVBoxLayout, QLabel, QWidget

from sdp.database import DatabaseSettings
from sdp.ui.utils import hbox, FieldEditor, DataclassSettings, DataclassForm


def default_size():
    size = QScreen().availableGeometry().size()
    width = min(size.width() * 0.8, 1280)
    height = min(size.height() * 0.8, 720)
    size = QSize(width, height)
    return size


@dataclasses.dataclass
class ApplicationSettings:
    window_size: QSize = dataclasses.field(default_factory=default_size)
    database_settings_visible: bool = True
    url_json_help: str = "https://github.com/SciProgCentre/jinr-database-tools/blob/main/sdp/resources/schema_doc.md"


class Settings(QObject):

    def __init__(self, database_settings: DatabaseSettings = DatabaseSettings(),):
        super(Settings, self).__init__()
        self.settings = QSettings()
        self.app = DataclassSettings("Application", ApplicationSettings())
        self.database = DataclassSettings("Database", database_settings)
        self.app.load_settings(self.settings)
        self.database.load_settings(self.settings)

    def save_settings(self):
        self.app.save_settings(self.settings)
        self.database.save_settings(self.settings)


class ConnectionDock(QDockWidget):
    def __init__(self, parent, backend: "Backend"):
        super().__init__("Database settings", parent)
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        self.setWidget(widget)
        vbox.addWidget(DataclassForm(backend.settings.database))
        error_label = ConnectionErrorLabel()
        vbox.addWidget(error_label)
        backend.connection_status.connect(error_label.change_status)
        backend.connection_error.connect(error_label.set_error)
        vbox.addStretch()


class ConnectionErrorLabel(QLabel):
    def __init__(self):
        super(ConnectionErrorLabel, self).__init__("")
        self.setProperty("class", "danger-title")
        self.setVisible(False)
        self.setWordWrap(True)

    def change_status(self, status):
        self.setVisible(not status)

    def set_error(self, error: str):
        error = error.replace(" ", " \u200b")
        error = error.replace(",", ",\u200b")
        error = error.replace(":", ":\u200b")
        self.setText(error)