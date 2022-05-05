import abc
import csv
import dataclasses
import xml.etree.ElementTree as ET
from typing import Iterable, Any, List

from sdp.description import Description
from sdp.description_typing import DatabaseType, DEFAULT_PEEKER


@dataclasses.dataclass
class Column:
    name: str
    order: int # TODO(Unused)
    type: DatabaseType


class SourceReader(abc.ABC):

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
    def chunk_generator(self, source: Any, chunk_size: int) -> Iterable[List[dict]]:
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

    @staticmethod
    def _create_chunk_generator(row_iterator, row_parser, chunk_size) -> Iterable[List[dict]]:
        chunk = []
        for n, row in enumerate(row_iterator):
            chunk.append(row_parser(row))
            if (n + 1) % chunk_size == 0:
                yield chunk
                chunk = []
        if len(chunk) > 0:
            yield chunk


class CSVReader(SourceReader):

    def chunk_generator(self, source: Iterable[str], chunk_size: int = 500) -> Iterable[List[dict]]:
        reader = csv.reader(source, **self.parser_settings["CSV"].data)
        return SourceReader._create_chunk_generator(reader,
            lambda row: {column.name: item for column, item in zip(self.columns, row)},
                                                    chunk_size)


class XMLReader(SourceReader):

    @staticmethod
    def get_content(element : ET.Element)->str:
        """Extract content of element as string
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

    def chunk_generator(self, source: Any, chunk_size: int = 500) -> Iterable[List[dict]]:
        tree = ET.parse(source)
        root = tree.getroot()
        table = root.find(".//{*}tbody") # Find table body using XPath syntax
        settings = self.parser_settings["XML"]
        if settings["header"]:
            header = table[0]
            table.remove(header)
        return SourceReader._create_chunk_generator(table,
                lambda row: {column.name : column.type(self.get_content(item)) for column, item in zip(self.columns, row)},
                                                    chunk_size)

