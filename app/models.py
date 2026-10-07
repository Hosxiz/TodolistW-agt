from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TaskRecord:
    id: int
    title: str
    description: str | None
    completed: bool
    priority: str
    due_date: str | None
    created_at: str
    updated_at: str
