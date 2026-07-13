"""Seed project_aliases and participant_names from Evolution API."""
import os, json, urllib.request
from pathlib import Path
import psycopg2

# Load .env
env_path = Path("/home/weirong/Documents/endflo/miniapp/.env")
for line in env_path.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, _, val = line.partition("=")
        os.environ[key.strip()] = val.strip()

client_id = "132182030958640@lid"

# Fetch groups
url = "http://100.106.84.62:8081/group/fetchAllGroups/endflo?getParticipants=true"
req = urllib.request.Request(url, headers={"apikey": "livelife"})
groups = json.loads(urllib.request.urlopen(req).read())
print(f"Fetched {len(groups)} groups")

conn = psycopg2.connect(
    host="100.106.84.62",
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    dbname="endflo-gritline",
)
cur = conn.cursor()

# Upsert project aliases
for g in groups:
    jid = g["id"] if isinstance(g["id"], str) else g["id"]["_serialized"]
    name = g.get("subject") or g.get("name") or jid
    cur.execute(
        """INSERT INTO project_aliases (client_id, chat_jid, project_name)
           VALUES (%s, %s, %s)
           ON CONFLICT (client_id, chat_jid)
           DO UPDATE SET project_name = EXCLUDED.project_name""",
        (client_id, jid, name),
    )
    print(f"  Project: {jid[:20]}... → {name}")

conn.commit()

# Seed participants with phone numbers as default names
seen = set()
inserted = 0
for g in groups:
    for p in g.get("participants", []):
        pid = p["id"] if isinstance(p["id"], str) else p["id"]["_serialized"]
        if pid in seen:
            continue
        seen.add(pid)
        
        push = p.get("pushname")
        name = p.get("name")
        pn = p.get("phoneNumber", "")
        
        # Build display name: phone number as default alias
        display = push or name or ""
        if (not display or display == "?") and pn:
            display = pn.replace("@s.whatsapp.net", "")
        if not display or display == "?":
            display = "Unknown"
        
        cur.execute(
            """INSERT INTO participant_names (client_id, whatsapp_id, display_name)
               VALUES (%s, %s, %s)
               ON CONFLICT (client_id, whatsapp_id)
               DO UPDATE SET display_name = EXCLUDED.display_name""",
            (client_id, pid, display),
        )
        if cur.rowcount > 0:
            inserted += 1
        print(f"  Participant: {pid:30s} → {display}")

conn.commit()

# Verify
cur.execute("SELECT COUNT(*) FROM project_aliases WHERE client_id = %s", (client_id,))
print(f"\nProject aliases: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM participant_names WHERE client_id = %s", (client_id,))
print(f"Participants: {cur.fetchone()[0]}")

cur.close()
conn.close()
print("Done.")
