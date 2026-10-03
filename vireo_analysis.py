from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import KFold, cross_val_score

TARGETS = {"chat":15, "voice":120, "social":240, "email":480}


def load_data(data_dir="data"):
    d = Path(data_dir)
    def find(suffix):
        xs = list(d.glob(f"*{suffix}"))
        if not xs:
            raise FileNotFoundError(f"Missing {suffix} under {d}")
        return xs[0]
    tickets = pd.read_csv(find("tickets.csv"))
    agents = pd.read_csv(find("agents.csv"))
    orders = pd.read_csv(find("orders.csv"))
    customers = pd.read_csv(find("customers.csv"))
    products = pd.read_csv(find("products.csv"))
    return tickets, agents, orders, customers, products


def prepare(tickets, agents, orders, products):
    t = tickets.copy()
    for c in ["created_at", "first_response_at", "resolved_at"]:
        t[c+"_dt"] = pd.to_datetime(t[c], errors="coerce")
    t["created_ist"] = t["created_at_dt"]
    t["first_ist"] = t["first_response_at_dt"]
    t["resolved_ist"] = t["resolved_at_dt"]
    legacy = t["source_system"].eq("legacy_fd") & t["resolved_at_dt"].notna()
    t.loc[legacy, "resolved_ist"] = t.loc[legacy, "resolved_at_dt"] + pd.Timedelta(hours=5, minutes=30)
    t["response_min"] = (t["first_ist"] - t["created_ist"]).dt.total_seconds()/60
    t["handle_min"] = (t["resolved_ist"] - t["first_ist"]).dt.total_seconds()/60
    t["target_min"] = t["channel"].map(TARGETS)
    t["breach"] = t["response_min"] > t["target_min"]
    t["attendance"] = t["status"].isin(["resolved", "closed"])
    t["month"] = t["created_ist"].dt.to_period("M").astype(str)
    t = t.merge(agents[["agent_id","name","site","team","shift","tier"]], on="agent_id", how="left")
    unit_cost = products.set_index("sku")["unit_cost_inr"]
    t["replacement_cost_inr"] = np.where(t["replacement_issued"].eq("Y"), t["product_sku"].map(unit_cost).fillna(0) + 340, 0)
    t["refund_flag"] = t["refund_amount_inr"].fillna(0).gt(0)

    # Exact order join, then a conservative fallback: latest prior order for same customer + SKU.
    t = t.merge(orders[["order_id","customer_id","sku","lot_code","order_date"]], on="order_id", how="left", suffixes=("", "_order"))
    t["pre_order"] = t["order_date"].notna() & (t["created_ist"] < pd.to_datetime(t["order_date"]) - pd.Timedelta(days=1))
    t.loc[t["pre_order"], "lot_code"] = np.nan
    t["lot_exact"] = t["lot_code"]
    missing = t["lot_code"].isna()
    oo = orders.rename(columns={"sku":"product_sku", "order_date":"od", "lot_code":"lc"})[["customer_id","product_sku","od","lc"]].copy()
    oo["od"] = pd.to_datetime(oo["od"])
    oo = oo.sort_values("od")
    fb = pd.merge_asof(
        t.loc[missing, ["ticket_id","customer_id","product_sku","created_ist"]].sort_values("created_ist"),
        oo,
        left_on="created_ist", right_on="od", by=["customer_id","product_sku"]
    )
    t = t.merge(fb[["ticket_id","lc"]], on="ticket_id", how="left")
    t["lot_code_final"] = t["lot_code"].fillna(t["lc"])
    t["lot_exact_match"] = t["lot_exact"].notna()
    t["lot_month"] = t["lot_code_final"].astype("string").str.split("-").str[1]
    t["junk_ivr"] = t["customer_message"].fillna("").str.contains(r"\[(?:inaudible|crosstalk|line dropped)\]", regex=True) | t["customer_message"].fillna("").str.replace(r"\[IVR transcript\]", "", regex=True).str.count(r"[A-Za-z]").lt(4)
    return t


def agent_metrics(t):
    x=t[t.attendance].copy()
    return x.groupby(["agent_id","name","team","tier"]).agg(
        tickets=("ticket_id","count"), csat_responses=("csat_score","count"), csat=("csat_score","mean"),
        handle_min=("handle_min","mean"), median_handle_min=("handle_min","median"), breach_rate=("breach","mean"),
        transfers=("transfers","sum"), replacements=("replacement_issued", lambda s:(s=="Y").sum()),
        replacement_cost=("replacement_cost_inr","sum")
    ).reset_index()


def monthly_metrics(t):
    x=t[t.attendance]
    m=x.groupby("month").agg(tickets=("ticket_id","count"), csat_responses=("csat_score","count"), csat=("csat_score","mean"), replacements=("replacement_issued",lambda s:(s=="Y").sum()), replacement_cost=("replacement_cost_inr","sum"), breaches=("breach","sum"), transfers=("transfers","sum")).reset_index()
    m["replacement_rate"] = m["replacements"]/m["tickets"]
    m["breach_rate"] = m["breaches"]/m["tickets"]
    return m


def build_text_model(t):
    text=t["customer_message"].fillna("").astype(str); labels=t["category"].astype(str); valid=text.str.len()>10
    Xtr,Xte,ytr,yte=train_test_split(text[valid],labels[valid],test_size=.20,random_state=42,stratify=labels[valid])
    pipe=Pipeline([("tfidf",TfidfVectorizer(ngram_range=(1,2),min_df=2,max_features=30000,sublinear_tf=True)),("clf",LogisticRegression(max_iter=500,C=3))])
    pipe.fit(Xtr,ytr); pred=pipe.predict(Xte)
    return pipe, accuracy_score(yte,pred)


def queue_adjusted_flags(t):
    survey=t[(t.attendance)&(t.tier==1)&t.csat_score.notna()].copy(); survey["month_num"]=survey.created_ist.dt.to_period("M").astype(str)
    features=["team","channel","category","priority","month_num"]
    pre=ColumnTransformer([("cat",OneHotEncoder(handle_unknown="ignore"),features)])
    pipe=Pipeline([("pre",pre),("reg",Ridge(alpha=10))])
    cv=KFold(n_splits=5,shuffle=True,random_state=42)
    cv_mae=float(-cross_val_score(pipe,survey[features],survey.csat_score,cv=cv,scoring="neg_mean_absolute_error").mean())
    pipe.fit(survey[features],survey.csat_score); survey["expected_csat"]=pipe.predict(survey[features]); survey["residual"]=survey.csat_score-survey.expected_csat
    flags=survey.groupby(["agent_id","name","team"]).agg(csat=("csat_score","mean"),csat_responses=("csat_score","count"),expected_csat=("expected_csat","mean"),residual=("residual","mean")).reset_index()
    flags=flags[flags.csat_responses>=50].sort_values("residual").copy(); flags["review_rank"]=range(1,len(flags)+1)
    return flags, cv_mae


def lot_monitor(t):
    x=t.dropna(subset=["lot_month"]).copy()
    x=x[x["attendance"]]
    g=x.groupby(["product_sku","lot_month"]).agg(tickets=("ticket_id","size"), replacements=("replacement_issued",lambda s:(s=="Y").sum()), replacement_rate=("replacement_issued",lambda s:(s=="Y").mean())).reset_index()
    big=g[g.tickets>=30].copy()
    base=big.groupby("product_sku").replacement_rate.median().rename("sku_baseline").reset_index()
    g=g.merge(base,on="product_sku",how="left")
    p=g.sku_baseline.clip(1e-6,1-1e-6)
    g["z_score"]=(g.replacements-g.tickets*p)/np.sqrt(g.tickets*p*(1-p))
    g["flag"]=(g.tickets>=30)&(g.z_score>5)
    return g.sort_values("z_score",ascending=False)


def lot_cost_analysis(t, lot_table):
    bad=set(map(tuple,lot_table.loc[lot_table.flag,["product_sku","lot_month"]].values))
    x=t.copy(); x["bad_lot"]=[(s,l) in bad for s,l in zip(x.product_sku,x.lot_month)]
    pl=x[x.product_sku.eq("VA-EB-PL2") & x.attendance].copy()
    base=float(pl.loc[~pl.bad_lot,"replacement_issued"].eq("Y").mean())
    badx=pl[pl.bad_lot]
    unit=float(badx["replacement_cost_inr"].replace(0,np.nan).dropna().iloc[0]-340) if not badx.empty else 0
    cost=unit+340
    excess=float(badx["replacement_issued"].eq("Y").sum()-base*len(badx))
    return {"bad_lot_tickets":len(badx),"bad_lot_rate":float(badx.replacement_issued.eq("Y").mean()),"baseline_rate":base,"excess_replacements":excess,"unit_cost":unit,"replacement_cost":cost,"excess_cost":excess*cost,"bad_lots":sorted(bad)}


def lot_backtest(t, lot_table):
    bad=set(map(tuple,lot_table.loc[lot_table.flag,["product_sku","lot_month"]].values))
    x=t[(t.product_sku=="VA-EB-PL2")&t.lot_month.notna()&t.attendance].copy().sort_values("created_ist")
    base=float(x.loc[~x.apply(lambda r:(r.product_sku,r.lot_month) in bad,axis=1),"replacement_issued"].eq("Y").mean())
    rows=[]
    for lot,d in x.groupby("lot_month"):
        d=d.sort_values("created_ist"); alarm=None
        for i in range(15,len(d)+1):
            y=d.iloc[:i]["replacement_issued"].eq("Y").sum(); z=(y-i*base)/np.sqrt(i*base*(1-base))
            if z>4: alarm=d.iloc[i-1].created_ist; break
        rows.append({"lot_month":lot,"bad":(d.product_sku.iloc[0],lot) in bad,"first_ticket":d.created_ist.iloc[0],"alarm_date":alarm,"tickets":len(d)})
    return pd.DataFrame(rows)


def business_goal(t):
    h1=t[(t.attendance)&(t.created_ist>="2026-01-01")&(t.created_ist<"2026-07-01")]
    q4=t[(t.attendance)&(t.created_ist>="2025-10-01")&(t.created_ist<"2026-01-01")]
    current_rate=float((h1.replacement_issued=="Y").mean()); target=.15
    avg_rep_cost=float(h1.loc[h1.replacement_issued=="Y","replacement_cost_inr"].mean())
    quarterly_saving=max(0,(current_rate-target))*(len(h1)/2)*avg_rep_cost
    return {"h1_rate":current_rate,"q4_rate":float((q4.replacement_issued=="Y").mean()),"target":target,"avg_replacement_cost":avg_rep_cost,"quarterly_saving":quarterly_saving,"h1_tickets":len(h1),"h1_replacements":int((h1.replacement_issued=="Y").sum())}
