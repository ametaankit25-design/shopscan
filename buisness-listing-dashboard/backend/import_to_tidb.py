"""
Import SQL dump to TiDB Cloud Database
Run: python import_to_tidb.py
"""
import os
from pathlib import Path
try:
    import pymysql
except ImportError:
    print("❌ pymysql not installed. Run: pip install pymysql")
    exit(1)

# TiDB Connection Details
print("=" * 60)
print("TiDB SQL Import Script")
print("=" * 60)

DB_HOST = input("Enter TiDB Host (e.g., gateway01.xxx.tidbcloud.com): ").strip()
DB_PORT = int(input("Enter TiDB Port (default 4000): ").strip() or "4000")
DB_USER = input("Enter TiDB Username: ").strip()
DB_PASSWORD = input("Enter TiDB Password: ").strip()
DB_NAME = input("Enter Database Name (default: listings_db): ").strip() or "listings_db"

print(f"\n🔌 Connecting to {DB_HOST}:{DB_PORT}...")

try:
    # Connect to TiDB
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    print("✅ Connected successfully!")
    
    with connection.cursor() as cursor:
        # Create database if it doesn't exist
        print(f"\n📦 Creating database '{DB_NAME}' if it doesn't exist...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{DB_NAME}' ready")
        
        # Switch to database
        cursor.execute(f"USE {DB_NAME}")
        
        # Read SQL dump
        sql_file = Path(__file__).parent.parent / "database" / "listing_master.sql"
        if not sql_file.exists():
            print(f"❌ SQL file not found at: {sql_file}")
            exit(1)
        
        print(f"\n📄 Reading SQL dump from: {sql_file.name}")
        sql_content = sql_file.read_text(encoding='utf-8')
        
        # Split into statements (simple split on semicolon)
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
        
        print(f"📊 Found {len(statements)} SQL statements to execute")
        print("\n⏳ Importing data (this may take a minute)...")
        
        # Execute statements
        executed = 0
        for i, statement in enumerate(statements, 1):
            # Skip MySQL-specific commands that might not work in TiDB
            if any(skip in statement for skip in ['/*!40', '/*!50']):
                # Try to execute but don't fail on these
                try:
                    cursor.execute(statement)
                    executed += 1
                except Exception:
                    pass  # Skip MySQL-specific syntax
            else:
                try:
                    cursor.execute(statement)
                    executed += 1
                    if i % 50 == 0:
                        print(f"  Progress: {i}/{len(statements)} statements executed...")
                except Exception as e:
                    print(f"  ⚠️ Warning on statement {i}: {str(e)[:100]}")
        
        connection.commit()
        
        # Verify import
        print("\n✅ Import complete! Verifying...")
        cursor.execute("SELECT COUNT(*) as count FROM listing_master")
        result = cursor.fetchone()
        count = result['count']
        
        print(f"\n" + "=" * 60)
        print(f"🎉 SUCCESS!")
        print(f"📊 Total records in listing_master: {count}")
        
        # Show breakdown
        cursor.execute("SELECT city, COUNT(*) as count FROM listing_master GROUP BY city ORDER BY count DESC LIMIT 5")
        cities = cursor.fetchall()
        print(f"\n🏙️ Top cities:")
        for city in cities:
            print(f"   - {city['city']}: {city['count']} listings")
        
        cursor.execute("SELECT category, COUNT(*) as count FROM listing_master GROUP BY category ORDER BY count DESC LIMIT 5")
        categories = cursor.fetchall()
        print(f"\n📑 Top categories:")
        for cat in categories:
            print(f"   - {cat['category']}: {cat['count']} listings")
        
        print("\n" + "=" * 60)
        print("✅ Your TiDB database is ready!")
        print(f"✅ Update your Render env var: DB_NAME={DB_NAME}")
        print("=" * 60)
        
except pymysql.Error as e:
    print(f"\n❌ Database error: {e}")
    print("\n💡 Tips:")
    print("  - Verify your TiDB credentials")
    print("  - Check if your IP is whitelisted in TiDB Security Settings")
    print("  - Ensure TiDB cluster is running")
except Exception as e:
    print(f"\n❌ Error: {e}")
finally:
    if 'connection' in locals():
        connection.close()
        print("\n🔌 Connection closed")
