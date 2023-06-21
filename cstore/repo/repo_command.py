import cstore.schemes as schemes
from cstore.models import Command
from cstore.database import LocalSession

class RepoCommand:
    def __init__(self) -> None:
        self.db = LocalSession()
    
    def create(self ,command_data: schemes.CommandSchemaBase) -> Command:
        db_command = Command(**command_data.dict())
        self.db.add(db_command)
        self.db.commit()
        self.db.refresh(db_command)
        self.db.close()
        return db_command


    def get_by_id(self ,command_id: int) -> Command:
        result = self.db.query(Command).filter(Command.id == command_id).first()
        self.db.close()
        return result
