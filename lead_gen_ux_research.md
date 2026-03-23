# Lead Generation & CRM UX Research for HHT Dashboard
**Date:** 2026-03-17
**Purpose:** Inform the redesign of HHT's Lead Engine CRM module with best-in-class UX patterns

---

## 1. Tool-by-Tool Analysis

### Tier 1: Best-in-Class UX (Steal From These)

#### Apollo.io — The Gold Standard for Lead Discovery
- **Lead Display:** Filterable table view with customisable columns (name, title, company, industry, location, social links). 65+ search filters including job title, company size, industry, location, tech stack
- **Lead Scoring:** AI-powered scoring that auto-prioritises based on engagement signals, buyer intent, job changes, and CRM activity. Score is visible as a badge on each lead row
- **Pipeline:** Multi-stage deal tracking with real-time enrichment. Intent signals and job change alerts surface timing opportunities
- **Activity Logging:** Automated — emails sent via Apollo auto-log. Manual logging for calls/meetings. Full sequence tracking with A/B test results
- **Lead Details:** Click-to-expand sidebar showing full contact info, company data, engagement history, and social profiles. One-click actions: email, call, add to sequence
- **Mobile:** Responsive web app, mobile-optimised
- **Design Language:** Clean, data-dense but not cluttered. Blue/white palette. Information hierarchy is excellent — key data surfaces without scrolling
- **What Makes It Good:** The "Persona" saved filter feature is brilliant. Save "Wedding Venues, Home Counties, 200+ capacity" as a persona and one-click apply it. Waterfall enrichment means if one data source fails, it tries the next automatically

#### Pipedrive — The King of Kanban Pipeline
- **Lead Display:** Kanban board is the primary view. Deal cards show: title, value, owner, organisation, days since last activity. Cards are colour-coded by activity status (green = active, red = stalled)
- **Lead Scoring:** AI-powered scoring (2025+), predicts deal health and likelihood to close. Visual indicators on cards
- **Pipeline:** Fully customisable stages with drag-and-drop. Multiple pipelines supported. Template pipelines for quick setup. Stage probability weighting for revenue forecasting
- **Activity Logging:** Icon-based quick actions — click call icon, email icon, meeting icon. Activities scheduled from card view. Overdue activities highlighted in red
- **Lead Details:** Click card to open full detail view with timeline of all activities, communication history, associated contacts, files, and notes. Three-panel layout: sidebar properties, centre timeline, right associations
- **Mobile:** Dedicated mobile app, offline capable. Cross-device sync
- **Design Language:** Visual-first. Cards surface 5-7 key fields. Drag-and-drop feels natural. Colour coding for urgency. Minimal chrome, maximum data
- **What Makes It Good:** Deal cards in kanban show just enough info to make decisions without clicking in. The "rotting deals" feature (highlighting stalled opportunities) is exactly what Joe needs — venues that haven't been contacted in X days turn red. You can review 40+ opportunities in under 2 minutes

#### Close.com — Best for Activity-First Selling
- **Lead Display:** Smart Views — dynamic filtered lists based on any criteria combination (status, location, last contact date, custom fields). List view with inline editing
- **Lead Scoring:** Confidence level and deal value visible on every opportunity. Pipeline reports show value + probability
- **Pipeline:** Bird's-eye pipeline view with drill-down to individual opportunities. Drag-and-drop between stages
- **Activity Logging:** Built-in calling (VoIP), email, and SMS from the lead record. Every interaction auto-logged. Call recordings transcribed. One-click "Draft Follow-up" with AI
- **Lead Details:** All communication history (form submissions, calls, emails, SMS, meetings, notes) stored on lead profile. Full context for every rep
- **Mobile:** Responsive, calling works from mobile
- **Design Language:** "No BS" — minimal, fast, zero-distraction interface. Claimed 50% faster setup than competitors
- **What Makes It Good:** The unified inbox ("Unibox") manages all communication channels in one place. Smart Views are the killer feature — create "Venues contacted >7 days ago with no response" and it auto-updates. This is what HHT needs for follow-up discipline

#### folk.app — Best Lightweight CRM Design
- **Lead Display:** Notion-like spreadsheet view OR kanban board. Toggle between views. Minimal, non-distracting colours. Loads in <3 seconds
- **Lead Scoring:** Smart fields auto-fill data (emails, phone numbers) with one click. AI "Magic Fields" extract data from prospect websites
- **Pipeline:** Kanban with drag-and-drop. Bulk-move contacts between stages. Shared pipelines with team roles
- **Activity Logging:** Lightweight — notes, tags, reminders. Syncs with Google Calendar
- **Lead Details:** Click to expand inline or open detail view. Clean card layout
- **Mobile:** Responsive web
- **Design Language:** The most Apple-like CRM on the market. White space, clean typography, minimal UI elements. Premium feel without complexity. Fast. This is the aesthetic HHT should target
- **What Makes It Good:** Proves you don't need complexity to be powerful. The spreadsheet-to-kanban toggle is genius — sometimes you want a list, sometimes you want a board. Import contacts from LinkedIn/Chrome extension in one click

### Tier 2: Specialist Tools (Specific Features to Steal)

#### Clay.com — Data Enrichment UX
- **Key Pattern:** Spreadsheet-like interface for managing leads. Waterfall enrichment checks 150+ data providers sequentially — if provider A can't find an email, it tries B, then C. Achieves 80%+ match rates vs 40-50% single-source
- **Steal This:** The AI Formula Generator — describe what you want in plain English ("find the events manager email for each venue") and it writes the enrichment formula. Also: the visual enrichment pipeline showing which providers were checked and which succeeded
- **Relevance to HHT:** This is how venue contact enrichment should work. Don't just try one source — waterfall through Google, LinkedIn, venue website, Companies House, Instagram

#### Streak CRM — Gmail Integration
- **Key Pattern:** Lives entirely inside Gmail. No separate app. Pipeline appears as a sidebar in your inbox. "Magic columns" auto-fill metrics (last email date, # interactions, last updated by)
- **Steal This:** The concept of CRM-inside-your-existing-tools. For HHT, this means the dashboard should feel like a natural extension of Joe's workflow, not a separate system to maintain. Also: magic columns that auto-calculate "days since last contact" and "total interactions"
- **Relevance to HHT:** Joe's team lives in email. Auto-logging sent emails and showing "last contacted" dates per venue would be transformative

#### Snov.io — Pipeline Customisation
- **Key Pattern:** Up to 20 custom pipelines, up to 200 custom fields per deal card. 7-tier email verification process
- **Steal This:** The custom fields approach. Each venue needs specific fields: capacity, venue type, dry hire status, wedding season dates, approved supplier list status. Snov.io shows how to make these manageable without clutter

#### Instantly.io — High-Volume Outreach UX
- **Key Pattern:** Unibox manages hundreds of inboxes. Mark leads as positive/negative. Campaign-based lead organisation
- **Steal This:** The positive/negative lead marking. Quick binary qualification: "Is this venue worth pursuing? Yes/No" with one click. Also: campaign-based organisation ("Spring Wedding Campaign", "Corporate Q4 Push")

#### Lemlist — Personalised Outreach
- **Key Pattern:** Drag-and-drop sequence builder for multi-channel campaigns. Dynamic personalisation with images, videos, landing pages per lead
- **Steal This:** The visual sequence builder. For HHT: build an outreach sequence like "Day 1: Email intro → Day 3: Follow-up → Day 7: Call → Day 14: Send portfolio"

#### Hunter.io — Email Discovery UX
- **Key Pattern:** Clean, minimal search bar. Enter domain → get all associated emails with names, titles, and sources. Bulk search for multiple domains at once
- **Steal This:** The source attribution. When showing a venue's contact email, show WHERE it was found (venue website, LinkedIn, Companies House). This builds trust in the data

#### Lusha — Intent Scoring
- **Key Pattern:** Each account gets an "intent score" showing likelihood of being interested right now. Based on engagement signals and buying patterns
- **Steal This:** The concept of timing-based scoring. A venue that just posted "Now taking 2027 bookings" on Instagram is hotter than one that hasn't posted in months

#### Leadfeeder — Behavioural Scoring
- **Key Pattern:** Scores visitors based on pages viewed, visit frequency, time on site, and source. 50+ behavioural and firmographic filters. Auto-removes ISP traffic (noise)
- **Steal This:** The saved filter "feeds" concept. Create feeds like "Venues from Oxfordshire that visited our portfolio page" and get real-time alerts

### Tier 3: CRM Giants (Design Patterns Only)

#### HubSpot CRM
- **Lead Scoring:** Most sophisticated scoring engine. Manual rules (Professional) or AI predictive (Enterprise). 2025 update added "explainability" — shows WHY a lead scored high. Transparency in scoring builds trust
- **Pipeline:** Visual pipeline with drag-and-drop. Score thresholds trigger automated actions (score >80 = auto-assign to Joe)
- **Steal This:** Explainable scoring. Don't just show "Score: 85" — show "Dry hire venue (+30), 300+ capacity (+20), posted about cocktails on IG (+15), within 50 miles (+10), wedding venue (+10)"

---

## 2. Design Patterns to Steal for HHT

### A. The Three-View Toggle (from folk.app + Pipedrive)
**Pattern:** Let users switch between three views of the same data:
1. **Kanban Board** — drag-and-drop pipeline stages (primary view for Joe)
2. **Table/List View** — sortable, filterable spreadsheet (for bulk operations)
3. **Map View** — geographic view of venues (HHT already has this — keep it)

**Implementation:** Tab bar at top: `[Board] [List] [Map]` — all showing the same leads, different visualisation

### B. The Smart Deal Card (from Pipedrive + Close)
**Pattern:** Each lead card in kanban shows exactly the right amount of info:
```
+----------------------------------+
| The Barn at Upcote               |
| Cheltenham, Gloucestershire      |
| DRY HIRE  |  Cap: 200  |  Score: 85  |
| Last contact: 3 days ago    [!]  |
| Emily Blacklock assigned         |
+----------------------------------+
```
- Venue name (bold)
- Location
- Tags: DRY_HIRE / EXTERNAL_OK (colour-coded pill)
- Capacity
- Lead score (colour: green >70, amber 40-70, red <40)
- Days since last contact (turns red if stale)
- Assigned team member
- Activity warning icon if overdue

**Maximum 5-7 fields per card.** Click to expand for full detail.

### C. The Slide-Out Detail Panel (from Apollo + HubSpot)
**Pattern:** Click a lead card → right-side panel slides out (not a new page, not a modal). Panel has three sections:
1. **Left column:** Key properties (address, phone, email, website, capacity, venue type, dry hire status, wedding season, social links)
2. **Centre column:** Activity timeline (chronological feed of all interactions)
3. **Action bar at top:** Quick actions — `[Email] [Call] [Note] [Task] [Move Stage]`

**Why slide-out, not modal:** User can still see the pipeline behind the panel. Context is maintained. Click outside to close.

### D. One-Click Activity Logging (from Close + Pipedrive)
**Pattern:** When logging an activity, present a minimal form:
```
[Email] [Call] [Meeting] [Note] [Task]
         ↓ (click Call)
+----------------------------------+
| Log Call                         |
| Date: [Today]  Time: [Now]      |
| Outcome: [Connected ▼]          |
|   - Connected                   |
|   - Left voicemail              |
|   - No answer                   |
|   - Wrong number                |
| Notes: [________________]       |
| Next step: [Follow up in 3 days]|
|            [Save]  [Cancel]     |
+----------------------------------+
```
- Pre-filled date/time (today, now)
- Dropdown outcomes (not free text)
- Optional notes
- "Next step" auto-creates a follow-up task
- One click to save, back to pipeline

### E. The Rotting Deal Alert (from Pipedrive)
**Pattern:** Deals that haven't been touched in X days get visual alerts:
- 3+ days without activity: amber border on card
- 7+ days: red border
- 14+ days: pulsing red icon + appears in "Needs Attention" dashboard widget
- Configurable per stage (New leads can sit longer than Proposal stage leads)

### F. Smart Saved Filters (from Close + Apollo)
**Pattern:** Save filter combinations as named views:
- "Hot Leads This Week" — Score >70, contacted in last 7 days
- "Oxfordshire Dry Hire" — Location = Oxfordshire, Type = DRY_HIRE
- "Stale Proposals" — Stage = Proposal, last contact >14 days
- "Uncontacted New Leads" — Stage = New, activities = 0

Filters appear as tabs above the pipeline. One click to switch context.

### G. Inline Editing (from CRM best practices)
**Pattern:** Double-click any field on a lead card or detail panel to edit it inline. No "edit mode" page. Change the phone number? Click it, type, press Enter. Done.

### H. Bulk Actions (from Apollo + folk)
**Pattern:** Select multiple leads (checkbox on cards) → action bar appears:
- Move to stage
- Assign to team member
- Add tag
- Export to CSV
- Start email sequence

---

## 3. Lead Scoring Model for HHT (Events Company)

### Scoring Criteria (100-point scale)

#### Venue Fit (max 40 points)
| Criteria | Points | Rationale |
|----------|--------|-----------|
| Dry hire / external bar allowed | +15 | This is the #1 qualifier. In-house bar = dead lead |
| Capacity 200+ | +10 | Larger events = higher revenue per booking |
| Capacity 100-199 | +5 | Still viable but smaller margin |
| Wedding venue | +5 | Core market for HHT |
| Corporate event space | +5 | Secondary market, often repeat business |
| Festival/outdoor venue | +5 | Premium pricing opportunity |
| Country house / estate | +5 | High-end clients, big budgets |
| Recently opened (last 2 years) | +5 | New venues actively seeking suppliers |

#### Engagement Signals (max 30 points)
| Criteria | Points | Rationale |
|----------|--------|-----------|
| Responded to outreach | +15 | Active interest |
| Opened email (tracked) | +5 | Awareness |
| Visited HHT website/portfolio | +10 | Research intent |
| Engaged on social media | +5 | Brand awareness |
| Requested info/pricing | +15 | High intent |
| Attended HHT showcase event | +10 | Serious consideration |
| Referred by existing client | +10 | Warm intro, high conversion |

#### Timing & Opportunity (max 20 points)
| Criteria | Points | Rationale |
|----------|--------|-----------|
| Posted "taking bookings" on social | +10 | Active need |
| Wedding season approaching (Mar-Oct) | +5 | Seasonal urgency |
| Currently uses competitor | +5 | Proven buyer of the service |
| Competitor relationship appears weak | +5 | Opportunity to displace |
| No current cocktail bar supplier listed | +5 | Greenfield opportunity |

#### Data Quality (max 10 points)
| Criteria | Points | Rationale |
|----------|--------|-----------|
| Verified email address | +3 | Can be contacted |
| Verified phone number | +3 | Can be called |
| Decision-maker identified | +4 | Right person, not generic inbox |

### Score Tiers
- **80-100: Hot Lead** — Immediate action required. Assign to Joe personally. These convert
- **60-79: Warm Lead** — Active outreach warranted. Follow standard sequence
- **40-59: Cool Lead** — Nurture with periodic check-ins. Not ready yet
- **20-39: Cold Lead** — Park in database. Monitor for signal changes
- **0-19: Dead Lead** — In-house bar, too small, or out of area. Archive

### Score Display
Show as a coloured badge on every lead card:
- Hot: solid green circle with score
- Warm: amber circle
- Cool: light grey circle
- Cold: outline only
- Include tooltip showing score breakdown (HubSpot's "explainability" pattern)

---

## 4. Pipeline Stages for HHT

### Recommended 6-Stage Pipeline

```
[New] → [Contacted] → [Qualified] → [Proposal] → [Booked] → [Completed]
```

#### Stage Definitions

**1. New (colour: light blue)**
- Lead has been identified but no outreach yet
- Auto-populated by scraper imports
- Minimum data: venue name, location, type, dry hire status
- Auto-actions: assign to team member based on location
- SLA: must be contacted within 5 business days

**2. Contacted (colour: amber)**
- First outreach has been made (email, call, or DM)
- Required fields: contact method, date, who reached out
- Sub-statuses: Awaiting Response, Follow-up Scheduled, No Response (x2)
- SLA: if no response after 3 touches over 14 days, flag for review

**3. Qualified (colour: green)**
- Venue has responded positively AND confirmed:
  - They allow external bar services
  - They have events that need cocktail bars
  - There's a decision-maker engaged
  - Budget expectation is realistic
- This is where lead scoring really kicks in
- Required fields: decision-maker name, approximate annual events count, budget indication

**4. Proposal Sent (colour: purple)**
- Formal proposal/quote has been sent
- Required fields: proposal value, proposal date, follow-up date
- Track: which services quoted, number of events quoted for, total value
- SLA: follow up within 3 business days if no response

**5. Booked (colour: dark green)**
- Contract signed / deposit paid
- Required fields: event dates, event type, crew requirements, equipment needs
- This stage triggers: event pipeline entry, team allocation, stock planning
- Revenue confirmed in financial forecasting

**6. Completed (colour: grey)**
- Event(s) delivered
- Required fields: feedback received, satisfaction score, repeat booking likelihood
- Post-event: request testimonial, ask for referral, schedule "check in for next season"
- Feeds back into scoring: completed clients get +10 referral score on future leads they generate

### Lost Deals
Separate from the pipeline — any lead can be marked "Lost" from any stage with a required reason:
- In-house bar only (mis-qualified)
- Went with competitor (which one?)
- Budget too low
- No response after full sequence
- Venue closed / not operational
- Other (free text)

Lost reasons feed analytics: "We lose 40% of proposals to Sweet & Chilli on price"

---

## 5. Making Lead Interaction Tracking Intuitive

### The Activity Bar Pattern
At the top of every lead detail panel, show five action buttons:

```
[📧 Email]  [📞 Call]  [📝 Note]  [📅 Meeting]  [📋 Task]
```

Each opens a minimal inline form (not a page navigation). Form is pre-filled with today's date/time and the assigned team member.

### Activity Timeline
Below the action bar, show a reverse-chronological timeline:

```
Today
  📞 Emily called — Connected, discussed summer 2027 bookings
  📧 Automated follow-up email sent (Sequence: Wedding Intro, Step 3)

3 days ago
  📝 Joe added note: "Met at Cotswolds Wedding Fair, interested in autumn package"

1 week ago
  📧 Emily sent initial outreach email — Opened (2x)

2 weeks ago
  🔍 Lead imported from Hitched.co.uk scraper
```

### Quick-Log Patterns
For the most common actions, minimise friction:

**Email:** If email integration exists, auto-log. If manual, just: `Subject + outcome (Sent/Replied/Bounced) + optional note`

**Call:** `Outcome dropdown (Connected/Voicemail/No Answer/Wrong Number) + duration + note + next step`

**Meeting:** `Date + location (venue/video/phone) + attendees + outcome + next step`

**Note:** `Free text + optional tag (Intel/Feedback/Internal)`

**Task:** `Description + due date + assigned to + priority (High/Medium/Low)`

### Auto-Logging Recommendations
Where possible, reduce manual data entry:
- Email opens tracked automatically
- "Days since last contact" calculated automatically
- "Total interactions" counted automatically
- Stage duration tracked automatically ("In Proposal for 12 days")
- Overdue tasks surfaced in Command Centre

### Mobile Quick Actions
On mobile, the lead card should show a "swipe to act" pattern:
- Swipe right: Log call (quick form)
- Swipe left: Schedule follow-up
- Tap: Open detail panel
- Long press: Move to next stage

---

## 6. Top 5 UX Recommendations for HHT Dashboard

### 1. Default to Kanban, Offer Table and Map as Alternatives
Pipedrive proves that kanban is the natural mental model for pipeline management. Joe should see his leads as cards flowing left to right through stages. But keep the table view for bulk operations and the map view for geographic planning. Toggle between all three with one click.

### 2. Steal folk.app's Design Language
Folk proves a CRM can be beautiful AND fast. The current HHT dashboard has a warm ivory editorial aesthetic (Georgia serif, Inter sans) — keep that, but apply folk's principles: generous white space, non-distracting colours, minimal UI chrome, fast load times (<3 seconds). Premium feel = Joe takes it seriously.

### 3. Implement Pipedrive's "Rotting Deals" as "Stale Leads"
The single most impactful feature for HHT. If a venue hasn't been contacted in 7+ days, the card turns amber. 14+ days, it turns red. This creates gentle urgency without being annoying. Joe's team is small (7 people) — they need visual prompts to maintain follow-up discipline across 392+ leads.

### 4. Make Lead Scoring Transparent (HubSpot Pattern)
Don't just show a number. Show WHY. Click the score badge and see: "Dry hire (+15), 250 capacity (+10), wedding venue (+5), responded to email (+15), Oxfordshire (+5) = 50". This builds trust in the system and helps Joe's team understand which leads are genuinely worth pursuing vs which just happen to have a high score.

### 5. One-Click Activity Logging (Close Pattern)
The #1 reason CRMs fail is data entry friction. Every interaction should be loggable in under 10 seconds. Pre-filled forms, dropdown outcomes, auto-calculated fields. If it takes more than 3 clicks to log a call, the team won't use it.

---

## 7. Competitive Feature Matrix

| Feature | Apollo | Pipedrive | Close | folk | HubSpot | HHT (Target) |
|---------|--------|-----------|-------|------|---------|---------------|
| Kanban pipeline | Partial | Best | Good | Good | Good | Must have |
| Table/list view | Best | Good | Best | Good | Good | Must have |
| Map view | No | No | No | No | No | Already have |
| Lead scoring | AI | AI (new) | Manual | No | Best | Weighted (custom) |
| Score explainability | No | No | No | No | Yes | Must have |
| One-click activity log | Good | Best | Best | Basic | Good | Must have |
| Activity timeline | Good | Good | Best | Basic | Best | Must have |
| Slide-out detail panel | Yes | Yes | Yes | Yes | Yes | Must have |
| Stale deal alerts | No | Best | Good | No | Good | Must have |
| Smart saved filters | Yes | Good | Best | Good | Good | Must have |
| Mobile responsive | Good | Best | Good | Good | Good | Must have |
| Bulk actions | Best | Good | Good | Good | Good | Must have |
| Gmail integration | Good | Good | Good | Good | Best | Nice to have |
| Data enrichment | Best | No | No | Basic | Good | Via Clay/waterfall |
| Venue classification | No | No | No | No | No | Unique to HHT |
| Competitor tracking | No | No | No | No | No | Unique to HHT |

---

## 8. Sources

### Tools Researched
- [Apollo.io](https://www.apollo.io/) — [Review](https://lagrowthmachine.com/apollo-io-review/)
- [Hunter.io](https://hunter.io/) — [Features](https://www.dimmo.ai/software-features/top-hunter-io-features)
- [Lemlist](https://www.lemlist.com/) — [Review](https://www.heyreach.io/blog/lemlist-review)
- [Instantly.ai](https://instantly.ai/) — [Review](https://www.salesforge.ai/blog/instantly-ai-review)
- [Clay.com](https://www.clay.com/) — [Review](https://lagrowthmachine.com/clay-review/)
- [Lusha](https://www.lusha.com/) — [Review](https://lagrowthmachine.com/lusha-review/)
- [Snov.io](https://snov.io/) — [CRM Features](https://snov.io/sales-crm)
- [Leadfeeder](https://www.leadfeeder.com/) — [Product](https://www.leadfeeder.com/product/)
- [Pipedrive](https://www.pipedrive.com/) — [Pipeline Management](https://www.pipedrive.com/en/features/pipeline-management), [Review](https://www.findmycrm.com/blog/pipedrive-crm-review-complete-analysis-of-features-pricing-performance)
- [HubSpot CRM](https://www.hubspot.com/products/crm/lead-management) — [Lead Scoring Guide](https://www.default.com/post/hubspot-lead-scoring)
- [Close.com](https://www.close.com/) — [Product Tour](https://www.close.com/product), [Review](https://www.authencio.com/blog/close-crm-review-power-dialer-pricing-pros-cons-competitors)
- [Streak CRM](https://www.streak.com/) — [Features](https://www.streak.com/features)
- [folk.app](https://www.folk.app/) — [Pipelines](https://www.folk.app/products/pipelines-management), [Review](https://www.onepagecrm.com/crm-reviews/folk/)

### Design Pattern Sources
- [CRM UX Design Best Practices — Aufait UX](https://www.aufaitux.com/blog/crm-ux-design-best-practices/)
- [Enterprise CRM UI/UX Design Patterns — Coders.dev](https://www.coders.dev/blog/great-examples-of-enterprise-applications-crm-ui-ux-design-patterns.html)
- [CRM Design Best Practices — Adam Fard](https://adamfard.com/blog/crm-design)
- [CRM Design Trends 2025-2026 — FuseLab](https://fuselabcreative.com/top-5-crm-design-trends-2025/)
- [Kanban in Sales — Pipeline CRM](https://pipelinecrm.com/blog/kanban-sales-pipelines/)

### Lead Scoring Sources
- [Lead Scoring for Events — Momencio](https://www.momencio.com/5-tips-for-effective-lead-scoring-criteria/)
- [Lead Qualification for Hotels & Venues — Event Temple](https://www.eventtemple.com/blog/mastering-lead-qualification-for-hotels-venues-checklist-examples-and-scoring-model)
- [B2B Lead Scoring Guide — Outfunnel](https://outfunnel.com/lead-scoring/)
- [Lead Scoring Examples — UserMotion](https://usermotion.com/blog/lead-scoring-examples)
- [HubSpot Lead Scoring 2026 — NBH](https://www.nbh.co/learn/hubspot-lead-scoring-2026-how-to-drive-predictable-growth)
