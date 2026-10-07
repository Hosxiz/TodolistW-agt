import pytest
from uuid import uuid4

from fastapi.testclient import TestClient

from app import database
from app.main import app



@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "tasks.db")
    with TestClient(app) as test_client:
        yield test_client


def test_root_page_loads_ui(client):
    response = client.get("/")
    assert response.status_code == 200
    text = response.text
    assert "งานของฉัน" in text or "แผงงาน" in text or "Task" in text


def test_create_and_list_task(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Write README",
            "description": "Create user guide",
            "completed": False,
            "priority": "high",
            "due_date": "2026-10-15",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Write README"
    assert body["description"] == "Create user guide"
    assert body["priority"] == "high"
    assert body["due_date"] == "2026-10-15"

    list_response = client.get("/tasks")
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1

    filtered = client.get("/tasks?priority=high")
    assert filtered.status_code == 200
    assert any(item["priority"] == "high" for item in filtered.json())


def test_task_text_is_not_treated_as_html(client):
    payload = "<img src=x onerror=alert('xss')>"
    created = client.post(
        "/tasks",
        json={"title": payload, "description": payload},
    )

    assert created.status_code == 201
    assert created.json()["title"] == payload
    assert created.json()["description"] == payload

    listed = client.get("/tasks")
    assert listed.status_code == 200
    assert any(task["title"] == payload for task in listed.json())


def test_search_matches_title_and_description(client):
    marker = f"search-{uuid4().hex}"
    title_match = client.post("/tasks", json={"title": f"{marker} title match"}).json()
    description_match = client.post(
        "/tasks",
        json={"title": "Unrelated title", "description": f"Contains {marker}"},
    ).json()
    unrelated = client.post("/tasks", json={"title": f"Unrelated {uuid4().hex}"}).json()

    response = client.get("/tasks", params={"q": marker})

    assert response.status_code == 200
    result_ids = {task["id"] for task in response.json()}
    assert result_ids == {title_match["id"], description_match["id"]}
    assert unrelated["id"] not in result_ids


def test_stats_are_based_on_all_tasks(client):
    client.post("/tasks", json={"title": "Open high priority", "priority": "high", "due_date": "2000-01-01"})
    client.post("/tasks", json={"title": "Open task", "priority": "low"})
    client.post("/tasks", json={"title": "Completed task", "completed": True, "priority": "medium"})

    response = client.get("/stats")

    assert response.status_code == 200
    assert response.json() == {
        "total": 3,
        "open": 2,
        "completed": 1,
        "high_priority": 1,
        "overdue": 1,
    }


def test_update_task(client):
    created = client.post(
        "/tasks",
        json={"title": "Review code", "description": "Check logic", "completed": False, "priority": "medium"},
    )
    task_id = created.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"completed": True, "title": "Review code final", "priority": "low", "due_date": "2026-10-20"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["completed"] is True
    assert body["title"] == "Review code final"
    assert body["priority"] == "low"
    assert body["due_date"] == "2026-10-20"


def test_delete_task(client):
    created = client.post(
        "/tasks",
        json={"title": "Delete this", "description": "Should be removed", "completed": False, "priority": "low"},
    )
    task_id = created.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "ลบงานสำเร็จ"

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404
