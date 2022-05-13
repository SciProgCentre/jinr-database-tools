import logging
import pathlib
import shutil
import sys
from tempfile import NamedTemporaryFile

from PySide2.QtCore import QItemSelectionModel

from sdp.database import FakeDatabase
from sdp.description import Description
from sdp.ui.app import DatabaseApp
from sdp.ui.backend import Backend
from sdp.ui.central_widget import CentralWidget
from sdp.ui.description_model import PathItem
from sdp.ui.settings import Settings

ROOT_PATH = pathlib.Path(__file__).parent
DATA_PATH = ROOT_PATH / ".." / "data"

def main():
    logging.root.setLevel(logging.DEBUG)
    app = DatabaseApp(sys.argv)
    settings = Settings()
    backend = Backend(settings, FakeDatabase)
    widget = CentralWidget(backend)

    shutil.rmtree(PathItem.FD_PATH / "Test", ignore_errors=True)
    collection = backend.description_model.create_collection_item("Test")
    item = backend.description_model.create_description_item("test", collection, Description.empty())
    widget.description_view.selectionModel().select(item.index(), QItemSelectionModel.ClearAndSelect)
    # backend.current_description_item = item

    for i in range(10):
        temp_file = NamedTemporaryFile()
        path = pathlib.Path(temp_file.name)
        backend.files_model.add_path(path)

    widget.show()
    app.exec_()

    shutil.rmtree(PathItem.FD_PATH / "Test", ignore_errors=True)

    return 0


if __name__ == '__main__':
    main()