# HHT Launch Checklist

Everything needed before Joe can start using the system daily.

## Phase 1: Data Foundation (CURRENT)
- [x] 392 venues classified (DRY_HIRE / EXTERNAL_OK / IN_HOUSE_ONLY)
- [x] Enrichment pipeline built and tested (hht_enricher.py)
- [x] 85+ venues enriched with contact data (45 with email, 45 with phone)
- [x] Priority scorer: 0-100 scoring with tier assignment
- [x] 7 outreach email templates (wedding, corporate, festival, pub_bar, follow-ups, orphaned client)
- [x] Database schema ready (PostgreSQL for Supabase)
- [x] SQLite database populated (361 venues, scored and tiered)
- [x] FastAPI backend working (venues, outreach, stats, dashboard endpoints)
- [x] CSV export for manual Supabase import
- [ ] **Fix Google search rate limiting** — enricher getting blocked after ~30 requests. Options: add SerpAPI key, use Bing, add longer delays, use proxy rotation
- [ ] **Re-run enrichment** with working search — 311 venues still need contact data
- [ ] **Manual enrichment for top 37 CALL_NOW venues** — these are highest priority, hand-verify emails if scraping fails

## Phase 2: Data Quality
- [ ] Verify all emails with MX record check (reduce bounce rate)
- [ ] Deduplicate across all data sources (venue_classifications, enriched, CSVs)
- [ ] Fill in contact_name for venues where possible (LinkedIn, venue website "team" pages)
- [ ] Add wedding planner data (64 from wedding-planners.csv need enrichment)
- [ ] Cross-reference competitor client lists for proven buyers

## Phase 3: Supabase Backend
- [ ] Create Supabase project
- [ ] Run schema.sql to create tables
- [ ] Import venues via CSV or import_venues.sql
- [ ] Set up Supabase auth (email/password for Joe)
- [ ] Configure RLS policies
- [ ] Update API to use Supabase client instead of SQLite
- [ ] Set up Supabase Edge Functions for scheduled tasks

## Phase 4: Outreach System
- [ ] Connect email sending (gmail_send.py or Supabase Edge Functions)
- [ ] Build template selector (auto-picks template based on venue type)
- [ ] Set up follow-up scheduling (Day 3, Day 7 automatic reminders)
- [ ] Track opens if possible (pixel tracking or use Instantly/Lemlist)
- [ ] WhatsApp integration for direct outreach
- [ ] Phone call logging (manual entry after calls)

## Phase 5: Dashboard Integration
- [ ] Connect live dashboard to Supabase (replace static data)
- [ ] Real-time pipeline metrics (contacted, replied, booked)
- [ ] Daily email/push notification to Joe: "10 venues to call, 3 follow-ups due"
- [ ] Mobile-responsive for on-the-go use
- [ ] Custom domain (not GitHub Pages URL)

## Phase 6: Automation
- [ ] Weekly scraper cron job (new venues from Hitched, Bridebook, Google Maps)
- [ ] Auto-enrichment pipeline for new leads
- [ ] Auto-scoring and tier assignment
- [ ] Deal rot alerts (14 days no activity = red flag)
- [ ] Monthly performance report generation

## Phase 7: Growth Features
- [ ] AI Assistant backend (GPT/Claude for venue research on demand)
- [ ] Competitor monitoring (track competitor IG followers for new leads)
- [ ] Seasonal campaign triggers (spring = wedding season push)
- [ ] Revenue forecasting based on pipeline data
- [ ] Integration with accounting (Xero/QuickBooks)

---

## Critical Metrics Joe Should See Daily
1. **New leads found** this week (from automated scraping)
2. **Outreach sent** today / this week
3. **Reply rate** (target: 8-12%, industry avg: 4-5%)
4. **Follow-ups due** today
5. **Pipeline value** (total GBP of all active enquiries/quotes)
6. **Bookings confirmed** this month
7. **Revenue booked** vs target
8. **Top 10 venues to call** (ranked by score)

## Realistic Response Rate Expectations
Based on B2B cold outreach benchmarks (2025-2026):
- **Average cold email response rate:** 4-5%
- **Top-quartile campaigns:** 15-25% (with strong targeting + follow-ups)
- **Wedding venue niche (estimated):** 8-12% (higher than average because venues actively need bar services)
- **Key factors:** Personalisation (+50% lift), follow-up sequence (+3x responses), Wednesday send day (+15%)
- **Expected for HHT:** With 45 emails, expect 4-5 replies from first batch. With follow-up sequence, could reach 8-10 replies.
- **Conversion to booking:** 20-30% of replies typically convert (so 2-3 bookings from first 45)
- **Average booking value:** GBP 2,000-5,000 = GBP 4,000-15,000 potential from first batch

## Email Quality Issue (R1 Finding)
Current email breakdown from 45 enriched emails:
- **High-value (events@/weddings@):** 9 emails (20%) — best conversion potential
- **Generic (info@/enquiries@/hello@):** 31 emails (69%) — lower conversion
- **Other specific:** 5 emails (11%)

**Action:** For the 31 generic emails, try to find events-specific contacts via LinkedIn or venue "team" pages. Generic info@ emails often go to admin who may not forward to events team.

## Template Quality Assessment (R2 Finding)
Templates are strong:
- Clear CTA in every template (call or meeting request)
- Value proposition is specific (not generic "we do cocktails")
- Social proof implicit (professional tone, website link)
- Follow-up #2 adds value (free cocktail menu) — excellent tactic
- Orphaned client template is well-positioned

**Improvements to consider:**
- Add specific numbers: "We've served at 200+ events" or "Our average couple rating is 4.9/5"
- Shorten initial email to 100-125 words (current ~200+ words, data shows shorter converts better)
- Add a P.S. line with a conversation starter: "P.S. Your barn looks incredible for sunset cocktails"
- Test subject line variants (current ones are functional but not curiosity-driven)
