# 01 — Market Scan: 50 Products at a Glance

## The Question

Day 1 of R5. 50 completely new products. Zero prior knowledge. Where do we start?

We built a systematic scanner (`scripts/r5_scan.py`) that computed per-product statistics and per-category correlations across all 3 days of practice data (days 2, 3, 4 — ~10,000 ticks each).

## What We Found

### Headline 1: Trends, Not Stationarity

R3/R4 products were mean-reverting (HYDROGEL ac1 = −0.129). **R5 was different.** Top drifts over 3 days:

| Product | Drift (3-day) | dmid std | ac1 of dmid |
|---|---|---|---|
| PEBBLES_XL | +6,068 | 30.3 | +0.008 |
| MICROCHIP_OVAL | −4,481 | 12.5 | −0.007 |
| PEBBLES_XS | −3,962 | 15.1 | −0.016 |
| OXYGEN_SHAKE_GARLIC | +3,886 | 12.0 | −0.004 |
| MICROCHIP_SQUARE | +3,633 | 20.7 | −0.024 |

**ac1_dmid ≈ 0 across the board.** Mid-price increments were uncorrelated — a random walk in levels with drift. No fast mean-reversion in price increments.

One exception: **ROBOT_IRONING ac1_dmid = −0.125** — the only non-trivial mean-reverter in the entire 50-product field.

### Headline 2: Siblings Diverge

We computed pairwise mid-price correlations within each category:

| Category | Avg intra-cat correlation | Read |
|---|---|---|
| SLEEP_POD | **+0.38** | Co-moving. Single factor. |
| GALAXY_SOUNDS | +0.06 | Independent |
| TRANSLATOR | −0.09 | Weakly divergent |
| UV_VISOR | −0.11 | Divergent |
| MICROCHIP | −0.12 | Divergent, high dispersion |
| OXYGEN_SHAKE | −0.12 | Divergent |
| ROBOT | −0.16 | Divergent |
| PANEL | −0.18 | Divergent, size-coded |
| PEBBLES | −0.21 | Divergent, size-coded |
| SNACKPACK | **−0.23** | Most divergent — pairs candidate |

**8 of 10 categories had negative intra-category correlation.** Products within a category weren't co-moving — they were actively diverging. This matched the problem statement's hint about "embedded patterns in certain groups."

### What This Told Us

1. **Don't trend-follow.** ac1 ≈ 0 means no momentum signal. Drift is real but unpredictable.
2. **Look for pairs/baskets within and across categories.** Negative intra-category correlation = diverging siblings = possible spread mean-reversion.
3. **SLEEP_POD is special** — the only positively correlated category. Possible single-factor index.
4. **PEBBLES and PANEL are size-coded** — possible arithmetic basket relationships (4X4 ≈ 4×1X4?).
5. **ROBOT_IRONING is special** — the lone mean-reverter. Possible market-making target.

## Priority List for Deep Dives

Based on signal strength, we ranked categories for detailed research:

1. **PEBBLES** — size-coded, ±6k drift spread, basket-arb candidate
2. **PANEL** — size-coded, area relationships to test
3. **SNACKPACK** — most negative intra-corr, strongest pairs candidate
4. **MICROCHIP** — highest price dispersion (6,732 median max-min), fewer trades (569 vs 733)
5. **UV_VISOR** — wavelength-ordered, AMBER drifting hard
6. **SLEEP_POD** — the lone positive-corr category
7–10. OXYGEN_SHAKE, GALAXY_SOUNDS, ROBOT, TRANSLATOR — lower priority

---

**Next:** [02-pebbles-constraint.md](02-pebbles-constraint.md) — The most striking finding in R5.
