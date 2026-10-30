# 🚀 Deployment Guide - TiDB Configuration

## Problem
Backend is showing only 28 listings (sample data) instead of full TiDB database.

## Root Cause
Backend environment variables not configured to connect to TiDB MySQL database.

---

## ✅ Solution: Configure TiDB Connection

### Step 1: Get TiDB Connection Details

From TiDB Cloud Console:
1. Go to your TiDB cluster
2. Click "Connect"
3. Copy the connection details:
   - **Host**: `gateway01.[region].prod.aws.tidbcloud.com`
   - **Port**: `4000`
   - **Username**: `[user].[cluster-id]` (e.g., `4QnF8VRhqK8zwY7.root`)
   - **Password**: Your database password
   - **Database**: `listings_db`

### Step 2: Configure Environment Variables

Choose your deployment platform:

---

## 🔷 **Render** (Recommended)

### Method A: Using DATABASE_URL (Recommended)

1. Go to https://dashboard.render.com
2. Select your backend service
3. Go to **Environment** tab
4. Add environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: `mysql+pymysql://[username]:[password]@[host]:4000/listings_db?ssl_mode=VERIFY_IDENTITY`
   
   **Example:**
   ```
   mysql+pymysql://4QnF8VRhqK8zwY7.root:YourPassword123@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/listings_db?ssl_mode=VERIFY_IDENTITY
   ```

5. Click **Save Changes**
6. Render will auto-redeploy

### Method B: Using Individual Variables

Add these environment variables:
```
DB_USER=4QnF8VRhqK8zwY7.root
DB_PASSWORD=YourPassword123
DB_HOST=gateway01.ap-southeast-1.prod.aws.tidbcloud.com
DB_PORT=4000
DB_NAME=listings_db
```

---

## 🔷 **Railway**

1. Go to https://railway.app/dashboard
2. Select your project
3. Click on the backend service
4. Go to **Variables** tab
5. Add **DATABASE_URL**:
   ```
   mysql+pymysql://[username]:[password]@[host]:4000/listings_db?ssl_mode=VERIFY_IDENTITY
   ```
6. Click **Deploy** or wait for auto-deploy

---

## 🔷 **Vercel Functions** (Backend as Serverless)

1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add:
   - **Variable**: `DATABASE_URL`
   - **Value**: `mysql+pymysql://[username]:[password]@[host]:4000/listings_db?ssl_mode=VERIFY_IDENTITY`
5. Select environment: **Production**, **Preview**, **Development**
6. Click **Save**
7. Redeploy: **Deployments** → **...** → **Redeploy**

---

## 🔷 **Heroku**

```bash
# Using Heroku CLI
heroku config:set DATABASE_URL="mysql+pymysql://[username]:[password]@[host]:4000/listings_db?ssl_mode=VERIFY_IDENTITY" -a your-app-name
```

Or via Heroku Dashboard:
1. Go to app settings
2. **Config Vars** → **Reveal Config Vars**
3. Add DATABASE_URL

---

## 🔷 **AWS Elastic Beanstalk**

1. Go to Elastic Beanstalk console
2. Select your environment
3. **Configuration** → **Software**
4. **Environment Properties** → Add:
   - `DATABASE_URL`: `mysql+pymysql://...`
5. **Apply**

---

## 🔷 **Google Cloud Run**

```bash
gcloud run services update backend-service \
  --update-env-vars DATABASE_URL="mysql+pymysql://[username]:[password]@[host]:4000/listings_db?ssl_mode=VERIFY_IDENTITY"
```

---

## 🔷 **Digital Ocean App Platform**

1. Go to app settings
2. Click your backend component
3. **Environment Variables** → **Edit**
4. Add DATABASE_URL
5. **Save** → App will redeploy

---

## 🧪 Verify Connection

After setting environment variables:

### 1. Check Deployment Logs

Look for:
```
✅ Connected to MySQL database successfully
```

**NOT:**
```
⚠️ MySQL unreachable. Using local SQLite fallback
```

### 2. Test API Endpoint

```bash
# Check health endpoint
curl https://your-backend-url/health

# Expected response:
{"status":"ok","database":"ok"}
```

### 3. Check Listings Count

```bash
curl https://your-backend-url/api/stats/overview
```

**Expected:**
```json
{
  "total_listings": 500+,  // NOT 28!
  "total_cities": 10+,
  "total_categories": 5+,
  "total_sources": 2
}
```

---

## 🔍 Troubleshooting

### Issue: Still showing 28 listings

**Cause:** Environment variables not loaded or wrong format

**Fix:**
1. Verify DATABASE_URL format is correct
2. Ensure no spaces in the connection string
3. Password must be URL-encoded if it contains special characters
4. Redeploy after setting env vars

### Issue: "Database unavailable" error

**Cause:** TiDB connection rejected

**Fix:**
1. Check TiDB cluster is running
2. Verify IP whitelist (TiDB → Security Settings)
3. Add `0.0.0.0/0` to allow all IPs (for testing)
4. Verify username/password are correct

### Issue: SSL/TLS errors

**Cause:** SSL configuration mismatch

**Fix:** Use one of these in DATABASE_URL:
```
# Option 1: Disable SSL verification (testing only)
?ssl_mode=DISABLED

# Option 2: Verify identity (production)
?ssl_mode=VERIFY_IDENTITY

# Option 3: Require SSL but don't verify
?ssl_mode=REQUIRED
```

---

## 📊 Expected Results After Fix

### Dashboard Stats:
- **Total Listings**: 500+ (not 28)
- **Destinations Covered**: 10+
- **Active Categories**: 5+

### Data Origin Chart:
- Should show breakdown: OpenStreetMap vs Mock

### Listings Page:
- Should show all cities from your SQL dump
- Pagination should have multiple pages

---

## 🎯 Quick Test Commands

### Local Testing:
```bash
# In backend folder
export DATABASE_URL="mysql+pymysql://[user]:[pass]@[host]:4000/listings_db"
uvicorn app.main:app --reload

# Should see in logs:
# INFO: Connected to MySQL database successfully
# INFO: Database already has XXX listings. Skipping seed.
```

### Production Testing:
```bash
# Test from your deployed URL
curl https://your-backend.onrender.com/api/stats/overview
```

---

## 💡 Pro Tips

1. **URL Encode Passwords**: If password has special chars (`@`, `#`, `$`, etc.):
   ```python
   from urllib.parse import quote_plus
   password = quote_plus("MyP@ssw0rd!")
   ```

2. **TiDB Free Tier Limitations**:
   - May hibernate after inactivity
   - First request might be slow (cold start)
   - Connection timeout of 5 seconds is usually enough

3. **Environment-Specific URLs**:
   ```
   # Development
   DATABASE_URL=sqlite:///./listings.db
   
   # Production
   DATABASE_URL=mysql+pymysql://...
   ```

---

## 📞 Need Help?

If you're still stuck, tell me:
1. Which platform are you deploying to? (Render/Railway/Vercel/etc.)
2. Can you access TiDB console?
3. What do the deployment logs show?

I'll provide platform-specific instructions!
