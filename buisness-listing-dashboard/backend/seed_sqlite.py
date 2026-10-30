"""
Seed SQLite database with sample listings
"""
import sqlite3
from datetime import datetime
from pathlib import Path

# Sample data
listings = [
    ("Good Luck Restaurant", "Restaurant", "Mumbai", "M Kahn Chowk, Mumbai, 400050", "02226422250", "OpenStreetMap"),
    ("Cafe Mondegar", "Cafe", "Mumbai", "Chhatrapati Shivaji Maharaj Road, Mumbai", "22020591", "OpenStreetMap"),
    ("Villa 39", "Restaurant", "Mumbai", "60, Madame Cama Road, Mumbai, 400039", "+91 22 6657 3939", "OpenStreetMap"),
    ("Kala Ghoda Cafe", "Cafe", "Mumbai", "10, Rope Walk Street, Mumbai, 400001", "+91 22 2265 0195", "OpenStreetMap"),
    ("The Bagel Shop", "Cafe", "Mumbai", "30, Pali Mala Road, Bandra West, Mumbai, 400050", "+91 22 2605 0178", "OpenStreetMap"),
    ("Lifeline", "Pharmacy", "Mumbai", "1, Off Yari Road, Mumbai, 400061", "+912226378686", "OpenStreetMap"),
    ("Wellness Forever", "Pharmacy", "Mumbai", "7, Central Avenue, Mumbai, 400076", "022 6162 0659", "OpenStreetMap"),
    ("Starbucks", "Cafe", "Mumbai", "Boraspada Road, Mumbai, 400067", "073044 75255", "OpenStreetMap"),
    ("Blue Tokai Coffee Roasters", "Cafe", "Mumbai", "New Kantwadi Road, Bandra West, Mumbai, 400050", "+91 90825 66400", "OpenStreetMap"),
    ("Cafe Coffee Day", "Cafe", "Mumbai", "123, Ganesh Purushottam Rd, Thane, 400605", "+91 9807965789", "OpenStreetMap"),
    
    ("Cafe Turtle", "Cafe", "Delhi", "Khan Market, New Delhi", "+911124655641", "OpenStreetMap"),
    ("Lama Kitchen Himalayan Cook House", "Restaurant", "Delhi", "Hauz Khas Village Road, New Delhi, 110017", "+911141008883", "OpenStreetMap"),
    ("Keshav Restaurant", "Restaurant", "Delhi", "Radial Road 6, New Delhi, 110001", "+91-90154-84272", "OpenStreetMap"),
    ("Sagar Ratna", "Restaurant", "Delhi", "15, Connaught Place, New Delhi, 110001", "+91 11 4737 7300", "OpenStreetMap"),
    ("Keventers", "Cafe", "Delhi", "GF22 Unity One, Shivaji Road, Delhi, 110058", "+91 92053 45002", "OpenStreetMap"),
    ("Apollo Pharmacy", "Pharmacy", "Delhi", "8, New Delhi", "+91 88269 92200", "OpenStreetMap"),
    ("Medicine House", "Pharmacy", "Delhi", "04, D00, New Delhi, 110001", "+91-95825-34440", "OpenStreetMap"),
    ("Blue Tokai Coffee Roasters", "Cafe", "Delhi", "Khan Market, Rabindra Nagar, New Delhi, 110003", "+91 98219 84555", "OpenStreetMap"),
    ("India Coffee House", "Cafe", "Delhi", "JNU Ring Road, Delhi, 110067", "+919013828749", "OpenStreetMap"),
    ("All India Pharmacy", "Pharmacy", "Delhi", "Lajpat Nagar 4, Delhi, 110024", "011-41038494", "OpenStreetMap"),
    
    ("Mavalli Tiffin Rooms", "Restaurant", "Bangalore", "14, Lalbagh Road, Bangalore, 560027", "+918022220022", "OpenStreetMap"),
    ("The Only Place", "Restaurant", "Bangalore", "13, Museum Road, Bangalore", "+91-80-32718989", "OpenStreetMap"),
    ("Ebony", "Restaurant", "Bangalore", "84, Mahatma Gandhi Road, Bangalore", "+91 8025136611", "OpenStreetMap"),
    ("Adyar Ananda Bhavan", "Restaurant", "Bangalore", "80 Feet Road, Koramangala, Bangalore, 560065", "+91 77950 73031", "OpenStreetMap"),
    ("The Cash Pharmacy", "Pharmacy", "Bangalore", "St. Marks Road, Opp Bishop Cotton Boys School", "080 3361 8456", "OpenStreetMap"),
    ("Swati Deluxe", "Restaurant", "Bangalore", "5, Modi Hospital Main Road, Bangalore, 560010", "+(91)-80-23595565", "OpenStreetMap"),
    ("Gokul Vegetarian", "Restaurant", "Bangalore", "399/34, 19th Main, Bangalore, 560010", "+91 80 2342 3955", "OpenStreetMap"),
    ("Chutney Chang", "Restaurant", "Bangalore", "Museum Road, Bangalore, 560001", "080 4000 1234", "OpenStreetMap"),
]

# Connect to SQLite
db_path = Path(__file__).parent / "listings.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table
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

# Insert data
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
for business_name, category, city, address, phone, source in listings:
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO listing_master 
            (business_name, category, city, address, phone, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (business_name, category, city, address, phone, source, now))
    except Exception as e:
        print(f"Error inserting {business_name}: {e}")

conn.commit()

# Verify
count = cursor.execute("SELECT COUNT(*) FROM listing_master").fetchone()[0]
print(f"✅ Database seeded with {count} listings")

# Show breakdown
print("\nBreakdown by city:")
cursor.execute("SELECT city, COUNT(*) FROM listing_master GROUP BY city ORDER BY COUNT(*) DESC")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} listings")

print("\nBreakdown by category:")
cursor.execute("SELECT category, COUNT(*) FROM listing_master GROUP BY category ORDER BY COUNT(*) DESC")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} listings")

conn.close()
print(f"\n✅ SQLite database ready at: {db_path}")
