# BUILD_PLAN.md — Tranzformation Nation

A hand-it-to-a-coder implementation plan. The stack is locked; no theory.

## Locked stack

- **Backend:** FastAPI + Uvicorn — one process serves BOTH the JSON API and the HTML pages.
- **Frontend:** static HTML + Tailwind (CDN) + Alpine.js (CDN) + Lucide (CDN). No npm, no build step. Every front-end lib is a `<script>`/`<link>` tag.
- **Database:** SQLite by default (stdlib `sqlite3`, zero setup). Swappable to Postgres via `DATABASE_URL` (see `db.py` + `ENV_SETUP.md`).
- **Run:** `bash scripts/run.sh` → http://localhost:8000. Seed with `bash scripts/initdb.sh`.

## Directory map

```
backend/    main.py (routes+API), auth.py (bcrypt+sessions), db.py (SQLite/PG swap),
            schema.sql, seed.sql, requirements.txt, .env.example
frontend/
  pages/    landing, funnel_customer, funnel_agent, faq, disclosures, a2p,
            login_customer, login_agent, register_customer, register_agent, verify_email,
            dashboard_customer, dashboard_agent, dashboard_admin,
            webinar, coaching, course
  static/   js/tracker.js, js/webinar.js, js/credit_tips.js, css/app.css
docs/       this file + PUBLIC_VIEW_CHANGES, TRACING, COMPLIANCE_CHECKLIST, API_SPEC, ENV_SETUP
templates/  PAGE, ENDPOINT, MIGRATION, PR, TICKET, CREDIT_TIPS
scripts/    run.sh, initdb.sh
```

## Pages → routes → access

| # | Page | Route | Access |
|---|------|-------|--------|
| 1 | Main landing | `GET /` | public |
| 2 | Customer funnel/track | `GET /customer` | public |
| 3 | Agent funnel/track | `GET /agent` | public |
| — | FAQ | `GET /faq` | public |
| — | Disclosures/Privacy/Terms | `GET /disclosures` | public |
| — | A2P explainer | `GET /a2p` | public |
| 4 | Customer login | `GET /login/customer` | public |
| 5 | Agent login | `GET /login/agent` | public |
| 6 | Customer register | `GET /register/customer` | public |
| 7 | Agent register | `GET /register/agent` | public |
| — | Verify email | `GET /verify-email` | public |
| 8 | Customer dashboard | `GET /customer/dashboard` | customer |
| 9 | Agent dashboard | `GET /agent/dashboard` | agent |
| 10 | Admin dashboard | `GET /admin` | admin |
| 11 | Webinar room | `GET /webinar/customer`, `GET /webinar/agent` | logged-in |
| 12 | Coaching offer/booking | `GET /coaching` | logged-in |
| 13 | Course/lessons | `GET /course` | logged-in |

## Ticket-by-ticket build order

1. **TN-1 Skeleton + DB** — `db.py`, `schema.sql`, `seed.sql`, `init_db()`; `scripts/initdb.sh`, `scripts/run.sh`. *Done.*
2. **TN-2 Auth** — `auth.py` (bcrypt hash/verify, itsdangerous signed cookie), register/login/logout/verify endpoints, auth-guard redirect pattern. *Done.*
3. **TN-3 Static serving + pages** — FastAPI routes return HTML files; mount `/static`. *Done.*
4. **TN-4 Tracking** — `tracker.js` on every page; `POST /api/track` → `events`; login back-fill. *Done.*
5. **TN-5 Webinar** — `/api/time`, `/api/webinar/state` (server-clock JIT), `webinar.js` (countdown → click-to-join → synced YouTube → timed offers → ended), tips ticker. *Done.*
6. **TN-6 Course** — `/api/lessons` reads modules/lessons; `course.html`. *Done.*
7. **TN-7 Coaching (stubbed)** — `/api/checkout` 503 behind `CHECKOUT_ENABLED`; `/api/coaching/request`. *Done.*
8. **TN-8 Admin analytics** — `/api/admin/stats`, `/api/admin/funnel` (Tailwind bars), `/api/admin/users`. *Done.*
9. **TN-9 Docs + compliance copy pass** — this folder. *Done.*

## TODO (deferred, clearly marked in code)

- **Stripe** — real Checkout Session + verified webhook → create `course_purchases`/entitlement. Do not unlock on success URL alone. (`main.py` `/api/checkout`)
- **Cal.com** — replace the request form with the hosted embed + signed webhook; validate 1–6 PM ET server-side. (`main.py` `/api/coaching/request`)
- **Email** — replace the console stub with Resend/SMTP for verification + transactional/marketing flows. (`main.py` `_print_verification_email`)
- **Postgres** — flip `DATABASE_URL`, uncomment `psycopg`, port the schema types (see `ENV_SETUP.md`).
- **Protected video** — YouTube is a placeholder and is not secure; move to Cloudflare Stream / Mux / Vimeo OTT with signed playback for production.
