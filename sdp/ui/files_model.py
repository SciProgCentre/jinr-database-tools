import pathlib
from typing import Optional

from PySide2.QtCore import Slot, QSortFilterProxyModel, QModelIndex
from PySide2.QtGui import QStandardItem, QStandardItemModel
from PySide2 import QtCore

from ..file_status import LoadStatus
from .utils import get_icon


class FileItem(QStandardItem):

    PATH_ROLE =  QtCore.Qt.UserRole + 1
    STATUS_ROLE = PATH_ROLE + 1

    def __init__(self, path: pathlib.Path, level: int):
        super(FileItem, self).__init__()
        self.setEditable(False)
        self.path = path
        self.setData(path, FileItem.PATH_ROLE)
        self.status = LoadStatus.NEW
        self._level = level
        self.level = level

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self._level = max(self._level, value)
        text = "/".join(self.path.parts[-self._level:])
        self.setData(text, QtCore.Qt.DisplayRole)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
        icon = get_icon(FileItem.status_to_icon(value))
        self.setData(icon, QtCore.Qt.DecorationRole)
        self.setData(self._status, FileItem.STATUS_ROLE)

    @staticmethod
    def status_to_icon(status):
        if status == LoadStatus.NEW:
            tail = "status-add.svg"
        elif status == LoadStatus.SUCCESS:
            tail= "status-success.svg"
        elif status == LoadStatus.DELETED:
            tail = "status-error.svg"
        else:
            tail = "status-error.svg"
        return tail


class FilesModel(QStandardItemModel):
    def __init__(self):
        super(FilesModel, self).__init__()

    @Slot()
    def clear_loaded(self):
        items = []
        for row in range(self.rowCount()):
            item = self.item(row)
            if item.status == LoadStatus.SUCCESS:
                items.append(item)
        for item in items:
            self.removeRow(item.row())
    @Slot()
    def clear(self):
        super(FilesModel, self).clear()

    @Slot(str)
    def add_path(self, path: pathlib.Path) -> Optional[FileItem]:
        if path.is_dir():
            for child in path.iterdir():
                self.add_path(child)
            return None

        for i in range(self.rowCount()):
            item = self.item(i)
            if item.path == path:
                return None

        lvl = self._check_path(path)

        root = self.invisibleRootItem()
        item = FileItem(path, lvl)
        root.appendRow(item)
        return item

    def _check_path(self, path):

        def check_names(path1: pathlib.Path, path2: pathlib.Path, lvl: int = 1):
            return check_names(path1.parent, path2.parent, lvl + 1) if path1.name == path2.name else lvl

        max_lvl = 1
        for i in range(self.rowCount()):
            item = self.item(i)
            lvl = check_names(path, item.path)
            item.level = lvl
            max_lvl = max(max_lvl, lvl)
        return max_lvl


class ProxyFilesModel(QSortFilterProxyModel):
    def __init__(self, model, loaded: bool = True):
        super(ProxyFilesModel, self).__init__()
        self.setSourceModel(model)
        self.loaded = loaded

    def filterAcceptsColumn(self, source_column:int, source_parent: QModelIndex) -> bool:
        return True

    def filterAcceptsRow(self, source_row:int, source_parent: QModelIndex) -> bool:
        item = self.sourceModel().index(source_row, 0, source_parent)
        if self.loaded:
            return item.data(FileItem.STATUS_ROLE) == LoadStatus.SUCCESS
        else:
            return item.data(FileItem.STATUS_ROLE) != LoadStatus.SUCCESS

    def lessThan(self, source_left: QModelIndex, source_right: QModelIndex) -> bool:
        return True