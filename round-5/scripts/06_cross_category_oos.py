"""06: Out-of-sample test for cross-cat winners.
For all 1225 pairs, train on days 2+3, trade day 4 with rolling-z (window=2000).
Compares to in-sample full-3-day. Flags pairs where in-sample is high but OOS is poor (curve-fit).
Output: r5_research/output/06_cross_category_oos.csv
"""
from __future__ import annotations
import sys, time
sys.path.insert(0, str(__file__.rsplit("/", 1)[0]))
import pandas as pd
import numpy as np
from itertools import combinations
from lib import load_prices, pivot_mid, all_products, category_of

px = load_prices()
mid = pivot_mid(px)

DAY = 10000
ZE, ZX, LOT, W = 1.5, 0.3, 10, 2000


def trade(spread, m, s):
    pos, ent, pnl, n, w = 0, 0.0, 0.0, 0, 0
    for i in range(len(spread)):
        if np.isnan(s[i]) or s[i] <= 0 or np.isnan(m[i]):
            continue
        z = (spread[i] - m[i]) / s[i]
        if pos == 0:
            if z >= ZE: pos = -1; ent = spread[i]
            elif z <= -ZE: pos = +1; ent = spread[i]
        elif abs(z) <= ZX:
            g = (spread[i] - ent) * pos * LOT
            pnl += g; n += 1; w += int(g > 0); pos = 0
    if pos != 0:
        g = (spread[-1] - ent) * pos * LOT
        pnl += g; n += 1; w += int(g > 0)
    return pnl, n, w


prods = all_products()
rows = []
t0 = time.time()
total = len(prods) * (len(prods) - 1) // 2
done = 0
for a, b in combinations(prods, 2):
    if a not in mid.columns or b not in mid.columns:
        continue
    sp = (mid[a] - mid[b]).values
    s = pd.Series(sp)
    m = s.rolling(W, min_periods=W).mean().values
    sd = s.rolling(W, min_periods=W).std().values
    sp_d4 = sp[2*DAY:3*DAY]
    m_d4 = m[2*DAY:3*DAY]
    sd_d4 = sd[2*DAY:3*DAY]
    pnl_oos, n_oos, w_oos = trade(sp_d4, m_d4, sd_d4)
    pnl_full, n_full, w_full = trade(sp, m, sd)
    rows.append({
        "a": a, "b": b,
        "cat_a": category_of(a), "cat_b": category_of(b),
        "same_cat": int(category_of(a) == category_of(b)),
        "spread_std": float(sp.std()),
        "drift_d2_d4": float(sp[-1] - sp[0]),
        "in_sample_pnl": pnl_full,
        "in_sample_n": n_full,
        "oos_d4_pnl": pnl_oos,
        "oos_d4_n": n_oos,
        "oos_d4_w": w_oos,
    })
    done += 1

df = pd.DataFrame(rows)
df["oos_winrate"] = df["oos_d4_w"] / df["oos_d4_n"].replace(0, np.nan)
df["robustness"] = (df["oos_d4_pnl"] / df["in_sample_pnl"].replace(0, np.nan)).clip(-2, 5)
df.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/06_cross_category_oos.csv", index=False)
print(f"\n{len(df)} pairs in {time.time()-t0:.0f}s")

print("\n=== TOP 30 by Day-4 OOS PnL ===")
top = df.sort_values("oos_d4_pnl", ascending=False).head(30)
print(top[["a", "b", "same_cat", "in_sample_pnl", "oos_d4_pnl", "oos_d4_n", "oos_winrate", "drift_d2_d4"]].to_string(index=False))

print("\n=== TOP 30 within-cat by OOS PnL ===")
top_w = df[df["same_cat"]==1].sort_values("oos_d4_pnl", ascending=False).head(30)
print(top_w[["a", "b", "in_sample_pnl", "oos_d4_pnl", "oos_d4_n", "oos_winrate"]].to_string(index=False))

print("\n=== TOP 30 cross-cat by OOS PnL ===")
top_c = df[df["same_cat"]==0].sort_values("oos_d4_pnl", ascending=False).head(30)
print(top_c[["a", "b", "in_sample_pnl", "oos_d4_pnl", "oos_d4_n", "oos_winrate", "drift_d2_d4"]].to_string(index=False))

print("\n=== Worst overfit: high in-sample, negative OOS ===")
overfit = df[(df["in_sample_pnl"] > 30000) & (df["oos_d4_pnl"] < 0)].sort_values("oos_d4_pnl").head(15)
print(overfit[["a", "b", "in_sample_pnl", "oos_d4_pnl", "drift_d2_d4"]].to_string(index=False))

print("\n=== Stable signals (both in-sample and OOS positive, OOS > 5000) ===")
stable = df[(df["in_sample_pnl"] > 0) & (df["oos_d4_pnl"] > 5000)].sort_values("oos_d4_pnl", ascending=False)
print(f"  count: {len(stable)}")
print(f"  total OOS PnL across these: {stable['oos_d4_pnl'].sum():.0f}")
print(f"  Within-cat: {stable['same_cat'].sum()}, Cross-cat: {(1-stable['same_cat']).sum()}")
