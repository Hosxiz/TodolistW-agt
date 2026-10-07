from __future__ import annotations

from datetime import datetime, timezone

from .database import get_connection
from .models import TaskRecord, TaskStats
from .schema import TaskCreate, TaskUpdate


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_record(row) -> TaskRecord:
    keys = set(row.keys()) if row else set()
    return TaskRecord(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"]),
        priority=row["priority"] if "priority" in keys else "medium",
        due_date=row["due_date"] if "due_date" in keys else None,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def list_tasks(
    status: str | None = None,
    priority: str | None = None,
    search: str | None = None,
) -> list[TaskRecord]:
    query = "SELECT * FROM tasks"
    clauses: list[str] = []
    params: list[str | int] = []

    if status in {"open", "done"}:
        clauses.append("completed = ?")
        params.append(0 if status == "open" else 1)

    if priority in {"low", "medium", "high"}:
        clauses.append("priority = ?")
        params.append(priority)

    if search and search.strip():
        search_pattern = "%" + search.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        clauses.append("(title LIKE ? ESCAPE '\\' OR description LIKE ? ESCAPE '\\')")
        params.extend((search_pattern, search_pattern))

    if clauses:
        query += " WHERE " + " AND ".join(clauses)

    query += " ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date ASC, id DESC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [_row_to_record(row) for row in rows]


def get_stats() -> TaskStats:
    query = """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN completed = 0 THEN 1 ELSE 0 END) AS open,
            SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) AS completed,
            SUM(CASE WHEN priority = 'high' THEN 1 ELSE 0 END) AS high_priority,
            SUM(
                CASE
                    WHEN completed = 0 AND due_date IS NOT NULL AND due_date < CURRENT_DATE THEN 1
                    ELSE 0
                END
            ) AS overdue
        FROM tasks
    """
    with get_connection() as conn:
        row = conn.execute(query).fetchone()
        return TaskStats(
            total=int(row["total"]),
            open=int(row["open"] or 0),
            completed=int(row["completed"] or 0),
            high_priority=int(row["high_priority"] or 0),
            overdue=int(row["overdue"] or 0),
        )


def get_task_by_id(task_id: int) -> TaskRecord | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return _row_to_record(row) if row else None


def create_task(payload: TaskCreate) -> TaskRecord:
    now = _now_iso()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tasks (title, description, completed, priority, due_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.title, payload.description, int(payload.completed), payload.priority, payload.due_date, now, now),
        )
        task_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return _row_to_record(row)


def update_task(task_id: int, payload: TaskUpdate) -> TaskRecord | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            return None

        existing = _row_to_record(row)
        updated_title = payload.title if payload.title is not None else existing.title
        updated_description = payload.description if payload.description is not None else existing.description
        updated_completed = payload.completed if payload.completed is not None else existing.completed
        updated_priority = payload.priority if payload.priority is not None else existing.priority
        updated_due_date = payload.due_date if payload.due_date is not None else existing.due_date

        conn.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, completed = ?, priority = ?, due_date = ?, updated_at = ?
            WHERE id = ?
            """,
            (updated_title, updated_description, int(updated_completed), updated_priority, updated_due_date, _now_iso(), task_id),
        )
        updated_row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return _row_to_record(updated_row)


def delete_task(task_id: int) -> bool:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            return False
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return True
