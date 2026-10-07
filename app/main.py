from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import FileResponse

from .database import initialize_db
from .schema import TaskCreate, TaskRead, TaskStats, TaskUpdate
from .service import create_task, delete_task, get_stats, get_task_by_id, list_tasks, update_task


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_db()
    yield


app = FastAPI(title="Task Dashboard", lifespan=lifespan)


@app.get("/", response_class=FileResponse)
def index_page() -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/stats", response_model=TaskStats)
def stats_endpoint() -> TaskStats:
    return get_stats()


@app.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task_endpoint(payload: TaskCreate) -> TaskRead:
    record = create_task(payload)
    return TaskRead(**record.__dict__)


@app.get("/tasks", response_model=list[TaskRead])
def list_tasks_endpoint(
    status: str = Query("all"),
    priority: str = Query("all"),
    q: str = Query("", max_length=200),
) -> list[TaskRead]:
    normalized_status = status if status in {"all", "open", "done"} else "all"
    normalized_priority = priority if priority in {"all", "low", "medium", "high"} else "all"
    records = list_tasks(
        status=None if normalized_status == "all" else normalized_status,
        priority=None if normalized_priority == "all" else normalized_priority,
        search=q,
    )
    return [TaskRead(**record.__dict__) for record in records]


@app.get("/tasks/{task_id}", response_model=TaskRead)
def get_task_endpoint(task_id: int) -> TaskRead:
    record = get_task_by_id(task_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบงาน")
    return TaskRead(**record.__dict__)


@app.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task_endpoint(task_id: int, payload: TaskUpdate) -> TaskRead:
    record = update_task(task_id, payload)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบงาน")
    return TaskRead(**record.__dict__)


@app.delete("/tasks/{task_id}")
def delete_task_endpoint(task_id: int) -> dict[str, str]:
    if not delete_task(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบงาน")
    return {"message": "ลบงานสำเร็จ"}
