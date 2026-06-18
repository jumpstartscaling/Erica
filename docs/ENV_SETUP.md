# ENV_SETUP.md — environment variables & the SQLite ↔ Postgres swap

Copy `backend/.env.example` → `backend/.env` and edit. `.env` is gitignored.
The app reads env vars from the process environment; `scripts/run.sh` loads `.env`.

## Variables

| Var | Default | Purpose |
|-----|---------|---------|
| `SECRET_KEY` | `dev-insecure-change-me` | Signs session cookies. **Set a strong value in prod.** |
| `APP_BASE_URL` | `http://localhost:8000` | Used in the stubbed verification email link. |
| `COOKIE_SECURE` | `false` | Set `true` behind HTTPS so the session cookie is `Secure`. |
| `DATABASE_URL` | *(empty)* | Empty → SQLite. `postgres...` → Postgres via psycopg. |
| `SQLITE_PATH` | `backend/app.db` | Override SQLite file location. |
| `WEBINAR_YOUTUBE_ID` | `dQw4w9WgXcQ` | Placeholder video id. Never hard-code real ids in HTML. |
| `CHECKOUT_ENABLED` | `false` | `false` → `/api/checkout` returns 503 (safety rail). |
| `PRICE_COURSE` | `35` | Display price for the course. |
| `PRICE_COACHING_SINGLE` | `75` | Display price, single 30-min session. |
| `PRICE_COACHING_PACKAGE` | `200` | Display price, 6-month package. |

Generate a strong secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Default: SQLite (zero setup)

Leave `DATABASE_URL` empty. `db.py` uses the stdlib `sqlite3` driver against
`backend/app.db`. `init_db()` runs `schema.sql` + `seed.sql` automatically on first
boot (and `scripts/initdb.sh` runs it explicitly).

## Swap to Postgres

1. Provision Postgres and create a database.
2. Set `DATABASE_URL=postgresql://user:pass@host:5432/dbname`.
3. Uncomment `psycopg[binary]` in `backend/requirements.txt` and reinstall.
4. Port the schema types (SQLite `schema.sql` → Postgres):
   - `INTEGER PRIMARY KEY AUTOINCREMENT` → `GENERATED ALWAYS AS IDENTITY` (or `SERIAL`).
   - `datetime('now')` defaults → `now()` (or set timestamps from the app).
   - `TEXT` json columns → `JSONB` (optional).
5. Run the ported schema/seed, then start the app.

The application code is dialect-free: all SQL uses `?` placeholders, which `db.py`
translates to `%s` for psycopg. `db.insert()` uses `RETURNING id` on Postgres and
`cursor.lastrowid` on SQLite.

## Notes

- Demo admin (seeded): `admin@example.com` / `password`. Rotate before any real use.
- Email is a stub: verification links are printed to the server console (`_print_verification_email`). For convenience in dev, registration also redirects to `/verify-email?token=...`.
