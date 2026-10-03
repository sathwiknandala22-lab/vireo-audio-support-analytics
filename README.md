# Vireo Audio — Support Tickets (Set B)

## What this submission does
A runnable Streamlit dashboard for Vireo Audio's support-ticket task. It answers the requested agent scorecard question and adds a validated lot-level replacement-cost signal so the business goal is tied to a concrete operational lever.

### Headline findings
- H1 2026 replacement rate: **22.1%** vs **12.3% in Q4 2025**.
- H1 2026 CSAT: **3.17/5** vs **3.43/5 in Q4 2025**.
- A lot-level monitor flags **Pulse 2 lots 2510, 2511 and 2512**: about **34.4–38.4% replacement rate** versus an approximately **11.2% baseline** for other Pulse 2 lots.
- The flagged lots contain **2,428 completed tickets** and imply approximately **₹12.2 lakh of excess replacement cost** under the policy cost formula. This is an anomaly-based estimate, not a guarantee or a claim that the lots are physically defective.
- The operational target used in the dashboard is **reduce the H1 replacement rate to 15%**; at the H1 run-rate this is a planning scenario of about **₹3.38 lakh per quarter** in avoided replacement cost.
- Raw agent bottom-10 results are presented as a **review queue**, not an automatic retraining decision, because queue mix and Tier 2/hardware-triage work materially affect CSAT.

## Run on a clean machine
Requirements: Python 3.10+.

### Windows
```bat
run.bat
```

### macOS/Linux
```bash
bash run.sh
```

Or manually:
```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The supplied `data/` folder is included. The loader also accepts the UUID-prefixed source filenames from the original task pack because it searches by filename suffix.

## AI use
The submitted tool makes **no per-ticket paid model calls**. The AI-assisted development work was used to write and refine the analysis/code. The dashboard's text model is a local TF-IDF + logistic-regression classifier, validated on a held-out 20% split (about **78.3% accuracy**). It is an analysis aid, not a causal or personnel decision model.

## Important methodology decisions
- Join agents by **`agent_id`**, never by display name.
- Blank CSAT means no survey response and is excluded from CSAT averages.
- Handle time = first human response → resolution.
- Legacy resolution timestamps are shifted **UTC → IST (+5:30)** according to the supplied policy.
- SLA targets: chat 15m, voice 120m, social 240m, email 480m.
- Tier 2 / Escalations & Warranty is kept separate from Tier 1 comparisons.
- Replacement cost = product unit cost + **₹340 logistics** per policy.
- Lot linkage uses exact `order_id` first, then latest prior order for the same customer + SKU; tickets that predate their order are not assigned a lot.

## Included files
- `app.py` — Streamlit dashboard.
- `vireo_analysis.py` — reusable analysis and lot-monitor functions.
- `requirements.txt` — dependencies.
- `run.sh` / `run.bat` — clean-machine launch helpers.
- `memo.pdf` / `memo.md` — one-page memo to Priya.
- `validation.md` — validation and limitations.
- `ai_prompt_log.md` — prompt/approach evolution and discarded work.
- `screen_recording_script.md` — <=3-minute demo script.
- `submission-form.md` — completed reconstructed form; the exact original form was not included in the supplied ZIP.
- `data/` — supplied CSVs and support policy.
