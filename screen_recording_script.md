# <=3-minute screen recording script

**0:00–0:20 — Ask and setup**
“Vireo asked for CSAT and handle time per agent, a bottom-ten view, a numerical business goal, validation, and an AI-assisted workflow. I separated Tier 2 from Tier 1, joined agents by agent_id, excluded blank CSAT, and corrected legacy UTC resolution timestamps to IST.”

**0:20–0:55 — Dashboard**
Show the KPI cards and the Agent Dashboard. Say: “The H1 2026 replacement rate is 22.1%, CSAT is 3.17, and the dashboard provides the requested agent scorecard. The bottom ten are a review queue, not an automatic performance verdict.”

**0:55–1:35 — Root-cause signal**
Scroll to the Pulse 2 lot section. Say: “The stronger business signal is at lot level. Lots 2510, 2511 and 2512 have roughly 35–38% replacement rates versus an approximately 11.2% Pulse 2 baseline. The estimated excess replacement cost is about ₹12.2 lakh using the policy cost formula. This is an anomaly signal, not proof of a physical defect.”

**1:35–2:00 — Business goal and validation**
Show the goal and historical alarm dates. Say: “The operational goal is to detect abnormal lots within about four weeks of first tickets. Separately, the KPI target is to reduce H1 replacement rate from 22.1% to 15%, which is about ₹3.38 lakh per quarter at the H1 run-rate.”

**2:00–2:30 — AI**
Click “Run validation.” Say: “The AI component is local TF-IDF plus logistic regression, with about 78.3% held-out accuracy. There are no per-ticket paid API calls.”

**2:30–2:55 — Prompt changes / discarded work**
Show `ai_prompt_log.md`. Say: “I discarded raw agent ranking as a personnel conclusion, per-ticket LLM calls, an unvalidated anger score, and treating lot anomalies as proof of defect. The final workflow keeps reproducible metrics and validation.”

**2:55–3:00 — Close**
Show the memo and package files. “The output includes the dashboard, memo, validation, prompt log, and submission form.”
