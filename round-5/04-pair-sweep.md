# 04 — The 1,225-Pair Sweep

## The Idea

Scripts: `04_cross_category.py`, `06_cross_category_oos.py` → Outputs: `04_cross_category.csv`, `06_cross_category_oos.csv`

After resolving the methodology war in favor of rolling-z, we asked: why limit ourselves to within-category pairs? If rolling-z can detect spread stationarity in drifting products, then *any* two products whose spreads revert — whether in the same category or not — should work.

50 products × 49 partners ÷ 2 = **1,225 unique unordered pairs.** We tested all of them.

## Within-Category Results (Top 15)

| Rank | Category | Pair | PnL | Win Rate | Trades |
|---|---|---|---|---|---|
| 1 | MICROCHIP | OVAL − TRIANGLE | **63,480** | 90.7% | 43 |
| 2 | PEBBLES | M − XL | **61,170** | 75.0% | 36 |
| 3 | PEBBLES | S − L | 44,365 | 77.1% | 36 |
| 4 | TRANSLATOR | ECLIPSE_CHARCOAL − VOID_BLUE | 42,475 | 87.5% | 40 |
| 5 | ROBOT | VACUUMING − LAUNDRY | 42,085 | 89.7% | 40 |
| 6 | ROBOT | DISHES − IRONING | 41,010 | 88.2% | 34 |
| 7 | PEBBLES | XS − XL | 40,765 | 72.7% | 33 |
| 8 | MICROCHIP | CIRCLE − RECTANGLE | 40,545 | 87.5% | 41 |
| 9 | SNACKPACK | STRAWBERRY − RASPBERRY | 39,945 | 84.4% | 32 |
| 10 | SLEEP_POD | POLYESTER − COTTON | 39,920 | 78.8% | 34 |
| 11 | SNACKPACK | PISTACHIO − RASPBERRY | 38,620 | 87.9% | 33 |
| 12 | PEBBLES | XS − S | 37,325 | 80.6% | 32 |
| 13 | PANEL | 1X2 − 2X4 | 35,430 | 82.5% | 40 |
| 14 | TRANSLATOR | ASTRO_BLACK − GRAPHITE_MIST | 33,885 | 90.2% | 42 |
| 15 | MICROCHIP | SQUARE − TRIANGLE | 28,675 | 80.8% | 27 |

## Cross-Category: The Bigger Edge

Of the 1,225 pairs tested:

- **471 pairs profitable** both in-sample and out-of-sample
- **433 of those 471 (87%) were cross-category**
- Total OOS PnL across all 471: **6.6 million**

The cross-category edge was much larger than within-category. Here's why this was surprising: the initial research had focused entirely on within-category structure (PEBBLES constraint, SNACKPACK anti-correlation). But the rolling-z method found that *any* two products with complementary drift patterns could form a profitable pair.

### Top Cross-Category Pairs

| Rank | Pair | OOS PnL |
|---|---|---|
| 1 | MICROCHIP_CIRCLE − PEBBLES_XL | **107,145** |
| 2 | SLEEP_POD_POLYESTER − MICROCHIP_TRIANGLE | 59,715 |
| 3 | MICROCHIP_OVAL − PEBBLES_XS | 56,025 |
| 4 | ROBOT_VACUUMING − SNACKPACK_RASPBERRY | 51,820 |
| 5 | PEBBLES_S − PANEL_2X2 | 51,360 |

### "Factor Proxy" Products

Some products appeared in many profitable pairs — acting as universal hedging legs:

| Product | Appearances in top-50 OOS pairs |
|---|---|
| SLEEP_POD_POLYESTER | 8 |
| MICROCHIP_TRIANGLE | 8 |
| ROBOT_DISHES | 8 |
| PEBBLES_S | 7 |
| PEBBLES_XL | 6 |
| PEBBLES_M | 6 |

These products had high individual volatility (wide price walks) but their walks were predictable enough that pairing them with quieter products produced stationary spreads. PEBBLES_XL — with its 2× volatility from the sum constraint — was especially effective.

## The 13-Pair "Robust Core"

We identified pairs that were profitable on *every individual day* (D2, D3, AND D4). These are the most robust — not dependent on any single day's regime:

| Pair | D2 | D3 | D4 | Total |
|---|---|---|---|---|
| MICROCHIP_CIRCLE − PEBBLES_XL | 7,830 | 58,770 | 40,545 | **107,145** |
| SLEEP_POD_POLYESTER − MICROCHIP_TRIANGLE | 11,505 | 22,140 | 26,070 | 59,715 |
| MICROCHIP_OVAL − PEBBLES_XS | 13,345 | 19,750 | 22,930 | 56,025 |
| ROBOT_VACUUMING − SNACKPACK_RASPBERRY | 7,550 | 11,920 | 32,350 | 51,820 |
| PEBBLES_S − PANEL_2X2 | 5,125 | 19,645 | 26,590 | 51,360 |
| ... (8 more pairs) | | | | |
| **Total** | **84,375** | **200,465** | **268,890** | **553,730** |

Note the monotonic improvement: D2 was weakest (rolling window still warming up), D3 was strong, D4 was strongest. This suggested live D5+ performance would be at least as good as D4.

**Every single robust-core pair was cross-category.** Within-category pairs were real but less stable day-to-day.

---

**Next:** [05-bot-forensics.md](05-bot-forensics.md) — Who is actually generating these trades?
