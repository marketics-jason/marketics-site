# COUNSEL ROUTING — `/legal` states the service fee on two incompatible bases

**Raised by:** Code · **Date:** 2026-08-27 · **Status:** open, awaiting counsel
**Public visibility:** internal only — force-shadowed to 404 in `_redirects`.
**Nature:** contract-wording conflict inside a live public document. Not a drafting-style note.

---

## The issue in one line

`marketics.io/legal` describes the ongoing service fee **two different ways in the same
document** — once as a percentage of *net payout*, and elsewhere as a percentage of *gross
booking revenue before deductions*. Those cannot both be true, and they produce different
amounts of money on every booking.

## The four passages

| Where | What it says |
|---|---|
| §390 | "Configure the payout split mechanism so that Marketics receives **10% of booking revenue** directly from the platform at the time of payout" |
| §588 | "Client agrees to configure the payout split mechanism … to direct **10% of gross booking revenue per booking**" |
| **§601** | "Following the onboarding period, the ongoing service fee is **10% of the net payout per booking**" |
| §602 | "The Service Fee is calculated on **gross booking revenue before platform service fees, taxes, or other deductions** by the booking platform" |

**§601 and §602 are directly contradictory.** Net payout is the amount remaining *after* the
platform's host service fee and any platform-remitted taxes. §602 specifies the basis as the
amount *before* exactly those deductions. One of the two is wrong.

## Why it is not cosmetic

On a booking, gross-before-deductions and net payout differ by the platform's host service fee
plus any remitted taxes. A 10% fee therefore yields a **materially different amount** depending
on which sentence governs. A client reading the terms cannot determine what they owe.

## What the rest of the estate says

- **The Co-Host Agreement** (`/join` §2) — the document a client actually signs — defines the fee
  as **10% of the net payout per booking**, and defines net payout as *"gross guest charges minus
  Airbnb's host service fee minus any platform-remitted taxes."* This agrees with `/legal` §601.
- **Every marketing surface** was corrected on 2026-08-27 to state **net payout**, on Jason's
  ruling (GATE 0, Option A: 10% of the host's net payout on each booking, a 90/10 split at the
  transaction level). That is now consistent across the homepage, `/pricing`, `/results`, `/faq`,
  `/get-started`, `/join` page copy, `/lp/keep-control`, `llms.txt` and 12 intel pages.

**So `/legal` §390, §588 and §602 are now the only statements on the site describing the fee on a
gross basis** — and they disagree with both the signed agreement and `/legal`'s own §601.

## What Code did and did not do

- **Did not edit `/legal` or the Co-Host Agreement.** Standing rule: those are counsel lane, and
  Code reports rather than edits, regardless of how clear the fix looks.
- **Did not let it pass silently.** `scripts/validate-site.py` carries a counsel-lane exemption
  for this file so CI is not permanently red, and prints a warning **on every run** until it is
  resolved. It cannot quietly drop off the list.

## What counsel needs to decide

1. Which basis is correct and intended — **net payout** (per §601 and the signed Co-Host
   Agreement) or **gross booking revenue** (per §390, §588, §602)?
2. If net payout, as the signed agreement and the business ruling both indicate: amend §390,
   §588 and §602 so the document states one basis throughout, and confirm the payout-split
   mechanism described in §390/§588 actually operates on that basis.
3. Whether any client onboarded under the current wording needs notifying, and whether any
   billing to date was calculated on the basis the terms will end up stating.

**Point 3 is the one Code cannot assess at all** and is flagged for that reason: it depends on
what was actually charged, which is not visible from the repository.

## Contact

Fee/canon questions: Jason. Copy questions: Strategy. This document: Code.
Once `/legal` is amended, remove the `legal/index.html` entry from `COUNSEL_LANE_EXEMPT` in
`scripts/validate-site.py` so the fee tokens become a hard gate there too.
