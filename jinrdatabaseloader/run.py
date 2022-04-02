import argparse
import logging
import pathlib
import sys

import jsonschema

from jinrdatabaseloader.database import Database
from jinrdatabaseloader.description import Description
from jinrdatabaseloader.utils import open_help_html
from jinrdatabaseloader.dev_utils import generate_descriptions, generate_fake_data
from jinrdatabaseloader.ui.app import DatabaseApp


class DebugAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in self.option_strings:
            logging.root.setLevel(logging.DEBUG)


def create_parser():
    parser = argparse.ArgumentParser(description='Add file to database.')
    parser.add_argument("--debug", action=DebugAction, nargs=0, help=argparse.SUPPRESS)

    subparsers = parser.add_subparsers(metavar="command", required=True)

    parser_validate = subparsers.add_parser("validate", help="Validate json file")
    parser_validate.add_argument("descriptions", nargs="+", metavar="JSON_DESCRIPTIONS")
    parser_validate.set_defaults(func=validate)

    parser_load = subparsers.add_parser("load", help="Load file to database")
    parser_load.add_argument("files", nargs="+", metavar="FILE")
    parser_load.add_argument("-c", "--config", action="store", default="config.json",
                             help="Configuration file with database settings")
    parser_load.add_argument("-d", "--description", action="store", required=True,
                             metavar="JSON_DESCRIPTION", help="JSON description of data")
    parser_load.set_defaults(func = load_to_database)


    parser_schema = subparsers.add_parser("json_schema",
                                          help="Open HTML documentation for JSON Schema")
    parser_schema.set_defaults(func=lambda x: open_help_html("scheme.html"))

    parser_gen = subparsers.add_parser("generate", help="Generate json templates from database")
    parser_gen.add_argument("-c", "--config", action="store", default="config.json",
                             help="Configuration file with database settings")
    parser_gen.set_defaults(func=generate)

    parser_load = subparsers.add_parser("generate_fake_data")
    parser_load.add_argument("descriptions", nargs="+", metavar="JSON_DESCRIPTIONS")
    parser_load.set_defaults(func = generate_fake_data_from_description)
    return parser


def validate(args):
    for file in args.descriptions:
        load_description(file)
    return 0


def load_description(path):
    try:
        description = Description.load(path)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        return None
    print(path, "successfully validated.")
    return description


def load_to_database(args):

    description = load_description(args.description)

    if description is None:
        return 1

    for file in args.files:
        path = pathlib.Path(file)
        if not path.exists():
            print("File {} doesn't exist!".format(path))
            continue

        database = Database.connect_from_file(args.config)
        if database is None:
            print("Can't connect to database")
            return 1

        load_result = database.load_data(description, path)
        print(load_result.to_string())
    return 0


def generate(args):
    database = Database.connect_from_file(args.config)
    if database is None:
        return 1
    generate_descriptions(database, pathlib.Path("."))
    return 0


def generate_fake_data_from_description(args):
    for description_name in args.descriptions:
        description = load_description(description_name)

        if description is None:
            return 1

        with open(pathlib.Path(description_name).stem + ".csv", "w") as fout:
            generate_fake_data(fout, description)
    return 0


def console_app():
    parser = create_parser()
    args = parser.parse_args()
    if "func" in args: # Check subcommand function argument
        args.func(args)
    else:
        parser.print_help()
    return 0


def gui_app():
    app = DatabaseApp(sys.argv)
    app.start_main_window()
    return sys.exit(app.exec_())