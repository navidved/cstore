import os
import json
from typing import Optional, List
from typing_extensions import Annotated
from os.path import exists
import pyperclip
from rich.console import Console
from rich.prompt import Prompt
from rich import print
from typer import Typer, Option, Exit, Context, confirm, Abort, prompt
from simple_term_menu import TerminalMenu
import cryptocode


import schemes as schemes
from models import DcBase, Command, Tag
from database import engine
from constants import actions_enum, ActionsEnum
from repo.repo_command import RepoCommand
from repo.repo_tag import RepoTag
from verbose import Verbose


__version__ = "0.6.0"
db_path = "cstore_sqlite.db"
state = {"verbose": False}
defult_action = actions_enum.filter
app = Typer()
console = Console()
verbose_manager = Verbose()


def gen_fernet_key(passcode:bytes) -> bytes:
    assert isinstance(passcode, bytes)
    hlib = hashlib.md5()
    hlib.update(passcode)
    return base64.urlsafe_b64encode(hlib.hexdigest().encode('latin-1'))


def startup() -> None:
    if not exists(db_path):
        DcBase.metadata.create_all(bind=engine)


def print_search_result(search_result: List[Command]) -> int:
    menu_list = []
    for item in search_result:
        menu_item = item.body
        if item.description and not item.is_secret:
            menu_item += f" ({item.description})"
        menu_list.append(menu_item)
    terminal_menu = TerminalMenu(menu_list, title="search results")
    return terminal_menu.show()


class BaseAction:
    def __init__(self, entities: schemes.EntitiesSchema) -> None:
        self.entities = entities

    def execute(self):
        pass


class ConcreteFilterAction(BaseAction):
    def execute(self):
        selected_index = 0
        result = RepoCommand().search_and_filter(self.entities)
        
        if not result:
            print("Oops! nothing found.")
            raise Exit()
        
        if len(result) > 1:
            selected_index = print_search_result(result)
            
        if selected_index >= 0:
            selected_command = result[selected_index]
            
            if selected_command.is_secret:
                password = prompt(f"please enter a password to decrypt '{selected_command.body}'", hide_input=True)
                decrypted_command = cryptocode.decrypt(selected_command.description,password)
                if not decrypted_command:
                    print("invalid password!")
                    raise Exit()
                
                pyperclip.copy(decrypted_command)                        
            else:
                pyperclip.copy(selected_command.body)
            print(
                f"Command id {selected_command.id} copied to clipboard!")


class ConcreteAddAction(BaseAction):
    def execute(self):
        command: Command = None
        tags: list[Tag] = []

        if self.entities.command != None:
            if self.entities.command.is_secret:
                if self.entities.command.description:
                    print("It is not possible to enter description for the secret mode, write it into command")
                    raise Exit() 
                
                secret_command = prompt("please enter a your secrect command", hide_input=True)
                password = prompt("please enter a password to encryption (don't forget it!)", hide_input=True)
                encrypted_command = cryptocode.encrypt(secret_command, password)
                self.entities.command.description = encrypted_command
                
            if self.entities.tags != []:
                for tag in self.entities.tags:
                    tag_obj, is_new_tag = RepoTag().get_or_create(tag)
                    verbose_manager.action(verbose_kind="tag", state=state,
                                        tag_obj=tag_obj, is_new_tag=is_new_tag)
                    tags.append(tag_obj)
            
            command_schema = schemes.CommandCreateWithTagsSchema(
                **self.entities.command.__dict__)

            if tags:
                command_schema.tags = tags

            command, is_new_command = RepoCommand().get_or_create(command_schema)
            if is_new_command:
                print(f"New command added. (id={command.id})")
            else:
                current_tags = []
                for ctag in command.tags:
                    current_tags.append(ctag.name)

                for tag_item in tags:
                    if tag_item.name not in current_tags:
                        RepoCommand().add_tag(command.id, tag_item.id)


class ConcreteDeleteAction(BaseAction):
    def execute(self):
        if self.entities.command:
            result = RepoCommand().search_and_filter(self.entities)
            if not result:
                print("Oops! nothing found.")
                raise Exit()
            selected_index = print_search_result(result)
            if selected_index >= 0:
                command_id = result[selected_index].id
                if self.entities.tags:
                    delete_ok = confirm(
                        "Are you sure you want to delete commands tags?")
                    if not delete_ok:
                        raise Abort()
                    else:
                        for tag in self.entities.tags:
                            tag_db = RepoTag().get_by_name(tag.name)
                            if not tag_db:
                                print(f"Tag '{tag.name}' not found")
                            else:
                                RepoCommand().remove_tag(command_id=command_id, tag_id=tag_db.id)
                                print(f"Commands tag {tag_db.name} deleted!")
                else:
                    delete_ok = confirm(
                        f"Are you sure you want to delete {result[selected_index].body} command?")
                    if not delete_ok:
                        raise Abort()
                    else:
                        for command_tag_item in result[selected_index].tags:
                            RepoCommand().remove_tag(command_id, command_tag_item.id)
                        RepoCommand().remove(command_id)
                        print("Command deleted.")
        else:
            if self.entities.tags:
                delete_ok = confirm(
                    "Are you sure you want to delete all commands related to tags?")
                if not delete_ok:
                    raise Abort()
                else:
                    for tag in self.entities.tags:
                        tag_db = RepoTag().get_by_name(tag.name)
                        if not tag_db:
                            print(f"Tag '{tag.name}' not found")
                        else:
                            for command_item in tag_db.commands:
                                RepoCommand().remove_tag(command_item.id, tag_db.id)
                                RepoCommand().remove(command_item.id)
                            RepoTag().remove(tag_db.id)
                            print("All commands related to tags removed.")


class ConcreteShowAction(BaseAction):
    def execute(self):
        if self.entities.command:
            result = RepoCommand().search_and_filter(self.entities)
            if not result:
                print("Oops! nothing found.")
                raise Exit()
            if len(result) > 1:
                selected_index = print_search_result(result)
            else:
                selected_index = 0

            if selected_index >= 0:
                command = result[selected_index]
                if command.is_secret:
                    print("[bold red]it's a secret command, unable to show it![/bold red]")
                else:
                    print(f"[bold cyan]id[/bold cyan]: {command.id}")
                    print(f"[bold cyan]command body[/bold cyan]: {command.body}")
                    print(
                        f"[bold cyan]description[/bold cyan]: {command.description}")
                    tags_str = ""
                    for tag in command.tags:
                        if tags_str != "":
                            tags_str += ", "
                        tags_str += f"{tag.name}"
                    print(f"[bold cyan]tags[/bold cyan]: {tags_str}")


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
            # case actions_enum.modify:
            #     return ConcreteModifyAction(entities=self.entities)
            case actions_enum.show:
                return ConcreteShowAction(entities=self.entities)
            case _:
                print(f"Invalid action")
                raise Exit()


def version_callback(value: bool):
    if value:
        print(f"Command store (cstore) version: {__version__}")
        raise Exit()


@app.command("import")
def import_from_json_to_db(json_path: Annotated[
        str, Option("--path", help="json file path to import")]):

    if not exists(json_path):
        print(f"This path is invalid.")
        raise Exit()

    try:
        with open(json_path, "r") as json_file:
            dict_data = json.load(json_file)
            for dict_item in dict_data:
                import_data(dict_item)
            print("Import done!")

    except ValueError:
        print(f"This is not json file.")
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
                print(f"Command exist. (id:{command_db.id})")
            else:
                print(f"New command created. (id:{command_db.id})")

        except Exception as e:
            print(f"Commands not imported: {dict_item['body']} | error: {e}")
    else:
        print("Commands body is required.")


@app.command("flush")
def flush_db():
    if exists(db_path):
        os.remove(db_path)
        print("Database flushed.")


@app.command("tags")
def show_all_tags():
    all_tags = RepoTag().get_all()
    menu_list = []
    for tag_item in all_tags:
        menu_list.append(tag_item.name)
    terminal_menu = TerminalMenu(menu_list, title="tags list")
    selected_index = terminal_menu.show()
    if selected_index >= 0:
        selected_tag = all_tags[selected_index].name
        os.system(f"cstore --tag {selected_tag}")


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
    # modify: Annotated[
    #     Optional[bool], Option(
    #         "-m", "--modify", help="modify command & tag")
    # ] = False,
    show: Annotated[
        Optional[bool], Option(
            "-s", "--show", help="show command & related tags")
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
        print("Verbose activated!")
        state["verbose"] = True

    if ctx.invoked_subcommand is None:
        activated_action = get_activated_action(
            add=add,
            delete=delete,
            # modify=modify,
            show=show,
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
        print(f"Only one of add, delete and show actions can be used in each command")
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


# TODO: we need to modify commands and tags
# class ConcreteModifyAction(BaseAction):
#     def execute(self):
#         print("_edit_")


# # TODO: we need export all commands
# @app.command("export")
# def export_db_to_json():
#     print("Export")


if __name__ == "__main__":
    app()
