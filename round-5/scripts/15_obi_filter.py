"""15: OBI as entry filter on the K=1 portfolio.
Hypothesis: When entering long-spread (z<-1.5, i.e. bullish on a-b), require:
- OBI_a > 0 (bid pressure on A)
- OR OBI_b < 0 (ask pressure on B)
i.e. the imbalance shouldn't say next-tick goes against us.

Test 4 modes:
- M0: baseline, no filter
- M1: require OBI_a × sign(spread - mean) < 0 on entry (mean-reversion-friendly)
- M2: require OBI_a × pos > 0 (pressure with our position direction)
- M3: same as M2 + OBI_b × pos < 0

Output: r5_research/output/15_obi_filter.csv
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__file__.rsplit("/", 1)[0]))
import pandas as pd
import numpy as np
from lib import load_prices, pivot_mid, pivot_field

px = load_prices()
mid = pivot_mid(px)
bid = pivot_field(px, "bid_price_1")
ask = pivot_field(px, "ask_price_1")
bv = pivot_field(px, "bid_volume_1")
av = pivot_field(px, "ask_volume_1")

DAY = 10000
ZE, ZX, LOT, W = 1.5, 0.3, 10, 2000


def obi(b, a):
    return np.where((b + a) > 0, (b - a) / (b + a), 0.0)


def trade_filter(spread, m, s, obi_a, obi_b, mode):
    pos, ent, pnl, n, w = 0, 0.0, 0.0, 0, 0
    for i in range(len(spread)):
        if np.isnan(s[i]) or s[i] <= 0 or np.isnan(m[i]):
            continue
        z = (spread[i] - m[i]) / s[i]
        if pos == 0:
            if z >= ZE:
                # Want pos = -1 (short A long B). Want OBI_a < 0 (sellers on A) and OBI_b > 0 (buyers on B)
                if mode == 0:
                    pos, ent = -1, spread[i]
                elif mode == 1:
                    if obi_a[i] < 0 or obi_b[i] > 0:
                        pos, ent = -1, spread[i]
                elif mode == 2:
                    if obi_a[i] < 0:
                        pos, ent = -1, spread[i]
                elif mode == 3:
                    if obi_a[i] < 0 and obi_b[i] > 0:
                        pos, ent = -1, spread[i]
            elif z <= -ZE:
                # Want pos = +1 (long A short B). Want OBI_a > 0, OBI_b < 0
                if mode == 0:
                    pos, ent = +1, spread[i]
                elif mode == 1:
                    if obi_a[i] > 0 or obi_b[i] < 0:
                        pos, ent = +1, spread[i]
                elif mode == 2:
                    if obi_a[i] > 0:
                        pos, ent = +1, spread[i]
                elif mode == 3:
                    if obi_a[i] > 0 and obi_b[i] < 0:
                        pos, ent = +1, spread[i]
        elif abs(z) <= ZX:
            g = (spread[i] - ent) * pos * LOT
            pnl += g; n += 1; w += int(g > 0); pos = 0
    return pnl, n, w


port = pd.read_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/08_portfolio_K1.csv")
modes = [0, 1, 2, 3]
mode_names = {0: "baseline", 1: "either", 2: "OBI_a only", 3: "both AND"}

# Aggregate per mode
agg = {m: {"pnl": 0.0, "n": 0, "w": 0, "d4_pnl": 0.0, "d4_n": 0, "d4_w": 0} for m in modes}
per_pair = []
for _, p in port.iterrows():
    a, b = p["a"], p["b"]
    sp = (mid[a] - mid[b]).values
    s = pd.Series(sp)
    m = s.rolling(W, min_periods=W).mean().values
    sd = s.rolling(W, min_periods=W).std().values
    oa = obi(bv[a].values, av[a].values)
    ob = obi(bv[b].values, av[b].values)
    rec = {"a": a, "b": b}
    for mode in modes:
        # Full 3-day
        pnl, n, w_ = trade_filter(sp, m, sd, oa, ob, mode)
        # D4 OOS
        d4 = trade_filter(sp[2*DAY:3*DAY], m[2*DAY:3*DAY], sd[2*DAY:3*DAY],
                          oa[2*DAY:3*DAY], ob[2*DAY:3*DAY], mode)
        agg[mode]["pnl"] += pnl; agg[mode]["n"] += n; agg[mode]["w"] += w_
        agg[mode]["d4_pnl"] += d4[0]; agg[mode]["d4_n"] += d4[1]; agg[mode]["d4_w"] += d4[2]
        rec[f"m{mode}_3d_pnl"] = pnl
        rec[f"m{mode}_d4_pnl"] = d4[0]
        rec[f"m{mode}_d4_n"] = d4[1]
    per_pair.append(rec)

per_df = pd.DataFrame(per_pair)
per_df.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/15_obi_filter.csv", index=False)

print("=== K=1 portfolio aggregate, OBI filter modes ===")
for mode in modes:
    a = agg[mode]
    wr = a["w"] / max(a["n"], 1)
    wr4 = a["d4_w"] / max(a["d4_n"], 1)
    print(f"  M{mode} ({mode_names[mode]:12}): full_3d_pnl={a['pnl']:>9.0f} n={a['n']:>4} winrate={wr:.3f}  |  "
          f"d4_pnl={a['d4_pnl']:>9.0f} n={a['d4_n']:>4} winrate={wr4:.3f}")
