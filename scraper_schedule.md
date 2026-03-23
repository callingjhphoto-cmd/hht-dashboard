# HHT Lead Scraper — Cron Schedule

## Weekly Scrape Runs

### 1. New Venue Discovery
- **Script:** `lead_scraper_v2.py`
- **Schedule:** Every Monday 06:00 UTC
- **Cron:** `0 6 * * 1 cd /Users/jameshuertas/Documents/Claude/projects/hht && python3 lead_scraper_v2.py --mode=discovery >> logs/scraper.log 2>&1`
- **Target:** Home Counties, Oxfordshire, Cotswolds
- **Sources:** SerpAPI (requires key), Hitched, Bridebook, Guides for Brides
- **Output:** `new_leads_YYYY-MM-DD.json`
- **Requires:** SerpAPI key (not yet configured)

### 2. Email Enrichment
- **Script:** `email_enrichment.py` (TO BE BUILT)
- **Schedule:** Every Tuesday 06:00 UTC
- **Cron:** `0 6 * * 2 cd /Users/jameshuertas/Documents/Claude/projects/hht && python3 email_enrichment.py >> logs/enrichment.log 2>&1`
- **Target:** All venues with website but no email
- **Method:** curl scrape of venue contact pages, mailto extraction
- **Output:** Updates existing lead JSON files in-place

### 3. Venue Classification
- **Script:** `venue_classifier.py` (TO BE BUILT)
- **Schedule:** Every Wednesday 06:00 UTC
- **Cron:** `0 6 * * 3 cd /Users/jameshuertas/Documents/Claude/projects/hht && python3 venue_classifier.py >> logs/classifier.log 2>&1`
- **Target:** Unclassified venues (UNKNOWN tag)
- **Method:** Website scrape for "dry hire", "approved suppliers", "bring your own" keywords
- **Output:** `venue_classifications.json`

### 4. Dashboard Refresh
- **Schedule:** After each scrape completes
- **Action:** Rebuild `hht_dashboard.html` with updated counts
- **Push:** Auto-push to GitHub Pages if data changed

## Cron Installation (macOS launchd alternative)

For "The Bunker" (always-on server), use launchd plist:
```
~/Library/LaunchAgents/com.hht.scraper.plist
```

For "The Nomad" (laptop), run manually or use crontab when connected.

## Rate Limits
- Max 1 request per 2 seconds to any single domain
- SerpAPI: 100 searches/month (free tier)
- No scraping between 22:00-06:00 UK time (respect robots.txt)

## Dependencies
- Python 3.9+
- `requests`, `beautifulsoup4` (pip install)
- SerpAPI key: not yet configured (James action)
- GitHub token: $GITHUB_TOKEN_LIQUID (configured)

## Status
- lead_scraper_v2.py: EXISTS but needs SerpAPI key for full runs
- email_enrichment.py: NOT YET BUILT
- venue_classifier.py: NOT YET BUILT
- Cron not yet installed — manual runs only
