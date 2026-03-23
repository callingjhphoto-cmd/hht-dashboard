#!/usr/bin/env python3
"""
HHT Outreach Manager — Automated Outreach Pipeline

Manages daily outreach to prioritised venue leads.
Tracks status, generates email drafts, logs all activity.

Commands:
    python3 outreach_manager.py status           — pipeline overview
    python3 outreach_manager.py today             — today's outreach tasks
    python3 outreach_manager.py send <venue_id>   — generate email draft for a venue
    python3 outreach_manager.py followup          — show venues due for follow-up
    python3 outreach_manager.py history           — recent outreach log
    python3 outreach_manager.py score             — re-score all venues and show top leads
"""

import json
import os
import sys
import hashlib
from datetime import datetime, timedelta
from collections import Counter

# Paths
BASE = os.path.expanduser("~/Documents/Claude/projects/hht")
OUTREACH_DIR = os.path.join(BASE, "outreach")
LOG_PATH = os.path.join(OUTREACH_DIR, "outreach_log.json")
GMAIL_SEND = os.path.expanduser("~/Documents/Claude/scripts/gmail_send.py")
SENDER_EMAIL = "james@huertas.co.uk"

# Daily batch size
DAILY_BATCH = 8

# Status progression
STATUSES = [
    "not_contacted",
    "email_sent",
    "followed_up_1",
    "followed_up_2",
    "nurture_month2",
    "nurture_month3",
    "responded",
    "booked",
    "declined",
    "no_email",   # venues without usable email
]

# Follow-up schedule (days after previous touch)
FOLLOWUP_1_DAYS = 3
FOLLOWUP_2_DAYS = 7
NURTURE_MONTH2_DAYS = 30   # 30 days after follow-up 2
NURTURE_MONTH3_DAYS = 30   # 30 days after month 2 nurture


def _venue_id(venue: dict) -> str:
    """Generate a stable ID for a venue based on name."""
    if venue.get("id"):
        return str(venue["id"])
    name = venue.get("name", "unknown")
    return hashlib.md5(name.encode()).hexdigest()[:8]


def _venue_name(venue: dict) -> str:
    return venue.get("name", venue.get("venue_name", "Unknown"))


def load_all_venues() -> list:
    """Load venues from all data sources, deduplicated by name."""
    all_venues = []
    seen_names = set()

    sources = [
        ("sample_leads.json", lambda d: d.get("leads", d) if isinstance(d, dict) else d),
        ("orphaned_clients_2026-03-18.json", lambda d: d),
        ("new_leads_2026-03-18.json", lambda d: d),
        ("enriched_leads_2026-03-19.json", lambda d: d),
        ("net_new_leads_2026-03-19.json", lambda d: d),
    ]

    for filename, extractor in sources:
        path = os.path.join(BASE, filename)
        if not os.path.exists(path):
            continue
        try:
            with open(path) as f:
                data = json.load(f)
            venues = extractor(data)
            if not isinstance(venues, list):
                continue
            for v in venues:
                name = _venue_name(v).lower().strip()
                if name not in seen_names and name != "unknown":
                    seen_names.add(name)
                    v["_source_file"] = filename
                    v["_venue_id"] = _venue_id(v)
                    all_venues.append(v)
        except (json.JSONDecodeError, KeyError):
            continue

    return all_venues


def load_log() -> dict:
    """Load outreach log. Structure: { venue_id: { status, events: [...] } }"""
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            return json.load(f)
    return {}


def save_log(log: dict):
    """Save outreach log."""
    os.makedirs(OUTREACH_DIR, exist_ok=True)
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)


def get_status(log: dict, venue_id: str) -> str:
    """Get current outreach status for a venue."""
    if venue_id in log:
        return log[venue_id].get("status", "not_contacted")
    return "not_contacted"


def log_event(log: dict, venue_id: str, venue_name: str, event_type: str, details: str = ""):
    """Log an outreach event."""
    if venue_id not in log:
        log[venue_id] = {
            "venue_name": venue_name,
            "status": "not_contacted",
            "events": [],
        }

    log[venue_id]["events"].append({
        "type": event_type,
        "timestamp": datetime.now().isoformat(),
        "details": details,
    })

    # Update status based on event
    status_map = {
        "initial_email": "email_sent",
        "followup_1": "followed_up_1",
        "followup_2": "followed_up_2",
        "nurture_month2": "nurture_month2",
        "nurture_month3": "nurture_month3",
        "response_received": "responded",
        "booking_confirmed": "booked",
        "declined": "declined",
    }
    if event_type in status_map:
        log[venue_id]["status"] = status_map[event_type]


def score_venues(venues: list) -> list:
    """Score all venues using priority_scorer."""
    sys.path.insert(0, OUTREACH_DIR)
    from priority_scorer import score_all
    return score_all(venues)


def get_todays_batch(venues: list, log: dict) -> list:
    """
    Select today's outreach batch:
    - Highest scored venues that haven't been contacted yet
    - Up to DAILY_BATCH venues
    - Must have a usable email address
    """
    scored = score_venues(venues)
    batch = []

    for v in scored:
        if len(batch) >= DAILY_BATCH:
            break

        vid = v["_venue_id"]
        status = get_status(log, vid)

        # Skip already contacted or no-email venues
        if status != "not_contacted":
            continue

        # Must have email
        email = str(v.get("email", "")).strip()
        if not email or email in ("NEEDS_ENRICHMENT", "UNABLE_TO_FIND", "CONTACT_FORM_ONLY") or "@" not in email:
            continue

        # Skip geo-filtered/archived
        if v.get("tier") == "ARCHIVE":
            continue

        batch.append(v)

    return batch


def get_followups(venues: list, log: dict) -> dict:
    """Find venues due for follow-up 1, follow-up 2, or nurture touches."""
    now = datetime.now()
    followups = {
        "followup_1": [],
        "followup_2": [],
        "nurture_month2": [],
        "nurture_month3": [],
    }

    venue_map = {v["_venue_id"]: v for v in venues}

    for vid, entry in log.items():
        status = entry.get("status", "not_contacted")
        events = entry.get("events", [])

        if not events:
            continue

        last_event = events[-1]
        last_time = datetime.fromisoformat(last_event["timestamp"])
        days_since = (now - last_time).days

        if status == "email_sent" and days_since >= FOLLOWUP_1_DAYS:
            venue = venue_map.get(vid, {"name": entry.get("venue_name", vid)})
            followups["followup_1"].append((venue, days_since))

        elif status == "followed_up_1" and days_since >= (FOLLOWUP_2_DAYS - FOLLOWUP_1_DAYS):
            venue = venue_map.get(vid, {"name": entry.get("venue_name", vid)})
            followups["followup_2"].append((venue, days_since))

        elif status == "followed_up_2" and days_since >= NURTURE_MONTH2_DAYS:
            venue = venue_map.get(vid, {"name": entry.get("venue_name", vid)})
            followups["nurture_month2"].append((venue, days_since))

        elif status == "nurture_month2" and days_since >= NURTURE_MONTH3_DAYS:
            venue = venue_map.get(vid, {"name": entry.get("venue_name", vid)})
            followups["nurture_month3"].append((venue, days_since))

    return followups


# ---------------------------------------------------------------------------
# COMMANDS
# ---------------------------------------------------------------------------

def cmd_status():
    """Show pipeline overview."""
    venues = load_all_venues()
    log = load_log()
    scored = score_venues(venues)

    # Count by outreach status
    status_counts = Counter()
    for v in scored:
        vid = v["_venue_id"]
        status_counts[get_status(log, vid)] += 1

    # Count venues with email
    with_email = sum(1 for v in venues if "@" in str(v.get("email", "")))
    without_email = len(venues) - with_email

    # Tier breakdown
    tier_counts = Counter(v.get("outreach_tier", "UNSCORED") for v in scored)

    print("=" * 60)
    print("  HHT OUTREACH PIPELINE — STATUS")
    print(f"  {datetime.now().strftime('%d %B %Y, %H:%M')}")
    print("=" * 60)

    print(f"\nTotal venues in database:    {len(venues)}")
    print(f"  With email:                {with_email}")
    print(f"  Without email:             {without_email}")

    print(f"\n{'--- OUTREACH STATUS ---':^40}")
    for status in STATUSES:
        count = status_counts.get(status, 0)
        bar = "#" * min(count, 40)
        if count > 0:
            print(f"  {status:<20} {count:>4}  {bar}")

    print(f"\n{'--- PRIORITY TIERS ---':^40}")
    for tier in ["CALL_NOW", "HIGH_PRIORITY", "STANDARD", "NURTURE", "LOW"]:
        count = tier_counts.get(tier, 0)
        if count > 0:
            print(f"  {tier:<20} {count:>4}")

    # Follow-ups due
    followups = get_followups(scored, log)
    fu1 = len(followups["followup_1"])
    fu2 = len(followups["followup_2"])
    if fu1 or fu2:
        print(f"\n{'--- FOLLOW-UPS DUE ---':^40}")
        if fu1:
            print(f"  Follow-up #1 due:      {fu1}")
        if fu2:
            print(f"  Follow-up #2 due:      {fu2}")

    print()


def cmd_today():
    """Show today's outreach tasks."""
    venues = load_all_venues()
    log = load_log()

    batch = get_todays_batch(venues, log)
    followups = get_followups(venues, log)

    print("=" * 70)
    print("  HHT OUTREACH — TODAY'S TASKS")
    print(f"  {datetime.now().strftime('%A %d %B %Y')}")
    print("=" * 70)

    if batch:
        print(f"\n  NEW OUTREACH ({len(batch)} venues):")
        print(f"  {'#':<4} {'Score':>5}  {'Tier':<16} {'Venue':<30} {'Email'}")
        print("  " + "-" * 85)
        for i, v in enumerate(batch, 1):
            name = _venue_name(v)[:29]
            email = str(v.get("email", ""))[:35]
            print(f"  {i:<4} {v['outreach_score']:>5}  {v['outreach_tier']:<16} {name:<30} {email}")

        print(f"\n  To send an email:  python3 outreach_manager.py send <venue_id>")
        print(f"  Venue IDs: {', '.join(v['_venue_id'] for v in batch)}")
    else:
        print("\n  No new outreach targets for today.")
        print("  (All eligible venues have been contacted or lack email addresses)")

    # Follow-ups
    fu1 = followups.get("followup_1", [])
    fu2 = followups.get("followup_2", [])

    if fu1:
        print(f"\n  FOLLOW-UP #1 DUE ({len(fu1)} venues — {FOLLOWUP_1_DAYS}+ days since initial):")
        for venue, days in fu1:
            print(f"    - {_venue_name(venue)} ({days} days ago)")

    if fu2:
        print(f"\n  FOLLOW-UP #2 DUE ({len(fu2)} venues — value-add email):")
        for venue, days in fu2:
            print(f"    - {_venue_name(venue)} ({days} days since follow-up #1)")

    print()


def cmd_send(venue_identifier: str):
    """Generate email draft for a venue."""
    venues = load_all_venues()
    log = load_log()
    scored = score_venues(venues)

    # Find venue by ID or name substring
    target = None
    for v in scored:
        if v["_venue_id"] == venue_identifier:
            target = v
            break
        if venue_identifier.lower() in _venue_name(v).lower():
            target = v
            break

    if not target:
        print(f"Venue not found: {venue_identifier}")
        print("Use 'python3 outreach_manager.py today' to see available venues.")
        return

    name = _venue_name(target)
    email = str(target.get("email", "")).strip()
    contact = target.get("contact_person", "there")
    location = target.get("county", target.get("city", target.get("location", "")))

    if not email or "@" not in email:
        print(f"No email address for {name}.")
        if target.get("phone"):
            print(f"Phone: {target['phone']}")
        if target.get("email") == "CONTACT_FORM_ONLY":
            print(f"This venue only accepts enquiries via their website contact form.")
        return

    # Select template and generate
    sys.path.insert(0, OUTREACH_DIR)
    from email_templates import select_template, get_template, get_ab_subjects
    from ab_testing import ABTestManager

    ab = ABTestManager()
    template_key = select_template(target)
    status = get_status(log, target["_venue_id"])

    # If already contacted, select appropriate follow-up/nurture template
    if status == "email_sent":
        template_key = "followup_1"
    elif status == "followed_up_1":
        template_key = "followup_2"
    elif status == "followed_up_2":
        template_key = "nurture_seasonal"
    elif status == "nurture_month2":
        template_key = "nurture_final"
    elif status in ("nurture_month3", "responded", "booked", "declined"):
        print(f"Venue {name} status is '{status}' — no further automated emails.")
        return

    # Get A/B variant for subject line
    variant = ab.get_variant(template_key, target["_venue_id"])

    # Show all subject variants
    all_subjects = get_ab_subjects(
        template_key,
        venue_name=name,
        contact_name=contact if contact else "there",
        location=location,
    )

    subject, body = get_template(
        template_key,
        variant=variant,
        venue_name=name,
        contact_name=contact if contact else "there",
        location=location,
        event_type=target.get("lead_type", target.get("type", "event")),
    )

    print("=" * 60)
    print(f"  EMAIL DRAFT — {name}")
    print("=" * 60)
    print(f"  To:       {email}")
    print(f"  From:     {SENDER_EMAIL}")
    print(f"  Template: {template_key}")
    print(f"  A/B Test: Variant {variant}")
    print(f"  Score:    {target.get('outreach_score', '?')}/21 ({target.get('outreach_tier', '?')})")
    print(f"  Status:   {status}")

    # Show all subject variants
    print(f"\n  Subject line variants:")
    for v_key, v_subject in all_subjects.items():
        marker = " <-- SELECTED" if v_key == variant else ""
        print(f"    [{v_key}] {v_subject}{marker}")

    print("-" * 60)
    print(f"Subject: {subject}")
    print("-" * 60)
    print(body)
    print("-" * 60)

    # Generate gmail_send.py command
    escaped_subject = subject.replace('"', '\\"')
    escaped_body = body.replace('"', '\\"').replace("\n", "\\n")
    print(f"\nTo create Gmail draft, run:")
    print(f'  python3 {GMAIL_SEND} draft {SENDER_EMAIL} "{email}" "{escaped_subject}" "<body>"')
    print(f"\n  (Full body text is too long for command line — use the draft command")
    print(f"   or copy the email above into Gmail manually)")

    # Log the send and A/B test
    event_type = {
        "followup_1": "followup_1",
        "followup_2": "followup_2",
        "nurture_seasonal": "nurture_month2",
        "nurture_case_study": "nurture_month2",
        "nurture_final": "nurture_month3",
    }.get(template_key, "initial_email")

    log_event(log, target["_venue_id"], name, event_type,
              f"template={template_key}, variant={variant}, to={email}")
    save_log(log)

    # Log to A/B testing
    ab.log_send(template_key, variant, target["_venue_id"])

    print(f"\n  Logged: {event_type} for {name} (variant {variant})")


def cmd_followup():
    """Show all venues due for follow-up."""
    venues = load_all_venues()
    log = load_log()
    scored = score_venues(venues)
    followups = get_followups(scored, log)

    print("=" * 60)
    print("  HHT OUTREACH — FOLLOW-UPS DUE")
    print("=" * 60)

    fu1 = followups.get("followup_1", [])
    fu2 = followups.get("followup_2", [])
    n2 = followups.get("nurture_month2", [])
    n3 = followups.get("nurture_month3", [])

    if not fu1 and not fu2 and not n2 and not n3:
        print("\n  No follow-ups due right now.")
        print()
        return

    if fu1:
        print(f"\n  FOLLOW-UP #1 (gentle nudge — {len(fu1)} venues):")
        for venue, days in fu1:
            vid = venue.get("_venue_id", _venue_id(venue))
            print(f"    [{vid}] {_venue_name(venue)} — {days} days since initial email")

    if fu2:
        print(f"\n  FOLLOW-UP #2 (value-add menu — {len(fu2)} venues):")
        for venue, days in fu2:
            vid = venue.get("_venue_id", _venue_id(venue))
            print(f"    [{vid}] {_venue_name(venue)} — {days} days since follow-up #1")

    if n2:
        print(f"\n  NURTURE — MONTH 2 (seasonal/case study — {len(n2)} venues):")
        for venue, days in n2:
            vid = venue.get("_venue_id", _venue_id(venue))
            print(f"    [{vid}] {_venue_name(venue)} — {days} days since follow-up #2")

    if n3:
        print(f"\n  NURTURE — MONTH 3 (final attempt — {len(n3)} venues):")
        for venue, days in n3:
            vid = venue.get("_venue_id", _venue_id(venue))
            print(f"    [{vid}] {_venue_name(venue)} — {days} days since month 2 nurture")

    print(f"\n  To send:  python3 outreach_manager.py send <venue_id>")
    print()


def cmd_history():
    """Show recent outreach history."""
    log = load_log()

    if not log:
        print("No outreach history yet.")
        return

    print("=" * 60)
    print("  HHT OUTREACH — HISTORY")
    print("=" * 60)

    # Flatten all events and sort by timestamp
    all_events = []
    for vid, entry in log.items():
        for event in entry.get("events", []):
            all_events.append({
                "venue": entry.get("venue_name", vid),
                "type": event["type"],
                "time": event["timestamp"],
                "details": event.get("details", ""),
            })

    all_events.sort(key=lambda e: e["time"], reverse=True)

    print(f"\n  {'Date':<20} {'Type':<18} {'Venue':<30}")
    print("  " + "-" * 70)
    for e in all_events[:30]:
        ts = e["time"][:16].replace("T", " ")
        print(f"  {ts:<20} {e['type']:<18} {e['venue']:<30}")

    print()


def cmd_score():
    """Re-score all venues and show top leads."""
    venues = load_all_venues()
    scored = score_venues(venues)

    print("=" * 70)
    print("  HHT OUTREACH — TOP SCORED VENUES")
    print("=" * 70)

    print(f"\n  {'Score':>5}  {'Tier':<16} {'Venue':<35} {'Email':<30}")
    print("  " + "-" * 90)
    for v in scored[:25]:
        name = _venue_name(v)[:34]
        email = str(v.get("email", ""))[:29]
        print(f"  {v['outreach_score']:>5}  {v['outreach_tier']:<16} {name:<35} {email:<30}")

    # Tier summary
    tier_counts = Counter(v.get("outreach_tier", "UNSCORED") for v in scored)
    print(f"\n  Tier summary:")
    for tier in ["CALL_NOW", "HIGH_PRIORITY", "STANDARD", "NURTURE", "LOW"]:
        count = tier_counts.get(tier, 0)
        if count > 0:
            print(f"    {tier:<20} {count}")

    print(f"\n  Total venues scored: {len(scored)}")
    print()


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("HHT Outreach Manager")
        print("=" * 40)
        print("Commands:")
        print("  status           Pipeline overview")
        print("  today            Today's outreach tasks")
        print("  send <id/name>   Generate email draft")
        print("  followup         Venues due for follow-up")
        print("  history          Recent outreach log")
        print("  score            Re-score and show top leads")
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "status":
        cmd_status()
    elif cmd == "today":
        cmd_today()
    elif cmd == "send":
        if len(sys.argv) < 3:
            print("Usage: python3 outreach_manager.py send <venue_id or name>")
            sys.exit(1)
        cmd_send(" ".join(sys.argv[2:]))
    elif cmd == "followup":
        cmd_followup()
    elif cmd == "history":
        cmd_history()
    elif cmd == "score":
        cmd_score()
    else:
        print(f"Unknown command: {cmd}")
        print("Available: status, today, send, followup, history, score")
        sys.exit(1)
