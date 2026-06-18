-- Tranzformation Nation -- SQLite-compatible schema.
-- This file is the default (SQLite). For Postgres see docs/ENV_SETUP.md:
--   * INTEGER PRIMARY KEY AUTOINCREMENT  -> SERIAL / GENERATED ... AS IDENTITY
--   * datetime('now')                    -> now()
--   * TEXT json columns                  -> JSONB (optional)
-- The application code uses "?" placeholders and is otherwise dialect-free.

CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    first_name      TEXT,
    last_name       TEXT,
    role            TEXT NOT NULL DEFAULT 'customer',     -- customer | agent | admin
    approval_status TEXT NOT NULL DEFAULT 'approved',     -- agents start 'pending'
    business_name   TEXT,
    experience_level TEXT,
    primary_goal    TEXT,
    email_verified  INTEGER NOT NULL DEFAULT 0,
    verify_token    TEXT,
    marketing_opt_in INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- One events table powers all tracking + the admin funnel (see docs/TRACING.md).
CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    visitor_id  TEXT,                                     -- anonymous id from tracker.js
    user_id     INTEGER,                                  -- nullable; filled after login back-fill
    event_name  TEXT NOT NULL,
    props       TEXT,                                     -- JSON string
    url         TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_events_visitor ON events(visitor_id);
CREATE INDEX IF NOT EXISTS idx_events_user ON events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_name ON events(event_name);

-- Per-audience webinar configuration. Editable by admin without code changes.
CREATE TABLE IF NOT EXISTS webinar_config (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    audience             TEXT NOT NULL UNIQUE,            -- customer | agent
    title                TEXT NOT NULL,
    youtube_id           TEXT NOT NULL,
    duration_seconds     INTEGER NOT NULL DEFAULT 3120,   -- ~52 min
    interval_minutes     INTEGER NOT NULL DEFAULT 15,     -- JIT cadence
    lead_minutes         INTEGER NOT NULL DEFAULT 0,
    course_reveal_seconds INTEGER NOT NULL DEFAULT 1200,  -- $35 course CTA at 20:00
    offer_reveal_seconds INTEGER NOT NULL DEFAULT 2520,   -- coaching CTA at 42:00
    updated_at           TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Course content: modules + lessons (read by the course page).
CREATE TABLE IF NOT EXISTS modules (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    audience    TEXT NOT NULL DEFAULT 'customer',         -- customer | agent
    title       TEXT NOT NULL,
    summary     TEXT,
    sort_order  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS lessons (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id       INTEGER NOT NULL REFERENCES modules(id),
    title           TEXT NOT NULL,
    body            TEXT,
    video_id        TEXT,
    duration_minutes INTEGER NOT NULL DEFAULT 5,
    sort_order      INTEGER NOT NULL DEFAULT 0
);

-- Coaching booking requests (the $75 single + $200 6-month package).
CREATE TABLE IF NOT EXISTS coaching_requests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id),
    offer_code      TEXT NOT NULL,                        -- single_30 | package_6mo
    requested_date  TEXT,
    requested_slot  TEXT,                                 -- e.g. "1:00 PM ET"
    status          TEXT NOT NULL DEFAULT 'requested',    -- requested | confirmed | cancelled
    notes           TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Entitlements / purchases. Created only by verified payment flow (stubbed for now).
CREATE TABLE IF NOT EXISTS course_purchases (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(id),
    product_code  TEXT NOT NULL,                          -- course_35 | coaching_75 | coaching_200
    amount_cents  INTEGER NOT NULL DEFAULT 0,
    status        TEXT NOT NULL DEFAULT 'pending',        -- pending | active | refunded
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
