"""04: Cross-category pair sweep — does any *cross-category* pair beat the within-cat winners?
50 products → 1225 unordered pairs total. We compute the rolling-z PnL on the full 3 days for each
and rank. We also store correlation, spread half-life, and absolute drift.
Output: r5_research/output/04_cross_category.csv
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
prods = all_products()

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


def halflife(x):
    """OU half-life via AR(1) on first-differences."""
    s = pd.Series(x).dropna().values
    if len(s) < 100:
        return np.nan
    y = np.diff(s)
    xv = s[:-1] - s[:-1].mean()
    if np.dot(xv, xv) == 0:
        return np.nan
    phi = np.dot(xv, y) / np.dot(xv, xv)
    if phi >= 0 or phi <= -2:
        return np.nan
    return -np.log(2) / np.log(1 + phi)


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
    pnl, n, win = trade(sp, m, sd)
    rows.append({
        "a": a, "b": b,
        "cat_a": category_of(a), "cat_b": category_of(b),
        "same_cat": int(category_of(a) == category_of(b)),
        "spread_mean": float(sp.mean()),
        "spread_std": float(sp.std()),
        "drift_d2_d4": float(sp[-1] - sp[0]),
        "corr": float(mid[a].corr(mid[b])),
        "halflife": halflife(sp),
        "pnl": pnl, "n_trades": n, "n_wins": win,
    })
    done += 1
    if done % 200 == 0:
        elapsed = time.time() - t0
        print(f"  {done}/{total} pairs ({elapsed:.0f}s)")

df = pd.DataFrame(rows)
df["winrate"] = df["n_wins"] / df["n_trades"].replace(0, np.nan)
df.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/04_cross_category.csv", index=False)
print(f"\n{len(df)} pairs scored in {time.time()-t0:.0f}s")

print("\n=== TOP 25 cross-category pairs (full 3-day rolling-z) ===")
print(df[df["same_cat"] == 0].sort_values("pnl", ascending=False).head(25)[
    ["a", "b", "pnl", "n_trades", "winrate", "corr", "spread_std", "halflife", "drift_d2_d4"]
].to_string(index=False))

print("\n=== Top 10 within-cat (sanity vs prior sweep) ===")
print(df[df["same_cat"] == 1].sort_values("pnl", ascending=False).head(10)[
    ["a", "b", "pnl", "n_trades", "winrate", "corr"]
].to_string(index=False))

print("\n=== Highest |corr| cross-cat pairs (top 15) ===")
print(df[df["same_cat"] == 0].assign(absc=df["corr"].abs()).sort_values("absc", ascending=False).head(15)[
    ["a", "b", "corr", "pnl", "spread_std"]
].to_string(index=False))
