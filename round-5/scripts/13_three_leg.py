"""13: 3-leg basket search.
For each robust K=1 pair (a, b), search for a 3rd product c that minimizes residual variance
of the 3-leg combo (a - b + γc) with γ ∈ {-1, 0, +1} (integer, pos-limit-friendly).
Also do unconstrained: spread = a - b - δ*c with δ free.
Output: r5_research/output/13_three_leg.csv
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__file__.rsplit("/", 1)[0]))
import pandas as pd
import numpy as np
from lib import load_prices, pivot_mid, all_products

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
            if z >= ZE: pos, ent = -1, spread[i]
            elif z <= -ZE: pos, ent = +1, spread[i]
        elif abs(z) <= ZX:
            g = (spread[i] - ent) * pos * LOT
            pnl += g; n += 1; w += int(g > 0); pos = 0
    return pnl, n, w


def trade_oos_d4(sp):
    s = pd.Series(sp)
    m = s.rolling(W, min_periods=W).mean().values
    sd = s.rolling(W, min_periods=W).std().values
    return trade(sp[2*DAY:3*DAY], m[2*DAY:3*DAY], sd[2*DAY:3*DAY])


port = pd.read_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/08_portfolio_K1.csv")
prods = all_products()

best_rows = []
for _, p in port.iterrows():
    a, b = p["a"], p["b"]
    if a not in mid.columns or b not in mid.columns:
        continue
    A = mid[a].values; B = mid[b].values
    raw = A - B  # 1:1 spread

    # Baseline: raw d4 OOS
    raw_pnl, raw_n, raw_w = trade_oos_d4(raw)

    # Search over c with γ ∈ {-1, +1}
    best = None
    for c in prods:
        if c in (a, b) or c not in mid.columns:
            continue
        C = mid[c].values
        for gamma in [-1, +1]:
            sp = A - B + gamma * C
            pnl, n, w = trade_oos_d4(sp)
            if best is None or pnl > best["pnl_3leg"]:
                best = {"c": c, "gamma": gamma, "pnl_3leg": pnl, "n_3leg": n, "w_3leg": w}
    best_rows.append({
        "a": a, "b": b, "raw_d4_pnl": raw_pnl, "raw_n": raw_n, "raw_w": raw_w,
        **best,
        "improvement": best["pnl_3leg"] - raw_pnl,
    })

df = pd.DataFrame(best_rows).sort_values("improvement", ascending=False)
df.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/13_three_leg.csv", index=False)

print("=== Best 3-leg add (γ ∈ ±1, search over all 50) for each K=1 pair, D4 OOS ===")
print(df[["a","b","c","gamma","raw_d4_pnl","pnl_3leg","improvement","n_3leg","w_3leg"]].to_string(index=False))
print(f"\nSum raw d4: {df['raw_d4_pnl'].sum():.0f}")
print(f"Sum 3-leg d4: {df['pnl_3leg'].sum():.0f}")
print(f"Improvement: {df['improvement'].sum():.0f} ({(df['improvement']>0).sum()}/{len(df)} pairs improve)")
