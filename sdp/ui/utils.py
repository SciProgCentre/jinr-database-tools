import abc
import dataclasses
import os
import pathlib
import typing
from enum import Enum
from typing import Optional

from PySide2.QtCore import QUrl, QStandardPaths, QObject, Signal
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QHBoxLayout, QWidget, QLayout, QBoxLayout, QLineEdit, QPushButton, QComboBox, QVBoxLayout

ORGANIZATION_NAME = "NPM_Group"
ORGANIZATION_DOMAIN = "npm.mipt.ru"
APPLICATION_NAME = "Smart Data Parser"
FD_FOLDER =  "FileDescriptions"
ROOT_DIR = pathlib.Path(__file__).parent
CSS_PATH = ROOT_DIR / "resources" / "material.css"

def appdata():
    path = pathlib.Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
    sub_path = pathlib.Path(ORGANIZATION_NAME) / APPLICATION_NAME
    if not path.match(str(sub_path)):
        path = path / sub_path
    if not path.exists():
        os.makedirs(path, exist_ok=True)
    return path


def resolve_path(path):
    print(path)
    if isinstance(path, str):
        path = QUrl(path).toLocalFile()
        print(path)
    return pathlib.Path(path).absolute()


def get_icon(id) -> QIcon:
    path = ROOT_DIR / "resources" / "icons"
    return QIcon(str(path / id))


class FieldEditor(QObject):
    updated = Signal()

    @property
    def widget(self):
        return self._editor

    @staticmethod
    def create_field_editor(obj, field: dataclasses.Field):
        if field.type == str:
            return StrFieldEditor(obj, field)
        if field.type == Optional[int] or field.type == int:
            return IntFieldEditor(obj, field)
        if issubclass(field.type, Enum):
            return EnumFieldEditor(obj, field)


class StrFieldEditor(FieldEditor):

    def __init__(self, obj, field):
        super(StrFieldEditor, self).__init__()
        self._editor = QLineEdit( obj.__getattribute__(field.name))

        def finish():
            obj.__setattr__( field.name, self._editor.text())
            self.updated.emit()

        self._editor.editingFinished.connect(finish)


class EnumFieldEditor(FieldEditor):

    def __init__(self, obj, field):
        super(EnumFieldEditor, self).__init__()
        self._editor = QComboBox()
        for item in field.type:
            self._editor.addItem(item.value)
        indx = self._editor.findText(obj.__getattribute__(field.name).value)
        self._editor.setCurrentIndex(indx)

        def select():
            obj.__setattr__(field.name, field.type(self._editor.currentText()))
            self.updated.emit()

        self._editor.textActivated.connect(select)


class IntFieldEditor(FieldEditor):

    def __init__(self, obj, field):
        #TODO(INT validator)
        super(IntFieldEditor, self).__init__()
        self._editor = QLineEdit(str(obj.__getattribute__(field.name)))

        def finish():
            try:
                obj.__setattr__(field.name, int(self._editor.text()))
                self.updated.emit()
            except ValueError:
                pass

        self._editor.editingFinished.connect(finish)


def _box(factory,  *args, parent = None):
    if parent is not None:
        if isinstance(parent, QWidget):
            box = factory(parent)
        elif isinstance(parent, QBoxLayout):
            box = factory()
            parent.addLayout(box)
    else:
        box = factory()
    for arg in args:
        if isinstance(arg, tuple):
            box.addWidget(*arg)
        else:
            if isinstance(arg, QWidget):
                box.addWidget(arg)
            elif isinstance(arg, QLayout):
                box.addLayout(arg)
    return box


def hbox(*args, parent = None) -> QHBoxLayout:
    return _box(QHBoxLayout, *args, parent=parent)


def vbox( *args, parent = None) -> QVBoxLayout:
    return _box(QVBoxLayout, *args, parent = parent)


def button(parent, text, icon = None, action = None):
    if icon is not None:
        button = QPushButton(icon, text)
    else:
        button = QPushButton(text)
    if isinstance(parent, QLayout):
        parent.addWidget(button)
    if action is not None:
        button.clicked.connect(action)
    return button