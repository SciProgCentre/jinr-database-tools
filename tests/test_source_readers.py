import unittest
from unittest import TestCase

from sdp.description import Description
from sdp.source_readers import CSVReader, XMLReader


class CSVReaderTest(TestCase):

    def setUp(self) -> None:
        description = Description.load("data/detector_.json")
        self.reader = CSVReader(description)

    def test_chunk_generator(self):
        with open("data/detector_.csv") as fin:
            for row in self.reader.parse_source(fin):
                print(row)


class XMLReaderTest(TestCase):

    def setUp(self) -> None:
        description = Description.load("data/run_info.json")
        self.reader = XMLReader(description)

    def test_chunk_generator(self):
        with open("data/run_info.xml") as fin:
            for row in self.reader.parse_source(fin):
                print(row)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(CSVReaderTest())
    suite.addTest(XMLReaderTest())
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())