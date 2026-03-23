# HHT Verifier Training Audit — 2026-03-20

## 1. Verification Output Audit

### verified_leads_2026-03-20.csv
- **Total leads verified:** 1 (Hampshire Cricket / Utilita Bowl)
- **Confidence score distribution:**
  - >= 40 (PASS): 0
  - < 40 (QUARANTINE): 1
  - Score = 0: 1 lead (Hampshire Cricket)
- **Why only 1 lead?** The `for_verification_2026-03-20.csv` input file contained only 1 lead. The JSON-to-CSV bridge (`hht_json_to_verifier_csv.py --skip-archived`) filters out ARCHIVE-tier leads, and 147/148 enriched leads were ARCHIVE. Only 1 was NURTURE.
- **Why confidence = 0?** The lead had:
  - `website_status: MISMATCH` (ageasbowl.com didn't match "Hampshire Cricket" name — the Utilita Bowl branding causes a mismatch)
  - `phone: no_phone` — no phone number in source data
  - `email: none found` — no email extracted
  - `crossref: skipped` — cross-reference was skipped
  - `bar_policy: UNKNOWN` — couldn't determine bar policy
  - Per the scoring formula: MISMATCH(-5) + no_email(-10) + no_phone(-10) + no_contact_person(-10) + no_crossref(-10) = -45, clamped to 0

### Failure Reasons
| Reason | Count |
|--------|-------|
| Website MISMATCH | 1 |
| No phone | 1 |
| No email found | 1 |
| Cross-ref skipped | 1 |
| Bar policy UNKNOWN | 1 |

## 2. Deduplication Effectiveness

### net_new_leads_2026-03-20.json
- **Contents:** Empty array `[]`
- **Verified count:** 1 lead
- **Net new:** 0 leads
- **Duplicate %:** N/A — the single lead scored 0 (below quarantine threshold of 40), so it never reached the dedup stage. The empty net_new file means either dedup found it was a duplicate OR the pipeline correctly quarantined it before dedup.
- **Near-match analysis:** Not applicable with only 1 lead processed.

## 3. Quarantine Review

- **quarantine_leads_2026-03-20.json:** DOES NOT EXIST
- **Issue:** The pipeline should have created this file for the 1 lead that scored 0 (below threshold of 40). This is a gap in the pipeline — quarantine file was not generated, meaning the failed lead was silently dropped.
- **Recoverable leads:** Hampshire Cricket (Utilita Bowl) IS recoverable:
  - It's a real venue (Ageas Bowl, Southampton — large cricket/events venue)
  - The website mismatch is a false negative — the venue rebranded from Ageas Bowl, URL is correct
  - Manually enrichable: website is live, events team contactable
  - **Recommendation:** Add manual override for known venue rebrandings/alias mismatches

## 4. Verifier Script Audit (`hht_lead_verifier.py`)

### Confidence Scoring Logic (lines 699-758)
| Check | Pass | Fail |
|-------|------|------|
| Website VERIFIED | +30 | -5 to -10 |
| Email found + MX valid | +25 | -10 |
| Phone valid | +15 | -10 |
| Contact person found | +10 | -10 |
| Cross-ref confirmed | +20 | -10 |
| Google rating/reviews bonus | +2 to +5 | 0 |
| Bar policy boost (post-score) | +10 to +15 | -20 (in-house) |

**Maximum possible:** 30+25+15+10+20+5+15 = 120 (clamped to 100)
**Minimum possible (all fail):** -10-10-10-10-10+0-20 = -70 (clamped to 0)

### Edge Cases and Issues Found

1. **CRITICAL — Asymmetric penalty structure causes score floor at 0:**
   - A lead with no data (no website, no email, no phone, no contact, no crossref) scores -50 before bar policy. This means ANY lead entering the verifier without pre-enriched contact data will score 0 and be quarantined — even if the venue is legitimate.
   - This explains why 147/148 ARCHIVE leads were filtered before verification: the enricher found 0 websites, 0 emails, 0 phones for all 100 venues it processed, so they'd all score 0.

2. **Website MISMATCH logic too strict (lines 259-266):**
   - Requires >= 50% of "meaningful name parts" to appear in page title or body
   - Fails for venues with rebrandings, trading names different from legal names, or venues whose website title doesn't contain the venue name (e.g., "Utilita Bowl" vs "Hampshire Cricket")
   - **Fix needed:** Add alias/trading name lookup, or reduce threshold to 30%, or check URL domain as additional signal

3. **No partial credit for having a website URL even if unverifiable:**
   - If the HTTP request times out or gets a 403, the lead loses points (-10 for DEAD or MISMATCH) even though having a URL is better than having nothing
   - **Fix needed:** Add a small positive score (+5) for having a non-empty website URL, separate from verification status

4. **Cross-reference penalty too harsh:**
   - Skipping cross-ref (--skip-crossref flag) still costs -10 points, same as if cross-ref actively failed
   - **Fix needed:** If cross-ref was SKIPPED (not FAILED), score should be 0, not -10

5. **Contact person extraction biased toward team pages:**
   - Only checks h2/h3/h4/strong/b tags and team-keyword-class elements
   - Many venue sites list the events manager or wedding coordinator in paragraph text or footer
   - Won't catch "Events Manager: Sarah Jones" unless Sarah Jones is in a heading tag

6. **Phone verification doesn't handle international format well:**
   - UK_PHONE_RE expects `+44` or `0` prefix patterns
   - Some venues list phones as "01234 567890" in text but the scraper passes empty string if the number wasn't in source CSV
   - The verifier only checks source CSV phone, not phones extracted from website, for the initial `phone` field

### Improvements Needed (Priority Order)

1. **P0 — Fix cross-ref SKIPPED vs FAILED scoring:** Score 0 when skipped, -10 only when actively failed
2. **P0 — Generate quarantine file:** Pipeline must create quarantine JSON for all leads < 40, not silently drop them
3. **P1 — Add partial credit for having a URL:** +5 for non-empty website field regardless of verification status
4. **P1 — Website name matching improvements:** Lower threshold to 30% OR add domain-name matching (if "ageasbowl" is in URL and "bowl" appears in venue name, treat as partial match)
5. **P2 — Extract contacts from page body text:** Add regex for patterns like "Contact: [Name]", "Events Manager: [Name]", "[Name], Events Coordinator"
6. **P2 — Log why each point was awarded/deducted:** Add verbose flag to output score breakdown per lead

## 5. Master Database Cross-Reference

### hht-leads.csv
- **Total leads:** 40 (41 lines including header)
- **Format:** Category, Company Name, Contact Person, Website, Email, Phone, Location, Relevance Notes
- **Net new appended from today's run:** 0 (net_new was empty)
- **Formatting issues:** None detected — header and data rows are consistent
- **Note:** The master database has only 40 leads vs 148 enriched + 392 in SQLite DB (per TEAM.md notes). The master CSV is significantly behind the actual pipeline output. Leads from the expansion scraper (new counties) have not been merged into hht-leads.csv.

## 6. Upstream Enrichment Problem

The enrichment log (`enrichment_log_2026-03-20.txt`) reveals the root cause of today's poor verification results:
- **100/100 venues processed by enricher returned "No website found via search"**
- **0 websites found, 0 emails found, 0 phones found**
- This means the enricher's web search capability was non-functional on 2026-03-20
- Likely cause: WebFetch/WebSearch permissions denied (per the Permission Strategy in TEAM.md)
- All 100 venues were saved to enriched_venues.json without any contact data
- The verifier then received 1 lead (the only NURTURE-tier lead), which also had no contact data

**This is the primary pipeline failure.** The verifier performed correctly given its input — the problem is upstream. Agent 2 (Enricher) produced zero-quality output, and the pipeline still ran through to Agent 3 without raising an alert.

## 7. Summary Statistics

| Metric | Value |
|--------|-------|
| Enriched leads (input to pipeline) | 148 |
| ARCHIVE tier (filtered out) | 147 |
| NURTURE tier (sent to verifier) | 1 |
| Verified (score >= 40) | 0 |
| Quarantined (score < 40) | 1 |
| Quarantine file generated | NO (bug) |
| Net new leads added | 0 |
| Duplicate leads found | 0 |
| Master DB total (hht-leads.csv) | 40 |
| Enricher success rate | 0% (0/100 websites found) |

## 8. Recommendations

1. **Add enrichment quality gate:** Before Agent 3 runs, check if enrichment actually found data. If websites_found = 0 and emails_found = 0, halt pipeline and alert — don't waste verification cycles.
2. **Fix quarantine file generation:** The pipeline MUST create quarantine_leads JSON. Silent lead dropping is unacceptable.
3. **Fix cross-ref SKIPPED scoring:** Eliminate the -10 penalty when cross-ref is intentionally skipped.
4. **Add website alias matching:** Support venue name aliases/rebranding in the verification step.
5. **Merge expansion leads to master CSV:** 392 venues in SQLite are not reflected in hht-leads.csv (40 leads). Need a merge/sync process.
6. **Add pipeline health check:** After each stage, emit a pass/fail signal. If any stage produces 0 actionable output, the pipeline should report this rather than silently completing.

---
*Audit performed: 2026-03-20 | Agent: HHT Verification & Deduplication Agent (Training Mode)*
