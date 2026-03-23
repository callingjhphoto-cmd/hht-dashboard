#!/usr/bin/env python3
"""
HHT Operations API
===================
FastAPI backend for Joe Stokoe's cocktail bar lead-gen CRM.
Uses SQLite locally, designed for Supabase migration later.

Run:
  pip install fastapi uvicorn
  cd ~/Documents/Claude/projects/hht/api
  uvicorn app:app --reload --port 8000

Endpoints:
  GET  /api/venues              — List venues (filter by category, tier, county, classification)
  GET  /api/venues/{id}         — Single venue detail
  GET  /api/outreach/today      — Today's outreach tasks
  POST /api/outreach/{venue_id}/sent — Mark venue as contacted
  GET  /api/stats               — Pipeline overview
  GET  /api/dashboard           — Daily dashboard metrics for Joe
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DB_PATH = Path.home() / "Documents/Claude/projects/hht/database/hht.db"
app = FastAPI(title="HHT Operations API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    """Get SQLite connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row) -> dict:
    """Convert sqlite3.Row to dict."""
    if row is None:
        return None
    d = dict(row)
    # Parse JSON arrays stored as strings
    for key in ("all_emails", "all_phones"):
        if key in d and isinstance(d[key], str):
            try:
                d[key] = json.loads(d[key])
            except (json.JSONDecodeError, TypeError):
                d[key] = []
    return d


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class OutreachCreate(BaseModel):
    channel: str = "email"
    template_used: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    notes: Optional[str] = None


class BookingCreate(BaseModel):
    event_date: Optional[str] = None
    event_type: Optional[str] = None
    guests: Optional[int] = None
    package: Optional[str] = None
    value_gbp: Optional[float] = None
    status: str = "enquiry"
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# VENUES
# ---------------------------------------------------------------------------

@app.get("/api/venues")
def list_venues(
    category: Optional[str] = None,
    classification: Optional[str] = None,
    tier: Optional[str] = None,
    county: Optional[str] = None,
    has_email: Optional[bool] = None,
    min_score: Optional[int] = None,
    search: Optional[str] = None,
    sort: str = "score",
    order: str = "desc",
    limit: int = Query(default=50, le=500),
    offset: int = 0,
):
    """List venues with filtering, sorting, pagination."""
    conn = get_db()
    conditions = []
    params = []

    if category:
        conditions.append("category = ?")
        params.append(category)
    if classification:
        conditions.append("classification = ?")
        params.append(classification)
    if tier:
        conditions.append("tier = ?")
        params.append(tier)
    if county:
        conditions.append("county = ?")
        params.append(county)
    if has_email:
        conditions.append("email IS NOT NULL AND email != ''")
    if min_score is not None:
        conditions.append("score >= ?")
        params.append(min_score)
    if search:
        conditions.append("(name LIKE ? OR county LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    valid_sorts = {"score", "name", "capacity", "tier", "county", "created_at"}
    sort_col = sort if sort in valid_sorts else "score"
    order_dir = "ASC" if order.lower() == "asc" else "DESC"

    # Get total count
    count_sql = f"SELECT COUNT(*) FROM venues {where}"
    total = conn.execute(count_sql, params).fetchone()[0]

    # Get paginated results
    query = f"""
        SELECT * FROM venues {where}
        ORDER BY {sort_col} {order_dir}
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "venues": [row_to_dict(r) for r in rows],
    }


@app.get("/api/venues/{venue_id}")
def get_venue(venue_id: str):
    """Get single venue with outreach history and bookings."""
    conn = get_db()

    venue = conn.execute("SELECT * FROM venues WHERE id = ?", (venue_id,)).fetchone()
    if not venue:
        conn.close()
        raise HTTPException(status_code=404, detail="Venue not found")

    outreach = conn.execute(
        "SELECT * FROM outreach WHERE venue_id = ? ORDER BY created_at DESC",
        (venue_id,)
    ).fetchall()

    bookings = conn.execute(
        "SELECT * FROM bookings WHERE venue_id = ? ORDER BY event_date DESC",
        (venue_id,)
    ).fetchall()

    conn.close()

    return {
        "venue": row_to_dict(venue),
        "outreach_history": [row_to_dict(r) for r in outreach],
        "bookings": [row_to_dict(r) for r in bookings],
    }


# ---------------------------------------------------------------------------
# OUTREACH
# ---------------------------------------------------------------------------

@app.get("/api/outreach/today")
def outreach_today():
    """
    Get today's outreach tasks:
    1. New contacts: CALL_NOW tier venues not yet contacted
    2. Follow-ups: Venues where sent > 7 days ago with no reply
    3. Scheduled: Any follow-ups due today
    """
    conn = get_db()
    today = date.today().isoformat()
    seven_days_ago = (date.today() - timedelta(days=7)).isoformat()

    # New contacts: CALL_NOW and HIGH_PRIORITY not yet contacted
    new_contacts = conn.execute("""
        SELECT v.* FROM venues v
        WHERE v.tier IN ('CALL_NOW', 'HIGH_PRIORITY')
        AND v.email IS NOT NULL AND v.email != ''
        AND v.id NOT IN (SELECT DISTINCT venue_id FROM outreach)
        ORDER BY v.score DESC
        LIMIT 20
    """).fetchall()

    # Follow-ups needed: sent but no reply after 7 days
    follow_ups = conn.execute("""
        SELECT v.*, o.sent_at, o.channel, o.status as outreach_status
        FROM venues v
        JOIN outreach o ON o.venue_id = v.id
        WHERE o.status = 'sent'
        AND o.sent_at < ?
        AND o.follow_up_1_at IS NULL
        ORDER BY v.score DESC
        LIMIT 20
    """, (seven_days_ago,)).fetchall()

    # Scheduled follow-ups for today
    scheduled = conn.execute("""
        SELECT v.*, o.follow_up_1_at, o.channel
        FROM venues v
        JOIN outreach o ON o.venue_id = v.id
        WHERE (o.follow_up_1_at = ? OR o.follow_up_2_at = ? OR o.follow_up_3_at = ?)
        ORDER BY v.score DESC
    """, (today, today, today)).fetchall()

    conn.close()

    return {
        "date": today,
        "new_contacts": [row_to_dict(r) for r in new_contacts],
        "follow_ups_needed": [row_to_dict(r) for r in follow_ups],
        "scheduled_today": [row_to_dict(r) for r in scheduled],
        "total_tasks": len(new_contacts) + len(follow_ups) + len(scheduled),
    }


@app.post("/api/outreach/{venue_id}/sent")
def mark_outreach_sent(venue_id: str, outreach: OutreachCreate):
    """Record that a venue has been contacted."""
    conn = get_db()

    # Verify venue exists
    venue = conn.execute("SELECT id, name FROM venues WHERE id = ?", (venue_id,)).fetchone()
    if not venue:
        conn.close()
        raise HTTPException(status_code=404, detail="Venue not found")

    outreach_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    follow_up_1 = (datetime.now() + timedelta(days=7)).isoformat()

    conn.execute("""
        INSERT INTO outreach (id, venue_id, channel, template_used, subject, body, status, sent_at, follow_up_1_at, notes)
        VALUES (?, ?, ?, ?, ?, ?, 'sent', ?, ?, ?)
    """, (
        outreach_id, venue_id, outreach.channel,
        outreach.template_used, outreach.subject, outreach.body,
        now, follow_up_1, outreach.notes
    ))
    conn.commit()
    conn.close()

    return {
        "outreach_id": outreach_id,
        "venue_id": venue_id,
        "venue_name": dict(venue)["name"],
        "status": "sent",
        "sent_at": now,
        "follow_up_1_due": follow_up_1,
    }


# ---------------------------------------------------------------------------
# STATS / DASHBOARD
# ---------------------------------------------------------------------------

@app.get("/api/stats")
def pipeline_stats():
    """Pipeline overview: totals, by tier, by status, conversion funnel."""
    conn = get_db()

    total = conn.execute("SELECT COUNT(*) FROM venues").fetchone()[0]

    by_tier = dict(conn.execute(
        "SELECT tier, COUNT(*) FROM venues GROUP BY tier ORDER BY COUNT(*) DESC"
    ).fetchall())

    by_classification = dict(conn.execute(
        "SELECT classification, COUNT(*) FROM venues GROUP BY classification ORDER BY COUNT(*) DESC"
    ).fetchall())

    by_county = dict(conn.execute(
        "SELECT county, COUNT(*) FROM venues GROUP BY county ORDER BY COUNT(*) DESC LIMIT 15"
    ).fetchall())

    with_email = conn.execute(
        "SELECT COUNT(*) FROM venues WHERE email IS NOT NULL AND email != ''"
    ).fetchone()[0]

    with_phone = conn.execute(
        "SELECT COUNT(*) FROM venues WHERE phone IS NOT NULL AND phone != ''"
    ).fetchone()[0]

    avg_score = conn.execute("SELECT AVG(score) FROM venues").fetchone()[0] or 0

    # Outreach stats
    outreach_sent = conn.execute(
        "SELECT COUNT(*) FROM outreach WHERE status = 'sent'"
    ).fetchone()[0]
    outreach_replied = conn.execute(
        "SELECT COUNT(*) FROM outreach WHERE status = 'replied'"
    ).fetchone()[0]
    outreach_booked = conn.execute(
        "SELECT COUNT(*) FROM outreach WHERE status = 'booked'"
    ).fetchone()[0]

    # Booking stats
    total_bookings = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    pipeline_value = conn.execute(
        "SELECT COALESCE(SUM(value_gbp), 0) FROM bookings WHERE status IN ('enquiry', 'quoted', 'confirmed')"
    ).fetchone()[0]
    confirmed_value = conn.execute(
        "SELECT COALESCE(SUM(value_gbp), 0) FROM bookings WHERE status IN ('confirmed', 'deposit_paid', 'completed')"
    ).fetchone()[0]

    conn.close()

    return {
        "venues": {
            "total": total,
            "with_email": with_email,
            "with_phone": with_phone,
            "avg_score": round(avg_score, 1),
            "by_tier": by_tier,
            "by_classification": by_classification,
            "top_counties": by_county,
        },
        "outreach": {
            "sent": outreach_sent,
            "replied": outreach_replied,
            "booked": outreach_booked,
            "reply_rate": f"{(outreach_replied / outreach_sent * 100):.1f}%" if outreach_sent > 0 else "0%",
            "conversion_rate": f"{(outreach_booked / outreach_sent * 100):.1f}%" if outreach_sent > 0 else "0%",
        },
        "bookings": {
            "total": total_bookings,
            "pipeline_value_gbp": float(pipeline_value),
            "confirmed_value_gbp": float(confirmed_value),
        },
    }


@app.get("/api/dashboard")
def daily_dashboard():
    """
    Joe's daily dashboard — what he needs to see every morning.
    """
    conn = get_db()
    today = date.today().isoformat()

    # Top 10 venues to call today
    call_now = conn.execute("""
        SELECT id, name, county, email, phone, score, tier, classification
        FROM venues
        WHERE tier = 'CALL_NOW'
        AND email IS NOT NULL AND email != ''
        AND id NOT IN (SELECT DISTINCT venue_id FROM outreach)
        ORDER BY score DESC
        LIMIT 10
    """).fetchall()

    # Follow-ups due
    follow_ups_due = conn.execute("""
        SELECT v.name, v.email, o.sent_at, o.channel
        FROM venues v
        JOIN outreach o ON o.venue_id = v.id
        WHERE o.status = 'sent'
        AND o.follow_up_1_at <= ?
        AND o.follow_up_1_at IS NOT NULL
        LIMIT 10
    """, (today,)).fetchall()

    # Quick stats
    total_venues = conn.execute("SELECT COUNT(*) FROM venues").fetchone()[0]
    contacted = conn.execute("SELECT COUNT(DISTINCT venue_id) FROM outreach").fetchone()[0]
    replied = conn.execute("SELECT COUNT(DISTINCT venue_id) FROM outreach WHERE status = 'replied'").fetchone()[0]
    bookings = conn.execute("SELECT COUNT(*) FROM bookings WHERE status NOT IN ('cancelled')").fetchone()[0]

    # Email quality breakdown
    email_quality = {
        "total_with_email": conn.execute("SELECT COUNT(*) FROM venues WHERE email != ''").fetchone()[0],
        "events_emails": conn.execute("SELECT COUNT(*) FROM venues WHERE email LIKE 'events@%'").fetchone()[0],
        "weddings_emails": conn.execute("SELECT COUNT(*) FROM venues WHERE email LIKE 'wedding%@%'").fetchone()[0],
        "info_emails": conn.execute("SELECT COUNT(*) FROM venues WHERE email LIKE 'info@%'").fetchone()[0],
        "other_specific": conn.execute("""
            SELECT COUNT(*) FROM venues
            WHERE email != '' AND email NOT LIKE 'info@%'
            AND email NOT LIKE 'events@%' AND email NOT LIKE 'wedding%@%'
            AND email NOT LIKE 'enquir%@%'
        """).fetchone()[0],
    }

    conn.close()

    return {
        "date": today,
        "greeting": f"Morning Joe — {len(call_now)} venues to call, {len(follow_ups_due)} follow-ups due.",
        "call_now": [row_to_dict(r) for r in call_now],
        "follow_ups_due": [row_to_dict(r) for r in follow_ups_due],
        "stats": {
            "total_venues": total_venues,
            "contacted": contacted,
            "replied": replied,
            "bookings": bookings,
            "contact_rate": f"{(contacted / total_venues * 100):.0f}%" if total_venues > 0 else "0%",
        },
        "email_quality": email_quality,
    }


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    """Health check."""
    db_exists = DB_PATH.exists()
    if db_exists:
        conn = get_db()
        count = conn.execute("SELECT COUNT(*) FROM venues").fetchone()[0]
        conn.close()
        return {"status": "ok", "db": str(DB_PATH), "venues": count}
    return {"status": "no_db", "db": str(DB_PATH), "venues": 0}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
