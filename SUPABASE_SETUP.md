# HHT Supabase Setup Guide

**Status:** Schema ready. Migration script ready. Awaiting Supabase project credentials from James.

---

## What's Already Built

| File | Purpose |
|------|---------|
| `database/schema.sql` | Full PostgreSQL schema — 6 tables, indexes, RLS policies, triggers |
| `database/migrate_venues.py` | Reads all enriched venue JSONs, scores them, outputs SQL + CSV + SQLite |
| `database/import_venues.sql` | Pre-generated SQL INSERT statements for 361 venues |
| `database/import_venues.csv` | CSV bulk import file |
| `database/hht.db` | Local SQLite copy (working right now — no cloud needed yet) |
| `api/app.py` | FastAPI backend (7 endpoints), currently talks to SQLite |

## Schema Summary

```
venues          — 502 venues, priority scored 0-100, tiered CALL_NOW→LOW
outreach        — email/call/DM tracking per venue
bookings        — confirmed events, revenue tracking, margin calculation
outreach_templates — 10 A/B-tested email templates
activity_log    — full audit trail
daily_metrics   — dashboard reporting snapshots
```

---

## One-Time Setup (When James Creates Supabase Project)

### Step 1 — Create Free Supabase Project

1. Go to https://supabase.com and sign up (free)
2. Click "New Project"
3. Name it: `hht-operations`
4. Choose region: **West EU (London)**
5. Set a strong database password (save it somewhere safe)
6. Wait ~2 minutes for project to provision

### Step 2 — Get Connection Details

In Supabase dashboard: **Project Settings → Database → Connection string**

Copy the **URI** format, which looks like:
```
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres
```

Also note your **Project URL** and **anon/public API key** from:
**Project Settings → API → Project URL + Project API keys**

### Step 3 — Set Environment Variables

```bash
export SUPABASE_URL="https://xxxxxxxxxxxx.supabase.co"
export SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."   # anon key
export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres"
```

Or add to `~/.zshrc` for persistence:
```bash
echo 'export SUPABASE_URL="..."' >> ~/.zshrc
echo 'export SUPABASE_KEY="..."' >> ~/.zshrc
echo 'export DATABASE_URL="..."' >> ~/.zshrc
source ~/.zshrc
```

### Step 4 — Run the Schema (Single Command)

In the Supabase dashboard, go to **SQL Editor** and paste the entire contents of:
```
~/Documents/Claude/projects/hht/database/schema.sql
```

Click **Run**. This creates all 6 tables, indexes, RLS policies, and triggers.

Alternatively, run via `psql`:
```bash
psql "$DATABASE_URL" -f ~/Documents/Claude/projects/hht/database/schema.sql
```

### Step 5 — Migrate All 361 Venues (Single Command)

```bash
cd ~/Documents/Claude/projects/hht
python3 database/migrate_venues.py --format sql
```

Then in Supabase SQL Editor, paste the generated `database/import_venues.sql` and run it.

Or direct via psql:
```bash
psql "$DATABASE_URL" -f ~/Documents/Claude/projects/hht/database/import_venues.sql
```

This imports all 361 enriched venues with:
- Priority scores (0-100)
- Tiers: 37 CALL_NOW, 12 HIGH_PRIORITY, 31 STANDARD, 255 NURTURE, 26 LOW
- Classification: DRY_HIRE / EXTERNAL_OK / IN_HOUSE_ONLY / UNKNOWN

### Step 6 — Connect the API

Update `api/app.py` to use Supabase instead of SQLite:

```bash
pip install supabase
```

Then in `api/app.py`, swap the SQLite connection for:
```python
from supabase import create_client
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
```

The API is already structured for this — it's a ~20 line swap.

### Step 7 — Verify

```bash
# Check venues imported
curl http://localhost:8000/venues?tier=CALL_NOW | python3 -m json.tool | head -40

# Check dashboard stats
curl http://localhost:8000/dashboard | python3 -m json.tool
```

---

## Current Tier Distribution (from last migrate run)

| Tier | Count | Description |
|------|-------|-------------|
| CALL_NOW | 37 | Score 80+, verified email, DRY_HIRE — phone Joe immediately |
| HIGH_PRIORITY | 12 | Score 65-79, good signal |
| STANDARD | 31 | Score 50-64 |
| NURTURE | 255 | Score 25-49, needs enrichment |
| LOW | 26 | Score 0-24, hotels/in-house |

---

## No Supabase Yet? SQLite Works Fine

The local SQLite database at `database/hht.db` already contains all 361 venues and is working right now. The FastAPI backend (`api/app.py`) uses it natively.

To use the local API:
```bash
pip install fastapi uvicorn
uvicorn api.app:app --reload --port 8000
```

Then open http://localhost:8000/docs for the interactive API explorer.

---

## Cost

- **Free tier:** 500MB DB, 2GB bandwidth, unlimited API calls — plenty for this use case
- **Pro tier ($25/month):** If Joe scales to 5,000+ venues — not needed yet

---

## Questions?

Contact James. Do not create the Supabase project yet — wait for James to provide credentials in Step 2. Everything else is ready and waiting.
