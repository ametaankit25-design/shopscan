"""
Import all 885 records to TiDB by truncating and re-importing
"""
import pymysql
import sys

# TiDB Connection
DB_HOST = "gateway01.ap-northeast-1.prod.aws.tidbcloud.com"
DB_PORT = 4000
DB_USER = "LDFob2SC4JiXGN1.root"
DB_PASSWORD = "55jHw5sR6Nmee7ak"
DB_NAME = "listings_db"

print("=" * 60)
print("TiDB Full Data Import - 885 Records")
print("=" * 60)

try:
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    print("✅ Connected to TiDB")
    
    with connection.cursor() as cursor:
        # Check current count
        cursor.execute("SELECT COUNT(*) as count FROM listing_master")
        before_count = cursor.fetchone()['count']
        print(f"\n📊 Current records: {before_count}")
        
        # Truncate table
        print("\n🗑️  Clearing existing records...")
        cursor.execute("TRUNCATE TABLE listing_master")
        connection.commit()
        print("✅ Table cleared")
        
        # Connect to local Docker MySQL and copy data
        print("\n📡 Connecting to local Docker MySQL...")
        source_conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='rootpass',
            database='listings_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✅ Connected to source database")
        
        with source_conn.cursor() as source_cursor:
            # Fetch all records from source
            print("\n📥 Fetching all records from Docker MySQL...")
            source_cursor.execute("""
                SELECT business_name, category, city, address, phone, 
                       source, image_url, created_at
                FROM listing_master
                ORDER BY id
            """)
            records = source_cursor.fetchall()
            print(f"✅ Fetched {len(records)} records")
            
            # Insert in batches
            print("\n📤 Inserting records to TiDB...")
            batch_size = 100
            inserted = 0
            
            sql = """
                INSERT INTO listing_master 
                (business_name, category, city, address, phone, source, image_url, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                
                # Prepare batch data
                batch_data = []
                for record in batch:
                    batch_data.append((
                        record['business_name'],
                        record['category'],
                        record['city'],
                        record['address'],
                        record['phone'],
                        record['source'],
                        record['image_url'],
                        record['created_at']
                    ))
                
                # Execute batch insert
                cursor.executemany(sql, batch_data)
                connection.commit()
                inserted += len(batch)
                print(f"  Progress: {inserted}/{len(records)} records...")
            
            print(f"\n✅ Inserted {inserted} records")
        
        source_conn.close()
        
        # Verify final count
        cursor.execute("SELECT COUNT(*) as count FROM listing_master")
        after_count = cursor.fetchone()['count']
        
        print(f"\n📊 Final count: {after_count} records")
        
        # Show breakdown
        cursor.execute("SELECT city, COUNT(*) as count FROM listing_master GROUP BY city ORDER BY count DESC")
        cities = cursor.fetchall()
        print(f"\n🏙️ Top cities:")
        for city in cities[:10]:
            print(f"   - {city['city']}: {city['count']} listings")
        
        cursor.execute("SELECT category, COUNT(*) as count FROM listing_master GROUP BY category ORDER BY count DESC")
        categories = cursor.fetchall()
        print(f"\n📑 Top categories:")
        for cat in categories[:10]:
            print(f"   - {cat['category']}: {cat['count']} listings")
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Data imported to TiDB")
        print("=" * 60)
        
except pymysql.Error as e:
    print(f"\n❌ Database error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    if 'connection' in locals():
        connection.close()
        print("\n🔌 Connection closed")
