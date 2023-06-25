import json
from os.path import exists
from typing import Optional, List
from typing_extensions import Annotated
from rich.console import Console
from typer import Typer, Option, Exit, Context
from rich.prompt import Prompt
from rich import print
from simple_term_menu import TerminalMenu
import pyperclip


from models import DcBase, Command, Tag
import schemes as schemes
from database import engine
from constants import actions_enum, ActionsEnum
from repo.repo_command import RepoCommand
from repo.repo_tag import RepoTag


__version__ = "0.5.0"
db_path = "cstore_sqlite.db"
state = {"verbose": False}
defult_action = actions_enum.filter
app = Typer()
console = Console()


def startup() -> None:
    if not exists(db_path):
        DcBase.metadata.create_all(bind=engine)


def verbose_action(verbose_kind, **data):
    if state['verbose']:
        match verbose_kind:
            case "tag":
                if data["is_new_tag"]:
                    print(
                        f"tag '{data['tag_obj'].name}' created. (id={data['tag_obj'].id})")
                else:
                    print(
                        f"tag '{data['tag_obj'].name}' loaded. (id={data['tag_obj'].id})")


def print_search_result(search_result: List[Command]) -> None:
    menu_list = []
    for item in search_result:
        menu_item = f"[{item.id}] {item.body}"
        if item.description:
            menu_item += f" ({item.description})"
        menu_list.append(menu_item)
    terminal_menu = TerminalMenu(menu_list, title="search results")
    menu_entry_index = terminal_menu.show()
    pyperclip.copy(search_result[menu_entry_index].body)
    print(
        f"command id {search_result[menu_entry_index].id} copied to clipboard!")


class BaseAction:
    def __init__(self, entities: schemes.EntitiesSchema) -> None:
        self.entities = entities

    def execute(self):
        pass


class ConcreteFilterAction(BaseAction):
    def execute(self):
        result = RepoCommand().search_and_filter(self.entities)
        if not result:
            print("oops! nothing found.")
            raise Exit()
        print_search_result(result)


class ConcreteAddAction(BaseAction):
    def execute(self):
        command: Command = None
        tags: list[Tag] = []

        if self.entities.tags != []:
            for tag in self.entities.tags:
                tag_obj, is_new_tag = RepoTag().get_or_create(tag)
                verbose_action(verbose_kind="tag",
                               tag_obj=tag_obj, is_new_tag=is_new_tag)
                tags.append(tag_obj)

        if self.entities.command != None:
            command_schema = schemes.CommandCreateWithTagsSchema(
                **self.entities.command.__dict__)

            if tags:
                command_schema.tags = tags

            command = RepoCommand().create(command_schema)
            print(f"new command added. (id={command.id})")


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
                print(f"invalid action")
                raise Exit()


def version_callback(value: bool):
    if value:
        print(f"command store (cstore) version: {__version__}")
        raise Exit()


# TODO: we need export all commands
@app.command("export")
def export_db_to_json():
    print("Export")


@app.command("import")
def import_from_json_to_db(json_path: Annotated[
        str, Option("--path", help="json file path to import")]):

    if not exists(json_path):
        print(f"this path is invalid.")
        raise Exit()

    try:
        with open(json_path, "r") as json_file:
            dict_data = json.load(json_file)
            for dict_item in dict_data:
                import_data(dict_item)
            print("import done!")

    except ValueError:
        print(f"this is not json file.")
        raise Exit()


def import_data(dict_item: dict):
    if "body" in dict_item:
        command = None
        tags = []
        tags_db = []

        try:
            if "tags" in dict_item and isinstance(dict_item["tags"], list):
                for tag_item in dict_item["tags"]:
                    tags.append(schemes.TagSchemaBase(name=tag_item))

            if len(tags) >= 1:
                tags_db = []
                for tag in tags:
                    tag_db, is_new_tag = RepoTag().get_or_create(tag)
                    tags_db.append(tag_db)

            command = schemes.CommandCreateWithTagsSchema(
                body=dict_item["body"],
                description=dict_item["description"] if "description" in dict_item else None,
            )

            if tags_db:
                command.tags = tags_db

            command_db, is_new_command = RepoCommand().get_or_create(command)

            if not is_new_command:
                print(f"command exist. (id:{command_db.id})")
            else:
                print(f"new command created. (id:{command_db.id})")

        except Exception as e:
            print(f"commands not imported: {dict_item['body']} | error: {e}")
    else:
        print("commands body is required.")


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
            "-a", "--add", help="Add command, tag or a combination of these")
    ] = False,
    delete: Annotated[
        Optional[bool], Option(
            "-d", "--delete", help="delete command & tag")
    ] = False,
    modify: Annotated[
        Optional[bool], Option(
            "-m", "--modify", help="modify command & tag")
    ] = False,
    filter: Annotated[
        Optional[bool], Option(
            "-f", "--filter", help="filter command & tag")
    ] = False,
    secret: Annotated[
        Optional[bool], Option(
            "--secret", help="flag to make secret a command")
    ] = False,
    description: Annotated[
        Optional[str], Option(
            "--desc", help="description could be used for commands")
    ] = None,
    command: Annotated[
        Optional[str], Option(
            "-c", "--command", help="Command entity")
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
            tags=tags,
            is_secret=secret)

        if not entities:
            input_prompt = Prompt.ask("enter someting to search :boom:")
            entities = schemes.EntitiesSchema(
                command=schemes.CommandSchemaBase(
                    description=description,
                    is_secret=secret,
                    body=input_prompt
                ))

        ActionFactory(entities=entities).create_action(
            activated_action).execute()


def get_activated_action(**actions) -> str:
    true_actions_count = sum(actions.values())
    if true_actions_count == 0:
        return defult_action
    elif true_actions_count == 1:
        return actions_enum(next(action_name for action_name, action_value in actions.items() if action_value))
    else:
        print(f"only one of add, delete and modify actions can be used in each command")
        raise Exit()


def validate_entities(command: str, description: str, tags: list[str], is_secret: bool) -> schemes.EntitiesSchema:
    comman_entity = schemes.CommandSchemaBase(
        body=command,
        description=description,
        is_secret=is_secret
    ) if command else None

    if command:
        description = None

    tag_list_entity: list[str] = []
    for tag in tags:
        tag_list_entity.append(schemes.TagSchemaBase(name=tag))

    if comman_entity or tag_list_entity:
        return schemes.EntitiesSchema(
            command=comman_entity,
            tags=tag_list_entity
        )
    else:
        return None


if __name__ == "__main__":
    app()


# TODO Tasks :
# 1. import => 2h
# 2. flush_db => 1h
# 3. delete action => 2h
# 4. modify action => 2h
# 5. export => 2h
# 6. verbose move to new class and complated => 1h
# 7. prety print_search => 1h
# 8. ignore case sensetive => 1h
# 9. code comments and docstrings => 2h
# 10. github readme and help => 2h
# 11. pypi github and help => 1h
# 12. linkedin post => 1h
# 13. copy command to clipbord => 1
# 17. secret messages => 1
# ------------------------------
# sum : 20h => 4h per day => 6 days (9tir)
