# Template: New HTML PAGE

Copy this skeleton into `frontend/pages/<name>.html`, then add the route in
`backend/main.py` (`@app.get("/<route>") ... return serve_page("<name>.html")`).

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PAGE TITLE — Tranzformation Nation</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="/static/css/app.css" />
  <!-- Add Alpine only if the page is interactive: -->
  <script defer src="https://unpkg.com/alpinejs@3.14.1/dist/cdn.min.js"></script>
  <!-- Add Lucide only if you use icons: -->
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
  <!-- tracker.js LAST so window.TN is available to inline handlers: -->
  <script src="/static/js/tracker.js"></script>
</head>
<body class="bg-slate-50 text-slate-800" x-data="pageData()" x-init="init()">
  <!-- content; use data-track="event_name" on CTAs -->
  <script>
    function pageData() {
      return {
        async init() { /* fetch /api/me etc. */ },
      };
    }
  </script>
</body>
</html>
```

Checklist:
- [ ] `data-track="..."` on every CTA you want in the funnel.
- [ ] Compliance-safe copy (no guarantees; "pre-recorded"). See COMPLIANCE_CHECKLIST.md.
- [ ] Auth-gated? Add `require_role(...)` in the route.
- [ ] No secrets / real video ids / admin URLs in the HTML (PUBLIC_VIEW_CHANGES.md).
- [ ] Educational footer disclaimer where appropriate.
```
