# 03 — The Methodology War: Rolling-Z vs Previous-Day Mean

## The Problem

Script: `02_methodology.py` → Output: `02_methodology.csv`

This was the single most consequential research question in R5. Two different methods for anchoring pair spread signals produced **wildly different results on the same data:**

| Method | How it works |
|---|---|
| **A. Previous-day mean** | Use yesterday's full-day average spread as today's "fair" spread. Enter when today's spread deviates by ≥1.5σ from yesterday's mean. |
| **B. Rolling z-score** | Track a trailing 2,000-tick window of the spread. Enter when the current spread is ≥1.5σ from the rolling mean. |

### The Divergence

Same data, same pair, same entry/exit rules — different anchor:

| Pair | Method A (prev-day) | Method B (rolling-z) |
|---|---|---|
| SNACKPACK CHOC−VAN | **+25,220** | +4,810 |
| TRANSLATOR ECLIPSE−VOID | **SKIP** (non-stationary) | **+42,475** (#4 in field) |
| ROBOT VAC−LAU | Not tested | **+42,085** (#5 in field) |
| PANEL 1X2−2X4 | **SKIP** (non-stationary) | **+35,430** (#13 in field) |

Method A said SKIP on TRANSLATOR, ROBOT pairs, and PANEL. Method B found them among the most profitable pairs in the entire field. **Both couldn't be right.**

## How We Resolved It

We designed a proper out-of-sample test. Train on days 2+3 (20,000 ticks). Trade on day 4 (10,000 ticks). No peeking.

| Metric | Method A (prev-day) | Method B (rolling-z) |
|---|---|---|
| Total D4 OOS PnL (100 within-cat pairs) | 309,135 | **616,365** |
| Positive pairs | 60/100 | **67/100** |
| Avg trades per pair | 1–7 | **15–40** |
| Top-pair win rates | 70–85% | **85–95%** |

**Rolling-z won by 2×.**

### Why Method A Failed

Method A assumed the spread mean was stable across days. But R5 spreads drifted — the mean on day 3 was different from day 2. When Method A used yesterday's mean as today's anchor, it either:
- Never fired (spread had drifted away from yesterday's mean permanently), or
- Fired on the wrong side (yesterday's "fair" was today's "extreme")

Method A's apparent wins (like SNACKPACK CHOC−VAN +25k) were small-sample artifacts — it fired 1–7 trades total, and those few happened to be winners. Method B fired 30–40 trades on the same pair, with consistent 85%+ win rates.

### Why Method B Worked

The rolling window **tracked the drift** while still detecting within-window excursions. It didn't care where the spread "should" be — it measured where the spread *has been recently* and fired when the current value was extreme relative to that recent history.

## What This Changed

This single finding **promoted 8 pairs from SKIP to SHIP:**

| Pair | Previous verdict | New verdict (rolling-z OOS) |
|---|---|---|
| TRANSLATOR ECLIPSE_CHARCOAL − VOID_BLUE | SKIP | **+42,475** |
| ROBOT VACUUMING − LAUNDRY | Not tested | **+42,085** |
| ROBOT DISHES − IRONING | Not tested | **+41,010** |
| TRANSLATOR ASTRO_BLACK − GRAPHITE_MIST | Not tested | **+33,885** |
| PANEL 1X2 − 2X4 | SKIP | **+35,430** |

The methodology war consumed multiple research sessions. In hindsight, we should have settled it on day 1 with a clean OOS test instead of debating theoretical arguments.

---

**Next:** [04-pair-sweep.md](04-pair-sweep.md) — All 1,225 pairs, ranked.
