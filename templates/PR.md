# Template: Pull Request

## Summary
<!-- 1–3 sentences: what changed and why (the value, not just the diff). -->

## Pages / endpoints touched
- Routes:
- New/changed API:
- DB changes (migration?):

## Screenshots / evidence
<!-- Before/after for UI; curl output for API. -->

## Compliance check (credit category — required)
- [ ] No guarantees or misleading claims in any copy (see COMPLIANCE_CHECKLIST.md).
- [ ] Webinar still labeled "Pre-Recorded / Scheduled Premiere".
- [ ] No new collection of SSN / full reports / IDs.
- [ ] Payments remain behind `CHECKOUT_ENABLED` (or legal sign-off attached).

## Security check
- [ ] No secrets / real video ids / admin URLs in client HTML/JS.
- [ ] Auth guards on non-public routes; correct redirects.
- [ ] Public forms validated server-side (and rate-limit/CAPTCHA noted if missing).

## Test plan
- [ ] `python -m py_compile backend/*.py`
- [ ] `bash scripts/initdb.sh` succeeds
- [ ] `bash scripts/run.sh` boots; key routes return expected status
- [ ] Admin login works; funnel renders
```
