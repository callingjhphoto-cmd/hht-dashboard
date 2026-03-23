# HHT Venue Scraper — Training Report 2026-03-20

## 1. Expansion County Coverage Audit

### Summary Table

| County | Venues | DRY_HIRE | EXTERNAL_OK | UNKNOWN | % DRY_HIRE | Status |
|--------|--------|----------|-------------|---------|------------|--------|
| Cambridgeshire | 12 | 10 | 2 | 0 | 83% | OK |
| Norfolk | 11 | 8 | 2 | 0 | 73% | OK (1 LOW priority) |
| Suffolk | 11 | 8 | 3 | 0 | 73% | OK |
| Somerset | 10 | 7 | 3 | 0 | 70% | OK |
| Dorset | 10 | 8 | 1 | 0 | 80% | OK (1 EXTERNAL_OK) |
| Devon | 10 | 7 | 2 | 0 | 70% | OK (1 LOW priority) |
| Warwickshire | 10 | 7 | 3 | 0 | 70% | OK |
| Worcestershire | **0** | 0 | 0 | 0 | N/A | **MISSING FROM FILE** |
| Kent | 11 | 6 | 4 | 0 | 55% | OK (lowest DRY_HIRE %) |
| **TOTAL** | **85** | **61** | **20** | **0** | **72%** | — |

**Note:** The metadata in `new_counties.json` says `total_venues: 96` and `counties_added: 8` but actual count is 85 venues across 8 counties. The 96 figure may include planned Worcestershire venues that were never added.

### Flags

- **NEEDS_MORE_SCRAPING: Worcestershire** — Zero venues. The county is listed in TEAM.md's expansion geography (line 61) and has postcode prefixes assigned (WR) but is completely absent from `new_counties.json`. This is the most critical gap.
- **Kent** has the lowest DRY_HIRE percentage (55%) — 4 of 11 venues are EXTERNAL_OK (Leeds Castle, Penshurst Place, Cooling Castle Barn, Port Lympne). Still acceptable but could benefit from more confirmed dry-hire leads.
- **Norfolk/Suffolk postcode overlap**: Both counties list "IP" as a postcode prefix. The Granary Estates is listed under Norfolk but described as "Woodbridge, Suffolk/Norfolk border" — potential geo-classification issue.
- All counties except Worcestershire have 10+ venues, so no other counties fall below the 5-venue threshold.

### Classification Quality
- Zero UNKNOWN classifications across all expansion venues — good data quality
- Every venue has a priority assigned (HIGH/MEDIUM/LOW)
- 4 venues have no website URL (The Manor Barn, Mill Farm, The Cider Barn at Cheddar, Tithe Barn Hinton St Mary) — these need manual enrichment

---

## 2. New Venue Directories & Sources

### From competitor_landscape.md — Venue Names in Competitor Portfolios

These are venues/clients mentioned in competitor profiles that could be scraped as leads (checking if they need external bar services):

**Directories identified (line 57, 447-458):**
- Add to Event (addtoevent.co.uk) — Major UK supplier directory, NOT currently scraped
- Poptop (poptop.uk.com) — Instant pricing/booking, NOT currently scraped
- Togather (togather.com) — Corporate event booking, NOT currently scraped
- Alive Network (alivenetwork.com) — Entertainment/bar hire, NOT currently scraped
- Bridebook (bridebook.com) — Wedding-specific, referenced in lead_scraper_v2.py but unclear if expansion counties are covered
- DesignMyNight (designmynight.com) — Events discovery, NOT currently scraped
- Hire a Bartender (hireabartender.co) — Bartender marketplace, NOT currently scraped

**Industry Bodies (potential venue member lists):**
- HAE/EHA — 3,500+ member businesses
- HBAA — quality assurance mark holders

**Key insight:** The scraper currently only uses Guides for Brides as a directory source. Adding even one more directory (e.g., Bridebook or Hitched wedding venue pages) for the 9 expansion counties would significantly increase coverage.

### From expansion_targets.md — Gaps vs new_counties.json

expansion_targets.md covers Oxfordshire, Cotswolds, and Home Counties (25 venues) — these are the ORIGINAL target geography, not the expansion counties. No overlap or gap with new_counties.json expected.

However, expansion_targets.md mentions regional competitors operating in areas that overlap with expansion counties:
- **Sip 'n' Swig** — Stratford-upon-Avon (Warwickshire) — their venue clients could be scraped
- **The Watering Hole Event Bars** — Cotswolds, covers Worcester/Midlands — their venue partners may include Worcestershire venues
- **Melt Bars** — Chippenham/Wiltshire, covers Somerset/Dorset border

### From lead_gen_ux_research.md — Directory Sources

The UX research document references several lead generation platforms but focuses on CRM tools rather than venue directories. The most relevant finding: Clay.com's waterfall enrichment concept (checking 150+ data providers) should be applied to expansion county venue discovery, not just contact enrichment.

**Additional directories identified from cross-referencing all files:**
1. Hitched.co.uk — wedding venue listings by county (already in lead_scraper_v2.py but needs expansion county URLs)
2. Coco Wedding Venues — referenced in new_counties.json metadata as a source
3. Tagvenue — referenced in new_counties.json metadata as a source
4. Wedding venue websites that list "preferred suppliers" — scraping these lists in reverse finds dry-hire venues

---

## 3. Scraper Configuration Gaps

### Current State of `hht_dryhire_scraper.py`

The scraper's `ALL_COUNTY_URLS` list (lines 24-33) contains only the original 8 counties:
```
Oxfordshire, Berkshire, Buckinghamshire, Gloucestershire,
Hampshire, Surrey, Hertfordshire, Wiltshire
```

**NONE of the 9 expansion counties are configured.**

### Changes Needed (DO NOT MODIFY — plan only)

Add the following entries to `ALL_COUNTY_URLS` (lines 24-33):

```python
# Expansion counties (added 2026-03-20)
("Cambridgeshire", "https://guidesforbrides.co.uk/dry-hire-venues/cambridgeshire"),
("Norfolk", "https://guidesforbrides.co.uk/dry-hire-venues/norfolk"),
("Suffolk", "https://guidesforbrides.co.uk/dry-hire-venues/suffolk"),
("Somerset", "https://guidesforbrides.co.uk/dry-hire-venues/somerset"),
("Dorset", "https://guidesforbrides.co.uk/dry-hire-venues/dorset"),
("Devon", "https://guidesforbrides.co.uk/dry-hire-venues/devon"),
("Warwickshire", "https://guidesforbrides.co.uk/dry-hire-venues/warwickshire"),
("Worcestershire", "https://guidesforbrides.co.uk/dry-hire-venues/worcestershire"),
("Kent", "https://guidesforbrides.co.uk/dry-hire-venues/kent"),
```

**IMPORTANT:** Before adding these URLs, verify that `guidesforbrides.co.uk/dry-hire-venues/{county}` pages actually exist for each county. The scraper handles 404s gracefully (returns empty list) but confirming avoids wasted cycles.

### Additional Configuration Changes Needed

1. **Phase 4 `target_counties` list** (line 485-488): Currently only includes the original 8 + "cotswolds". Must add all 9 expansion counties:
   ```python
   target_counties = [
       "oxfordshire", "berkshire", "buckinghamshire", "gloucestershire",
       "hampshire", "surrey", "hertfordshire", "wiltshire", "cotswolds",
       # Expansion counties
       "cambridgeshire", "norfolk", "suffolk", "somerset", "dorset",
       "devon", "warwickshire", "worcestershire", "kent",
   ]
   ```

2. **Phase 4 `other_counties` list** (lines 517-521): Remove expansion counties from this list — they are no longer "other" counties. Currently includes devon, cornwall, somerset, dorset, norfolk, suffolk, kent, warwickshire. After expansion, only cornwall, essex, london, yorkshire, lancashire, nottinghamshire, leicestershire, northamptonshire should remain as "other" for geo-mismatch detection.

3. **Dedup check**: After adding expansion counties, the scraper will produce leads that may already exist in `new_counties.json`. The dedup phase should cross-reference against `~/Documents/Claude/projects/hht/expansion/new_counties.json` to avoid re-adding the 85 manually researched venues.

### Postcode Prefixes (for reference)

From TEAM.md line 62, the expansion postcode prefixes are already documented:
- CB, PE (Cambridgeshire)
- NR, IP (Norfolk) — note IP overlaps with Suffolk
- IP, CO, CB (Suffolk) — note CB overlaps with Cambridgeshire
- BA, TA, BS (Somerset)
- DT, BH, SP (Dorset)
- EX, TQ, PL (Devon)
- CV, B (Warwickshire)
- WR (Worcestershire — from TEAM.md, not in new_counties.json)
- CT, ME, TN, DA, BR (Kent)

---

## 4. Summary of Findings

### Critical Issues
1. **Worcestershire completely missing** from new_counties.json — 0 venues for an expansion county
2. **Scraper not configured** for any of the 9 expansion counties — no Guides for Brides URLs added
3. **Phase 4 validation lists** need updating to recognize expansion counties as valid targets

### Medium Issues
4. Norfolk/Suffolk postcode prefix overlap (IP) could cause mis-classification
5. 4 venues lack website URLs — need manual enrichment
6. new_counties.json metadata claims 96 venues but only 85 exist
7. Kent has lowest DRY_HIRE ratio (55%) — consider additional dry-hire-focused scraping

### Opportunities
8. 6 additional venue directories identified but not currently scraped
9. Competitor portfolios in expansion counties could yield venue leads
10. Reverse-scraping "preferred supplier" lists from venues finds more dry-hire targets
