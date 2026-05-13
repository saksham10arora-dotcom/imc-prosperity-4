"""16: Proper out-of-sample portfolio construction.
Procedure:
1. For each of 1225 pairs, compute PnL on days 2+3 only (rolling-z, w=2000, but trade only after warm-up).
2. Greedy select K=1 portfolio (no shared legs) from highest D2+D3 PnL.
3. Apply that portfolio (frozen) to day 4. Report d4 PnL.

This is the "if we had only seen days 2+3, what's our day-4 PnL?" question.
Output: r5_research/output/16_proper_oos_portfolio.csv
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


prods = all_products()
print(f"Computing {len(prods)*(len(prods)-1)//2} pair PnL on D2+D3 (in-sample) and D4 (OOS)...")
rows = []
for a, b in combinations(prods, 2):
    if a not in mid.columns or b not in mid.columns:
        continue
    sp = (mid[a] - mid[b]).values
    s = pd.Series(sp)
    m = s.rolling(W, min_periods=W).mean().values
    sd = s.rolling(W, min_periods=W).std().values
    # In-sample: D2+D3
    p_is, n_is, w_is = trade(sp[:2*DAY], m[:2*DAY], sd[:2*DAY])
    # OOS: D4
    p_oos, n_oos, w_oos = trade(sp[2*DAY:3*DAY], m[2*DAY:3*DAY], sd[2*DAY:3*DAY])
    rows.append({
        "a": a, "b": b,
        "same_cat": int(category_of(a) == category_of(b)),
        "is_d23_pnl": p_is, "is_d23_n": n_is, "is_d23_w": w_is,
        "oos_d4_pnl": p_oos, "oos_d4_n": n_oos, "oos_d4_w": w_oos,
    })

df = pd.DataFrame(rows)
df.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/16_proper_oos_pairs.csv", index=False)


def greedy_K1(ranked, K=1):
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


# Strategy A: Pick top by IS D2+D3, freeze, evaluate on D4
positive_is = df[df["is_d23_pnl"] > 0].sort_values("is_d23_pnl", ascending=False)
port_A = greedy_K1(positive_is, K=1)
port_A.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/16_portfolio_A.csv", index=False)

# Strategy B: For comparison, pick top by D4 OOS directly (cheating — uses D4 to select)
positive_oos = df[df["oos_d4_pnl"] > 0].sort_values("oos_d4_pnl", ascending=False)
port_B = greedy_K1(positive_oos, K=1)

# Strategy C: Pick top by joint (IS_pos AND IS-rank-stable approach)
# Truncate to top-200 by IS, then sort by IS again
top200_is = positive_is.head(200)
port_C = greedy_K1(top200_is, K=1)

print(f"\n=== Portfolio A: select on IS (D2+D3), freeze, test on D4 OOS ===")
print(f"  pairs: {len(port_A)}")
print(f"  IS PnL (D2+D3): {port_A['is_d23_pnl'].sum():.0f}")
print(f"  OOS PnL (D4):   {port_A['oos_d4_pnl'].sum():.0f}")
print(f"  OOS pos pairs:  {(port_A['oos_d4_pnl']>0).sum()}/{len(port_A)}")

print(f"\n=== Portfolio B: select on D4 directly (CHEATING upper bound) ===")
print(f"  pairs: {len(port_B)}")
print(f"  D4 PnL: {port_B['oos_d4_pnl'].sum():.0f}")

print(f"\n=== Portfolio A details ===")
print(port_A[["a","b","same_cat","is_d23_pnl","oos_d4_pnl"]].to_string(index=False))

print(f"\n=== How many of port_A pairs would have been in port_B (overlap)? ===")
A_pairs = set(zip(port_A["a"], port_A["b"]))
B_pairs = set(zip(port_B["a"], port_B["b"]))
print(f"  port_A: {len(A_pairs)} pairs, port_B: {len(B_pairs)} pairs, overlap: {len(A_pairs & B_pairs)}")
print(f"  port_A captures {port_A['oos_d4_pnl'].sum() / port_B['oos_d4_pnl'].sum() * 100:.1f}% of the optimum D4 PnL")

# Per-pair win/loss accounting on D4
print(f"\n=== Port A: pairs with IS > 0 but OOS < 0 (would-be losers) ===")
losers = port_A[port_A["oos_d4_pnl"] < 0].sort_values("oos_d4_pnl")
print(losers[["a","b","is_d23_pnl","oos_d4_pnl"]].to_string(index=False))
print(f"\nLoser sum: {losers['oos_d4_pnl'].sum():.0f}")
