import pathlib

from PySide2.QtCore import QObject, Signal, Slot

from jinrdatabaseloader.database import Database
from jinrdatabaseloader.file_status import LoadStatus
from jinrdatabaseloader.ui.description_model import FDFilesTree
from jinrdatabaseloader.ui.files_model import FilesModel
from jinrdatabaseloader.ui.settings import Settings
from jinrdatabaseloader.ui.utils import appdata, FD_FOLDER


class Backend(QObject):

    _files_model = None
    _description_model = None

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

    @Slot()
    def load_to_database(self):
        for row in range(self._files_model.rowCount()):
            item = self._files_model.item(row)
            path: pathlib.Path = item.path
            if item.status != LoadStatus.SUCCESS:
                #TODO(get description)
                item.status = self.database.load_data({}, item.path)


    @Slot()
    def open_help_html(self):
        html_path = appdata() / "schema.html"
        from ..utils import open_help_html
        open_help_html(html_path)
        return 0