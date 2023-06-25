from typing import List
from sqlalchemy import or_

import schemes as schemes
from models import Command, Tag
from database import LocalSession


class RepoCommand:
    def __init__(self) -> None:
        self.db = LocalSession()

    def create(self, command_data: schemes.CommandCreateWithTagsSchema) -> Command:
        db_command = Command(**command_data.dict())
        self.db.add(db_command)
        self.db.commit()
        self.db.refresh(db_command)
        self.db.close()
        return db_command

    def get_by_id(self, command_id: int) -> Command:
        result = self.db.query(Command).filter(
            Command.id == command_id).first()
        self.db.close()
        return result

    def get_by_body(self, command_body: str) -> Command:
        result = self.db.query(Command).filter(
            Command.body == command_body
        ).first()
        self.db.close()
        return result

    def get_or_create(self, command_data: schemes.CommandCreateWithTagsSchema) -> any:
        is_new_command = False
        command = self.get_by_body(command_data.body)
        if not command:
            command = self.create(command_data)
            is_new_command = True
        return command, is_new_command

    def search_and_filter(self,
                          entities: schemes.EntitiesSchema
                          ) -> List[Command] | None:
        result = None
        query_object = None

        if entities.command or entities.tags:
            query_object = self.db.query(Command)

        if entities.command:
            command_query = "%" + entities.command.body + "%"
            description_query = "%" + entities.command.body + "%"
            query_object = query_object.filter(or_(Command.body.ilike(command_query),
                                                   Command.description.ilike(description_query)))

        if entities.tags:
            tags_names = []
            for tag in entities.tags:
                tags_names.append(tag.name)

            if len(tags_names):
                query_object = query_object.filter(
                    Command.tags.any(Tag.name.in_(tags_names)))

        if query_object:
            result = query_object.all()

        return result
