"""09: For the K=1 portfolio, compute per-day PnL of the rolling-z strategy.
This catches pairs whose total PnL is concentrated on one day (less robust forecast).
Output: r5_research/output/09_day_stability.csv
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
ZE, ZX, LOT, W = 1.5, 0.3, 10, 2000


def trade_per_segment(spread, m, s, segments):
    """Return per-segment PnL given pre-computed (m, s).
    segments: list of (start, end) indices.
    """
    pos, ent = 0, 0.0
    seg_pnl = [0.0] * len(segments)
    seg_n = [0] * len(segments)
    seg_w = [0] * len(segments)

    def which_seg(i):
        for k, (s0, e) in enumerate(segments):
            if s0 <= i < e:
                return k
        return -1

    for i in range(len(spread)):
        if np.isnan(s[i]) or s[i] <= 0 or np.isnan(m[i]):
            continue
        z = (spread[i] - m[i]) / s[i]
        if pos == 0:
            if z >= ZE: pos, ent = -1, spread[i]; entry_seg = which_seg(i)
            elif z <= -ZE: pos, ent = +1, spread[i]; entry_seg = which_seg(i)
        elif abs(z) <= ZX:
            seg_idx = which_seg(i)
            g = (spread[i] - ent) * pos * LOT
            seg_pnl[seg_idx] += g
            seg_n[seg_idx] += 1
            seg_w[seg_idx] += int(g > 0)
            pos = 0
    return seg_pnl, seg_n, seg_w


# Load K=1 portfolio
port = pd.read_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/08_portfolio_K1.csv")
segments = [(0, DAY), (DAY, 2*DAY), (2*DAY, 3*DAY)]

rows = []
for _, p in port.iterrows():
    a, b = p["a"], p["b"]
    sp = (mid[a] - mid[b]).values
    s = pd.Series(sp)
    m = s.rolling(W, min_periods=W).mean().values
    sd = s.rolling(W, min_periods=W).std().values
    seg_pnl, seg_n, seg_w = trade_per_segment(sp, m, sd, segments)
    rows.append({
        "a": a, "b": b,
        "d2_pnl": seg_pnl[0], "d2_n": seg_n[0],
        "d3_pnl": seg_pnl[1], "d3_n": seg_n[1],
        "d4_pnl": seg_pnl[2], "d4_n": seg_n[2],
        "total_pnl": sum(seg_pnl),
        "negative_days": sum(1 for x in seg_pnl if x < 0),
    })

df = pd.DataFrame(rows)
df = df.sort_values("total_pnl", ascending=False)
df.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/09_day_stability.csv", index=False)

print("=== K=1 portfolio per-day PnL ===")
print(df.to_string(index=False))
print(f"\nTotal: D2={df['d2_pnl'].sum():.0f}  D3={df['d3_pnl'].sum():.0f}  D4={df['d4_pnl'].sum():.0f}  Sum={df['total_pnl'].sum():.0f}")
print(f"\nPairs negative on at least 1 day: {(df['negative_days']>=1).sum()}/{len(df)}")
print(f"Pairs negative on at least 2 days: {(df['negative_days']>=2).sum()}/{len(df)}")

# Robustness ranking: pairs that are positive on all 3 days
robust = df[df["negative_days"] == 0].sort_values("total_pnl", ascending=False)
print(f"\n=== Pairs positive on ALL 3 days ({len(robust)}) ===")
print(robust[["a","b","d2_pnl","d3_pnl","d4_pnl","total_pnl"]].to_string(index=False))
