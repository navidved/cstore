from enum import Enum


class ActionsEnum(Enum):
    add = "add"
    delete = "delete"
    modify = "modify"
    filter = "filter"


actions_enum = ActionsEnum
