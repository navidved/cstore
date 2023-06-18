from typing import Optional
from typing_extensions import Annotated
from rich.console import Console
from typer import Typer, run, Option, Exit

from schemes import CommandSchemaBase, EntitiesSchema, GroupSchemaBase, TagSchemaBase
from action_handler import ActionFactory


__version__ = "0.3.4"
app = Typer()
console = Console()


def version_callback(value: bool):
    if value:
        print(f"CStore Version: {__version__}")
        raise Exit()


def get_activated_action(**actions) -> str:
    true_actions_count = sum(actions.values())
    if true_actions_count == 0:
        return None
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

    return EntitiesSchema(
        command=comman_entity,
        group=group_entity,
        tag=tag_entity
    )


def main(
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
                "--desc", "--description", help="description could be used for commands and groups")
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
    activated_action = get_activated_action(
        add=add, delete=delete, modify=modify, filter=filter)
    entities = validate_entities(
        command=command, description=description, group=group, tag=tag, is_secret=secret)
    action = ActionFactory(entities=entities).create_action(activated_action)
    action.execute()


# TODO: we need export command to export a group of commands or all commands
# @app.command()
# def export_json():
#     print("Export")


# TODO: we need import command to import a group of commands or all commands
# @app.command()
# def import_json():
#     print("Import")


# TODO: we need flush command to flush or clear add data (double check before it)
# @app.command()
# def flush():
#     print("Flush")


def run_main():
    run(main)


if __name__ == "__main__":
    run_main()
