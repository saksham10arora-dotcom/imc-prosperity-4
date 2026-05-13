"""14: Time-of-day patterns.
Bucket each tick within a day (0-9999) into 20 buckets of 500 ticks each.
For each pair in K=1 portfolio:
- Mean dmid std per bucket
- Z-score firing rate per bucket
- Win rate per bucket
For each product:
- Per-bucket mean spread (ask - bid)
- Per-bucket trade count (proxy for activity)
Output: r5_research/output/14_time_of_day.csv
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__file__.rsplit("/", 1)[0]))
import pandas as pd
import numpy as np
from lib import load_prices, load_trades, pivot_mid, pivot_field, all_products

px = load_prices()
tr = load_trades()
mid = pivot_mid(px)

DAY = 10000
N_BUCKETS = 20
B = DAY // N_BUCKETS  # 500


# Per-product activity by bucket (avg over 3 days)
print("=== Per-product activity by bucket (avg over D2-D4) ===")
rows = []
for prod in all_products():
    sub = px[px["product"] == prod].copy()
    if len(sub) == 0:
        continue
    sub["bucket"] = (sub["timestamp"] // 100 // B).astype(int)
    spread = sub["ask_price_1"] - sub["bid_price_1"]
    g = sub.groupby("bucket").agg(spread_mean=("bid_price_1", lambda x: np.nan),  # placeholder
                                    n=("timestamp", "size")).reset_index()
    # compute spread mean
    sub["sp"] = sub["ask_price_1"] - sub["bid_price_1"]
    g_sp = sub.groupby("bucket")["sp"].mean()
    sub["dmid"] = sub.groupby("day")["mid_price"].diff()
    g_dmid = sub.groupby("bucket")["dmid"].std()
    for bk in range(N_BUCKETS):
        rows.append({
            "product": prod,
            "bucket": bk,
            "tick_start": bk * B,
            "spread_mean": float(g_sp.get(bk, np.nan)),
            "dmid_std": float(g_dmid.get(bk, np.nan)),
        })
prod_df = pd.DataFrame(rows)
prod_df.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/14_product_buckets.csv", index=False)

# Aggregate across products: which buckets have highest dmid_std (volatile windows)?
agg = prod_df.groupby("bucket").agg(
    avg_spread=("spread_mean", "mean"),
    avg_dmid_std=("dmid_std", "mean"),
).reset_index()
print(agg.to_string(index=False))

# Trade-count buckets
print("\n=== Trade counts per bucket (sum across all products, all 3 days) ===")
tr["bucket"] = (tr["timestamp"] // 100 // B).astype(int)
print(tr.groupby("bucket").agg(n_trades=("symbol","size"), total_qty=("quantity","sum")).to_string())

# Per-pair PnL by bucket on day-4 OOS
ZE, ZX, LOT, W = 1.5, 0.3, 10, 2000
def bucket_of(idx):
    return (idx % DAY) // B

port = pd.read_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/08_portfolio_K1.csv")

print("\n=== Per-bucket PnL of K=1 portfolio on D4 OOS ===")
all_bucket_pnl = np.zeros(N_BUCKETS)
all_bucket_n = np.zeros(N_BUCKETS, dtype=int)
all_bucket_w = np.zeros(N_BUCKETS, dtype=int)

for _, p in port.iterrows():
    a, b = p["a"], p["b"]
    sp = (mid[a] - mid[b]).values
    s = pd.Series(sp)
    m = s.rolling(W, min_periods=W).mean().values
    sd = s.rolling(W, min_periods=W).std().values
    # Trade only D4
    pos, ent, ent_idx = 0, 0.0, 0
    d4_start = 2 * DAY
    for i in range(d4_start, 3 * DAY):
        if np.isnan(sd[i]) or sd[i] <= 0 or np.isnan(m[i]):
            continue
        z = (sp[i] - m[i]) / sd[i]
        if pos == 0:
            if z >= ZE: pos, ent, ent_idx = -1, sp[i], i
            elif z <= -ZE: pos, ent, ent_idx = +1, sp[i], i
        elif abs(z) <= ZX:
            g = (sp[i] - ent) * pos * LOT
            bk = bucket_of(ent_idx)
            all_bucket_pnl[bk] += g
            all_bucket_n[bk] += 1
            all_bucket_w[bk] += int(g > 0)
            pos = 0

bucket_df = pd.DataFrame({
    "bucket": range(N_BUCKETS),
    "tick_start": [b * B for b in range(N_BUCKETS)],
    "tick_end": [(b+1) * B - 1 for b in range(N_BUCKETS)],
    "pnl": all_bucket_pnl,
    "n_trades": all_bucket_n,
    "wins": all_bucket_w,
    "winrate": all_bucket_w / np.where(all_bucket_n > 0, all_bucket_n, 1),
})
bucket_df.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/14_time_of_day.csv", index=False)
print(bucket_df.to_string(index=False))
print(f"\nMost-PnL bucket: {bucket_df['bucket'][bucket_df['pnl'].idxmax()]} "
      f"(ticks {bucket_df['tick_start'][bucket_df['pnl'].idxmax()]}–{bucket_df['tick_end'][bucket_df['pnl'].idxmax()]})")
