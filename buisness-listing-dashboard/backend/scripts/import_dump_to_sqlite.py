import re
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "..", "listings.db")
dump_path = os.path.join(os.path.dirname(__file__), "..", "..", "database", "dump.sql")

if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS listing_master (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  business_name TEXT NOT NULL,
  category TEXT NOT NULL DEFAULT 'Unknown',
  city TEXT NOT NULL DEFAULT 'Unknown',
  address TEXT,
  phone TEXT,
  source TEXT NOT NULL DEFAULT 'Unknown',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  image_url TEXT
);
""")

with open(dump_path, "r", encoding="utf-8", errors="ignore") as f:
    sql = f.read()

insert_count = 0
for idx, line in enumerate(sql.splitlines()):
    if "INSERT INTO" in line and "listing_master" in line:
        insert_count += 1
        clean_line = line.replace("`listing_master`", "listing_master")
        clean_line = clean_line.replace(r"\'", "''")
        clean_line = clean_line.replace(r'\"', '""')
        try:
            cur.execute(clean_line)
        except Exception as e:
            print(f"Error on line {idx}: {e}")

conn.commit()
cur.execute("SELECT COUNT(*) FROM listing_master")
total = cur.fetchone()[0]
print(f"Found {insert_count} INSERT statements. Total listings imported: {total}")
conn.close()
