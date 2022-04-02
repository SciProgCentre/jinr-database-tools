from unittest import TestCase

from jinrdatabaseloader.database import Database
from jinrdatabaseloader.description import Description
from jinrdatabaseloader.file_status import LoadStatus


class CVSReaderTest(TestCase):

    def setUp(self) -> None:
        self.database = Database.connect_from_file("config.json")

    def _test_file(self, desc, file):
        description = Description.load("data/detector_.json")
        load_result = self.database.load_data(description, file)
        self.assert_(load_result.status == LoadStatus.SUCCESS,
                     msg= load_result.to_string())

    def test_csv(self):
        self._test_file("data/detector_.json", "data/detector_.csv")

    def test_xml(self):
        # FIXME(Нет подходящей таблицы)
        self._test_file("data/run_info.json", "data/run_info.xml")