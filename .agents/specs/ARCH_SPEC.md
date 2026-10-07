# System Architecture Specification: Simple Task Management

## 1. Overview & Objective

- **Problem Statement:** User needs a simple application to create, view, update, complete, and delete tasks.
- **Target Outcome:** A task management system that can be used immediately through a web interface and has a reliable backend API.
- **Primary User:** A user who manages daily tasks and wants to keep completed and pending work organized.

## 2. System Topology & Directory Structure

```text
TESTA/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── repositories/
│   │   └── task_repository.py
│   └── services/
│       └── task_service.py
├── tests/
│   ├── test_api.py
│   └── test_task_service.py
├── requirements.txt
├── pyproject.toml
├── README.md
└── .agents/specs/
    ├── ARCH_SPEC.md
    ├── RESEARCH_NOTE.md
    └── QA_REPORT.md
```

## 3. Data Models & Interface Contracts

### Task Data Model

```python
from datetime import datetime
from typing import Optional

class Task:
    id: int
    title: str
    description: Optional[str]
    is_completed: bool
    created_at: datetime
    updated_at: datetime
```

### API Contracts

```text
POST /tasks
Request: { title: string, description?: string }
Response: 201 { id, title, description, is_completed, created_at, updated_at }

GET /tasks
Response: 200 { items: [Task], total: number }

GET /tasks/{id}
Response: 200 Task

PUT /tasks/{id}
Request: { title?: string, description?: string, is_completed?: boolean }
Response: 200 Task

DELETE /tasks/{id}
Response: 204
```

### Validation Rules

- Task title is required and must contain between 1 and 200 characters.
- Task description must contain at most 2,000 characters when provided.
- Task ID must be a positive integer.
- A task cannot be marked complete before it has a valid title.
- API responses must not expose internal database details.

## 4. Error Handling & Resilience Strategy

- Invalid request data returns HTTP status `422` with validation details.
- A missing task returns HTTP status `404` with a stable error message.
- Internal database failures return HTTP status `500` without leaking stack traces.
- Database operations must use transactions.
- No retry mechanism is required for the initial version.
- The service must support graceful application startup and shutdown.

## 5. Non-Negotiable Constraints

- [ ] Use Python with FastAPI and SQLite.
- [ ] Keep API and persistence logic separated into service and repository layers.
- [ ] Use strict type annotations and Pydantic request/response models.
- [ ] Use SQL parameterization and prevent SQL injection.
- [ ] Add automated tests for create, list, retrieve, update, delete, validation, and not-found behavior.
- [ ] Do not add authentication, authorization, or multi-user feature in the first version.
- [ ] Do not add frontend framework in the first version; use FastAPI's built-in OpenAPI documentation for API testing.
- [ ] All production code must pass linting, type checking, and tests.
- [ ] No placeholder code, TODO comments, or dead code is allowed.

## 6. Acceptance Criteria

- A user can create a task through the API.
- A user can retrieve all tasks in a deterministic order.
- A user can retrieve a single task by ID.
- A user can update task fields and completion status.
- A user can delete a task by ID.
- Validation errors and missing tasks are handled consistently.
- The API can be started with a single documented command.
- Automated tests cover happy paths and boundary conditions.
