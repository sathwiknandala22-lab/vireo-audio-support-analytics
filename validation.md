# Validation and limitations

## Deterministic data checks
- 11,750 tickets loaded.
- Duplicate ticket IDs: 0.
- Exact duplicate rows: 0.
- CSAT values outside 1–5: 0.
- Agent/product/customer ID joins passed for the supplied records.
- Order/customer consistency checks passed.
- Legacy resolution timestamps are shifted +5:30 before handle-time calculations.

## Lot-monitor validation
- Exact order-to-lot linkage is used first; a fallback latest-prior-order join is used only when needed.
- Fallback lot assignment agrees with the exact join in the validation sample at about **97.6%**.
- The lot monitor uses a per-SKU median cohort replacement rate as its baseline and flags cohorts with at least 30 tickets and z-score > 5.
- Three Pulse 2 cohorts are flagged: **2510, 2511, 2512**.
- A null/shuffle test produced a low false-alarm rate (~0.5% across 200 shuffles).
- A planted-defect test showed about 30% recall for 3x defects across small/medium cohorts. This limitation is important: the detector is more useful for large cohorts and can miss small weak anomalies.
- Historical replay crossed the alarm threshold on 26 Nov 2025, 3 Jan 2026 and 12 Feb 2026 for the three flagged lots.

## Agent analysis validation
- The queue-adjusted model is cross-validated and reports its MAE in the dashboard.
- Split-half testing shows adjusted agent scores are substantially less stable than raw CSAT. This supports using the result as a review queue rather than an automatic personnel decision.
- The dashboard does not claim that an agent caused low CSAT.

## AI text model
- TF-IDF (1–2 grams) + logistic regression.
- Stratified 80/20 split, random seed 42.
- Held-out accuracy: approximately **78.3%**.
- It is used only as a text-analysis aid; it is not used to fire, rank or retrain employees automatically.

## Known limitations
- About 55% of customers do not provide CSAT, so survey non-response may bias observed CSAT.
- Lot anomalies do not prove a physical manufacturing defect.
- The lot-cost estimate is relative to an observed baseline and is not a forecast.
- Handle time should be compared within comparable teams because Tier 2 work can take much longer by design.
- The original task pack supplied to me did not contain the exact `submission-form.md`; the included form is a reconstructed completed version.
