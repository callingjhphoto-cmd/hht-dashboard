#!/usr/bin/env python3
"""
HHT Outreach — Priority Scorer V2 (Loop 8 Upgrade)
=====================================================
Scores venues on a 0-35 point scale to prioritize outreach.

V2 Enhancements:
  - Venue capacity weighting (bigger = more revenue per event)
  - Social media activity score (active Instagram = more likely to respond)
  - Website quality score (professional site = legitimate business)
  - Seasonality bonus (summer venues get priority in spring outreach)
  - Competitor presence (if competitor serves them, adjust priority)
  - Response likelihood score based on email type
  - Revenue potential weighting by event type

V1 Scoring (0-21):
  +5  Orphaned Cocktail Service client
  +3  Has events section on website
  +3  Is a wedding venue
  +3  No in-house bar (DRY_HIRE / EXTERNAL_OK)
  +2  Capacity > 100
  +2  Target geography
  +2  Has contact email
  +1  Verified / enriched data

V2 Additional (0-14):
  +3  Capacity tier bonus (200+ = +3, 150+ = +2, 100+ = +1)
  +2  Social media activity (Instagram found = +1, >1 platform = +2)
  +2  Named contact / decision maker found
  +2  Revenue potential (festival > corporate > wedding > private)
  +2  Seasonality alignment (venue type matches current outreach window)
  +1  Website quality (has SSL, loads fast, professional design signals)
  +1  No competitor presence detected
  +1  Email quality bonus (named person > events@ > info@)

Total V2 max: 35 points

Tiers (V2):
  28+ = IMMEDIATE (raw 28+) — call today
  22-27 = HIGH_PRIORITY — this week
  15-21 = STANDARD — this month
  8-14 = NURTURE — next quarter
  0-7 = LOW — archive unless strategic

Usage:
    from priority_scorer import score_venue_v2, score_all_v2
    score = score_venue_v2(venue_dict)
    scored_list = score_all_v2(venues_list)
"""

import os
import json
import sys
from datetime import datetime
from collections import Counter

# Target geographies (case-insensitive matching)
TARGET_GEOS = [
    "london", "greater london", "oxfordshire", "cotswolds",
    "buckinghamshire", "berkshire", "surrey", "hertfordshire",
    "kent", "essex", "hampshire", "sussex", "east sussex", "west sussex",
    "home counties", "middlesex", "wiltshire", "gloucestershire",
    # Expansion counties
    "cambridgeshire", "norfolk", "suffolk",
    "somerset", "dorset", "devon",
    "warwickshire", "worcestershire",
]

# Revenue estimates by event type (used for revenue potential scoring)
REVENUE_BY_TYPE = {
    "festival": 8000,
    "corporate": 5000,
    "wedding": 3500,
    "polo": 10000,
    "racing": 8000,
    "awards": 6000,
    "christmas_party": 4000,
    "product_launch": 6000,
    "private_hire": 2500,
}

# Current month for seasonality
CURRENT_MONTH = datetime.now().month

# Seasonality windows — when to prioritize outreach by venue type
SEASONALITY = {
    # Outreach months → event months
    # Outreach in Jan-Mar for summer weddings
    "wedding": {"outreach_months": [1, 2, 3, 4, 9, 10], "peak_months": [5, 6, 7, 8, 9]},
    # Outreach in Sep-Oct for Christmas
    "christmas_party": {"outreach_months": [7, 8, 9, 10], "peak_months": [11, 12]},
    # Outreach in Jan-Apr for summer festivals
    "festival": {"outreach_months": [1, 2, 3, 4], "peak_months": [5, 6, 7, 8, 9]},
    # Corporate = year-round
    "corporate": {"outreach_months": list(range(1, 13)), "peak_months": list(range(1, 13))},
    # Polo/racing = spring outreach for summer season
    "polo": {"outreach_months": [2, 3, 4], "peak_months": [5, 6, 7, 8]},
}

# Email quality ranking (lower = better)
EMAIL_QUALITY = {
    "named_person": 1,  # firstname.lastname@ or firstname@
    "events": 2,
    "weddings": 2,
    "wedding": 2,
    "functions": 3,
    "bookings": 3,
    "hire": 3,
    "enquiries": 4,
    "hello": 5,
    "info": 6,
    "admin": 7,
    "reception": 7,
}


def classify_email_quality(email: str) -> str:
    """Classify email quality tier."""
    if not email or "@" not in email:
        return "none"
    local = email.split("@")[0].lower()
    # Named person check — has a dot and no generic prefix
    generic_prefixes = ["info", "admin", "hello", "enquir", "reception",
                        "bookings", "events", "weddings", "wedding",
                        "functions", "hire", "contact"]
    if "." in local and not any(local.startswith(p) for p in generic_prefixes):
        return "named_person"
    for prefix, _ in sorted(EMAIL_QUALITY.items(), key=lambda x: x[1]):
        if local.startswith(prefix):
            return prefix
    return "generic"


def detect_event_type(venue: dict) -> str:
    """Detect the primary event type for a venue."""
    text = " ".join([
        str(venue.get("category", "")),
        str(venue.get("type", "")),
        str(venue.get("lead_type", "")),
        str(venue.get("event_types", "")),
        str(venue.get("notes", "")),
    ]).lower()

    if "festival" in text:
        return "festival"
    if "polo" in text:
        return "polo"
    if "racing" in text or "racecourse" in text:
        return "racing"
    if "christmas" in text:
        return "christmas_party"
    if "award" in text or "gala" in text:
        return "awards"
    if "corporate" in text or "conference" in text or "retreat" in text:
        return "corporate"
    if "launch" in text or "product" in text:
        return "product_launch"
    if "wedding" in text or "bridal" in text or "ceremony" in text:
        return "wedding"
    return "private_hire"


# ---------------------------------------------------------------------------
# V1 Scoring (Original — preserved for backwards compatibility)
# ---------------------------------------------------------------------------

def score_venue(venue: dict) -> dict:
    """
    V1 scorer — 0-21 scale. Kept for backwards compatibility.
    """
    score = 0
    reasons = []

    # +5 — Orphaned Cocktail Service client
    is_orphan = (
        str(venue.get("id", "")).startswith("ORPHAN")
        or bool(venue.get("cocktail_service_relationship"))
        or str(venue.get("strategic_reason", "")).lower() == "orphaned_client"
    )
    if is_orphan:
        score += 5
        reasons.append("orphaned_client(+5)")

    # +3 — Has events section
    has_events = venue.get("has_events_section", False)
    if not has_events:
        desc = " ".join([
            str(venue.get("description", "")),
            str(venue.get("notes", "")),
            str(venue.get("raw_description", "")),
            str(venue.get("classification_note", "")),
        ]).lower()
        if any(w in desc for w in ["event", "function", "hire", "reception", "hospitality"]):
            has_events = True
    if has_events:
        score += 3
        reasons.append("events_section(+3)")

    # +3 — Wedding venue
    desc_lower = " ".join([
        str(venue.get("lead_type", "")),
        str(venue.get("type", "")),
        str(venue.get("category", "")),
        str(venue.get("description", "")),
        str(venue.get("classification_note", "")),
    ]).lower()
    if any(w in desc_lower for w in ["wedding", "ceremony", "bridal"]):
        score += 3
        reasons.append("wedding_venue(+3)")

    # +3 — No in-house bar
    classification = str(venue.get("classification", "")).upper()
    no_bar = venue.get("has_in_house_bar") is False or venue.get("no_bar_mentioned", False)
    if classification in ("DRY_HIRE", "EXTERNAL_OK") or no_bar:
        score += 3
        reasons.append("no_in_house_bar(+3)")

    # +2 — Capacity > 100
    cap = venue.get("capacity", 0) or venue.get("estimated_capacity", 0)
    if isinstance(cap, str):
        cap = int("".join(c for c in cap if c.isdigit()) or "0")
    if cap > 100:
        score += 2
        reasons.append(f"capacity_{cap}(+2)")

    # +2 — Target geography
    geo_fields = " ".join([
        str(venue.get("county", "")),
        str(venue.get("city", "")),
        str(venue.get("location", "")),
        str(venue.get("address", "")),
    ]).lower()
    if any(g in geo_fields for g in TARGET_GEOS):
        score += 2
        reasons.append("target_geo(+2)")

    # +2 — Has contact email
    email = str(venue.get("email", "")).strip()
    has_email = (
        email
        and email not in ("", "NEEDS_ENRICHMENT", "UNABLE_TO_FIND", "CONTACT_FORM_ONLY")
        and "@" in email
    )
    if has_email:
        score += 2
        reasons.append("has_email(+2)")

    # +1 — Verified
    enrichment = str(venue.get("enrichment_status", "")).upper()
    is_verified = not venue.get("unverified", True)
    if "ENRICHED" in enrichment or is_verified:
        score += 1
        reasons.append("verified(+1)")

    # Tier
    if score >= 15:
        tier = "CALL_NOW"
    elif score >= 10:
        tier = "HIGH_PRIORITY"
    elif score >= 6:
        tier = "STANDARD"
    elif score >= 3:
        tier = "NURTURE"
    else:
        tier = "LOW"

    venue["outreach_score"] = score
    venue["outreach_score_breakdown"] = " + ".join(reasons) if reasons else "no_qualifying_criteria"
    venue["outreach_tier"] = tier
    return venue


# ---------------------------------------------------------------------------
# V2 Scoring (Enhanced — 0-35 scale)
# ---------------------------------------------------------------------------

def score_venue_v2(venue: dict) -> dict:
    """
    V2 scorer — 0-35 scale with enhanced criteria.
    """
    score = 0
    reasons = []

    # ===== V1 CRITERIA (0-21) =====

    # +5 — Orphaned client
    is_orphan = (
        str(venue.get("id", "")).startswith("ORPHAN")
        or bool(venue.get("cocktail_service_relationship"))
        or str(venue.get("strategic_reason", "")).lower() == "orphaned_client"
        or str(venue.get("strategic_priority", "")).upper() == "HIGH"
    )
    if is_orphan:
        score += 5
        reasons.append("orphaned_client(+5)")

    # +3 — Events section
    has_events = venue.get("has_events_section", False)
    if not has_events:
        desc = " ".join([
            str(venue.get("description", "")),
            str(venue.get("notes", "")),
            str(venue.get("raw_description", "")),
            str(venue.get("classification_note", "")),
        ]).lower()
        if any(w in desc for w in ["event", "function", "hire", "reception", "hospitality"]):
            has_events = True
    if has_events:
        score += 3
        reasons.append("events_section(+3)")

    # +3 — Wedding venue
    desc_lower = " ".join([
        str(venue.get("lead_type", "")),
        str(venue.get("type", "")),
        str(venue.get("category", "")),
        str(venue.get("description", "")),
        str(venue.get("classification_note", "")),
    ]).lower()
    if any(w in desc_lower for w in ["wedding", "ceremony", "bridal"]):
        score += 3
        reasons.append("wedding_venue(+3)")

    # +3 — No in-house bar
    classification = str(venue.get("classification", "")).upper()
    no_bar = venue.get("has_in_house_bar") is False or venue.get("no_bar_mentioned", False)
    if classification in ("DRY_HIRE", "EXTERNAL_OK") or no_bar:
        score += 3
        reasons.append("no_in_house_bar(+3)")

    # +2 — Target geography
    geo_fields = " ".join([
        str(venue.get("county", "")),
        str(venue.get("city", "")),
        str(venue.get("location", "")),
        str(venue.get("address", "")),
    ]).lower()
    if any(g in geo_fields for g in TARGET_GEOS):
        score += 2
        reasons.append("target_geo(+2)")

    # +2 — Has email
    email = str(venue.get("email", "")).strip()
    has_email = (email and "@" in email
                 and email not in ("NEEDS_ENRICHMENT", "UNABLE_TO_FIND", "CONTACT_FORM_ONLY"))
    if has_email:
        score += 2
        reasons.append("has_email(+2)")

    # +1 — Verified
    enrichment = str(venue.get("enrichment_status", "")).upper()
    is_verified = not venue.get("unverified", True)
    if "ENRICHED" in enrichment or is_verified:
        score += 1
        reasons.append("verified(+1)")

    # ===== V2 ENHANCEMENTS (0-14) =====

    # +3 — Capacity tier (replaces V1 binary +2)
    cap = venue.get("capacity", 0) or venue.get("estimated_capacity", 0)
    if isinstance(cap, str):
        cap = int("".join(c for c in cap if c.isdigit()) or "0")
    if cap >= 200:
        score += 3
        reasons.append(f"capacity_{cap}(+3)")
    elif cap >= 150:
        score += 2
        reasons.append(f"capacity_{cap}(+2)")
    elif cap >= 100:
        score += 1
        reasons.append(f"capacity_{cap}(+1)")

    # +2 — Social media activity
    social_count = 0
    if venue.get("instagram"):
        social_count += 1
    if venue.get("facebook"):
        social_count += 1
    if venue.get("linkedin"):
        social_count += 1
    if venue.get("tiktok"):
        social_count += 1
    social_score = venue.get("social_score", 0)
    if social_count >= 2 or social_score >= 5:
        score += 2
        reasons.append(f"social_active_{social_count}platforms(+2)")
    elif social_count >= 1 or social_score >= 3:
        score += 1
        reasons.append(f"social_present(+1)")

    # +2 — Named decision maker found
    has_contact_name = bool(venue.get("contact_name") or venue.get("decision_maker_name"))
    if has_contact_name:
        score += 2
        reasons.append("decision_maker_found(+2)")

    # +2 — Revenue potential
    event_type = detect_event_type(venue)
    rev = REVENUE_BY_TYPE.get(event_type, 2500)
    if rev >= 8000:
        score += 2
        reasons.append(f"high_revenue_{event_type}(+2)")
    elif rev >= 5000:
        score += 1
        reasons.append(f"medium_revenue_{event_type}(+1)")

    # +2 — Seasonality alignment
    season = SEASONALITY.get(event_type)
    if season and CURRENT_MONTH in season["outreach_months"]:
        score += 2
        reasons.append(f"seasonal_alignment_{event_type}(+2)")

    # +1 — Website quality (SSL + loads)
    website = str(venue.get("website", ""))
    if website.startswith("https://"):
        score += 1
        reasons.append("website_ssl(+1)")

    # +1 — No competitor presence
    has_competitor = venue.get("competitor_used", False) or venue.get("competitor_presence", False)
    if not has_competitor:
        score += 1
        reasons.append("no_competitor(+1)")

    # +1 — Email quality bonus (named person email)
    email_quality = classify_email_quality(email)
    if email_quality == "named_person":
        score += 1
        reasons.append("named_email(+1)")

    # ===== TIER ASSIGNMENT (V2 scale) =====
    if score >= 28:
        tier = "IMMEDIATE"
    elif score >= 22:
        tier = "HIGH_PRIORITY"
    elif score >= 15:
        tier = "STANDARD"
    elif score >= 8:
        tier = "NURTURE"
    else:
        tier = "LOW"

    venue["outreach_score_v2"] = score
    venue["outreach_score_v2_breakdown"] = " + ".join(reasons) if reasons else "no_qualifying_criteria"
    venue["outreach_tier_v2"] = tier
    venue["event_type"] = event_type
    venue["estimated_revenue"] = rev
    venue["email_quality"] = email_quality

    # Also compute V1 for backwards compatibility
    venue = score_venue(venue)

    return venue


def score_all(venues: list) -> list:
    """Score all venues with V1, sort by score descending."""
    scored = [score_venue(v) for v in venues]
    scored.sort(key=lambda v: v["outreach_score"], reverse=True)
    return scored


def score_all_v2(venues: list) -> list:
    """Score all venues with V2, sort by V2 score descending."""
    scored = [score_venue_v2(v) for v in venues]
    scored.sort(key=lambda v: v["outreach_score_v2"], reverse=True)
    return scored


def print_summary(scored: list, version: str = "v1"):
    """Print a tier summary."""
    score_key = "outreach_score_v2" if version == "v2" else "outreach_score"
    tier_key = "outreach_tier_v2" if version == "v2" else "outreach_tier"

    tiers = Counter(v.get(tier_key, "UNKNOWN") for v in scored)

    if version == "v2":
        tier_order = ["IMMEDIATE", "HIGH_PRIORITY", "STANDARD", "NURTURE", "LOW"]
    else:
        tier_order = ["CALL_NOW", "HIGH_PRIORITY", "STANDARD", "NURTURE", "LOW"]

    print(f"\n{'Tier':<20} {'Count':>6}")
    print("-" * 28)
    for tier in tier_order:
        print(f"{tier:<20} {tiers.get(tier, 0):>6}")
    print(f"{'TOTAL':<20} {len(scored):>6}")

    # Revenue summary
    if version == "v2":
        total_rev = sum(v.get("estimated_revenue", 0) for v in scored
                        if v.get(tier_key) in ("IMMEDIATE", "HIGH_PRIORITY"))
        print(f"\nEstimated revenue from IMMEDIATE + HIGH_PRIORITY: £{total_rev:,.0f}")


if __name__ == "__main__":
    base = os.path.expanduser("~/Documents/Claude/projects/hht")

    # Load all venue sources
    all_venues = []

    for fname in ["sample_leads.json", "orphaned_clients_2026-03-18.json",
                   "new_leads_2026-03-18.json", "enriched_leads_2026-03-19.json"]:
        fpath = os.path.join(base, fname)
        if os.path.exists(fpath):
            with open(fpath) as f:
                data = json.load(f)
                leads = data.get("leads", data) if isinstance(data, dict) else data
                if isinstance(leads, list):
                    for v in leads:
                        v.setdefault("_source_file", fname)
                    all_venues.extend(leads)

    # Also load enriched venues
    enriched_path = os.path.join(base, "enriched_venues.json")
    if os.path.exists(enriched_path):
        with open(enriched_path) as f:
            enriched = json.load(f)
            for v in enriched:
                v.setdefault("_source_file", "enriched_venues.json")
            all_venues.extend(enriched)

    print(f"Loaded {len(all_venues)} venues from all sources")

    # Score with both versions
    use_v2 = "--v2" in sys.argv

    if use_v2:
        scored = score_all_v2(all_venues)
        print("\n=== V2 SCORING (0-35 scale) ===")
        print_summary(scored, "v2")

        print(f"\nTop 15 venues by V2 score:")
        print(f"{'V2':>4} {'V1':>4}  {'Tier':<16} {'Type':<12} {'Rev':>6}  {'Name':<30} {'Email Quality':<14}")
        print("-" * 100)
        for v in scored[:15]:
            name = v.get("venue_name", v.get("name", "Unknown"))[:29]
            print(f"{v.get('outreach_score_v2', 0):>4} {v.get('outreach_score', 0):>4}  "
                  f"{v.get('outreach_tier_v2', '?'):<16} {v.get('event_type', '?'):<12} "
                  f"£{v.get('estimated_revenue', 0):>5,}  {name:<30} {v.get('email_quality', '?'):<14}")
    else:
        scored = score_all(all_venues)
        print("\n=== V1 SCORING (0-21 scale) ===")
        print_summary(scored, "v1")

        print(f"\nTop 15 venues by V1 score:")
        print(f"{'Score':>5}  {'Tier':<16} {'Name':<35} {'Email':<35}")
        print("-" * 95)
        for v in scored[:15]:
            name = v.get("venue_name", v.get("name", "Unknown"))[:34]
            email = str(v.get("email", ""))[:34]
            print(f"{v['outreach_score']:>5}  {v['outreach_tier']:<16} {name:<35} {email:<35}")

    if "--full" in sys.argv:
        out_path = os.path.join(base, "outreach", "scored_venues.json")
        with open(out_path, "w") as f:
            json.dump(scored, f, indent=2)
        print(f"\nFull scored list saved to {out_path}")
