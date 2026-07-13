"""
Database layer for the Endflo Mini App backend.

Single database: endflo
  - public.messages      — unified WhatsApp + Telegram messages (client-agnostic)
  - {schema}.tasks        — client-specific tasks
  - {schema}.client_meetings
  - {schema}.pending_triage
  - {schema}.project_aliases
  - {schema}.participant_names

Each client has their own schema (e.g. gritline, acme_corp).
The schema name is provided by the caller (derived from CLIENT_MAP).

Connections are opened per-request. Low traffic, no pooling needed.
"""
import os
import psycopg2
import psycopg2.extras

HOST = os.getenv("PGHOST", "100.106.84.62")
PORT = int(os.getenv("PGPORT", "5432"))
USER = os.getenv("PGUSER")
PASS = os.getenv("PGPASSWORD")
DBNAME = os.getenv("PGDATABASE", "endflo")

if not USER or not PASS:
    raise RuntimeError("PGUSER and PGPASSWORD must be set in environment")


def _connect():
    """Open a new connection to the endflo database."""
    return psycopg2.connect(
        host=HOST, port=PORT, user=USER, password=PASS, dbname=DBNAME,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


# ---------------------------------------------------------------------------
# Task queries  (schema: supplied by caller)
# ---------------------------------------------------------------------------

def get_total_task_count(schema: str) -> int:
    """Return total number of tasks ever created (for time-saved calculation)."""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) as cnt FROM {schema}.tasks")
            row = cur.fetchone()
            return row["cnt"] if row else 0
    finally:
        conn.close()


def get_tasks(schema: str) -> list[dict]:
    """Return outstanding tasks, newest first. Only for active projects."""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""SELECT task_id, chat_id, title, owner,
                          status, deadline, created_at, updated_at
                   FROM {schema}.tasks
                   WHERE status != 'Done'
                     AND chat_id IN (SELECT chat_jid FROM {schema}.project_aliases WHERE is_active = true)
                   ORDER BY deadline ASC NULLS LAST, task_id DESC""",
            )
            return cur.fetchall()
    finally:
        conn.close()


def mark_task_done(schema: str, task_id: int) -> bool:
    """Mark a task as Done. Returns True if a row was updated."""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE {schema}.tasks SET status = 'Done', updated_at = NOW() WHERE task_id = %s",
                (task_id,),
            )
            conn.commit()
            return cur.rowcount > 0
    finally:
        conn.close()


def undo_task(schema: str, task_id: int) -> bool:
    """Revert a task from Done back to Needs Action. Returns True if updated."""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE {schema}.tasks SET status = 'Needs Action', updated_at = NOW() WHERE task_id = %s AND status = 'Done'",
                (task_id,),
            )
            conn.commit()
            return cur.rowcount > 0
    finally:
        conn.close()


def get_recently_done_tasks(schema: str, limit: int = 30) -> list[dict]:
    """Return tasks marked Done recently (by updated_at), newest first. Only for active projects."""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""SELECT task_id, chat_id, title, owner,
                          status, deadline, created_at, updated_at
                   FROM {schema}.tasks
                   WHERE status = 'Done'
                     AND chat_id IN (SELECT chat_jid FROM {schema}.project_aliases WHERE is_active = true)
                   ORDER BY updated_at DESC NULLS LAST
                   LIMIT %s""",
                (limit,),
            )
            return cur.fetchall()
    finally:
        conn.close()


def get_tasks_completed_today() -> int:
    """Count tasks marked Done today (SGT date)."""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT COUNT(*) as cnt FROM gritline.tasks
                   WHERE status = 'Done'
                   AND updated_at >= (now() AT TIME ZONE 'Asia/Singapore')::date::timestamptz""",
            )
            row = cur.fetchone()
            return row["cnt"] if row else 0
    finally:
        conn.close()


def get_tasks_cleared_yesterday() -> int:
    """Count tasks marked Done yesterday (SGT date)."""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT COUNT(*) as cnt FROM gritline.tasks
                   WHERE status = 'Done'
                   AND updated_at >= ((now() AT TIME ZONE 'Asia/Singapore')::date - INTERVAL '1 day')::timestamptz
                   AND updated_at < (now() AT TIME ZONE 'Asia/Singapore')::date::timestamptz""",
            )
            row = cur.fetchone()
            return row["cnt"] if row else 0
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Meeting queries  (schema: supplied by caller)
# ---------------------------------------------------------------------------

def get_meetings(schema: str) -> list[dict]:
    """Return upcoming meetings, soonest first. Only for active projects."""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""SELECT meeting_id, chat_id, title,
                          scheduled_time, location, status
                   FROM {schema}.client_meetings
                   WHERE status = 'scheduled'
                     AND chat_id IN (SELECT chat_jid FROM {schema}.project_aliases WHERE is_active = true)
                   ORDER BY scheduled_time ASC""",
            )
            return cur.fetchall()
    finally:
        conn.close()


def clear_meeting(schema: str, meeting_id: int) -> bool:
    """Mark a meeting as cancelled. Returns True if updated."""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE {schema}.client_meetings SET status = 'cancelled', updated_at = NOW() WHERE meeting_id = %s AND status = 'scheduled'",
                (meeting_id,),
            )
            conn.commit()
            return cur.rowcount > 0
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Triage queries  (schema: supplied by caller)
# ---------------------------------------------------------------------------

def get_triage(schema: str) -> list[dict]:
    """Return pending triage items, newest first. Only for active projects."""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""SELECT triage_id, chat_id, issue_description,
                          source_message_ids
                   FROM {schema}.pending_triage
                   WHERE (status IS NULL OR status != 'resolved')
                     AND chat_id IN (SELECT chat_jid FROM {schema}.project_aliases WHERE is_active = true)
                   ORDER BY triage_id DESC""",
            )
            return cur.fetchall()
    finally:
        conn.close()


def get_triage_messages(schema: str, triage_id: int) -> list[dict] | None:
    """Return the source messages a triage item was extracted from, oldest first.

    Scoped to the client: the triage row must exist in the client's schema,
    and messages are matched on that row's chat_id. Returns None if the
    triage item doesn't exist.
    """
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT chat_id, source_message_ids FROM {schema}.pending_triage WHERE triage_id = %s",
                (triage_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            ids = row["source_message_ids"] or []
            if not ids:
                return []
            cur.execute(
                """SELECT id, sender_name, content, content_type, sent_at
                   FROM public.messages
                   WHERE id::text = ANY(%s) AND chat_id = %s
                   ORDER BY sent_at ASC, id ASC""",
                (ids, row["chat_id"]),
            )
            return cur.fetchall()
    finally:
        conn.close()


def resolve_triage(schema: str, triage_id: int, clarification: str | None) -> bool:
    """Mark a triage item as resolved with optional user clarification."""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""UPDATE {schema}.pending_triage
                   SET status = 'resolved',
                       clarification = %s,
                       resolved_at = NOW(),
                       updated_at = NOW()
                   WHERE triage_id = %s
                   RETURNING triage_id""",
                (clarification, triage_id),
            )
            ok = cur.fetchone() is not None
            conn.commit()
            return ok
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Config queries  (schema: supplied by caller)
# ---------------------------------------------------------------------------

def get_project_aliases(schema: str) -> list[dict]:
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""SELECT id, chat_jid, project_name, project_address, is_active
                   FROM {schema}.project_aliases
                   ORDER BY project_name""",
            )
            return cur.fetchall()
    finally:
        conn.close()


def upsert_project_alias(
    schema: str, chat_jid: str, project_name: str, project_address: str = "",
    is_active: bool = True,
) -> dict:
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {schema}.project_aliases (chat_jid, project_name, project_address, is_active)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (chat_jid)
                   DO UPDATE SET project_name = EXCLUDED.project_name,
                                 project_address = EXCLUDED.project_address,
                                 is_active = EXCLUDED.is_active,
                                 updated_at = NOW()
                   RETURNING id, chat_jid, project_name, project_address, is_active""",
                (chat_jid, project_name, project_address, is_active),
            )
            conn.commit()
            return cur.fetchone()
    finally:
        conn.close()


def delete_project_alias(schema: str, alias_id: int) -> bool:
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {schema}.project_aliases WHERE id = %s", (alias_id,))
            conn.commit()
            return cur.rowcount > 0
    finally:
        conn.close()


def get_participant_names(schema: str) -> list[dict]:
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""SELECT id, whatsapp_id, display_name, role
                   FROM {schema}.participant_names
                   ORDER BY display_name""",
            )
            return cur.fetchall()
    finally:
        conn.close()


def get_participants_by_project(schema: str) -> dict[int, list[dict]]:
    """Return a mapping of project_alias.id -> list of participant dicts
    using a SQL join between participant_names and project_aliases."""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""SELECT pn.id, pn.whatsapp_id, pn.display_name, pn.phone_number, pn.chat_jid,
                          pn.role,
                          pa.id as alias_id, pa.project_name
                   FROM {schema}.participant_names pn
                   JOIN {schema}.project_aliases pa
                     ON pa.chat_jid = pn.chat_jid
                   WHERE pn.whatsapp_id NOT IN ('58296295780416@lid', '132182030958640@lid')
                   ORDER BY pa.project_name, pn.display_name""",
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    result: dict[int, list[dict]] = {}
    for r in rows:
        alias_id = r["alias_id"]
        if alias_id not in result:
            result[alias_id] = []
        result[alias_id].append({
            "whatsapp_id": r["whatsapp_id"],
            "display_name": r["display_name"],
            "phone_number": r.get("phone_number", ""),
            "role": r.get("role") or "Client",
        })
    return result


def upsert_participant(schema: str, chat_jid: str, whatsapp_id: str, display_name: str, phone_number: str = "", role: str = "Client") -> dict:
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {schema}.participant_names (chat_jid, whatsapp_id, display_name, phone_number, role)
                   VALUES (%s, %s, %s, %s, %s)
                   ON CONFLICT (chat_jid, whatsapp_id)
                   DO UPDATE SET display_name = EXCLUDED.display_name,
                                 phone_number = EXCLUDED.phone_number,
                                 role = EXCLUDED.role,
                                 updated_at = NOW()
                   RETURNING id, chat_jid, whatsapp_id, display_name, phone_number, role""",
                (chat_jid, whatsapp_id, display_name, phone_number, role),
            )
            conn.commit()
            return cur.fetchone()
    finally:
        conn.close()


def delete_participant(schema: str, participant_id: int) -> bool:
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {schema}.participant_names WHERE id = %s", (participant_id,))
            conn.commit()
            return cur.rowcount > 0
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Name resolution helpers
# ---------------------------------------------------------------------------

def resolve_project_names(schema: str, items: list[dict], jid_field: str) -> list[dict]:
    """Replace chat JIDs with project names using project_aliases table.
    Falls back to the raw JID if no alias found."""
    aliases = get_project_aliases(schema)
    jid_to_name = {a["chat_jid"]: a["project_name"] for a in aliases}
    jid_to_addr = {a["chat_jid"]: a.get("project_address", "") for a in aliases}

    for item in items:
        jid = item.get(jid_field, "")
        item["project_name"] = jid_to_name.get(jid, jid or "Unassigned")
        item["project_address"] = jid_to_addr.get(jid, "")
    return items


# ---------------------------------------------------------------------------
# Visitor tracking
# ---------------------------------------------------------------------------

def log_visit(schema: str, tg_user_id: int, first_name: str = "", username: str = "",
              endpoint: str = ""):
    """Log a visit. Upserts one row per user per day, bumping request_count.
    endpoint: 'tasks', 'meetings', 'triage', or 'settings' — increments the
    corresponding counter. Pass empty string to only bump request_count.
    """
    hit_tasks = 1 if endpoint == "tasks" else 0
    hit_meetings = 1 if endpoint == "meetings" else 0
    hit_triage = 1 if endpoint == "triage" else 0
    hit_settings = 1 if endpoint == "settings" else 0

    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {schema}.visitor_logs
                      (tg_user_id, first_name, username, visit_date,
                       hit_tasks, hit_meetings, hit_triage, hit_settings)
                   VALUES (%s, %s, %s,
                           (now() AT TIME ZONE 'Asia/Singapore')::date,
                           %s, %s, %s, %s)
                   ON CONFLICT (tg_user_id, visit_date)
                   DO UPDATE SET first_name = EXCLUDED.first_name,
                                 username = EXCLUDED.username,
                                 last_request_at = NOW(),
                                 request_count = {schema}.visitor_logs.request_count + 1,
                                 hit_tasks    = {schema}.visitor_logs.hit_tasks    + EXCLUDED.hit_tasks,
                                 hit_meetings = {schema}.visitor_logs.hit_meetings + EXCLUDED.hit_meetings,
                                 hit_triage   = {schema}.visitor_logs.hit_triage   + EXCLUDED.hit_triage,
                                 hit_settings = {schema}.visitor_logs.hit_settings + EXCLUDED.hit_settings,
                                 updated_at = NOW()""",
                (tg_user_id, first_name, username,
                 hit_tasks, hit_meetings, hit_triage, hit_settings),
            )
            conn.commit()
    finally:
        conn.close()


def get_visitor_logs(schema: str, days: int = 14) -> list[dict]:
    """Return visitor logs for the last N days, newest first."""
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""SELECT tg_user_id, first_name, username,
                          visit_date, first_visited_at, last_request_at,
                          request_count,
                          hit_tasks, hit_meetings, hit_triage, hit_settings
                   FROM {schema}.visitor_logs
                   WHERE visit_date >= (now() AT TIME ZONE 'Asia/Singapore')::date - %s::int * INTERVAL '1 day'
                   ORDER BY visit_date DESC, last_request_at DESC""",
                (days,),
            )
            rows = cur.fetchall()
            result = []
            for r in rows:
                result.append({
                    "tg_user_id": r["tg_user_id"],
                    "first_name": r["first_name"],
                    "username": r["username"],
                    "visit_date": r["visit_date"].isoformat(),
                    "first_visited_at": r["first_visited_at"].isoformat(),
                    "last_request_at": r["last_request_at"].isoformat(),
                    "request_count": r["request_count"],
                    "tabs": {
                        "tasks": r["hit_tasks"],
                        "meetings": r["hit_meetings"],
                        "triage": r["hit_triage"],
                        "settings": r["hit_settings"],
                    },
                })
            return result
    finally:
        conn.close()


def resolve_owner_names(schema: str, items: list[dict], owner_field: str) -> list[dict]:
    """Replace raw WhatsApp IDs with display names. Strips @lid/@s.whatsapp.net
    suffixes before lookup. Falls back to the raw ID."""
    participants = get_participant_names(schema)
    id_to_name = {}
    for p in participants:
        raw = p["whatsapp_id"]
        id_to_name[raw] = p["display_name"]
        cleaned = raw.replace("@lid", "").replace("@s.whatsapp.net", "")
        if cleaned not in id_to_name:
            id_to_name[cleaned] = p["display_name"]

    for item in items:
        raw_owner = item.get(owner_field) or ""
        cleaned = raw_owner.replace("@lid", "").replace("@s.whatsapp.net", "")
        item["owner_name"] = id_to_name.get(raw_owner) or id_to_name.get(cleaned) or raw_owner
    return items
