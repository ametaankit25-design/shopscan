# 🚀 TiDB Database Setup Guide

## Quick Start - 3 Methods

Choose the method that works best for you:

---

## ✅ **Method 1: Python Script (Easiest - No MySQL Client Required)**

### Step 1: Install Requirements
```bash
cd buisness-listing-dashboard/backend
pip install pymysql
```

### Step 2: Run Import Script
```bash
python import_to_tidb.py
```

### Step 3: Enter TiDB Details When Prompted
```
Enter TiDB Host: gateway01.ap-southeast-1.prod.aws.tidbcloud.com
Enter TiDB Port: 4000
Enter TiDB Username: 4QnF8VRhqK8zwY7.root  (your actual username)
Enter TiDB Password: ********
Enter Database Name: listings_db
```

The script will:
- ✅ Create the database
- ✅ Import all tables and data
- ✅ Show you the record count
- ✅ Verify the import

---

## ✅ **Method 2: TiDB Cloud Console (Web Interface)**

### Step 1: Create Database
1. Go to https://tidbcloud.com
2. Click on your cluster
3. Click **"Chat2Query"** or **"SQL Editor"**
4. Run this command:
```sql
CREATE DATABASE listings_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 2: Import Data
**Option A - Copy/Paste:**
1. Open `buisness-listing-dashboard/database/listing_master.sql` in a text editor
2. Copy the entire content
3. In TiDB SQL Editor, run:
```sql
USE listings_db;
```
4. Paste and execute the SQL dump

**Option B - Import Feature (if available):**
1. Look for **"Import"** or **"Data Import"** button in TiDB Console
2. Upload `listing_master.sql` file
3. Select target database: `listings_db`
4. Click Import

### Step 3: Verify
```sql
USE listings_db;
SELECT COUNT(*) FROM listing_master;
SHOW TABLES;
```

---

## ✅ **Method 3: MySQL Command Line (If you have MySQL installed)**

### Windows PowerShell:
```powershell
cd buisness-listing-dashboard

# First create the database
mysql -u "YOUR_USERNAME" -h gateway01.xxx.tidbcloud.com -P 4000 -p -e "CREATE DATABASE IF NOT EXISTS listings_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"

# Then import
Get-Content database\listing_master.sql | mysql -u "YOUR_USERNAME" -h gateway01.xxx.tidbcloud.com -P 4000 -p listings_db
```

### macOS/Linux:
```bash
cd buisness-listing-dashboard

# Create database
mysql -u 'YOUR_USERNAME' -h gateway01.xxx.tidbcloud.com -P 4000 -p -e "CREATE DATABASE IF NOT EXISTS listings_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"

# Import
mysql -u 'YOUR_USERNAME' -h gateway01.xxx.tidbcloud.com -P 4000 -p listings_db < database/listing_master.sql
```

---

## 🔍 **Get Your TiDB Connection Details**

### From TiDB Cloud Console:
1. Go to https://tidbcloud.com
2. Click your cluster
3. Click **"Connect"** button
4. Copy these details:
   - **Host**: `gateway01.region.prod.aws.tidbcloud.com`
   - **Port**: `4000`
   - **Username**: `xxxx.root` (format varies)
   - **Password**: Your cluster password

---

## 🔧 **After Import: Update Render Environment Variables**

Once data is imported, update your backend deployment:

### In Render Dashboard:
1. Go to your backend service
2. Click **Environment** tab
3. Update or add:
   ```
   DB_NAME=listings_db
   DB_HOST=gateway01.xxx.tidbcloud.com
   DB_PORT=4000
   DB_USER=your_tidb_username
   DB_PASSWORD=your_tidb_password
   ```
4. Save → Render will auto-redeploy

### Verify Deployment:
Watch the Render logs for:
```
✅ Connected to MySQL database successfully
📊 Found XXX existing listings in database
```

---

## ⚠️ **Troubleshooting**

### Issue: "Access denied" or "Connection refused"

**Solution 1: Whitelist Your IP**
1. TiDB Console → Your Cluster → **Security**
2. Click **IP Access List**
3. Add your IP or `0.0.0.0/0` (allow all - for testing only)

**Solution 2: Check Credentials**
- Verify username format (might include cluster ID)
- Ensure password is correct
- Check if cluster is active (not paused/hibernating)

### Issue: "SSL connection error"

Add to your connection string:
```
?ssl_mode=DISABLED
```

Or use the Python script which handles SSL automatically.

### Issue: Import seems stuck

- TiDB free tier has rate limits
- Large imports may take 2-5 minutes
- Check TiDB console for cluster status

---

## ✅ **Verification Checklist**

After import, verify everything works:

### 1. Check Database
```sql
USE listings_db;
SHOW TABLES;
-- Should show: listing_master

SELECT COUNT(*) FROM listing_master;
-- Should show: 500+ (or your record count)

SELECT * FROM listing_master LIMIT 5;
-- Should show sample records
```

### 2. Test Backend API
```bash
# Replace with your Render URL
curl https://your-backend.onrender.com/api/stats/overview

# Should return:
{
  "total_listings": 500+,
  "total_cities": 10+,
  "total_categories": 5+
}
```

### 3. Check Frontend
Visit your deployed frontend:
- Dashboard should show 500+ total listings (not 28!)
- Listings page should have multiple pages
- Filters should show all cities/categories from TiDB

---

## 💡 **Pro Tips**

1. **Keep SQL Dump Updated**: Regenerate regularly
   ```bash
   docker exec mysql_container mysqldump -u user -p database > listing_master.sql
   ```

2. **TiDB Free Tier Limits**:
   - May hibernate after inactivity
   - First request after wake-up is slower
   - Connection timeout: 5 seconds

3. **Backup Important**: TiDB free tier data is not guaranteed
   - Keep your SQL dump in git (if < 100MB)
   - Or store separately

4. **Environment Variables**: Never commit real credentials
   - Use `.env` files locally
   - Use platform env vars for production

---

## 📞 **Need Help?**

If you encounter issues:
1. Check TiDB cluster status in console
2. Verify IP whitelist settings
3. Test connection with `ping gateway01.xxx.tidbcloud.com`
4. Check Render deployment logs for connection errors

---

## 🎉 **Success Criteria**

You'll know it's working when:
- ✅ TiDB shows `listings_db` database
- ✅ Table `listing_master` exists with 500+ rows
- ✅ Render logs show "Connected to MySQL successfully"
- ✅ Frontend shows full data, not just 28 records
- ✅ Dashboard stats match your SQL dump

Good luck! 🚀
