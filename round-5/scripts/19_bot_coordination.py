"""19: Bot tick-coordination — are trades fired in basket bursts?
Findings from 18:
  - 28 products share the EXACT same trade count (358 BUY / 375 SELL = 733).
  - 5 MICROCHIP products share 300/269 = 569.
  - 5 PEBBLES products share 321/323 = 644.

Hypothesis: a single "global tick event" triggers a trade on every product in a
shared basket, with possibly-correlated sides.

Tests:
  A. Per-tick: how many distinct products trade simultaneously?
  B. Are the SAME ticks used across the "733 club"? (Jaccard of trade-tick sets)
  C. At a 'basket tick', do products move with the same aggressor side?
  D. Across-day persistence of the basket schedule.
  E. Side-correlation matrix on basket ticks (which products move together?)

Output: r5_research/output/19_*.csv
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__file__.rsplit("/", 1)[0]))
import pandas as pd
import numpy as np
from itertools import combinations
from lib import load_trades, load_prices, pivot_mid, pivot_field, all_products

print("Loading...")
tr = load_trades()
px = load_prices()
mid = pivot_mid(px)

# Trade ticks per product
ticks_per = tr.groupby("symbol")["gt"].agg(set)
counts = tr.groupby("symbol").size().sort_values(ascending=False)

print("\n=== Per-product trade counts (all 50) ===")
print(counts.to_string())

# Group by exact count → should reveal shared 'baskets'
groups = counts.groupby(counts).apply(lambda s: list(s.index))
print("\n=== Products grouped by identical trade counts ===")
for cnt, members in sorted(groups.items(), reverse=True):
    print(f"  count={cnt}  n={len(members)}: {members[:6]}{'...' if len(members)>6 else ''}")

# A. Tick-coincidence among the 733-club
big = [s for s, c in counts.items() if c == counts.max()]
print(f"\n=== Top group ({len(big)} products, count={counts.max()}) ===")

# Are the trade-ticks IDENTICAL?
ts0 = ticks_per[big[0]]
all_identical = all(ticks_per[s] == ts0 for s in big)
print(f"  All trade-tick sets identical: {all_identical}")
if not all_identical:
    # Pairwise Jaccard
    sample = big[:5]
    print(f"  Pairwise Jaccard (first 5):")
    for a, b in combinations(sample, 2):
        ja = len(ticks_per[a] & ticks_per[b]) / len(ticks_per[a] | ticks_per[b])
        print(f"    {a:30} ↔ {b:30}: J={ja:.3f}")

# B. Multi-product per tick
prods_per_tick = tr.groupby("gt")["symbol"].nunique().sort_values(ascending=False)
print(f"\n=== Distinct products per tick (whole tape) ===")
print(f"  ticks total: {len(prods_per_tick)}")
print(f"  median: {prods_per_tick.median()}")
print(f"  mean: {prods_per_tick.mean():.1f}")
print(f"  max: {prods_per_tick.max()}  (top 5: {prods_per_tick.head(5).values.tolist()})")
print(f"  histogram of n_prods_per_tick:")
print(prods_per_tick.value_counts().sort_index().to_string())

# C. Side-coordination on the basket: when many products fire at same tick,
#    are aggressor sides correlated?
mid_long = mid.stack().rename("mid").reset_index()
mid_long.columns = ["gt","symbol","mid"]
tr2 = tr.merge(mid_long, on=["gt","symbol"], how="left").dropna(subset=["mid"])
tr2["aggr"] = np.where(tr2["price"]>tr2["mid"], 1,
              np.where(tr2["price"]<tr2["mid"], -1, 0))

# At each tick, take side per product. If a tick has many products, is sum(aggr) ≠ 0?
side_per_tick = tr2.groupby("gt")["aggr"].agg(["sum","count"])
side_per_tick = side_per_tick[side_per_tick["count"] >= 5]
print(f"\n=== Tick-level aggressor sum (only ticks with ≥5 products) ===")
print(f"  total: {len(side_per_tick)}")
print(f"  mean abs sum: {side_per_tick['sum'].abs().mean():.2f}")
print(f"  fraction unanimous (all-buy or all-sell):")
def unan(row):
    return abs(row["sum"]) == row["count"]
print(f"    {side_per_tick.apply(unan, axis=1).mean()*100:.1f}%")
print(f"  fraction at least 80% one-sided:")
print(f"    {(side_per_tick['sum'].abs() / side_per_tick['count'] >= 0.8).mean()*100:.1f}%")

# D. Cross-day: does the basket schedule reset per day, or carry across days?
# Each day has 10000 ticks; basket events at e.g. tick 100, 200, ... ?
tr2["tick_in_day"] = tr2["gt"] % 10000
sched_per_day = tr2.groupby("day")["tick_in_day"].agg(set)
inter = sched_per_day[2] & sched_per_day[3] & sched_per_day[4]
union = sched_per_day[2] | sched_per_day[3] | sched_per_day[4]
print(f"\n=== Basket schedule: ticks-of-day ===")
print(f"  Day 2: {len(sched_per_day[2])}  Day 3: {len(sched_per_day[3])}  Day 4: {len(sched_per_day[4])}")
print(f"  intersection: {len(inter)}  union: {len(union)}")
print(f"  schedule overlap (Jaccard): {len(inter)/len(union):.3f}")

# E. Per-product aggressor correlation on shared ticks
shared_ticks = sorted(ticks_per[big[0]] & ticks_per[big[1]])
print(f"\n=== Sample side-correlation matrix ({len(big)} products, {len(shared_ticks)} shared ticks) ===")
side_pivot = (tr2[tr2["symbol"].isin(big)]
                 .pivot_table(index="gt", columns="symbol", values="aggr", aggfunc="last"))
side_pivot = side_pivot.dropna()
print(f"  pivot shape (ticks × products): {side_pivot.shape}")
corr = side_pivot.corr()
# Show a 10×10 slice
sample = big[:10]
print(corr.loc[sample, sample].round(2).to_string())
corr.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/19_side_correlation.csv")

# Block correlations — average corr within vs across categories
from lib import category_of
cat_of = {p: category_of(p) for p in side_pivot.columns}
inb, outb = [], []
for a, b in combinations(side_pivot.columns, 2):
    if a == b: continue
    c = corr.loc[a, b]
    if pd.isna(c): continue
    if cat_of[a] == cat_of[b]: inb.append(c)
    else: outb.append(c)
print(f"\n  Mean within-category aggressor corr: {np.mean(inb):.3f} (n={len(inb)})")
print(f"  Mean across-category aggressor corr: {np.mean(outb):.3f} (n={len(outb)})")

# F. Look at tiny groups: products with FEWER trades — which are 'individuals'?
small_groups = [c for c in counts.unique() if (counts == c).sum() <= 2]
print(f"\n=== Products with unique/rare trade counts (likely independent flow) ===")
unique = counts[counts.isin(small_groups)]
print(unique.to_string())

print("\nDone.")
