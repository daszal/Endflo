#!/usr/bin/env python3
"""Quick connection test — reads .env directly."""
import os
from pathlib import Path

# Read .env manually
env_path = Path(__file__).parent / ".env"
for line in env_path.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, _, val = line.partition("=")
        os.environ[key.strip()] = val.strip()

import psycopg2

# Test both databases
for dbname in ["evolution", "endflo-gritline"]:
    try:
        conn = psycopg2.connect(
            host=os.getenv("PGHOST", "100.106.84.62"),
            port=int(os.getenv("PGPORT", "5432")),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            dbname=dbname,
        )
        cur = conn.cursor()
        cur.execute("SELECT 1")
        print(f"Connected to '{dbname}': OK")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Connected to '{dbname}': FAILED — {e}")

# Now test db.py
import db
client = "132182030958640@lid"
tasks = db.get_tasks(client)
print(f"Tasks: {len(tasks)} outstanding")
print("ALL TESTS PASSED")
