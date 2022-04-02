import dataclasses
import json
import logging
import pathlib
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

from sqlalchemy import create_engine, MetaData, insert
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL

from jinrdatabaseloader.description import Description
from jinrdatabaseloader.description_typing import TypePeeker, DEFAULT_PEEKER
from jinrdatabaseloader.source_readers import SourceReader
from jinrdatabaseloader.file_status import LoadStatus, LoadResult


class Drivers(Enum):
    POSTGRES = "postgresql"
    POSTGRES_PSYCOPG2 = "postgresql+psycopg2"
    POSTGRES_PG8000 = "postgresql+pg8000"
    MYSQL = "mysql"
    ORACLE = "oracle"
    MICROSOFT_SQL_PYODBC = "mssql+pyodbc"
    MICROSOFT_SQL_PYMSSQL = "mssql+pymssql"
    SQLITE = "sqlite"


@dataclass
class DatabaseSettings:
    drivername: Drivers = Drivers.POSTGRES_PSYCOPG2
    host: str = "localhost"
    port: Optional[int] = None
    database: str = "postgres"
    username: str = "postgres"
    password: str = ""

    def to_url(self):
        settings = dataclasses.asdict(self)
        settings["drivername"] = self.drivername.value
        return URL(**settings)


class Database:
    engine: Optional[Engine] = None

    def __init__(self, settings: DatabaseSettings = None, type_peeker: TypePeeker = DEFAULT_PEEKER, echo=False):
        """
        Main class for interaction with database
        """
        self.engine_args = {"echo": echo}
        self.type_peeker = type_peeker
        self.settings = None
        self.url = None
        if settings is not None:
            self.update_engine(settings)

    def update_engine(self, settings: DatabaseSettings):
        self.settings = settings
        self.url = settings.to_url()
        logging.debug(self.url)
        self.engine = create_engine(self.url, **self.engine_args)

    def test_connect(self) -> bool:
        conn = None
        try:
            conn = self.engine.connect()
            return True
        except Exception as e:
            logging.debug(e)
            return False
        finally:
            if conn is not None:
                conn.close()

    @property
    def tables_name(self):
        return self.engine.table_names()

    def table_columns(self, name) -> list[str]:
        try:
            with self.engine.connect() as conn:
                metadata = MetaData(bind=conn, reflect=True)
                table = metadata.tables[name]
                return table.c.keys()
        except Exception:
            return []

    def check_description(self, description: Description):
        base_table = description["table"]
        errors = []
        if base_table not in self.engine.table_names():
            errors.append("Table {} doesn't exist in database {}."
                          .format(base_table, self.url))

        if len(errors) == 0:
            with self.engine.connect() as conn:
                metadata = MetaData(bind=conn,  reflect=True)
                table = metadata.tables[base_table]
                table_keys = table.c.keys()
                columns = description["columns"]
                for column in columns:
                    name = column["name"]
                    if name not in table_keys:
                        errors.append("Column {} doesn't exist in table {}".format(name, base_table))
                    else:
                        database_column = table.c[name]
                        generic_type = self.type_peeker.peek(column["type"], column["type_properties"])
                        if not generic_type.is_target(database_column.type):
                            errors.append("Column {} have type \"{}\", when target column have type \"{}\"".format(
                                name, column["type"], database_column.type
                            ))
        return errors

    def _load_data(self, conn, description: Description, source):
        metadata = MetaData(bind=conn, reflect=True)
        table = metadata.tables[description["table"]]
        reader = SourceReader.get_reader(description)
        for chunk in reader.chunk_generator(source):
            stmt = insert(table, values=chunk)
            result = conn.execute(stmt)

    def load_data(self, description: Description, source: Union[pathlib.Path, str]) -> LoadResult:
        """
        :param description: Словарь с описывающий формат файла
        :param source: Путь к файлу
        :return: FileStatus.SUCCESS если удалось успешно загрузить файл в базу, иначе FileStatus.REJECTED
        """
        errors = self.check_description(description)
        if len(errors) != 0:
            return LoadResult(LoadStatus.REJECTED, errors)

        with self.engine.connect() as conn:
            try:
                if isinstance(source, str):
                    source = pathlib.Path(source)
                if isinstance(source, pathlib.Path):
                    if not source.exists():
                        return LoadResult(LoadStatus.DELETED)
                    with source.open() as fin:
                        self._load_data(conn, description, fin)
            except Exception as e:
                logging.warning(e)
                return LoadResult(LoadStatus.REJECTED, exceptions=[e])

        return LoadResult(LoadStatus.SUCCESS)

    @staticmethod
    def connect_from_file(config):
        with open(config) as fin:
            config = json.load(fin)
        database_settings = DatabaseSettings(**config["database"])
        database = Database(database_settings)
        if not database.test_connect():
            logging.warning("Bad database connection!")
            return None
        return database
