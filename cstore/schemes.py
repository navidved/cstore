from typing import Optional, List

from pydantic import validator
from pydantic import BaseModel, Field


def to_lowercase(v):
    return str(v).lower()


def should_not_contain_any_space(cls, v, field_name: str):
    if ' ' in v:
        raise ValueError(f"There should not be any space in the {field_name}")
    return v


class TagSchemaBase(BaseModel):
    name: str = Field(min_length=3, max_length=30)

    @validator('name')
    def description_should_not_contain_any_space(cls, v):
        return should_not_contain_any_space(cls, v, 'tag name')

    @validator('name')
    def change_to_lowercase(cls, v):
        return to_lowercase(v)


class CommandSchemaBase(BaseModel):
    body: str = Field(min_length=2, max_length=500)
    description: Optional[str] = Field(max_length=1000, default=None)
    is_secret: Optional[bool]

    @validator('description')
    def change_to_lowercase(cls, v):
        return to_lowercase(v)


class TagDBSchema(TagSchemaBase):
    id: int

    class Config:
        orm_mode = True


class CommandCreateWithTagsSchema(CommandSchemaBase):
    tags: Optional[list[TagSchemaBase]] = []


class CommandDBSchema(CommandSchemaBase):
    id: int
    tags: Optional[list[TagDBSchema]] = []

    class Config:
        orm_mode = True


class EntitiesSchema(BaseModel):
    command: Optional[CommandSchemaBase]
    tags: Optional[List[TagSchemaBase]]
