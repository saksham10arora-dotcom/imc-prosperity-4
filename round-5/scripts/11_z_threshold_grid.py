"""11: Z-threshold grid over the K=1 portfolio.
Test entry z ∈ {1.0, 1.25, 1.5, 1.75, 2.0, 2.5} × exit z ∈ {0.0, 0.2, 0.3, 0.5, 0.75}.
Optimum across the portfolio total.
Output: r5_research/output/11_z_grid.csv
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__file__.rsplit("/", 1)[0]))
import pandas as pd
import numpy as np
from lib import load_prices, pivot_mid

px = load_prices()
mid = pivot_mid(px)

DAY = 10000
LOT, W = 10, 2000


def trade(spread, m, s, ze, zx):
    pos, ent, pnl, n, w = 0, 0.0, 0.0, 0, 0
    for i in range(len(spread)):
        if np.isnan(s[i]) or s[i] <= 0 or np.isnan(m[i]):
            continue
        z = (spread[i] - m[i]) / s[i]
        if pos == 0:
            if z >= ze: pos, ent = -1, spread[i]
            elif z <= -ze: pos, ent = +1, spread[i]
        elif abs(z) <= zx:
            g = (spread[i] - ent) * pos * LOT
            pnl += g; n += 1; w += int(g > 0); pos = 0
    if pos != 0:
        g = (spread[-1] - ent) * pos * LOT
        pnl += g; n += 1; w += int(g > 0)
    return pnl, n, w


ENTRIES = [1.0, 1.25, 1.5, 1.75, 2.0, 2.5]
EXITS = [0.0, 0.1, 0.2, 0.3, 0.5, 0.75]

port = pd.read_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/08_portfolio_K1.csv")

# Pre-compute (m, s) for each pair
cache = {}
for _, p in port.iterrows():
    a, b = p["a"], p["b"]
    sp = (mid[a] - mid[b]).values
    s = pd.Series(sp)
    m = s.rolling(W, min_periods=W).mean().values
    sd = s.rolling(W, min_periods=W).std().values
    cache[(a, b)] = (sp, m, sd)

# Aggregate over portfolio
agg_rows = []
for ze in ENTRIES:
    for zx in EXITS:
        if zx >= ze:
            continue
        total_pnl, total_n, total_w = 0, 0, 0
        d4_pnl, d4_n, d4_w = 0, 0, 0
        for (a, b), (sp, m, sd) in cache.items():
            pnl, n, w = trade(sp, m, sd, ze, zx)
            pnl4, n4, w4 = trade(sp[2*DAY:3*DAY], m[2*DAY:3*DAY], sd[2*DAY:3*DAY], ze, zx)
            total_pnl += pnl; total_n += n; total_w += w
            d4_pnl += pnl4; d4_n += n4; d4_w += w4
        agg_rows.append({
            "entry_z": ze, "exit_z": zx,
            "total_pnl": total_pnl, "total_n": total_n, "total_w": total_w,
            "d4_pnl": d4_pnl, "d4_n": d4_n, "d4_w": d4_w,
            "winrate": total_w / total_n if total_n > 0 else 0,
            "d4_winrate": d4_w / d4_n if d4_n > 0 else 0,
        })

df = pd.DataFrame(agg_rows).sort_values("d4_pnl", ascending=False)
df.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/11_z_grid.csv", index=False)

print("=== Z-grid over the K=1 robust portfolio (sorted by D4 OOS PnL) ===")
print(df.to_string(index=False))

print("\n=== Pivot: D4 OOS PnL ===")
print(df.pivot(index="entry_z", columns="exit_z", values="d4_pnl").to_string())

print("\n=== Pivot: D4 OOS win rate ===")
print(df.pivot(index="entry_z", columns="exit_z", values="d4_winrate").to_string(float_format=lambda x: f"{x:.2f}"))

print("\n=== Pivot: full-3day total PnL ===")
print(df.pivot(index="entry_z", columns="exit_z", values="total_pnl").to_string())

print("\n=== Pivot: D4 #trades ===")
print(df.pivot(index="entry_z", columns="exit_z", values="d4_n").to_string())
