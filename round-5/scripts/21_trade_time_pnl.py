"""21: Relationship between trade-tick times and combined PnL.

For each pair in the K=1 portfolio, replay the trade rule (rolling-z w=2000 z=1.5/0.3
on full 30k ticks) and tag every entry and exit:
  - basket-tick? (any of BIG/PEBBLES/MICROCHIP fires at that tick for either leg)
  - leg-A trade-tick? leg-B trade-tick? (for the relevant basket of A and of B)
  - quiet (no trade event in either leg's basket)

Per round-trip we record:
  entry_at_basket, exit_at_basket, gain
Then aggregate:
  - PnL by entry-bucket × exit-bucket
  - Win-rate by bucket
  - PnL by inter-arrival to the nearest basket event (does proximity matter?)

Output: r5_research/output/21_*.csv
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__file__.rsplit("/", 1)[0]))
import pandas as pd
import numpy as np
from lib import load_trades, load_prices, pivot_mid, all_products, category_of, CATEGORIES

print("Loading...")
tr = load_trades()
px = load_prices()
mid = pivot_mid(px)

# Build per-product trade-tick set
ticks_per_prod = tr.groupby("symbol")["gt"].apply(set).to_dict()

# Basket tick sets
BIG = {p for p in all_products() if category_of(p) not in ("PEBBLES","MICROCHIP")}
PEB = {p for p in all_products() if category_of(p) == "PEBBLES"}
CHIP = {p for p in all_products() if category_of(p) == "MICROCHIP"}

big_ticks = ticks_per_prod[next(iter(BIG))]
peb_ticks = ticks_per_prod[next(iter(PEB))]
chip_ticks = ticks_per_prod[next(iter(CHIP))]

def basket_of(prod):
    if prod in PEB: return peb_ticks
    if prod in CHIP: return chip_ticks
    return big_ticks

# Load K=1 portfolio
port = pd.read_csv("r5_research/output/08_portfolio_K1.csv")
print(f"Pairs in K=1 portfolio: {len(port)}")

W, ZE, ZX, LOT = 2000, 1.5, 0.3, 10

def replay_with_tags(a, b):
    sp = (mid[a] - mid[b]).values
    s_pd = pd.Series(sp)
    m = s_pd.rolling(W, min_periods=W).mean().values
    sd = s_pd.rolling(W, min_periods=W).std().values
    ix = mid.index.values  # global ticks

    bt_a, bt_b = basket_of(a), basket_of(b)

    pos, ent, ent_t = 0, 0.0, None
    out = []
    for i in range(len(sp)):
        if np.isnan(sd[i]) or sd[i] <= 0 or np.isnan(m[i]):
            continue
        z = (sp[i] - m[i]) / sd[i]
        gt = ix[i]
        if pos == 0:
            if z >= ZE:
                pos, ent, ent_t = -1, sp[i], gt
            elif z <= -ZE:
                pos, ent, ent_t = +1, sp[i], gt
        elif abs(z) <= ZX:
            g = (sp[i] - ent) * pos * LOT
            ent_basket = (ent_t in bt_a) or (ent_t in bt_b)
            exit_basket = (gt in bt_a) or (gt in bt_b)
            out.append({
                "a": a, "b": b,
                "ent_t": int(ent_t), "exit_t": int(gt),
                "hold_ticks": int(gt - ent_t),
                "ent_basket": int(ent_basket),
                "exit_basket": int(exit_basket),
                "gain": float(g),
            })
            pos = 0
    return out

print("Replaying portfolio with basket-tick tags...")
all_rt = []
for _, p in port.iterrows():
    rts = replay_with_tags(p["a"], p["b"])
    all_rt.extend(rts)
df = pd.DataFrame(all_rt)
df.to_csv("r5_research/output/21_roundtrips_tagged.csv", index=False)
print(f"Total round-trips: {len(df)}")

print(f"\n=== Round-trip count by entry × exit bucket (basket=1, quiet=0) ===")
ct = df.groupby(["ent_basket","exit_basket"]).size().unstack(fill_value=0)
print(ct)

print(f"\n=== Total PnL by entry × exit bucket ===")
pnl = df.groupby(["ent_basket","exit_basket"])["gain"].agg(["sum","mean","count"])
pnl["winrate"] = df.groupby(["ent_basket","exit_basket"])["gain"].apply(lambda x: (x>0).mean())
print(pnl.round(1))

print(f"\n=== Marginal: by ENTRY bucket only ===")
e = df.groupby("ent_basket")["gain"].agg(["sum","mean","count"])
e["winrate"] = df.groupby("ent_basket")["gain"].apply(lambda x: (x>0).mean())
print(e.round(2))
share_basket_entries = (df["ent_basket"]==1).sum() / len(df)
print(f"  Entry-on-basket-tick share: {share_basket_entries*100:.1f}%")
print(f"  Expected if random (6.4%): basket entries should be ~6.4%; actual {share_basket_entries*100:.1f}%")

print(f"\n=== Marginal: by EXIT bucket only ===")
ex = df.groupby("exit_basket")["gain"].agg(["sum","mean","count"])
ex["winrate"] = df.groupby("exit_basket")["gain"].apply(lambda x: (x>0).mean())
print(ex.round(2))

# --- Distance from entry to NEAREST basket tick (any leg) ---
all_basket = big_ticks | peb_ticks | chip_ticks
sorted_b = np.array(sorted(all_basket))
def nearest_dist(t):
    i = np.searchsorted(sorted_b, t)
    cands = []
    if i > 0: cands.append(t - sorted_b[i-1])
    if i < len(sorted_b): cands.append(sorted_b[i] - t)
    return min(cands) if cands else np.nan

df["ent_dist_to_basket"] = df["ent_t"].apply(nearest_dist)
df["exit_dist_to_basket"] = df["exit_t"].apply(nearest_dist)

print(f"\n=== PnL by entry-distance-to-basket bucket ===")
df["ent_dist_b"] = pd.cut(df["ent_dist_to_basket"], bins=[-1,0,5,15,40,1e9],
                          labels=["AT(0)","1-5","6-15","16-40","41+"])
print(df.groupby("ent_dist_b", observed=True)["gain"].agg(["sum","mean","count"]).round(2))

# --- Hold-time distribution ---
print(f"\n=== Round-trip hold-tick distribution ===")
print(df["hold_ticks"].describe(percentiles=[.25,.5,.75,.9,.95]).round(1).to_string())

# --- PnL by hold-time bucket ---
print(f"\n=== PnL by hold-time bucket ===")
df["hold_b"] = pd.cut(df["hold_ticks"], bins=[-1,10,30,100,500,1e9],
                      labels=["≤10","11-30","31-100","101-500","500+"])
print(df.groupby("hold_b", observed=True)["gain"].agg(["sum","mean","count"]).round(2))

# --- Did the round-trip span a basket-tick? ---
def spans_basket(row):
    lo, hi = int(row["ent_t"]), int(row["exit_t"])
    sub = sorted_b[(sorted_b >= lo) & (sorted_b <= hi)]
    return len(sub)
df["n_basket_in_trip"] = df.apply(spans_basket, axis=1)
print(f"\n=== PnL by # basket-events spanned by round-trip ===")
df["span_b"] = pd.cut(df["n_basket_in_trip"], bins=[-1,0,1,3,10,1e9],
                      labels=["0","1","2-3","4-10","11+"])
print(df.groupby("span_b", observed=True)["gain"].agg(["sum","mean","count"]).round(2))

# --- Per-pair: entry-on-basket share and total PnL ---
per_pair = df.groupby(["a","b"]).agg(
    n=("gain","count"),
    pnl=("gain","sum"),
    ent_basket_share=("ent_basket","mean"),
    exit_basket_share=("exit_basket","mean"),
    mean_n_basket_spanned=("n_basket_in_trip","mean"),
)
per_pair = per_pair.sort_values("pnl", ascending=False)
per_pair.to_csv("r5_research/output/21_per_pair_basket_share.csv")
print(f"\n=== Per-pair basket-entry share (top 10 by PnL) ===")
print(per_pair.head(10).round(3))

# Correlation between basket-entry share and pair PnL
import scipy.stats as ss
if len(per_pair) >= 5:
    c, p = ss.spearmanr(per_pair["ent_basket_share"], per_pair["pnl"])
    print(f"\n  Spearman corr(entry-on-basket share, pair PnL): r={c:.3f} p={p:.3f}")
    c2, p2 = ss.spearmanr(per_pair["mean_n_basket_spanned"], per_pair["pnl"])
    print(f"  Spearman corr(# basket events spanned, pair PnL): r={c2:.3f} p={p2:.3f}")

print("\nDone.")
