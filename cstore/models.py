from typing import List
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import DbBase


class Group(DbBase):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(String(1000), nullable=True)
    is_secret = Column(Boolean, default=False)
    commands = relationship("Command", back_populates="group", lazy='joined')


class Command(DbBase):
    __tablename__ = "commands"
    id = Column(Integer, primary_key=True, index=True)
    body = Column(String(500))
    description = Column(String(1000), nullable=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    group_order = Column(Integer)
    group = relationship("Group", back_populates="commands", lazy='joined')
    tags = relationship('Tag', secondary='commands_tags', backref='commands')
    is_secret = Column(Boolean, default=False)


class Tag(DbBase):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True)
    commands = relationship(
        "Command", bsecondary='commands_tags', lazy='joined')


class CommandTag(DbBase):
    __tablename__ = 'commands_tags'
    command_id = Column(Integer, ForeignKey('commands.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
