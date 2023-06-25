from enum import Enum


class ActionsEnum(Enum):
    add = "add"
    delete = "delete"
    # modify = "modify"
    filter = "filter"
    show = "show"


actions_enum = ActionsEnum
