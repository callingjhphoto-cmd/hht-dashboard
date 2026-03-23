-- HHT Operations Platform — Supabase PostgreSQL Schema
-- Created: 2026-03-20
-- Purpose: Backend for Joe Stokoe's cocktail bar lead-gen & outreach CRM

-- ============================================================
-- VENUES
-- ============================================================
CREATE TABLE venues (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  county TEXT,
  category TEXT,                    -- Event Space, Country Estate, Barn Venue, Castle, etc.
  classification TEXT,              -- DRY_HIRE, EXTERNAL_OK, IN_HOUSE_ONLY
  classification_reason TEXT,
  capacity INTEGER,
  website TEXT,
  email TEXT,                       -- Primary contact email
  all_emails TEXT[],                -- All discovered emails
  phone TEXT,
  all_phones TEXT[],
  instagram TEXT,
  facebook TEXT,
  has_events_section BOOLEAN DEFAULT false,
  contact_name TEXT,
  notes TEXT,
  score INTEGER DEFAULT 0,         -- 0-100 priority score
  tier TEXT,                        -- CALL_NOW, HIGH_PRIORITY, STANDARD, NURTURE, LOW
  enrichment_date DATE,
  enrichment_error TEXT,
  pages_scraped INTEGER DEFAULT 0,
  source TEXT,                      -- hitched, bridebook, google_maps, manual
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- OUTREACH TRACKING
-- ============================================================
CREATE TABLE outreach (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  venue_id UUID NOT NULL REFERENCES venues(id) ON DELETE CASCADE,
  template_used TEXT,               -- e.g. "initial_intro", "follow_up_1", "seasonal"
  channel TEXT NOT NULL,            -- email, whatsapp, phone, instagram_dm
  status TEXT NOT NULL DEFAULT 'draft', -- draft, sent, opened, replied, booked, declined, bounced
  subject TEXT,
  body TEXT,
  sent_at TIMESTAMPTZ,
  opened_at TIMESTAMPTZ,
  replied_at TIMESTAMPTZ,
  follow_up_1_at TIMESTAMPTZ,
  follow_up_2_at TIMESTAMPTZ,
  follow_up_3_at TIMESTAMPTZ,
  response TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- BOOKINGS
-- ============================================================
CREATE TABLE bookings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  venue_id UUID NOT NULL REFERENCES venues(id) ON DELETE CASCADE,
  event_date DATE,
  event_type TEXT,                  -- wedding, corporate, festival, private, charity
  guests INTEGER,
  package TEXT,                     -- standard, premium, luxury, custom
  value_gbp DECIMAL(10,2),
  cost_gbp DECIMAL(10,2),          -- COGS for this booking
  margin_gbp DECIMAL(10,2) GENERATED ALWAYS AS (value_gbp - cost_gbp) STORED,
  status TEXT DEFAULT 'enquiry',    -- enquiry, quoted, confirmed, deposit_paid, completed, cancelled
  contact_name TEXT,
  contact_email TEXT,
  contact_phone TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- OUTREACH TEMPLATES
-- ============================================================
CREATE TABLE outreach_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,        -- e.g. "initial_intro"
  channel TEXT NOT NULL,            -- email, whatsapp
  subject TEXT,
  body TEXT NOT NULL,
  variables TEXT[],                 -- e.g. {venue_name, contact_name, county}
  is_active BOOLEAN DEFAULT true,
  send_count INTEGER DEFAULT 0,
  reply_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- ACTIVITY LOG (audit trail)
-- ============================================================
CREATE TABLE activity_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  venue_id UUID REFERENCES venues(id) ON DELETE SET NULL,
  action TEXT NOT NULL,             -- enriched, contacted, replied, booked, scored, imported
  details JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- DAILY METRICS (for dashboard reporting)
-- ============================================================
CREATE TABLE daily_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metric_date DATE NOT NULL UNIQUE,
  total_venues INTEGER DEFAULT 0,
  enriched_venues INTEGER DEFAULT 0,
  emails_found INTEGER DEFAULT 0,
  outreach_sent INTEGER DEFAULT 0,
  replies_received INTEGER DEFAULT 0,
  bookings_confirmed INTEGER DEFAULT 0,
  revenue_pipeline_gbp DECIMAL(12,2) DEFAULT 0,
  revenue_confirmed_gbp DECIMAL(12,2) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- INDEXES
-- ============================================================

-- Venues: most common queries
CREATE INDEX idx_venues_classification ON venues(classification);
CREATE INDEX idx_venues_tier ON venues(tier);
CREATE INDEX idx_venues_county ON venues(county);
CREATE INDEX idx_venues_score ON venues(score DESC);
CREATE INDEX idx_venues_category ON venues(category);
CREATE INDEX idx_venues_email ON venues(email) WHERE email IS NOT NULL;
CREATE INDEX idx_venues_classification_tier ON venues(classification, tier);

-- Outreach: daily task queries
CREATE INDEX idx_outreach_venue_id ON outreach(venue_id);
CREATE INDEX idx_outreach_status ON outreach(status);
CREATE INDEX idx_outreach_sent_at ON outreach(sent_at);
CREATE INDEX idx_outreach_follow_up ON outreach(follow_up_1_at)
  WHERE status = 'sent' AND follow_up_1_at IS NOT NULL;

-- Bookings
CREATE INDEX idx_bookings_venue_id ON bookings(venue_id);
CREATE INDEX idx_bookings_event_date ON bookings(event_date);
CREATE INDEX idx_bookings_status ON bookings(status);

-- Activity log
CREATE INDEX idx_activity_venue ON activity_log(venue_id);
CREATE INDEX idx_activity_created ON activity_log(created_at DESC);

-- Daily metrics
CREATE INDEX idx_metrics_date ON daily_metrics(metric_date DESC);

-- ============================================================
-- ROW-LEVEL SECURITY (for Supabase)
-- ============================================================
ALTER TABLE venues ENABLE ROW LEVEL SECURITY;
ALTER TABLE outreach ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE outreach_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_metrics ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users full access (single-tenant for Joe)
CREATE POLICY "Authenticated users can do everything on venues"
  ON venues FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can do everything on outreach"
  ON outreach FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can do everything on bookings"
  ON bookings FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can do everything on templates"
  ON outreach_templates FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can do everything on activity_log"
  ON activity_log FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can do everything on daily_metrics"
  ON daily_metrics FOR ALL USING (auth.role() = 'authenticated');

-- ============================================================
-- TRIGGER: auto-update updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER venues_updated_at
  BEFORE UPDATE ON venues
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER bookings_updated_at
  BEFORE UPDATE ON bookings
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
