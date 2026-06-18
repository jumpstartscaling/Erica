# API_SPEC.md — endpoint reference

Base URL (dev): `http://localhost:8000`. All JSON bodies are `application/json`.
Auth is a signed httponly cookie (`tn_session`); send cookies with requests.

## HTML page routes (return HTML)

`GET /`, `/customer`, `/agent`, `/faq`, `/disclosures`, `/a2p`,
`/login/customer`, `/login/agent`, `/register/customer`, `/register/agent`,
`/verify-email`, `/customer/dashboard` 🔒, `/agent/dashboard` 🔒, `/admin` 🔒,
`/webinar/customer` 🔒, `/webinar/agent` 🔒, `/coaching` 🔒, `/course` 🔒.

🔒 = auth-guarded; unauthenticated requests get a `303` redirect to the right login.

## Auth

### `POST /api/register/customer`
Body: `{ first_name, last_name?, email, password, marketing_opt_in?, visitor_id? }`
→ `200 { ok, redirect:"/verify-email", verify_token }` · `409` if email exists.
Side effects: creates user (role `customer`, `email_verified=0`), prints verify link to console, back-fills + records `register_customer`.

### `POST /api/register/agent`
Body: `{ first_name, last_name?, email, password, business_name?, experience_level?, primary_goal?, marketing_opt_in?, visitor_id? }`
→ same shape. Creates role `agent`, `approval_status='pending'`.

### `POST /api/login`
Body: `{ email, password, expected_role?, visitor_id? }`
→ `200 { ok, redirect, role }` and sets session cookie.
→ `401 { ok:false, error }` on bad credentials.
→ `403 { ok:false, wrong_portal:true, error, redirect }` if logging into the wrong portal (admins bypass this check).
Side effects: back-fills anonymous events, records `login`.

### `POST /api/logout`
→ `200 { ok, redirect:"/" }`, clears cookie.

### `GET /api/verify?token=...`
→ `200 { ok, email }` (marks verified, clears token) · `400` on bad token.

### `GET /api/me`
→ `200 { ok, authenticated:true, user }` · `401` if not logged in.

## Tracking

### `POST /api/track`
Body: `{ visitor_id, event_name, props?, url? }` → `200 { ok }`.
Stamps `user_id` if a session is present. Designed for `navigator.sendBeacon`.

## Webinar (server-clock sync)

### `GET /api/time`
→ `{ server_now_ms }` — authoritative clock for the synced-now loop.

### `GET /api/webinar/state?audience=customer|agent`
→ `{ audience, title, youtube_id, duration_seconds, server_now_ms,
      session_start_ms, next_session_start_ms, elapsed_seconds, state,
      course_reveal_seconds, offer_reveal_seconds, interval_minutes, prices }`.
`state` ∈ `waiting | live | ended`. `youtube_id` defaults to env `WEBINAR_YOUTUBE_ID`.
Evergreen model: a new screening starts every `duration_seconds`; the browser
computes the video offset as `serverNow - session_start` and trusts the **server**
clock, so refreshing/clock-tampering can't change offer timing.

## Course

### `GET /api/lessons?audience=customer|agent`
→ `{ ok, audience, modules:[ { id, title, summary, sort_order, lessons:[ {id,title,body,video_id,duration_minutes,sort_order} ] } ] }`.

## Coaching + payments (STUBBED)

### `POST /api/checkout`
Body: `{ product_code, visitor_id? }`
→ **`503 { ok:false, error }`** while `CHECKOUT_ENABLED=false` (default).
→ when enabled: `401` if not logged in, else `200 { ok, checkout_url, product_code }` (placeholder). TODO: real Stripe.

### `POST /api/coaching/request`
Body: `{ offer_code, requested_date?, requested_slot?, notes? }` (login required)
→ `200 { ok, message }`. Inserts a `coaching_requests` row. TODO: Cal.com embed + webhook, server-side 1–6 PM ET validation.

## Admin (role: admin)

### `GET /api/admin/stats` → `{ ok, stats:{ users_total, verified_accounts, customers, agents, agents_pending, events_total, webinar_starts, coaching_requests, purchases } }`
### `GET /api/admin/funnel` → `{ ok, steps:[ { event_name, label, count, visitors, pct } ] }`
### `GET /api/admin/users` → `{ ok, users:[...] }` (latest 200)

Non-admins get `403`.

## Health

### `GET /healthz` → `{ ok, ts }`
