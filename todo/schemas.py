import typing as t

from pydantic import BaseModel


class TodoBase(BaseModel):
    title: str
    description: t.Optional[str] = None


class TodoCreate(TodoBase):
    pass


class Todo(TodoBase):
    id: int

    class Config:
        orm_mode = True
