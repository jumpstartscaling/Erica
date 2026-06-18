# Tranzformation Nation

A runnable wireframe for a credit-**education** funnel: a free, pre-recorded
webinar funnel, a $35 course, and two educational coaching upsells ($75 single
30-min session, $200 6-month package). Two audience tracks — **customer**
(improve your own credit) and **agent** (build a credit-education business) —
plus an **admin**.

> Educational only. Not legal/financial/credit-repair advice. No guarantees.
> Payments are **stubbed** behind a flag pending legal review. See
> `docs/COMPLIANCE_CHECKLIST.md`.

## Stack (locked)

- **Backend:** FastAPI + Uvicorn — one process serves the JSON API **and** the HTML pages.
- **Frontend:** static HTML + Tailwind (CDN) + Alpine.js (CDN) + Lucide (CDN). No npm, no build step.
- **Database:** SQLite by default (stdlib `sqlite3`, zero setup). Swappable to Postgres via `DATABASE_URL` — all DB access is in `backend/db.py`.

## Run it (one command)

```bash
bash scripts/initdb.sh   # create + seed the SQLite DB (optional; run.sh also auto-inits)
bash scripts/run.sh      # → http://localhost:8000
```

`run.sh` creates a virtualenv, installs `backend/requirements.txt`, copies
`backend/.env.example` → `backend/.env` if missing, and starts Uvicorn.

Manual alternative:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
cd backend && uvicorn main:app --reload   # http://localhost:8000
```

## Demo login

- **Admin:** `admin@example.com` / `password` → `/admin` (real bcrypt hash, works out of the box).
- Create your own **customer**/**agent** accounts via `/register/customer` and `/register/agent`.
  Email is stubbed — the verification link prints to the **server console** (and, for dev convenience, registration redirects to `/verify-email?token=...`).

## Pages (all wired to real routes)

Public: `/` landing, `/customer`, `/agent`, `/faq`, `/disclosures`, `/a2p`.
Auth: `/login/customer`, `/login/agent`, `/register/customer`, `/register/agent`, `/verify-email`.
Logged-in: `/customer/dashboard`, `/agent/dashboard`, `/admin`, `/webinar/customer`, `/webinar/agent`, `/coaching`, `/course`.

## The webinar room (the only "smart" page)

Server-clock JIT/evergreen sync: the browser asks the **server** for the current
time + the computed session start, then trusts the **server** clock — so
refreshing or skipping ahead can't cheat the offer timing. Flow: countdown →
**click-to-join** (autoplay-safe) → YouTube IFrame seeked to `serverNow −
sessionStart` → timed offer CTAs reveal → "ended" state. Plus a rotating,
compliance-safe **credit tips ticker**. The YouTube id is a placeholder from
`WEBINAR_YOUTUBE_ID` (default `dQw4w9WgXcQ`); images use `picsum.photos`.

## Tracking

`tracker.js` (on every page) assigns an anonymous `visitor_id`, auto-fires
`page_view` + `data-track` clicks, and uses `sendBeacon`. One `POST /api/track` →
one `events` table. On login the server **back-fills** prior anonymous events to
the user, so the admin funnel shows the full anonymous → signup → purchase
journey (rendered as **Tailwind bar divs**, no charting library).

## Safety rails

- **Payments stubbed:** `/api/checkout` returns **503** until `CHECKOUT_ENABLED=true` *and* legal sign-off.
- **Admin never has public registration.** Seed/CLI only.
- **Compliance-safe copy** on all public pages; dangerous copy lives only in `docs/COMPLIANCE_CHECKLIST.md` as "what to fix".
- **Secure session cookie** (HttpOnly, SameSite=Lax, signed; Secure via `COOKIE_SECURE`). Security headers + permissive CSP (tighten for prod).

## Docs

- `docs/BUILD_PLAN.md` — full plan + ticket order.
- `docs/PUBLIC_VIEW_CHANGES.md` — public vs auth-gated map, never-expose list, form hardening, the 4-step safety test.
- `docs/TRACING.md` — tracker + events + admin funnel + login back-fill.
- `docs/COMPLIANCE_CHECKLIST.md` — CROA/TSR/FTC/state CSO, dangerous copy fixes, the $200 advance-payment issue.
- `docs/API_SPEC.md` — endpoint reference.
- `docs/ENV_SETUP.md` — env vars + the SQLite↔Postgres swap.
- `templates/` — PAGE, ENDPOINT, MIGRATION, PR, TICKET, CREDIT_TIPS.

## TODO (deferred, marked in code)

- **Stripe** — real Checkout Session + verified webhook → create entitlements (don't unlock on success URL alone).
- **Cal.com** — hosted booking embed + signed webhook; validate 1–6 PM ET server-side.
- **Email** — replace the console stub with Resend/SMTP (verification + transactional + marketing).
- **Postgres** — set `DATABASE_URL`, uncomment `psycopg`, port schema types (`docs/ENV_SETUP.md`).
- **Protected video** — move off YouTube to signed/protected playback for production.
- **Form hardening** — add rate limiting + CAPTCHA on public forms.
