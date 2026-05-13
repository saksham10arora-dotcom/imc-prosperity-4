# 06 — Portfolio Construction: Catching Our Own Selection Bias

## The Problem

Scripts: `08_portfolio_greedy.py`, `09_day_stability.py`, `16_proper_oos_portfolio.py`, `10_fill_cost.py`

After the pair sweep (Step 04), we had 471 profitable pairs. The initial headline was bold: "K=1 portfolio of 23 cross-category pairs = **552,415 OOS PnL.**"

Then we looked more carefully at how that number was computed — and caught ourselves cheating.

## The Bias

The 552k number was computed by:
1. Selecting pairs that were positive on D4
2. Totalling their D4 PnL

That's circular. We selected the winners *on the test set*, then measured their performance *on the same test set*. Of course it looked great — every pair was positive by construction.

## The Honest Test

Script `16_proper_oos_portfolio.py` did it correctly:
1. Rank all 1,225 pairs by D2+D3 PnL only (training set)
2. Greedy-select K=1 portfolio (each product in at most 1 pair)
3. **Freeze the portfolio.** No more changes.
4. Measure PnL on D4 (test set). No peeking.

| Selection rule | Pairs | IS (D2+D3) PnL | **D4 OOS PnL** | Positive/Negative |
|---|---|---|---|---|
| A — total IS rank | 24 | 806,655 | **197,930** | 20 / 4 |
| B — require D2>0 AND D3>0 | 24 | 791,850 | 194,990 | 20 / 4 |
| C — B + require total ≥ 20k | 19 | 717,470 | 188,180 | 17 / 2 |
| D — rank by D3 only (recency) | 24 | 683,855 | 156,820 | 17 / 7 |
| Cheating upper bound | 24 | — | 584,455 | 24 / 0 |

**Strategy A (simple total-IS rank) was best at 197,930.** Stability filters didn't add value. The honest OOS captured 34% of the cheating optimum.

## Realistic Fill Costs (Script 10)

Mid-fills assume we can trade at the midpoint of the spread. In reality, we cross the bid-ask:
- To go long the spread (buy A, sell B): pay A's ask, receive B's bid
- Each side costs half the bid-ask spread

| Portfolio | Mid PnL | Real (bid/ask) PnL | Haircut |
|---|---|---|---|
| K=1, 23 pairs, full 3 days | 820,550 | **637,380** | 22% |

Only 1 of 23 pairs flipped negative after costs. Top pairs lost only 9–18%.

## The Honest Headline

| Metric | Cherry-picked | Honest OOS |
|---|---|---|
| 3-day PnL (mid fills) | 552,415 | ~198,000 |
| 3-day PnL (real bid/ask fills) | ~440,000 | **~155,000** |
| Pairs positive on D4 | 23/23 (by construction) | 20/24 |

Still a shippable strategy — positive on 83% of pairs, 90% trade-level win rate, no portfolio-level negative day. But **3× smaller** than the initial cherry-picked claim.

## Why We Published This Correction

It would have been easy to present only the 552k number. But we'd already learned (from the vol smile saga in R3/R4) that unchallenged claims lead to bad decisions. The honest number set realistic expectations for live performance and prevented overconfidence in pair selection.

---

**Next:** [07-negative-results.md](07-negative-results.md) — What we tried that didn't work.
