import schemes as schemes
from models import Group
from database import LocalSession

class RepoGroup:
    def __init__(self) -> None:
        self.db = LocalSession()
    
    def create(self ,group_data: schemes.GroupSchemaBase) -> Group:
        db_group = Group(**group_data.dict())
        self.db.add(db_group)
        self.db.commit()
        self.db.refresh(db_group)
        self.db.close()
        return db_group


    def get_by_name(self ,group_name: str) -> Group:
        result = self.db.query(Group).filter(Group.name == group_name).first()
        self.db.close()
        return result


    def get_by_id(self ,group_id: int) -> Group:
        result = self.db.query(Group).filter(Group.id == group_id).first()
        self.db.close()
        return result


    def get_or_create(self ,group_data: schemes.GroupSchemaBase) -> Group:
        group = self.get_by_name(group_data.name)
        if not group:
            group = self.create(group_data)
        return group
