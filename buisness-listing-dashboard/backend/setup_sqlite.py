"""
Quick SQLite setup script to create the listing_master table
and import data from the MySQL dump.
"""
import sqlite3
import re
from pathlib import Path

# Connect to SQLite
db_path = Path(__file__).parent / "listings.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table (SQLite syntax)
cursor.execute("""
CREATE TABLE IF NOT EXISTS listing_master (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  business_name VARCHAR(255) NOT NULL,
  category VARCHAR(150) NOT NULL DEFAULT 'Unknown',
  city VARCHAR(100) NOT NULL DEFAULT 'Unknown',
  address TEXT,
  phone VARCHAR(30),
  source VARCHAR(50) NOT NULL DEFAULT 'Unknown',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  image_url VARCHAR(500)
)
""")

# Create unique index
cursor.execute("""
CREATE UNIQUE INDEX IF NOT EXISTS uq_name_city_source 
ON listing_master(business_name, city, source)
""")

# Create indexes
cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON listing_master(category)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_city ON listing_master(city)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON listing_master(source)")

# Parse and import data from SQL dump
sql_file = Path(__file__).parent.parent / "database" / "listing_master.sql"
if sql_file.exists():
    content = sql_file.read_text(encoding='utf-8')
    
    # Extract INSERT statements
    insert_pattern = r"INSERT INTO `listing_master` VALUES \((.*?)\)(?:,|\;)"
    matches = re.findall(insert_pattern, content, re.DOTALL)
    
    print(f"Found {len(matches)} records to import...")
    
    imported = 0
    for match in matches:
        try:
            # Parse values - handle escaped quotes and NULL values
            values = []
            parts = match.split("',")
            for i, part in enumerate(parts):
                part = part.strip()
                if part == 'NULL':
                    values.append(None)
                elif part.startswith("'"):
                    # Remove quotes and handle escaped quotes
                    val = part[1:].replace("\\'", "'")
                    # If this is not the last part, add back the comma we split on
                    if i < len(parts) - 1:
                        values.append(val)
                    else:
                        # Last part might have trailing quote
                        values.append(val.rstrip("'"))
                else:
                    # Numeric value
                    values.append(part.strip("'"))
            
            if len(values) >= 8:  # Ensure we have all required fields
                cursor.execute("""
                    INSERT OR IGNORE INTO listing_master 
                    (id, business_name, category, city, address, phone, source, created_at, image_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values[:9])
                imported += 1
        except Exception as e:
            print(f"Error importing record: {e}")
            continue
    
    print(f"Imported {imported} records successfully!")
else:
    print(f"SQL dump not found at {sql_file}")

# Commit and verify
conn.commit()

# Check count
count = cursor.execute("SELECT COUNT(*) FROM listing_master").fetchone()[0]
print(f"\nTotal records in database: {count}")

# Show some sample data
print("\nSample records:")
cursor.execute("SELECT business_name, category, city FROM listing_master LIMIT 5")
for row in cursor.fetchall():
    print(f"  - {row[0]} ({row[1]}) in {row[2]}")

conn.close()
print(f"\n✅ SQLite database ready at: {db_path}")
