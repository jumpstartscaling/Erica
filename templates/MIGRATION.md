# Template: schema MIGRATION

This wireframe keeps the full schema in `backend/schema.sql` (idempotent
`CREATE TABLE IF NOT EXISTS`). For incremental changes, add a numbered migration
file and apply it via `db.py`.

```
backend/migrations/
  001_add_widgets.sql
  002_add_widget_status.sql
```

`001_add_widgets.sql` (SQLite-compatible; note Postgres differences in a comment):
```sql
-- up
CREATE TABLE IF NOT EXISTS widgets (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,  -- PG: GENERATED ALWAYS AS IDENTITY
    user_id    INTEGER NOT NULL REFERENCES users(id),
    name       TEXT NOT NULL,
    status     TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT (datetime('now')) -- PG: now()
);
```

Apply (quick approach for this project):
```python
import db
for stmt in db._split_statements(open("backend/migrations/001_add_widgets.sql").read()):
    db.execute(stmt)
```

Rules:
- [ ] One logical change per file; never edit an applied migration — add a new one.
- [ ] Keep `schema.sql` as the source-of-truth snapshot (update it too).
- [ ] Backward-compatible columns (nullable or with defaults) for zero-downtime.
- [ ] Document SQLite vs Postgres type differences inline.
```
