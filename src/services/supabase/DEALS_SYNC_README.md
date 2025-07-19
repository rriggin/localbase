# RoofMaxx Deals Sync to Supabase

**Store all 868 deals permanently for analytics and business intelligence! 📊**

## 🎯 What This Does

- ✅ **Creates** a `roofmaxx_deals` table in your Supabase database
- ✅ **Fetches** all 868 deals from RoofMaxx Connect API  
- ✅ **Stores** them in Supabase with proper indexing
- ✅ **Provides** instant analytics on your stored data
- ✅ **Enables** dashboards, reporting, and advanced analytics

## 🚀 Quick Start

### 1. Get Supabase Credentials

1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Create a project (free tier works!)
3. Go to **Settings** → **API**
4. Copy your:
   - **Project URL** (looks like `https://xxx.supabase.co`)
   - **Service Role Key** (starts with `eyJ...`)

### 2. Run the Sync

```bash
# Easy way - interactive setup
python3 src/services/supabase/setup_deals_sync.py

# Or set environment variables first
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
python3 src/services/supabase/setup_deals_sync.py
```

### 3. Enjoy Your Data! 

Once synced, you can:
- 📊 Query deals by source: `SELECT deal_type, count(*) FROM roofmaxx_deals GROUP BY deal_type`
- 🗺️ Geographic analysis: `SELECT city, state, count(*) FROM roofmaxx_deals GROUP BY city, state`
- 📈 Timeline analysis: `SELECT DATE(create_date), count(*) FROM roofmaxx_deals GROUP BY DATE(create_date)`
- 💼 Build dashboards with tools like Grafana, Retool, or custom apps

## 📊 Database Schema

The `roofmaxx_deals` table includes:

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Primary key |
| `deal_id` | BIGINT | RoofMaxx deal ID |
| `deal_type` | TEXT | Lead source (NAP, RMCL, etc.) |
| `deal_lifecycle` | TEXT | Lead, Lost, etc. |
| `customer_email` | TEXT | Customer contact |
| `city`, `state` | TEXT | Geographic data |
| `create_date` | TIMESTAMPTZ | When deal was created |
| `raw_data` | JSONB | Complete API response |

## 🔄 Ongoing Sync

After initial sync, you can:

```python
# Manual sync update
from src.services.supabase import DealsSyncService

sync_service = DealsSyncService(roofmaxx_config, supabase_config)
sync_status = sync_service.run_full_sync()
```

## 📈 Analytics Examples

```python
# Get business summary
from src.services.supabase import DealsAnalytics

analytics = DealsAnalytics(supabase_config)
summary = analytics.get_business_summary()

# Custom queries
deals_by_source = analytics.get_deals_by_source()
conversion_metrics = analytics.get_conversion_metrics()
```

## 🎉 What You Get

- **Permanent storage** of all your deals data
- **Fast queries** with proper indexing
- **Backup protection** - your data is safe
- **Dashboard ready** - connect any BI tool
- **Scalable** - handles growth as your business expands

**Tom's going to love this permanent business intelligence! 🍆💥** 