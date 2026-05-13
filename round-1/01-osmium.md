# 01 — ASH_COATED_OSMIUM: The OU Clock

## The Question

ASH_COATED_OSMIUM was a delta-1 asset with an 80-unit position limit. Before we could trade it, we needed to understand: what kind of price process is this, and who else is in the book?

## What We Measured

We ran a full statistical fingerprint using 3 days of historical data (days −2, −1, 0 — ~10,000 ticks each):

| Statistic | Value | Interpretation |
|---|---|---|
| Lag-1 autocorrelation (wall_mid steps) | **−0.458** | Strongly mean-reverting |
| OU α (mean-reversion speed) | **0.0294** | Half-life ~24 ticks (~2.4 seconds) |
| OU β (volatility) | **1.145** | |
| OU γ (long-run mean) | **10,000** | Stable across all 3 days |
| Implied std (β/√2α) | **4.72** | Typical range: 9985–10015 |
| Spread | ~16 ticks total | 8 each side from wall_mid |

**Conclusion:** OSMIUM is a textbook Ornstein-Uhlenbeck mean-reverting process centered on 10,000. Deviations correct rapidly.

## The Discovery: 6 Independent Bots

When we decomposed the order book tick by tick, we found **6 distinct bots**, each with independent arrival processes and fixed behavioral rules:

### Bot 1 — Inner Wall Maker
- **Presence:** ~95% of ticks (always there)
- **Offset:** ±8 ticks from wall_mid
- **Volume:** Uniform [10, 15]
- **Role:** Defines the tight spread. This is the "inner wall" — the visible market.

### Bot 2 — Outer Wall Maker
- **Presence:** 100% of ticks
- **Offset:** ±10.5 ticks from wall_mid
- **Volume:** Uniform [20, 30]
- **Role:** Provides depth behind the inner wall. Always present.

### Bot 3 — Passive Inside Maker
- **Presence:** ~2.5% of ticks (Bernoulli per tick)
- **Offset:** floor(FV) ± 2, on the CORRECT side (buy below FV, sell above FV)
- **Volume:** Uniform [2, 5]
- **Offset formula:** `round(FV + 2 + k)`, where k varies 0.3–0.7 across days (initially measured as 2.5, later refined with iawa's confirmation)
- **Role:** Free edge when it appears — quotes inside the spread at favorable prices.

### Bot 4 — Crossed Inside Maker
- **Presence:** ~1.3% of ticks (Bernoulli per tick, independent of Bot 3)
- **Offset:** floor(FV) ± 2, on the WRONG side (wants to get filled)
- **Volume:** Uniform [4, 10]
- **Role:** Easy fill target. Posts buy orders above FV and sell orders below FV.

### Bot 5 — Taker
- **Arrival:** Poisson, rate ~1/2300 per tick
- **Direction:** 50/50 buy/sell
- **Volume:** Uniform [2, 7]
- **Behavior:** Almost never eats the full posted level. Direction-agnostic — doesn't care about distance from fair value. The wall midpoint does not react to trades.

### Bot 6 — Scrooge McDuck (Hidden)
- **Trigger:** Appears ONLY when one side of the order book is completely empty
- **Behavior:** Bids at FV + 100 (or asks at FV − 100) when the opposite side is cleared
- **Discovery:** Could NOT be seen in historical data — the book never goes empty without player intervention. Only discoverable by probing live.
- **Source:** beast (external competitor) found it by submitting a strategy that deliberately ate one side.

**Key insight about Bots 3 and 4:** We initially grouped them as a single "inside bot" at ±2.5 from wall_mid. Splitting them into two independent Bernoulli processes matched the volume distribution better, which iawa independently confirmed from his own calibration.

## Cross-Asset Correlation

| Day | Correlation (Osmium, Pepper) |
|---|---|
| Day −2 | −0.001 |
| Day −1 | +0.015 |
| Day 0 | −0.003 |

**Products are completely independent.** No cross-asset signal exists.

## Risk Assessment

1. **Scrooge exploit dependency:** ~1.5K of the final 12.2K live score came from Scrooge. If IMC patches it in later rounds, that edge disappears.
2. **Bot parameter drift:** Inside bot offset k shifts across days (0.3 to 0.7). Could shift further in live.
3. **Wall_mid stability:** All fair-value estimates depend on wall_mid being stable. If the inner wall bot changes behavior, all offsets break.

---

**Next:** [02-pepper.md](02-pepper.md) — The trending asset with a statistically proven but unmonetizable signal.
