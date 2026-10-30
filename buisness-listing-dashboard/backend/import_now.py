"""
Automated TiDB import with your credentials
"""
import pymysql
from pathlib import Path

# Connection details
DB_HOST = "gateway01.ap-northeast-1.prod.aws.tidbcloud.com"
DB_PORT = 4000
DB_USER = "LDFob2SC4JiXGN1.root"
DB_PASSWORD = "55jHw5sR6Nmee7ak"
DB_NAME = "listings_db"

print("=" * 60)
print("TiDB Data Import")
print("=" * 60)
print(f"Connecting to {DB_HOST}:{DB_PORT}...")

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
        # Create database if needed
        print(f"\n📦 Ensuring database '{DB_NAME}' exists...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {DB_NAME}")
        print(f"✅ Using database '{DB_NAME}'")
        
        # Check current count
        cursor.execute("SELECT COUNT(*) as count FROM listing_master")
        result = cursor.fetchone()
        current_count = result['count'] if result else 0
        print(f"\n📊 Current records in listing_master: {current_count}")
        
        if current_count >= 100:
            print("\n✅ Database already has data!")
            print("Showing breakdown:")
            
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
                
            print(f"\n✅ Total: {current_count} listings ready to use!")
        else:
            print("\n⚠️ Database has less than 100 records")
            print("Importing from SQL dump...")
            
            # Read and execute SQL dump
            sql_file = Path(__file__).parent.parent / "database" / "listing_master_FULL.sql"
            if not sql_file.exists():
                print(f"❌ SQL file not found at: {sql_file}")
                exit(1)
            
            print(f"📄 Reading {sql_file.name}...")
            sql_content = sql_file.read_text(encoding='utf-8')
            
            # Execute SQL dump
            statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
            print(f"📊 Executing {len(statements)} SQL statements...")
            
            for i, statement in enumerate(statements, 1):
                try:
                    if i % 20 == 0:
                        print(f"  Progress: {i}/{len(statements)}...")
                    cursor.execute(statement)
                except Exception as e:
                    # Skip errors for MySQL-specific syntax
                    if '/*!' not in statement:
                        print(f"  ⚠️ Warning: {str(e)[:80]}")
            
            connection.commit()
            print("✅ Import complete!")
            
            # Verify
            cursor.execute("SELECT COUNT(*) as count FROM listing_master")
            new_count = cursor.fetchone()['count']
            print(f"\n📊 New total: {new_count} records")
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS!")
        print("=" * 60)
        print(f"✅ Database: {DB_NAME}")
        print(f"✅ Total Records: {current_count if current_count >= 100 else 'check above'}")
        print("\n📝 Next: Update Render DATABASE_URL if needed")
        print("=" * 60)
        
except pymysql.Error as e:
    print(f"\n❌ Database error: {e}")
    print("\n💡 Tips:")
    print("  - Check if TiDB cluster is running")
    print("  - Verify credentials are correct")
    print("  - Check IP whitelist in TiDB Security Settings")
except Exception as e:
    print(f"\n❌ Error: {e}")
finally:
    if 'connection' in locals():
        connection.close()
        print("\n🔌 Connection closed")
