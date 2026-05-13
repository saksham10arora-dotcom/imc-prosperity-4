# 07 — Negative Results: What Didn't Work

Every research program produces dead ends. These are ours — documented because understanding *why* something fails is often as valuable as understanding why something works.

## 1. β-Cointegration (Engle-Granger)

Script: `12_cointegration_walkforward.py`

**Idea:** Instead of trading the raw 1:1 spread (A − B), fit a regression coefficient β on training data and trade the residual (A − β·B). Classic pairs trading.

**Result:** Catastrophically worse.

| Method | D4 OOS PnL | Pairs that improved |
|---|---|---|
| Raw (1:1) spread | 559,705 | (baseline) |
| β-fitted residual | 167,276 | **2 / 23** |

**21 of 23 pairs got worse** with β-fitting. The fitted coefficients drifted heavily across days (median |Δβ| = 0.85 from D2 to D4; max 2.21). The β-residual half-life expanded 2–10× vs the raw spread.

**Why it failed:** R5 pairs are not classic Engle-Granger cointegrated. They're closer to "two parallel random walks with equal scale." The 1:1 spread works because the products move at similar magnitudes. Fitting β tries to find a hedge ratio that doesn't exist — and destabilizes the spread in the process.

**Lesson:** Don't reflexively apply textbook techniques. Test them against the naive baseline.

## 2. Order-Book Imbalance (OBI) as Entry Filter

Script: `15_obi_filter.py`

**Idea:** Only enter pair trades when the order-book imbalance on one or both legs confirms the direction. OBI correlated with next-tick dmid at +0.13 for SNACKPACK products — maybe it could improve trade selection.

**Result:** Net negative.

| Mode | D4 OOS PnL | Trades | Win Rate |
|---|---|---|---|
| No filter (baseline) | **559,705** | 381 | 0.906 |
| Require OBI_a confirms | 422,935 | 254 | 0.917 |
| Require both OBI confirm | 109,735 | 51 | 0.941 |

Win rate improved by 1–4pp. But trade count dropped far more than proportionally. **The rolling-z signal at 90% accuracy doesn't need a tiebreaker** — adding one just throws away good trades.

## 3. Time-of-Day Patterns

Script: `14_time_of_day.py`

**Idea:** Look for open/close effects or intraday seasonality in trade activity and PnL.

**Result:** Nothing exploitable. Trade counts were roughly uniform across 20 time buckets (1,280–2,145 per bucket). Win rates ranged 0.78–1.00 with no consistent pattern. The best bucket (ticks 2000–2499) was just the rolling-z window warm-up zone — not a true intraday signal.

## 4. Aggressor-Side Following

Script: `18_bot_behavior.py`

**Idea:** When the basket bot buys, maybe we should buy too (momentum following).

**Result:** Dead on arrival. Pearson(side, next-tick mid) = 0.015. The basket bot's direction is random and uninformed. Following it is equivalent to flipping a coin.

## 5. PANEL Area-Arithmetic Baskets

**Idea:** PANEL products are area-coded (1X2=2, 2X2=4, 1X4=4, 2X4=8, 4X4=16). Maybe 4X4 ≈ 4·1X4, or 2X4 ≈ 2·1X4?

**Result:** Completely wrong. Prices are per-product, not per-area:

| Product | Area | Mid Price | Price per sq unit |
|---|---|---|---|
| PANEL_1X2 | 2 | 8,923 | 4,461 |
| PANEL_2X2 | 4 | 9,151 | 2,288 |
| PANEL_1X4 | 4 | 9,236 | 2,309 |
| PANEL_2X4 | 8 | 9,587 | 1,198 |
| PANEL_4X4 | 16 | 9,879 | 617 |

Price-per-area collapses 7× from 1X2 to 4X4. All cointegration p-values for arithmetic baskets were >0.3. The pricing model has nothing to do with area — the "size coding" was a red herring.

## 6. Trades Held > 500 Ticks

Script: `21_trade_time_pnl.py`

**Idea:** Let positions run longer for bigger moves.

**Result:** Opposite. Round-trip trades held more than 500 ticks were **consistent net losers**. The mean-reversion signal has a finite horizon — beyond ~500 ticks, the spread has either reverted (profit taken) or drifted further (loss-making). Holding longer only adds to the losing tail.

**Implication:** A hard time-stop at 500 ticks would improve strategy health by cutting the losing tail.

## 7. 3-Leg Baskets (Promising but Impractical)

Script: `13_three_leg.py`

**Idea:** For each pair (A, B), find a third leg C that improves the spread.

**Result:** Dramatically better on paper:

| Method | D4 OOS PnL |
|---|---|
| 2-leg pairs | 559,705 |
| Best 3-leg baskets | **975,320** |

But each 3-leg basket uses 30 contract slots (vs 20 for 2-leg). Per-contract PnL improved only modestly. With position-limit-10 per product, we couldn't run all 23 triplets — and the extra complexity wasn't worth the marginal improvement.

---

**Next:** [08-execution.md](08-execution.md) — The 1k-tick discovery and final architecture.
