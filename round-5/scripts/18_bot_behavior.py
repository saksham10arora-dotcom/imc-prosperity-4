"""18: Bot fingerprinting from R5 trade tape (counterparty names redacted).

We can't read buyer/seller, so we fingerprint by:
  A. Aggressor side identification (compare price to mid at trade tick).
  B. Quantity-mode clusters (bots reuse fixed sizes).
  C. Per-product imbalance (one-sided flow → directional bot).
  D. Tick-frequency bursts (bot bursts look different from random).
  E. Price-vs-mid pricing offset (passive quotes, mid-cross, through-bid).

Output: r5_research/output/18_bot_*.csv  +  console summary.
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__file__.rsplit("/", 1)[0]))
import pandas as pd
import numpy as np
from lib import load_trades, load_prices, pivot_mid, pivot_field, all_products, category_of

print("Loading trades + prices...")
tr = load_trades()
px = load_prices()
mid = pivot_mid(px)
bid1 = pivot_field(px, "bid_price_1")
ask1 = pivot_field(px, "ask_price_1")

# Map (gt, product) -> mid/bid/ask
tr["sym"] = tr["symbol"]
tr_keys = list(zip(tr["gt"].values, tr["sym"].values))

# Build lookup
mid_lu, bid_lu, ask_lu = {}, {}, {}
for prod in mid.columns:
    s_mid = mid[prod].dropna()
    s_bid = bid1[prod].dropna()
    s_ask = ask1[prod].dropna()
    for gt, v in s_mid.items(): mid_lu[(gt, prod)] = v
    for gt, v in s_bid.items(): bid_lu[(gt, prod)] = v
    for gt, v in s_ask.items(): ask_lu[(gt, prod)] = v

tr["mid"] = [mid_lu.get(k) for k in tr_keys]
tr["bid1"] = [bid_lu.get(k) for k in tr_keys]
tr["ask1"] = [ask_lu.get(k) for k in tr_keys]
tr = tr.dropna(subset=["mid"])

# Aggressor classification:
#   trade_price > mid → buyer was aggressor (lifted offer)
#   trade_price < mid → seller was aggressor (hit bid)
#   trade_price == mid → mid-cross (off-book or both passive)
tr["off_mid"] = tr["price"] - tr["mid"]
tr["aggressor"] = np.where(tr["off_mid"] > 0, "BUY",
                    np.where(tr["off_mid"] < 0, "SELL", "MID"))

# How far through the book? Negative = inside spread, positive = aggressive
tr["thru_ask"] = tr["price"] - tr["ask1"]
tr["thru_bid"] = tr["bid1"] - tr["price"]

print(f"\nTotal trades: {len(tr)}  |  buy-aggressor: {(tr['aggressor']=='BUY').sum()}  "
      f"sell-aggressor: {(tr['aggressor']=='SELL').sum()}  mid: {(tr['aggressor']=='MID').sum()}")

# --- A. Per-product aggressor imbalance (directional-bot signal) -----------
agg_prod = tr.groupby(["sym", "aggressor"]).size().unstack(fill_value=0)
for c in ("BUY","SELL","MID"):
    if c not in agg_prod.columns: agg_prod[c] = 0
agg_prod["total"] = agg_prod[["BUY","SELL","MID"]].sum(axis=1)
agg_prod["buy_pct"] = agg_prod["BUY"] / agg_prod["total"]
agg_prod["sell_pct"] = agg_prod["SELL"] / agg_prod["total"]
agg_prod["mid_pct"] = agg_prod["MID"] / agg_prod["total"]
agg_prod["bs_skew"] = agg_prod["buy_pct"] - agg_prod["sell_pct"]
agg_prod = agg_prod.sort_values("bs_skew")

print("\n=== Aggressor skew (BUY% − SELL%): top sell-pressure products ===")
print(agg_prod.head(10)[["BUY","SELL","MID","total","bs_skew"]].to_string())
print("\n=== Top buy-pressure products ===")
print(agg_prod.tail(10)[["BUY","SELL","MID","total","bs_skew"]].to_string())

agg_prod.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/18_aggressor_imbalance.csv")

# --- B. Quantity-mode clusters (bot signatures) ---------------------------
qty_per_sym = (tr.groupby(["sym","quantity"]).size().rename("n")
                  .reset_index().sort_values(["sym","n"], ascending=[True, False]))
# Top-3 sizes per symbol with their share
qty_per_sym["share"] = qty_per_sym.groupby("sym")["n"].transform(lambda x: x / x.sum())
qty_top = qty_per_sym.groupby("sym").head(3)
print("\n=== Quantity-mode dominance (top single size share, sorted high) ===")
top1 = qty_per_sym.groupby("sym").first().sort_values("share", ascending=False)
print(top1.head(15).to_string())
qty_top.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/18_qty_modes.csv", index=False)

# --- C. Mid-cross fraction (passive-quote bots use prearranged price) -----
print("\n=== Mid-cross fraction (passive bots / pre-arranged) — top products ===")
mid_top = agg_prod.sort_values("mid_pct", ascending=False).head(10)
print(mid_top[["BUY","SELL","MID","total","mid_pct"]].to_string())

# --- D. Tick burst pattern: trades-per-tick distribution ------------------
tps = tr.groupby(["sym","gt"]).size().rename("trades_at_tick").reset_index()
burst = tps.groupby("sym")["trades_at_tick"].agg(
    p50="median", p95=lambda x: x.quantile(0.95),
    pmax="max", n_ticks="count")
burst = burst.sort_values("p95", ascending=False)
print("\n=== Tick-burst (max trades within a single tick) ===")
print(burst.head(15).to_string())
burst.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/18_tick_burst.csv")

# --- E. Aggressor segmented by trade size (size-based fingerprint) --------
# For each (product, qty), what's the aggressor mix?
seg = (tr.groupby(["sym","quantity","aggressor"]).size().unstack(fill_value=0))
for c in ("BUY","SELL","MID"):
    if c not in seg.columns: seg[c] = 0
seg["total"] = seg[["BUY","SELL","MID"]].sum(axis=1)
seg = seg[seg["total"] >= 30]
seg["buy_pct"] = seg["BUY"] / seg["total"]
seg["sell_pct"] = seg["SELL"] / seg["total"]
seg["bs_skew"] = seg["buy_pct"] - seg["sell_pct"]
print("\n=== Top 'one-sided fixed-size' bot fingerprints (|skew|>0.6, n>=30) ===")
strong = seg[seg["bs_skew"].abs() > 0.6].sort_values("bs_skew")
print(strong.head(20).to_string())
print("...")
print(strong.tail(20).to_string())
seg.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/18_size_aggressor.csv")

# --- F. Per-day stability of skew (does the bot persist across days?) -----
day_skew = (tr.groupby(["sym","day","aggressor"]).size()
              .unstack(fill_value=0))
for c in ("BUY","SELL","MID"):
    if c not in day_skew.columns: day_skew[c] = 0
day_skew["total"] = day_skew[["BUY","SELL","MID"]].sum(axis=1)
day_skew["bs_skew"] = (day_skew["BUY"] - day_skew["SELL"]) / day_skew["total"]
day_skew_pivot = day_skew["bs_skew"].unstack("day")
day_skew_pivot["min"] = day_skew_pivot.min(axis=1)
day_skew_pivot["max"] = day_skew_pivot.max(axis=1)
day_skew_pivot["range"] = day_skew_pivot["max"] - day_skew_pivot["min"]
day_skew_pivot["mean"] = day_skew_pivot[[2,3,4]].mean(axis=1)
day_skew_pivot = day_skew_pivot.sort_values("mean")
print("\n=== Per-day skew stability — top 10 persistent sell-pressure ===")
print(day_skew_pivot.head(10).to_string())
print("\n=== Top 10 persistent buy-pressure ===")
print(day_skew_pivot.tail(10).to_string())
day_skew_pivot.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/18_day_skew.csv")

# --- G. Price-improvement: how often inside the spread? -------------------
inside = tr[(tr["price"] > tr["bid1"]) & (tr["price"] < tr["ask1"])]
print(f"\n=== Inside-spread trades: {len(inside)} / {len(tr)} = {len(inside)/len(tr)*100:.2f}% ===")
inside_by_sym = inside.groupby("sym").size() / tr.groupby("sym").size()
print(inside_by_sym.sort_values(ascending=False).head(10).to_string())

# --- H. Trade-flow conditioned on next-tick mid move (informed flow?) -----
# For each trade, what does the mid do next-tick?
# Build next-tick mid lookup
next_mid = mid.shift(-1)
nm_lu = {}
for prod in next_mid.columns:
    s = next_mid[prod].dropna()
    for gt, v in s.items(): nm_lu[(gt, prod)] = v
tr["next_mid"] = [nm_lu.get(k) for k in tr_keys]
inf = tr.dropna(subset=["next_mid"]).copy()
inf["dmid"] = inf["next_mid"] - inf["mid"]
# Buy-aggressor + mid_up = informed; sell-aggressor + mid_down = informed
inf["informed"] = ((inf["aggressor"]=="BUY")&(inf["dmid"]>0)) | ((inf["aggressor"]=="SELL")&(inf["dmid"]<0))
inf["uninformed"] = ((inf["aggressor"]=="BUY")&(inf["dmid"]<0)) | ((inf["aggressor"]=="SELL")&(inf["dmid"]>0))
sub = inf[inf["aggressor"].isin(["BUY","SELL"])]
inf_rate = sub.groupby("sym").apply(lambda g: g["informed"].sum() / max(g["informed"].sum() + g["uninformed"].sum(),1))
inf_rate = inf_rate.sort_values()
print("\n=== Informed-flow rate (high = aggressor predicts next-tick mid) ===")
print("--- Top 'uninformed/anti-informed' (mean-reversion fodder) ---")
print(inf_rate.head(10).to_string())
print("--- Top 'informed' (aggressor predicts next move) ---")
print(inf_rate.tail(10).to_string())
inf_rate.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/18_informed_rate.csv",
                header=["informed_rate"])

print("\nDone. Output: r5_research/output/18_*.csv")
