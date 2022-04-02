import copy
import json
import pathlib
from collections import UserList
from typing import Any, Union, Optional

import jsonschema

from jinrdatabaseloader.utils import JSON_SCHEMA


class TypeChecker:
    def __init__(self, type):
        self.type = type

    @property
    def is_bool(self):
        return self.type == "boolean"

    @property
    def is_str(self):
        return self.type == "string"

    @property
    def is_int(self):
        return self.type == "integer"


class Description:
    """Special wrapper on dict. Проверяет ключи на соответствие схеме и использует схему для выдачи дефолтных значений

    """
    _root_schema = None

    def __init__(self, data: dict, scheme: dict):
        self.data = data
        self.scheme = scheme

    def available_keys(self):
        return self.scheme["properties"].keys()

    def get_property_scheme(self, key) -> dict:
        self._check_key(key)
        return self.scheme["properties"][key]

    def avaiable_enum_values(self, key) -> Optional[list]:
        property = self.get_property_scheme(key)
        return property.get("enum")

    def property_type(self, key) -> TypeChecker:
        property = self.get_property_scheme(key)
        return TypeChecker(property["type"])

    def get_docs(self, key) -> str:
        return self.get_property_scheme(key).get("description", "")

    def _check_key(self, key):
        keys = self.scheme["properties"].keys()
        if key not in keys:
            raise KeyError("{} is'n valid key".format(key))
        return True

    def __getitem__(self, key):
        self._check_key(key)
        value = self.data.get(key)
        property = self.scheme["properties"][key]
        if property["type"] == "object":
            if value is None:
                value = {}
                self.data[key] = value
            return Description(value, property)
        elif property["type"] == "array":
            if isinstance(value, DescriptionList):
                return value

            schema = property["items"]
            if value is None:
                value = []
            value = DescriptionList.from_list(value, schema)
            self.data[key] = value
            return value
        else:
            if value is None:
                return property.get("default")
        return value

    def __setitem__(self, key, value):
        self._check_key(key)
        property = self.scheme["properties"][key]
        if not (property.get("default") == value):
            self.data[key] = value

    @classmethod
    def load_scheme(cls):
        if cls._root_schema is None:
            with open(JSON_SCHEMA) as fin:
                cls._root_schema = json.load(fin)
        return cls._root_schema

    @staticmethod
    def load(path: Union[str, pathlib.Path]):
        schema = Description.load_scheme()
        with open(path) as fin:
            description = json.load(fin)

        jsonschema.validate(description, schema=schema)
        return Description(description, schema)

    @staticmethod
    def empty():
        schema = Description.load_scheme()
        description = {"table" : "", "format": "CSV", "columns": [{"name" : "column 1", "type": "float"}]}
        jsonschema.validate(description, schema=schema)
        return Description(description, schema)

    def dump(self, path):
        with open(path, "w") as fout:
            json.dump(self, fout, cls=DescriptionEncoder)

    def clone(self):
        return Description(copy.deepcopy(self.data), self.scheme)


class DescriptionList(UserList):

    schema = None

    def add_description(self, item : dict):
        description = Description(item, self.schema)
        self.append(description)
        return description

    @staticmethod
    def from_list(data: list, schema: dict):
        if not isinstance(data, DescriptionList):
            new_list = DescriptionList()
            new_list.schema = schema
            for item in data:
                new_list.append(item)
            data = new_list
        for i in range(len(data)):
            item = data[i]
            if schema["type"] == "object" and not isinstance(item, Description):
                item = Description(item, schema)
                data[i] = item
        return data

class DescriptionEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Description):
            return obj.data
        elif isinstance(obj, DescriptionList):
            return obj.data
        return super(DescriptionEncoder, self).default(obj)