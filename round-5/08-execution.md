# 08 — Execution Constraints: The 1k-Tick Discovery & Group vs Pair

## The 1,000-Tick Website Discovery

All our research was done on 10,000-tick-per-day practice data. Parameters were optimized for 10k ticks: windows of 500–2000, warm-up periods of 500+ ticks.

Then we discovered: **the Prosperity website backtester ran 1,000 ticks per day, not 10,000.**

This broke everything:
- A window of w=2000 would never warm up on a 1k-tick day
- Even w=500 needed half the day to produce its first signal
- Parameters that were net-positive on 10k ticks were **net-negative** on 1k ticks

### The Re-Optimization

We ran a full grid search for the 1k-tick environment across window ∈ {50, 75, 100, 150, 200} and z-threshold ∈ {1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0}:

| Module | Optimal window | Optimal z | 1k-tick PnL |
|---|---|---|---|
| PEBBLES (group residual) | 200 | 2.5 | ~51k |
| TRANSLATOR (group residual) | 100 | 2.5 | ~13k |
| MICROCHIP OVAL-TRI (pair) | 75 | 2.0 | ~10k |
| UV_VISOR (group residual) | 100 | 1.75 | ~5k |
| PANEL 1X2-2X4 (pair) | 100 | 1.5 | ~3k |

Modules that needed long windows to be profitable were dropped entirely: ROBOT (always negative on 1k-tick days), SNACKPACK (fragile 4.5k), SLEEP_POD.

**Lesson:** Infrastructure constraints (tick counts, state size limits, execution time) matter as much as alpha. We had the research to ship a more profitable strategy but couldn't fit the parameters.

## Group Residual vs Pair Spread

One of our most important architectural findings was *when* to use each approach:

**Group Residual:** Compute the mean mid-price across all 5 products in a category. Trade each product's deviation from the group mean using rolling z-scores.

**Pair Spread:** Pick two specific products. Trade their price difference using rolling z-scores.

| Category | Group Residual PnL | Best Pair PnL | Winner |
|---|---|---|---|
| PEBBLES | **273,399** | 178,335 | Group (+53%) |
| TRANSLATOR | **113,547** | 42,475 | Group (+167%) |
| SNACKPACK | **68,926** | 39,945 | Group (+73%) |
| MICROCHIP | **101,353** | 63,480 | Group (+60%) |
| SLEEP_POD | −3,388 | **39,920** | Pair |
| ROBOT | −25,709 | **51,010** | Pair |
| PANEL | −25,041 | **35,430** | Pair |

**The rule:** Group residual dominates when the category has strong internal structure (PEBBLES' sum constraint, TRANSLATOR's factor, SNACKPACK's 2-group anti-correlation). All 5 products contribute signal, and the group mean is a better fair-value estimate than any single pair partner.

Pair spread wins when siblings are independent or weakly correlated (SLEEP_POD, ROBOT, PANEL). The group mean is noise — better to pick the two most cointegrated products directly.

## The traderData Limit

The final execution constraint: **state storage.** The Prosperity platform persisted trader state across ticks via a `traderData` JSON string, but with a size limit.

Our full v2 trader (7 modules, 32 products, windows up to 2000) produced **116,681 bytes** of serialized state. This exceeded the platform cap.

We had to strip down to v3: 5 modules with shorter windows (75–200 instead of 500–2000), dropping ROBOT, SNACKPACK, and SLEEP_POD entirely. This cost ~140k PnL from the dropped modules.

Mitigation techniques we used:
- Single-character JSON keys (`"p"` instead of `"pebbles"`)
- Integer-scaled residuals (multiply by 10, store as int instead of float)
- Aggressive history truncation (keep only the most recent `window` ticks)

---

## Final Architecture

The production trader used two base classes:

1. **GroupResidualModule** — Trades each product vs the category mean
2. **PairSpreadModule** — Trades the spread between two specific products

Five modules shipped:

| Module | Type | Products | Window | Z-threshold |
|---|---|---|---|---|
| PEBBLES | Group | 5 products | 200 | 2.5 |
| TRANSLATOR | Group | 5 products | 100 | 2.5 |
| MICROCHIP | Pair | OVAL-TRIANGLE | 75 | 2.0 |
| UV_VISOR | Group | 5 products | 100 | 1.75 |
| PANEL | Pair | 1X2-2X4 | 100 | 1.5 |

**Backtested PnL: 1.67M across 3 days. Zero negative trading periods. Zero limit breaches.**
