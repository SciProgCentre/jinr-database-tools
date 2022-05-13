import pathlib

from PySide2 import QtCore
from PySide2.QtWidgets import QWidget, QListView, QPushButton, QFileDialog, QLabel, QVBoxLayout

from sdp.ui.backend import Backend
from sdp.ui.description_manager_widget import DescriptionView
from sdp.ui.files_model import ProxyFilesModel
from sdp.ui.utils import hbox, get_icon, vbox


def title_label(text):
    label = QLabel(text)
    label.setProperty("class", "title")
    return label


class SelectedDescription(QLabel):
    def __init__(self, backend: Backend):
        super(SelectedDescription, self).__init__()
        self.backend = backend
        backend.description_changed.connect(self.update_label)
        self.setProperty("class", "selected_description")
        self.update_label()

    def update_label(self):
        item = self.backend.current_description_item
        if item is None:
            self.setText(self.tr("No selected schema"))
        else:
            self.setText(item.name)


class CentralWidget(QWidget):
    def __init__(self, backend: Backend):
        super().__init__()
        self.backend = backend
        description_manager = self.init_description_manager(backend)
        loading_database = self.init_loading_database(backend)
        hbox(description_manager, loading_database, parent=self)

    def init_description_manager(self, backend: Backend) -> QVBoxLayout:
        self.description_view = DescriptionView(backend)
        return vbox(
            title_label(self.tr("Data format manager")),
            self.description_view,
        )

    def _add_files(self):
        add_files = QPushButton(get_icon("is-folder-search.svg"), self.tr("Add files"))

        def add_file():
            files, _ = QFileDialog.getOpenFileNames(self,
                                                    self.tr("Select Files for Loading to Database"))
            for file in files:
                self.backend.files_model.add_path(pathlib.Path(file))

        add_files.clicked.connect(add_file)
        return add_files

    def _load_to_database(self):
        load_to_database = QPushButton(get_icon("is-database-upload"), self.tr("Load to database"))

        def block_loading():
            if self.backend.current_description_item is None:
                load_to_database.setDisabled(True)
                load_to_database.setToolTip(self.tr("Select schema of input files"))
            else:
                load_to_database.setDisabled(False)
                load_to_database.setToolTip(self.tr("Load input files in database"))

        self.backend.description_changed.connect(block_loading)
        block_loading()
        load_to_database.clicked.connect(self.backend.load_to_database)
        return load_to_database

    def init_loading_database(self, backend: Backend) -> QVBoxLayout:

        clear_loaded = QPushButton(get_icon("delete.svg"), self.tr("Clear"))
        clear_all = QPushButton(get_icon("delete.svg"), self.tr("Clear"))
        clear_loaded.setProperty("class", "warning")
        clear_all.setProperty("class", "danger")
        clear_loaded.clicked.connect(backend.files_model.clear_loaded)
        clear_all.clicked.connect(backend.files_model.clear)

        hbox_up = hbox(self._add_files(), self._load_to_database())
        hbox_up.addStretch()

        clear_all = hbox(clear_all)
        clear_all.insertStretch(0)
        clear_loaded = hbox(clear_loaded)
        clear_loaded.insertStretch(0)
        return vbox(
            title_label(self.tr("Loading to database")),
            SelectedDescription(backend),
            hbox_up,
            vbox(FileListView(backend), clear_all),
            vbox(LoadedFilesView(backend), clear_loaded)
        )


class FileListView(QListView):
    def __init__(self, backend: Backend):
        super(FileListView, self).__init__()
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QListView.MultiSelection)
        self.setModel(ProxyFilesModel(backend.files_model, False))
        self.backend = backend

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            for indx in self.selectedIndexes():
                self.model().removeRow(indx.row())
        else:
            super(FileListView, self).keyPressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
            for url in event.mimeData().urls():
                path = pathlib.Path(str(url.toLocalFile()))
                self.backend.files_model.add_path(path)
        else:
            event.ignore()


class LoadedFilesView(QListView):
    def __init__(self, backend: Backend):
        super(LoadedFilesView, self).__init__()
        proxy_model = ProxyFilesModel(backend.files_model, True)
        self.setModel(proxy_model)
