# 05 - Monte Carlo Simulator: Synthetic Markets from Calibrated Bots

## The Question

The replay backtester runs against historical data - but there are only 3 days of it. Could we generate *unlimited* synthetic market data from our calibrated bot parameters, and test strategies against thousands of scenarios?

## What We Built

`mc_simulator.py` - a full synthetic market generator:

1. **OU price path for Osmium** - α=0.0294, β=1.145, γ=10000
2. **Drift + noise for Pepper** - +0.108/tick, σ=1.7
3. **Synthetic order books** - Wall bots at calibrated offsets, inside bots at Bernoulli rates
4. **Order matching engine** - Sweeps limit orders against the synthetic book
5. **Taker-fills-us logic** - Simulated market takers hitting our passive orders
6. **Resting order carry** - Unfilled orders persist to next tick
7. **Scrooge McDuck logic** - Hidden bot at FV±100 when book goes one-sided
8. **Crash mode** - `--crash` flips Pepper drift negative at tick 5000
9. **iawa's parameter sampling** - Each sim samples bot parameters from Normal(mean, std)

## Accuracy Check

| Strategy | MC PnL | Replay PnL | Error |
|---|---|---|---|
| Algov4 (Zain v2) | 94,157 | ~95,000 | **< 1%** ✓ |
| Algov5 (Zain final) | −141,661 | ~96,000 | **Completely wrong** ✗ |

**The MC simulator was only reliable for algov4-style strategies.** Algov5 used EMA smoothing and threshold logic that interacted with the synthetic book structure differently. The synthetic 2-level books couldn't reproduce the dynamics algov5 exploited.

## Crash Testing (Algov4)

| Scenario | OSMIUM | PEPPER | TOTAL |
|---|---|---|---|
| Normal (50 sims) | 8,134 | 86,023 | 94,157 |
| Crash at tick 5000 | 8,134 | 2,695 | **10,829** |
| 5th percentile worst | - | - | **−9,200** |

Pepper PnL drops from +86K to +2.7K under a crash. Strategy survives but gets hurt.

## Lesson Learned

**MC simulators are dangerous when the synthetic environment doesn't match real microstructure.** For simple strategies, MC works. For strategies that exploit subtle book dynamics, only replay against real data is trustworthy.

**Rule:** Always validate MC against replay first. If they disagree by more than 10%, the MC is wrong.

---


