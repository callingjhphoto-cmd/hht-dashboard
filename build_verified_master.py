#!/usr/bin/env python3
"""
HHT Verified Leads Master Builder
===================================
Agent 3: Verification & Dedup Specialist

Steps:
1. Clean contact_finder_results.json (extract real names/roles, remove junk emails)
2. Run dedup across all sources
3. Merge all clean, deduped data into verified_leads_master.json
   Schema: { venue_name, website, email, phone, contact_name, contact_role,
             classification, county, score }

Usage: python3 build_verified_master.py
"""

import csv
import json
import os
import re
import sys
from datetime import datetime

try:
    from rapidfuzz import fuzz
except ImportError:
    print("ERROR: rapidfuzz not installed. Run: pip3 install rapidfuzz")
    sys.exit(1)

PROJECT_DIR = os.path.expanduser("~/Documents/Claude/projects/hht")
PLATFORM_DIR = os.path.expanduser("~/Documents/hht-operations-platform")
THRESHOLD = 85

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

JUNK_EMAILS = {"example@mail.com", "user@domain.com"}
SENTRY_PATTERN = re.compile(r"[a-f0-9]{32}@sentry", re.IGNORECASE)


def is_junk_email(email):
    if not email:
        return True
    if email.lower().strip() in JUNK_EMAILS:
        return True
    if SENTRY_PATTERN.search(email):
        return True
    return False


def clean_emails(emails_list):
    return [e.strip() for e in emails_list if not is_junk_email(e)]


def normalize_name(name):
    if not name:
        return ""
    name = name.lower().strip()
    for suffix in [
        " wedding venue", " weddings", " events", " venue", " ltd", " limited",
        " hotel & spa", " & spa", " golf club", " golf course", " country club",
        " wedding", " house wedding venue",
    ]:
        if name.endswith(suffix):
            name = name[: -len(suffix)].strip()
    if name.startswith("the "):
        name = name[4:]
    return name


def is_real_human_name(name):
    """Check if a string looks like a human name (not a UI element or bio blob)."""
    if not name:
        return False
    nl = name.lower().strip()
    JUNK_NAMES = {
        "venue manager", "wedding event manager", "general manager",
        "reviews from 2025", "reviews from 2024", "experienced team:",
        "menu", "360° virtual tour", "360\u00b0 virtual tour",
        "web design sozo", "senior event manager", "bar & event manager",
        "event manager", "head wedding coordinator", "our team",
        "the team", "meet the team",
    }
    if nl in JUNK_NAMES:
        return False
    if nl.endswith(":"):
        return False
    if len(nl) > 60:
        return False
    words = nl.split()
    if len(words) > 4:
        return False
    alpha_words = [w for w in words if re.match(r"^[a-zA-Z\-\']+$", w)]
    return len(alpha_words) >= 1


def clean_role_text(role):
    """Extract a clean job title from messy bio text."""
    if not role:
        return None
    role = role.strip()
    # Already clean if short
    if len(role) <= 60 and "\n" not in role:
        words = role.split()
        if len(words) <= 8:
            return role

    # Look for recognisable job title patterns
    patterns = [
        r"((?:Senior |Head |Lead |Junior |Assistant |Deputy )?(?:Wedding|Event|Events|Venue|Sales|Operations|General|Office)s?\s+(?:Manager|Coordinator|Planner|Director|Administrator|Executive|Consultant))",
        r"((?:Head|Director|Owner|Co-Owner|Co Owner|Partner|Founder)(?:\s+and\s+[\w\s]+)?)",
        r"(Owner(?:\s+(?:and|&)\s+[\w\s]+)?)",
        r"(Director(?:\s+(?:and|&)\s+[\w\s]+)?)",
    ]
    for pattern in patterns:
        m = re.search(pattern, role, re.IGNORECASE)
        if m:
            result = m.group(1).strip()
            if len(result) <= 80:
                return result

    # Fall back: first meaningful clause
    first = re.split(r"[\n.]", role)[0].strip()
    if len(first) <= 60:
        return first or None
    return None


# Manual overrides for entries where automated logic fails
CONTACT_OVERRIDES = {
    "Rackleys": (None, "Wedding Event Manager"),
    "Quantock Lakes": ("Sarah", "Wedding Coordinator"),
    "Dodford Manor": (None, "General Manager"),
    "Gate Street Barn": ("Annabel Kent", "Senior Event Manager"),
    "High House": (None, "Events Team"),
    "Lapstone Barn": (None, None),
    "Upton Barn": (None, None),
    "Godwick Hall": (None, "Wedding Planner Team"),
    "The Compasses at Pattiswick": ("Jane Clark", "Owner"),
    "The Granary Estates": ("Joely Allard", "Weddings and Events Sales Manager"),
}

# Granary Estates best_email was wrong (university arms) — correct it
EMAIL_OVERRIDES = {
    "The Granary Estates": "info@thegranaryestates.co.uk",
}


# ─────────────────────────────────────────────
# STEP 1: CLEAN contact_finder_results.json
# ─────────────────────────────────────────────

def clean_contact_finder():
    path = os.path.join(PROJECT_DIR, "contact_finder_results.json")
    with open(path) as f:
        raw = json.load(f)

    cleaned = []
    for entry in raw:
        venue = entry["venue_name"]

        # Clean emails
        raw_emails = entry.get("emails_found", [])
        clean_em = clean_emails(raw_emails)
        best_email = entry.get("best_email", "")
        if is_junk_email(best_email):
            best_email = clean_em[0] if clean_em else ""

        # Apply email overrides
        if venue in EMAIL_OVERRIDES:
            best_email = EMAIL_OVERRIDES[venue]

        # Extract contact name + role
        if venue in CONTACT_OVERRIDES:
            name, role = CONTACT_OVERRIDES[venue]
        else:
            existing_name = (entry.get("contact_name") or "").strip()
            existing_role = (entry.get("contact_role") or "").strip()
            if is_real_human_name(existing_name):
                name = existing_name.title()
                role = clean_role_text(existing_role)
            else:
                # Try contacts_found list
                name, role = None, None
                for c in (entry.get("contacts_found") or []):
                    cname = (c.get("name") or "").strip()
                    crole = (c.get("role") or "").strip()
                    if is_real_human_name(cname):
                        name = cname.title()
                        role = clean_role_text(crole)
                        break

        cleaned.append({
            "venue_name": venue,
            "website": entry.get("website", ""),
            "email": best_email,
            "all_emails": clean_em,
            "contact_name": name,
            "contact_role": role,
        })

    print(f"[Step 1] Cleaned {len(cleaned)} contact_finder entries")
    print(f"         With contact name: {sum(1 for c in cleaned if c['contact_name'])}")
    print(f"         With clean email:  {sum(1 for c in cleaned if c['email'])}")
    return cleaned


# ─────────────────────────────────────────────
# STEP 2: LOAD ALL LEAD SOURCES
# ─────────────────────────────────────────────

def load_json_leads(path, name_key="name", fallback_keys=None):
    """Load leads from a JSON file. Returns list of dicts."""
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = data.get("leads", data.get("results", []))
        if not isinstance(data, list):
            return []

        results = []
        for item in data:
            n = item.get(name_key) or ""
            if not n and fallback_keys:
                for fk in fallback_keys:
                    n = item.get(fk) or ""
                    if n:
                        break
            if n.strip():
                results.append(item)
        return results
    except Exception as e:
        print(f"  Warning: Could not read {os.path.basename(path)}: {e}")
        return []


def load_csv_leads(path):
    """Load leads from a CSV file. Returns list of dicts."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    except Exception as e:
        print(f"  Warning: Could not read {os.path.basename(path)}: {e}")
        return []


def get_lead_name(lead):
    """Extract normalised venue name from any lead format."""
    for key in ["venue_name", "name", "Name", "Company Name", "company_name"]:
        v = lead.get(key, "")
        if v and v.strip():
            return normalize_name(v.strip())
    return ""


# ─────────────────────────────────────────────
# STEP 3: BUILD MASTER SCHEMA RECORDS
# ─────────────────────────────────────────────

def to_master_record(source_dict, source_label="", contact_overrides=None):
    """Convert any lead format into the master schema."""

    def g(*keys):
        for k in keys:
            v = source_dict.get(k)
            if v and str(v).strip() and str(v).strip().lower() not in ("none", "null", "n/a", ""):
                return str(v).strip()
        return ""

    venue_name = g("venue_name", "name", "Name", "Company Name")
    website = g("website", "Website")
    email = g("email", "best_email", "Email")
    phone = g("phone", "Phone")
    contact_name = g("contact_name", "contact_person", "Contact Name")
    contact_role = g("contact_role", "Contact Role")
    classification = g("classification", "bar_policy", "Classification")
    county = g("county", "area", "County")
    score_raw = g("lead_score", "lead_score_raw", "confidence_score", "Score")

    try:
        score = int(float(score_raw)) if score_raw else 0
    except (ValueError, TypeError):
        score = 0

    # Apply contact overrides from contact_finder cleaning
    if contact_overrides and venue_name.lower() in contact_overrides:
        ov = contact_overrides[venue_name.lower()]
        if ov.get("contact_name"):
            contact_name = ov["contact_name"]
        if ov.get("contact_role"):
            contact_role = ov["contact_role"]
        if ov.get("email"):
            email = ov["email"]

    if not venue_name:
        return None

    return {
        "venue_name": venue_name,
        "website": website,
        "email": email,
        "phone": phone,
        "contact_name": contact_name,
        "contact_role": contact_role,
        "classification": classification or "UNKNOWN",
        "county": county,
        "score": score,
        "source": source_label,
    }


# ─────────────────────────────────────────────
# STEP 4: DEDUPLICATE
# ─────────────────────────────────────────────

def deduplicate(records, threshold=THRESHOLD):
    """Remove duplicate records by normalized name fuzzy match.
    When merging, prefer the record with more data (email, phone, contact_name, score).
    """
    deduped = []
    seen_normalized = []
    dupe_count = 0

    for rec in records:
        norm = normalize_name(rec["venue_name"])
        if not norm:
            continue

        # Check against seen
        best_match_idx = None
        best_match_score = 0
        for i, seen_norm in enumerate(seen_normalized):
            score = fuzz.ratio(norm, seen_norm)
            if score >= threshold and score > best_match_score:
                best_match_score = score
                best_match_idx = i

        if best_match_idx is not None:
            # Merge: keep the richer record
            existing = deduped[best_match_idx]
            merged = merge_records(existing, rec)
            deduped[best_match_idx] = merged
            dupe_count += 1
        else:
            deduped.append(rec)
            seen_normalized.append(norm)

    return deduped, dupe_count


def merge_records(a, b):
    """Merge two records, preferring non-empty / higher-scoring values."""
    result = dict(a)
    for key in ["website", "email", "phone", "contact_name", "contact_role", "county"]:
        if not result.get(key) and b.get(key):
            result[key] = b[key]
    # Prefer more specific classification
    priority = {"DRY_HIRE": 4, "EXTERNAL_OK": 3, "UNKNOWN": 2, "IN_HOUSE_ONLY": 1}
    score_a = priority.get(a.get("classification", "UNKNOWN"), 0)
    score_b = priority.get(b.get("classification", "UNKNOWN"), 0)
    if score_b > score_a:
        result["classification"] = b["classification"]
    # Prefer higher lead score
    if (b.get("score") or 0) > (result.get("score") or 0):
        result["score"] = b["score"]
    # Merge sources
    sources_a = result.get("source", "")
    sources_b = b.get("source", "")
    if sources_b and sources_b not in sources_a:
        result["source"] = f"{sources_a},{sources_b}" if sources_a else sources_b
    return result


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("HHT Verified Leads Master Builder — Agent 3")
    print(f"Run date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Step 1: Clean contact_finder_results
    print("\n[Step 1] Cleaning contact_finder_results.json...")
    cf_cleaned = clean_contact_finder()

    # Build quick lookup from cleaned contacts
    cf_lookup = {}
    for c in cf_cleaned:
        cf_lookup[normalize_name(c["venue_name"])] = {
            "email": c["email"],
            "contact_name": c["contact_name"],
            "contact_role": c["contact_role"],
        }

    # Step 2: Load all sources
    print("\n[Step 2] Loading all lead sources...")

    all_records = []

    # A: enriched_leads_2026-03-20.json (148 records — main scored batch)
    src = load_json_leads(os.path.join(PROJECT_DIR, "enriched_leads_2026-03-20.json"))
    recs = [to_master_record(r, "enriched_leads_2026-03-20", cf_lookup) for r in src]
    recs = [r for r in recs if r]
    all_records.extend(recs)
    print(f"  enriched_leads_2026-03-20.json: {len(recs)} records")

    # B: enriched_venues.json (150 records — contact enricher output)
    src = load_json_leads(os.path.join(PROJECT_DIR, "enriched_venues.json"), name_key="venue_name")
    recs = [to_master_record(r, "enriched_venues", cf_lookup) for r in src]
    recs = [r for r in recs if r]
    all_records.extend(recs)
    print(f"  enriched_venues.json: {len(recs)} records")

    # C: contact_finder_results.json (25 records — now cleaned)
    cf_as_leads = []
    for c in cf_cleaned:
        # Need county/classification from enriched_venues if available
        norm = normalize_name(c["venue_name"])
        county = ""
        classification = "DRY_HIRE"  # all contact_finder venues are dry hire barns
        for r in src:
            if normalize_name(r.get("venue_name", "")) == norm:
                county = r.get("county", "")
                classification = r.get("classification", "DRY_HIRE")
                break
        cf_as_leads.append({
            "venue_name": c["venue_name"],
            "website": c["website"],
            "email": c["email"],
            "phone": "",
            "contact_name": c["contact_name"],
            "contact_role": c["contact_role"],
            "classification": classification,
            "county": county,
            "score": 0,
        })
    recs = [to_master_record(r, "contact_finder_2026-03-20") for r in cf_as_leads]
    recs = [r for r in recs if r]
    all_records.extend(recs)
    print(f"  contact_finder_results.json (cleaned): {len(recs)} records")

    # D: hht_dryhire_leads.csv (110 records)
    src_csv = load_csv_leads(os.path.join(PROJECT_DIR, "hht_dryhire_leads.csv"))
    for row in src_csv:
        row["name"] = row.get("venue_name", "")
        row["classification"] = "DRY_HIRE"
    recs = [to_master_record(r, "hht_dryhire_leads_csv") for r in src_csv]
    recs = [r for r in recs if r]
    all_records.extend(recs)
    print(f"  hht_dryhire_leads.csv: {len(recs)} records")

    # E: enriched_leads_2026-03-18.json (5 records)
    src = load_json_leads(os.path.join(PROJECT_DIR, "enriched_leads_2026-03-18.json"))
    recs = [to_master_record(r, "enriched_leads_2026-03-18") for r in src]
    recs = [r for r in recs if r]
    all_records.extend(recs)
    print(f"  enriched_leads_2026-03-18.json: {len(recs)} records")

    # F: enriched_leads_2026-03-19.json (3 records)
    src = load_json_leads(os.path.join(PROJECT_DIR, "enriched_leads_2026-03-19.json"))
    recs = [to_master_record(r, "enriched_leads_2026-03-19") for r in src]
    recs = [r for r in recs if r]
    all_records.extend(recs)
    print(f"  enriched_leads_2026-03-19.json: {len(recs)} records")

    print(f"\n  TOTAL before dedup: {len(all_records)} records")

    # Step 3: Deduplicate
    print("\n[Step 3] Deduplicating...")
    master, dupe_count = deduplicate(all_records)
    print(f"  Duplicates merged: {dupe_count}")
    print(f"  Unique records: {len(master)}")

    # Sort by classification priority then score
    CLASSIF_ORDER = {"DRY_HIRE": 0, "EXTERNAL_OK": 1, "UNKNOWN": 2, "IN_HOUSE_ONLY": 3}
    master.sort(key=lambda r: (CLASSIF_ORDER.get(r["classification"], 99), -(r.get("score") or 0)))

    # Step 4: Stats
    has_email = sum(1 for r in master if r.get("email"))
    has_contact = sum(1 for r in master if r.get("contact_name"))
    has_phone = sum(1 for r in master if r.get("phone"))
    dry_hire = sum(1 for r in master if r.get("classification") == "DRY_HIRE")
    external_ok = sum(1 for r in master if r.get("classification") == "EXTERNAL_OK")
    unknown = sum(1 for r in master if r.get("classification") == "UNKNOWN")
    in_house = sum(1 for r in master if r.get("classification") == "IN_HOUSE_ONLY")

    print(f"\n[Stats]")
    print(f"  Total unique leads:    {len(master)}")
    print(f"  DRY_HIRE:              {dry_hire}")
    print(f"  EXTERNAL_OK:           {external_ok}")
    print(f"  UNKNOWN:               {unknown}")
    print(f"  IN_HOUSE_ONLY:         {in_house}")
    print(f"  With email:            {has_email}")
    print(f"  With phone:            {has_phone}")
    print(f"  With named contact:    {has_contact}")

    # Step 5: Write output
    out_path = os.path.join(PROJECT_DIR, "verified_leads_master.json")
    with open(out_path, "w") as f:
        json.dump(master, f, indent=2)
    print(f"\n[Output] Written: {out_path}")
    print(f"         {len(master)} records, {os.path.getsize(out_path) // 1024}KB")

    # Also write a summary CSV for easy viewing
    csv_path = os.path.join(PROJECT_DIR, "verified_leads_master.csv")
    fieldnames = ["venue_name", "website", "email", "phone", "contact_name",
                  "contact_role", "classification", "county", "score", "source"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in master:
            writer.writerow({k: rec.get(k, "") for k in fieldnames})
    print(f"         CSV: {csv_path}")

    print("\n[Done] verified_leads_master.json complete.")
    return master, dupe_count


if __name__ == "__main__":
    main()
