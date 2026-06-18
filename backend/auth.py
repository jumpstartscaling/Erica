"""Authentication helpers: password hashing, signed session cookies, guards.

- Passwords: bcrypt (via the `bcrypt` package directly -- robust on modern
  Python where passlib's bcrypt backend can break).
- Sessions: a signed, timed token (itsdangerous) stored in an httponly cookie.
  The cookie holds only the user id; we re-load the user from the DB each request.
"""

from __future__ import annotations

import os
from typing import Optional

import bcrypt
from fastapi import Request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

import db

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-change-me")
SESSION_COOKIE = "tn_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 14  # 14 days
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "false").lower() == "true"

_serializer = URLSafeTimedSerializer(SECRET_KEY, salt="tn-session")


# --------------------------------------------------------------------------- #
# Passwords
# --------------------------------------------------------------------------- #
def _to_72_bytes(password: str) -> bytes:
    # bcrypt only uses the first 72 bytes; truncate to avoid ValueError.
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_to_72_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_to_72_bytes(password), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# --------------------------------------------------------------------------- #
# Sessions
# --------------------------------------------------------------------------- #
def create_session_token(user_id: int) -> str:
    return _serializer.dumps({"uid": user_id})


def read_session_token(token: str) -> Optional[int]:
    try:
        data = _serializer.loads(token, max_age=SESSION_MAX_AGE)
        return int(data["uid"])
    except (BadSignature, SignatureExpired, KeyError, ValueError, TypeError):
        return None


def set_session_cookie(response, user_id: int) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=create_session_token(user_id),
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        path="/",
    )


def clear_session_cookie(response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/")


def current_user(request: Request) -> Optional[dict]:
    """Return the logged-in user row (dict) or None."""
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    uid = read_session_token(token)
    if uid is None:
        return None
    return db.query_one(
        "SELECT id, email, first_name, last_name, role, approval_status, "
        "business_name, email_verified, marketing_opt_in, created_at "
        "FROM users WHERE id = ?",
        (uid,),
    )
