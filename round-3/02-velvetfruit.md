# 02 — VELVETFRUIT_EXTRACT: The Dual-Role Asset

## The Question

VELVETFRUIT_EXTRACT served two roles: a standalone delta-1 asset *and* the underlier for VEV voucher options. We needed to understand its microstructure independently, and decide how much of our 200-unit position limit to reserve for delta hedging the options book.

## Statistical Profile

| Statistic | Value |
|---|---|
| Lag-1 autocorrelation (mid) | **−0.16** (mean-reverting, stronger than HYDROGEL) |
| Stability | Consistent across all 3 days |
| Long-term mean | ~5250 |
| Cross-correlation with HYDROGEL | **0.006** (essentially independent) |

Unlike HYDROGEL, VELVETFRUIT had no exploitable bot fingerprint. Trade flow was diffuse, with Poisson-ish cadence and no concentration at specific offsets.

## Spread Regime Analysis

We identified three distinct spread regimes:

| Regime | Condition | Frequency | Interpretation |
|---|---|---|---|
| Tight | spread ≤ 2 | 4% of ticks | Momentary book compression — aggressive quotes |
| Large-wall | bid_vol ≥ 45 | 45–70% | Large resting orders at L1 — stable regime |
| Normal | everything else | ~30% | Standard trading |

The tight-spread regime was interesting: when `ask_vol < 15 AND spread ≤ 2`, it signaled a compression event where we could buy cheaply. The symmetric condition (`bid_vol < 15 AND spread ≤ 2`) signaled a sell.

## Position Budget Allocation

With 200 units of position limit and a dual role (standalone trading + option hedge), we had to split:

- **±50 units** for standalone mean-reversion (the z-score strategy)
- **±150 units** reserved for delta hedging the voucher portfolio

This was conservative, but losing control of the hedge budget risked uncontrolled delta exposure from the options book.

## Z-Score Strategy

Rather than the wall-mid approach used for HYDROGEL, VELVETFRUIT used an EMA-based z-score:

1. Track `EMA_mean` and `EMA_std` (both using α = 0.0002)
2. Compute `z = (mid - EMA_mean) / EMA_std`
3. Buy aggressively (hit ask) when `z < -1.5`
4. Sell aggressively (hit bid) when `z > +1.5`

The EMA parameters were **seeded from historical priors** on the first tick (mean = 5250.10, std = 15.63), then updated every tick. This eliminated cold-start issues — the strategy was ready from tick 1.

---

**Next:** [03-options.md](03-options.md) — Pricing VEV vouchers and the flat vol smile.
