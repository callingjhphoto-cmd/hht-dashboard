#!/usr/bin/env python3
"""
HHT Venue Migration Script
===========================
Reads enriched_venues.json + venue_classifications.json,
calculates priority scores, and outputs:
  1. SQL INSERT statements for Supabase import
  2. CSV file for bulk import
  3. SQLite database for local API use

Usage:
  python migrate_venues.py                    # Generate all outputs
  python migrate_venues.py --format sql       # SQL only
  python migrate_venues.py --format csv       # CSV only
  python migrate_venues.py --format sqlite    # SQLite only
"""

import argparse
import csv
import json
import os
import re
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

HHT_DIR = Path.home() / "Documents/Claude/projects/hht"
DB_DIR = HHT_DIR / "database"
ENRICHED_FILE = HHT_DIR / "enriched_venues.json"
CLASSIFICATIONS_FILE = HHT_DIR / "venue_classifications.json"
OUTPUT_SQL = DB_DIR / "import_venues.sql"
OUTPUT_CSV = DB_DIR / "import_venues.csv"
OUTPUT_SQLITE = DB_DIR / "hht.db"


# ---------------------------------------------------------------------------
# Priority Scorer
# ---------------------------------------------------------------------------

def calculate_score(venue: dict) -> int:
    """
    Score venues 0-100 based on conversion potential.
    Higher score = Joe should call sooner.

    Scoring factors:
    - Classification (DRY_HIRE=30, EXTERNAL_OK=20, IN_HOUSE_ONLY=0)
    - Has specific email (events@/weddings@ = 15, named = 10, info@ = 5)
    - Has phone number (+10)
    - Has events section on website (+10)
    - Has Instagram (+5)
    - Capacity sweet spot 100-300 (+10), 300+ (+5)
    - Has website (+5)
    - Category bonus: Barn Venue/Country Estate (+5)
    """
    score = 0

    # Classification weight (biggest factor)
    cls = venue.get("classification", "")
    if cls == "DRY_HIRE":
        score += 30
    elif cls == "EXTERNAL_OK":
        score += 20

    # Email quality
    email = venue.get("email", "").lower()
    if email:
        if any(prefix in email for prefix in ["events@", "weddings@", "wedding@", "hire@", "functions@"]):
            score += 15  # Specific department = high intent
        elif not email.startswith("info@") and not email.startswith("enquir"):
            score += 10  # Named/specific email
        else:
            score += 5   # Generic but still an email

    # Phone
    if venue.get("phone"):
        score += 10

    # Events section
    if venue.get("has_events_section"):
        score += 10

    # Social media
    if venue.get("instagram"):
        score += 5

    # Capacity
    cap = venue.get("capacity", 0) or 0
    if 100 <= cap <= 300:
        score += 10  # Sweet spot for cocktail bar events
    elif cap > 300:
        score += 5   # Large but still good

    # Website
    if venue.get("website"):
        score += 5

    # Category bonus
    cat = venue.get("category", "")
    if cat in ("Barn Venue", "Country Estate"):
        score += 5

    return min(score, 100)


def calculate_tier(score: int, classification: str) -> str:
    """
    Assign tier based on score.
    From Gemini research: 80+ = call immediately, 50-79 = high priority
    """
    if score >= 80:
        return "CALL_NOW"
    elif score >= 60:
        return "HIGH_PRIORITY"
    elif score >= 40:
        return "STANDARD"
    elif score >= 20 and classification in ("DRY_HIRE", "EXTERNAL_OK"):
        return "NURTURE"
    else:
        return "LOW"


# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------

def load_all_venues() -> list[dict]:
    """Merge enriched data with classifications."""

    # Load classifications (base data for all 392 venues)
    with open(CLASSIFICATIONS_FILE) as f:
        classifications = {v["venue_name"].lower().strip(): v for v in json.load(f)}

    # Load enriched data (venues with scraped contact info)
    enriched = {}
    if ENRICHED_FILE.exists():
        with open(ENRICHED_FILE) as f:
            for v in json.load(f):
                enriched[v["venue_name"].lower().strip()] = v

    # Merge: start with all classified venues, overlay enriched data
    venues = []
    seen = set()

    for name_lower, cls_data in classifications.items():
        if name_lower in seen:
            continue
        seen.add(name_lower)

        venue = {
            "name": cls_data.get("venue_name", ""),
            "county": cls_data.get("county", ""),
            "category": cls_data.get("category", ""),
            "classification": cls_data.get("classification", ""),
            "classification_reason": cls_data.get("classification_reason", ""),
            "capacity": cls_data.get("capacity", 0),
            "website": "",
            "email": "",
            "all_emails": [],
            "phone": "",
            "all_phones": [],
            "instagram": "",
            "facebook": "",
            "has_events_section": False,
            "enrichment_date": None,
            "enrichment_error": "",
            "pages_scraped": 0,
            "source": "venue_classifications",
        }

        # Overlay enriched data if available
        if name_lower in enriched:
            e = enriched[name_lower]
            venue["website"] = e.get("website", "")
            venue["email"] = e.get("email", "")
            venue["all_emails"] = e.get("all_emails", [])
            venue["phone"] = e.get("phone", "")
            venue["all_phones"] = e.get("all_phones", [])
            venue["instagram"] = e.get("instagram", "")
            venue["facebook"] = e.get("facebook", "")
            venue["has_events_section"] = e.get("has_events_section", False)
            venue["enrichment_date"] = e.get("enrichment_date")
            venue["enrichment_error"] = e.get("enrichment_error", "")
            venue["pages_scraped"] = e.get("pages_scraped", 0)
            venue["source"] = "enriched"

        # Calculate score and tier
        venue["score"] = calculate_score(venue)
        venue["tier"] = calculate_tier(venue["score"], venue["classification"])

        venues.append(venue)

    # Sort by score descending
    venues.sort(key=lambda v: -v["score"])
    return venues


# ---------------------------------------------------------------------------
# Output Generators
# ---------------------------------------------------------------------------

def escape_sql(val) -> str:
    """Escape a value for SQL insertion."""
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, list):
        # PostgreSQL array literal
        items = ", ".join(f"'{str(v).replace(chr(39), chr(39)+chr(39))}'" for v in val)
        return f"ARRAY[{items}]" if items else "ARRAY[]::TEXT[]"
    s = str(val).replace("'", "''")
    return f"'{s}'"


def generate_sql(venues: list[dict]):
    """Generate SQL INSERT file."""
    lines = [
        "-- HHT Venue Import",
        f"-- Generated: {datetime.now().isoformat()}",
        f"-- Total venues: {len(venues)}",
        "",
        "BEGIN;",
        "",
    ]

    for v in venues:
        lines.append(f"""INSERT INTO venues (name, county, category, classification, capacity, website, email, all_emails, phone, all_phones, instagram, facebook, has_events_section, score, tier, enrichment_date, enrichment_error, pages_scraped, source)
VALUES ({escape_sql(v['name'])}, {escape_sql(v['county'])}, {escape_sql(v['category'])}, {escape_sql(v['classification'])}, {escape_sql(v['capacity'])}, {escape_sql(v['website'])}, {escape_sql(v['email'])}, {escape_sql(v['all_emails'])}, {escape_sql(v['phone'])}, {escape_sql(v['all_phones'])}, {escape_sql(v['instagram'])}, {escape_sql(v['facebook'])}, {escape_sql(v['has_events_section'])}, {escape_sql(v['score'])}, {escape_sql(v['tier'])}, {escape_sql(v['enrichment_date'])}, {escape_sql(v['enrichment_error'])}, {escape_sql(v['pages_scraped'])}, {escape_sql(v['source'])});""")
        lines.append("")

    lines.append("COMMIT;")

    with open(OUTPUT_SQL, "w") as f:
        f.write("\n".join(lines))
    print(f"SQL written: {OUTPUT_SQL} ({len(venues)} venues)")


def generate_csv(venues: list[dict]):
    """Generate CSV for Supabase bulk import."""
    fields = [
        "name", "county", "category", "classification", "capacity",
        "website", "email", "phone", "instagram", "facebook",
        "has_events_section", "score", "tier", "enrichment_date", "source"
    ]

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for v in venues:
            row = {k: v.get(k, "") for k in fields}
            writer.writerow(row)

    print(f"CSV written: {OUTPUT_CSV} ({len(venues)} venues)")


def generate_sqlite(venues: list[dict]):
    """Generate SQLite database for local API."""
    if OUTPUT_SQLITE.exists():
        OUTPUT_SQLITE.unlink()

    conn = sqlite3.connect(str(OUTPUT_SQLITE))
    c = conn.cursor()

    # Create tables (SQLite-compatible version of schema)
    c.executescript("""
        CREATE TABLE venues (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            county TEXT,
            category TEXT,
            classification TEXT,
            classification_reason TEXT,
            capacity INTEGER,
            website TEXT,
            email TEXT,
            all_emails TEXT,
            phone TEXT,
            all_phones TEXT,
            instagram TEXT,
            facebook TEXT,
            has_events_section BOOLEAN DEFAULT 0,
            contact_name TEXT,
            notes TEXT,
            score INTEGER DEFAULT 0,
            tier TEXT,
            enrichment_date TEXT,
            enrichment_error TEXT,
            pages_scraped INTEGER DEFAULT 0,
            source TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE outreach (
            id TEXT PRIMARY KEY,
            venue_id TEXT NOT NULL REFERENCES venues(id),
            template_used TEXT,
            channel TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft',
            subject TEXT,
            body TEXT,
            sent_at TEXT,
            opened_at TEXT,
            replied_at TEXT,
            follow_up_1_at TEXT,
            follow_up_2_at TEXT,
            follow_up_3_at TEXT,
            response TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE bookings (
            id TEXT PRIMARY KEY,
            venue_id TEXT NOT NULL REFERENCES venues(id),
            event_date TEXT,
            event_type TEXT,
            guests INTEGER,
            package TEXT,
            value_gbp REAL,
            cost_gbp REAL,
            status TEXT DEFAULT 'enquiry',
            contact_name TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX idx_venues_classification ON venues(classification);
        CREATE INDEX idx_venues_tier ON venues(tier);
        CREATE INDEX idx_venues_county ON venues(county);
        CREATE INDEX idx_venues_score ON venues(score DESC);
        CREATE INDEX idx_outreach_venue_id ON outreach(venue_id);
        CREATE INDEX idx_outreach_status ON outreach(status);
        CREATE INDEX idx_bookings_venue_id ON bookings(venue_id);
        CREATE INDEX idx_bookings_status ON bookings(status);
    """)

    # Insert venues
    for v in venues:
        vid = str(uuid.uuid4())
        c.execute("""
            INSERT INTO venues (id, name, county, category, classification, classification_reason,
                capacity, website, email, all_emails, phone, all_phones,
                instagram, facebook, has_events_section, score, tier,
                enrichment_date, enrichment_error, pages_scraped, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vid, v["name"], v["county"], v["category"], v["classification"],
            v.get("classification_reason", ""),
            v["capacity"], v["website"], v["email"],
            json.dumps(v.get("all_emails", [])),
            v["phone"], json.dumps(v.get("all_phones", [])),
            v["instagram"], v["facebook"],
            1 if v["has_events_section"] else 0,
            v["score"], v["tier"],
            v.get("enrichment_date"), v.get("enrichment_error", ""),
            v.get("pages_scraped", 0), v.get("source", "")
        ))

    conn.commit()

    # Print stats
    c.execute("SELECT tier, COUNT(*) FROM venues GROUP BY tier ORDER BY COUNT(*) DESC")
    tiers = c.fetchall()
    c.execute("SELECT classification, COUNT(*) FROM venues GROUP BY classification")
    classes = c.fetchall()
    c.execute("SELECT COUNT(*) FROM venues WHERE email != '' AND email IS NOT NULL")
    with_email = c.fetchone()[0]

    conn.close()

    print(f"SQLite written: {OUTPUT_SQLITE} ({len(venues)} venues)")
    print(f"  By tier: {dict(tiers)}")
    print(f"  By classification: {dict(classes)}")
    print(f"  With email: {with_email}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="HHT Venue Migration")
    parser.add_argument("--format", choices=["sql", "csv", "sqlite", "all"], default="all")
    args = parser.parse_args()

    print("Loading venues...")
    venues = load_all_venues()
    print(f"Loaded {len(venues)} venues")

    # Print summary
    tiers = {}
    for v in venues:
        tiers[v["tier"]] = tiers.get(v["tier"], 0) + 1
    print(f"Tier distribution: {tiers}")

    with_email = sum(1 for v in venues if v.get("email"))
    with_phone = sum(1 for v in venues if v.get("phone"))
    print(f"With email: {with_email}, With phone: {with_phone}")

    if args.format in ("sql", "all"):
        generate_sql(venues)
    if args.format in ("csv", "all"):
        generate_csv(venues)
    if args.format in ("sqlite", "all"):
        generate_sqlite(venues)

    print("\nMigration complete!")


if __name__ == "__main__":
    main()
