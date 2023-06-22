from os.path import exists
from typing import Optional, List
from typing_extensions import Annotated
from rich.console import Console
from typer import Typer, Option, Exit, Context
from rich.prompt import Prompt
from rich import print

from models import DcBase, Group, Command, Tag
import schemes as schemes
from database import engine
from constants import actions_enum, ActionsEnum
from repo.repo_group import RepoGroup
from repo.repo_command import RepoCommand



__version__ = "0.3.7"
db_path = "cstore_sqlite.db"
state = {"verbose": False}
defult_action = actions_enum.filter
app = Typer()
console = Console()


def startup() -> None:
    if not exists(db_path):
        DcBase.metadata.create_all(bind=engine)


class BaseAction:
    def __init__(self, entities: schemes.EntitiesSchema) -> None:
        self.entities = entities

    def execute(self):
        pass


class ConcreteFilterAction(BaseAction):
    def execute(self):
        print("_search_")


class ConcreteAddAction(BaseAction):
    def execute(self):
        group: Group = None
        command: Command = None
        tags: list[Tag] = []
        
        if self.entities.group != None:
            group = RepoGroup().get_or_create(self.entities.group)
            
        if self.entities.tags != []:
            for tag in self.entities.tags:
                tags.append()
            
        if self.entities.command != None:
            command_schema = schemes.CommandCreateWithGroupAndTagsSchema(**self.entities.command)
            if group:
                command_schema.group_id = group.id
            command = RepoCommand().create(command_schema)

            
        print(command)


class ConcreteDeleteAction(BaseAction):
    def execute(self):
        print("_remove_")


class ConcreteModifyAction(BaseAction):
    def execute(self):
        print("_edit_")


class ActionFactory:
    def __init__(self, entities: schemes.EntitiesSchema) -> None:
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
                raise Exit()


def version_callback(value: bool):
    if value:
        print(f"Command Store (cstore) Version: {__version__}")
        raise Exit()


# TODO: we need export command to export a group of commands or all commands
@app.command("export")
def export_db_to_json():
    print("Export")


# TODO: we need import command to import a group of commands or all commands
@app.command("import")
def import_from_json_to_db():
    print("Import")


# TODO: we need flush command to clean and fresh db
@app.command("flush")
def flush_db():
    print("Flush")


@app.callback(invoke_without_command=True)
def main(
    ctx: Context,
    verbose: bool = False,
    version: Annotated[
        Optional[bool], Option(
            "-v", "--version", callback=version_callback)
    ] = None,
    add: Annotated[
        Optional[bool], Option(
            "-a", "--add", help="Add command, group & tag or a combination of these")
    ] = False,
    delete: Annotated[
        Optional[bool], Option(
            "-d", "--delete", help="delete command, group & tag")
    ] = False,
    modify: Annotated[
        Optional[bool], Option(
            "-m", "--modify", help="modify command, group & tag")
    ] = False,
    filter: Annotated[
        Optional[bool], Option(
            "-f", "--filter", help="filter command, group & tag")
    ] = False,
    secret: Annotated[
        Optional[bool], Option(
            "--secret", help="flag to make secret a command or a group")
    ] = False,
    description: Annotated[
        Optional[str], Option(
            "--desc", help="description could be used for commands and groups")
    ] = None,
    command: Annotated[
        Optional[str], Option(
            "-c", "--command", help="Command entity")
    ] = None,
    group: Annotated[
        Optional[str], Option(
            "-g", "--group", help="Group entity")
    ] = None,
    tags: Annotated[
        Optional[List[str]], Option(
            "-t", "--tag", help="Tag entity")
    ] = [],
):
    """
    Main Method Help
    """
    startup()
    
    if verbose:
        print("verbose activated!")
        state["verbose"] = True

    if ctx.invoked_subcommand is None:
        activated_action = get_activated_action(
            add=add,
            delete=delete,
            modify=modify,
            filter=filter)

        entities = validate_entities(
            command=command,
            description=description,
            group=group,
            tags=tags,
            is_secret=secret)

        if not entities:
            input_prompt = Prompt.ask("enter someting to search :boom:")
            entities = schemes.EntitiesSchema(
                command= schemes.CommandSchemaBase(
                    description=description,
                    is_secret=secret,
                    body=input_prompt
                ))
            
        ActionFactory(entities=entities).create_action(activated_action).execute()


def get_activated_action(**actions) -> str:
    true_actions_count = sum(actions.values())
    if true_actions_count == 0:
        return defult_action
    elif true_actions_count == 1:
        return actions_enum(next(action_name for action_name, action_value in actions.items() if action_value))
    else:
        print(f"Only one of add, delete and modify actions can be used in each command")
        raise Exit()


def validate_entities(command: str, description: str, group: str, tags: list[str], is_secret: bool) -> schemes.EntitiesSchema:
    comman_entity = schemes.CommandSchemaBase(
        body=command,
        description=description,
        is_secret=is_secret
    ) if command else None
    
    if command:
        description = None
        
    group_entity = schemes.GroupSchemaBase(
        name=group,
        description=description,
        is_secret=is_secret
    ) if group else None

    tag_list_entity: list[str] = []
    for tag in tags:
        tag_list_entity.append(schemes.TagSchemaBase(name=tag))

    if comman_entity or group_entity or tag_list_entity:
        return schemes.EntitiesSchema(
            command=comman_entity,
            group=group_entity,
            tags=tag_list_entity
        )
    else:
        return None


if __name__ == "__main__":
    app()
