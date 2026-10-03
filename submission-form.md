# Vireo Audio — Support Tickets (Set B) — Submission Form

> The exact original `submission-form.md` was not included in the supplied task ZIP. This is a completed reconstruction based on the brief and email thread. If Vireo provides an official template, copy these answers into that template.

## 1. Tool
**Location:** `app.py` + `vireo_analysis.py`, launched with `run.bat` or `bash run.sh`.

**What it does:** agent scorecard, bottom-10 review queue, monthly trend, replacement KPI, Pulse 2 lot anomaly monitor, historical alarm replay, queue-adjusted review check, and local text-classification validation.

**Running cost:** no per-ticket paid model calls.

## 2. Business goal as a number
**Primary operational KPI:** reduce H1 2026 replacement rate from **22.1% to 15%**. At the H1 run-rate and observed average replacement cost, this is approximately **₹3.38 lakh per quarter** in potential avoided replacement cost.

**Root-cause monitoring goal:** flag an abnormal product lot within approximately **four weeks of its first support tickets**. The historical replay crossed the threshold on 26 Nov 2025 (2510), 3 Jan 2026 (2511), and 12 Feb 2026 (2512).

## 3. What the analysis found
Pulse 2 lots 2510–2512 had approximately 35–38% replacement rates versus an approximately 11.2% rate for other Pulse 2 lots. They contain 2,544 completed tickets. Relative to the observed baseline, the excess replacement estimate is approximately **671 replacements / ₹12.2 lakh** using product unit cost + ₹340 logistics.

## 4. How I know it works / limitations
- Duplicate ticket IDs: 0.
- Exact duplicate rows: 0.
- CSAT values outside 1–5: 0.
- Fallback lot join agrees with exact join in the validation sample at ~97.6%.
- Lot detector null/shuffle false-alarm rate: ~0.5% over 200 runs.
- Planted 3x-defect recall: ~30%; small/weak cohorts are a known limitation.
- Agent adjusted-score stability is limited; therefore the bottom ten is a review queue, not an automatic training decision.
- Text classifier: TF-IDF + logistic regression, held-out accuracy ~78.3%.

## 5. Decisions where the brief was unclear
1. Joined agents by `agent_id`, never name.
2. Excluded blank CSAT from CSAT averages.
3. Corrected legacy `resolved_at` from UTC to IST.
4. Used first human response → resolution for handle time.
5. Kept Tier 2 separate from Tier 1 comparisons.
6. Used policy replacement cost (unit cost + ₹340 logistics), rather than the rough ₹2,500 estimate in Finance's email.
7. Used order/lot data because it is the key available signal for the replacement-cost problem.
8. Treated the agent bottom ten as a review queue because queue mix can drive raw CSAT.
9. Treated lot flags as anomaly signals, not proof of manufacturing defect or supplier liability.

## 6. What was left out
Customer non-response weighting, deeper SLA-credit economics, repeat-contact modeling, transfer-cost analysis, and causal manufacturing/supplier analysis were left out of the headline because they were not required to establish the main operational signal within the task time limit.

## 7. AI tools used
**AI-assisted development:** ChatGPT (OpenAI) was used to help inspect the task, reason about the analysis, write/refine code and documentation, and validate the workflow. The submitted application itself makes no per-ticket paid model calls.

**Actual time spent:** [ENTER YOUR ACTUAL HOURS]

**Discarded approaches:** raw bottom-ten personnel conclusion, per-ticket paid LLM calls, unvalidated customer-anger scoring, automatic retraining decisions, and treating a lot anomaly as proof of physical defect.

## 8. Screen recording
Use `screen_recording_script.md` for the required <=3-minute walkthrough. Record the dashboard, business goal, lot monitor, AI validation, and discarded approaches.
