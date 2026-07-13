"""Fetch groups + participants from Evolution API and populate config tables."""
import os, json, urllib.request
from pathlib import Path
import psycopg2

# Load .env
env_path = Path(__file__).parent / ".env"
for line in env_path.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, _, val = line.partition("=")
        os.environ[key.strip()] = val.strip()

client_id = "132182030958640@lid"

# Step 1: Fetch groups from Evolution API
url = "http://100.106.84.62:8081/group/fetchAllGroups/endflo?getParticipants=true"
req = urllib.request.Request(url, headers={"apikey": "livelife"})
groups = json.loads(urllib.request.urlopen(req).read())
print(f"Fetched {len(groups)} groups from Evolution API\n")

# Step 2: Update project_aliases with real names
conn = psycopg2.connect(
    host=os.getenv("PGHOST", "100.106.84.62"),
    port=int(os.getenv("PGPORT", "5432")),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    dbname="endflo-gritline",
)
cur = conn.cursor()

updated_projects = 0
unique_participants = set()

for g in groups:
    if isinstance(g["id"], dict):
        jid = g["id"]["_serialized"]
    else:
        jid = g["id"]
    name = g.get("subject", g.get("name", jid))
    
    # Upsert project alias with real name
    cur.execute(
        """INSERT INTO project_aliases (client_id, chat_jid, project_name)
           VALUES (%s, %s, %s)
           ON CONFLICT (client_id, chat_jid)
           DO UPDATE SET project_name = EXCLUDED.project_name
           RETURNING id, project_name""",
        (client_id, jid, name),
    )
    row = cur.fetchone()
    print(f"  {jid}")
    print(f"  → {name}  (id={row[0]})")
    
    # Collect unique participants
    for p in g.get("participants", []):
        if isinstance(p["id"], dict):
            pid = p["id"]["_serialized"]
        else:
            pid = p["id"]
        pname = p.get("pushname") or p.get("name") or ""
        # Use phoneNumber as fallback — strip @s.whatsapp.net suffix
        if (not pname or pname == "?") and p.get("phoneNumber"):
            pname = p["phoneNumber"].replace("@s.whatsapp.net", "")
        if not pname or pname == "?":
            pname = f"User_{pid.replace('@lid','')[:6]}"
    updated_projects += 1

conn.commit()

# Step 3: Seed participant_names (only those with real names or all)
inserted_par = 0
skipped_par = 0
for pid, pname in sorted(unique_participants):
    cur.execute(
        """INSERT INTO participant_names (client_id, whatsapp_id, display_name)
           VALUES (%s, %s, %s)
           ON CONFLICT (client_id, whatsapp_id)
           DO UPDATE SET display_name = EXCLUDED.display_name""",
        (client_id, pid, pname),
    )
    if cur.rowcount > 0:
        inserted_par += 1
    else:
        skipped_par += 1

conn.commit()

# Show final state
cur.execute("SELECT chat_jid, project_name FROM project_aliases WHERE client_id = %s ORDER BY project_name", (client_id,))
print(f"\nFinal project aliases ({cur.rowcount}):")
for row in cur.fetchall():
    print(f"  {row[0]} → {row[1]}")

cur.execute("SELECT whatsapp_id, display_name FROM participant_names WHERE client_id = %s ORDER BY display_name", (client_id,))
print(f"\nParticipants ({cur.rowcount}):")
for row in cur.fetchall():
    print(f"  {row[0]} → {row[1]}")

cur.close()
conn.close()

print(f"\nUpdated {updated_projects} project aliases.")
print(f"Inserted {inserted_par} new participants, skipped {skipped_par} existing.")
print("Done.")
