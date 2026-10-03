# AI / prompt and approach log

## Version 1 — discarded
**Approach:** immediately produce a bottom-10 agent ranking from raw CSAT.

**Why discarded:** Neha's email warns that hardware-triage agents receive harder cases, and Tier 2 is not directly comparable with Tier 1. Raw ranking risks confusing queue assignment with individual performance.

## Version 2 — kept
**Approach:** define joins and metric rules explicitly: agent_id joins, blank CSAT excluded, first-response-to-resolution handle time, legacy UTC→IST correction, Tier 2 separation, and policy replacement cost.

**Result:** reproducible scorecard plus a review queue rather than an automatic training verdict.

## Version 3 — added root-cause monitor
**Approach:** inspect product lot cohorts and compare each SKU/lot replacement rate with a robust per-SKU median baseline. Require a minimum cohort size and high z-score before flagging.

**Result:** Pulse 2 lots 2510–2512 were flagged; the historical replay shows the monitor would have alerted within roughly four weeks of each lot's first ticket.

## Version 4 — AI text check
**Approach:** local TF-IDF + logistic regression on customer opening messages, with a held-out validation split.

**Result:** ~78.3% held-out accuracy. This is a classification aid only.

## Explicitly discarded
- Per-ticket paid LLM calls across ~12k tickets: unnecessary running cost and contrary to Finance's constraint.
- Customer "anger" lexicon as a causal CSAT variable: not sufficiently validated.
- Automatic retraining decisions based on agent rank.
- Customer-level profiling.
- Treating a lot anomaly as proof of physical defect or supplier fault.
