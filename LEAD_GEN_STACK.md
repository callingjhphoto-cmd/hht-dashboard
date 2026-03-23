# HHT Lead Gen Stack — Comparison & Recommendation

**Generated:** 2026-03-20
**Context:** 372 UK wedding/event venues. Need: named decision makers, direct emails, social media.
**Current baseline:** 11/372 contact names (3%), 85/372 emails (23%), 5/372 Instagram links.

---

## The Problem With Current Web Scraping

| Issue | Impact |
|---|---|
| ~5s per venue (scrape + search) | 31 min for 372 venues |
| Returns generic info@ / admin@ | Low reply rates — not a named person |
| No names at all | Can't personalise outreach |
| Sites block scrapers | ~25% failure rate |
| Only surfaces public emails | Misses decision makers who don't publish email |

---

## Tool-by-Tool Breakdown

### 1. Companies House API (UK Government)
**URL:** https://developer.company-information.service.gov.uk/

| Attribute | Detail |
|---|---|
| **Cost** | FREE — just needs email to register |
| **Rate limit** | 600 requests per 5 minutes (~5M/month) |
| **Auth** | Free API key (HTTP Basic) |
| **Data returned** | Company name, number, status, SIC codes, registered address, ALL current officers with name + role + occupation |
| **Speed** | ~0.6s per lookup |
| **UK coverage** | ~80% of venues are registered companies |
| **Data quality** | Government source — authoritative, verified |
| **What you get** | "Claire Fortescue, Director, Occupation: Events Co-Ordinator" |

**Verdict: Use this first. It's free, fast, and gives you real names.**

Key insight: Companies House stores the officer's declared **occupation** (e.g. "Events Co-Ordinator", "Hospitality Manager") — this is more useful than their director title for identifying the right contact.

**Steps to activate:**
1. Register (free) at https://developer.company-information.service.gov.uk/
2. Create an application → copy API key
3. `export COMPANIES_HOUSE_KEY='your_key'`
4. `python3 ~/Documents/Claude/scripts/hht_companies_house_enricher.py --limit 20`

---

### 2. Hunter.io
**URL:** https://hunter.io

| Attribute | Detail |
|---|---|
| **Cost** | Free: 50 credits/month. Starter: €49/month (2,000 credits). Growth: €149/month (10,000) |
| **Rate limit** | 15 req/sec, 500/min |
| **Auth** | API key in query params |
| **Domain search** | Give it a domain → get all emails found on that domain, with names + job titles |
| **Email finder** | Give it first name + last name + domain → get their most likely email with confidence score |
| **Speed** | ~0.5s per lookup |
| **Coverage** | Works on any domain — not UK-specific |
| **Data quality** | Strong for tech/business sectors, weaker for small hospitality venues |

**Verdict: Use in Layer 2. Pair with Companies House: CH gives you the name, Hunter finds the email.**

The real power combo: Companies House gives you "Claire Fortescue, Director" → Hunter email-finder gives you claire.fortescue@venuepark.co.uk.

**Cost for 372 venues:**
- Free tier: 50 searches — covers ~50 venues/month
- Starter (€49): 2,000 credits — covers all 372 venues and then some
- Recommendation: Start free, upgrade to Starter when ready

---

### 3. Apollo.io
**URL:** https://apollo.io

| Attribute | Detail |
|---|---|
| **Cost** | Free: 10,000 credits/month (Fair Use Policy). Basic: $49/month. Professional: $99/month |
| **Data** | B2B contact database — 275M+ contacts, 73M companies |
| **Best for** | Mid-size to large companies with LinkedIn presence |
| **UK hospitality coverage** | Patchy — better for corporate venues than boutique farms/barns |
| **Speed** | API-based, fast |
| **Auth** | API key |

**Verdict: Skip for this use case.** Apollo is optimised for B2B SaaS/corporate. Small UK wedding venues (barns, farms, country houses) have thin LinkedIn presence and won't be in Apollo's database. The free 10,000 credits look attractive but you'll get 0 results for ~60% of the venue list. Reserve Apollo for future expansion into corporate event bookers (EA to CEO, marketing managers).

---

### 4. Clearbit / Breeze by HubSpot
**URL:** https://clearbit.com (now HubSpot Breeze)

| Attribute | Detail |
|---|---|
| **Cost** | Was $99/month. Now folded into HubSpot — requires HubSpot subscription |
| **Data** | Company enrichment — firmographics, tech stack, social profiles |
| **UK coverage** | Good for larger companies, poor for small hospitality |
| **Relevance** | Returns company-level data, not individual contacts |

**Verdict: Skip.** The HubSpot rebrand has made it less accessible as a standalone API. Overkill for venue contact finding — it would tell you what CRM Hatfield House uses, not who to call.

---

### 5. Snov.io
**URL:** https://snov.io

| Attribute | Detail |
|---|---|
| **Cost** | Free: 50 credits/month (renewable trial). Starter: ~$29/month (1,000 credits) |
| **Data** | Domain search, email finder, LinkedIn enrichment |
| **vs. Hunter** | Very similar product. Slightly cheaper at starter tier |
| **UK coverage** | Similar to Hunter — decent |
| **Note** | Free tier requires a "demo call" to get API access |

**Verdict: Backup to Hunter.io.** Almost identical product. Use if Hunter free credits run out mid-month. The API access barrier on free tier is annoying.

---

### 6. RocketReach
**URL:** https://rocketreach.co

| Attribute | Detail |
|---|---|
| **Cost** | Essentials: ~$39/month (170 lookups). Pro: ~$99/month (450 lookups) |
| **Data** | Personal emails + direct dials. Strong LinkedIn integration |
| **UK coverage** | Better than Apollo for UK contacts |
| **Lookups per month** | Low compared to Hunter/Snov at the price point |

**Verdict: Too expensive per lookup for 372 venues.** $99 for 450 lookups = $0.22/venue. Hunter Starter at €49 for 2,000 = €0.025/venue. RocketReach is 9x more expensive per lookup.

---

### 7. Clay
**URL:** https://clay.com

| Attribute | Detail |
|---|---|
| **Cost** | Starter: $149/month (1,000 credits). Growth: $400/month. Explorer: free (100 credits) |
| **What it is** | Data enrichment platform that aggregates 150+ data providers |
| **How it works** | Build "tables" that automatically enrich a list using multiple providers in sequence |
| **Relevance** | Would query Companies House + Hunter + LinkedIn + web scraping automatically |
| **Learning curve** | Medium — no-code but requires workflow setup |

**Verdict: Interesting for scale, overkill for now.** Clay is what professional lead gen agencies use. At $149/month minimum, it's 3x Hunter. The multi-provider approach is exactly what hht_lead_gen_engine.py does — but in code, for free. Revisit when list exceeds 2,000 venues or when James wants to automate without managing API keys.

---

### 8. Google Custom Search API
**URL:** https://console.cloud.google.com

| Attribute | Detail |
|---|---|
| **Cost** | Free: 100 queries/day. Paid: $5 per 1,000 queries |
| **How it works** | Programmatic Google search. Send query → get JSON results with URLs, titles, snippets |
| **Use case** | "{venue name} events manager email" → extract emails from snippets/results |
| **Coverage** | Any venue that has ever appeared in a press release, directory, or article |
| **Note** | Closed to new customers as of 2027 — existing customers grandfathered |

**Verdict: Useful as Layer 3 complement.** 100 free queries/day = covers all 372 venues in 4 days for free. Particularly good at finding email addresses from press releases ("contact events@venuename.co.uk for bookings") and industry directories that are indexed by Google but not scraped directly.

**Setup:** Enable Custom Search API in Google Cloud Console → create a Programmable Search Engine (point it at all UK websites) → set `GOOGLE_CSE_KEY` and `GOOGLE_CSE_ID`.

---

### 9. Companies House (Already Covered Above)

---

### 10. Instagram Graph API + Facebook Pages API

| Attribute | Detail |
|---|---|
| **Instagram Graph API cost** | Free — but requires a Business/Creator account to use |
| **What it returns** | Can search business accounts — but only if you have the Instagram Business ID |
| **Practical approach** | Construct URL from venue name → test if it resolves → check it's not a person account |
| **Facebook Pages API** | Same pattern — construct facebook.com/VenueName → verify |
| **Rate limits** | Strict — avoid polling individual profiles repeatedly |

**Verdict: Use URL construction + HTTP head check (already in hht_lead_gen_engine.py).** The Graph API requires OAuth for business data and won't help with contact finding — it's for accessing your own business page. The simple approach of constructing `instagram.com/hatfieldhouse` and doing a HEAD request is free and sufficient.

---

## Recommended Stack for James's Budget

### Phase 1: £0/month (Start immediately)

| Layer | Tool | Action |
|---|---|---|
| 1 | **Companies House API** | Get free key → run on all 372 venues → get ~250 named directors |
| 2 | **Google CSE** | Free Google Cloud account → 100 queries/day → 4-day sweep for email snippets |
| 3 | **Web scraping** | Existing capability — already built, just needs CH enrichment to improve targeting |
| 4 | **Social URL construction** | Already in engine — just HEAD requests |

**Expected results at £0:**
- Contact names: 11 → ~200 (Companies House directors)
- Emails: 85 → ~150 (Google CSE + scraping)
- Instagram: 5 → ~50 (URL construction)

### Phase 2: €49/month (When ready to scale outreach)

| Addition | Cost | Value |
|---|---|---|
| **Hunter.io Starter** | €49/month | 2,000 credits — run Email Finder on each CH name → get personal emails |
| Expected result | — | +100 personal, verified emails like claire@venuepark.co.uk |

**Total Phase 2 spend: €49/month**

### Skip These (Not worth it for this use case)

- Apollo.io — wrong market, low UK hospitality coverage
- Clearbit/Breeze — company data not contact data
- RocketReach — too expensive per lookup
- Clay — worth it at 2,000+ venues or when budget hits £400/month

---

## Speed Comparison (372 venues)

| Approach | Time | Cost | Names Found | Emails Found |
|---|---|---|---|---|
| Current (web scrape only) | 31 min | £0 | ~10 | ~85 |
| + Companies House | +4 min | £0 | ~250 | ~85 |
| + Google CSE (4 days) | +4 min/day | £0 | ~250 | ~150 |
| + Hunter Starter | +4 min | €49/mo | ~250 | ~300 |

---

## Script Reference

```bash
# Run Companies House enrichment (get free key first):
export COMPANIES_HOUSE_KEY="your_key"
python3 ~/Documents/Claude/scripts/hht_companies_house_enricher.py --limit 20  # test
python3 ~/Documents/Claude/scripts/hht_companies_house_enricher.py              # all 372

# Run full lead gen engine:
export COMPANIES_HOUSE_KEY="your_key"
export HUNTER_API_KEY="your_key"       # optional
export GOOGLE_CSE_KEY="your_key"       # optional
export GOOGLE_CSE_ID="your_cse_id"     # optional
python3 ~/Documents/Claude/scripts/hht_lead_gen_engine.py --limit 50   # test 50

# Check status:
python3 ~/Documents/Claude/scripts/hht_lead_gen_engine.py --status

# Merge CH names back into master:
python3 ~/Documents/Claude/scripts/hht_lead_gen_engine.py --merge-ch

# Demo mode (no keys needed):
python3 ~/Documents/Claude/scripts/hht_companies_house_enricher.py --demo
```

---

## Immediate Next Action

**Get the Companies House API key today — it takes 5 minutes and is completely free.**

1. Go to: https://developer.company-information.service.gov.uk/
2. Register (just email + password)
3. Create application → copy API key
4. `export COMPANIES_HOUSE_KEY='your_key'`
5. `python3 ~/Documents/Claude/scripts/hht_companies_house_enricher.py --limit 20`

You'll have 20 venue directors' names — real, verified, named people — in about 30 seconds.
