"""01: Validate hard structural constraints across all 30k ticks per category.

Tests the PEBBLES sum=50,000 claim and looks for similar identities in every category:
- Sum of all 5 mids being constant
- Sum of all 5 mids being a linear function of (constant + factor)
- 4-vs-1 identity (one product = sum/diff of others)

Output: r5_research/output/01_constraints.csv
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
print(f"Loaded mid: {mid.shape}")

rows = []
for cat, members in CATEGORIES.items():
    cols = [f"{cat}_{m}" for m in members]
    sub = mid[cols].dropna()
    s = sub.sum(axis=1)
    rows.append({
        "category": cat,
        "test": "sum_all_5",
        "mean": s.mean(),
        "std": s.std(),
        "min": s.min(),
        "max": s.max(),
        "range": s.max() - s.min(),
        "n_ticks": len(s),
        "constant_within_3sigma": s.std() < 5.0,
    })
    # First differences of sum
    ds = s.diff().dropna()
    rows.append({
        "category": cat,
        "test": "delta_sum_all_5",
        "mean": ds.mean(),
        "std": ds.std(),
        "min": ds.min(),
        "max": ds.max(),
        "range": ds.max() - ds.min(),
        "n_ticks": len(ds),
        "constant_within_3sigma": ds.std() < 0.5,
    })

# Per-day test of sum
for cat, members in CATEGORIES.items():
    cols = [f"{cat}_{m}" for m in members]
    sub = mid[cols].dropna()
    s = sub.sum(axis=1)
    for day_idx, label in enumerate(["d2", "d3", "d4"]):
        sl = s.iloc[day_idx*10000:(day_idx+1)*10000]
        rows.append({
            "category": cat,
            "test": f"sum_{label}",
            "mean": sl.mean(),
            "std": sl.std(),
            "min": sl.min(),
            "max": sl.max(),
            "range": sl.max() - sl.min(),
            "n_ticks": len(sl),
            "constant_within_3sigma": sl.std() < 5.0,
        })

out = pd.DataFrame(rows)
out_path = "/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/01_constraints.csv"
out.to_csv(out_path, index=False)
print(out[out["test"].str.startswith("sum_all")].to_string(index=False))
print(f"\nWrote {out_path}")

# Subsidiary: any 4-of-5 linear combo with very low residual std?
print("\n=== Best 4-of-5 OLS reconstructions (lowest residual std) per category ===")
res_rows = []
for cat, members in CATEGORIES.items():
    cols = [f"{cat}_{m}" for m in members]
    sub = mid[cols].dropna().values
    n_obs = len(sub)
    for i, m_target in enumerate(members):
        y = sub[:, i]
        X_idx = [j for j in range(5) if j != i]
        X = sub[:, X_idx]
        X1 = np.column_stack([X, np.ones(len(X))])
        beta, *_ = np.linalg.lstsq(X1, y, rcond=None)
        resid = y - X1 @ beta
        res_rows.append({
            "category": cat,
            "target": m_target,
            "regressors": ",".join(members[j] for j in X_idx),
            "coefs": ",".join(f"{b:.4f}" for b in beta[:-1]),
            "intercept": float(beta[-1]),
            "resid_std": float(resid.std()),
            "resid_max_abs": float(np.abs(resid).max()),
            "r2": 1 - float(resid.var() / y.var()),
        })
res_df = pd.DataFrame(res_rows).sort_values("resid_std")
res_df.to_csv("/Users/sakshamarora/Desktop/untitled folder/imcdom/r5_research/output/01_4of5_ols.csv", index=False)
print(res_df.groupby("category")["resid_std"].min().sort_values().to_string())
print("\nTop 10 lowest-resid reconstructions:")
print(res_df.head(10).to_string(index=False))
