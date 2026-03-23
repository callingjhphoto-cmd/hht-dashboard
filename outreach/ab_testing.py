#!/usr/bin/env python3
"""
HHT Outreach — A/B Testing Framework

For each venue, randomly assigns a subject line variant (A, B, or C).
Tracks sends, opens (if available), and responses per variant.
After 20 sends per variant, calculates the winner and auto-switches.

Data stored in: ~/Documents/Claude/projects/hht/outreach/ab_test_data.json

Usage:
    from ab_testing import ABTestManager
    ab = ABTestManager()

    # Get which variant to use for a venue
    variant = ab.get_variant("wedding", venue_id="abc123")

    # Log a send
    ab.log_send("wedding", "A", venue_id="abc123")

    # Log a response
    ab.log_response("wedding", "A", venue_id="abc123")

    # Check if we have a winner
    winner = ab.get_winner("wedding")  # Returns "A", "B", "C", or None

CLI:
    python3 ab_testing.py status         — show all test results
    python3 ab_testing.py reset          — reset all test data
    python3 ab_testing.py winner <key>   — check winner for a template
"""

import json
import os
import random
from datetime import datetime
from collections import defaultdict

# Paths
BASE = os.path.expanduser("~/Documents/Claude/projects/hht/outreach")
DATA_PATH = os.path.join(BASE, "ab_test_data.json")

# Config
MIN_SENDS_PER_VARIANT = 20  # Minimum sends before declaring a winner
VARIANTS = ["A", "B", "C"]
CONFIDENCE_THRESHOLD = 1.5  # Winner must be 1.5x better than second-best


class ABTestManager:
    """Manages A/B/C testing for email subject lines."""

    def __init__(self, data_path: str = DATA_PATH):
        self.data_path = data_path
        self.data = self._load()

    def _load(self) -> dict:
        """Load test data from disk."""
        if os.path.exists(self.data_path):
            with open(self.data_path) as f:
                return json.load(f)
        return {
            "tests": {},           # template_key -> { variant -> stats }
            "assignments": {},     # venue_id -> { template_key -> variant }
            "events": [],          # chronological event log
            "winners": {},         # template_key -> winning variant
        }

    def _save(self):
        """Save test data to disk."""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def _ensure_template(self, template_key: str):
        """Ensure a template entry exists in tests."""
        if template_key not in self.data["tests"]:
            self.data["tests"][template_key] = {}
            for v in VARIANTS:
                self.data["tests"][template_key][v] = {
                    "sends": 0,
                    "responses": 0,
                    "opens": 0,
                    "response_rate": 0.0,
                }

    def get_variant(self, template_key: str, venue_id: str) -> str:
        """
        Get the variant to use for a venue.

        Logic:
        1. If there's a declared winner for this template, always use it
        2. If the venue already has an assignment, use that
        3. Otherwise, assign the variant with fewest sends (balanced allocation)
        """
        # Check for winner
        if template_key in self.data.get("winners", {}):
            return self.data["winners"][template_key]

        # Check existing assignment
        if venue_id in self.data.get("assignments", {}):
            if template_key in self.data["assignments"][venue_id]:
                return self.data["assignments"][venue_id][template_key]

        # Balanced assignment — pick variant with fewest sends
        self._ensure_template(template_key)
        stats = self.data["tests"][template_key]
        min_sends = min(stats[v]["sends"] for v in VARIANTS)
        candidates = [v for v in VARIANTS if stats[v]["sends"] == min_sends]
        variant = random.choice(candidates)

        # Save assignment
        if venue_id not in self.data.get("assignments", {}):
            self.data["assignments"][venue_id] = {}
        self.data["assignments"][venue_id][template_key] = variant
        self._save()

        return variant

    def log_send(self, template_key: str, variant: str, venue_id: str = ""):
        """Log that an email was sent with a specific variant."""
        self._ensure_template(template_key)
        self.data["tests"][template_key][variant]["sends"] += 1
        self.data["events"].append({
            "type": "send",
            "template": template_key,
            "variant": variant,
            "venue_id": venue_id,
            "timestamp": datetime.now().isoformat(),
        })
        self._recalculate(template_key)
        self._check_winner(template_key)
        self._save()

    def log_response(self, template_key: str, variant: str, venue_id: str = ""):
        """Log that a response was received for a specific variant."""
        self._ensure_template(template_key)
        self.data["tests"][template_key][variant]["responses"] += 1
        self.data["events"].append({
            "type": "response",
            "template": template_key,
            "variant": variant,
            "venue_id": venue_id,
            "timestamp": datetime.now().isoformat(),
        })
        self._recalculate(template_key)
        self._check_winner(template_key)
        self._save()

    def log_open(self, template_key: str, variant: str, venue_id: str = ""):
        """Log that an email was opened (if tracking available)."""
        self._ensure_template(template_key)
        self.data["tests"][template_key][variant]["opens"] += 1
        self.data["events"].append({
            "type": "open",
            "template": template_key,
            "variant": variant,
            "venue_id": venue_id,
            "timestamp": datetime.now().isoformat(),
        })
        self._recalculate(template_key)
        self._save()

    def _recalculate(self, template_key: str):
        """Recalculate response rates."""
        for v in VARIANTS:
            stats = self.data["tests"][template_key][v]
            if stats["sends"] > 0:
                stats["response_rate"] = round(stats["responses"] / stats["sends"] * 100, 1)
            else:
                stats["response_rate"] = 0.0

    def _check_winner(self, template_key: str):
        """
        Check if we can declare a winner.
        Requirements:
        - All variants have >= MIN_SENDS_PER_VARIANT sends
        - Winner's response rate is >= CONFIDENCE_THRESHOLD times the second-best
        """
        stats = self.data["tests"][template_key]

        # Check minimum sends
        for v in VARIANTS:
            if stats[v]["sends"] < MIN_SENDS_PER_VARIANT:
                return  # Not enough data yet

        # Sort by response rate
        ranked = sorted(VARIANTS, key=lambda v: stats[v]["response_rate"], reverse=True)
        best_rate = stats[ranked[0]]["response_rate"]
        second_rate = stats[ranked[1]]["response_rate"]

        # Check confidence threshold
        if second_rate == 0:
            if best_rate > 0:
                self.data["winners"][template_key] = ranked[0]
        elif best_rate / second_rate >= CONFIDENCE_THRESHOLD:
            self.data["winners"][template_key] = ranked[0]

    def get_winner(self, template_key: str):
        """Get the winning variant for a template, or None if undecided."""
        return self.data.get("winners", {}).get(template_key)

    def get_status(self, template_key: str = None) -> dict:
        """Get current test status for one or all templates."""
        if template_key:
            return self.data["tests"].get(template_key, {})
        return self.data["tests"]

    def reset(self, template_key: str = None):
        """Reset test data for one or all templates."""
        if template_key:
            if template_key in self.data["tests"]:
                del self.data["tests"][template_key]
            if template_key in self.data.get("winners", {}):
                del self.data["winners"][template_key]
            # Remove assignments for this template
            for vid in self.data.get("assignments", {}):
                if template_key in self.data["assignments"][vid]:
                    del self.data["assignments"][vid][template_key]
        else:
            self.data = {
                "tests": {},
                "assignments": {},
                "events": [],
                "winners": {},
            }
        self._save()

    def print_status(self):
        """Print a formatted status report."""
        from email_templates import TEMPLATES

        print("=" * 70)
        print("  HHT A/B TESTING — STATUS REPORT")
        print(f"  {datetime.now().strftime('%d %B %Y, %H:%M')}")
        print("=" * 70)

        if not self.data["tests"]:
            print("\n  No tests running yet. Send some emails to start collecting data.")
            print()
            return

        for tkey, variants in self.data["tests"].items():
            tname = TEMPLATES.get(tkey, {}).get("name", tkey)
            winner = self.data.get("winners", {}).get(tkey)

            print(f"\n  {tname} ({tkey})")
            if winner:
                print(f"  WINNER: Variant {winner}")
            print(f"  {'Variant':<10} {'Sends':>6} {'Responses':>10} {'Rate':>8} {'Opens':>6}")
            print("  " + "-" * 45)

            for v in VARIANTS:
                s = variants.get(v, {"sends": 0, "responses": 0, "response_rate": 0, "opens": 0})
                marker = " <--" if v == winner else ""
                print(f"  {v:<10} {s['sends']:>6} {s['responses']:>10} {s['response_rate']:>7.1f}% {s['opens']:>6}{marker}")

            # Progress to decision
            min_sends = min(variants.get(v, {}).get("sends", 0) for v in VARIANTS)
            remaining = max(0, MIN_SENDS_PER_VARIANT - min_sends)
            if not winner and remaining > 0:
                print(f"  Need {remaining} more sends per variant before declaring winner")

        # Total events
        total_sends = sum(1 for e in self.data.get("events", []) if e["type"] == "send")
        total_responses = sum(1 for e in self.data.get("events", []) if e["type"] == "response")
        print(f"\n  Total sends: {total_sends}  |  Total responses: {total_responses}")
        if total_sends > 0:
            print(f"  Overall response rate: {total_responses/total_sends*100:.1f}%")
        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    ab = ABTestManager()

    if len(sys.argv) < 2:
        print("HHT A/B Testing Framework")
        print("=" * 40)
        print("Commands:")
        print("  status             Show all test results")
        print("  reset              Reset all test data")
        print("  reset <template>   Reset specific template")
        print("  winner <template>  Check winner for a template")
        print("  simulate           Run a simulation with fake data")
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "status":
        ab.print_status()

    elif cmd == "reset":
        tkey = sys.argv[2] if len(sys.argv) > 2 else None
        ab.reset(tkey)
        if tkey:
            print(f"Reset test data for: {tkey}")
        else:
            print("Reset all test data.")

    elif cmd == "winner":
        if len(sys.argv) < 3:
            print("Usage: python3 ab_testing.py winner <template_key>")
            sys.exit(1)
        tkey = sys.argv[2]
        winner = ab.get_winner(tkey)
        if winner:
            print(f"Winner for {tkey}: Variant {winner}")
        else:
            print(f"No winner declared yet for {tkey}")
            status = ab.get_status(tkey)
            if status:
                for v in VARIANTS:
                    s = status.get(v, {})
                    print(f"  [{v}] {s.get('sends', 0)} sends, {s.get('responses', 0)} responses ({s.get('response_rate', 0):.1f}%)")

    elif cmd == "simulate":
        print("Running simulation with fake data...")
        ab.reset()
        import random as rng

        # Simulate: variant A gets 15% response, B gets 8%, C gets 5%
        rates = {"A": 0.15, "B": 0.08, "C": 0.05}
        for i in range(25):
            for v in VARIANTS:
                venue_id = f"sim_{v}_{i}"
                ab.log_send("wedding", v, venue_id)
                if rng.random() < rates[v]:
                    ab.log_response("wedding", v, venue_id)

        ab.print_status()

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
