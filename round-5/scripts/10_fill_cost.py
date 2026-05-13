"""10: Replace mid-fills with realistic bid/ask fills.
Long spread: buy A at ask_A, sell B at bid_B. Close: sell A at bid_A, buy B at ask_B.
Crosses 4 spreads per round-trip. Applied to the K=1 robust portfolio.
Output: r5_research/output/10_fill_cost.csv
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__file__.rsplit("/", 1)[0]))
import pandas as pd
import numpy as np
from lib import load_prices, pivot_field, pivot_mid

px = load_prices()
mid = pivot_mid(px)
bid = pivot_field(px, "bid_price_1")
ask = pivot_field(px, "ask_price_1")

DAY = 10000
ZE, ZX, LOT, W = 1.5, 0.3, 10, 2000


def trade_realistic(a_name, b_name, mid_arr, bid_a, ask_a, bid_b, ask_b):
    """Use mid for signal; actual fill at bid/ask."""
    spread = mid_arr  # signal series
    s = pd.Series(spread)
    m = s.rolling(W, min_periods=W).mean().values
    sd = s.rolling(W, min_periods=W).std().values
    pos, ent_cost, n, w, mid_pnl, real_pnl = 0, 0.0, 0, 0, 0.0, 0.0
    ent_mid = 0.0
    for i in range(len(spread)):
        if np.isnan(sd[i]) or sd[i] <= 0 or np.isnan(m[i]):
            continue
        if np.isnan(bid_a[i]) or np.isnan(ask_a[i]) or np.isnan(bid_b[i]) or np.isnan(ask_b[i]):
            continue
        z = (spread[i] - m[i]) / sd[i]
        if pos == 0:
            if z >= ZE:
                # short A long B (short spread). At entry: sell A at bid_A, buy B at ask_B.
                pos = -1
                ent_cost = bid_a[i] * LOT - ask_b[i] * LOT
                ent_mid = spread[i]
            elif z <= -ZE:
                # long A short B
                pos = +1
                ent_cost = ask_a[i] * LOT - bid_b[i] * LOT
                ent_mid = spread[i]
        elif abs(z) <= ZX:
            if pos == +1:
                # close: sell A at bid, buy B at ask
                exit_val = bid_a[i] * LOT - ask_b[i] * LOT
                pnl_real = exit_val - ent_cost
            else:
                # close: buy A at ask, sell B at bid
                exit_val = ask_a[i] * LOT - bid_b[i] * LOT
                pnl_real = ent_cost - exit_val
            mid_g = (spread[i] - ent_mid) * pos * LOT
            real_pnl += pnl_real
            mid_pnl += mid_g
            n += 1
            w += int(pnl_real > 0)
            pos = 0
    return mid_pnl, real_pnl, n, w


port = pd.read_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/08_portfolio_K1.csv")
rows = []
for _, p in port.iterrows():
    a, b = p["a"], p["b"]
    if a not in mid.columns or b not in mid.columns:
        continue
    sp = (mid[a] - mid[b]).values
    mp, rp, n, w = trade_realistic(a, b, sp, bid[a].values, ask[a].values, bid[b].values, ask[b].values)
    rows.append({
        "a": a, "b": b,
        "mid_pnl": mp, "real_pnl": rp, "n": n, "winrate_real": w/n if n>0 else np.nan,
        "haircut_pct": (1 - rp/mp)*100 if mp != 0 else np.nan,
    })

df = pd.DataFrame(rows).sort_values("real_pnl", ascending=False)
df.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/10_fill_cost.csv", index=False)
print("=== K=1 portfolio: mid-fill PnL vs realistic bid/ask-fill PnL ===")
print(df.to_string(index=False))
print(f"\nSum mid PnL: {df['mid_pnl'].sum():.0f}")
print(f"Sum real PnL: {df['real_pnl'].sum():.0f}")
print(f"Avg haircut: {df['haircut_pct'].mean():.1f}%")
print(f"Pairs that go negative after costs: {(df['real_pnl']<0).sum()}/{len(df)}")
