# To: Neha Kulkarni  |  Re: First-response breaches

**Short answer:** the Morning team is where breaches *land*, not where they start. Fixing it needs no hiring.

**What the data shows (Jan 2025 – Jun 2026, 11,200 tickets after removing 616 duplicates)**
- Breach rate was ~9% a month until June 2025. From July 2025 it jumped to ~25% and has stayed there.
- The jump is one thing: tickets that arrive overnight (10pm–6am IST). Every overnight chat since July breaches (100%); overnight social 86%; overnight email 50%. Daytime tickets are still at ~9%.
- On 30 June 2025 two of the three Indore night chat agents (Tarun Mishra, Harpreet Deshpande) moved to Day; the third (Zoya Mehta) has no roster row after 29 June. Overnight chat has had no one since.
- Those overnight tickets wait until the Morning shift opens, so Morning agents answer them late and the breach is booked against them. 1,566 of Morning's 2,018 breaches arrived overnight. Morning agents breach ~9% on tickets that arrived on their own shift, the same as Day.

**What it costs:** every breach issues a Rs 350 credit. Overnight breaches since July: ~395 a quarter, about **Rs 1.4 lakh a quarter** in credits. This is likely the SLA credit line Arjun asked about: monthly breaches stepped up 3-5x between June and August 2025 and have been flat since, which is why credits look flat to Priya.

**Goal:** bring overall breach rate from **25% to ~10% within a quarter**, saving roughly **Rs 1.2 lakh a quarter** (about Rs 5 lakh a year), by putting overnight chat cover back. No new headcount: move the two Indore agents back to Night. Zoya Mehta's status is unclear from the roster; if she has left, two people cover a night thinly, so start with chat and check email. Cost-neutral on salary; the trade-off is whatever those two do on Day, which I did not analyse.

**What I'd ask you not to do:** have the conversation with Morning agents on the current numbers. Their own-shift rate is fine. The weekly report therefore shows, per agent, tickets that arrived in their own shift separately from tickets they inherited.

**Caveats:** (0) Overnight chat volume also roughly doubled after June 2025 (about 41 to 86 a month), so more overnight tickets are hitting the same gap; this raises the credit bill but does not change the cause. Waiting time tracks the clock almost perfectly (r=0.98 with minutes until 6am), which is what an uncovered night looks like. (1) correlation with the 30 June change is strong but I can't see why else it might have changed; (2) CSAT: tickets that breached score 2.8 vs 3.5 for those that did not, and the monthly average dipped from ~3.46 (Jun 2025) to ~3.27 (Aug) before recovering to ~3.4, so Priya is right that it moved, but modestly; (3) 616 duplicates were removed keeping the helpdesk row; (4) the Rs 1.2 lakh assumes overnight breaches fall to the ~9% daytime rate.

Tool: `python breach_report.py data out` produces the weekly tables; README has the steps.
