# Template: CREDIT_TIPS (compliance-safe ticker copy)

Tips live in `frontend/static/js/credit_tips.js` as `window.CREDIT_TIPS = [ ... ]`
and rotate in the webinar ticker. **Every tip must be educational and safe.**

## Hard rules (reject a tip if it breaks any)
- ❌ No guarantees ("boost your score", "guaranteed deletion", a specific number/points).
- ❌ No "force the bureaus", "make them delete", "bureau MUST delete".
- ❌ No "overnight", "hack", "secret", "go to war", "scares them".
- ❌ No advice to dispute information the consumer knows is accurate.
- ❌ No CPNs, EIN substitution, fake identity-theft claims, buying/renting tradelines.
- ✅ Educational, factual, FCRA-rights framed, "results vary".

## Good patterns
- "Dispute only information you believe is inaccurate, incomplete, or unverifiable."
- "Payment history matters. Paying bills on time can help build credit over time."
- "AnnualCreditReport.com is the official source for free credit reports."
- "Accurate, current negative information generally cannot be legally removed."
- "Be cautious of anyone promising guaranteed deletions or a specific score increase."

## Adding a tip
```js
// frontend/static/js/credit_tips.js
window.CREDIT_TIPS = [
  // ...existing...
  "Your new educational, guarantee-free tip here.",
];
```
Then re-read COMPLIANCE_CHECKLIST.md if unsure. When in doubt, leave it out.
```
