from schemes import EntitiesSchema


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
        return "add ", self.entities.command, self.entities.group, self.entities.tag


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

    def create_action(self, action_type):
        match action_type:
            case "filter":
                return ConcreteFilterAction(entities=self.entities)
            case "add":
                return ConcreteAddAction(entities=self.entities)
            case "delete":
                return ConcreteDeleteAction(entities=self.entities)
            case "modify":
                return ConcreteModifyAction(entities=self.entities)
            case _:
                print(f"Invalid Action")
