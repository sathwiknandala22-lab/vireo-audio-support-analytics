import streamlit as st
import pandas as pd
from vireo_analysis import load_data, prepare, agent_metrics, monthly_metrics, build_text_model, queue_adjusted_flags, business_goal, lot_monitor, lot_cost_analysis, lot_backtest

st.set_page_config(page_title="Vireo Audio — Support Tickets Set B", layout="wide")
st.title("Vireo Audio — Support Tickets (Set B)")
st.caption("Jan 2025–Jun 2026 | IST handling | Tier 1 review separated from Tier 2 | Local AI only")

@st.cache_data
def get_data(): return load_data("data")
@st.cache_data
def get_prepared():
    tickets, agents, orders, customers, products = get_data()
    return prepare(tickets, agents, orders, products)
@st.cache_data
def get_metrics():
    t=get_prepared(); return agent_metrics(t), monthly_metrics(t), business_goal(t)
@st.cache_data
def get_lots():
    t=get_prepared(); lm=lot_monitor(t); return lm, lot_cost_analysis(t,lm), lot_backtest(t,lm)
@st.cache_resource
def get_text_model(): return build_text_model(get_prepared())

t=get_prepared(); ag,monthly,goal=get_metrics(); lots,money,backtest=get_lots()

st.sidebar.header("Filters")
teams=st.sidebar.multiselect("Tier 1 team", sorted(ag.loc[ag.tier==1,"team"].dropna().unique()), default=sorted(ag.loc[ag.tier==1,"team"].dropna().unique()))
min_surveys=st.sidebar.number_input("Minimum CSAT responses", min_value=0, value=50, step=10)
period=st.sidebar.selectbox("Trend period", ["All","2025 H2","2026 H1"])

if period=="2025 H2": tt=t[t.created_ist.between("2025-07-01","2025-12-31 23:59:59")]
elif period=="2026 H1": tt=t[t.created_ist.between("2026-01-01","2026-06-30 23:59:59")]
else: tt=t
att=tt[tt.attendance]
c1,c2,c3,c4=st.columns(4)
c1.metric("CSAT", f"{att.csat_score.mean():.2f}/5")
c2.metric("Avg handle", f"{att.handle_min.mean():.0f} min")
c3.metric("Replacement rate", f"{(att.replacement_issued=='Y').mean():.1%}")
c4.metric("First-response breaches", f"{att.breach.mean():.1%}")

st.subheader("Business goal")
st.info(f"**Operational target:** reduce H1 2026 replacement rate from **{goal['h1_rate']:.1%} to 15%**. At the H1 run-rate and observed average replacement cost of **₹{goal['avg_replacement_cost']:,.0f}**, the scenario is about **₹{goal['quarterly_saving']:,.0f} per quarter**. This is a planning scenario, not a forecast.")

st.subheader("Root-cause signal: Pulse 2 production lots")
st.write("A lot-level monitor finds three Pulse 2 cohorts with unusually high replacement rates. This is a statistical anomaly signal; it does not by itself prove a physical manufacturing defect.")
mc1,mc2,mc3=st.columns(3)
mc1.metric("Flagged lots", len(money["bad_lots"]))
mc2.metric("Bad-lot replacement rate", f"{money['bad_lot_rate']:.1%}")
mc3.metric("Excess replacement cost", f"₹{money['excess_cost']:,.0f}")
show=lots[lots["product_sku"].eq("VA-EB-PL2")].head(8).copy()
st.dataframe(show[["product_sku","lot_month","tickets","replacements","replacement_rate","sku_baseline","z_score","flag"]].rename(columns={"lot_month":"Lot","tickets":"Tickets","replacements":"Replacements","replacement_rate":"Replacement rate","sku_baseline":"SKU baseline","z_score":"Z-score","flag":"Flag"}), use_container_width=True, hide_index=True)

st.caption("The historical replay would have crossed the monitor threshold on 26 Nov 2025 (lot 2510), 3 Jan 2026 (2511), and 12 Feb 2026 (2512).")
st.dataframe(backtest[backtest.bad][["lot_month","first_ticket","alarm_date","tickets"]].rename(columns={"lot_month":"Lot","first_ticket":"First ticket","alarm_date":"Alarm date","tickets":"Tickets"}), use_container_width=True, hide_index=True)

st.subheader("Agent dashboard")
a=ag[(ag.tier==1)&ag.team.isin(teams)&(ag.csat_responses>=min_surveys)].copy(); a["handle_time_hours"]=a.handle_min/60
cols=["agent_id","name","team","tickets","csat_responses","csat","handle_time_hours","breach_rate","replacements"]
st.dataframe(a.sort_values("csat")[cols].rename(columns={"csat":"CSAT","handle_time_hours":"Avg handle (hrs)","breach_rate":"Breach rate"}),use_container_width=True,hide_index=True)
st.caption("Tier 2 Escalations & Warranty is not ranked against Tier 1. All joins use agent_id, never display name.")

st.subheader("Bottom-10 review queue")
bottom=a.sort_values("csat").head(10).copy(); bottom["flag"]="Review"
st.dataframe(bottom[["agent_id","name","team","csat_responses","csat","handle_time_hours","breach_rate","flag"]].rename(columns={"csat_responses":"CSAT responses","csat":"CSAT","handle_time_hours":"Avg handle (hrs)","breach_rate":"Breach rate"}),use_container_width=True,hide_index=True)
st.warning("This is a review queue, not an automatic performance verdict. Queue mix, hardware triage, channel and case complexity can affect raw CSAT.")

st.subheader("Trend")
tm=monthly.copy()
if period=="2025 H2": tm=tm[tm.month.between("2025-07","2025-12")]
elif period=="2026 H1": tm=tm[tm.month.between("2026-01","2026-06")]
st.line_chart(tm.set_index("month")[["csat","replacement_rate"]])

st.subheader("AI-assisted text check")
st.write("Local TF-IDF + logistic regression on customer opening messages. No per-ticket paid model calls are required.")
if st.button("Run validation"):
    model,acc=get_text_model(); st.metric("Held-out category accuracy",f"{acc:.1%}")
    st.caption("This validates the text-classification component only; it is not a causal model of CSAT.")
    sample=t[["ticket_id","category","customer_message"]].sample(min(20,len(t)),random_state=42).copy(); sample["predicted_category"]=model.predict(sample.customer_message.fillna("")); st.dataframe(sample,use_container_width=True,hide_index=True)

st.subheader("Queue-adjusted review check")
flags,mae=queue_adjusted_flags(t)
st.caption(f"Cross-validated MAE: {mae:.2f} CSAT points. This controls for team, channel, category, priority and month; it is a review aid, not a causal personnel model.")
st.dataframe(flags.head(10),use_container_width=True,hide_index=True)

st.subheader("Method / controls")
st.markdown("""
- **CSAT:** blank surveys excluded.
- **Handle time:** first human response → resolution; legacy resolution timestamps shifted UTC→IST.
- **SLA:** chat 15m, voice 120m, social 240m, email 480m.
- **Replacement cost:** product unit cost + ₹340 logistics per policy.
- **Lot linkage:** exact order_id first; otherwise latest prior order for same customer + SKU; tickets before their order are not assigned a lot.
- **Agent identity:** joins use `agent_id`, never name.
- **AI cost control:** local classifier; no per-ticket paid API calls.
""")
