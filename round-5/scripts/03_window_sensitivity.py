"""03: Rolling-z window sensitivity for the top sweep pairs.
Tests w in {200, 500, 1000, 2000, 3000, 5000, 8000} on day-4 OOS (train d2+d3, trade d4).
Also runs a "no-look-ahead" min_periods=w version vs an expanding fallback.
Output: r5_research/output/03_window_sensitivity.csv
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

DAY = 10000
ZE, ZX, LOT = 1.5, 0.3, 10
WINDOWS = [200, 500, 1000, 2000, 3000, 5000, 8000]


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


# Top 30 pairs by full-3-day rolling z (per the prior sweep)
top_pairs = [
    ("MICROCHIP", "OVAL", "TRIANGLE"),
    ("PEBBLES", "M", "XL"),
    ("PEBBLES", "S", "L"),
    ("TRANSLATOR", "ECLIPSE_CHARCOAL", "VOID_BLUE"),
    ("ROBOT", "VACUUMING", "LAUNDRY"),
    ("ROBOT", "DISHES", "IRONING"),
    ("PEBBLES", "XS", "XL"),
    ("MICROCHIP", "CIRCLE", "RECTANGLE"),
    ("SNACKPACK", "STRAWBERRY", "RASPBERRY"),
    ("SLEEP_POD", "POLYESTER", "COTTON"),
    ("SNACKPACK", "PISTACHIO", "RASPBERRY"),
    ("PEBBLES", "XS", "S"),
    ("PANEL", "1X2", "2X4"),
    ("TRANSLATOR", "ASTRO_BLACK", "GRAPHITE_MIST"),
    ("MICROCHIP", "SQUARE", "TRIANGLE"),
]

rows = []
for cat, a, b in top_pairs:
    ca, cb = f"{cat}_{a}", f"{cat}_{b}"
    sp = (mid[ca] - mid[cb]).values
    sp_d4 = sp[2*DAY:3*DAY]
    for w in WINDOWS:
        s = pd.Series(sp)
        m = s.rolling(w, min_periods=w).mean().values[2*DAY:3*DAY]
        sd = s.rolling(w, min_periods=w).std().values[2*DAY:3*DAY]
        pnl, n, win = trade(sp_d4, m, sd)
        # Full 3-day in-sample
        m_full = s.rolling(w, min_periods=w).mean().values
        sd_full = s.rolling(w, min_periods=w).std().values
        pnl_full, n_full, win_full = trade(sp, m_full, sd_full)
        rows.append({
            "pair": f"{cat}:{a}-{b}",
            "window": w,
            "d4_oos_pnl": pnl, "d4_oos_n": n, "d4_oos_w": win,
            "full_3d_pnl": pnl_full, "full_3d_n": n_full, "full_3d_w": win_full,
        })

df = pd.DataFrame(rows)
df.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/03_window_sensitivity.csv", index=False)

print("=== Day-4 OOS PnL by window ===")
print(df.pivot(index="pair", columns="window", values="d4_oos_pnl").to_string())
print("\n=== Full-3day in-sample PnL by window ===")
print(df.pivot(index="pair", columns="window", values="full_3d_pnl").to_string())
print("\n=== Win rate (d4 OOS) by window ===")
df["d4_winrate"] = df["d4_oos_w"] / df["d4_oos_n"].replace(0, np.nan)
print(df.pivot(index="pair", columns="window", values="d4_winrate").to_string(float_format=lambda x: f"{x:.2f}"))
