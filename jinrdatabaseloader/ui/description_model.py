import abc
import os
import pathlib
import shutil
import typing
from typing import Optional, Callable

from PySide2 import QtCore
from PySide2.QtCore import QModelIndex, Qt
from PySide2.QtGui import QStandardItemModel, QStandardItem

from .utils import get_icon, FD_FOLDER, appdata
from ..description import Description


class Sender:
    _subscribers  = None

    def add_subscriber(self, event_type, subscriber: Callable):
        if self._subscribers is None:
            self._subscribers = {}
        subscribers_list = self._subscribers.get(event_type, [])
        subscribers_list.append(subscriber)
        self._subscribers[event_type] = subscribers_list

    def send(self, event_type):
        if self._subscribers is not None:
            subscriber_list = self._subscribers.get(event_type, [])
            for subscriber in subscriber_list:
                subscriber()


class PathItem(QStandardItem):

    FD_PATH = appdata() / FD_FOLDER
    NAME_ROLE = QtCore.Qt.DisplayRole
    DESCRIPTION_ROLE = QtCore.Qt.UserRole + 1
    REPRESENTATION_ROLE = DESCRIPTION_ROLE + 1
    PATH_ROLE = REPRESENTATION_ROLE + 1

    def __init__(self, name):
        super(PathItem, self).__init__()
        self.sender = Sender()
        self.setData(name, PathItem.NAME_ROLE)

    @property
    @abc.abstractmethod
    def path(self) -> pathlib.Path:
        pass

    @property
    def name(self):
        return self.data(PathItem.NAME_ROLE)

    @name.setter
    def name(self, value):
        self.setData(value, PathItem.NAME_ROLE)

    def data(self, role = QtCore.Qt.UserRole):
        if role == PathItem.PATH_ROLE:
            return self.path
        else:
            return super(PathItem, self).data(role)

    def setData(self, value, role=QtCore.Qt.UserRole):
        if role == PathItem.NAME_ROLE:
            old = self.data(PathItem.NAME_ROLE)
            if old is not None:
                self.change_name(value)
            super(PathItem, self).setData(value, PathItem.NAME_ROLE)
            self.sender.send(PathItem.NAME_ROLE)
        elif role == Qt.EditRole:
            self.setData(value, PathItem.NAME_ROLE)
        else:
            super(PathItem, self).setData(value, role)

    @abc.abstractmethod
    def change_name(self, new_name):
        pass

    @abc.abstractmethod
    def delete(self):
        pass


class CollectionItem(PathItem):
    def __init__(self, name):
        super(CollectionItem, self).__init__(name)
        self.setData(get_icon("is-folder-add.svg"), QtCore.Qt.DecorationRole)
        os.makedirs(self.path, exist_ok=True)

    def data(self, role = QtCore.Qt.UserRole):
        if role == PathItem.REPRESENTATION_ROLE:
            return "Collection: {}".format(self.path.name)
        else:
            return super(CollectionItem, self).data(role)

    def child_items(self) -> list["FDItem"]:
        return [self.child(row, 0) for row in range(self.rowCount())]

    @property
    def path(self):
        return PathItem.FD_PATH / self.data(PathItem.NAME_ROLE)

    def change_name(self, new_name):
        old_path = self.path
        new_path = PathItem.FD_PATH / new_name
        os.makedirs(new_path, exist_ok=True)
        for item in self.child_items():
            path = item.path
            shutil.move(path, new_path / path.name)
        os.removedirs(old_path)

    def delete(self):
        shutil.rmtree(self.path)


class FDItem(PathItem):
    JSON = ".json"

    def __init__(self, name, collection: CollectionItem, description : Optional[Description] = None):
        super(FDItem, self).__init__(name)
        self.collection = collection
        collection.appendRow(self)
        if description is None:
            description = Description.empty()
        self.setData(description, PathItem.DESCRIPTION_ROLE)

    def setData(self, value, role=QtCore.Qt.UserRole):
        if role == PathItem.DESCRIPTION_ROLE:
            value.dump(self.path)
        else:
            return super(FDItem, self).setData(value, role)

    def data(self, role = QtCore.Qt.UserRole):
        if role == PathItem.DESCRIPTION_ROLE:
            return Description.load(self.path)
        elif role == PathItem.REPRESENTATION_ROLE:
            return "Description: {}".format(self.path.name)
        else:
            return super(FDItem, self).data(role)

    @property
    def description(self):
        """Load copy of description content in item"""
        return self.data(PathItem.DESCRIPTION_ROLE)

    @property
    def path(self) -> pathlib.Path:
        name = self.data(PathItem.NAME_ROLE) + FDItem.JSON
        return self.collection.path / name

    def change_name(self, new_name):
        new_name = new_name + FDItem.JSON
        shutil.move(self.path, self.collection.path / new_name)

    def delete(self):
        os.remove(self.path)


class FDFilesTree(QStandardItemModel):
    def __init__(self):
        super(FDFilesTree, self).__init__()

    @property
    def default_collection(self):
        root = self.invisibleRootItem()
        if root.rowCount() == 0:
            item = self.create_collection_item("General")
            return item
        return root.child(0,0)

    def initialize(self):
        self.clear()
        if not PathItem.FD_PATH.exists():
            os.makedirs(PathItem.FD_PATH, exist_ok=True)
        for path in PathItem.FD_PATH.iterdir():
            self.add_collection_from_path(path)
        if self.invisibleRootItem().rowCount() == 0:
            self.create_collection_item("General")
        return 0

    def add_collection_from_path(self, path: pathlib.Path):
        if path.is_dir():
            item = self.create_collection_item(path.name)
            for sub_path in path.iterdir():
                if sub_path.is_file():
                    self.add_description_from_path(sub_path, item)

    def add_description_from_path(self, path: pathlib.Path, collection):
        self.create_description_item(path.stem, collection,  Description.load(path))

    @staticmethod
    def check_name(item, name):
        for i in range(item.rowCount()):
            child_item = item.child(i)
            if name == child_item.data(QtCore.Qt.DisplayRole):
                return False
        return True

    @staticmethod
    def _resolve_name(item, name):
        base_name = name
        count = 1
        while True:
            if FDFilesTree.check_name(item, name):
                break
            else:
                name = base_name + " ({:d})".format(count)
            count += 1
        return name

    def create_collection_item(self, name)-> CollectionItem:
        name = FDFilesTree._resolve_name(self.invisibleRootItem(), name)
        item = CollectionItem(name)
        self.invisibleRootItem().appendRow(item)
        return item

    @staticmethod
    def create_description_item(name, collection: CollectionItem, description: dict = None) -> FDItem:
        name = FDFilesTree._resolve_name(collection, name)
        item = FDItem(name, collection, description)
        return item

    def delete_item(self, item: PathItem):
        item.delete()
        if not isinstance(item, CollectionItem):
            self.removeRow(item.row(), parent=item.parent().index())
        else:
            self.removeRow(item.row())

    # def keyPressEvent(self, event):
    #     if event.key() == QtCore.Qt.Key_Delete:
    #         self.delete_descriptions()
    #     elif event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
    #         items = self.selectedItems()
    #         for item in items:
    #             if isinstance(item, CollectionItem):
    #                 item.setExpanded(not item.isExpanded())
    #     else:
    #         super().keyPressEvent(event)
    #

    def duplicate_item(self, item: PathItem):
        if isinstance(item, FDItem):
            self.create_description_item(item.name, item.collection, item.description)

    def create_collection(self):
        self.create_collection_item("New collection")

    @staticmethod
    def export_all_to_zip(filename):
        shutil.make_archive(filename, "zip", PathItem.FD_PATH)

    @staticmethod
    def export_description(filename, item):
        description = item.description
        description.dump(filename)

    def import_from_zip(self, filename):
        shutil.unpack_archive(filename, PathItem.FD_PATH, "zip")
        self.initialize()


