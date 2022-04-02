import pathlib

from PySide2 import QtCore
from PySide2.QtWidgets import QTreeView, QMenu, QFileDialog, QMessageBox

from jinrdatabaseloader.ui.backend import Backend
from jinrdatabaseloader.ui.description_editor import DescriptionEditor
from jinrdatabaseloader.ui.description_model import CollectionItem
from jinrdatabaseloader.ui.utils import get_icon


class DescriptionView(QTreeView):
    def __init__(self, backend: Backend):
        super(DescriptionView, self).__init__()
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setHeaderHidden(True)
        self.setSelectionMode(QTreeView.MultiSelection)
        self.setModel(backend.description_model)
        self.backend = backend
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

    def open_context_menu(self, position):
        indexes = self.selectedIndexes()
        menu = QMenu()
        model = self.backend.description_model
        if len(indexes) == 1:
            item = model.itemFromIndex(indexes[0])
            if isinstance(item, CollectionItem):
                menu.addAction(get_icon("is-file-add.svg"), self.tr("New description"),
                               lambda : self.new_description(item))
                menu.addAction(get_icon("is-file-search.svg"),self.tr("Add description"),
                               lambda : self.add_description(item))
            else:
                menu.addAction(get_icon("is-file-edit.svg"),self.tr("Edit description"),
                               lambda : DescriptionEditor.open_editor(item, self.backend))
                menu.addAction(get_icon("duplicate.svg"),self.tr("Duplicate description"),
                               lambda : model.duplicate_item(item))
                menu.addAction(get_icon("is-file-download.svg"),self.tr("Export description"),
                               lambda : self.export_description(item))
                menu.addAction(get_icon("delete.svg"),self.tr("Delete description"),
                               lambda : self.delete_items([item]))
        elif len(indexes) == 0:
            menu.addAction(get_icon("is-folder-add.svg"),self.tr("Create collection"),
                           lambda : model.create_collection_item("New collection"))
            menu.addAction(get_icon("is-archive-download.svg"),self.tr("Save to ZIP"),
                           self.export_all_to_zip)
            menu.addAction(get_icon("is-archive.svg"),self.tr("Import from ZIP"),
                           self.import_from_zip)

        menu.exec_(self.viewport().mapToGlobal(position))

    def new_description(self, collection: CollectionItem):
        model = self.backend.description_model
        item = model.create_description_item("New description", collection)
        DescriptionEditor.open_editor(item, self.backend)

    def add_description(self, collection):
        files, _ = QFileDialog.getOpenFileNames(self, "Add description")
        for file in files:
            self.backend.description_model.add_description_from_path(pathlib.Path(file), collection)

    def delete_items(self, items):

        for item in items:
            self.backend.description_model.delete_item(item)

    def export_all_to_zip(self):
        filename = QFileDialog.getSaveFileName(self, self.tr("Save to ZIP"),
            str(pathlib.Path.home() / "description_export.zip"))[0]
        self.backend.description_model.export_all_to_zip(filename)

    def import_from_zip(self):
        message_box = QMessageBox(self)
        message_box.setText(self.tr("Existing description can be overwritten. Do you want load description from ZIP?"))
        message_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        ret = message_box.exec_()
        if ret == QMessageBox.Ok:
            filename = QFileDialog.getOpenFileName(self, self.tr("Load from ZIP"))[0]
            self.backend.description_model.import_from_zip(filename)

    def export_description(self, item):
        filename = QFileDialog.getSaveFileName(self, self.tr("Select File for Export Description"),
                                               str(pathlib.Path.home() / "description.json"))[0]
        self.backend.description_model.export_description(filename, item)

    # def keyPressEvent(self, event):
    #     if event.key() == QtCore.Qt.Key_Delete:
    #         for indx in self.selectedIndexes():
    #             self.model().removeRow(indx.row())
    #     else:
    #         super(DescriptionView, self).keyPressEvent(event)

    # def dragEnterEvent(self, event):
    #     if event.mimeData().hasUrls:
    #         event.accept()
    #     else:
    #         event.ignore()
    #
    # def dragMoveEvent(self, event):
    #     if event.mimeData().hasUrls:
    #         event.accept()
    #     else:
    #         event.ignore()
    #
    # def dropEvent(self, event):
    #     if event.mimeData().hasUrls:
    #         event.accept()
    #         for url in event.mimeData().urls():
    #             path = pathlib.Path(str(url.toLocalFile()))
    #             self.backend.description_model.add_path(path)
    #     else:
    #         event.ignore()
