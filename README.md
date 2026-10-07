# Task Management App

A lightweight FastAPI task-management MVP with a browser UI and SQLite persistence.

## Features
- Add, view, complete, update, and delete tasks
- Set priority and due date
- Filter by status and priority
- Search tasks by title or description
- Toggle dark mode
- Use the API from another application

## Run locally

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/
```

## API

```powershell
curl.exe -X POST http://127.0.0.1:8000/tasks `
  -H "Content-Type: application/json" `
  -d '{"title":"Write README","priority":"high"}'

curl.exe http://127.0.0.1:8000/tasks

curl.exe "http://127.0.0.1:8000/tasks?q=README"
```

## Test

```powershell
python -m pytest -q
```
