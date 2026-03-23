# HHT Lead Generation Platform — Roadmap
**Last updated:** 19 March 2026
**Owner:** James Huertas
**Client:** Joe Stokoe / Heads, Hearts & Tails

---

## Current State (March 2026)

### What Exists
- Live dashboard on GitHub Pages (https://callingjhphoto-cmd.github.io/hht-dashboard/) — 4 tabs, Chart.js, dark theme
- Operations platform on GitHub Pages (https://callingjhphoto-cmd.github.io/hht-operations-platform/) — 6 modules, 3,400 lines React
- 392 venue leads across 27 UK counties (venueData.js)
- 112 venues verified, 308 tagged as qualified (dry hire / external OK)
- 58 competitors profiled with pricing, services, weaknesses
- contact_enricher.py — scrapes venue websites for email/phone/social
- lead_scraper_v2.py — scrapes Hitched, Bridebook, Google Maps, Companies House
- Enriched leads: 462 unique venues after deduplication
- Cocktail Service orphaned client strategy (3 targets, £24K expected value)
- 25 expansion targets across Oxfordshire, Cotswolds, Home Counties

### What's Missing
- Most venue email/phone fields still empty
- No automated weekly scraping (manual only)
- No outreach integration (no send-from-dashboard)
- No backend (localStorage only)
- No Joe buy-in yet (message drafted, not sent)

---

## Phase 1: Pilot Launch (Weeks 1-4) — March/April 2026
**Goal:** Get Joe using it. Prove value. Land first orphaned client.

### Week 1 (19-25 March)
- [x] Complete Ralph Loop research (market, lead gen, Cocktail Service, pricing, outreach)
- [x] Write WhatsApp pitch message for Joe
- [x] Update roadmap
- [ ] James sends WhatsApp to Joe
- [ ] Joe reviews dashboard
- [ ] Schedule 15-min demo call

### Week 2 (26 March - 1 April)
- [ ] Demo call with Joe — walk through dashboard, venue map, competitor intel
- [ ] Get Joe's feedback on lead quality and relevance
- [ ] Run contact_enricher.py on top 50 target venues (fill emails + phones)
- [ ] Joe calls Blenheim Palace (01993 813874 / sales@blenheimpalace.com)
- [ ] Joe emails BBC Good Food Show (info@goodfoodshow.com)

### Week 3 (2-8 April)
- [ ] Deliver first batch of 20 enriched, scored leads to Joe via email/WhatsApp
- [ ] Joe submits Blenheim enquiry form with HHT credentials
- [ ] Follow up on all orphaned client outreach
- [ ] Begin outreach to top 10 Oxfordshire venues using email templates

### Week 4 (9-15 April)
- [ ] Review pilot month — how many leads delivered? How many Joe contacted? Any responses?
- [ ] If positive: propose £200/mo retainer starting May
- [ ] If feedback needed: iterate on lead quality, scoring, or format
- [ ] Run second batch of enrichment on next 50 venues

---

## Phase 2: Paid Service (Months 2-3) — May/June 2026
**Goal:** Stable retainer. Automated weekly leads. First booking from platform leads.

### Data & Enrichment
- [ ] Full enrichment run on all 392 venues (target: 80%+ email coverage)
- [ ] Add 100+ new venues from expansion targets (Oxon, Cotswolds, Home Counties)
- [ ] Implement SerpAPI Google Maps scraper for real-time new venue discovery
- [ ] Build deduplication pipeline (match on name + postcode)
- [ ] Add wedding planner leads (64 existing, expand to 150+)

### Automation
- [ ] Set up weekly cron for lead_scraper_v2.py (run every Monday)
- [ ] Auto-email Joe with "10 New Leads This Week" summary
- [ ] Implement ntfy push notification for new high-scoring leads (score 80+)
- [ ] Build enrichment waterfall: website scrape → Hunter API → manual fallback

### Dashboard Improvements
- [ ] Add "New This Week" badge on fresh leads
- [ ] Lead status tracking (New → Contacted → Responded → Meeting → Booked)
- [ ] Export to CSV button for Joe's own records
- [ ] Mobile responsiveness (Joe will check on phone)

### Outreach Support
- [ ] Deliver email templates (venue coordinators, corporate bookers, festival organisers)
- [ ] Build outreach calendar with monthly focus areas
- [ ] Prep pitch decks for Blenheim, BBC Good Food Show, Pub in the Park

---

## Phase 3: Scale (Months 4-6) — July-September 2026
**Goal:** 500+ leads in database. 3+ bookings attributable to platform. Price increase.

### Platform
- [ ] Migrate to Supabase backend (replace localStorage)
- [ ] User authentication (Joe + Emily Blacklock login)
- [ ] Real CRM pipeline: Lead → Qualified → Proposal → Won/Lost
- [ ] Deal tracking: link leads to bookings and revenue
- [ ] Custom domain (e.g., leads.headsheartsandtails.com)

### Intelligence
- [ ] Competitor monitoring — weekly check for new competitors, pricing changes
- [ ] Seasonal insights — which venues are booking for autumn/Christmas 2026
- [ ] Win/loss analysis — why did Joe win or lose each deal?
- [ ] Venue classification confidence scoring (auto-detect dry hire from website text)

### Revenue
- [ ] Increase retainer to £350/mo (justified by proven bookings)
- [ ] Add optional pay-per-lead tier for overflow (£15 per lead above 20/month)
- [ ] Track ROI: total leads delivered vs bookings closed vs revenue generated

---

## Phase 4: Full Product (Months 7-12) — October 2026 - March 2027
**Goal:** Self-sustaining lead gen engine. Minimal manual intervention. £500/mo retainer.

### Advanced Features
- [ ] AI-powered lead scoring (train on Joe's win/loss data)
- [ ] Automated outreach sequences (send email 1, wait 4 days, send email 2)
- [ ] WhatsApp Business API integration (send directly from dashboard)
- [ ] Calendar integration (propose meeting times from dashboard)
- [ ] Competitor alert system (new competitor detected, competitor lost a review)

### Data Expansion
- [ ] 750+ UK venues in database
- [ ] 200+ wedding planners
- [ ] 100+ corporate event bookers
- [ ] Regional coverage: expand beyond South East to Midlands, North West, Scotland

### Business Model Evolution
- [ ] £500/mo retainer (comprehensive service)
- [ ] Or hybrid: £300/mo base + 5% revenue share on first booking from each lead
- [ ] Explore productising for other service businesses (photographers, florists, caterers)

---

## Long-Term Vision (Year 2+)

### For Joe
- HHT becomes the dominant cocktail bar agency outside London
- Blenheim Palace as anchor client opens all Oxfordshire doors
- BBC Good Food Show partnership delivers brand visibility + revenue
- Dashboard becomes Joe's daily tool — he checks it like email

### For James
- HHT retainer: £500/mo = £6K/year recurring
- Template for "lead gen as a service" offering to other niche service businesses
- Portfolio piece: "Built a lead gen platform that delivered £X in bookings for a cocktail agency"
- Potential to license the scraping/enrichment stack

---

## Key Metrics to Track

| Metric | Target (Month 1) | Target (Month 6) | Target (Month 12) |
|--------|------------------|-------------------|---------------------|
| Venues in database | 392 | 550 | 750 |
| Email coverage | 30% | 80% | 90% |
| Leads delivered to Joe/week | 10 | 20 | 20 |
| Joe's contact rate | 50% | 70% | 80% |
| Bookings from platform leads | 0 | 3 | 10 |
| Monthly retainer | £0 (pilot) | £350 | £500 |
| ROI for Joe | N/A | 10x | 20x |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Joe doesn't engage / too busy | Medium | High | Keep pilot frictionless. Send leads via WhatsApp, not just dashboard. Make it zero-effort for him. |
| Lead quality is poor (wrong venue types) | Medium | High | Pre-filter aggressively. Only send dry hire + external OK. Get Joe's feedback on first batch. |
| Venues don't respond to outreach | High | Medium | Multi-channel: email + phone + LinkedIn. Referral leads where possible. Offer tastings. |
| Competition from other lead gen tools | Low | Low | HHT platform is niche-specific. Generic tools (Apollo, Hunter) don't know wedding venue classification. |
| Scraping gets blocked | Medium | Medium | Rotate user agents, respect rate limits, use multiple sources, have manual fallback. |
| Joe can't afford £200/mo | Low | Medium | If cashflow is tight, offer £100/mo or pure pay-per-lead. The goal is the relationship. |
| Blenheim/BBC Good Food already have a new supplier | Medium | Medium | Don't put all eggs in orphaned client basket. The 308 qualified venues are the core value. |

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 19 Mar 2026 | Set pilot price at £0 for 30 days, then £200/mo | Low barrier, proves value before asking for money |
| 19 Mar 2026 | Prioritise Blenheim Palace as #1 orphaned client | Highest probability (40%), Oxfordshire expansion anchor |
| 19 Mar 2026 | Use WhatsApp for Joe pitch (not email) | Joe is mobile-first, WhatsApp is where he communicates |
| 19 Mar 2026 | Pub in the Park status updated: LIVE, owned by Live Nation | Previous intel was wrong (domain was different). Festival confirmed for May 2026. |
