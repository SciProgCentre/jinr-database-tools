import dataclasses
from enum import Enum, auto

from sdp.utils import BColors


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

    def to_string(self, path):

        if self.status == LoadStatus.SUCCESS:
            status = BColors.OKGREEN + self.status.name + BColors.ENDC
        else:
            status = BColors.FAIL + self.status.name + BColors.ENDC
        result = "Loading {}: {}\n".format(path, status)
        result += "\n".join(map(lambda x : "{}: {}".format(BColors.ERROR, x), self.errors))
        result += "\n".join(map(lambda x : "{}: {}".format(BColors.EXCEPTION, x), self.exceptions))
        return result