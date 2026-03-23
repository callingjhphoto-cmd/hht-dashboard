#!/usr/bin/env python3
"""
HHT Lead Generation Scraper v2
================================
Scrapes potential leads for Heads, Hearts & Tails mobile cocktail/event bartending.

Targets:
  1. Wedding venues
  2. Corporate event spaces
  3. Hotels without in-house cocktail capability
  4. PR/marketing agencies (brand activations)
  5. Festival organisers

Cities: London, Manchester, Birmingham, Edinburgh, Bristol

Data sources:
  - Google Maps (via SerpAPI or ScraperAPI)
  - Wedding directories (Hitched, Bridebook)
  - Companies House API (new hospitality businesses)
  - Google search enrichment

Usage:
  pip install requests beautifulsoup4 aiohttp
  python lead_scraper_v2.py

Environment variables required:
  SERPAPI_KEY    — SerpAPI key for Google Maps/Search results
  (optional) COMPANIES_HOUSE_KEY — Companies House API key for new business detection
"""

import json
import os
import re
import time
import hashlib
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")
COMPANIES_HOUSE_KEY = os.environ.get("COMPANIES_HOUSE_KEY", "")

CITIES = ["London", "Manchester", "Birmingham", "Edinburgh", "Bristol"]

LEAD_TYPES = {
    "wedding": [
        "wedding venues",
        "wedding reception venues",
        "barn wedding venues",
        "outdoor wedding venues",
        "country house wedding venues",
    ],
    "corporate": [
        "corporate event spaces",
        "conference venues",
        "corporate party venues",
        "team building venues",
        "corporate hospitality venues",
    ],
    "hotel": [
        "boutique hotels with event space",
        "hotels with function rooms",
        "new hotels",
        "luxury hotels with event facilities",
    ],
    "pr_agency": [
        "PR agencies brand activations",
        "experiential marketing agencies",
        "event marketing agencies",
        "brand activation agencies",
    ],
    "festival": [
        "festival organisers",
        "music festival organisers",
        "food festival organisers",
        "outdoor event organisers",
        "street food festival organisers",
    ],
}

# Keywords that suggest no in-house bar (positive signal for HHT)
NO_BAR_KEYWORDS = [
    "byob", "bring your own", "dry hire", "no bar",
    "outside catering", "external caterers welcome",
    "no in-house", "blank canvas", "self-catering",
    "corkage", "external bar", "bar not included",
]

# Keywords suggesting they already have cocktail services (negative signal)
HAS_BAR_KEYWORDS = [
    "in-house bar", "our cocktail menu", "resident bartender",
    "house mixologist", "cocktail lounge", "full bar service included",
]

EVENTS_KEYWORDS = [
    "events", "hire", "private hire", "weddings", "corporate events",
    "parties", "functions", "celebrations", "book an event",
    "event enquiry", "private dining",
]

OUTPUT_DIR = Path(__file__).parent
OUTPUT_FILE = OUTPUT_DIR / "scraped_leads.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("hht_scraper")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Lead:
    name: str
    address: str = ""
    city: str = ""
    website: str = ""
    phone: str = ""
    email: str = ""
    lead_type: str = ""          # wedding / corporate / hotel / pr_agency / festival
    estimated_capacity: int = 0
    social_media: dict = field(default_factory=dict)  # {instagram, facebook, linkedin, twitter}
    has_events_section: bool = False
    has_in_house_bar: bool = False
    no_bar_mentioned: bool = False
    recently_opened: bool = False
    data_sources: list = field(default_factory=list)
    raw_description: str = ""
    scraped_at: str = ""
    score: int = 0

    def compute_score(self) -> int:
        """Lead scoring system."""
        s = 0
        if self.website:
            s += 1
        if self.has_events_section:
            s += 2
        if self.no_bar_mentioned and not self.has_in_house_bar:
            s += 3
        if self.recently_opened:
            s += 2
        if self.estimated_capacity >= 200:
            s += 2
        self.score = s
        return s

    def uid(self) -> str:
        raw = f"{self.name.lower().strip()}|{self.city.lower().strip()}"
        return hashlib.md5(raw.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Scraping helpers
# ---------------------------------------------------------------------------

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
})


def serpapi_google_maps(query: str, city: str, limit: int = 20) -> list[dict]:
    """Search Google Maps via SerpAPI and return place results."""
    if not SERPAPI_KEY:
        log.warning("No SERPAPI_KEY set — skipping Google Maps search for '%s in %s'", query, city)
        return []

    params = {
        "engine": "google_maps",
        "q": f"{query} in {city}",
        "type": "search",
        "api_key": SERPAPI_KEY,
        "num": limit,
    }
    try:
        resp = SESSION.get("https://serpapi.com/search.json", params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("local_results", [])
    except Exception as e:
        log.error("SerpAPI Maps error: %s", e)
        return []


def serpapi_google_search(query: str, limit: int = 10) -> list[dict]:
    """Regular Google search via SerpAPI."""
    if not SERPAPI_KEY:
        return []

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": limit,
    }
    try:
        resp = SESSION.get("https://serpapi.com/search.json", params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("organic_results", [])
    except Exception as e:
        log.error("SerpAPI Search error: %s", e)
        return []


def scrape_hitched(city: str, max_pages: int = 3) -> list[dict]:
    """Scrape wedding venues from Hitched.co.uk."""
    results = []
    city_slug = city.lower().replace(" ", "-")

    for page in range(1, max_pages + 1):
        url = f"https://www.hitched.co.uk/wedding-venues/{city_slug}/"
        if page > 1:
            url += f"?page={page}"

        try:
            resp = SESSION.get(url, timeout=15)
            if resp.status_code != 200:
                break
            soup = BeautifulSoup(resp.text, "html.parser")

            # Hitched venue cards
            cards = soup.select("div.vendor-tile, article.vendor-card, div[data-testid='vendor-card']")
            if not cards:
                # fallback: look for any venue-like links
                cards = soup.select("a[href*='/wedding-venues/']")

            for card in cards:
                name_el = card.select_one("h2, h3, .vendor-tile__title, span.vendor-name")
                name = name_el.get_text(strip=True) if name_el else ""
                if not name:
                    if card.name == "a":
                        name = card.get_text(strip=True)
                    if not name:
                        continue

                link_el = card.select_one("a[href]") if card.name != "a" else card
                link = link_el.get("href", "") if link_el else ""
                if link and not link.startswith("http"):
                    link = "https://www.hitched.co.uk" + link

                results.append({
                    "name": name,
                    "source_url": link,
                    "source": "hitched.co.uk",
                })

            time.sleep(1.5)
        except Exception as e:
            log.error("Hitched scrape error (%s p%d): %s", city, page, e)
            break

    return results


def scrape_bridebook(city: str) -> list[dict]:
    """Scrape wedding venues from Bridebook."""
    results = []
    city_slug = city.lower().replace(" ", "-")
    url = f"https://bridebook.com/uk/wedding-venues/{city_slug}"

    try:
        resp = SESSION.get(url, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select("div[class*='VenueCard'], div[class*='venue-card'], a[href*='/venues/']")
            for card in cards:
                name_el = card.select_one("h2, h3, span[class*='name'], p[class*='name']")
                name = name_el.get_text(strip=True) if name_el else ""
                if not name and card.name == "a":
                    name = card.get_text(strip=True)
                if not name:
                    continue

                link_el = card.select_one("a[href]") if card.name != "a" else card
                link = link_el.get("href", "") if link_el else ""
                if link and not link.startswith("http"):
                    link = "https://bridebook.com" + link

                results.append({
                    "name": name,
                    "source_url": link,
                    "source": "bridebook.com",
                })
    except Exception as e:
        log.error("Bridebook scrape error (%s): %s", city, e)

    return results


def scrape_companies_house_new(sic_codes: list[str], city: str, months_back: int = 12) -> list[dict]:
    """Find recently incorporated hospitality companies via Companies House API."""
    if not COMPANIES_HOUSE_KEY:
        log.info("No COMPANIES_HOUSE_KEY — skipping new company detection for %s", city)
        return []

    results = []
    cutoff = datetime.now() - timedelta(days=months_back * 30)

    for sic in sic_codes:
        try:
            resp = SESSION.get(
                "https://api.company-information.service.gov.uk/advanced-search/companies",
                params={
                    "sic_codes": sic,
                    "location": city,
                    "incorporated_from": cutoff.strftime("%Y-%m-%d"),
                    "size": 50,
                },
                auth=(COMPANIES_HOUSE_KEY, ""),
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("items", []):
                    addr = item.get("registered_office_address", {})
                    results.append({
                        "name": item.get("company_name", ""),
                        "address": ", ".join(filter(None, [
                            addr.get("address_line_1"),
                            addr.get("address_line_2"),
                            addr.get("locality"),
                            addr.get("postal_code"),
                        ])),
                        "incorporated": item.get("date_of_creation", ""),
                        "source": "companies_house",
                    })
            time.sleep(0.6)
        except Exception as e:
            log.error("Companies House error (SIC %s, %s): %s", sic, city, e)

    return results


# ---------------------------------------------------------------------------
# Enrichment — scrape a venue's own website for deeper intel
# ---------------------------------------------------------------------------

def enrich_from_website(lead: Lead) -> Lead:
    """Visit the venue website and look for contact info, events pages, bar info."""
    if not lead.website:
        return lead

    try:
        resp = SESSION.get(lead.website, timeout=10, allow_redirects=True)
        if resp.status_code != 200:
            return lead

        text = resp.text.lower()
        soup = BeautifulSoup(resp.text, "html.parser")

        # --- Extract email ---
        if not lead.email:
            email_matches = re.findall(
                r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}", resp.text
            )
            # Filter out common non-contact emails
            filtered = [
                e for e in email_matches
                if not any(x in e.lower() for x in ["sentry", "webpack", "example", "wixpress", "test"])
            ]
            if filtered:
                lead.email = filtered[0]

        # --- Extract phone ---
        if not lead.phone:
            phone_matches = re.findall(
                r"(?:(?:\+44|0)\s*(?:\d[\s-]*){9,10})", resp.text
            )
            if phone_matches:
                lead.phone = re.sub(r"\s+", " ", phone_matches[0].strip())

        # --- Social media ---
        for link_tag in soup.find_all("a", href=True):
            href = link_tag["href"].lower()
            if "instagram.com/" in href and "instagram" not in lead.social_media:
                lead.social_media["instagram"] = link_tag["href"]
            elif "facebook.com/" in href and "facebook" not in lead.social_media:
                lead.social_media["facebook"] = link_tag["href"]
            elif "linkedin.com/" in href and "linkedin" not in lead.social_media:
                lead.social_media["linkedin"] = link_tag["href"]
            elif "twitter.com/" in href or "x.com/" in href:
                if "twitter" not in lead.social_media:
                    lead.social_media["twitter"] = link_tag["href"]

        # --- Events section detection ---
        nav_links = soup.find_all("a", href=True)
        for a in nav_links:
            link_text = a.get_text(strip=True).lower()
            link_href = a["href"].lower()
            if any(kw in link_text or kw in link_href for kw in EVENTS_KEYWORDS):
                lead.has_events_section = True
                break

        # --- In-house bar detection ---
        for kw in NO_BAR_KEYWORDS:
            if kw in text:
                lead.no_bar_mentioned = True
                break

        for kw in HAS_BAR_KEYWORDS:
            if kw in text:
                lead.has_in_house_bar = True
                break

        # --- Capacity detection ---
        cap_matches = re.findall(
            r"(?:capacity|seats?|holds?|accommodates?|up\s+to)\s*[:\s]*(\d{2,4})\s*(?:guests?|people|seated|standing)?",
            text,
        )
        if cap_matches:
            lead.estimated_capacity = max(int(c) for c in cap_matches)

    except Exception as e:
        log.debug("Enrichment error for %s: %s", lead.website, e)

    return lead


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def google_maps_to_lead(place: dict, lead_type: str, city: str, query: str) -> Lead:
    """Convert a SerpAPI Google Maps result into a Lead."""
    addr = place.get("address", "")
    website = place.get("website", "") or ""

    lead = Lead(
        name=place.get("title", place.get("name", "")),
        address=addr,
        city=city,
        website=website,
        phone=place.get("phone", "") or "",
        lead_type=lead_type,
        data_sources=[f"google_maps:{query}"],
        raw_description=place.get("description", "") or place.get("snippet", "") or "",
        scraped_at=datetime.utcnow().isoformat(),
    )

    # GPS coordinates sometimes present
    gps = place.get("gps_coordinates", {})
    if gps:
        lead.data_sources.append(f"gps:{gps.get('latitude','')},{gps.get('longitude','')}")

    return lead


def directory_to_lead(item: dict, city: str) -> Lead:
    """Convert a wedding directory result into a Lead."""
    return Lead(
        name=item.get("name", ""),
        city=city,
        website=item.get("source_url", ""),
        lead_type="wedding",
        data_sources=[item.get("source", "directory")],
        scraped_at=datetime.utcnow().isoformat(),
    )


def run_scraper() -> list[Lead]:
    """Main scraper orchestration."""
    all_leads: dict[str, Lead] = {}  # uid -> Lead (dedup)

    for city in CITIES:
        log.info("=== Scraping city: %s ===", city)

        # --- 1. Google Maps searches ---
        for lead_type, queries in LEAD_TYPES.items():
            for query in queries:
                log.info("  Google Maps: '%s' in %s", query, city)
                places = serpapi_google_maps(query, city)
                for place in places:
                    lead = google_maps_to_lead(place, lead_type, city, query)
                    uid = lead.uid()
                    if uid not in all_leads:
                        all_leads[uid] = lead
                    else:
                        # merge sources
                        existing = all_leads[uid]
                        existing.data_sources.extend(lead.data_sources)
                        if not existing.website and lead.website:
                            existing.website = lead.website
                time.sleep(0.5)

        # --- 2. Wedding directories ---
        log.info("  Hitched.co.uk: %s", city)
        for item in scrape_hitched(city):
            lead = directory_to_lead(item, city)
            uid = lead.uid()
            if uid not in all_leads:
                all_leads[uid] = lead
            else:
                all_leads[uid].data_sources.append("hitched.co.uk")

        log.info("  Bridebook: %s", city)
        for item in scrape_bridebook(city):
            lead = directory_to_lead(item, city)
            uid = lead.uid()
            if uid not in all_leads:
                all_leads[uid] = lead
            else:
                all_leads[uid].data_sources.append("bridebook.com")

        # --- 3. Companies House (new hospitality businesses) ---
        # SIC codes: 56210 (event catering), 56302 (pubs), 55100 (hotels), 93290 (entertainment)
        hospitality_sics = ["56210", "55100", "56302", "93290"]
        log.info("  Companies House new businesses: %s", city)
        for item in scrape_companies_house_new(hospitality_sics, city, months_back=12):
            lead = Lead(
                name=item["name"],
                address=item.get("address", ""),
                city=city,
                lead_type="corporate",  # new companies default to corporate
                recently_opened=True,
                data_sources=["companies_house"],
                scraped_at=datetime.utcnow().isoformat(),
            )
            uid = lead.uid()
            if uid not in all_leads:
                all_leads[uid] = lead

    # --- 4. Enrich all leads from their websites ---
    leads_list = list(all_leads.values())
    log.info("Enriching %d leads from websites...", len(leads_list))
    for i, lead in enumerate(leads_list):
        if lead.website:
            log.info("  [%d/%d] Enriching: %s", i + 1, len(leads_list), lead.name)
            enrich_from_website(lead)
            time.sleep(0.8)

    # --- 5. Score all leads ---
    for lead in leads_list:
        lead.compute_score()

    # Sort by score descending
    leads_list.sort(key=lambda x: x.score, reverse=True)

    return leads_list


def save_leads(leads: list[Lead], filepath: Path):
    """Save leads to JSON."""
    output = {
        "metadata": {
            "scraped_at": datetime.utcnow().isoformat(),
            "total_leads": len(leads),
            "cities": CITIES,
            "lead_types": list(LEAD_TYPES.keys()),
            "scoring": {
                "has_website": "+1",
                "has_events_section": "+2",
                "no_in_house_bar": "+3",
                "recently_opened": "+2",
                "high_capacity_200_plus": "+2",
            },
        },
        "leads": [asdict(lead) for lead in leads],
        "summary": {
            "by_city": {},
            "by_type": {},
            "by_score": {
                "hot (7+)": len([l for l in leads if l.score >= 7]),
                "warm (4-6)": len([l for l in leads if 4 <= l.score < 7]),
                "cool (1-3)": len([l for l in leads if 1 <= l.score < 4]),
                "cold (0)": len([l for l in leads if l.score == 0]),
            },
        },
    }

    # City breakdown
    for city in CITIES:
        city_leads = [l for l in leads if l.city == city]
        output["summary"]["by_city"][city] = len(city_leads)

    # Type breakdown
    for lt in LEAD_TYPES:
        type_leads = [l for l in leads if l.lead_type == lt]
        output["summary"]["by_type"][lt] = len(type_leads)

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(output, f, indent=2, default=str)

    log.info("Saved %d leads to %s", len(leads), filepath)


# ---------------------------------------------------------------------------
# Standalone Google search enrichment (bonus — find venue emails/socials)
# ---------------------------------------------------------------------------

def google_search_enrich(lead: Lead) -> Lead:
    """Use a Google search to find missing contact details."""
    if lead.email and lead.phone:
        return lead

    query = f"{lead.name} {lead.city} contact email phone"
    results = serpapi_google_search(query, limit=3)

    for result in results:
        snippet = result.get("snippet", "")

        if not lead.email:
            emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}", snippet)
            if emails:
                lead.email = emails[0]

        if not lead.phone:
            phones = re.findall(r"(?:(?:\+44|0)\s*(?:\d[\s-]*){9,10})", snippet)
            if phones:
                lead.phone = phones[0].strip()

        if not lead.website:
            link = result.get("link", "")
            if link and "google" not in link and "facebook" not in link:
                lead.website = link

    return lead


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    log.info("HHT Lead Scraper v2 starting...")
    log.info("Cities: %s", ", ".join(CITIES))
    log.info("Lead types: %s", ", ".join(LEAD_TYPES.keys()))

    if not SERPAPI_KEY:
        log.warning(
            "SERPAPI_KEY not set. Google Maps/Search scraping will be skipped. "
            "Set it with: export SERPAPI_KEY='your_key_here'"
        )

    leads = run_scraper()

    # Optional: deeper enrichment via Google Search for leads missing contact info
    if SERPAPI_KEY:
        incomplete = [l for l in leads if not l.email or not l.phone]
        log.info("Google Search enrichment for %d incomplete leads...", len(incomplete))
        for i, lead in enumerate(incomplete[:50]):  # cap at 50 to conserve API calls
            log.info("  [%d/%d] Searching: %s", i + 1, min(len(incomplete), 50), lead.name)
            google_search_enrich(lead)
            lead.compute_score()  # re-score after enrichment
            time.sleep(1)

    # Re-sort after enrichment
    leads.sort(key=lambda x: x.score, reverse=True)

    save_leads(leads, OUTPUT_FILE)

    # Print top leads
    print("\n" + "=" * 70)
    print("TOP 20 LEADS BY SCORE")
    print("=" * 70)
    for i, lead in enumerate(leads[:20]):
        print(f"\n{i+1}. [{lead.score}/10] {lead.name}")
        print(f"   Type: {lead.lead_type} | City: {lead.city}")
        print(f"   Website: {lead.website or 'N/A'}")
        print(f"   Email: {lead.email or 'N/A'} | Phone: {lead.phone or 'N/A'}")
        print(f"   Capacity: {lead.estimated_capacity or 'Unknown'}")
        print(f"   Events section: {lead.has_events_section} | No bar: {lead.no_bar_mentioned}")
        print(f"   Sources: {', '.join(lead.data_sources)}")

    print(f"\nTotal leads scraped: {len(leads)}")
    print(f"Output saved to: {OUTPUT_FILE}")
