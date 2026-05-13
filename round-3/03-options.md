# 03 - VEV Vouchers: The Flat Vol Smile

## The Question

VEV vouchers were European call options on VELVETFRUIT_EXTRACT with 10 strikes (VEV_4000 through VEV_6500). The key questions: What implied volatility surface should we use? Is there a smile? And who is providing the flow?

## Strike Classification

Not all 10 strikes were real options:

| Strike | Status | Why |
|---|---|---|
| VEV_4000, VEV_4500 | **Deep ITM** | Traded at intrinsic value. No extrinsic value, no optionality. |
| VEV_5000–5500 | **Tradeable** | Had meaningful extrinsic value. The real options. |
| VEV_6000, VEV_6500 | **Pinned** | Permanently at 0.50 XIRECs. std = 0. Dead strikes. |

This immediately simplified the problem from 10 strikes to 6 (and really 4 with significant extrinsic).

## The Vol Smile: It's Flat

We computed implied volatility for each strike using Black-Scholes inversion, then tested whether a parabolic smile existed:

| Metric | Value |
|---|---|
| Pooled σ (across tradeable strikes) | **0.2323 ± 0.009** |
| Parabola R² | **0.02–0.09** |
| Per-strike IV range | 0.223 – 0.241 |

A parabola fit explained only 2–9% of the IV variation. **The smile was effectively flat.** There was no need for per-strike IV calibration — a single volatility number was sufficient.

This was a major architectural simplification. Instead of maintaining a smile model, we could use one σ for all strikes.

## TTE Mapping

The time-to-expiry decreased by 1 day each round:

| Round | TTE (days) |
|---|---|
| Tutorial | 8 |
| Round 1 | 7 |
| Round 2 | 6 |
| Round 3 (live) | 5 |

Verified empirically by checking option decay rates against BS predictions.

## Flow Analysis

Trade flow on vouchers was heavily asymmetric:

- **82–97% of voucher flow was selling** (depending on strike)
- Seller-aggressor dominated across all tradeable strikes
- This meant we should quote with **tighter bids** (to step inside the resting buyer and capture seller flow) and **wider asks**

## The Antigravity Correction

During development, our IDE agent initially had the bid/ask widths **swapped** - wider on the ask side, tighter on the bid. Our independent review process (Antigravity) caught this by doing a direct recount of aggressor direction across 3 days of trade data.

This would have been catastrophic if shipped: we'd have been quoting the wrong side of the market, offering liquidity where there was no demand and missing the dominant seller flow entirely.

**Lesson:** Independent verification of directional claims is non-negotiable, especially when the claim determines which side of the market you face.

## Result

Round 3 finished at **#84 globally, #7 in India** - up from #277 at the end of Phase 1. The HYDROGEL market-making strategy drove the bulk of PnL.

---

**Next round:** [Round 4](../round-4/README.md) - Counterparty names appear.
