"""08: Portfolio construction.
Given the 471 pairs that are positive in-sample AND OOS, pos-limit=10/product, build
a maximum-PnL portfolio that:
- Doesn't double-count any product's pos-limit
- Greedy by OOS PnL: pick the highest PnL pair, remove its legs from availability,
  repeat.
- Also reports a "soft" version where each leg can carry K pairs (K=2, 3) by sharing.
Output: r5_research/output/08_portfolio.csv + summary
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__file__.rsplit("/", 1)[0]))
import pandas as pd
import numpy as np

oos = pd.read_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/06_cross_category_oos.csv")
oos = oos.sort_values("oos_d4_pnl", ascending=False).reset_index(drop=True)

# Filter to robust pairs
robust = oos[(oos["in_sample_pnl"] > 0) & (oos["oos_d4_pnl"] > 0)].copy()

def greedy(robust, K=1):
    used = {}  # product -> count
    picks = []
    for _, row in robust.iterrows():
        a, b = row["a"], row["b"]
        if used.get(a, 0) >= K or used.get(b, 0) >= K:
            continue
        picks.append(row.to_dict())
        used[a] = used.get(a, 0) + 1
        used[b] = used.get(b, 0) + 1
    return pd.DataFrame(picks)


print("=== K=1 (each product in at most one pair) ===")
p1 = greedy(robust, K=1)
print(f"  pairs: {len(p1)}, sum OOS PnL: {p1['oos_d4_pnl'].sum():.0f}, sum in-sample: {p1['in_sample_pnl'].sum():.0f}")
print(p1.head(20)[["a","b","in_sample_pnl","oos_d4_pnl","oos_winrate"]].to_string(index=False))
p1.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/08_portfolio_K1.csv", index=False)

print("\n=== K=2 (each product in up to 2 pairs — pos limit halved per pair to 5) ===")
p2 = greedy(robust, K=2)
print(f"  pairs: {len(p2)}, sum OOS PnL (gross @ 10-lot): {p2['oos_d4_pnl'].sum():.0f}, halved: {p2['oos_d4_pnl'].sum()/2:.0f}")
p2.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/08_portfolio_K2.csv", index=False)

print("\n=== Best 50% of OOS PnL after halving for K=2 ===")
print(p2.head(20)[["a","b","oos_d4_pnl","oos_winrate"]].to_string(index=False))

# Greedy on within-category only
print("\n=== K=1 within-cat only ===")
p1w = greedy(robust[robust["same_cat"]==1], K=1)
print(f"  pairs: {len(p1w)}, sum OOS PnL: {p1w['oos_d4_pnl'].sum():.0f}")
print(p1w[["a","b","in_sample_pnl","oos_d4_pnl"]].to_string(index=False))

# What if we restrict to only the top 10 OOS pairs (no portfolio constraint, just see total)
top10 = oos.head(10)
print(f"\n=== Top 10 OOS pairs (ignoring pos-limit conflict) sum: {top10['oos_d4_pnl'].sum():.0f} ===")
print(top10[["a","b","oos_d4_pnl"]].to_string(index=False))

# Conflict count: which products appear in many top-OOS pairs?
print("\n=== Products with most appearances in top 50 OOS pairs ===")
top50 = oos.head(50)
prod_counts = pd.concat([top50["a"], top50["b"]]).value_counts().head(15)
print(prod_counts.to_string())
