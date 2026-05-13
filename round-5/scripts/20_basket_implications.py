"""20: What the basket-bot discovery means for our trader.

Confirmed in script 19:
  - 40 products fire trades at the SAME 733 ticks ('big basket').
  - PEBBLES-5 fire at their own 644 ticks.
  - MICROCHIP-5 fire at their own 569 ticks.
  - At basket ticks, aggressor is 99% UNANIMOUS across all products.
  - Schedule is randomized per day (Jaccard 0.001 across days).

Questions:
  Q1. How big is the basket-tick mid-move vs non-basket-tick mid-move?
  Q2. Is the bot's aggressor side INFORMED (predicts next-mid) or RANDOM?
  Q3. Within-category, what fraction of cross-spread movement is *common*
      vs *idiosyncratic*? (Common-factor decomposition.)
  Q4. Are our 'pair signals' actually firing AT basket ticks (false signals)
      or between basket ticks (real signals)?
  Q5. What's the per-tick distribution of basket events — clusters vs uniform?
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

# Identify basket-tick sets
big_prods = [p for p in all_products() if category_of(p) not in ("PEBBLES", "MICROCHIP")]
peb_prods = [p for p in all_products() if category_of(p) == "PEBBLES"]
chip_prods = [p for p in all_products() if category_of(p) == "MICROCHIP"]

big_ticks = set(tr[tr["symbol"]==big_prods[0]]["gt"])
peb_ticks = set(tr[tr["symbol"]==peb_prods[0]]["gt"])
chip_ticks = set(tr[tr["symbol"]==chip_prods[0]]["gt"])
all_basket = big_ticks | peb_ticks | chip_ticks
non_basket = set(mid.index) - all_basket

print(f"Big basket ticks: {len(big_ticks)}")
print(f"PEBBLES ticks:    {len(peb_ticks)}")
print(f"MICROCHIP ticks:  {len(chip_ticks)}")
print(f"Any basket tick:  {len(all_basket)}  ({len(all_basket)/len(mid.index)*100:.1f}%)")
print(f"Quiet ticks:      {len(non_basket)}")

# Q1: Mid move magnitude on basket vs non-basket ticks
print("\n=== Q1. Mid move magnitudes ===")
dmid = mid.diff()
mu_basket, mu_quiet = [], []
for prod in big_prods:
    s = dmid[prod].dropna()
    in_b = s.index.isin(big_ticks)
    if in_b.sum() == 0: continue
    mu_basket.append(s[in_b].abs().mean())
    mu_quiet.append(s[~in_b].abs().mean())
print(f"  Big basket: mean |dmid| AT basket-tick: {np.nanmean(mu_basket):.3f}")
print(f"              mean |dmid| ELSEWHERE:      {np.nanmean(mu_quiet):.3f}")
print(f"              ratio (basket/quiet): {np.nanmean(mu_basket)/np.nanmean(mu_quiet):.2f}x")

# Q2: Is basket aggressor informed? Bot aggression vs next-tick mid move
mid_long = mid.stack().rename("mid").reset_index()
mid_long.columns = ["gt","symbol","mid"]
trm = tr.merge(mid_long, on=["gt","symbol"], how="left").dropna(subset=["mid"])
trm["aggr"] = np.where(trm["price"]>trm["mid"], 1, np.where(trm["price"]<trm["mid"], -1, 0))

# next-tick mid move per (gt, symbol)
nm = mid.shift(-1).stack().rename("next_mid").reset_index()
nm.columns = ["gt","symbol","next_mid"]
trm = trm.merge(nm, on=["gt","symbol"], how="left").dropna(subset=["next_mid"])
trm["dmid"] = trm["next_mid"] - trm["mid"]

# per basket-tick aggregate
big_trm = trm[trm["symbol"].isin(big_prods)]
# average aggressor at the tick (basket sign)
basket_side = big_trm.groupby("gt")["aggr"].mean()
basket_side = basket_side[basket_side.index.isin(big_ticks)]
# average next-tick dmid across the 40 products
basket_dmid = big_trm.groupby("gt")["dmid"].mean()

merged = pd.concat([basket_side.rename("side"), basket_dmid.rename("dmid")], axis=1).dropna()
print(f"\n=== Q2. Basket aggressor predicting next-tick mid? ===")
print(f"  n basket-ticks with data: {len(merged)}")
print(f"  Pearson corr(side, dmid): {merged['side'].corr(merged['dmid']):.3f}")
print(f"  When side = +1 (all-buy): mean dmid next tick: {merged[merged['side']>0.5]['dmid'].mean():.3f}")
print(f"  When side = -1 (all-sell): mean dmid next tick: {merged[merged['side']<-0.5]['dmid'].mean():.3f}")
# t-test-ish: split medians
buy_med  = merged[merged['side']>0.5]['dmid']
sell_med = merged[merged['side']<-0.5]['dmid']
print(f"  Sample sizes: BUY={len(buy_med)}, SELL={len(sell_med)}")

# Q3: Common-factor decomposition. At basket ticks, what % of dmid is shared?
print(f"\n=== Q3. Common-factor variance explained at basket ticks ===")
# Take basket ticks only, compute return per product
M = mid.loc[sorted(big_ticks)][big_prods].diff().dropna()  # T × 40
# subtract per-product mean (innovation around drift)
Mc = M - M.mean()
# PCA: first PC captures common factor
U, S, Vt = np.linalg.svd(Mc.values, full_matrices=False)
total_var = (S**2).sum()
print(f"  PC1 variance fraction: {S[0]**2/total_var*100:.1f}%")
print(f"  PC1+PC2:               {(S[0]**2+S[1]**2)/total_var*100:.1f}%")
print(f"  PC1+...+PC5:           {sum(S[:5]**2)/total_var*100:.1f}%")
print(f"  → If PC1 is huge, basket-tick moves are nearly all common-factor noise.")

# Same for non-basket ticks
quiet = sorted(non_basket - {min(non_basket)})  # drop a single tick to avoid issues
Mq = mid.loc[[t for t in mid.index if t not in all_basket]][big_prods].diff().dropna()
if len(Mq) > 50:
    Mqc = Mq - Mq.mean()
    Uq, Sq, _ = np.linalg.svd(Mqc.values, full_matrices=False)
    total_q = (Sq**2).sum()
    print(f"  At QUIET ticks, PC1 variance fraction: {Sq[0]**2/total_q*100:.1f}%")

# Q4: Where do z-score signals fire — at basket ticks or quiet ticks?
print(f"\n=== Q4. Where do our z-thresholds trigger? ===")
W = 100  # current trader window
ZE = 1.5
# Pick a representative pair: TRANSLATOR pair from group
prod = "TRANSLATOR_SPACE_GRAY"
grp = [p for p in CATEGORIES.get("TRANSLATOR", [])]
grp_full = [f"TRANSLATOR_{m}" for m in grp]
grp_mid = mid[grp_full].mean(axis=1)
spread = mid[prod] - grp_mid
m = spread.rolling(W, min_periods=W).mean()
s = spread.rolling(W, min_periods=W).std()
z = (spread - m) / s
sig = (z.abs() >= ZE)
in_basket = sig.index.isin(all_basket)
total = sig.sum()
in_b = (sig & pd.Series(in_basket, index=sig.index)).sum()
print(f"  Product: {prod}  vs TRANSLATOR group, w={W}, |z|>={ZE}")
print(f"  Total signal-ticks:           {int(total)}")
print(f"  Of those, AT a basket tick:   {int(in_b)}  ({int(in_b)/max(int(total),1)*100:.1f}%)")
print(f"  Quiet-tick signals:           {int(total-in_b)}  ({(int(total)-int(in_b))/max(int(total),1)*100:.1f}%)")

# Q5: Time-of-day distribution
print(f"\n=== Q5. Basket-tick clustering within day ===")
big_in_day = pd.Series(sorted(big_ticks)) % 10000
# Histogram by quintile of day
q = pd.qcut(big_in_day, 5, labels=False)
print(f"  Big basket ticks per day-quintile:")
print(q.value_counts().sort_index().to_string())

# Inter-arrival
ia = np.diff(sorted(big_ticks))
print(f"\n  Big-basket inter-arrival ticks: median={np.median(ia):.1f}, mean={np.mean(ia):.1f}, "
      f"p95={np.quantile(ia,0.95):.0f}, max={ia.max()}")

# Q6: How clean is non-unanimity (the 1%)? When does the basket bot disagree?
print(f"\n=== Q6. The 1% of basket ticks where aggressor isn't unanimous ===")
agg_per_tick = big_trm.groupby("gt")["aggr"].agg(["mean","count","sum"])
disagree = agg_per_tick[(agg_per_tick["count"]==40) &
                        (agg_per_tick["sum"].abs() < agg_per_tick["count"])]
disagree = disagree[disagree["sum"].abs() < 36]  # < 90% one-sided
print(f"  Disagreement ticks: {len(disagree)}")
if len(disagree) > 0:
    print(f"  Sample sums (positive=more buys): {disagree['sum'].head(20).values}")
    # Which products tend to dissent?
    dissent_ticks = disagree.index.tolist()
    sub = big_trm[big_trm["gt"].isin(dissent_ticks)]
    by_prod = sub.groupby("symbol")["aggr"].agg(["mean","count"])
    print(f"\n  Per-product mean aggressor on dissent ticks (extreme on either side dissent more):")
    print(by_prod.sort_values("mean").head(5).to_string())
    print(by_prod.sort_values("mean").tail(5).to_string())

print("\nDone.")
