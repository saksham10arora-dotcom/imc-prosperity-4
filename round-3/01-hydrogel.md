# 01 — HYDROGEL_PACK: The ±8 Bot

## The Question

HYDROGEL_PACK was a delta-1 asset with a 200-unit position limit. Before we could trade it, we needed to understand: what kind of asset is this, and who else is trading it?

## What We Measured

We ran a full statistical fingerprint using 3 days of historical data (days 0–2, ~30,000 ticks each):

| Statistic | Value | Interpretation |
|---|---|---|
| Lag-1 autocorrelation | **−0.129** | Mean-reverting (negative = price overshoots then corrects) |
| Hurst exponent (R/S) | **H = 0.196** | Strongly sub-diffusive (well below 0.5 random walk) |
| AR(1) half-life | **~300 ticks** | Deviations from fair value correct in ~30 seconds |
| Long-term mean | ~9991 | Stable across all 3 days, std = 32 |

**Conclusion:** HYDROGEL_PACK is a textbook mean-reverting asset. Price deviates from ~9991, then snaps back.

## Fair Value: Wall Mid

Wall mid (L1 midpoint) was the clear winner as a fair value proxy:

- Correlation with reported mid: **0.9996**
- Mean divergence: **0.012 ticks**
- Max divergence: **4.5 ticks**
- VWAP and wall-mid were nearly identical (within 0.06 ticks)

Simple, fast, and almost perfectly correlated with the reported mid. No correction needed.

## The Discovery: The ±8 Bot

When we plotted the distribution of trade prices relative to wall mid, a striking pattern emerged:

- **36% of all trades** occurred at exactly `wall_mid ± 8` ticks (within ±0.5 tolerance)
- Top offsets from wall mid: **+8.5** (93 trades), **−7.5** (88), **−8.5** (83), **+7.5** (82)
- Lot sizes were uniform {2, 3, 4, 5, 6} — Herfindahl = 0.20 (maximum diversity)
- Cadence: top gap = 100 ticks (10% share), median gap = 700 ticks — Poisson-ish

**This was a symmetric, uninformed market-taking bot.** It wasn't responding to signals — it was mechanically lifting asks and hitting bids at fixed offsets from fair value. Not a market-maker (not one-sided). Not informed (symmetric). Just noise flow hitting the book at ±8.

## Why This Mattered

If someone is *always* willing to buy at `fair_value + 8` and sell at `fair_value - 8`, and they're uninformed, then we can profit by quoting *inside* their offsets.

**Our edge:** Quote at `wall_mid ± 7`. We undercut the ±8 bot by 1 tick. When the bot fires, it hits our quotes first (price-time priority). We collect the spread.

## The Spread Scenario Decoder

We also discovered that spread compression carried directional information:

When `spread < 9` ticks:
- If `|ask_shift| > |bid_shift| + 2` → the ask dropped while the bid held → **buy signal**
- If `|bid_shift| > |ask_shift| + 2` → the bid rose while the ask held → **sell signal**
- If both shifted → **mixed signal** (both sides quote)

When `spread ≥ 15` ticks → quotes reset (ignore previous levels).

## Risk Assessment

1. **Spread compression risk:** If other bots tighten to ±7 or ±6, our edge compresses
2. **Inventory trap:** A one-sided 50-tick run pins us at max position. Mitigation: skew factor + max position cap at 150 (leaving 50-lot buffer before the 200 limit)
3. **Half-life instability:** H = 0.196 is a 3-day aggregate. If the regime shifts to trending, autocorrelation flips. Would need rolling 500-tick check.

---

**Next:** [02-velvetfruit.md](02-velvetfruit.md) — The dual-role asset that served as both a standalone trade and an options hedge.
