# PUBLIC_VIEW_CHANGES.md — what changes when a page is viewable without login

This is the security/compliance map for "what is safe to serve to an anonymous
visitor." Read it before exposing any new page or field.

## Page-by-page: public vs auth-gated

| Page | Route | Public? | Notes |
|------|-------|---------|-------|
| Landing | `/` | ✅ public | Marketing only. No prices implying guarantees. |
| Customer funnel | `/customer` | ✅ public | CTA → register/login. |
| Agent funnel | `/agent` | ✅ public | Mention pending approval, no guarantees. |
| FAQ | `/faq` | ✅ public | "Pre-recorded", "no guarantees". |
| Disclosures/Privacy/Terms | `/disclosures` | ✅ public | Required legal posture. |
| A2P explainer | `/a2p` | ✅ public | No customer data. |
| Login (customer/agent) | `/login/*` | ✅ public | Forms only. Generic auth errors. |
| Register (customer/agent) | `/register/*` | ✅ public | Forms only. |
| Verify email | `/verify-email` | ✅ public | Consumes a single-use token. |
| Customer dashboard | `/customer/dashboard` | 🔒 customer | Redirects anon → `/login/customer`. |
| Agent dashboard | `/agent/dashboard` | 🔒 agent | Redirects anon → `/login/agent`. |
| Admin dashboard | `/admin` | 🔒 admin | Redirects non-admin away. Never linked publicly. |
| Webinar room | `/webinar/*` | 🔒 logged-in | Video id fetched from API, not in static HTML. |
| Coaching | `/coaching` | 🔒 logged-in | Checkout disabled (503). |
| Course | `/course` | 🔒 logged-in | Lessons fetched from API. |

## Auth-guard redirect pattern

Every protected route runs `require_role(request, *roles)`:
- Not logged in → `303` redirect to the role-appropriate login (`/login/customer` or `/login/agent`).
- Logged in but wrong portal → redirect to the user's own dashboard (admins bypass).
- API equivalents return `401`/`403` JSON; the page JS redirects.

## NEVER expose in public HTML

- **Real video IDs / signed playback URLs.** The webinar video id comes from `/api/webinar/state` (server, behind login), defaulting to the env placeholder `WEBINAR_YOUTUBE_ID`. Production must use protected video (Cloudflare Stream/Mux/Vimeo OTT) — YouTube is inherently shareable.
- **Admin URLs / admin nav.** `/admin` is never linked from public pages.
- **Secrets.** `SECRET_KEY`, DB credentials, Stripe/Cal.com keys live only in `.env` (gitignored).
- **Other users' data.** Admin endpoints are role-checked server-side; no PII in client bundles.
- **Internal IDs in guessable links.** Use signed tokens (HMAC / itsdangerous) for any emailed deep link.

## Form hardening (public forms: register, login, coaching request)

- **Rate limit** every public POST (per-IP + per-email). TODO: add a limiter (e.g. SlowAPI / reverse-proxy limit). Currently not implemented — add before launch.
- **CAPTCHA** (hCaptcha/Turnstile) on register + login to slow credential-stuffing/bot signups. TODO.
- **Validation** server-side via Pydantic models (already enforced) — never trust client validation alone.
- **Generic auth errors** ("Incorrect email or password.") to avoid account enumeration.
- **Password policy**: min length enforced client + should be enforced server-side too (TODO: add length check in `/api/register/*`).

## Secure cookie flags

The session cookie (`tn_session`) is:
- `HttpOnly` (no JS access),
- `SameSite=Lax`,
- `Secure` when `COOKIE_SECURE=true` (set true behind HTTPS in prod),
- signed + timed via `itsdangerous` (14-day max age). It contains only the user id.

## Security headers (set in `main.py` middleware)

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Content-Security-Policy` — currently permissive (allows the CDN libs + inline Alpine + YouTube embed). **Production hardening:** move to nonce/hashed scripts, drop `'unsafe-eval'`, and pin exact CDN origins.

## 4-step "is this safe to be public?" test

1. **Does the page render any user-specific or paid data?** If yes → must be auth-gated.
2. **Does the HTML/JS contain a secret, real video id, admin URL, or internal id?** If yes → move it server-side / behind login.
3. **Can the marketing copy be read as a guarantee or a misleading claim?** If yes → rewrite (see `COMPLIANCE_CHECKLIST.md`).
4. **Is every public form rate-limited, validated server-side, and bot-resistant?** If no → add it before exposing.
