from typing import List

import cstore.schemes as schemes
from cstore.models import Tag
from cstore.database import LocalSession


class RepoTag:
    def __init__(self) -> None:
        self.db = LocalSession()

    def create(self, tag_data: schemes.TagSchemaBase) -> Tag:
        db_tag = Tag(**tag_data.dict())
        self.db.add(db_tag)
        self.db.commit()
        self.db.refresh(db_tag)
        self.db.close()
        return db_tag

    def get_by_id(self, tag_id: int) -> Tag:
        result = self.db.query(Tag).filter(Tag.id == tag_id).first()
        self.db.close()
        return result

    def get_by_name(self, tag_name: str) -> Tag:
        result = self.db.query(Tag).filter(Tag.name == tag_name).first()
        self.db.close()
        return result

    def get_or_create(self, tag_data: schemes.TagSchemaBase) -> any:
        is_new_tag = False
        tag = self.get_by_name(tag_data.name)
        if not tag:
            tag = self.create(tag_data)
            is_new_tag = True
        return tag, is_new_tag

    def remove(self, tag_id: int):
        self.db.query(Tag).filter(
            Tag.id == tag_id).delete()
        self.db.commit()
        self.db.close()

    def get_all(self) -> List[Tag]:
        result = self.db.query(Tag).all()
        self.db.close()
        return result