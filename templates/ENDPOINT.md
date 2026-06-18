# Template: New API ENDPOINT (FastAPI)

Add to `backend/main.py`. Use a Pydantic model for the body, guard with
`auth.current_user` / `require_role`, and record an event when it matters.

```python
class WidgetCreate(BaseModel):
    name: str
    visitor_id: Optional[str] = None


@app.post("/api/widgets")
async def api_create_widget(request: Request, payload: WidgetCreate):
    user = auth.current_user(request)
    if not user:
        return JSONResponse({"ok": False, "error": "Login required."}, status_code=401)

    widget_id = db.insert(
        "INSERT INTO widgets (user_id, name, created_at) VALUES (?, ?, ?)",
        (user["id"], payload.name, utc_now_iso()),
    )
    record_event(request.cookies.get("tn_visitor"), user["id"], "widget_created",
                 {"widget_id": widget_id})
    return {"ok": True, "id": widget_id}
```

Checklist:
- [ ] Pydantic model validates input (never trust the client).
- [ ] Auth guard if non-public (`current_user` for any role, `require_role` for specific roles).
- [ ] Use `db.query / query_one / execute / insert` (all `?` placeholders → dialect-free).
- [ ] `record_event(...)` for funnel-relevant actions; keep event names stable.
- [ ] Return `{ ok: bool, ... }`; use proper status codes (401/403/409/503).
- [ ] Update `docs/API_SPEC.md`.
```
