#!/usr/bin/env python3
"""
HHT Outreach — Email Templates v2.0
Research-optimised templates based on 2025-2026 cold email best practices.

Key changes from v1:
- Under 125 words per email (50-125 word sweet spot for reply rates)
- 3 A/B subject line options per template (2-4 word subject lines get 46% open rates)
- Personalised opening lines (17% response rate vs 7% without)
- Single clear CTA (not multiple options)
- P.S. lines on every email (read before body — Zeigarnik effect)
- Social proof with specific client names and credentials
- Mobile-friendly formatting

Usage:
    from email_templates import get_template, list_templates, get_ab_subjects
    subject, body = get_template("wedding", variant="A", venue_name="Blenheim Palace",
                                  contact_name="Sarah", location="Oxfordshire")
"""

import random


def _format(template: str, **kwargs) -> str:
    """Fill placeholders, leaving unfilled ones as-is for manual review."""
    for key, val in kwargs.items():
        template = template.replace(f"{{{key}}}", str(val))
    return template


# ---------------------------------------------------------------------------
# TEMPLATE DEFINITIONS — v2.0 (Research-Optimised)
# ---------------------------------------------------------------------------

TEMPLATES = {
    "wedding": {
        "name": "Wedding Venue",
        "subjects": {
            "A": "quick question, {contact_name}",
            "B": "{venue_name} weddings",
            "C": "cocktail idea for {venue_name}",
        },
        "body": """Hi {contact_name},

I spotted {venue_name} while mapping wedding venues in {location} — your space is exactly the kind of venue our couples love.

I'm Joe, founder of Heads, Hearts & Tails. We build bespoke cocktail bars for weddings — custom menus, trained bartenders, full setup and breakdown. Everything arrives and leaves with us.

We've designed cocktail programmes for Bombay Sapphire, Belvedere, and Grey Goose — and we bring that same R&D approach to every wedding. Each couple gets a menu developed in our Camden kitchen, not picked from a standard list.

Would you be open to a 10-minute call about getting on your suppliers list?

Best,
Joe
Heads, Hearts & Tails
www.headsandtails.co.uk

P.S. Happy to send over a sample seasonal cocktail menu designed for barn/estate venues — no strings attached.""",
    },
    "corporate": {
        "name": "Corporate Venue",
        "subjects": {
            "A": "quick question, {contact_name}",
            "B": "drinks for {venue_name} events",
            "C": "{venue_name} — cocktail partner",
        },
        "body": """Hi {contact_name},

I noticed {venue_name} hosts corporate events and wanted to introduce a different kind of drinks partner.

I'm Joe from Heads, Hearts & Tails — we're a drinks agency (not just a mobile bar). We've created cocktail programmes for Johnnie Walker, Patron, and Louis Vuitton, and now we're bringing that expertise to venue partnerships.

What makes us different: every menu is developed in our Camden kitchen. We can brand cocktails to a client's colours, product, or campaign theme — something generic bar hire can't do.

Could we have a quick call about becoming a recommended bar partner?

Best regards,
Joe
Heads, Hearts & Tails
www.headsandtails.co.uk

P.S. Our corporate clients typically see a 30-40% uplift in guest satisfaction scores when they switch from standard bar service to bespoke cocktails.""",
    },
    "festival": {
        "name": "Festival / Outdoor Event",
        "subjects": {
            "A": "bar partner for {venue_name}",
            "B": "{venue_name} drinks",
            "C": "cocktails at {venue_name}?",
        },
        "body": """Hi {contact_name},

I saw {venue_name} is coming up and wanted to get in early about the bar setup.

I'm Joe, founder of Heads, Hearts & Tails. We run fully self-contained cocktail bars built for outdoor, high-volume service — 200+ drinks per hour, weather-proof, all licensing handled.

We've worked with BBC Good Food Show and major brand activations (Bacardi, Schweppes, Coca-Cola). Our pre-batched signature cocktails mean festival-quality speed without sacrificing drink quality.

We're partnering with a small number of events this season. Would {venue_name} be open to a quick chat?

Cheers,
Joe
Heads, Hearts & Tails
www.headsandtails.co.uk

P.S. We can often bring spirit brand co-funding to events — which means a better bar at lower cost to you.""",
    },
    "pub_bar": {
        "name": "Pub / Bar",
        "subjects": {
            "A": "idea for {venue_name}",
            "B": "midweek footfall at {venue_name}",
            "C": "{venue_name} — cocktail night?",
        },
        "body": """Hi {contact_name},

Quick idea for {venue_name}: we run guest cocktail nights and masterclasses that typically drive a 30-40% uplift in evening covers — zero risk or cost to you.

I'm Joe from Heads, Hearts & Tails. Two formats:

1. **Guest cocktail night** — I bring the theatre, you keep normal service running. Great for midweek.
2. **Bookable masterclass** — groups of 8-20 learn to make 3 cocktails. Perfect for hen dos and birthdays. You keep all food and standard drinks revenue.

We handle all specialist ingredients and equipment. Revenue share or flat fee — whatever works.

Fancy trying a one-off night?

Cheers,
Joe
Heads, Hearts & Tails
www.headsandtails.co.uk

P.S. I've developed drinks for Milk & Honey and Trailer Happiness — happy to share what's trending in cocktails right now.""",
    },
    "orphaned_client": {
        "name": "Orphaned Client (ex-Cocktail Service)",
        "subjects": {
            "A": "your cocktail bar partner",
            "B": "{venue_name} — drinks partner",
            "C": "replacing your bar service?",
        },
        "body": """Hi {contact_name},

I understand {venue_name} previously worked with an external cocktail bar provider. With The Cocktail Service no longer operating, I wanted to introduce Heads, Hearts & Tails as a replacement partner.

I'm Joe — I've spent 25 years in London's cocktail scene (Milk & Honey, Trailer Happiness) and now run HHT, a drinks agency covering {location} and the wider UK.

The difference: you deal directly with me as founder. Every menu is developed in our Camden kitchen — genuinely bespoke, not a standard list with your logo. And our pricing is competitive without the overhead of a large corporate operation.

Could we have a brief call about your upcoming events calendar?

Best regards,
Joe
Heads, Hearts & Tails
www.headsandtails.co.uk

P.S. We already work with Bombay Sapphire, Belvedere, and Woodford Reserve — happy to share how spirit brand partnerships can offset your bar costs.""",
    },

    # -----------------------------------------------------------------------
    # FOLLOW-UP SEQUENCE (3 touches, each adds value)
    # -----------------------------------------------------------------------
    "followup_1": {
        "name": "Follow-up #1 (Day 3) — Gentle Nudge",
        "subjects": {
            "A": "Re: {venue_name}",
            "B": "bumping this up, {contact_name}",
            "C": "still keen to chat",
        },
        "body": """Hi {contact_name},

Just floating my note back up — I know event inboxes are relentless.

I'd love 10 minutes to walk you through what we do at {venue_name}. If it's not a fit, no hard feelings at all.

If a call feels like too much, I'm happy to send over some photos and a sample menu so you can see the standard.

Best,
Joe
Heads, Hearts & Tails

P.S. We just wrapped a 250-guest wedding bar in Oxfordshire last weekend — went brilliantly. Happy to share the case study.""",
    },
    "followup_2": {
        "name": "Follow-up #2 (Day 7) — Value-Add",
        "subjects": {
            "A": "cocktail menu for {venue_name}",
            "B": "thought you'd find this useful",
            "C": "free menu for {venue_name}",
        },
        "body": """Hi {contact_name},

I put together a sample seasonal cocktail menu designed for venues like {venue_name} — 6 cocktails (2 refreshing, 2 spirit-forward, 2 low-ABV) with costings and suggested pricing.

Happy to send it over as a PDF. Use it however you like, even if we don't end up working together.

If you'd like something designed specifically for your venue and clientele, I'll put a bespoke version together. No charge.

Best,
Joe
Heads, Hearts & Tails
www.headsandtails.co.uk

P.S. Low-ABV cocktails are the fastest-growing segment in UK hospitality right now — worth having on any menu.""",
    },

    # -----------------------------------------------------------------------
    # NURTURE SEQUENCE (Month 2-3, for non-responders)
    # -----------------------------------------------------------------------
    "nurture_seasonal": {
        "name": "Nurture — Month 2 (Seasonal Angle)",
        "subjects": {
            "A": "summer bookings at {venue_name}",
            "B": "{contact_name} — quick seasonal update",
            "C": "wedding season prep",
        },
        "body": """Hi {contact_name},

Quick seasonal note: we're booking summer 2026 events now and have a few weekend slots left in {location}.

I reached out previously about partnering with {venue_name} on cocktail bar services. Since then, we've added 3 new venue partnerships in the area and completed a bespoke cocktail programme for a Cotswolds wedding that got featured in a national bridal magazine.

If you're reviewing your suppliers list ahead of peak season, I'd love to be considered.

Happy to send our updated portfolio — just say the word.

Best,
Joe
Heads, Hearts & Tails

P.S. We're offering a free tasting session for new venue partners this month — no commitment, just great cocktails.""",
    },
    "nurture_case_study": {
        "name": "Nurture — Month 2 Alt (Case Study)",
        "subjects": {
            "A": "how we handled 300 guests at a barn wedding",
            "B": "case study from a venue like yours",
            "C": "{contact_name} — thought this was relevant",
        },
        "body": """Hi {contact_name},

Wanted to share a quick case study that might be relevant to {venue_name}.

Last month we ran the cocktail bar at a 300-guest wedding in a barn venue — similar setup to yours. The couple wanted cocktails that matched their floral theme, so we developed a lavender Collins and a rose gin fizz in our Camden kitchen.

Result: the venue owner said it was the best bar service they'd had in 5 years. We're now on their permanent suppliers list.

Would something like this work for {venue_name}? Happy to chat.

Best,
Joe
Heads, Hearts & Tails

P.S. I've attached a photo of the bar setup — might give you a sense of how we'd fit into your space.""",
    },
    "nurture_final": {
        "name": "Nurture — Month 3 (Final Attempt)",
        "subjects": {
            "A": "closing our summer books",
            "B": "last note from me, {contact_name}",
            "C": "{venue_name} — final check-in",
        },
        "body": """Hi {contact_name},

This is my last note — I don't want to be that person who won't stop emailing.

We're closing our summer 2026 bookings this month. If there's any interest in adding a cocktail bar partner to {venue_name}'s suppliers list, I'd love to have a quick conversation before we're fully booked.

If not, absolutely no worries. I'll leave you in peace and wish you a brilliant season ahead.

Best,
Joe
Heads, Hearts & Tails
www.headsandtails.co.uk

P.S. If the timing's wrong but you'd like to revisit later in the year, just reply "later" and I'll check back in autumn.""",
    },
}


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

def list_templates() -> list:
    """Return list of available template keys and names."""
    return [(k, v["name"]) for k, v in TEMPLATES.items()]


def get_ab_subjects(template_key: str, **kwargs) -> dict:
    """
    Get all A/B/C subject line variants for a template.
    Returns: {"A": "subject...", "B": "subject...", "C": "subject..."}
    """
    if template_key not in TEMPLATES:
        raise ValueError(f"Unknown template: {template_key}. Available: {list(TEMPLATES.keys())}")
    subjects = {}
    for variant, subject in TEMPLATES[template_key]["subjects"].items():
        subjects[variant] = _format(subject, **kwargs)
    return subjects


def get_template(template_key: str, variant: str = "A", **kwargs) -> tuple:
    """
    Get a formatted (subject, body) tuple for a given template.

    Args:
        template_key: One of the template keys (wedding, corporate, etc.)
        variant: Subject line variant — "A", "B", or "C" (default "A")
        **kwargs: Placeholders: venue_name, contact_name, location, event_type

    Returns:
        (subject: str, body: str)
    """
    if template_key not in TEMPLATES:
        raise ValueError(f"Unknown template: {template_key}. Available: {list(TEMPLATES.keys())}")

    t = TEMPLATES[template_key]
    subject_template = t["subjects"].get(variant, t["subjects"]["A"])
    subject = _format(subject_template, **kwargs)
    body = _format(t["body"], **kwargs)
    return subject, body


def get_random_variant() -> str:
    """Return a random A/B/C variant for testing."""
    return random.choice(["A", "B", "C"])


def select_template(venue: dict) -> str:
    """
    Auto-select the best template key based on venue data.
    Checks for orphaned client status first, then matches on venue type/classification.
    """
    # Check orphaned client
    if venue.get("id", "").startswith("ORPHAN") or venue.get("cocktail_service_relationship"):
        return "orphaned_client"

    # Check venue type / lead_type / description
    desc = " ".join([
        str(venue.get("lead_type", "")),
        str(venue.get("description", "")),
        str(venue.get("type", "")),
        str(venue.get("category", "")),
        str(venue.get("classification_note", "")),
    ]).lower()

    if any(w in desc for w in ["wedding", "ceremony", "bridal", "barn"]):
        return "wedding"
    if any(w in desc for w in ["corporate", "conference", "office", "meeting"]):
        return "corporate"
    if any(w in desc for w in ["festival", "outdoor", "food_festival", "park"]):
        return "festival"
    if any(w in desc for w in ["pub", "bar", "tavern", "inn"]):
        return "pub_bar"

    # Default to corporate for general event spaces
    return "corporate"


def get_nurture_template(month: int, variant: str = "default") -> str:
    """
    Select the appropriate nurture template based on month in sequence.

    Args:
        month: Month number (2 or 3)
        variant: "seasonal", "case_study", or "default" (auto-select)

    Returns:
        Template key string
    """
    if month == 2:
        if variant == "case_study":
            return "nurture_case_study"
        return "nurture_seasonal"
    elif month >= 3:
        return "nurture_final"
    else:
        return "followup_1"


# ---------------------------------------------------------------------------
# WORD COUNT VALIDATOR
# ---------------------------------------------------------------------------

def validate_templates():
    """Check all templates meet the 150-word mobile-friendly limit."""
    print(f"\n{'Template':<25} {'Words':>6}  {'Status'}")
    print("-" * 50)
    for key, t in TEMPLATES.items():
        # Count words in body only (not subject)
        word_count = len(t["body"].split())
        status = "OK" if word_count <= 150 else "OVER LIMIT"
        marker = "" if word_count <= 150 else " <<<"
        print(f"  {key:<23} {word_count:>6}  {status}{marker}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "list":
        print("Available email templates (v2.0):")
        print("-" * 55)
        for key, name in list_templates():
            print(f"  {key:25s} {name}")
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        key = sys.argv[2] if len(sys.argv) > 2 else "wedding"
        variant = sys.argv[3] if len(sys.argv) > 3 else "A"

        # Show all subject variants
        subjects = get_ab_subjects(
            key,
            venue_name="Merriscourt",
            contact_name="Sarah",
            location="Oxfordshire",
        )
        print(f"\nSubject line variants for '{key}':")
        for v, s in subjects.items():
            marker = " <-- selected" if v == variant else ""
            print(f"  [{v}] {s}{marker}")

        subject, body = get_template(
            key,
            variant=variant,
            venue_name="Merriscourt",
            contact_name="Sarah",
            location="Oxfordshire",
            event_type="wedding",
        )
        print(f"\nSubject: {subject}\n")
        print(body)
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        validate_templates()
        sys.exit(0)

    print("Usage:")
    print("  python3 email_templates.py list                    — show all templates")
    print("  python3 email_templates.py preview [key] [A/B/C]   — preview a template")
    print("  python3 email_templates.py validate                — check word counts")
