import pathlib

from PySide2 import QtCore
from PySide2.QtWidgets import QWidget, QListView, QPushButton, QFileDialog, QLabel, QVBoxLayout

from sdp.ui.backend import Backend
from sdp.ui.description_manager_widget import DescriptionView
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
            self.setText(self.tr("No selected description"))
        else:
            self.setText(item.name)


class CentralWidget(QWidget):
    def __init__(self, backend):
        super().__init__()
        description_manager = self.init_description_manager(backend)
        loading_database = self.init_loading_database(backend)
        hbox(description_manager, loading_database, parent=self)

    def init_description_manager(self, backend: Backend) -> QVBoxLayout:

        return vbox(
            SelectedDescription(backend),
            title_label(self.tr("Format description manager")),
            DescriptionView(backend),
        )

    def init_loading_database(self, backend: Backend) -> QVBoxLayout:
        add_files = QPushButton(get_icon("is-folder-search.svg"), self.tr("Add files"))
        load_to_database = QPushButton(get_icon("is-database-upload"), self.tr("Load to database"))
        clear_loaded = QPushButton(get_icon("delete.svg"), self.tr("Clear loaded"))
        clear_all = QPushButton(get_icon("delete.svg"), self.tr("Clear all"))

        clear_loaded.setProperty("class", "warning")
        clear_all.setProperty("class", "danger")

        def block_loading():
            if backend.current_description_item is None:
                load_to_database.setDisabled(True)
                load_to_database.setToolTip(self.tr("Select description of files"))
            else:
                load_to_database.setDisabled(False)
                load_to_database.setToolTip(self.tr("Load this files in database"))

        backend.description_changed.connect(block_loading)
        block_loading()

        def add_file():
            files, _ = QFileDialog.getOpenFileNames(self, self.tr("Select Files for Loading to Database"))
            for file in files:
                backend.files_model.add_path(pathlib.Path(file))

        add_files.clicked.connect(add_file)
        load_to_database.clicked.connect(backend.load_to_database)
        clear_loaded.clicked.connect(backend.files_model.clear_loaded)
        clear_all.clicked.connect(backend.files_model.clear)

        hbox_up = hbox(add_files, load_to_database)
        hbox_up.addStretch()
        hbox_down = hbox(clear_loaded, clear_all)
        hbox_down.insertStretch(0)

        return vbox(title_label(self.tr("Loading to database")),
            hbox_up, FileListView(backend), hbox_down)


class FileListView(QListView):
    def __init__(self, backend: Backend):
        super(FileListView, self).__init__()
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QListView.MultiSelection)
        self.setModel(backend.files_model)
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
