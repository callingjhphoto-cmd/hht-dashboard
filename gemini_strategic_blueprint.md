# Strategic Blueprint for AI-Driven Lead Generation and CRM Architecture: HHT
**Source:** Gemini Deep Research (17 March 2026)

## Key Numbers
- UK pubs/bars market: £30.5B by end 2025 (+4.5% YoY)
- Cocktail bars grew 4.3% (larger than 2020 despite nightclub decline)
- UK cocktail mixers: $1.2B in 2024, 8% CAGR to $1.9B by 2030
- RTD cocktails: $220M in 2024, 16.8% CAGR to $555M by 2030
- The Cocktail Service: entered admin 25 Jan 2024, dissolution April 2025

## Cost: AI vs Salesperson
- £60K salesperson fully loaded = **£73,000/year** (inc 15% employer NIC, pension, overheads)
- Human SDRs spend only 28% of time actually selling
- AI SDR stack: **£4,700-£18,800/year** = 80% cost saving
- Responding within 5 minutes = 21x qualification odds (MIT research)
- AI companies report 30% increase in lead conversion

## Pricing Benchmarks (verified)
| Model | UK Cost |
|---|---|
| Cash bar / min spend | £300-500 booking, £1,500-3,500 min spend |
| Part-hosted hybrid | £1,000-2,000 tab |
| All-inclusive open bar | £32-60+/head, £2,500-6,500+ total |
| Dry hire | £749-1,999 |
| Target AOV | £1,150-1,550+ per event |
| Target GM | 70-85% |

## 7-Stage Pipeline
1. Lead Captured / Prospecting
2. Qualification (MQL) — auto-disqualify below £1,500 min spend
3. Needs Assessment / Discovery
4. Proposal & Quote Sent — auto follow-up 48hr + 7 days
5. Negotiation & Contract
6. Closed Won (deposit paid) — triggers Event Execution pipeline
7. Post-Event Nurture — auto review request + re-booking drip

## Lead Scoring

### B2B (Corporate)
- Target industry (PR, Events, Tech, Finance): +20
- Job title authority (Event Director, Head of Marketing): +15
- Company 100-500+ employees: +15
- Requested quote/demo: +30
- Multiple pricing page visits: +15

### B2C (Weddings)
- Event 6-12 months out: +20
- Venue booked: +25
- 100+ guests: +20
- Responds within 24hr: +15

### Thresholds
- 80+ = SQL/Hot → immediate human contact within 1 hour
- 50-79 = MQL/Warm → automated nurture sequence
- 0-49 = Cold → monthly newsletter
- Negative = Disqualified → archive

## Tech Stack
1. **Scraping:** Apollo.io / PhantomBuster
2. **Enrichment:** Clay (waterfall, 150+ data providers)
3. **AI Qualification:** LLM reads company About page, scores against ICP
4. **Outreach:** Smartlead / Instantly (inbox rotation, warm-up)
5. **Automation:** Make.com / Zapier
6. **CRM:** Custom Pipedrive-style kanban

## UX Lessons
- Apollo.io: great data density but overwhelming UI, steep learning curve
- Hunter.io: elegant, simple, focused — model for frontend
- **Synthesis:** Apollo's backend utility + Hunter's minimalist frontend
- Don't expose backend complexity to Joe — dashboard is consumption layer only

## Mobile Dashboard (Apple HIG)
- SF Pro typography, Dynamic Type support
- Bento box card grids
- 44x44pt minimum touch targets
- Bottom tab navigation
- White (#FFFFFF) / light gray (#F2F2F7) backgrounds
- Color only for status: Green=Won, Blue=Active, Red=Action Required
- SF Symbols 7 for icons

## Action Items
- [ ] Build Pipedrive kanban with 7 stages
- [ ] Implement lead scoring (B2B + B2C rubrics)
- [ ] Set up deal rotting (14 days = red flag)
- [ ] Map The Cocktail Service's orphaned clients
- [ ] Build automated outreach sequences
- [ ] Auto-disqualify below £1,500 min spend
- [ ] Mobile-first Apple HIG design
- [ ] Present to Joe: "£15K AI engine vs £73K salesperson"
