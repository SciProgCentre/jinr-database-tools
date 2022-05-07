from unittest import TestCase

from sqlalchemy import delete

from sdp.database import Database
from sdp.description import Description
from sdp.file_status import LoadStatus


class DatabaseTest(TestCase):

    def setUp(self) -> None:
        self.database = Database.connect_from_file("config.json")

    def test_csv(self):
        description = Description.load("data/detector_.json")
        load_result = self.database.load_data(description, "data/detector_.csv")
        self.assert_(load_result.status == LoadStatus.SUCCESS,
                     msg= load_result.to_string("data/detector_.csv"))
        # if load_result.status == LoadStatus.SUCCESS:
            # self.test_clear_detector_()

    def test_clear_detector_(self):
        description = Description.load("data/detector_.json")
        with self.database.engine.connect() as conn:
            metadata = self.database._metadata(conn)
            for i in range(10):
                table = metadata.tables[description["table"]]
                statement = delete(table).where(
                    table.c.detector_name == "\'{}\'".format(str(i))
                )
                conn.execute(statement)

    def test_xml(self):
        # FIXME(Нет подходящей таблицы)
        description = Description.load("data/run_info.json")
        load_result = self.database.load_data(description, "data/run_info.xml")