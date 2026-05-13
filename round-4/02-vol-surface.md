# 02 - The Vol Smile Saga: Catching Agent Errors

## The Question

Did the R4 vol surface change from R3? Should we recalibrate our single-vol BS architecture?

## The Error (Twice)

A sub-agent analyzed R4 options data and reported: "R4 smile has R² = 0.97 - strongly curved. You need per-strike IV calibration."

This contradicted our R3 finding (R² = 0.02–0.09, flat smile). A 50× jump in explanatory power would be extraordinary.

### What Went Wrong

The agent had included **sub-intrinsic strikes** (VEV_4000, VEV_4500) in the IV computation. These deep ITM options traded at intrinsic value - BS inversion on them produces nonsensical implied volatilities (extremely high or undefined). Including these garbage IVs in the parabola fit inflated the curvature and the R².

### The Catch

Our independent review process (Antigravity) flagged this by:

1. Recomputing IV only on strikes with meaningful extrinsic value (VEV_5000–5500)
2. Running the parabola fit on the cleaned dataset
3. Getting **R² = 0.01–0.05** - still flat, consistent with R3

**Actual R4 smile: flat.** Single-vol BS architecture was correct all along.

This was the **second** time a sub-agent produced wrong IV calibration (the first was in R3). Both times, the error was including inappropriate data points in the fit. Both times, independent verification caught it.

### The Rule We Instituted

After the second error: **no claim about implied volatility or smile shape ships into production without independent reproduction from raw data.** Period.

## Daily σ Recalibration

The single-vol did need daily updating as TTE decreased:

| Day | TTE | σ (annualized) |
|---|---|---|
| Day 1 | 4 days | 0.3133 |
| Day 2 | 3 days | 0.3318 |
| Day 3 | 2 days | 0.3636 |

The rising σ as TTE shrinks is expected - shorter time horizon means proportionally more daily variance relative to remaining time. We recalibrated each day using the previous day's realized vol.

## Key Takeaway

The most valuable output of R4 wasn't a new signal or a better model. It was the **verification discipline**: every quantitative claim reviewed independently before deployment. This process would prove essential in R5, where the scale of research (50 products, 1,225 pairs) made casual error-checking impossible.

---

**Next round:** [Round 5](../round-5/README.md) - 50 new products, everything resets.
