# 08 — Execution Constraints: The 1k-Tick Discovery & Group vs Pair

## The 1,000-Tick Website Discovery

All our research was done on 10,000-tick-per-day practice data. Parameters were optimized for 10k ticks: windows of 500–2000, warm-up periods of 500+ ticks.

Then we discovered: **the Prosperity website backtester ran 1,000 ticks per day, not 10,000.**

This broke everything:
- A window of w=2000 would never warm up on a 1k-tick day
- Even w=500 needed half the day to produce its first signal
- Parameters that were net-positive on 10k ticks were **net-negative** on 1k ticks

### The Re-Optimization

We ran a full grid search for the 1k-tick environment across window ∈ {50, 75, 100, 150, 200} and z-threshold ∈ {1.0, 1.5, 2.0, 2.5, 3.0}:

| Module | Optimal window | Optimal z | 1k-tick PnL |
|---|---|---|---|
| PEBBLES (group residual) | 200 | 2.5 | 51,055 |
| TRANSLATOR (group residual) | 100 | 2.5 | 13,445 |
| MICROCHIP OVAL-TRI (pair) | 75 | 2.0 | 10,488 |

Modules that needed long windows to be profitable were dropped or demoted: ROBOT (always negative on 1k-tick days at all tested settings), SNACKPACK (negative across the grid).

**Lesson:** Infrastructure constraints (tick counts, state size limits, execution time) matter as much as alpha. We had the research to ship a more profitable strategy but couldn't fit the parameters.

## Group Residual vs Pair Spread

One of our most important architectural findings was *when* to use each approach:

**Group Residual:** Compute the mean mid-price across all 5 products in a category. Trade each product's deviation from the group mean using rolling z-scores.

**Pair Spread:** Pick two specific products. Trade their price difference using rolling z-scores.

| Category | Group Residual PnL | Best Pair PnL | Winner |
|---|---|---|---|
| PEBBLES | **273,399** | 178,335 | Group (+53%) |
| TRANSLATOR | **113,547** | 42,475 | Group (+167%) |
| MICROCHIP | **101,353** | 63,480 | Group (+60%) |
| SNACKPACK | **68,926** | 39,945 | Group (+73%) |
| UV_VISOR | −18,458 | **21,720** | Pair |
| SLEEP_POD | −3,388 | **39,920** | Pair |
| ROBOT | −25,709 | **51,010** | Pair |
| PANEL | −25,041 | **35,430** | Pair |
| OXYGEN_SHAKE | −6,073 | **15,565** | Pair |
| GALAXY_SOUNDS | −19,337 | **15,535** | Pair |

**The rule:** Group residual dominates when the category has strong internal structure (PEBBLES' sum constraint, TRANSLATOR's factor, SNACKPACK's 2-group anti-correlation, MICROCHIP's shape-pair relationships). All 5 products contribute signal, and the group mean is a better fair-value estimate than any single pair partner.

Pair spread wins when siblings are independent or weakly correlated (SLEEP_POD, ROBOT, PANEL, UV_VISOR, OXYGEN_SHAKE, GALAXY_SOUNDS). The group mean is noise — better to pick the two most cointegrated products directly.

## The traderData Limit

The final execution constraint: **state storage.** The Prosperity platform persisted trader state across ticks via a `traderData` JSON string, but with a size limit.

Our full v2 trader (7 modules, 32 products, windows up to 2000) produced **116,681 bytes** of serialized state. This exceeded the platform cap.

We had to strip down to v3 with shorter windows and fewer modules. Mitigation techniques:
- Single-character JSON keys (`"p"` instead of `"pebbles"`)
- Integer-scaled residuals (multiply by 10, store as int instead of float)
- Aggressive history truncation (keep only the most recent `window` ticks)

---

## Final Architecture: `finalfinal.py`

The production trader (`finalfinal.py`, 1,940 lines) was far more ambitious than the conservative "Tier 1 only" plan. It deployed **10 strategy modules covering all 10 categories** — every product in the R5 field was either traded directionally or market-made.

### Three Strategy Types

1. **GroupResidualModule** — Trades each of 5 products vs the category mean (PEBBLES only)
2. **PairSpreadModule** — Trades the spread between specific product pairs using rolling z-scores
3. **Market-Making Fallback** — Any product without an active directional signal gets bid/ask quotes inside the spread

### The 10 Modules

| Module | Type | Products | Key Params |
|---|---|---|---|
| PEBBLES | Group residual | 5 (XS, S, M, L, XL) | w=500, z=2.35, hold-to-flip |
| TRANSLATOR | 4-pair network | 5 (AB-GM, EC-VB, SG-EC, AB-EC) | w=500, z=2.0–3.25 |
| MICROCHIP | 3 pairs | 5 (OT, CR, SR) | w=1000–2500, z=1.25–3.0 |
| ROBOT | 2 pairs | 4 (LV, DM) | w=500–2000, z=2.25–3.0 |
| SNACKPACK | 3 EWMA pairs | 5 (CV, RS, PR) | EMA α=0.00005, z=2.75 |
| SLEEP_POD | 3 pairs (2 EWMA + 1 rolling) | 5 (PC, LN, SP) | z=2.75 |
| GALAXY_SOUNDS | 2 pairs | 4 (DM-BH, SW-SF) | w=1500–3000, z=2.5–3.0 |
| OXYGEN_SHAKE | 2 pairs | 4 (CG, EM) | w=500–3500, z=2.0–3.0 |
| UV_VISOR | 2 pairs | 4 (YM, AR) | w=1500–2500, z=2.5–2.75 |
| PANEL | 2 pairs | 4 (1X2-2X4, 2X2-1X4) | w=1000–4000, z=1.75–2.5 |

**Total: 45 products traded directionally, 5 remaining get market-making only.**

### Key Engineering

- **State compression**: base64-encoded int16 history arrays, offset encoding, single-character JSON keys
- **Position clamping**: all aggregate targets clamped to ±10 (position limit) before ordering
- **No limit breaches**: order_to_target() enforces position limits on every order

**Backtested PnL: 1.67M across 3 days (10k-tick practice data).**
