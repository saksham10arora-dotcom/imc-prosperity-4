"""05: ROBOT_IRONING ac1_dmid forensics.
Q: Is ac1_dmid = -0.125 a real reversion signal, or bid-ask bounce in mid?
- Compute ac1 of: mid, dmid, dmid_per_day, micro-price (bid_p1*ask_v + ask_p1*bid_v)/(bid_v+ask_v),
  and trade prices.
- Run for ALL products (not just IRONING) so we can spot any others with reversion.
Output: r5_research/output/05_microstructure.csv
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__file__.rsplit("/", 1)[0]))
import pandas as pd
import numpy as np
from lib import load_prices, all_products

px = load_prices()
DAY = 10000


def ac1(x):
    x = pd.Series(x).dropna().values
    if len(x) < 10:
        return np.nan
    return float(pd.Series(x).autocorr(lag=1))


rows = []
for prod in all_products():
    sub = px[px["product"] == prod].sort_values("gt").reset_index(drop=True)
    if len(sub) < 100:
        continue
    mid = sub["mid_price"].values
    dmid = np.diff(mid)
    bid = sub["bid_price_1"].values
    ask = sub["ask_price_1"].values
    bv = sub["bid_volume_1"].values
    av = sub["ask_volume_1"].values
    micro = np.where((bv + av) > 0, (bid * av + ask * bv) / (bv + av), np.nan)
    # spread
    spread = ask - bid

    rec = {
        "product": prod,
        "ac1_mid": ac1(mid),
        "ac1_dmid": ac1(dmid),
        "ac1_micro": ac1(micro),
        "ac1_dmicro": ac1(np.diff(pd.Series(micro).dropna().values)),
        "spread_mean": float(np.nanmean(spread)),
        "spread_std": float(np.nanstd(spread)),
        # Per day
        "ac1_dmid_d2": ac1(np.diff(mid[:DAY])),
        "ac1_dmid_d3": ac1(np.diff(mid[DAY:2*DAY])),
        "ac1_dmid_d4": ac1(np.diff(mid[2*DAY:3*DAY])),
        # Higher-order: ac2, ac5
        "ac2_dmid": float(pd.Series(dmid).autocorr(lag=2)),
        "ac5_dmid": float(pd.Series(dmid).autocorr(lag=5)),
    }
    rows.append(rec)

df = pd.DataFrame(rows).sort_values("ac1_dmid")
df.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/05_microstructure.csv", index=False)

print("=== Top 10 most-negative ac1_dmid (potential MR products) ===")
print(df.head(10)[["product", "ac1_dmid", "ac1_dmicro", "ac1_dmid_d2", "ac1_dmid_d3", "ac1_dmid_d4", "spread_mean"]].to_string(index=False))
print("\n=== Distribution of ac1_dmid across the 50 products ===")
print(df["ac1_dmid"].describe().to_string())
print("\n=== Top 10 most-positive ac1_dmid (potential trend products) ===")
print(df.tail(10)[["product", "ac1_dmid", "ac1_dmicro", "ac1_dmid_d2", "ac1_dmid_d3", "ac1_dmid_d4"]].to_string(index=False))

# === Trade-print autocorr for IRONING vs comparison products ===
print("\n=== Trade-price ac1 (bid-ask-bounce diagnostic) ===")
from lib import load_trades
tr = load_trades()
for p in ["ROBOT_IRONING", "ROBOT_DISHES", "PEBBLES_XL", "MICROCHIP_OVAL", "SLEEP_POD_POLYESTER"]:
    sub = tr[tr["symbol"] == p].sort_values(["day", "timestamp"])
    if len(sub) < 50:
        print(f"  {p}: too few trades ({len(sub)})")
        continue
    p_ser = sub["price"].values
    print(f"  {p}: ac1(trade_price)={ac1(p_ser):.3f}  ac1(diff)={ac1(np.diff(p_ser)):.3f}  n={len(sub)}")
