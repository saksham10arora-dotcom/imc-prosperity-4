"""17: Stability-filtered portfolio selection.
Selects from pairs where D2 PnL > 0 AND D3 PnL > 0 separately (each day independently positive).
Then test on D4. This is a stricter selection criterion than total-D2+D3.
Also tests: rank by D3 PnL only (most-recent-day proxy for D5 live).
Output: r5_research/output/17_stability.csv
"""
from __future__ import annotations
import sys
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
            if z >= ZE: pos, ent = -1, spread[i]
            elif z <= -ZE: pos, ent = +1, spread[i]
        elif abs(z) <= ZX:
            g = (spread[i] - ent) * pos * LOT
            pnl += g; n += 1; w += int(g > 0); pos = 0
    return pnl, n, w


print("Computing per-day PnL for all 1225 pairs...")
prods = all_products()
rows = []
for a, b in combinations(prods, 2):
    if a not in mid.columns or b not in mid.columns:
        continue
    sp = (mid[a] - mid[b]).values
    s = pd.Series(sp)
    m = s.rolling(W, min_periods=W).mean().values
    sd = s.rolling(W, min_periods=W).std().values
    p2, n2, w2 = trade(sp[0:DAY], m[0:DAY], sd[0:DAY])
    p3, n3, w3 = trade(sp[DAY:2*DAY], m[DAY:2*DAY], sd[DAY:2*DAY])
    p4, n4, w4 = trade(sp[2*DAY:3*DAY], m[2*DAY:3*DAY], sd[2*DAY:3*DAY])
    rows.append({
        "a": a, "b": b,
        "same_cat": int(category_of(a) == category_of(b)),
        "d2_pnl": p2, "d2_n": n2,
        "d3_pnl": p3, "d3_n": n3,
        "d4_pnl": p4, "d4_n": n4,
        "d23_pnl": p2 + p3, "d23_n": n2 + n3,
    })

df = pd.DataFrame(rows)
df.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/17_per_day_pairs.csv", index=False)


def greedy(ranked, K=1):
    used = {}
    picks = []
    for _, row in ranked.iterrows():
        a, b = row["a"], row["b"]
        if used.get(a, 0) >= K or used.get(b, 0) >= K:
            continue
        picks.append(row.to_dict())
        used[a] = used.get(a, 0) + 1
        used[b] = used.get(b, 0) + 1
    return pd.DataFrame(picks)


# Strategy A: rank by total D2+D3 PnL (baseline, from script 16)
A = greedy(df[df["d23_pnl"] > 0].sort_values("d23_pnl", ascending=False))
# Strategy A2: same but require min trades
A2 = greedy(df[(df["d23_pnl"] > 0) & (df["d23_n"] >= 8)].sort_values("d23_pnl", ascending=False))
# Strategy B: stability — require BOTH D2>0 and D3>0
B = greedy(df[(df["d2_pnl"] > 0) & (df["d3_pnl"] > 0)].sort_values("d23_pnl", ascending=False))
# Strategy C: stability + size — require D2>0, D3>0, AND total>20000
C = greedy(df[(df["d2_pnl"] > 0) & (df["d3_pnl"] > 0) & (df["d23_pnl"] >= 20000)].sort_values("d23_pnl", ascending=False))
# Strategy D: rank by D3 only (most-recent-day proxy)
D = greedy(df[df["d3_pnl"] > 0].sort_values("d3_pnl", ascending=False))
# Strategy E: rank by min(D2, D3) — worst-day floor
df["min_d23"] = df[["d2_pnl", "d3_pnl"]].min(axis=1)
E = greedy(df[df["min_d23"] > 0].sort_values("min_d23", ascending=False))
# Strategy F: D3 only with stability (D2>0 AND D3>0)
F = greedy(df[(df["d2_pnl"] > 0) & (df["d3_pnl"] > 0)].sort_values("d3_pnl", ascending=False))

results = []
for label, port in [("A: total IS PnL", A), ("A2: total IS PnL, n>=8", A2),
                    ("B: D2>0 AND D3>0, rank by total", B),
                    ("C: D2>0, D3>0, total>=20k", C),
                    ("D: rank by D3 only", D),
                    ("E: rank by min(D2,D3)", E),
                    ("F: stability + rank by D3", F)]:
    if len(port) == 0:
        continue
    results.append({
        "strategy": label,
        "n_pairs": len(port),
        "is_pnl_d23": port["d23_pnl"].sum(),
        "oos_pnl_d4": port["d4_pnl"].sum(),
        "n_oos_pos": (port["d4_pnl"] > 0).sum(),
        "n_oos_neg": (port["d4_pnl"] < 0).sum(),
    })
res = pd.DataFrame(results)
print("\n=== Portfolio selection strategies (all evaluated on D4 OOS) ===")
print(res.to_string(index=False))

print("\n=== Strategy E (top by worst-day-floor) — full portfolio ===")
print(E[["a","b","d2_pnl","d3_pnl","d4_pnl"]].to_string(index=False))

print("\n=== Strategy C details ===")
print(C[["a","b","d2_pnl","d3_pnl","d4_pnl"]].to_string(index=False))

# Save the best one
best_name = res.loc[res["oos_pnl_d4"].idxmax(), "strategy"]
print(f"\n*** Best strategy: {best_name} → {res['oos_pnl_d4'].max():.0f} D4 OOS PnL ***")
res.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/17_strategy_compare.csv", index=False)
