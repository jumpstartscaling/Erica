# TRACING.md — user tracing, events, funnel, and the login back-fill trick

One drop-in script, one endpoint, one table. No third-party analytics, no charting library.

## 1. `tracker.js` (on every page)

Loaded via `<script src="/static/js/tracker.js">`. It:

- Assigns an anonymous **`visitor_id`** and stores it in **both** `localStorage`
  and a `tn_visitor` cookie. The cookie matters: the server reads it during the
  login back-fill even if the client forgets to send it.
- Auto-fires **`page_view`** on `DOMContentLoaded`.
- Auto-fires a click event for any element with **`data-track="name"`** (capturing
  the trimmed text + `href`).
- Sends via **`navigator.sendBeacon`** (fallback: `fetch(..., {keepalive:true})`),
  so analytics **never block or break the page**.
- Exposes `window.TN.track(name, props)` for custom events (used by `webinar.js`).

## 2. `POST /api/track` → one `events` table

```sql
events (
  id, visitor_id, user_id /* nullable */, event_name, props /* json */, url, created_at
)
```

The endpoint reads the current session (if any) and stamps `user_id` when the
visitor is already logged in; otherwise `user_id` is NULL and gets back-filled later.

## 3. The login back-fill trick

On `register` and `login`, the server runs:

```sql
UPDATE events SET user_id = ? WHERE visitor_id = ? AND user_id IS NULL;
```

This associates **all prior anonymous events** for that browser with the now-known
user. Result: the admin funnel shows the full **anonymous → signup → purchase**
journey, not just post-login activity. The `visitor_id` is taken from the request
(`tn_visitor` cookie or the body field), which the client sends with the auth call.

## 4. Admin funnel (Tailwind bars, no chart lib)

`GET /api/admin/funnel` returns ordered steps with counts and a `pct` (relative to
the top step). The admin page renders each as a `<div>` whose width is the `pct`:

```
[ Visited a page         ] 100%
[ Clicked a track CTA    ]  62%
[ Registered (customer)  ]  31%
[ Logged in              ]  24%
[ Entered webinar        ]  18%
[ Clicked coaching offer ]   7%
[ Started checkout       ]   3%
```

Default funnel steps (see `FUNNEL_STEPS` in `main.py`): `page_view`, `cta_click`,
`register_customer`, `register_agent`, `login`, `webinar_state`, `course_cta`,
`coaching_cta`, `checkout_start`, `coaching_request`.

## 5. Event name conventions

- Page-level auto: `page_view`.
- CTA clicks: `cta_click` (with `data-cta` in props) and named clicks via `data-track`.
- Auth: `register_customer`, `register_agent`, `login`, `email_verified`.
- Webinar: `webinar_enter`, `webinar_join`, `offer_reveal`, `webinar_state`.
- Offers: `course_cta`, `coaching_cta`, `checkout_start`, `coaching_request`.

Keep names stable — the funnel and any future dashboards key off them.
