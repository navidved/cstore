from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database import DcBase



class Group(DcBase):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(String(1000), nullable=True)
    is_secret = Column(Boolean, default=False)
    commands = relationship("Command", back_populates="group", lazy="joined")


class Command(DcBase):
    __tablename__ = "commands"
    id = Column(Integer, primary_key=True, index=True)
    body = Column(String(1000))
    description = Column(String(1000), nullable=True)
    group_order = Column(Integer)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    group = relationship("Group", back_populates="commands", lazy="joined")
    tags = relationship("Tag", secondary="commands_tags", back_populates="commands")
    is_secret = Column(Boolean, default=False)


class Tag(DcBase):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True)
    commands = relationship("Command", secondary="commands_tags", back_populates="tags")


class CommandTag(DcBase):
    __tablename__ = 'commands_tags'
    command_id = Column(Integer, ForeignKey('commands.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)