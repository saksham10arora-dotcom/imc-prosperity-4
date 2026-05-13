# 06 — Negative Results: What We Tried That Didn't Work

Every research program produces dead ends. These are ours.

## 1. Asymmetry Signal Integration (V14)

**Idea:** Use the level asymmetry signal (asym ≤ −1 → 91% up) to boost the Pepper trend indicator.

**Result:** 10.4K live vs 10.7K baseline. **Worse.**

**Why it failed:** At max position (long 80), the signal has no actionable use. Reducing position on asym ≥ +1 caused premature exits from profitable trends. The trend indicator already captured the same directional information.

## 2. Bot Sniping (V16)

**Idea:** When Bot 3/4 appear (~2.5% and ~1.3% of ticks), aggressively take their quotes for guaranteed fills at favorable prices.

**Result:** Same or worse PnL. No improvement.

**Why it failed:** The bots appear rarely, and the existing strategy already captures them as part of regular flow.

## 3. Every V13–V16 Variant

| Version | Replay PnL | Live PnL | Key Change |
|---|---|---|---|
| Zain original | 287K | 10.7K | Baseline |
| V13 | ~284K | — | Parameter sweep variant |
| V14 | ~284K | — | Asymmetry-boosted indicator |
| V15 | ~284K | — | Refined asymmetry integration |
| V16 | 284K | 10.4K | Bot sniping + asymmetry |
| **Algov4 (+Scrooge)** | **284K** | **12.2K** | Scrooge exploit added |

**Every integration attempt scored the same or worse than the original.** The strategy was already near-optimal.

## 4. Khima's Codex Analysis

Independent statistical analysis — contingency tests, motif analysis, correlation checks, chi-squared tests on book state transitions. Confirmed everything we'd already found. No new alpha discovered.

## 5. MC Simulator for Strategy Comparison

MC said algov5 was catastrophically bad (−142K). Replay said it was slightly better (+288K). Almost led us to discard the better strategy.

**Lesson:** Never use a single evaluation tool. Cross-validate MC with replay.

## The Big Lesson

**Understanding the market ≠ beating the market.** We produced a detailed, statistically validated decomposition of both products. None of it translated to incremental PnL. The biggest gain (+1.5K) came from a competitor tip about a hidden bot discovered through live probing.

---

**Final Round 1 Result:** Global Rank **#90** — 12,200 SeaShells live.
