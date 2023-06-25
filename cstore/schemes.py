from typing import Optional, List
from pydantic import validator, root_validator
from pydantic import BaseModel, Field


def to_lowercase(v):
    return str(v).lower()


def remove_stars_and_trim(v):
    return str(v).replace('*', '').strip()


def should_not_contain_any_space(cls, v, field_name: str):
    if ' ' in v:
        raise ValueError(f"There should not be any space in the {field_name}")
    return v


class TagSchemaBase(BaseModel):
    name: str = Field(min_length=3, max_length=30)

    @validator('name')
    def tag_name_validation(cls, v):
        return should_not_contain_any_space(cls, v, 'tag name')

    @validator('name')
    def tag_name_preprocess(cls, v):
        return remove_stars_and_trim(to_lowercase(v))


class CommandSchemaBase(BaseModel):
    body: str = Field(min_length=2, max_length=500)
    description: Optional[str] = Field(max_length=1000, default=None)
    is_secret: Optional[bool]

    @validator('body')
    def command_body_preprocess(cls, v):
        return remove_stars_and_trim(to_lowercase(v))

    @root_validator
    def command_description_preprocess(cls, values):
        if not values["is_secret"] and values["description"] != None:
            values["description"] = remove_stars_and_trim(to_lowercase(values["description"]))
        return values


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
