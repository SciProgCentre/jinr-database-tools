import logging
import pathlib

from PySide2.QtCore import QObject, Signal, Slot

from sdp.database import Database
from sdp.file_status import LoadStatus
from sdp.ui.description_model import FDFilesTree
from sdp.ui.files_model import FilesModel
from sdp.ui.settings import Settings
from sdp.ui.utils import appdata


class Backend(QObject):

    _files_model = None
    _description_model = None
    _current_description_item = None
    description_changed = Signal()

    def __init__(self, settings: Settings):
        super(Backend, self).__init__(parent=None)
        self.settings = settings
        self.database = Database(self.settings.database_settings)
        settings.update_database.connect(self.update_settings)

    def update_settings(self):
        self.database.update_engine(self.settings.database_settings)
        self.check_connection_status()

    connection_status = Signal(bool)

    @Slot(result=bool)
    def check_connection_status(self):
        status = self.database.test_connect()
        self.connection_status.emit(status)
        return status

    @property
    def files_model(self):
        if self._files_model is None: self._files_model = FilesModel()
        return self._files_model

    @property
    def description_model(self):
        if self._description_model is None:
            self._description_model = FDFilesTree()
            self._description_model.initialize()
        return self._description_model

    @property
    def current_description_item(self) -> "FDItem":
        return self._current_description_item

    @current_description_item.setter
    def current_description_item(self, item):
        self._current_description_item = item
        self.description_changed.emit()

    @Slot()
    def load_to_database(self):
        description = self.current_description_item.description
        if description is not None:
            for row in range(self._files_model.rowCount()):
                item = self._files_model.item(row)
                if item.status != LoadStatus.SUCCESS:
                    load_result = self.database.load_data(description, item.path)
                    item.status = load_result.status
                    if load_result.status != LoadStatus.SUCCESS:
                        logging.error(load_result.to_string())


    @Slot()
    def open_help_html(self):
        html_path = appdata() / "schema.html"
        from ..utils import open_help_html
        open_help_html(html_path)
        return 0