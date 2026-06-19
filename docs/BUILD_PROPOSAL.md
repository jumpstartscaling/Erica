# Tranzformation Nation — Build Proposal

## Overview

A credit-education funnel platform: free pre-recorded webinar → $35 course → $75 single coaching session → $200 6-month coaching package. Two audience tracks (customer/agent) plus admin. Currently deployed at `tranzformation-nation.jumpstartscaling.com`.

---

## 1. Architecture

| Layer | Technology | Status |
|-------|-----------|--------|
| Backend | FastAPI + Uvicorn (single process) | ✅ Built |
| Frontend | Static HTML + Tailwind CSS (CDN) + Alpine.js + Lucide icons | ✅ Built |
| Database | SQLite (default) / Postgres (swap via DATABASE_URL) | ✅ Built |
| Auth | bcrypt passwords + itsdangerous signed httponly cookies | ✅ Built |
| Tracking | Anonymous visitor_id + sendBeacon → events table | ✅ Built |
| Webinar | Server-clock JIT/evergreen sync (YouTube IFrame) | ✅ Built |
| Payments | **Stubbed** — returns 503 | ❌ TODO |
| Email | **Stubbed** — prints to console | ❌ TODO |
| Booking | **Stubbed** — inserts coaching_requests row | ❌ TODO |
| Video | YouTube (placeholder) | ❌ TODO |

### Directory Structure

```
backend/
  main.py          — All routes + API logic (676 lines)
  auth.py          — bcrypt passwords, signed session cookies
  db.py            — SQLite/Postgres abstraction layer
  schema.sql       — 7 tables: users, events, webinar_config, modules, lessons, coaching_requests, course_purchases
  seed.sql         — Demo admin, webinar config, course modules/lessons
  requirements.txt — fastapi, uvicorn, pydantic, bcrypt, itsdangerous
  .env.example     — Environment template

frontend/
  pages/           — 17 HTML pages (all auth-guarded where appropriate)
  static/
    js/
      nav.js       — Shared navigation dropdown (5 sections)
      tracker.js   — Anonymous analytics (page_view + click tracking)
      webinar.js   — Server-synced YouTube player + timed offers
      credit_tips.js — Compliance-safe rotating tips
    css/
      app.css      — Custom styles

docs/
  BUILD_PLAN.md        — Original implementation plan
  BUILD_PROPOSAL.md    — This document
  API_SPEC.md          — Endpoint reference
  COMPLIANCE_CHECKLIST.md — CROA/TSR/FTC/state law notes
  ENV_SETUP.md         — Environment variables + Postgres swap
  PUBLIC_VIEW_CHANGES.md — Auth-gating map
  TRACING.md           — Analytics design

scripts/
  run.sh           — One-command startup
  initdb.sh        — Create + seed database
```

---

## 2. Page Inventory (17 pages)

### Public (no login required)
| Route | Page | Purpose |
|-------|------|---------|
| `/` | landing.html | Main marketing landing page |
| `/customer` | funnel_customer.html | Customer track sales page |
| `/agent` | funnel_agent.html | Agent track sales page |
| `/faq` | faq.html | Accordion FAQ |
| `/disclosures` | disclosures.html | Disclosures, Privacy, Terms |
| `/a2p` | a2p.html | SMS/A2P messaging info |

### Auth (login/register)
| Route | Page | Purpose |
|-------|------|---------|
| `/login/customer` | login_customer.html | Customer login form |
| `/login/agent` | login_agent.html | Agent login form |
| `/register/customer` | register_customer.html | Customer registration |
| `/register/agent` | register_agent.html | Agent registration |
| `/verify-email` | verify_email.html | Email verification status |

### Logged-in (auth-guarded, 303 redirect if not authenticated)
| Route | Page | Purpose |
|-------|------|---------|
| `/customer/dashboard` | dashboard_customer.html | Customer training hub |
| `/agent/dashboard` | dashboard_agent.html | Agent business tools |
| `/admin` | dashboard_admin.html | Admin analytics + users |
| `/webinar/customer` | webinar.html | Customer webinar room |
| `/webinar/agent` | webinar.html | Agent webinar room |
| `/coaching` | coaching.html | Coaching pricing + request |
| `/course` | course.html | Course lessons (LMS) |

---

## 3. API Endpoints

### Auth
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/register/customer` | Create customer account |
| POST | `/api/register/agent` | Create agent account (pending approval) |
| POST | `/api/login` | Authenticate, set session cookie |
| POST | `/api/logout` | Clear session |
| GET | `/api/verify?token=` | Verify email address |
| GET | `/api/me` | Get current user |

### Tracking
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/track` | Record analytics event |

### Webinar
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/time` | Server clock (for sync) |
| GET | `/api/webinar/state?audience=` | Webinar state + config |

### Course
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/lessons?audience=` | Modules + lessons |

### Coaching / Payments (STUBBED)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/checkout` | **Returns 503** — needs real payment |
| POST | `/api/coaching/request` | Submit coaching time request |

### Admin (role: admin)
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/admin/stats` | Platform statistics |
| GET | `/api/admin/funnel` | Conversion funnel data |
| GET | `/api/admin/users` | User list (latest 200) |

### Health
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/healthz` | Health check |

---

## 4. Database Schema (7 tables)

### `users`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | Auto-increment |
| email | TEXT UNIQUE | Login identifier |
| password_hash | TEXT | bcrypt hash |
| first_name, last_name | TEXT | |
| role | TEXT | customer / agent / admin |
| approval_status | TEXT | approved (default) / pending (agents) |
| business_name | TEXT | Agent only |
| experience_level | TEXT | Agent only |
| primary_goal | TEXT | Agent only |
| email_verified | INTEGER | 0/1 |
| verify_token | TEXT | Email verification token |
| marketing_opt_in | INTEGER | 0/1 |
| created_at | TEXT | ISO datetime |

### `events`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| visitor_id | TEXT | Anonymous browser ID |
| user_id | INTEGER | Nullable, back-filled on login |
| event_name | TEXT | page_view, cta_click, register_*, login, etc. |
| props | TEXT | JSON string |
| url | TEXT | Page URL |
| created_at | TEXT | ISO datetime |

### `webinar_config`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| audience | TEXT | customer / agent |
| title | TEXT | Display title |
| youtube_id | TEXT | YouTube video ID |
| duration_seconds | INTEGER | ~52 min default |
| interval_minutes | INTEGER | JIT cadence |
| course_reveal_seconds | INTEGER | When $35 offer appears |
| offer_reveal_seconds | INTEGER | When coaching offer appears |

### `modules` / `lessons`
Course content hierarchy. Modules have many lessons. Both have `audience` and `sort_order`.

### `coaching_requests`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| user_id | INTEGER FK | |
| offer_code | TEXT | single_30 / package_6mo |
| requested_date, requested_slot | TEXT | |
| status | TEXT | requested / confirmed / cancelled |
| notes | TEXT | |
| created_at | TEXT | |

### `course_purchases`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| user_id | INTEGER FK | |
| product_code | TEXT | course_35 / coaching_75 / coaching_200 |
| amount_cents | INTEGER | |
| status | TEXT | pending / active / refunded |
| created_at | TEXT | |

---

## 5. Build Phases

### Phase 1: Foundation ✅ (Complete)
- FastAPI backend with all routes
- SQLite database with schema + seed data
- Auth system (bcrypt + signed cookies)
- 17 HTML pages with shared navigation
- Analytics tracking (anonymous + login back-fill)
- Server-clock webinar sync
- Course content API
- Coaching request system
- Admin dashboard with stats, funnel, users
- Security headers + CSP
- Deployed on spark-tms behind Caddy + Cloudflare Tunnel

### Phase 2: Real Payments (NEXT)
**Goal**: Replace stubbed `/api/checkout` with real payment processing.

**Options** (you mentioned Stripe, Square, PayPal):

#### Option A: Stripe Checkout (Recommended)
- Create Stripe account + API keys
- Add `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` to env
- Implement `POST /api/create-checkout-session`:
  - Accepts `product_code` (course_35, coaching_75, coaching_200)
  - Creates Stripe Checkout Session with `mode=payment`
  - Returns `checkout_url` → redirect user to Stripe
- Implement Stripe webhook endpoint `POST /api/stripe-webhook`:
  - Verify signature with `STRIPE_WEBHOOK_SECRET`
  - On `checkout.session.completed`:
    - Create `course_purchases` row with `status=active`
    - Record `purchase` event in analytics
    - Optionally send confirmation email
- Update coaching page to show real prices and redirect to Stripe
- Set `CHECKOUT_ENABLED=true` after legal review

**Files to modify**: `main.py`, `.env.example`, `requirements.txt` (add `stripe`)

#### Option B: Square Payment Links
- Create Square account
- Generate payment links for each product in Square Dashboard
- Store links in env vars: `SQUARE_COURSE_LINK`, `SQUARE_COACHING_75_LINK`, `SQUARE_COACHING_200_LINK`
- On checkout, redirect user to the pre-made Square payment link
- Square webhook or manual reconciliation for fulfillment

**Simpler but less control** — no dynamic pricing, no webhook verification in MVP.

#### Option C: PayPal Buy Now Buttons
- Create PayPal Business account
- Generate hosted buy-now button IDs for each product
- Embed PayPal buttons or redirect to PayPal checkout
- PayPal IPN (Instant Payment Notification) for fulfillment

**Files to modify**: `main.py`, coaching page HTML, `.env.example`

### Phase 3: Email (Transactional)
**Goal**: Replace console-stub email verification with real email.

- Add `RESEND_API_KEY` (or SMTP credentials) to env
- Install `resend` or `smtplib` package
- Replace `_print_verification_email()` with actual email send
- Add transactional email templates:
  - Email verification
  - Purchase receipt
  - Coaching request confirmation
  - Password reset (future)

### Phase 4: Booking (Cal.com)
**Goal**: Replace manual coaching request form with automated scheduling.

- Create Cal.com account
- Add `CALCOM_EMBED_LINK` and `CALCOM_WEBHOOK_SECRET` to env
- Embed Cal.com scheduling widget on coaching page
- Implement Cal.com webhook to confirm bookings
- Server-side validation: 1–6 PM ET time slots

### Phase 5: Protected Video
**Goal**: Replace public YouTube with secure playback.

- Options: Cloudflare Stream (signed URLs), Mux, Vimeo OTT
- Implement signed URL generation on the backend
- Update webinar page to use protected player
- Remove YouTube IFrame API dependency

### Phase 6: Postgres + Scaling
**Goal**: Swap SQLite for Postgres for production reliability.

- Provision Postgres database
- Set `DATABASE_URL` in env
- Uncomment `psycopg[binary]` in requirements.txt
- Port schema types (see `docs/ENV_SETUP.md`)
- Run ported schema + seed

---

## 6. Compliance Requirements (Pre-Launch)

From `docs/COMPLIANCE_CHECKLIST.md`:

1. ✅ No guarantees in copy
2. ✅ No "force / weapon / hack / overnight" language
3. ✅ States accurate negative info generally cannot be removed
4. ✅ States consumers can dispute themselves for free
5. ✅ Does not advise disputing accurate info
6. ✅ No CPN / EIN / false identity references
7. ✅ Webinar labeled "Pre-Recorded Training" / "Scheduled Premiere"
8. ✅ No SSNs or full credit reports collected
9. ❌ Attorney review of CROA / state CSO applicability
10. ❌ If CROA applies: contracts, disclosures, cancellation forms, compliant payment timing
11. ❌ $200 prepaid coaching package — may violate CROA advance-payment ban

**Before enabling payments**: Legal must determine whether the $200 prepaid coaching package is (a) an educational product, (b) a covered credit-repair service that cannot be prepaid, or (c) billable only after delivery.

---

## 7. Current Deployment

| Component | Detail |
|-----------|--------|
| Server | spark-tms (72.9.155.219) |
| Service | `tranzformation-nation.service` (systemd) |
| Port | 8008 |
| Domain | `tranzformation-nation.jumpstartscaling.com` |
| Reverse Proxy | Caddy (TLS internal) |
| Tunnel | Cloudflare (tunnel ID: 9cc908fc-...) |
| Runtime | Python 3.12, Uvicorn |
| Repo | `github.com/jumpstartscaling/Erica` |

---

## 8. Effort Estimates

| Phase | Estimated Effort | Dependencies |
|-------|-----------------|--------------|
| P1: Foundation | ✅ Complete | — |
| P2: Payments (Stripe) | 2-3 days | Legal review, Stripe account |
| P2: Payments (Square) | 1 day | Square account |
| P2: Payments (PayPal) | 1 day | PayPal Business account |
| P3: Email (Resend) | 1 day | Resend account |
| P4: Booking (Cal.com) | 1-2 days | Cal.com account |
| P5: Protected Video | 2-3 days | Cloudflare Stream / Mux account |
| P6: Postgres | 1 day | Postgres instance |
| Legal review | Variable | Attorney |

---

## 9. Recommended Next Steps

1. **Legal review** — Determine CROA/state CSO applicability before any payment work
2. **Stripe integration** — Most professional option, best webhook support
3. **Resend email** — Quick win, replaces console stub
4. **Cal.com booking** — Replaces manual coaching request form
5. **Protected video** — Only needed for production launch
6. **Postgres** — Only needed when SQLite concurrency becomes a bottleneck
