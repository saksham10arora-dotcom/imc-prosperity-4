# Analysis Scripts

21 numbered Python scripts that produced every quantitative finding in the research. Each script reads raw price/trade CSVs and outputs results to `../data/`.

## Dependencies

- Python 3.10+
- numpy, pandas
- `lib.py` (shared data loaders, in this directory)

## Script Index

| # | Script | What it does | Key output |
|---|---|---|---|
| 01 | `01_constraints.py` | Tests sum constraints across all 10 categories. Discovers PEBBLES sum=50,000±2.8. Runs 4-of-5 OLS regression. | `01_constraints.csv`, `01_4of5_ols.csv` |
| 02 | `02_methodology.py` | Head-to-head OOS test: prev-day-mean vs rolling-z (window=2000). Train on D2+D3, trade D4. Rolling-z wins 2×. | `02_methodology.csv` |
| 03 | `03_window_sensitivity.py` | Tests windows {200, 500, 1000, 2000, 5000, 8000} on top pairs. PEBBLES prefers w=200 (11× better than w=8000). | `03_window_sensitivity.csv` |
| 04 | `04_cross_category.py` | Exhaustive sweep of all 1,225 unordered pairs (in-sample, days 2–4 concatenated). | `04_cross_category.csv` |
| 05 | `05_robot_microstructure.py` | ac1 forensics on all 50 products. Confirms IRONING ac1=-0.125 is quote-driven (not bid-ask bounce). Discovers DISHES, OXYGEN_SHAKE_EVENING_BREATH. | `05_microstructure.csv` |
| 06 | `06_cross_category_oos.py` | Full 1,225-pair sweep with proper OOS (train D2+D3, test D4). Master file: 471 profitable pairs, 87% cross-category. | `06_cross_category_oos.csv` |
| 07 | `07_flow_imbalance.py` | Tests whether OBI or trade-flow predicts next-tick mid moves. OBI corr peaks at +0.13 for SNACKPACK; trade-flow ≈ 0. | `07_flow.csv` |
| 08 | `08_portfolio_greedy.py` | Greedy K=1 and K=2 portfolio construction with position-limit conflict resolution. | `08_portfolio_K1.csv`, `08_portfolio_K2.csv` |
| 09 | `09_day_stability.py` | Per-day PnL breakdown for the K=1 portfolio. Identifies the 13-pair "robust core" (positive every day). | `09_day_stability.csv` |
| 10 | `10_fill_cost.py` | Replaces mid-fills with realistic bid/ask crossings. Average haircut: 22%. Only 1/23 pairs flips negative. | `10_fill_cost.csv` |
| 11 | `11_z_threshold_grid.py` | Grid search: entry ∈ {1.0–2.5}, exit ∈ {0.0–0.75}. Optimum: entry=1.5, exit=0.3. Mean-cross exit is catastrophic. | `11_z_grid.csv` |
| 12 | `12_cointegration_walkforward.py` | Tests β-cointegration (Engle-Granger) vs raw 1:1 spread. β-fitting is worse for 21/23 pairs. | `12_cointegration.csv` |
| 13 | `13_three_leg.py` | For each pair, searches for optimal 3rd leg. 3-leg PnL = 975k vs 560k for 2-leg, but uses 50% more capacity. | `13_three_leg.csv` |
| 14 | `14_time_of_day.py` | Buckets ticks into 20 time zones. No exploitable intraday pattern. | `14_time_of_day.csv`, `14_product_buckets.csv` |
| 15 | `15_obi_filter.py` | Tests OBI as entry filter. Win rate +1–4pp but trade count drops more. Net negative vs unfiltered baseline. | `15_obi_filter.csv` |
| 16 | `16_proper_oos_portfolio.py` | Proper OOS portfolio: rank by D2+D3 only, freeze, test on D4. Corrects the 552k→198k selection bias. | `16_proper_oos_pairs.csv`, `16_portfolio_A.csv` |
| 17 | `17_stability_filter.py` | Compares 7 portfolio selection rules. Simple IS-rank is best; stability filters don't add value. | `17_per_day_pairs.csv`, `17_strategy_compare.csv` |
| 18 | `18_bot_behavior.py` | Bot fingerprinting: quantity modes, aggressor skews, informed-rate tests. Discovers 3-basket structure. | `18_*.csv` (6 files) |
| 19 | `19_bot_coordination.py` | Discovers the three baskets by analyzing timestamp coincidence. Verifies 100% coverage. | `19_side_correlation.csv` |
| 20 | `20_basket_implications.py` | Tests bot informedness (Pearson=0.015), common-factor decomposition, signal locations (94% on quiet ticks). | `21_per_pair_basket_share.csv` |
| 21 | `21_trade_time_pnl.py` | Hold-time analysis. Trades held >500 ticks are net losers. Suggests hard time-stop. | `21_roundtrips_tagged.csv` |

## How to Run

Each script is standalone (imports only `lib.py` and standard libraries). They expect price/trade CSVs in a `data/` directory. Example:

```bash
python 01_constraints.py
# → writes output/01_constraints.csv
```

Note: The raw price/trade data files from the competition are not included in this repository (they are proprietary to IMC). The output CSVs contain all derived results.
