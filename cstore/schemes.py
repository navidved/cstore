from typing import Optional
from pydantic import BaseModel, Field


class TagSchemaBase(BaseModel):
    name: str = Field(min_length=3, max_length=30)


class GroupSchemaBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: Optional[str] = Field(max_length=1000, default=None)
    is_secret: Optional[bool]


class GroupReadSchema(GroupSchemaBase):
    id: int

    class Config:
        orm_mode = True


class CommandSchemaBase(BaseModel):
    body: str = Field(min_length=2, max_length=500)
    description: Optional[str] = Field(max_length=1000, default=None)
    is_secret: Optional[bool]


class TagDBSchema(TagSchemaBase):
    id: int

    class Config:
        orm_mode = True


class CommandCreateWithGroupSchema(CommandSchemaBase):
    group_id: Optional[int]
    tags: Optional[list[TagSchemaBase]] = []


class CommandDBSchema(CommandSchemaBase):
    id: int
    group_id: Optional[int]
    group: Optional[GroupReadSchema]
    tags: Optional[list[TagDBSchema]] = []

    class Config:
        orm_mode = True


class GroupDBSchema(GroupSchemaBase):
    id: int
    commands: Optional[list[CommandSchemaBase]] = []

    class Config:
        orm_mode = True


class EntitiesSchema(BaseModel):
    command: Optional[CommandSchemaBase]
    group: Optional[GroupSchemaBase]
    tag: Optional[TagSchemaBase]
