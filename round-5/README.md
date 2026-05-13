# Round 5 - 50-Product Research Program

Everything changed. 50 new products in 10 categories of 5 each. All R3/R4 products gone. Position limits dropped from 200 to 10 (a 20× reduction). Counterparty names redacted again. No options - all delta-1.

This folder documents the research program we ran across these 50 products. It's organized as 8 numbered steps, each building on the previous findings.

## The 10 Categories

| Category | Products | Coding |
|---|---|---|
| PEBBLES | XS, S, M, L, XL | Sizes |
| MICROCHIP | CIRCLE, OVAL, SQUARE, RECTANGLE, TRIANGLE | Shapes |
| TRANSLATOR | SPACE_GRAY, ASTRO_BLACK, ECLIPSE_CHARCOAL, GRAPHITE_MIST, VOID_BLUE | Dark colors |
| SNACKPACK | CHOCOLATE, VANILLA, PISTACHIO, STRAWBERRY, RASPBERRY | Flavors |
| ROBOT | VACUUMING, MOPPING, DISHES, LAUNDRY, IRONING | Chores |
| UV_VISOR | YELLOW, AMBER, ORANGE, RED, MAGENTA | Wavelengths |
| SLEEP_POD | SUEDE, LAMB_WOOL, POLYESTER, NYLON, COTTON | Fabrics |
| PANEL | 1X2, 2X2, 1X4, 2X4, 4X4 | Sizes (area-coded) |
| OXYGEN_SHAKE | MORNING_BREATH, EVENING_BREATH, MINT, CHOCOLATE, GARLIC | Flavors |
| GALAXY_SOUNDS | DARK_MATTER, BLACK_HOLES, PLANETARY_RINGS, SOLAR_WINDS, SOLAR_FLAMES | Cosmic events |

## Research Steps

| # | Document | What It Answers |
|---|---|---|
| 01 | [Market scan](01-market-scan.md) | What does each product look like? Which categories have structure? |
| 02 | [PEBBLES constraint](02-pebbles-constraint.md) | Why do PEBBLES products sum to exactly 50,000? |
| 03 | [Methodology war](03-methodology-war.md) | Rolling-z or prev-day-mean? (This decided everything.) |
| 04 | [Pair sweep](04-pair-sweep.md) | Which of the 1,225 possible pairs are profitable? |
| 05 | [Bot forensics](05-bot-forensics.md) | Who is generating the trades? Can we front-run them? |
| 06 | [Portfolio construction](06-portfolio.md) | How to select pairs honestly and avoid selection bias |
| 07 | [Negative results](07-negative-results.md) | What we tried that didn't work (and why) |
| 08 | [Execution constraints](08-execution.md) | The 1k-tick discovery and group-vs-pair architecture |

## Reproducibility

All analysis is reproducible from the 21 Python scripts in [scripts/](scripts/) and 32 CSV outputs in [data/](data/).

---

**Start here:** [01-market-scan.md](01-market-scan.md)
