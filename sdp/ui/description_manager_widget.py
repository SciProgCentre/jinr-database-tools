import pathlib

from PySide2 import QtCore
from PySide2.QtCore import QItemSelectionModel
from PySide2.QtWidgets import QTreeView, QMenu, QFileDialog, QMessageBox

from sdp.ui.backend import Backend
from sdp.ui.description_editor import DescriptionEditor
from sdp.ui.description_model import CollectionItem, FDItem
from sdp.ui.utils import get_icon


class DescriptionView(QTreeView):
    def __init__(self, backend: Backend):
        super(DescriptionView, self).__init__()
        self.backend = backend
        self.fd_model = self.backend.description_model
        self.setModel(self.fd_model)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setHeaderHidden(True)
        self.setSelectionMode(QTreeView.SingleSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)
        self.selectionModel().currentChanged.connect(self.selection_change)
        self.init_context_menus()

    def selection_change(self, curr_index, prev_index):
        if curr_index.isValid():
            item = self._item(curr_index)
            if isinstance(item, FDItem):
                self.backend.current_description_item = item
            else:
                self.backend.current_description_item = None

    def init_context_menus(self):
        self.descritpion_menu = QMenu()
        self.descritpion_menu.addAction(get_icon("is-file-edit.svg"), self.tr("Edit description"),
                       lambda: DescriptionEditor.open_editor(self.context_item, self.backend))
        self.descritpion_menu.addAction(get_icon("duplicate.svg"), self.tr("Duplicate description"),
                       lambda: self.fd_model.duplicate_item(self.context_item))
        self.descritpion_menu.addAction(get_icon("is-file-download.svg"), self.tr("Export description"),
                       lambda: self.export_description(self.context_item))
        self.descritpion_menu.addAction(get_icon("delete.svg"), self.tr("Delete description"),
                       lambda: self.delete_items([self.context_item]))

        self.collection_menu = QMenu()
        self.collection_menu.addAction(get_icon("is-file-add.svg"), self.tr("New description"),
                       lambda: self.new_description(self.context_item))
        self.collection_menu.addAction(get_icon("is-file-search.svg"), self.tr("Add description"),
                       lambda: self.add_description(self.context_item))
        self.collection_menu.addSeparator()
        self.collection_menu.addAction(get_icon("delete.svg"), self.tr("Delete collection"),
                       lambda: self.delete_items([self.context_item]))

        self.root_menu = QMenu()
        self.root_menu.addAction(get_icon("is-folder-add.svg"), self.tr("Create collection"),
                       lambda: self.fd_model.create_collection_item("New collection"))
        self.root_menu.addAction(get_icon("is-archive-download.svg"), self.tr("Save to ZIP"),
                       self.export_all_to_zip)
        self.root_menu.addAction(get_icon("is-archive.svg"), self.tr("Import from ZIP"),
                       self.import_from_zip)

    def open_context_menu(self, position):
        index = self.indexAt(position)
        if index.isValid():
            self.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)
            self.context_item = self._item(index)
            if isinstance(self.context_item, CollectionItem):
                menu = self.collection_menu
            else:
                menu = self.descritpion_menu
        else:
            menu = self.root_menu
        menu.exec_(self.viewport().mapToGlobal(position))

    def new_description(self, collection: CollectionItem):
        item = self.fd_model.create_description_item("New description", collection)
        DescriptionEditor.open_editor(item, self.backend)

    def add_description(self, collection):
        files, _ = QFileDialog.getOpenFileNames(self, "Add description")
        for file in files:
            self.fd_model.add_description_from_path(pathlib.Path(file), collection)

    def delete_items(self, items):
        text = self.tr("Do you really want to remove these items:")
        text += "\n" + "\n".join(map(lambda x: x.name, items))
        ret = QMessageBox.question(self, self.tr("Delete items"), text)
        if ret == QMessageBox.Yes:
            for item in items:
                self.fd_model.delete_item(item)

    def export_all_to_zip(self):
        filename = QFileDialog.getSaveFileName(self, self.tr("Save to ZIP"),
            str(pathlib.Path.home() / "description_export.zip"))[0]
        self.fd_model.export_all_to_zip(filename)

    def import_from_zip(self):
        ret = QMessageBox.question(self, self.tr("Existing description can be overwritten. Do you want load description from ZIP?"))
        if ret == QMessageBox.Yes:
            filename = QFileDialog.getOpenFileName(self, self.tr("Load from ZIP"))[0]
            self.fd_model.import_from_zip(filename)

    def export_description(self, item):
        filename = QFileDialog.getSaveFileName(self, self.tr("Select File for Export Description"),
                                               str(pathlib.Path.home() / "description.json"))[0]
        self.fd_model.export_description(filename, item)

    # def keyPressEvent(self, event):
    #     if event.key() == QtCore.Qt.Key_Delete:
    #         for indx in self.selectedIndexes():
    #             self.model().removeRow(indx.row())
    #     else:
    #         super(DescriptionView, self).keyPressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
            index = self.indexAt(event.pos())
            if index.isValid():
                item = self._item(index)
                if not isinstance(item, CollectionItem):
                    index = index.parent()
            else:
                index  = self.fd_model.default_collection.index()
            self.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
            index = self.indexAt(event.pos())
            if index.isValid():
                item = self._item(index)
                if isinstance(item, CollectionItem):
                    target = item
                else:
                    target = item.parent()
            else:
                target = self.fd_model.default_collection
            for url in event.mimeData().urls():
                path = pathlib.Path(str(url.toLocalFile()))
                self.fd_model.add_description_from_path(path, target)
        else:
            event.ignore()

    def _item(self, index):
        return self.fd_model.itemFromIndex(index)
