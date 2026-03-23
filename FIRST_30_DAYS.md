# HHT Lead-to-Booking System — First 30 Days Playbook

**For:** Joe Stokoe / Heads, Hearts & Tails
**Prepared:** 20 March 2026
**Context:** This is the exact execution plan for month 1 after activating the outreach system.

---

## The Numbers That Matter

- **156 venues** in the database, **83 with email addresses**
- **39 high-priority targets** (CALL_NOW + HIGH_PRIORITY tier)
- **87% are wedding venues** (barns, estates, castles, halls) — this is your primary market
- **Peak wedding season:** May-September. Suppliers typically booked 10-12 months out.
- **For summer 2026:** We're in the window — couples booking now are filling last slots. Some will have gaps where suppliers dropped out. Urgency is real, not manufactured.
- **For 2027 season:** This is the golden window. Couples getting engaged Dec-Feb book venues Jan-Apr 2026. Their supplier search starts immediately after.

### Economic Model (R4)

| Metric | Value |
|---|---|
| Emails to send (Month 1) | 45-50 |
| Expected response rate | 8-12% (wedding niche, personalised) |
| Expected responses | 4-6 |
| Conversion to meeting | 50% |
| Meetings | 2-3 |
| Conversion to supplier listing | 60% |
| New venue partnerships (Month 1) | 1-2 |
| Avg bookings per venue partner per year | 3-5 |
| Avg revenue per booking | GBP 3,500 |
| **Annual revenue from Month 1 leads** | **GBP 10,500-35,000** |
| **Cost of system (monthly)** | **GBP 200** |
| **Annual cost** | **GBP 2,400** |
| **ROI** | **4.4x-14.6x** |

If Joe books just 2 events/month from these leads at GBP 3,500 avg = **GBP 84,000/year** in new revenue. Against GBP 2,400/year system cost = **35x ROI**.

---

## Week 1: Foundation (Days 1-7)

### Day 1: Review & Personalise
- [ ] Review top 10 CALL_NOW venues in the scored list
- [ ] For each: check their website, Instagram, recent events
- [ ] Add any personal notes (e.g., "just hosted a 300-guest wedding", "new barn conversion")
- [ ] These personal details get woven into the opening line of each email

### Day 2-3: First Batch (8 emails)
- [ ] Run `python3 outreach_manager.py today` to get the day's batch
- [ ] Send 8 emails to highest-scored venues
- [ ] System auto-assigns A/B subject line variants
- [ ] **Send between 10-11am or 1-2pm** (peak open rate windows)
- [ ] **Send Monday-Wednesday only** (best engagement days)

### Day 4-5: Follow-Up #1
- [ ] Run `python3 outreach_manager.py followup` to see who's due
- [ ] Day 3 follow-ups go out automatically — gentle nudge, under 60 words
- [ ] Send second batch of 8 new emails

### Day 6-7: Second Follow-Up + New Batch
- [ ] Day 7 follow-ups go out — value-add (sample cocktail menu offer)
- [ ] Send third batch of 8 new emails
- [ ] **Week 1 total: 24 initial emails + follow-ups**

### Week 1 Targets
- 24 initial emails sent
- 16 follow-up emails sent
- 2-3 responses expected
- 1 meeting booked

---

## Week 2: Expand & Refine (Days 8-14)

### Day 8-10: Next Batch + Orphaned Clients
- [ ] Send 8 more emails (HIGH_PRIORITY tier)
- [ ] **Priority: Contact orphaned Cocktail Service clients**
  - BBC Good Food Show (if still operating)
  - Blenheim Palace
  - Any others identified
- [ ] These get the `orphaned_client` template — they already buy this service

### Day 11-12: Phone Follow-Ups
- [ ] Any venue that opened your email but didn't reply: CALL THEM
- [ ] Script: "Hi, I'm Joe from Heads Hearts & Tails — I sent you an email earlier this week about cocktail bar services. Just wanted to put a voice to the email."
- [ ] Phone + email combo = 287% better results than email alone
- [ ] Focus on venues with phone numbers in the database (50+ have them)

### Day 13-14: Review A/B Results
- [ ] Run `python3 outreach/ab_testing.py status` to check early variant performance
- [ ] Note which subject lines are getting opens
- [ ] Adjust if one variant is clearly outperforming

### Week 2 Targets
- 16 more initial emails (40 total)
- All Week 1 follow-ups completed
- 3-4 total responses
- 1-2 meetings held
- Begin phone outreach to interested-but-silent venues

---

## Week 3: Nurture & Convert (Days 15-21)

### Day 15-17: Meetings & Proposals
- [ ] Hold venue meetings (in person preferred — bring sample cocktails)
- [ ] At each meeting, bring:
  - Printed seasonal cocktail menu (designed for their venue type)
  - Photo portfolio of previous bar setups
  - One-page partnership proposal (what HHT offers, pricing, logistics)
  - Business cards
- [ ] Ask to be added to their **recommended suppliers list** — this is the goal

### Day 18-19: Continue Outreach
- [ ] Send remaining emails to STANDARD tier venues
- [ ] Begin outreach to corporate/event spaces (template: corporate)
- [ ] Target: 8-10 more emails

### Day 20-21: Social Proof
- [ ] Post about venue visits on HHT Instagram (tag the venue)
- [ ] Share a "behind the scenes" at the Camden kitchen
- [ ] Connect with venue event managers on LinkedIn
- [ ] Comment on venue posts — genuine engagement, not spam

### Week 3 Targets
- 50+ total emails sent
- 1-2 venue partnerships secured (on recommended suppliers list)
- Active social media engagement with target venues

---

## Week 4: Systematise & Scale (Days 22-30)

### Day 22-24: Build the Machine
- [ ] Review overall stats: emails sent, response rate, meetings, conversions
- [ ] Run A/B test analysis — are we approaching 20 sends per variant?
- [ ] Create a repeatable weekly rhythm:
  - Monday: Send 8 new emails
  - Wednesday: Follow-up batch
  - Friday: Review responses, book meetings for next week

### Day 25-27: Wedding Planner Outreach
- [ ] Pivot some outreach to **wedding planners** (not just venues)
- [ ] These are multipliers — one planner relationship = 10-20 bookings/year
- [ ] Use a modified wedding template: emphasise reliability, premium quality, ease of working with HHT
- [ ] Target: 10 wedding planner emails

### Day 28-30: Month 1 Review
- [ ] Full pipeline review with outreach_manager.py status
- [ ] Calculate: emails sent, responses, meetings, partnerships, bookings
- [ ] Identify what's working (which template, which venue type, which geography)
- [ ] Set Month 2 targets
- [ ] Begin Month 2 nurture sequence for non-responders (seasonal angle)

### Week 4 Targets
- System running on weekly cadence
- 2-3 venue partnerships total
- Wedding planner outreach started
- Month 2 plan defined

---

## Key Principles

1. **Send 8 emails per day MAX.** Small batches = better deliverability + time to personalise each one.
2. **Personalise the opening line.** Research each venue for 2 minutes before sending. Mention something specific.
3. **Monday-Wednesday only.** Best engagement days. Save Thursday-Friday for meetings and follow-ups.
4. **10am-11am or 1pm-2pm.** Peak open windows.
5. **Every follow-up adds value.** Never just "checking in" — offer a menu, share a case study, provide an insight.
6. **Phone beats email.** If they opened but didn't reply, call. If they have no email, call.
7. **Get on the suppliers list.** This is the conversion event. Once you're on the list, bookings come to you.

---

## The Competitive Edge

Per the competitor analysis, Joe has weapons no competitor can match:

| What Joe Has | What Competitors Don't |
|---|---|
| Camden development kitchen | Generic recipe cards |
| 25-year CV (Milk & Honey, Trailer Happiness) | Event logistics background |
| Spirit brand relationships (Bombay Sapphire, Belvedere, Woodford Reserve) | No brand connections |
| Bespoke cocktail development per event | Pick 3 from a list of 20 |
| Brand activation capability | Wedding-only operations |
| Direct founder relationship | Account managers and middlemen |

**The Cocktail Service dissolved April 2025.** Their orphaned clients are looking for a replacement. Joe is the natural successor — same calibre of service, without the corporate overhead. This is a time-limited opportunity.

---

## Month 2-3 Nurture (Automated)

For venues that don't respond in Month 1, the system automatically queues:

- **Month 2 (Day 37):** Seasonal angle — "we're booking summer slots, just opened partnerships in your area" or a case study from a similar venue
- **Month 3 (Day 67):** Final attempt — "closing our summer books, last check-in, reply 'later' if you want to revisit in autumn"

Each touch adds genuine value. No "just following up" emails. After Month 3, non-responders move to annual re-contact (seasonal, not pushy).

---

## Daily Commands

```bash
# See today's outreach tasks
python3 outreach/outreach_manager.py today

# Check pipeline status
python3 outreach/outreach_manager.py status

# Send an email to a specific venue
python3 outreach/outreach_manager.py send "Merriscourt"

# Check follow-ups due
python3 outreach/outreach_manager.py followup

# View recent history
python3 outreach/outreach_manager.py history

# Check A/B test results
python3 outreach/ab_testing.py status

# Validate email template word counts
python3 outreach/email_templates.py validate
```

---

*Generated 20 March 2026 | Ralph Loop Agent*
