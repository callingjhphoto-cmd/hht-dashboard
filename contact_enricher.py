#!/usr/bin/env python3
"""
HHT Contact Enrichment Script
===============================
Reads venue data from existing CSVs and JSON files, scrapes venue websites
for missing contact information (email, phone, social media URLs).

Data sources:
  - hht_dryhire_verified.csv (111 venues, verified dry-hire leads)
  - hht_dryhire_leads.csv (110 venues, unverified leads)
  - new_leads_2026-03-18.json (scraped leads with some missing contacts)
  - venue_classifications.json (392 classified venues)

Usage:
  pip install requests beautifulsoup4
  python contact_enricher.py [--dry-run] [--limit N] [--source all|csv|json]

Output:
  - enriched_contacts_YYYY-MM-DD.csv (all venues with filled contact fields)
  - enrichment_log_YYYY-MM-DD.txt (stats: how many enriched, how many still empty)
"""

import argparse
import csv
import json
import logging
import os
import re
import sys
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Missing dependencies. Run: pip install requests beautifulsoup4")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent
DATA_DIR = Path(os.path.expanduser("~/Documents/Claude/data/hht"))
TODAY = datetime.now().strftime("%Y-%m-%d")

# Input files
CSV_VERIFIED = DATA_DIR / "hht_dryhire_verified.csv"
CSV_LEADS = DATA_DIR / "hht_dryhire_leads.csv"
JSON_NEW_LEADS = BASE_DIR / "new_leads_2026-03-18.json"
JSON_VENUE_CLASS = BASE_DIR / "venue_classifications.json"

# Output files
OUTPUT_CSV = BASE_DIR / f"enriched_contacts_{TODAY}.csv"
OUTPUT_LOG = BASE_DIR / f"enrichment_log_{TODAY}.txt"

# Rate limiting
MIN_DELAY = 3.0  # seconds between requests
MAX_DELAY = 5.0  # seconds between requests

# Request config
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}
REQUEST_TIMEOUT = 15  # seconds

# Regex patterns
EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE
)
PHONE_UK_PATTERN = re.compile(
    r"(?:(?:\+44\s?|0)(?:\d[\s\-]?){9,10}\d)",
    re.IGNORECASE
)
INSTAGRAM_PATTERN = re.compile(
    r"(?:instagram\.com|instagr\.am)/([a-zA-Z0-9_.]+)",
    re.IGNORECASE
)
FACEBOOK_PATTERN = re.compile(
    r"facebook\.com/([a-zA-Z0-9_.]+)",
    re.IGNORECASE
)
LINKEDIN_PATTERN = re.compile(
    r"linkedin\.com/(?:company|in)/([a-zA-Z0-9_.\-]+)",
    re.IGNORECASE
)
TWITTER_PATTERN = re.compile(
    r"(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)",
    re.IGNORECASE
)

# Emails to skip (generic/spam traps)
SKIP_EMAILS = {
    "user@domain.com", "email@example.com", "info@example.com",
    "noreply@", "no-reply@", "donotreply@",
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(OUTPUT_LOG, mode="w"),
    ]
)
log = logging.getLogger("hht_enricher")

# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------


def load_csv_venues(csv_path: Path) -> list[dict]:
    """Load venues from a CSV file."""
    venues = []
    if not csv_path.exists():
        log.warning(f"CSV not found: {csv_path}")
        return venues

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            venue = {
                "name": row.get("name", row.get("venue_name", "")).strip(),
                "website": row.get("website", "").strip(),
                "email": row.get("best_email", row.get("email", "")).strip(),
                "phone": row.get("phone", "").strip(),
                "instagram": row.get("instagram", "").strip(),
                "facebook": row.get("facebook", "").strip(),
                "linkedin": row.get("linkedin", "").strip(),
                "twitter": row.get("twitter", "").strip(),
                "area": row.get("area", row.get("county", "")).strip(),
                "address": row.get("address", row.get("location", "")).strip(),
                "bar_policy": row.get("bar_policy", row.get("classification", "")).strip(),
                "source_file": csv_path.name,
            }
            if venue["name"]:
                venues.append(venue)

    log.info(f"Loaded {len(venues)} venues from {csv_path.name}")
    return venues


def load_json_venues(json_path: Path, name_key: str = "name") -> list[dict]:
    """Load venues from a JSON file."""
    venues = []
    if not json_path.exists():
        log.warning(f"JSON not found: {json_path}")
        return venues

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle both array and {leads: [...]} formats
    if isinstance(data, dict) and "leads" in data:
        items = data["leads"]
    elif isinstance(data, list):
        items = data
    else:
        log.warning(f"Unexpected JSON structure in {json_path.name}")
        return venues

    for item in items:
        venue = {
            "name": item.get(name_key, item.get("venue_name", "")).strip(),
            "website": item.get("website", "").strip(),
            "email": item.get("email", item.get("best_email", "")).strip(),
            "phone": item.get("phone", "").strip(),
            "instagram": str(item.get("instagram", item.get("social_media", {}).get("instagram", "") if isinstance(item.get("social_media"), dict) else "")).strip(),
            "facebook": str(item.get("facebook", item.get("social_media", {}).get("facebook", "") if isinstance(item.get("social_media"), dict) else "")).strip(),
            "linkedin": str(item.get("linkedin", "")).strip(),
            "twitter": str(item.get("twitter", "")).strip(),
            "area": item.get("county", item.get("city", "")).strip(),
            "address": item.get("address", item.get("location", "")).strip(),
            "bar_policy": item.get("classification", item.get("bar_policy", "")).strip(),
            "source_file": json_path.name,
        }
        if venue["name"]:
            venues.append(venue)

    log.info(f"Loaded {len(venues)} venues from {json_path.name}")
    return venues


def deduplicate_venues(venues: list[dict]) -> list[dict]:
    """Remove duplicates based on normalised venue name."""
    seen = {}
    deduped = []
    for v in venues:
        key = re.sub(r"[^a-z0-9]", "", v["name"].lower())
        if key in seen:
            # Merge: prefer the record with more data
            existing = seen[key]
            for field in ["email", "phone", "instagram", "facebook", "linkedin", "twitter", "website"]:
                if not existing[field] and v[field]:
                    existing[field] = v[field]
        else:
            seen[key] = v
            deduped.append(v)

    log.info(f"Deduplicated: {len(venues)} -> {len(deduped)} unique venues")
    return deduped


# ---------------------------------------------------------------------------
# Web Scraping
# ---------------------------------------------------------------------------


def clean_url(url: str) -> str:
    """Clean and normalise a URL."""
    url = url.strip().rstrip("/")
    # Remove UTM params
    url = re.sub(r"\?utm_[^&]+(&utm_[^&]+)*$", "", url)
    url = re.sub(r"\?utm_[^&]+(&utm_[^&]+)*&", "?", url)
    if url and not url.startswith("http"):
        url = "https://" + url
    return url


def is_valid_email(email: str) -> bool:
    """Check if email looks valid and isn't a known dummy."""
    email = email.lower().strip()
    if not EMAIL_PATTERN.fullmatch(email):
        return False
    for skip in SKIP_EMAILS:
        if skip in email:
            return False
    # Skip image/asset emails
    if any(ext in email for ext in [".png", ".jpg", ".gif", ".svg", ".css", ".js"]):
        return False
    return True


def extract_emails_from_html(html: str, base_url: str = "") -> list[str]:
    """Extract email addresses from HTML content."""
    emails = set()

    # From mailto: links
    soup = BeautifulSoup(html, "html.parser")
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "mailto:" in href:
            email = href.split("mailto:")[-1].split("?")[0].strip()
            if is_valid_email(email):
                emails.add(email.lower())

    # From raw text
    for match in EMAIL_PATTERN.findall(html):
        if is_valid_email(match):
            emails.add(match.lower())

    return sorted(emails)


def extract_phones_from_html(html: str) -> list[str]:
    """Extract UK phone numbers from HTML content."""
    phones = set()

    # From tel: links
    soup = BeautifulSoup(html, "html.parser")
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "tel:" in href:
            phone = href.split("tel:")[-1].strip()
            phone = re.sub(r"[^\d+]", "", phone)
            if len(phone) >= 10:
                phones.add(phone)

    # From raw text
    for match in PHONE_UK_PATTERN.findall(html):
        phone = re.sub(r"[^\d+]", "", match)
        if len(phone) >= 10:
            phones.add(phone)

    return sorted(phones)


def extract_social_from_html(html: str) -> dict:
    """Extract social media URLs from HTML content."""
    social = {"instagram": "", "facebook": "", "linkedin": "", "twitter": ""}

    for match in INSTAGRAM_PATTERN.findall(html):
        if match.lower() not in ("p", "reel", "stories", "explore", "accounts"):
            social["instagram"] = f"instagram.com/{match}"
            break

    for match in FACEBOOK_PATTERN.findall(html):
        if match.lower() not in ("tr", "sharer.php", "share", "dialog", "plugins", "share.php"):
            social["facebook"] = f"facebook.com/{match}"
            break

    for match in LINKEDIN_PATTERN.findall(html):
        social["linkedin"] = f"linkedin.com/company/{match}"
        break

    for match in TWITTER_PATTERN.findall(html):
        if match.lower() not in ("share", "intent", "home"):
            social["twitter"] = f"x.com/{match}"
            break

    return social


def find_contact_pages(soup: BeautifulSoup, base_url: str) -> list[str]:
    """Find URLs likely to be contact/about pages."""
    contact_urls = []
    contact_keywords = ["contact", "about", "enquir", "get-in-touch", "reach-us"]

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].lower()
        text = a_tag.get_text().lower().strip()
        combined = href + " " + text
        if any(kw in combined for kw in contact_keywords):
            full_url = urljoin(base_url, a_tag["href"])
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                contact_urls.append(full_url)

    return list(set(contact_urls))[:3]  # Max 3 contact pages


def scrape_venue_contacts(website: str) -> dict:
    """
    Scrape a venue website for contact information.
    Returns dict with: emails, phones, social, pages_scraped
    """
    result = {
        "emails": [],
        "phones": [],
        "social": {"instagram": "", "facebook": "", "linkedin": "", "twitter": ""},
        "pages_scraped": 0,
        "error": None,
    }

    url = clean_url(website)
    if not url:
        result["error"] = "No URL"
        return result

    try:
        # 1. Scrape homepage
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
        html = resp.text
        result["pages_scraped"] += 1

        result["emails"].extend(extract_emails_from_html(html, url))
        result["phones"].extend(extract_phones_from_html(html))
        social = extract_social_from_html(html)
        for key, val in social.items():
            if val and not result["social"][key]:
                result["social"][key] = val

        # 2. Find and scrape contact pages
        soup = BeautifulSoup(html, "html.parser")
        contact_pages = find_contact_pages(soup, url)

        for contact_url in contact_pages:
            time.sleep(random.uniform(1.0, 2.0))  # Sub-delay for same domain
            try:
                resp2 = requests.get(contact_url, headers=HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
                if resp2.status_code == 200:
                    html2 = resp2.text
                    result["pages_scraped"] += 1
                    result["emails"].extend(extract_emails_from_html(html2, contact_url))
                    result["phones"].extend(extract_phones_from_html(html2))
                    social2 = extract_social_from_html(html2)
                    for key, val in social2.items():
                        if val and not result["social"][key]:
                            result["social"][key] = val
            except Exception:
                pass  # Skip failed sub-pages

        # Deduplicate
        result["emails"] = sorted(set(result["emails"]))
        result["phones"] = sorted(set(result["phones"]))

    except requests.exceptions.Timeout:
        result["error"] = "Timeout"
    except requests.exceptions.ConnectionError:
        result["error"] = "Connection failed"
    except requests.exceptions.HTTPError as e:
        result["error"] = f"HTTP {e.response.status_code}"
    except Exception as e:
        result["error"] = str(e)[:100]

    return result


# ---------------------------------------------------------------------------
# Enrichment Logic
# ---------------------------------------------------------------------------


def needs_enrichment(venue: dict) -> bool:
    """Check if a venue needs contact enrichment."""
    has_email = venue["email"] and is_valid_email(venue["email"])
    has_phone = venue["phone"] and len(re.sub(r"[^\d]", "", venue["phone"])) >= 10
    has_website = venue["website"] and venue["website"].startswith("http")

    # Only enrich if we have a website but missing email or phone
    if not has_website:
        return False
    if has_email and has_phone:
        return False
    return True


def enrich_venue(venue: dict) -> dict:
    """Enrich a single venue's contact details by scraping its website."""
    scraped = scrape_venue_contacts(venue["website"])

    enriched = venue.copy()
    enriched["enrichment_date"] = TODAY
    enriched["enrichment_error"] = scraped["error"] or ""
    enriched["pages_scraped"] = scraped["pages_scraped"]

    # Fill email if missing
    if not (venue["email"] and is_valid_email(venue["email"])):
        if scraped["emails"]:
            enriched["email"] = scraped["emails"][0]
            enriched["all_emails_found"] = "; ".join(scraped["emails"])
        else:
            enriched["all_emails_found"] = ""
    else:
        enriched["all_emails_found"] = venue["email"]

    # Fill phone if missing
    if not (venue["phone"] and len(re.sub(r"[^\d]", "", venue["phone"])) >= 10):
        if scraped["phones"]:
            enriched["phone"] = scraped["phones"][0]

    # Fill social media if missing
    for key in ["instagram", "facebook", "linkedin", "twitter"]:
        if not venue[key] and scraped["social"][key]:
            enriched[key] = scraped["social"][key]

    return enriched


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="HHT Contact Enrichment Script")
    parser.add_argument("--dry-run", action="store_true", help="Don't scrape, just report what would be enriched")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of venues to enrich (0 = all)")
    parser.add_argument("--source", choices=["all", "csv", "json"], default="all", help="Which data sources to load")
    args = parser.parse_args()

    log.info("=" * 60)
    log.info("HHT Contact Enrichment Script")
    log.info(f"Date: {TODAY}")
    log.info("=" * 60)

    # Load all venues
    all_venues = []

    if args.source in ("all", "csv"):
        all_venues.extend(load_csv_venues(CSV_VERIFIED))
        all_venues.extend(load_csv_venues(CSV_LEADS))

    if args.source in ("all", "json"):
        all_venues.extend(load_json_venues(JSON_NEW_LEADS))
        all_venues.extend(load_json_venues(JSON_VENUE_CLASS, name_key="venue_name"))

    # Deduplicate
    venues = deduplicate_venues(all_venues)

    # Stats before enrichment
    total = len(venues)
    with_email = sum(1 for v in venues if v["email"] and is_valid_email(v["email"]))
    with_phone = sum(1 for v in venues if v["phone"] and len(re.sub(r"[^\d]", "", v["phone"])) >= 10)
    with_website = sum(1 for v in venues if v["website"] and v["website"].startswith("http"))

    log.info(f"\n--- PRE-ENRICHMENT STATS ---")
    log.info(f"Total unique venues: {total}")
    log.info(f"With valid email: {with_email} ({100*with_email/total:.1f}%)")
    log.info(f"With valid phone: {with_phone} ({100*with_phone/total:.1f}%)")
    log.info(f"With website: {with_website} ({100*with_website/total:.1f}%)")

    # Find venues needing enrichment
    to_enrich = [v for v in venues if needs_enrichment(v)]
    log.info(f"Venues needing enrichment: {to_enrich.__len__()} (have website but missing email/phone)")

    if args.limit > 0:
        to_enrich = to_enrich[:args.limit]
        log.info(f"Limited to first {args.limit} venues")

    if args.dry_run:
        log.info("\n--- DRY RUN MODE ---")
        log.info(f"Would enrich {len(to_enrich)} venues. Exiting.")
        for v in to_enrich[:20]:
            log.info(f"  - {v['name']} | {v['website']} | email: {'YES' if v['email'] else 'MISSING'} | phone: {'YES' if v['phone'] else 'MISSING'}")
        return

    # Enrich venues
    log.info(f"\n--- STARTING ENRICHMENT ---")
    enriched_count = 0
    email_found = 0
    phone_found = 0
    errors = 0

    enriched_lookup = {}

    for i, venue in enumerate(to_enrich):
        log.info(f"[{i+1}/{len(to_enrich)}] Scraping: {venue['name']} ({venue['website'][:50]})")

        enriched = enrich_venue(venue)
        key = re.sub(r"[^a-z0-9]", "", venue["name"].lower())
        enriched_lookup[key] = enriched

        if enriched["enrichment_error"]:
            log.warning(f"  ERROR: {enriched['enrichment_error']}")
            errors += 1
        else:
            new_email = enriched["email"] != venue["email"] and enriched["email"]
            new_phone = enriched["phone"] != venue["phone"] and enriched["phone"]

            if new_email:
                email_found += 1
                log.info(f"  FOUND EMAIL: {enriched['email']}")
            if new_phone:
                phone_found += 1
                log.info(f"  FOUND PHONE: {enriched['phone']}")
            if new_email or new_phone:
                enriched_count += 1
            else:
                log.info(f"  No new contacts found (scraped {enriched['pages_scraped']} pages)")

        # Rate limit
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        time.sleep(delay)

    # Apply enrichments back to main list
    for venue in venues:
        key = re.sub(r"[^a-z0-9]", "", venue["name"].lower())
        if key in enriched_lookup:
            enriched = enriched_lookup[key]
            for field in ["email", "phone", "instagram", "facebook", "linkedin", "twitter",
                          "enrichment_date", "enrichment_error", "pages_scraped", "all_emails_found"]:
                venue[field] = enriched.get(field, venue.get(field, ""))

    # Stats after enrichment
    post_email = sum(1 for v in venues if v.get("email") and is_valid_email(v["email"]))
    post_phone = sum(1 for v in venues if v.get("phone") and len(re.sub(r"[^\d]", "", v["phone"])) >= 10)

    log.info(f"\n--- POST-ENRICHMENT STATS ---")
    log.info(f"Venues enriched: {enriched_count}")
    log.info(f"New emails found: {email_found}")
    log.info(f"New phones found: {phone_found}")
    log.info(f"Scrape errors: {errors}")
    log.info(f"Emails: {with_email} -> {post_email} (+{post_email - with_email})")
    log.info(f"Phones: {with_phone} -> {post_phone} (+{post_phone - with_phone})")
    log.info(f"Still missing email: {total - post_email}")
    log.info(f"Still missing phone: {total - post_phone}")

    # Write output CSV
    fieldnames = [
        "name", "area", "address", "website", "email", "all_emails_found",
        "phone", "instagram", "facebook", "linkedin", "twitter",
        "bar_policy", "source_file", "enrichment_date", "enrichment_error", "pages_scraped"
    ]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for venue in venues:
            writer.writerow(venue)

    log.info(f"\nOutput written to: {OUTPUT_CSV}")
    log.info(f"Log written to: {OUTPUT_LOG}")
    log.info("Done.")


if __name__ == "__main__":
    main()
