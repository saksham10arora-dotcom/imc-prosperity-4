# 01 — Counterparty Forensics: The Marks

## The Question

With counterparty names now visible in R4, we could answer the question we'd been guessing at in R3: exactly *who* was the ±8 bot? Were there multiple bots? And on the options side, who was providing the persistent seller flow?

## HYDROGEL_PACK: Three Marks

We ran a complete trade-level analysis, grouping every trade by buyer/seller name:

| Mark | Role | Offset from wall mid | Aggressor? | Volume share |
|---|---|---|---|---|
| **Mark 38** | The ±8 bot from R3 (now named) | buys at +8, sells at −8 | 100% aggressor | 100% of trades |
| **Mark 14** | Passive market-maker | posts at ±8 | 100% passive | 98.2% by volume |
| **Mark 22** | Sporadic passive poster | posts at ±4 | 100% passive | 1.8% by volume |

**Mark 38** was the R3 ±8 bot — confirmed by matching the exact offset, lot-size distribution, and cadence we'd fingerprinted anonymously. The naming revealed what we'd suspected: this was a single, uninformed, mechanical aggressor.

**Mark 14** was the standing liquidity. When Mark 38 fired, it almost always filled against Mark 14's resting orders. Mark 14 was, effectively, the "house" market-maker.

**Mark 22** was rare but interesting — posting at ±4, tighter than our ±7 quotes. However, with only 19 trades across 3 days (median gap of 129,250 ticks between appearances), Mark 22 was negligible.

### What This Confirmed

Our R3 strategy was correct: by quoting at ±7, we had price-time priority over Mark 14's ±8 quotes. When Mark 38 (the aggressor) fired, it hit our ±7 quotes first. Mark 14 only got filled when we weren't positioned.

## VEV Vouchers: The Mark 22 → Mark 01 Flow

On the options side, the naming revealed a clean bilateral flow:

| Mark | Behavior | Lots | Direction | Aggressor? |
|---|---|---|---|---|
| **Mark 22** | Persistent seller | 4,972 | 100% sell | 100% aggressor |
| **Mark 01** | Persistent buyer | 4,636 | 100% buy | 100% passive |

Mark 22 was dumping options. Mark 01 was absorbing them. This was the R3 "seller-dominated flow" — now with names attached.

### The Interception Strategy

Mark 01 posted resting bids. Mark 22's sell orders hit those bids. Our strategy: **step inside Mark 01's resting bid by 0.5 ticks**. When Mark 22's selling flow arrived, it would fill us first (better price for the seller), and Mark 01's bid would only get the overflow.

```
Mark 01's bid:  fair_value - 2.0
Our bid:        fair_value - 1.5    ← price-time priority
Mark 22 sells:  hits our bid first
```

## R4 Micro-regime Changes

Beyond naming, the market's statistical properties had shifted slightly from R3:

| Metric | R3 | R4 | Implication |
|---|---|---|---|
| HYDROGEL long-term mean | ~9991 | **~9995** | Re-center the mean-reversion anchor |
| |Δmid| std | 2.17 | **1.39** (−36%) | Lower adverse selection. ±7 spread still captures edge. |
| corr(deviation, fwd_100) | — | **−0.63** | When price deviates ≥60 from 9995, strong snap-back expected |
| Spread > 16 → fwd_20 | — | **−1.24** | Wide spreads are bearish — suppress marginal bids |

---

**Next:** [02-vol-surface.md](02-vol-surface.md) — How we caught two agent errors on the vol smile.
