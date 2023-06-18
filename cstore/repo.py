from sqlalchemy.orm import Session
from models import Group, Command, Tag
from schemes import GroupSchemaBase, CommandSchemaBase, TagSchemaBase
from database import LocalSession


def get_group_by_id(group_id: int):
    db = LocalSession()
    result = db.query(Group).filter(Group.id == group_id).first()
    db.close()
    return result


def create_group(group_data: GroupSchemaBase):
    db = LocalSession()
    db_group = Group(**group_data.dict())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    db.close()
    return db_group


def create_tag(tag_data: TagSchemaBase):
    db = LocalSession()
    db_tag = Tag(**tag_data.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    db.close()
    return db_tag


def create_command(command_data: CommandSchemaBase):
    db = LocalSession()
    db_command = Command(**command_data.dict())
    db.add(db_command)
    db.commit()
    db.refresh(db_command)
    db.close()
    return db_command
