# 02 — Backtester Evolution: From Fake Fills to High Fidelity

## The Problem

After Round 1, we had two backtesting systems and neither was accurate enough.

### Codex Backtester Flaws
- Market trade matching double-counted fills
- No hidden taker simulation
- No price-time priority enforcement

### r1bt (Anannya's Platform)
Architecturally superior — had LevelOwner tracking, taker simulation, queue modeling — but untested against our live data.

## Fixes Applied

1. Removed market trade double-counting
2. Added hidden taker layer with stochastic fills
3. Calibrated rates to match official replay

| Metric | Before | After |
|---|---|---|
| Local PnL | 34,620 | 288,619 |
| Official replay | — | 288,510 |
| Error | ~66% | **0.04%** |

## r1bt Audit Result

All fixes to the Codex backtester were reinventing what r1bt already did correctly. r1bt was the correct platform going forward.

---

**Next:** [03-maf-manual.md](03-maf-manual.md)
