import shutil
import sys
from unittest import TestCase

from jinrdatabaseloader.description import Description
from jinrdatabaseloader.ui.app import DatabaseApp
from jinrdatabaseloader.ui.description_editor import DescriptionEditor, ColumnsEditor, ColumnWidget
from jinrdatabaseloader.ui.description_model import PathItem
from jinrdatabaseloader.ui.utils import appdata


class BackendTest(TestCase):

    def setUp(self) -> None:
        shutil.rmtree(PathItem.FD_PATH / "Test", ignore_errors=True)
        self.app = DatabaseApp(sys.argv)
        self.backend = self.app.backend

    def test_settings(self):
        settings = self.backend.settings
        self.backend.settings.update_application_settings()

    def test_json_help(self):
        self.backend.open_help_html()

    def test_appdata(self):
        path = appdata()
        print(path)


class EditorTest(TestCase):

    def setUp(self) -> None:
        shutil.rmtree(PathItem.FD_PATH / "Test", ignore_errors=True)
        self.app = DatabaseApp(sys.argv)
        self.collection = self.app.backend.description_model.create_collection_item("Test")
        self.item = self.app.backend.description_model.create_description_item("test", self.collection, Description.empty())


    def test_editor(self):
        widget = DescriptionEditor(self.item, self.app.backend)
        self.app.apply_material()
        widget.show()
        self.app.exec_()

    def test_columns_editor(self):
        widget = ColumnsEditor(self.item.description["columns"], self.app.backend)
        widget.show()
        self.app.exec_()

    def test_column_widget(self):
        widget = ColumnWidget(self.item.description["columns"][0], self.app.backend)
        widget.show()
        self.app.exec_()

    def tearDown(self) -> None:
        shutil.rmtree(PathItem.FD_PATH / "Test", ignore_errors=True)
