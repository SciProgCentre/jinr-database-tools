import abc
import datetime
from abc import ABC
from typing import Callable, Optional, Any, Union, Type
import sqlalchemy.types

from jinrdatabaseloader.description import Description


class DatabaseType:

    def __init__(self, name, properties: Optional[Description] = None):
        self.name = name
        self.properties = properties

    @abc.abstractmethod
    def __call__(self, value: str) -> Any:
        pass

    @abc.abstractmethod
    def is_target(self, other: sqlalchemy.types.TypeEngine) -> bool:
        pass

    def represent(self, value) -> str:
        return str(value)

    def to_dict(self):
        result = {"type": self.name}
        if self.properties is not None:
            result["type_properties"] = self.properties
        return result

    @staticmethod
    def is_sqlalchemy_type(other: sqlalchemy.types.TypeEngine) -> bool:
        return isinstance(other, sqlalchemy.types.TypeEngine)

    @staticmethod
    def from_sqlalchemy_type(type_: sqlalchemy.types.TypeEngine) -> Optional["DatabaseType"]:
        if type_.python_type is not None:
            for name, value in PrimitiveTypePeeker.type.items():
                if type_.python_type is value:
                    return PrimitiveType(name, value)
            if type_.python_type is datetime.datetime:
                return ISODatetimeType()
        return DatabaseType("None")


class PrimitiveType(DatabaseType):

    def represent(self, value) -> str:
        if not isinstance(value, self.type):
            value = self(str(value))
        return repr(value)

    def __init__(self, name, python_type: Union[Type, Callable], properties: Optional[Description] = None):
        super(PrimitiveType, self).__init__(name, properties)
        self.type = python_type

    def __call__(self, value: str):
        if isinstance(self.type, bytes):
            return bytes(value, encoding=self.properties["encoding"])
        return self.type(value)

    def is_target(self, other):
        if DatabaseType.is_sqlalchemy_type(other):
            return self.type == other.python_type
        else:
            return False


class DatetimeType(DatabaseType, ABC):

    def __init__(self,  properties: Optional[Description] = None):
        super(DatetimeType, self).__init__("datetime", properties)

    def is_target(self, other: sqlalchemy.types.TypeEngine) -> bool:
        return isinstance(other, sqlalchemy.types.DateTime)


class ISODatetimeType(DatetimeType):

    def __init__(self):
        super(ISODatetimeType, self).__init__({"datetime_flavour": "iso"})

    def __call__(self, value: str) -> Any:
        return datetime.datetime.fromisoformat(value)


class TypePeeker(abc.ABC):

    @abc.abstractmethod
    def peek(self, name: str, properties: Optional[Description] = None) -> Optional[DatabaseType]:
        pass

    def peek_from_column(self, column: Description) -> Optional[DatabaseType]:
        return self.peek(column["type"], column["type_properties"])


class ListTypePeeker(TypePeeker):

    def __init__(self, *args: TypePeeker):
        self.peekers = list(args)

    def register(self, peeker: TypePeeker):
        self.peekers.append(peeker)

    def peek(self, name: str, properties: Optional[Description] = None) -> Optional[DatabaseType]:
        for peeker in self.peekers:
            type_ = peeker.peek(name, properties)
            if type_ is not None:
                return type_
        return None


class PrimitiveTypePeeker(TypePeeker):
    type = {
        "boolean": bool,
        "integer": int,
        "float": float,
        "string": str,
        "binary": bytes,
    }

    def peek(self, name: str, properties: Optional[Description] = None) -> Optional[DatabaseType]:
        if name not in self.type.keys():
            return None
        return PrimitiveType(name, self.type[name], properties)


class DatetimePeeker(TypePeeker):

    def peek(self, name: str, properties: Optional[Description] = None) -> Optional[DatabaseType]:
        if name != "datetime":
            return None
        flavour = properties["datetime_flavour"]
        if flavour == "iso":
            return ISODatetimeType()
        else:
            return None


DEFAULT_PEEKER = ListTypePeeker(PrimitiveTypePeeker(), DatetimePeeker())
