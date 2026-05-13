"""12: Cointegration coefficient (β) walk-forward stability + true OOS via Engle-Granger.
For each pair (a, b) in the K=1 portfolio:
- Fit β on day 2: (a - β*b) minimizes residual variance
- Test residual stationarity (ADF-like via half-life) on days 3 + 4
- Trade rolling-z on the residual instead of (a - b) raw
Compare PnL: raw spread vs cointegrated spread.
Output: r5_research/output/12_cointegration.csv
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


def halflife(x):
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


def fit_beta(a, b):
    """OLS: a = β*b + α. Returns (β, α)."""
    a = np.asarray(a); b = np.asarray(b)
    bv = b - b.mean()
    av = a - a.mean()
    if np.dot(bv, bv) == 0:
        return 1.0, 0.0
    beta = np.dot(av, bv) / np.dot(bv, bv)
    alpha = a.mean() - beta * b.mean()
    return beta, alpha


port = pd.read_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/08_portfolio_K1.csv")
rows = []
for _, p in port.iterrows():
    a, b = p["a"], p["b"]
    if a not in mid.columns or b not in mid.columns:
        continue
    A = mid[a].values
    B = mid[b].values
    # Fit on day 2
    beta_d2, alpha_d2 = fit_beta(A[:DAY], B[:DAY])
    # Fit on days 2+3
    beta_d23, alpha_d23 = fit_beta(A[:2*DAY], B[:2*DAY])
    # Coef stability ratio
    beta_d3, alpha_d3 = fit_beta(A[DAY:2*DAY], B[DAY:2*DAY])
    beta_d4, alpha_d4 = fit_beta(A[2*DAY:3*DAY], B[2*DAY:3*DAY])

    # Residual = A - β*B, then trade rolling-z
    resid_d2_fit = A - beta_d2 * B - alpha_d2
    resid_d23_fit = A - beta_d23 * B - alpha_d23
    raw = A - B  # the original "raw spread"

    # PnL on day 4 OOS using each beta
    def trade_oos(spread_full):
        s = pd.Series(spread_full)
        m = s.rolling(W, min_periods=W).mean().values
        sd = s.rolling(W, min_periods=W).std().values
        return trade(spread_full[2*DAY:3*DAY], m[2*DAY:3*DAY], sd[2*DAY:3*DAY])

    pnl_raw, n_raw, w_raw = trade_oos(raw)
    pnl_d2, n_d2, w_d2 = trade_oos(resid_d2_fit)
    pnl_d23, n_d23, w_d23 = trade_oos(resid_d23_fit)

    rows.append({
        "a": a, "b": b,
        "beta_d2": beta_d2, "beta_d3": beta_d3, "beta_d4": beta_d4, "beta_d23": beta_d23,
        "beta_drift_d2_d4": beta_d4 - beta_d2,
        "halflife_resid_d23_on_d4": halflife(A[2*DAY:3*DAY] - beta_d23 * B[2*DAY:3*DAY] - alpha_d23),
        "halflife_raw_on_d4": halflife(A[2*DAY:3*DAY] - B[2*DAY:3*DAY]),
        "raw_d4_pnl": pnl_raw,
        "coint_d2_fit_d4_pnl": pnl_d2,
        "coint_d23_fit_d4_pnl": pnl_d23,
        "raw_n": n_raw, "coint_d23_n": n_d23,
        "improvement_vs_raw": pnl_d23 - pnl_raw,
    })

df = pd.DataFrame(rows)
df.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/12_cointegration.csv", index=False)

print("=== Cointegration walk-forward β stability ===")
print(df[["a","b","beta_d2","beta_d3","beta_d4","beta_drift_d2_d4"]].to_string(index=False))

print(f"\n=== β drift D2→D4 distribution ===")
print(df["beta_drift_d2_d4"].describe())

print("\n=== D4 OOS: raw spread vs cointegrated spread (β fit on D2+D3) ===")
print(df[["a","b","raw_d4_pnl","coint_d23_fit_d4_pnl","improvement_vs_raw"]]
      .sort_values("improvement_vs_raw", ascending=False).to_string(index=False))

print(f"\nSum raw_d4: {df['raw_d4_pnl'].sum():.0f}")
print(f"Sum coint_d23_fit_d4: {df['coint_d23_fit_d4_pnl'].sum():.0f}")
print(f"Improvement: {df['improvement_vs_raw'].sum():.0f} ({(df['improvement_vs_raw'] > 0).sum()}/{len(df)} pairs improve)")

print("\n=== Half-life of residual on D4 (β fit on D2+D3) vs raw spread ===")
print(df[["a","b","halflife_resid_d23_on_d4","halflife_raw_on_d4"]].to_string(index=False))
