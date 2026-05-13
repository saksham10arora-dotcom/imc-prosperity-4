"""07: Trade-flow / order-book imbalance signal.
For each product, build:
- OBI = (bid_v_top - ask_v_top) / (bid_v_top + ask_v_top)
- Trade signed-flow at tick t: sign of (trade_price - mid_price_t-1) × qty
- Mid return at t+1, t+5, t+10
Compute corr(OBI_t, dmid_{t+k}) and corr(flow_t, dmid_{t+k}).
Output: r5_research/output/07_flow.csv
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__file__.rsplit("/", 1)[0]))
import pandas as pd
import numpy as np
from lib import load_prices, load_trades, all_products

px = load_prices()
tr = load_trades()

DAY = 10000
LAGS = [1, 5, 10, 50]

rows = []
for prod in all_products():
    sub = px[px["product"] == prod].sort_values("gt").reset_index(drop=True)
    if len(sub) < 1000:
        continue
    bv = sub["bid_volume_1"].fillna(0).values.astype(float)
    av = sub["ask_volume_1"].fillna(0).values.astype(float)
    obi = np.where((bv + av) > 0, (bv - av) / (bv + av), 0.0)
    mid = sub["mid_price"].values
    dmid = np.diff(mid)
    rec = {"product": prod}
    for k in LAGS:
        if k < len(dmid):
            rec[f"corr_obi_dmid_lag{k}"] = float(pd.Series(obi[:-k]).corr(pd.Series(dmid[k-1:])))
    # OBI autocorr
    rec["ac1_obi"] = float(pd.Series(obi).autocorr(lag=1))
    rec["obi_mean"] = float(np.mean(obi))
    rec["obi_std"] = float(np.std(obi))

    # Aggregate trade flow per tick (signed by trade vs mid)
    t_sub = tr[tr["symbol"] == prod].copy()
    if len(t_sub) > 100:
        t_sub = t_sub.sort_values(["day", "timestamp"]).reset_index(drop=True)
        # Aggregate to per-tick signed flow
        t_sub["mid_at_tick"] = t_sub["gt"].map(lambda g: mid[g] if g < len(mid) else np.nan)
        t_sub["sign"] = np.sign(t_sub["price"] - t_sub["mid_at_tick"]).fillna(0)
        t_sub["signed_qty"] = t_sub["sign"] * t_sub["quantity"]
        flow = t_sub.groupby("gt")["signed_qty"].sum()
        flow = flow.reindex(np.arange(len(mid)), fill_value=0).values
        for k in LAGS:
            if k < len(dmid):
                rec[f"corr_flow_dmid_lag{k}"] = float(pd.Series(flow[:-k]).corr(pd.Series(dmid[k-1:])))
        rec["flow_mean"] = float(flow[flow != 0].mean()) if (flow != 0).any() else 0.0
        rec["flow_total"] = float(flow.sum())
    rows.append(rec)

df = pd.DataFrame(rows)
df.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/07_flow.csv", index=False)

print("=== Top 10 |corr(OBI_t, dmid_{t+1})| (predictive OBI) ===")
df["abs_obi1"] = df["corr_obi_dmid_lag1"].abs()
print(df.sort_values("abs_obi1", ascending=False).head(10)[
    ["product", "corr_obi_dmid_lag1", "corr_obi_dmid_lag5", "corr_obi_dmid_lag10", "corr_obi_dmid_lag50"]
].to_string(index=False))

print("\n=== Top 10 |corr(flow_t, dmid_{t+1})| (predictive flow) ===")
if "corr_flow_dmid_lag1" in df.columns:
    df["abs_flow1"] = df["corr_flow_dmid_lag1"].abs()
    print(df.sort_values("abs_flow1", ascending=False).head(10)[
        ["product", "corr_flow_dmid_lag1", "corr_flow_dmid_lag5", "corr_flow_dmid_lag10"]
    ].to_string(index=False))

print("\n=== Distribution of corr(OBI, dmid+1) ===")
print(df["corr_obi_dmid_lag1"].describe())
