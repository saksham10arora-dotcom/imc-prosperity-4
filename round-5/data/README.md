# Data Outputs

32 CSV files produced by the 21 analysis scripts. These contain all derived quantitative results referenced in the research documents.

## Key Files

| File | What it contains | Used in |
|---|---|---|
| `06_cross_category_oos.csv` | **Master file.** All 1,225 pairs with in-sample PnL, D4 OOS PnL, win rate, trade count. | Steps 04, 06 |
| `01_constraints.csv` | Sum statistics for all 10 categories (mean, std, range). PEBBLES std=2.8. | Step 02 |
| `02_methodology.csv` | Head-to-head comparison of prev-day-mean vs rolling-z for 100 within-category pairs. | Step 03 |
| `05_microstructure.csv` | ac1_dmid and ac1_dmicro for all 50 products, per-day and aggregate. | Step 01 |
| `16_portfolio_A.csv` | The honest OOS portfolio: 24 pairs selected by D2+D3 rank, frozen, tested on D4. | Step 06 |
| `21_roundtrips_tagged.csv` | Every round-trip trade tagged with hold time, PnL, and basket-tick overlap. | Step 07 |

## Bot Forensics Files

| File | Contents |
|---|---|
| `18_aggressor_imbalance.csv` | Buy/sell skew per basket per day |
| `18_day_skew.csv` | Per-product daily aggressor skew |
| `18_informed_rate.csv` | Pearson(side, next-tick dmid) per product |
| `18_qty_modes.csv` | Trade quantity distribution by product |
| `18_size_aggressor.csv` | Aggressor side by trade size |
| `18_tick_burst.csv` | Basket tick clustering analysis |
| `19_side_correlation.csv` | Cross-product aggressor side correlation (proves basket coordination) |

## Grid Search Files

| File | Contents |
|---|---|
| `03_window_sensitivity.csv` | PnL by window size for top pairs |
| `11_z_grid.csv` | Entry × exit threshold grid (30 combinations) |
| `window_grid_search.csv` | Full w × z grid for 1k-tick optimization |

## Portfolio Construction Files

| File | Contents |
|---|---|
| `08_portfolio_K1.csv` | K=1 greedy portfolio (each product in ≤1 pair) |
| `08_portfolio_K2.csv` | K=2 greedy portfolio (each product in ≤2 pairs) |
| `09_day_stability.csv` | Per-day PnL for the robust-core pairs |
| `10_fill_cost.csv` | Mid-fill vs bid/ask-fill PnL comparison |
| `16_proper_oos_pairs.csv` | All 1,225 pairs with per-day PnL breakdown |
| `17_per_day_pairs.csv` | Extended per-day analysis for stability filtering |
| `17_strategy_compare.csv` | 7 selection rules compared on OOS PnL |
