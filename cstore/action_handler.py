from cstore.schemes import EntitiesSchema
from cstore.repo.repo_group import RepoGroup
from cstore.repo.repo_command import RepoCommand
from cstore.models import Group, Command
from cstore.constants import ActionsEnum, actions_enum


class BaseAction:
    def __init__(self, entities: EntitiesSchema) -> None:
        self.entities = entities

    def execute(self):
        pass


class ConcreteFilterAction(BaseAction):
    def execute(self):
        return "filter ", self.entities.command, self.entities.group, self.entities.tag


class ConcreteAddAction(BaseAction):
    def execute(self):
        if self.entities.command != None:
            command: Command = RepoCommand().create(self.entities.command)
            print(command.id)


class ConcreteDeleteAction(BaseAction):
    def execute(self):
        return "delete ", self.entities.command, self.entities.group, self.entities.tag


class ConcreteModifyAction(BaseAction):
    def execute(self):
        return "modify ", self.entities.command, self.entities.group, self.entities.tag


class ActionFactory:
    def __init__(self, entities: EntitiesSchema) -> None:
        self.entities = entities
        pass

    def create_action(self, action_type: ActionsEnum):
        match action_type:
            case actions_enum.filter:
                return ConcreteFilterAction(entities=self.entities)
            case actions_enum.add:
                return ConcreteAddAction(entities=self.entities)
            case actions_enum.delete:
                return ConcreteDeleteAction(entities=self.entities)
            case actions_enum.modify:
                return ConcreteModifyAction(entities=self.entities)
            case _:
                print(f"Invalid Action")
