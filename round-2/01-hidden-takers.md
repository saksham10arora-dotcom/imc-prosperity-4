# 01 — Hidden Takers: 64% of Fills Are Invisible

## The Question

After Round 1 scoring, we had access to our live execution log (`222844.log` — 983 ticks, 108 fills). We asked: how many of our fills matched visible book levels, and how many came from counterparties we couldn't see?

## The Discovery

**64% of our live fills (69/108) came from hidden flow** — counterparties NOT visible in the order book snapshot at the time of the trade.

| Fill Type | Count | Share |
|---|---|---|
| Hidden taker (not in book) | 69 | **64%** |
| Visible book match | 38 | 35% |
| Ambiguous | 1 | 1% |

### Where Hidden Fills Concentrate

Hidden fills clustered at `best_bid + 1` and `best_ask - 1` — inside the spread. These counterparties posted inside the visible book levels, but their orders arrived and were consumed within the same tick.

### Per-Product Breakdown

| Product | Hidden Buys | Hidden Sells | Buy Rate/tick | Sell Rate/tick |
|---|---|---|---|---|
| Osmium | 32 | 29 | 3.26% | 2.95% |
| Pepper | 2 | 6 | 0.20% | 0.61% |

**Osmium had 10× more hidden flow than Pepper.** Hidden fill volumes: Osmium mean=5.8 [2–10], Pepper mean=4.6 [3–7].

## Why It Mattered

### 1. The Book Is a Post-Trade Residual

The order book in `TradingState` is what's LEFT after all bot orders and market trades have been processed. The "true" liquidity at any price is higher than what the book shows.

### 2. Price-Time Priority Is Real

Bot orders have time priority at the same price level. If we post at `best_bid`, we do NOT get filled — the bot was there first. To get passive fills, we must **improve the price**.

### 3. Price Improvement Exists

Confirmed from live log: we fill at the **book price**, not our order price. If our buy at 10005 hits an ask at 10002, we fill at 10002.

## Calibrated Hidden Taker Rates

After iterative calibration:

| Product | Buy Rate | Sell Rate |
|---|---|---|
| Osmium | 0.0155 | 0.0140 |
| Pepper | 0.0010 | 0.0030 |

**Result:** Local backtester produced 288,619 PnL vs 288,510 official replay — **0.04% error**.

---

**Next:** [03-maf-manual.md](03-maf-manual.md) — Manual challenge analysis.
