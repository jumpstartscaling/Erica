# COMPLIANCE_CHECKLIST.md — read before enabling payments or publishing copy

> This is a sensitive category (credit). Nothing in this file is legal advice.
> A qualified attorney must review CROA / state CSO exposure before launch.
> **The dangerous copy below must NEVER appear live on a page — it lives here
> only as "what to fix."** The shipped pages already use the safe rewrites.

## Legal blockers

### CROA — Credit Repair Organizations Act
Can apply to anyone who sells services/advice represented to improve a consumer's
credit. Key requirements/limits:
- No false or misleading representations.
- Written contract + required consumer disclosures.
- 3-business-day cancellation right.
- **Restrictions on collecting money before services are performed** (advance-payment ban).
- Cannot advise consumers to make false statements.
- Cannot imply accurate negative information can be legally removed.

### TSR — Telemarketing Sales Rule
If sales happen by phone/Zoom/outbound or certain post-ad inbound calls, TSR may
apply. For credit repair sold via telemarketing, advance-fee restrictions are
**very strict** — do not assume monthly fees/deposits are safe.

### FTC truth-in-advertising
Claims must be truthful, not misleading, and substantiated **before** use. A
footer disclaimer does NOT cure a misleading headline or guarantee.

### State credit-services (CSO) laws
Many states require registration, surety bond, specific contract language,
cancellation notices, fee limits, and disclosures — and may apply based on where
the **customer** lives.

## Dangerous copy that MUST change (do not ship the left column)

| # | Dangerous (DO NOT USE) | Safe rewrite (shipped) |
|---|------------------------|------------------------|
| 1 | "make sure your credit gets repaired or your business grows" (a guarantee) | "Get monthly education, accountability, and strategy support as you work through your credit education or business growth plan. Results vary and are not guaranteed." |
| 2 | "force the bureaus" | "Use your FCRA rights to request an investigation of information you believe is inaccurate, incomplete, or unverifiable." |
| 3 | "Your credit report must be 100% accurate" | "The FCRA gives consumers the right to dispute information they believe is inaccurate, incomplete, or unverifiable." |
| 4 | "If the creditor cannot prove it… the bureau MUST DELETE" | "If disputed information cannot be verified as accurate, the credit reporting agency generally must correct or delete it." |
| 5 | "We are calling their bluff… go to war" | "The goal is to create clear, factual disputes about information you genuinely believe is inaccurate, incomplete, or unverifiable." |
| 6 | "NEVER dispute online. Ever." | "This course focuses on written mail disputes because they create a paper trail. Online disputes may be appropriate for some consumers; review the terms and keep records." |
| 7 | "90% of the time, this is a lie" | "If an item is verified and you still believe it is inaccurate or incomplete, you may request more information about the investigation or consider additional dispute steps." |
| 8 | "This scares them" | Remove entirely. |
| 9 | "No response is a major win" | "If you do not receive a timely response, you may have additional rights. Consider a CFPB complaint or consulting a consumer-rights attorney." |
| 10 | "Tradeline Hack" / "overnight" | "Becoming an authorized user on a trusted family member's well-managed account may help some consumers, but results vary and not all lenders/scoring models treat AU accounts the same. Never buy or rent tradelines." |
| 11 | "You now know more than 99% of the population" | "You now have a practical foundation for understanding credit reports, disputes, and rebuilding habits." |

## The $200 prepaid coaching issue (CROA advance-payment)

The 6-month, prepaid ($200) coaching package may implicate CROA's **advance-payment
ban** if the offering is a covered credit-repair service. Calling it "coaching" does
not automatically exempt it. Posture in this build:

- `CHECKOUT_ENABLED=false` → `/api/checkout` returns **503**. No money can flow.
- The coaching page surfaces an explicit caution on the $200 package.
- TODO (legal): decide whether the customer session is (a) an educational product,
  (b) a covered credit-repair service that **cannot be prepaid**, or (c) something
  billed only after delivery. The chat suggested separate flags, e.g.
  `CUSTOMER_COACHING_CHECKOUT_ENABLED=false` vs `AGENT_BUSINESS_COACHING_CHECKOUT_ENABLED=true`.

## Required posture before launch

1. Remove all guarantees.
2. Remove "force / weapon / go to war / hack / overnight" language.
3. State that accurate, timely negative info generally cannot be legally removed.
4. State that consumers can dispute errors themselves for free.
5. Do not advise disputing information the customer knows is accurate.
6. Do not mention CPNs / EIN substitution / false identity-theft claims except to warn against them.
7. Label the webinar **"Pre-Recorded Training" / "Scheduled Premiere"** — no fake "live", no fake attendee counts, no fake scarcity timers.
8. Do not collect SSNs, full credit reports, driver's licenses, or utility bills in the MVP.
9. Attorney determines CROA / state CSO applicability.
10. If CROA applies: implement required contracts, disclosures, cancellation forms, and compliant payment timing.

## Footer disclaimer (shipped, necessary-but-not-sufficient)

> Educational purposes only. Not legal, financial, tax, or credit-repair advice.
> You can dispute inaccurate information on your credit reports yourself for free.
> We do not guarantee credit score increases, deletions, approvals, funding, or
> business revenue. Accurate and current negative information generally cannot be
> legally removed. Results vary.

## Webinar tips ticker (compliance-safe)

`credit_tips.js` contains only educational tips — no guarantees, no "force the
bureaus", no "must delete", no "overnight/hack". Keep it that way (see `templates/CREDIT_TIPS.md`).
