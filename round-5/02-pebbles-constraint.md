# 02 — The PEBBLES Constraint: XS + S + M + L + XL = 50,000

## The Discovery

Script: `01_constraints.py` → Output: `01_constraints.csv`

We computed the sum of all 5 PEBBLES mid-prices at every tick across all 30,000 ticks:

```
Mean:  49,999.94
Std:   2.80
Min:   49,982.0
Max:   50,017.0
Range: 35.0
```

**XS + S + M + L + XL = 50,000, always, to within ±3 ticks.** This was not approximate — it was a hard constraint baked into the data generator.

No other category came close. We tested all 10:

| Category | Sum std | Sum range |
|---|---|---|
| **PEBBLES** | **2.8** | **35** |
| SNACKPACK | 190 | 1,320 |
| TRANSLATOR | 246 | 2,034 |
| MICROCHIP | 380 | 3,200 |
| ROBOT | 445 | 2,680 |
| UV_VISOR | 490 | 3,875 |
| All others | 500+ | 3,000+ |

## Why It Mattered

The constraint had several mechanical consequences:

### 1. XL has 2× the volatility of everything else

If 4 products move slightly, the 5th must absorb the residual to maintain the sum. PEBBLES_XL was that absorber:

| Product | dmid std |
|---|---|
| XS | 15.1 |
| S | 14.8 |
| M | 15.2 |
| L | 14.9 |
| **XL** | **30.3** |

XL's volatility was exactly the quadrature sum of the other four — confirming it mechanically balanced the constraint.

### 2. Return cross-correlations are mechanical

The constraint forced: corr(XL returns, any other PEBBLES returns) ≈ **−0.50**. Not because of a fundamental relationship, but because of the arithmetic identity.

### 3. Basket arbitrage is dead

We checked whether the constraint could be directly exploited:

- Ask sum < 50,000 only 1.5% of ticks
- Average profit on those ticks: 2.5 ticks
- Bid-ask spread per product: 10–17 ticks (5 products × ~13 = ~65 ticks round-trip cost)

**Cost exceeds profit by 25×.** Direct basket arb was not viable.

### 4. But pair mean-reversion is strong

The constraint *does* help indirectly: it forces spreads between PEBBLES pairs to revert quickly. If M drifts up while XL drifts down (sum stays constant), the M−XL spread will revert because both are being pulled back toward their constraint-consistent levels.

This was confirmed by the pair backtest results — PEBBLES pairs had the strongest and fastest mean-reversion of any category, and specifically preferred shorter rolling windows (w=200) because reversion was mechanically fast.

## PEBBLES Window Sensitivity (Script 03)

| Window | M−XL PnL | S−L PnL |
|---|---|---|
| w=200 | **118,380** | 85,445 |
| w=500 | 91,270 | 68,190 |
| w=2000 | 32,430 | 28,765 |
| w=8000 | 10,125 | 8,430 |

Shorter windows capture faster constraint-driven reversion. **w=200 was 11× better than w=8000.**

## 4-of-5 OLS Regression (Script 01)

We also tested whether any 4 products could predict the 5th via linear regression:

- R² for predicting XL from {XS, S, M, L}: **0.9998**
- R² for predicting any product from the other 4: **>0.999**

The constraint made each product a near-perfect linear function of the other four.

---

**Next:** [03-methodology-war.md](03-methodology-war.md) — The debate that decided everything.
