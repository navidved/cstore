from typing import Optional
from typing_extensions import Annotated
from rich.console import Console
from typer import Typer, Option, Exit, Argument, Context
from rich.prompt import Prompt

from cstore.models import DcBase
from cstore.schemes import CommandSchemaBase, EntitiesSchema, GroupSchemaBase, TagSchemaBase
from cstore.action_handler import ActionFactory
from cstore.database import engine
from cstore.constants import actions_enum


__version__ = "0.3.6"
state = {"verbose": False}
defult_action = actions_enum.add.value
app = Typer()
console = Console()
DcBase.metadata.create_all(bind=engine)


def version_callback(value: bool):
    if value:
        print(f"CStore Version: {__version__}")
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
    tag: Annotated[
        Optional[str], Option(
            "-t", "--tag", help="Tag entity")
    ] = None,
):
    """
    Main Method Help
    """
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
            tag=tag,
            is_secret=secret)
        
        if entities:
            print(activated_action)
            print(entities)
        else:
            name = Prompt.ask("Enter someting to search :sunglasses:")

        # ActionFactory(entities=entities).create_action(activated_action).execute()


def get_activated_action(**actions) -> str:
    true_actions_count = sum(actions.values())
    if true_actions_count == 0:
        return defult_action
    elif true_actions_count == 1:
        return next(action_name for action_name, action_value in actions.items() if action_value)
    else:
        print(f"Only one of add, delete and modify actions can be used in each command")
        raise Exit()


def validate_entities(command: str, description: str, group: str, tag: str, is_secret: bool) -> EntitiesSchema:
    comman_entity = CommandSchemaBase(
        body=command,
        description=description,
        is_secret=is_secret
    ) if command else None

    group_entity = GroupSchemaBase(
        name=group,
        description=description,
        is_secret=is_secret
    ) if group else None

    tag_entity = TagSchemaBase(
        name=tag
    ) if tag else None

    if comman_entity or group_entity or tag_entity:
        return EntitiesSchema(
            command=comman_entity,
            group=group_entity,
            tag=tag_entity
        )
    else:
        return None


if __name__ == "__main__":
    app()
