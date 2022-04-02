import json
import logging
import pathlib
from typing import Union, TextIO

from sqlalchemy import MetaData

from jinrdatabaseloader.database import Database
from jinrdatabaseloader.description_typing import DEFAULT_PEEKER, DatabaseType


def walk_database(database : Database):
    with database.engine.connect() as conn:
        metadata = MetaData(bind=conn, reflect=True)
        for name, table in metadata.tables.items():
            for column_name, column in table.c.items():
                yield table, column


def generate_descriptions(database: Database, out_folder: pathlib.Path):
    description = {
        "format" : "CSV"
    }
    with database.engine.connect() as conn:
        metadata = MetaData(bind=conn, reflect=True)
        for name, table in metadata.tables.items():
            logging.debug("Table {}".format(name))
            description["table"] = name
            columns = []
            for column_name, column in table.c.items():
                item = {"name" : column_name}
                item.update(DatabaseType.from_sqlalchemy_type(column.type).to_dict())
                columns.append(item)
            description["columns"] = columns
            with open(out_folder / "{}.json".format(name), "w") as fout:
                json.dump(description, fout, indent=2)
    return 0


def generate_fake_data(file: Union[str, pathlib.Path, TextIO], description: dict, peeker = DEFAULT_PEEKER):
    typers = [ peeker.peek_from_column(column) for column in description["columns"] ]
    for i in range(10):
        file.write(",".join(map(lambda typer: typer.represent(i), typers)))
        file.write("\n")
    return 0