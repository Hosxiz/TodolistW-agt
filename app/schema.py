#กำหนดระดับงาน
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Priority = Literal["low", "medium", "high"]


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str | None = None
    completed: bool = False
    priority: Priority = "medium"
    due_date: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    completed: bool | None = None
    priority: Priority | None = None
    due_date: str | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    completed: bool
    priority: Priority = "medium"
    due_date: str | None = None
    created_at: str
    updated_at: str


class TaskStats(BaseModel):
    total: int
    open: int
    completed: int
    high_priority: int
    overdue: int
