import dataclasses
from enum import Enum, auto


class LoadStatus(Enum):
    SUCCESS = auto()
    REJECTED = auto()
    NEW = auto()
    DELETED = auto()


@dataclasses.dataclass
class LoadResult:
    status : LoadStatus
    errors: list = dataclasses.field(default_factory=list)
    exceptions: list = dataclasses.field(default_factory=list)

    def to_string(self):
        result = "\n".join(map(lambda x : "ERROR: {}".format(x), self.errors))
        result += "\n".join(map(lambda x : "EXCEPTION: {}".format(x), self.exceptions))
        result += "\n" + str(self.status)
        return result