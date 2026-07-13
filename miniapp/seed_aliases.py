"""Find unique group chat JIDs from evolution DB for the Gritline client."""
import os, sys
from pathlib import Path
import psycopg2
import psycopg2.extras

# Load .env
env_path = Path(__file__).parent / ".env"
for line in env_path.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, _, val = line.partition("=")
        os.environ[key.strip()] = val.strip()

client_id = "132182030958640@lid"

conn = psycopg2.connect(
    host=os.getenv("PGHOST", "100.106.84.62"),
    port=int(os.getenv("PGPORT", "5432")),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    dbname="evolution",
    cursor_factory=psycopg2.extras.RealDictCursor,
)
cur = conn.cursor()

# Collect unique JIDs from all three tables
all_jids = set()

for table, col in [("tasks", "remotejid"), ("client_meetings", "chat_id"), ("pending_triage", "chat_id")]:
    cur.execute(
        f"SELECT DISTINCT {col} FROM {table} WHERE client_id = %s AND {col} IS NOT NULL",
        (client_id,),
    )
    jids = [r[col] for r in cur.fetchall()]
    print(f"{table}.{col}: {len(jids)} unique")
    for j in sorted(jids):
        print(f"  {j}")
    all_jids.update(jids)

print(f"\nTotal unique JIDs: {len(all_jids)}")

cur.close()
conn.close()

# Now insert into endflo-gritline
conn2 = psycopg2.connect(
    host=os.getenv("PGHOST", "100.106.84.62"),
    port=int(os.getenv("PGPORT", "5432")),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    dbname="endflo-gritline",
)
cur2 = conn2.cursor()

inserted = 0
for jid in sorted(all_jids):
    # Generate a simple project name from the JID
    # Use the JID prefix as a placeholder name
    short = jid.split("@")[0][:8]
    proj_name = f"Group {short}"
    try:
        cur2.execute(
            """INSERT INTO project_aliases (client_id, chat_jid, project_name)
               VALUES (%s, %s, %s)
               ON CONFLICT (client_id, chat_jid) DO NOTHING""",
            (client_id, jid, proj_name),
        )
        if cur2.rowcount > 0:
            inserted += 1
            print(f"  INSERTED: {jid} → {proj_name}")
        else:
            print(f"  SKIPPED (exists): {jid}")
    except Exception as e:
        print(f"  ERROR on {jid}: {e}")

conn2.commit()
cur2.close()
conn2.close()

print(f"\nInserted {inserted} new project aliases.")
print("Done.")
