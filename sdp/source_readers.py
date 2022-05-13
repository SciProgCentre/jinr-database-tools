import abc
import csv
import dataclasses
import xml.etree.ElementTree as ET
from typing import Iterable, Any, List, IO, Union

from sdp.description import Description
from sdp.description_typing import DatabaseType, DEFAULT_PEEKER


@dataclasses.dataclass
class Column:
    name: str
    order: int  # TODO(Unused)
    type: DatabaseType


class SourceReader(abc.ABC):
    """Base class for reading input data and
    represent every line of input table as dictionary using columns name as keys for table value
    """

    def __init__(self, description: Description):
        self.description = description
        self.parser_settings = description["parser_settings"]
        columns = description["columns"]
        self.columns = []
        for n_of_col, column in enumerate(columns):
            self.columns.append(
                Column(column["name"], column["order"],
                       DEFAULT_PEEKER.peek_from_column(column))
            )

    @abc.abstractmethod
    def parse_source(self, source: Union[Iterable[str]]) -> Iterable[dict]:
        """
        Convert input data to sequence of dictionary.
        Every dictionary used column names as key and input data as value
        """
        pass

    @staticmethod
    def get_reader(description: Description):
        source_format = description["format"]
        if source_format == "CSV":
            return CSVReader(description)
        elif source_format == "XML":
            return XMLReader(description)
        else:
            raise Exception("Unknown format")

    # @staticmethod
    # def _create_chunk_generator(row_iterator, row_parser, chunk_size) -> Iterable[List[dict]]:
    #     chunk = []
    #     for n, row in enumerate(row_iterator):
    #         chunk.append(row_parser(row))
    #         if (n + 1) % chunk_size == 0:
    #             yield chunk
    #             chunk = []
    #     if len(chunk) > 0:
    #         yield chunk


class CSVReader(SourceReader):
    """Reader for CSV files using module [csv]"""
    def parse_source(self, source: Iterable[str]) -> Iterable[dict]:
        reader = csv.reader(source, **self.parser_settings["CSV"].data)
        for row in reader:
            yield {column.name: item for column, item in zip(self.columns, row)}


class XMLReader(SourceReader):
    """Reader for XML files using [xml.etree]"""

    @staticmethod
    def get_content(element: ET.Element) -> str:
        """Extract content of element as raw string
        :param element:
        :return:
        """
        content = element.text
        if content is None:
            content = ""
        for item in element:
            content += ET.tostring(item).decode("UTF-8")
            if item.tail is not None:
                content += item.tail
        return content

    def parse_source(self, source: Any, chunk_size: int = 500) -> Iterable[dict]:
        tree = ET.parse(source)
        root = tree.getroot()
        table = root.find(".//{*}tbody")  # Find table body using XPath syntax
        settings = self.parser_settings["XML"]
        if settings["header"]:
            header = table[0]
            table.remove(header)
        for row in table:
            line = {column.name: column.type(self.get_content(item))
                        for column, item in zip(self.columns, row)}
            yield line

