"""02: Adjudicate prev-day-mean vs rolling-z anchoring on out-of-sample data.

Procedure for each within-category pair:
- Train on day 2, trade days 3+4
- Train on days 2+3, trade day 4 (true OOS)
- Compare prev-day-mean (anchor=last full day's spread mean/std) vs rolling-z (window=2000)

Output: r5_research/output/02_methodology.csv
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__file__.rsplit("/", 1)[0]))
import pandas as pd
import numpy as np
from itertools import combinations
from lib import load_prices, pivot_mid, CATEGORIES

px = load_prices()
mid = pivot_mid(px)

DAY_TICKS = 10000
ZE = 1.5  # entry
ZX = 0.3  # exit
LOT = 10


def trade_pair(spread: np.ndarray, mean: np.ndarray, std: np.ndarray) -> tuple[float, int, int]:
    """Trade a spread series given pre-computed (mean, std) per tick.
    Returns (realized_pnl, n_trades, win_count). 10-lot.
    """
    pos = 0  # +1 = long spread (long A short B), -1 = short
    entry_spread = 0.0
    pnl = 0.0
    trades = 0
    wins = 0
    for i in range(len(spread)):
        if std[i] <= 0 or np.isnan(std[i]) or np.isnan(mean[i]):
            continue
        z = (spread[i] - mean[i]) / std[i]
        if pos == 0:
            if z >= ZE:
                pos = -1
                entry_spread = spread[i]
            elif z <= -ZE:
                pos = +1
                entry_spread = spread[i]
        else:
            if abs(z) <= ZX:
                gain = (spread[i] - entry_spread) * pos * LOT
                pnl += gain
                trades += 1
                if gain > 0:
                    wins += 1
                pos = 0
    # Close at last
    if pos != 0:
        gain = (spread[-1] - entry_spread) * pos * LOT
        pnl += gain
        trades += 1
        if gain > 0:
            wins += 1
    return pnl, trades, wins


def rolling_mean_std(x: np.ndarray, w: int) -> tuple[np.ndarray, np.ndarray]:
    s = pd.Series(x)
    m = s.rolling(w, min_periods=w).mean().values
    sd = s.rolling(w, min_periods=w).std().values
    return m, sd


rows = []
for cat, members in CATEGORIES.items():
    for a, b in combinations(members, 2):
        ca, cb = f"{cat}_{a}", f"{cat}_{b}"
        if ca not in mid.columns or cb not in mid.columns:
            continue
        spread = (mid[ca] - mid[cb]).values  # length 30000
        d2 = spread[0:DAY_TICKS]
        d3 = spread[DAY_TICKS:2*DAY_TICKS]
        d4 = spread[2*DAY_TICKS:3*DAY_TICKS]

        # ---- TRUE OOS test: train days 2+3, trade day 4 ----
        # Method A: prev-day mean = mean of d3 (the immediately prior day)
        a_mean = np.full_like(d4, d3.mean(), dtype=float)
        a_std = np.full_like(d4, d3.std(), dtype=float)
        pnl_A_d4, n_A_d4, w_A_d4 = trade_pair(d4, a_mean, a_std)

        # Method B: rolling z window=2000 with day-3 history seeding
        full_to_d4 = np.concatenate([d2, d3, d4])
        m_full, s_full = rolling_mean_std(full_to_d4, 2000)
        m_d4 = m_full[2*DAY_TICKS:3*DAY_TICKS]
        s_d4 = s_full[2*DAY_TICKS:3*DAY_TICKS]
        pnl_B_d4, n_B_d4, w_B_d4 = trade_pair(d4, m_d4, s_d4)

        # ---- OOS test 2: train day 2, trade days 3+4 ----
        a_mean_full = np.full(2*DAY_TICKS, d2.mean(), dtype=float)
        a_std_full = np.full(2*DAY_TICKS, d2.std(), dtype=float)
        pnl_A_d34, n_A_d34, w_A_d34 = trade_pair(np.concatenate([d3, d4]), a_mean_full, a_std_full)

        m_d34 = m_full[DAY_TICKS:3*DAY_TICKS]
        s_d34 = s_full[DAY_TICKS:3*DAY_TICKS]
        pnl_B_d34, n_B_d34, w_B_d34 = trade_pair(np.concatenate([d3, d4]), m_d34, s_d34)

        rows.append({
            "category": cat,
            "pair": f"{a}-{b}",
            "spread_mean": spread.mean(),
            "spread_std": spread.std(),
            "d2_mean": d2.mean(),
            "d3_mean": d3.mean(),
            "d4_mean": d4.mean(),
            "drift_d2_d4": d4.mean() - d2.mean(),
            # day 4 OOS
            "A_d4_pnl": pnl_A_d4, "A_d4_n": n_A_d4, "A_d4_w": w_A_d4,
            "B_d4_pnl": pnl_B_d4, "B_d4_n": n_B_d4, "B_d4_w": w_B_d4,
            # days 3+4 OOS (looser train)
            "A_d34_pnl": pnl_A_d34, "A_d34_n": n_A_d34, "A_d34_w": w_A_d34,
            "B_d34_pnl": pnl_B_d34, "B_d34_n": n_B_d34, "B_d34_w": w_B_d34,
        })

out = pd.DataFrame(rows)
out_path = "/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/02_methodology.csv"
out.to_csv(out_path, index=False)

print(f"\n=== Aggregate OOS (TRAIN d2+d3, TRADE d4) ===")
print(f"Method A (prev-day mean of d3): total {out['A_d4_pnl'].sum():.0f}, "
      f"#pairs PnL>0: {(out['A_d4_pnl']>0).sum()}/{len(out)}, "
      f"avg trades: {out['A_d4_n'].mean():.1f}")
print(f"Method B (rolling z w=2000):    total {out['B_d4_pnl'].sum():.0f}, "
      f"#pairs PnL>0: {(out['B_d4_pnl']>0).sum()}/{len(out)}, "
      f"avg trades: {out['B_d4_n'].mean():.1f}")

print(f"\n=== Aggregate OOS (TRAIN d2, TRADE d3+d4) ===")
print(f"Method A: total {out['A_d34_pnl'].sum():.0f}, #pairs>0: {(out['A_d34_pnl']>0).sum()}/{len(out)}")
print(f"Method B: total {out['B_d34_pnl'].sum():.0f}, #pairs>0: {(out['B_d34_pnl']>0).sum()}/{len(out)}")

print("\n=== Per-pair winner: top 15 absolute |A−B| differences (d4 OOS) ===")
out["abs_diff_d4"] = (out["A_d4_pnl"] - out["B_d4_pnl"]).abs()
print(out.sort_values("abs_diff_d4", ascending=False).head(15)[
    ["category", "pair", "A_d4_pnl", "B_d4_pnl", "drift_d2_d4"]
].to_string(index=False))

print("\n=== Top 15 pairs by Method-B day-4 OOS PnL ===")
print(out.sort_values("B_d4_pnl", ascending=False).head(15)[
    ["category", "pair", "A_d4_pnl", "B_d4_pnl", "B_d4_n", "B_d4_w", "drift_d2_d4"]
].to_string(index=False))

print("\n=== Top 15 pairs by Method-A day-4 OOS PnL ===")
print(out.sort_values("A_d4_pnl", ascending=False).head(15)[
    ["category", "pair", "A_d4_pnl", "B_d4_pnl", "A_d4_n", "A_d4_w", "drift_d2_d4"]
].to_string(index=False))

print(f"\nWrote {out_path}")
