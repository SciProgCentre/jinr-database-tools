import json
import logging
import os.path
import pathlib
import webbrowser

import jsonschema
from json_schema_for_humans.generate import generate_from_file_object

ROOT_DIR = pathlib.Path(__file__).parent
JSON_SCHEMA = ROOT_DIR / "resources" / "schema.json"


def get_json_schema_docs(output: pathlib.Path):
    with JSON_SCHEMA.open() as fin, output.open("w") as fout:
        generate_from_file_object(fin, fout)
    return output


def open_help_html(html_path):
    html_path = pathlib.Path(html_path).absolute()
    json_time = os.path.getmtime(JSON_SCHEMA)
    if not html_path.exists() or json_time > os.path.getmtime(html_path):
        get_json_schema_docs(html_path)
    webbrowser.open_new_tab(html_path.as_uri())
    return 0


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    ERROR = FAIL + "ERROR" + ENDC
    EXCEPTION = FAIL + "EXCEPTION" + ENDC
