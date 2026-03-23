# HHT EXPANSION PLAN — 502 to 1,000 Venues
**Prepared:** 2026-03-20 | Agent 1: Venue Scraper
**Goal:** Double the pipeline to 1,000+ verified venues. Festival-first priority for Summer 2026.

---

## CURRENT STATE

| Metric | Count |
|--------|-------|
| Total venues in pipeline | 502 |
| With verified email | 45 (9%) |
| DRY_HIRE classified | 78+ |
| New counties scraped (Mar 20) | 8 (96 venues added) |
| Festival/event targets identified | 48 |
| Contact data enriched | 150 (30%) |

**Gap to 1,000:** 498 additional venues needed.

---

## PHASE 1 — IMMEDIATE PRIORITY: SUMMER 2026 FESTIVALS
*Deadline: April 2026 — booking decisions for summer festivals happen now*

These are high-value single relationships worth £5,000-£15,000 each. A festival organiser = one email, one call, one deal — not a year-long supplier list application.

### Tier 1: ORPHANED CLIENTS (Contact This Week)
These formerly used The Cocktail Service (dissolved Apr 2025). No locked-in replacement.

| Festival | Revenue Est. | Contact Deadline | Action |
|----------|-------------|------------------|--------|
| BBC Good Food Show | £15,000+ | By June 2026 | Email info@goodfoodshow.com + advertising@immediate.co.uk. Pitch: cocktail masterclass + bar concession for Nov/Dec 2026 shows at NEC, Olympia, Glasgow SEC |
| Blenheim Palace Food Festival | £8,000 | URGENT — May 2026 | Email Blenheim events team via blenheimpalace.com/events. Pitch: cocktail bar for 3-day food festival. Joe's Bombay Sapphire/Belvedere credentials are perfect here. |
| Pub in the Park | £8,000/weekend | Verify first | Domain expired pubinthepark.com. CHECK INSTAGRAM before contacting. If still operating, find Tom Kerridge's production company. |

### Tier 2: Summer 2026 Targets (Contact April)

| Festival | Revenue Est. | Location | Priority |
|----------|-------------|----------|----------|
| Taste of London | £15,000 | Regent's Park, June | HIGH — most prestigious food festival |
| Henley Royal Regatta | £12,000 | Oxfordshire, Jun-Jul | HIGH — target geo, premium audience |
| The Big Feastival | £12,000 | Oxfordshire (Alex James' farm), Aug | HIGH — target geo, boutique |
| Wilderness Festival | £10,000 | Cornbury Park, Oxfordshire, Aug | HIGH — target geo |
| Henley Festival | £10,000 | Oxfordshire, July | HIGH — target geo, black-tie |
| CLA Game Fair | £10,000 | Ragley Hall, Warwickshire, July | HIGH — premium rural audience |
| Glorious Goodwood | £12,000 | West Sussex, July | HIGH — hospitality boxes |
| Cartier Queen's Cup Polo | £10,000 | Windsor, Berkshire, June | HIGH — target geo |
| Royal Ascot | £15,000 | Berkshire, June | HIGH — target geo, corporate suites |
| Great British Food Festival | £5,000+ | Circuit of 10+ events | HIGH — one deal = multiple events. Contact the circuit organiser (greatbritishfoodfestival.com) — Berkshire, Wiltshire, Surrey all in target geo |
| Cowdray Gold Cup Polo | £8,000 | West Sussex, Jun-Jul | HIGH |
| Glyndebourne | £8,000 | East Sussex, May-Aug | HIGH — ultra-premium |
| Meatopia | £10,000 | London/Glasgow, September | MEDIUM — already has cocktail slots |
| South of England Show | £8,000 | Ardingly, West Sussex, June | MEDIUM |
| Royal Berkshire Show | £6,000 | Newbury, September | MEDIUM — target geo |
| Surrey County Show | £5,000 | Guildford, May | MEDIUM — target geo |
| Luna Cinema | £5,000 | Multiple — Blenheim, Kew, Hampton Court | MEDIUM — one partnership covers all venues |
| Highclere Castle events | £8,000 | Hampshire/Berkshire border | MEDIUM — Downton Abbey — corporate/charity |
| Waddesdon Manor (Christmas Fair) | £8,000 | Buckinghamshire | MEDIUM — target geo, Christmas window |

**Festival outreach script:** Use `festival` template in email_templates.py. Key differentiator: "We can bring spirit brand co-funding — means a better bar at lower cost to you."

---

## PHASE 2 — GEOGRAPHIC EXPANSION (April-June 2026)
*Target: +200 venues from new counties*

### Already Identified: 96 Venues Across 8 New Counties
File: `~/Documents/Claude/projects/hht/expansion/new_counties.json`
These are all DRY_HIRE classified with 0% email enrichment. Priority for contact_enricher.py run.

| County | Venues Identified | Enrichment Priority | Top Targets |
|--------|------------------|---------------------|-------------|
| Cambridgeshire | ~12 | HIGH | Waresley Park Estate (cap 250), Bassmead Manor Barns (cap 200), Histon Manor |
| Norfolk | ~10 | HIGH | Voewood, Oxnead Hall, Godwick Hall (already in enriched pipeline) |
| Suffolk | ~12 | HIGH | Glemham Hall, Henham Barns, Copdock Hall |
| Somerset | ~10 | HIGH | Elmhay Park, Pennard Hill Farm, St Audries Park |
| Devon | ~12 | MEDIUM | Huntsham Court, The Great Barn Devon, Rockbeare Manor |
| Dorset | ~10 | MEDIUM | Hale Park, Mapperton, Sopley Lake |
| Warwickshire | ~12 | MEDIUM | Wootton Park, Talton Lodge, Alveston Pastures Farm |
| Kent | ~10 | MEDIUM | Westenhanger Castle, The Hop Farm, Kent Event Centre |

**Action:** Run contact_enricher.py against new_counties.json — priority order: Cambridgeshire, Norfolk, Suffolk (closest to London, highest venue density).

### Directories NOT Yet Scraped

| Directory | Type | Status | Priority | Notes |
|-----------|------|--------|----------|-------|
| **Bark.com** | Service marketplace | NOT SCRAPED | HIGH | Venues requesting cocktail bar quotes = proven buyers. Filter by "mobile bar hire" category in target postcodes |
| **Google Maps API** | General | PARTIAL | HIGH | lead_scraper_v2.py covers cities only. Need to extend to postcode prefixes: OX, GL, RG, HP, SL, GU, RH, CB, NR, IP, BA, CT |
| **Instagram** | Social | NOT SCRAPED | HIGH | Two strategies: (1) scrape competitor follower lists — venues following Sweet & Chilli, Create Cocktails = proven buyers; (2) scrape #dryhirevenue, #barnwedding, #cotswoldsvenue hashtags |
| **Guides for Brides** | Wedding directory | PARTIAL | HIGH | hht_dryhire_scraper.py covers 8 counties. Extend to: Cambridgeshire, Norfolk, Suffolk, Somerset, Dorset, Kent, Warwickshire, Devon |
| **Hitched.co.uk** | Wedding directory | PARTIAL | HIGH | lead_scraper_v2.py covers some. Run dedicated Hitched scrape for dry hire filter across all 17 target counties |
| **Bridebook** | Wedding directory | NOT SCRAPED | HIGH | Sister platform to Hitched. Different venue database — deduplicate against existing |
| **Tagvenue** | Corporate venue directory | NOT SCRAPED | MEDIUM | Corporate event spaces with dry hire option. Good for corporate template pipeline |
| **Venuescanner** | Corporate/event | NOT SCRAPED | MEDIUM | Similar to Tagvenue — corporate spaces |
| **Coco Wedding Venues** | Wedding directory | PARTIAL (used in research) | MEDIUM | High-quality curated list. Good for premium tier |
| **Quintessentially Weddings** | Luxury wedding directory | NOT SCRAPED | MEDIUM | Ultra-premium tier — venues here are Joe's highest-value targets |
| **The Wedding Secret** | Wedding directory | NOT SCRAPED | LOW | Covers areas not on Hitched/Bridebook |
| **Marry Abroad / Weddings Abroad Guide** | Destination weddings | NOT SCRAPED | LOW | Lower priority, UK-focused expansion first |
| **Companies House** | Business registration | NOT SCRAPED | MEDIUM | Cross-reference SIC code 93299 (other amusement/recreation) + 56210 (event catering) for competitor mapping |

---

## PHASE 3 — INSTAGRAM + COMPETITOR INTELLIGENCE SCRAPING (May 2026)
*Target: +100 venues via social proof approach*

### Strategy: Scrape Competitor Clients (Proven Buyers)
Any venue that has used a competitor = proven buyer of cocktail bar services.

**Priority targets for Instagram scraping:**
1. **Sweet & Chilli** (@sweetandchilli) — tag their client venues in posts
2. **Create Cocktails** — search their posts for venue mentions
3. **The Cotswold Bar Company** — Cotswolds-specific, high overlap with target geo
4. **The Oxford Bar Company** — Oxfordshire overlap

**Methodology:**
- Search competitor Instagram for tagged venues
- Cross-reference venue names against existing pipeline
- Net new venues = COMPETITOR_CLIENT classification = highest priority (proven buyer)
- These venues go directly to CALL_NOW tier regardless of rubric score

**Hashtag scraping:**
- `#dryhirevenue` — UK posts only
- `#barnweddingreception` — venues visible in photos
- `#cotswoldswedding` — target geo
- `#oxfordshirewedding` — target geo
- `#countryousewedding` — premium tier

---

## PHASE 4 — BARK.COM SCRAPING (April 2026)
*Target: +50 warm leads from active buyers*

Bark.com shows venues that have already posted requests for cocktail bar hire. These are live buyers, not cold leads.

**Search parameters:**
- Category: Mobile Bar Hire / Cocktail Bar Hire
- Location: Oxfordshire, Berkshire, Surrey, Buckinghamshire, Gloucestershire, Hampshire, Hertfordshire, Wiltshire
- Filter: Posted in last 3 months

**Script:** Extend lead_scraper_v2.py with Bark module, or build hht_bark_scraper.py.
**Key difference from venue scraping:** These are event bookers, not venues. They may be wedding planners, corporate event companies, or private individuals. Add to a separate "active_buyers" list.

---

## PHASE 5 — WEDDING PLANNER MULTIPLIER (Ongoing)
*Target: +50 planners = 500-1,000 indirect bookings*

One wedding planner relationship = 10-20 bookings/year. This is the highest-leverage expansion.

**Currently in pipeline:** 64 planners in wedding-planners.csv (limited contact info)

**Where to find more:**
- **The Wedding Industry Awards (TWIA)** — shortlisted planners across all counties
- **Hitched.co.uk** — planner directory, filter by county
- **The Wedding Planner Association (TWPA)** — member directory
- **Association of British Professional Conference Organisers (ABPCO)** — for corporate planners
- **Instagram** — #weddingplanner + county hashtag

**Outreach approach:** Use wedding template but emphasise reliability for planners — they stake their reputation on suppliers. Joe's 25-year CV is the key differentiator.

---

## HOW TO GET FROM 502 TO 1,000 VENUES

| Source | Target Venues | Timeline | Script/Method |
|--------|--------------|----------|---------------|
| New counties enrichment (8 counties, 96 venues identified) | +96 | April | contact_enricher.py on new_counties.json |
| Guides for Brides extension (8 new counties) | +80 | April | Extend hht_dryhire_scraper.py with CB, NR, IP, BA, DT, CT, CV, EX postcode pages |
| Hitched.co.uk dedicated scrape (17 counties, dry hire filter) | +80 | April-May | New Hitched module in lead_scraper_v2.py |
| Bridebook (not yet scraped at all) | +60 | May | New Bridebook scraper |
| Bark.com active buyers | +50 | April | New Bark module |
| Instagram competitor clients | +50 | May | Manual + scraper |
| Google Maps API extension to postcode areas | +60 | April | lead_scraper_v2.py with postcode extension |
| Wedding planners enrichment | +50 | Ongoing | Expand wedding-planners.csv |
| Tagvenue / Venuescanner corporate | +30 | June | New corporate scraper module |
| **TOTAL PROJECTED ADDITIONS** | **+556** | By June 2026 | |
| **PROJECTED TOTAL** | **1,058** | June 2026 | |

---

## FESTIVAL SUMMER 2026 — PRIORITY EXECUTION TIMELINE

```
MARCH (NOW):
  - WhatsApp Joe → get call booked
  - Email BBC Good Food Show (booking deadline: June)
  - Email Blenheim Palace events team (festival: May 2026 — URGENT)
  - Verify Pub in the Park status via Instagram

APRIL:
  - Email Taste of London (Regent's Park, June)
  - Email Henley Royal Regatta (June-July)
  - Email Royal Ascot hospitality (June)
  - Email Cartier Queen's Cup Polo (June)
  - Email The Big Feastival (August Bank Holiday — book early)
  - Email Great British Food Festival circuit organiser (one email, 10+ events)
  - Extend dryhire_scraper.py to 8 new counties
  - Run Bridebook scraper (new)
  - Run Bark.com scraper (new)

MAY:
  - Email Wilderness Festival (Oxfordshire, August)
  - Email Henley Festival (Oxfordshire, July)
  - Email Glyndebourne (East Sussex, May-Aug — urgent)
  - Email CLA Game Fair (Warwickshire, July)
  - Email Glorious Goodwood (West Sussex, July)
  - Email Luna Cinema partnership (circuit deal)
  - Instagram scraping of competitor clients
  - Begin wedding planner outreach campaign

JUNE:
  - Email Cowdray Gold Cup Polo (Jun-Jul)
  - Email Meatopia (September — pitch in June)
  - Email Royal Berkshire Show (September)
  - Email Waddesdon Manor (Christmas Fair — book 6+ months out)
  - Tagvenue/Venuescanner corporate scrape
  - Mid-year pipeline review: 1,000 venues target check
```

---

## PIPELINE METRICS TARGETS

| Month | Venues in Pipeline | With Email | Festival Bookings Pitched | Supplier Partnerships |
|-------|-------------------|------------|--------------------------|----------------------|
| Mar 2026 (now) | 502 | 45 (9%) | 3 (orphaned) | 0 |
| Apr 2026 | 650 | 120 (18%) | 15 | 1-2 |
| May 2026 | 800 | 200 (25%) | 25 | 2-3 |
| Jun 2026 | 1,000 | 300 (30%) | 35 | 3-5 |

**Revenue projection from festivals alone (Summer 2026):**
- 3 festival bookings at average £10,000 = £30,000
- 5 festival bookings = £50,000
- This makes the entire system self-funding within Month 1 of Joe's first paid event.

---

## WHAT'S NEEDED TO EXECUTE

1. **SerpAPI key** — unlocks Google Maps enrichment at scale (242 venues pending). Cost: ~£50/mo.
2. **Running contact_enricher.py** on the 96 new county venues (no API needed — website scraping).
3. **Joe on a call** — so he can approve the first outreach batch and greenlight the Blenheim/BBC approach.
4. **Extending hht_dryhire_scraper.py** to new county URL paths on Guides for Brides.
5. **Building hht_bark_scraper.py** — straightforward extension of existing scraping patterns.

---

*Generated by Agent 1 (HHT Venue Scraper) | 2026-03-20*
*Cross-referenced: joe_alert_2026-03-20.md, expansion/festival_events.json, expansion/new_counties.json, FIRST_30_DAYS.md*
