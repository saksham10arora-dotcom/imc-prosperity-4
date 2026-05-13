# 03 — MAF Auction & Manual Allocation

## Market Access Fee (MAF)

Round 2 introduced bidding for extra market visibility.

- Same products (OSMIUM + PEPPER), same limits (80 each)
- Can bid for **25% more quotes** in the order book
- Top 50% of bids accepted. Blind auction.
- During testing: 80% visibility, slightly randomized per submission

**Our decision:** `bid() = 2500`. Conservative enough to be net-positive if we win.

## Manual Challenge: Budget Allocation

50,000 XIRECs across Research (x), Scale (y), Speed (z).

| Component | Formula | Character |
|---|---|---|
| Research(x) | 200,000 × ln(1+x) / ln(101) | Logarithmic — diminishing returns |
| Scale(y) | 7 × y / 100 | Linear — constant marginal return |
| Speed(z) | Rank-based (0.1→0.9) | Competitive — zero-sum |

**Optimal allocation:** Research = 23, Scale = 77, Speed = 0

Speed is a trap — purely competitive, zero-sum arms race. Most teams over-invest.

## Round 2 Ecosystem Findings

| Finding | Detail |
|---|---|
| Bot behavior | Identical to R1 (same offsets, volumes, frequencies) |
| Scrooge bot | Still active at ~FV±100 |
| Official backtester | `prosperity4btest` did NOT support R2 data |
| Cross-asset correlation | Still zero |

---

**Next:** [04-negative-results.md](04-negative-results.md)
