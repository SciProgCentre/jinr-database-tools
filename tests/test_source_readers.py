from unittest import TestCase

from jinrdatabaseloader.description import Description
from jinrdatabaseloader.source_readers import CSVReader, XMLReader


class CVSReaderTest(TestCase):

    def setUp(self) -> None:
        description = Description.load("data/detector_.json")
        self.reader = CSVReader(description)

    def test_chunk_generator(self):
        with open("data/detector_.csv") as fin:
            for chunk in self.reader.chunk_generator(fin, 2):
                print(chunk)


class XMLReaderTest(TestCase):

    def setUp(self) -> None:
        description = Description.load("data/run_info.json")
        self.reader = XMLReader(description)

    def test_chunk_generator(self):
        with open("data/run_info.xml") as fin:
            for chunk in self.reader.chunk_generator(fin, 2):
                print(chunk)