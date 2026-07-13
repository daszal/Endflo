"""
Endflo Mini App Backend — FastAPI application.

Serves the Telegram Mini App frontend (static/index.html) and provides
a JSON API for tasks, meetings, triage, and settings management.

All API endpoints require Telegram initData authentication via the
X-Telegram-InitData header. The Telegram user ID is mapped to an
Endflo schema name for data isolation.
"""
import json, os, re
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

# Load .env from the project root
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            if key.strip() not in os.environ:
                os.environ[key.strip()] = val.strip()

import auth, db

app = FastAPI(title="Endflo Mini App", version="0.1.0")

# ---------------------------------------------------------------------------
# Cache-control: force Telegram WebView to always revalidate HTML
# ---------------------------------------------------------------------------
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class NoCacheHTMLMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        ct = response.headers.get("content-type", "")
        if "text/html" in ct:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

app.add_middleware(NoCacheHTMLMiddleware)

# ---------------------------------------------------------------------------
# Client mapping: Telegram user ID → schema name (e.g. "gritline")
# ---------------------------------------------------------------------------
CLIENT_MAP: dict[int, str] = {}

def _load_client_map():
    raw = os.getenv("CLIENT_MAP", "{}")
    try:
        loaded = json.loads(raw)
        CLIENT_MAP.clear()
        # Keys come as strings from JSON; convert to int
        for k, v in loaded.items():
            CLIENT_MAP[int(k)] = v
    except json.JSONDecodeError:
        pass

_load_client_map()


def _endpoint_tag(path: str) -> str:
    """Map an API path to a tab group for visitor tracking."""
    if "/api/triage" in path:   return "triage"
    if "/api/meetings" in path:  return "meetings"
    if "/api/config" in path:    return "settings"
    if "/api/tasks" in path:     return "tasks"
    return ""  # frontend load or /api/visits — no tab flag


def _get_client_schema(request: Request) -> str:
    """Extract and validate initData from header, return the schema name."""
    init_data = request.headers.get("X-Telegram-InitData", "")
    user = auth.validate(init_data)
    tg_id = user["id"]
    schema = CLIENT_MAP.get(tg_id)
    if not schema:
        raise HTTPException(403, f"Telegram user {tg_id} not authorized")
    # Log the visit (upsert: one row per user per day) with tab tracking
    db.log_visit(schema, tg_id, user.get("first_name", ""), user.get("username", ""),
                 _endpoint_tag(request.url.path))
    return schema


# ---------------------------------------------------------------------------
# Exception handler for auth errors
# ---------------------------------------------------------------------------

@app.exception_handler(auth.AuthError)
def handle_auth_error(request: Request, exc: auth.AuthError):
    return JSONResponse(status_code=401, content={"error": str(exc)})


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

# --- Tasks ---

@app.get("/api/tasks")
def api_get_tasks(request: Request):
    schema = _get_client_schema(request)

    # Active tasks
    tasks = db.get_tasks(schema)
    tasks = db.resolve_project_names(schema, tasks, "chat_id")
    tasks = db.resolve_owner_names(schema, tasks, "owner")

    groups: dict[str, dict] = {}
    for t in tasks:
        pname = t["project_name"]
        if pname not in groups:
            groups[pname] = {"project_name": pname, "tasks": []}
        groups[pname]["tasks"].append({
            "task_id": t["task_id"],
            "title": t["title"],
            "owner": t["owner_name"],
            "status": t["status"],
            "deadline": t["deadline"].isoformat() if t.get("deadline") else None,
            "created_at": t["created_at"].isoformat() if t.get("created_at") else None,
        })

    # Recently completed tasks (for undo support)
    done_tasks = db.get_recently_done_tasks(schema)
    done_tasks = db.resolve_project_names(schema, done_tasks, "chat_id")
    done_tasks = db.resolve_owner_names(schema, done_tasks, "owner")

    done_groups: dict[str, dict] = {}
    for t in done_tasks:
        pname = t["project_name"]
        if pname not in done_groups:
            done_groups[pname] = {"project_name": pname, "tasks": []}
        done_groups[pname]["tasks"].append({
            "task_id": t["task_id"],
            "title": t["title"],
            "owner": t["owner_name"],
            "status": t["status"],
            "deadline": t["deadline"].isoformat() if t.get("deadline") else None,
            "created_at": t["created_at"].isoformat() if t.get("created_at") else None,
        })

    completed = db.get_tasks_completed_today()
    cleared_yesterday = db.get_tasks_cleared_yesterday()
    return {
        "projects": list(groups.values()),
        "completed_projects": list(done_groups.values()),
        "completed_today": completed,
        "cleared_yesterday": cleared_yesterday,
    }


@app.post("/api/tasks/{task_id}/done")
def api_mark_task_done(task_id: int, request: Request):
    schema = _get_client_schema(request)
    ok = db.mark_task_done(schema, task_id)
    if not ok:
        raise HTTPException(404, f"Task {task_id} not found")
    return {"ok": True}


@app.post("/api/tasks/{task_id}/undo")
def api_undo_task(task_id: int, request: Request):
    schema = _get_client_schema(request)
    ok = db.undo_task(schema, task_id)
    if not ok:
        raise HTTPException(404, f"Task {task_id} not found or not marked Done")
    return {"ok": True}


# --- Meetings ---

@app.get("/api/meetings")
def api_get_meetings(request: Request):
    schema = _get_client_schema(request)
    meetings = db.get_meetings(schema)
    meetings = db.resolve_project_names(schema, meetings, "chat_id")

    groups: dict[str, dict] = {}
    for m in meetings:
        pname = m["project_name"]
        if pname not in groups:
            groups[pname] = {"project_name": pname, "meetings": []}
        scheduled = m.get("scheduled_time")
        groups[pname]["meetings"].append({
            "meeting_id": m["meeting_id"],
            "title": m["title"],
            "scheduled_time": scheduled.isoformat() if scheduled else None,
            "location": m.get("location", ""),
            "project_address": m.get("project_address", ""),
        })

    return {"projects": list(groups.values())}


@app.post("/api/meetings/{meeting_id}/clear")
def api_clear_meeting(meeting_id: int, request: Request):
    schema = _get_client_schema(request)
    ok = db.clear_meeting(schema, meeting_id)
    if not ok:
        raise HTTPException(404, f"Meeting {meeting_id} not found or already cancelled")
    return {"ok": True}


# --- Triage ---

@app.get("/api/triage")
def api_get_triage(request: Request):
    schema = _get_client_schema(request)
    items = db.get_triage(schema)
    items = db.resolve_project_names(schema, items, "chat_id")

    groups: dict[str, dict] = {}
    for t in items:
        pname = t["project_name"]
        if pname not in groups:
            groups[pname] = {"project_name": pname, "items": []}
        groups[pname]["items"].append({
            "triage_id": t["triage_id"],
            "issue": t["issue_description"],
            "refs": t.get("source_message_ids", ""),
        })

    return {"projects": list(groups.values())}


@app.post("/api/triage/{triage_id}/resolve")
async def api_resolve_triage(request: Request, triage_id: int):
    schema = _get_client_schema(request)
    body = await request.json()
    clarification = body.get("clarification")  # None = no message provided
    success = db.resolve_triage(schema, triage_id, clarification)
    if not success:
        raise HTTPException(404, "Triage item not found")
    return {"status": "resolved", "triage_id": triage_id}


# --- Config: Projects ---

@app.get("/api/config/projects")
def api_get_projects(request: Request):
    schema = _get_client_schema(request)
    projects = db.get_project_aliases(schema)
    parts_by_project = db.get_participants_by_project(schema)
    for p in projects:
        p["participants"] = parts_by_project.get(p["id"], [])
    return {"projects": projects, "total_tasks": db.get_total_task_count(schema)}


@app.post("/api/config/projects")
async def api_upsert_project(request: Request):
    schema = _get_client_schema(request)
    body = await request.json()
    required = ["chat_jid", "project_name"]
    for field in required:
        if field not in body:
            raise HTTPException(400, f"Missing field: {field}")
    return db.upsert_project_alias(
        schema,
        body["chat_jid"],
        body["project_name"],
        body.get("project_address", ""),
        body.get("is_active", True),
    )


@app.delete("/api/config/projects/{alias_id}")
def api_delete_project(alias_id: int, request: Request):
    schema = _get_client_schema(request)
    ok = db.delete_project_alias(schema, alias_id)
    if not ok:
        raise HTTPException(404, f"Project alias {alias_id} not found")
    return {"ok": True}


# --- Config: Participants ---

@app.get("/api/config/participants")
def api_get_participants(request: Request):
    schema = _get_client_schema(request)
    return db.get_participant_names(schema)


@app.post("/api/config/participants")
async def api_upsert_participant(request: Request):
    schema = _get_client_schema(request)
    body = await request.json()
    required = ["chat_jid", "whatsapp_id", "display_name"]
    for field in required:
        if field not in body:
            raise HTTPException(400, f"Missing field: {field}")
    return db.upsert_participant(
        schema, body["chat_jid"], body["whatsapp_id"], body["display_name"],
        body.get("phone_number", ""), body.get("role", "Client")
    )


@app.delete("/api/config/participants/{participant_id}")
def api_delete_participant(participant_id: int, request: Request):
    schema = _get_client_schema(request)
    ok = db.delete_participant(schema, participant_id)
    if not ok:
        raise HTTPException(404, f"Participant {participant_id} not found")
    return {"ok": True}


# ---------------------------------------------------------------------------
# Visitor tracking
# ---------------------------------------------------------------------------

@app.get("/api/visits")
def api_get_visits(request: Request):
    schema = _get_client_schema(request)
    return db.get_visitor_logs(schema)


# ---------------------------------------------------------------------------
# Serve frontend
# ---------------------------------------------------------------------------

app.mount("/", StaticFiles(directory="static", html=True), name="static")
