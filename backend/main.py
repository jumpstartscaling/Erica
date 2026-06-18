"""Tranzformation Nation -- single FastAPI process serving HTML pages + JSON API.

Run:  bash scripts/run.sh   ->  http://localhost:8000

Architecture (locked):
  - FastAPI + Uvicorn, one process.
  - Front-end is static HTML + Tailwind/Alpine/Lucide via CDN (no build step).
  - DB defaults to SQLite; swappable to Postgres via DATABASE_URL (see db.py).
  - Payments are STUBBED behind CHECKOUT_ENABLED (default false) -> /api/checkout 503.
"""

from __future__ import annotations

import json
import math
import os
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr

import auth
import db

# --------------------------------------------------------------------------- #
# Paths / config
# --------------------------------------------------------------------------- #
BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
PAGES_DIR = ROOT_DIR / "frontend" / "pages"
STATIC_DIR = ROOT_DIR / "frontend" / "static"

WEBINAR_YOUTUBE_ID = os.environ.get("WEBINAR_YOUTUBE_ID", "dQw4w9WgXcQ")
CHECKOUT_ENABLED = os.environ.get("CHECKOUT_ENABLED", "false").lower() == "true"
PRICE_COURSE = os.environ.get("PRICE_COURSE", "35")
PRICE_COACHING_SINGLE = os.environ.get("PRICE_COACHING_SINGLE", "75")
PRICE_COACHING_PACKAGE = os.environ.get("PRICE_COACHING_PACKAGE", "200")
APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:8000")

app = FastAPI(title="Tranzformation Nation", docs_url=None, redoc_url=None)


@app.on_event("startup")
def _startup() -> None:
    # Make sure the schema exists even if initdb.sh wasn't run.
    db.init_db()


# --------------------------------------------------------------------------- #
# Security headers (see docs/PUBLIC_VIEW_CHANGES.md -- tighten CSP for prod)
# --------------------------------------------------------------------------- #
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
    # Permissive CSP: the wireframe relies on CDN libs + inline Alpine expressions.
    # Production should move to hashed/nonce'd scripts and drop 'unsafe-eval'.
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com "
        "https://unpkg.com https://www.youtube.com https://s.ytimg.com; "
        "style-src 'self' 'unsafe-inline' https://unpkg.com https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data: https://picsum.photos https://*.picsum.photos "
        "https://placehold.co https://i.ytimg.com; "
        "frame-src https://www.youtube.com https://www.youtube-nocookie.com; "
        "connect-src 'self'",
    )
    return response


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def serve_page(name: str) -> HTMLResponse:
    path = PAGES_DIR / name
    return HTMLResponse(path.read_text())


def now_ms() -> int:
    return int(time.time() * 1000)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def login_redirect_for(role: str) -> str:
    if role == "agent":
        return "/login/agent"
    return "/login/customer"


def dashboard_for(role: str) -> str:
    if role == "admin":
        return "/admin"
    if role == "agent":
        return "/agent/dashboard"
    return "/customer/dashboard"


def require_role(request: Request, *roles: str):
    """Return (user, None) if allowed, or (None, RedirectResponse) if not."""
    user = auth.current_user(request)
    if user is None:
        target = login_redirect_for(roles[0] if roles else "customer")
        return None, RedirectResponse(target, status_code=303)
    if roles and user["role"] not in roles and user["role"] != "admin":
        # Logged in but wrong portal -> send to their own dashboard.
        return None, RedirectResponse(dashboard_for(user["role"]), status_code=303)
    return user, None


# --------------------------------------------------------------------------- #
# Public HTML pages
# --------------------------------------------------------------------------- #
@app.get("/", response_class=HTMLResponse)
def page_landing():
    return serve_page("landing.html")


@app.get("/customer", response_class=HTMLResponse)
def page_funnel_customer():
    return serve_page("funnel_customer.html")


@app.get("/agent", response_class=HTMLResponse)
def page_funnel_agent():
    return serve_page("funnel_agent.html")


@app.get("/faq", response_class=HTMLResponse)
def page_faq():
    return serve_page("faq.html")


@app.get("/disclosures", response_class=HTMLResponse)
def page_disclosures():
    return serve_page("disclosures.html")


@app.get("/a2p", response_class=HTMLResponse)
def page_a2p():
    return serve_page("a2p.html")


# Auth pages
@app.get("/login/customer", response_class=HTMLResponse)
def page_login_customer():
    return serve_page("login_customer.html")


@app.get("/login/agent", response_class=HTMLResponse)
def page_login_agent():
    return serve_page("login_agent.html")


@app.get("/register/customer", response_class=HTMLResponse)
def page_register_customer():
    return serve_page("register_customer.html")


@app.get("/register/agent", response_class=HTMLResponse)
def page_register_agent():
    return serve_page("register_agent.html")


@app.get("/verify-email", response_class=HTMLResponse)
def page_verify_email():
    return serve_page("verify_email.html")


# Logged-in pages (auth-guarded)
@app.get("/customer/dashboard", response_class=HTMLResponse)
def page_customer_dashboard(request: Request):
    user, redirect = require_role(request, "customer")
    return redirect or serve_page("dashboard_customer.html")


@app.get("/agent/dashboard", response_class=HTMLResponse)
def page_agent_dashboard(request: Request):
    user, redirect = require_role(request, "agent")
    return redirect or serve_page("dashboard_agent.html")


@app.get("/admin", response_class=HTMLResponse)
def page_admin_dashboard(request: Request):
    user, redirect = require_role(request, "admin")
    return redirect or serve_page("dashboard_admin.html")


@app.get("/webinar/customer", response_class=HTMLResponse)
def page_webinar_customer(request: Request):
    user, redirect = require_role(request, "customer", "agent")
    return redirect or serve_page("webinar.html")


@app.get("/webinar/agent", response_class=HTMLResponse)
def page_webinar_agent(request: Request):
    user, redirect = require_role(request, "customer", "agent")
    return redirect or serve_page("webinar.html")


@app.get("/coaching", response_class=HTMLResponse)
def page_coaching(request: Request):
    user, redirect = require_role(request, "customer", "agent")
    return redirect or serve_page("coaching.html")


@app.get("/course", response_class=HTMLResponse)
def page_course(request: Request):
    user, redirect = require_role(request, "customer", "agent")
    return redirect or serve_page("course.html")


# --------------------------------------------------------------------------- #
# API models
# --------------------------------------------------------------------------- #
class CustomerRegister(BaseModel):
    first_name: str
    last_name: str = ""
    email: EmailStr
    password: str
    marketing_opt_in: bool = False
    visitor_id: Optional[str] = None


class AgentRegister(BaseModel):
    first_name: str
    last_name: str = ""
    email: EmailStr
    password: str
    business_name: str = ""
    experience_level: str = ""
    primary_goal: str = ""
    marketing_opt_in: bool = False
    visitor_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    expected_role: Optional[str] = None
    visitor_id: Optional[str] = None


class TrackEvent(BaseModel):
    visitor_id: str
    event_name: str
    props: Optional[dict] = None
    url: Optional[str] = None


class CheckoutRequest(BaseModel):
    product_code: str
    visitor_id: Optional[str] = None


class CoachingRequest(BaseModel):
    offer_code: str
    requested_date: Optional[str] = None
    requested_slot: Optional[str] = None
    notes: Optional[str] = None


# --------------------------------------------------------------------------- #
# Tracking
# --------------------------------------------------------------------------- #
def record_event(visitor_id: Optional[str], user_id: Optional[int], name: str,
                 props: Optional[dict] = None, url: Optional[str] = None) -> None:
    db.insert(
        "INSERT INTO events (visitor_id, user_id, event_name, props, url, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (visitor_id, user_id, name, json.dumps(props or {}), url, utc_now_iso()),
    )


def backfill_visitor(visitor_id: Optional[str], user_id: int) -> None:
    """Associate all prior anonymous events for this visitor with the user."""
    if not visitor_id:
        return
    db.execute(
        "UPDATE events SET user_id = ? WHERE visitor_id = ? AND user_id IS NULL",
        (user_id, visitor_id),
    )


@app.post("/api/track")
async def api_track(request: Request, event: TrackEvent):
    user = auth.current_user(request)
    record_event(
        event.visitor_id,
        user["id"] if user else None,
        event.event_name,
        event.props,
        event.url,
    )
    return {"ok": True}


# --------------------------------------------------------------------------- #
# Auth API
# --------------------------------------------------------------------------- #
def _visitor_from(request: Request, body_visitor: Optional[str]) -> Optional[str]:
    return body_visitor or request.cookies.get("tn_visitor")


@app.post("/api/register/customer")
async def api_register_customer(request: Request, payload: CustomerRegister):
    existing = db.query_one("SELECT id FROM users WHERE email = ?", (payload.email,))
    if existing:
        return JSONResponse({"ok": False, "error": "An account with that email already exists."}, status_code=409)

    token = secrets.token_urlsafe(24)
    user_id = db.insert(
        "INSERT INTO users (email, password_hash, first_name, last_name, role, "
        "approval_status, email_verified, verify_token, marketing_opt_in, created_at) "
        "VALUES (?, ?, ?, ?, 'customer', 'approved', 0, ?, ?, ?)",
        (payload.email, auth.hash_password(payload.password), payload.first_name,
         payload.last_name, token, 1 if payload.marketing_opt_in else 0, utc_now_iso()),
    )
    visitor = _visitor_from(request, payload.visitor_id)
    backfill_visitor(visitor, user_id)
    record_event(visitor, user_id, "register_customer", {"email": payload.email})
    _print_verification_email(payload.email, token)
    return {"ok": True, "redirect": "/verify-email", "verify_token": token}


@app.post("/api/register/agent")
async def api_register_agent(request: Request, payload: AgentRegister):
    existing = db.query_one("SELECT id FROM users WHERE email = ?", (payload.email,))
    if existing:
        return JSONResponse({"ok": False, "error": "An account with that email already exists."}, status_code=409)

    token = secrets.token_urlsafe(24)
    user_id = db.insert(
        "INSERT INTO users (email, password_hash, first_name, last_name, role, "
        "approval_status, business_name, experience_level, primary_goal, "
        "email_verified, verify_token, marketing_opt_in, created_at) "
        "VALUES (?, ?, ?, ?, 'agent', 'pending', ?, ?, ?, 0, ?, ?, ?)",
        (payload.email, auth.hash_password(payload.password), payload.first_name,
         payload.last_name, payload.business_name, payload.experience_level,
         payload.primary_goal, token, 1 if payload.marketing_opt_in else 0, utc_now_iso()),
    )
    visitor = _visitor_from(request, payload.visitor_id)
    backfill_visitor(visitor, user_id)
    record_event(visitor, user_id, "register_agent", {"email": payload.email})
    _print_verification_email(payload.email, token)
    return {"ok": True, "redirect": "/verify-email", "verify_token": token}


@app.post("/api/login")
async def api_login(request: Request, payload: LoginRequest):
    user = db.query_one(
        "SELECT id, email, password_hash, role FROM users WHERE email = ?",
        (payload.email,),
    )
    if not user or not auth.verify_password(payload.password, user["password_hash"]):
        return JSONResponse({"ok": False, "error": "Incorrect email or password."}, status_code=401)

    role = user["role"]
    # Friendly wrong-portal message (admins may log in from any portal).
    if payload.expected_role and role != "admin" and role != payload.expected_role:
        portal = "Customer" if role == "customer" else "Agent"
        return JSONResponse(
            {
                "ok": False,
                "wrong_portal": True,
                "error": f"This account belongs to the {portal} Portal. Continue to {portal} Login.",
                "redirect": login_redirect_for(role),
            },
            status_code=403,
        )

    visitor = _visitor_from(request, payload.visitor_id)
    backfill_visitor(visitor, user["id"])
    record_event(visitor, user["id"], "login", {"role": role})

    redirect = dashboard_for(role)
    response = JSONResponse({"ok": True, "redirect": redirect, "role": role})
    auth.set_session_cookie(response, user["id"])
    return response


@app.post("/api/logout")
async def api_logout():
    response = JSONResponse({"ok": True, "redirect": "/"})
    auth.clear_session_cookie(response)
    return response


@app.get("/api/verify")
async def api_verify(token: str):
    user = db.query_one("SELECT id, email FROM users WHERE verify_token = ?", (token,))
    if not user:
        return JSONResponse({"ok": False, "error": "Invalid or expired verification link."}, status_code=400)
    db.execute(
        "UPDATE users SET email_verified = 1, verify_token = NULL WHERE id = ?",
        (user["id"],),
    )
    record_event(None, user["id"], "email_verified", {"email": user["email"]})
    return {"ok": True, "email": user["email"]}


@app.get("/api/me")
async def api_me(request: Request):
    user = auth.current_user(request)
    if not user:
        return JSONResponse({"ok": False, "authenticated": False}, status_code=401)
    return {"ok": True, "authenticated": True, "user": user}


# --------------------------------------------------------------------------- #
# Webinar: server-clock JIT / evergreen sync
# --------------------------------------------------------------------------- #
def _webinar_config(audience: str) -> dict:
    cfg = db.query_one("SELECT * FROM webinar_config WHERE audience = ?", (audience,))
    if not cfg:
        cfg = {
            "audience": audience,
            "title": "Pre-Recorded Training",
            "youtube_id": WEBINAR_YOUTUBE_ID,
            "duration_seconds": 3120,
            "interval_minutes": 15,
            "course_reveal_seconds": 1200,
            "offer_reveal_seconds": 2520,
        }
    # Env override for the placeholder video id wins (never hard-code real ids in HTML).
    cfg["youtube_id"] = WEBINAR_YOUTUBE_ID or cfg.get("youtube_id")
    return cfg


def _webinar_state(audience: str) -> dict:
    cfg = _webinar_config(audience)
    duration = int(cfg["duration_seconds"])
    server_now = now_ms()

    # Evergreen "scheduled premiere": a new screening starts every `duration`
    # seconds. The browser trusts THIS server clock, so refreshing or skipping
    # ahead can't change the offer timing.
    period_s = max(duration, 60)
    now_s = server_now / 1000.0
    session_start_s = math.floor(now_s / period_s) * period_s
    session_start_ms = int(session_start_s * 1000)
    next_session_start_ms = session_start_ms + period_s * 1000
    elapsed = max(0, int(now_s - session_start_s))

    if elapsed < 0:
        state = "waiting"
    elif elapsed >= duration:
        state = "ended"
    else:
        state = "live"

    return {
        "audience": audience,
        "title": cfg["title"],
        "youtube_id": cfg["youtube_id"],
        "duration_seconds": duration,
        "server_now_ms": server_now,
        "session_start_ms": session_start_ms,
        "next_session_start_ms": next_session_start_ms,
        "elapsed_seconds": elapsed,
        "state": state,
        "course_reveal_seconds": int(cfg["course_reveal_seconds"]),
        "offer_reveal_seconds": int(cfg["offer_reveal_seconds"]),
        "interval_minutes": int(cfg.get("interval_minutes", 15)),
        "prices": {
            "course": PRICE_COURSE,
            "coaching_single": PRICE_COACHING_SINGLE,
            "coaching_package": PRICE_COACHING_PACKAGE,
        },
    }


@app.get("/api/time")
async def api_time():
    # Authoritative clock for the synced-now hook on the webinar page.
    return {"server_now_ms": now_ms()}


@app.get("/api/webinar/state")
async def api_webinar_state(request: Request, audience: str = "customer"):
    audience = "agent" if audience == "agent" else "customer"
    user = auth.current_user(request)
    if user:
        record_event(request.cookies.get("tn_visitor"), user["id"], "webinar_state",
                     {"audience": audience})
    return _webinar_state(audience)


# --------------------------------------------------------------------------- #
# Course
# --------------------------------------------------------------------------- #
@app.get("/api/lessons")
async def api_lessons(request: Request, audience: str = "customer"):
    user, _ = (auth.current_user(request), None)
    audience = "agent" if audience == "agent" else "customer"
    modules = db.query(
        "SELECT id, title, summary, sort_order FROM modules WHERE audience = ? ORDER BY sort_order",
        (audience,),
    )
    for m in modules:
        m["lessons"] = db.query(
            "SELECT id, title, body, video_id, duration_minutes, sort_order "
            "FROM lessons WHERE module_id = ? ORDER BY sort_order",
            (m["id"],),
        )
    return {"ok": True, "audience": audience, "modules": modules}


# --------------------------------------------------------------------------- #
# Coaching + payments (STUBBED)
# --------------------------------------------------------------------------- #
@app.post("/api/checkout")
async def api_checkout(request: Request, payload: CheckoutRequest):
    # SAFETY RAIL: no real money flow until CHECKOUT_ENABLED=true AND legal review.
    # TODO(Stripe): create a real Stripe Checkout Session here, verify via webhook,
    #   then create the course_purchases / entitlement row. Do NOT unlock on the
    #   success URL alone. See docs/COMPLIANCE_CHECKLIST.md (CROA advance-payment).
    if not CHECKOUT_ENABLED:
        return JSONResponse(
            {
                "ok": False,
                "error": "Checkout is disabled pending legal review (CHECKOUT_ENABLED=false).",
            },
            status_code=503,
        )
    user = auth.current_user(request)
    if not user:
        return JSONResponse({"ok": False, "error": "Login required."}, status_code=401)
    record_event(request.cookies.get("tn_visitor"), user["id"], "checkout_start",
                 {"product_code": payload.product_code})
    # Placeholder success path (only reachable when the flag is on).
    return {"ok": True, "checkout_url": "/coaching?stub=1", "product_code": payload.product_code}


@app.post("/api/coaching/request")
async def api_coaching_request(request: Request, payload: CoachingRequest):
    user = auth.current_user(request)
    if not user:
        return JSONResponse({"ok": False, "error": "Login required."}, status_code=401)
    db.insert(
        "INSERT INTO coaching_requests (user_id, offer_code, requested_date, requested_slot, "
        "status, notes, created_at) VALUES (?, ?, ?, ?, 'requested', ?, ?)",
        (user["id"], payload.offer_code, payload.requested_date, payload.requested_slot,
         payload.notes, utc_now_iso()),
    )
    record_event(request.cookies.get("tn_visitor"), user["id"], "coaching_request",
                 {"offer_code": payload.offer_code})
    # TODO(Cal.com): replace this with a verified booking via the Cal.com embed +
    #   webhook once payment/compliance is settled. Validate 1-6 PM ET server-side.
    return {"ok": True, "message": "Request received. Our team will follow up by email."}


# --------------------------------------------------------------------------- #
# Admin analytics
# --------------------------------------------------------------------------- #
FUNNEL_STEPS = [
    ("page_view", "Visited a page"),
    ("cta_click", "Clicked a track CTA"),
    ("register_customer", "Registered (customer)"),
    ("register_agent", "Registered (agent)"),
    ("login", "Logged in"),
    ("webinar_state", "Entered webinar"),
    ("course_cta", "Clicked course offer"),
    ("coaching_cta", "Clicked coaching offer"),
    ("checkout_start", "Started checkout"),
    ("coaching_request", "Requested coaching"),
]


def _count_events(name: str) -> int:
    row = db.query_one("SELECT COUNT(*) AS c FROM events WHERE event_name = ?", (name,))
    return int(row["c"]) if row else 0


def _count_distinct_visitors(name: str) -> int:
    row = db.query_one(
        "SELECT COUNT(DISTINCT visitor_id) AS c FROM events WHERE event_name = ?",
        (name,),
    )
    return int(row["c"]) if row else 0


@app.get("/api/admin/funnel")
async def api_admin_funnel(request: Request):
    user, redirect = require_role(request, "admin")
    if redirect:
        return JSONResponse({"ok": False, "error": "Admin only."}, status_code=403)

    steps = []
    top = None
    for name, label in FUNNEL_STEPS:
        count = _count_events(name)
        visitors = _count_distinct_visitors(name)
        if top is None:
            top = max(count, 1)
        steps.append({
            "event_name": name,
            "label": label,
            "count": count,
            "visitors": visitors,
            "pct": round(100.0 * count / top, 1) if top else 0.0,
        })
    return {"ok": True, "steps": steps}


@app.get("/api/admin/stats")
async def api_admin_stats(request: Request):
    user, redirect = require_role(request, "admin")
    if redirect:
        return JSONResponse({"ok": False, "error": "Admin only."}, status_code=403)

    def scalar(sql, params=()):
        row = db.query_one(sql, params)
        return int(list(row.values())[0]) if row else 0

    return {
        "ok": True,
        "stats": {
            "users_total": scalar("SELECT COUNT(*) FROM users"),
            "verified_accounts": scalar("SELECT COUNT(*) FROM users WHERE email_verified = 1"),
            "customers": scalar("SELECT COUNT(*) FROM users WHERE role = 'customer'"),
            "agents": scalar("SELECT COUNT(*) FROM users WHERE role = 'agent'"),
            "agents_pending": scalar("SELECT COUNT(*) FROM users WHERE role='agent' AND approval_status='pending'"),
            "events_total": scalar("SELECT COUNT(*) FROM events"),
            "webinar_starts": scalar("SELECT COUNT(*) FROM events WHERE event_name='webinar_state'"),
            "coaching_requests": scalar("SELECT COUNT(*) FROM coaching_requests"),
            "purchases": scalar("SELECT COUNT(*) FROM course_purchases WHERE status='active'"),
        },
    }


@app.get("/api/admin/users")
async def api_admin_users(request: Request):
    user, redirect = require_role(request, "admin")
    if redirect:
        return JSONResponse({"ok": False, "error": "Admin only."}, status_code=403)
    users = db.query(
        "SELECT id, email, first_name, last_name, role, approval_status, email_verified, "
        "created_at FROM users ORDER BY id DESC LIMIT 200"
    )
    return {"ok": True, "users": users}


# --------------------------------------------------------------------------- #
# Email stub
# --------------------------------------------------------------------------- #
def _print_verification_email(email: str, token: str) -> None:
    # TODO(email): replace with Resend/SMTP. For now we just log the link.
    link = f"{APP_BASE_URL}/verify-email?token={token}"
    print("\n" + "=" * 70)
    print(f"[EMAIL STUB] Verify {email}")
    print(f"[EMAIL STUB] Verification link: {link}")
    print("=" * 70 + "\n", flush=True)


@app.get("/healthz")
async def healthz():
    return {"ok": True, "ts": now_ms()}
