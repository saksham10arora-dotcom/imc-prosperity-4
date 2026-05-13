# IMC Prosperity 4 - Research Archive

> **#154 worldwide · #18 India · Top 1% out of 18,803 teams across 117 countries**

This repository documents the complete research process behind our performance in the IMC Prosperity 4 algorithmic trading competition. It is organized chronologically - each step explains *what we investigated*, *what we found*, and *why it mattered* for the next step.

**Team:** Alex Zhang · Annanye Naik · Saksham Arora · Zain Hirji

---

## How to Read This Repo

The research is organized into three rounds. Each round folder contains numbered markdown files that tell the story in order. Read them sequentially — each finding builds on the last.

```
round-3/                    R3: Market microstructure + options pricing
  ├── 01-hydrogel.md        The ±8 bot discovery
  ├── 02-velvetfruit.md     Dual-role asset analysis  
  └── 03-options.md         Flat vol smile + BS architecture

round-4/                    R4: Named counterparty forensics
  ├── 01-counterparty.md    Mark 38/14/22/01 identification
  └── 02-vol-surface.md     Catching agent errors on IV calibration

round-5/                    R5: 50-product research program (the big one)
  ├── 01-market-scan.md           Pass-1: scan all 50 products
  ├── 02-pebbles-constraint.md    The sum=50,000 discovery
  ├── 03-methodology-war.md       Rolling-z vs prev-day-mean (2× OOS)
  ├── 04-pair-sweep.md            1,225-pair exhaustive sweep
  ├── 05-bot-forensics.md         Reverse-engineering the simulator
  ├── 06-portfolio.md             Honest OOS portfolio construction
  ├── 07-negative-results.md      What didn't work (and why)
  ├── 08-execution.md             1k-tick discovery + group vs pair
  ├── scripts/                    21 analysis scripts (reproducible)
  │   ├── README.md               What each script does
  │   ├── 01_constraints.py → 21_trade_time_pnl.py
  │   └── lib.py                  Shared data loaders
  └── data/                       32 CSV output files
      └── README.md               Column descriptions
```

---

## The Arc in 60 Seconds

**Round 3** - We discovered that HYDROGEL_PACK had a symmetric bot trading at exactly ±8 ticks from fair value. We undercut it at ±7. For options, we proved the vol smile was flat (R² = 0.02) and used single-vol Black-Scholes. Result: **#84 globally, #7 India.**

**Round 4** - Counterparty names appeared. We identified Mark 38 as the ±8 bot, Mark 14 as the passive market-maker, Mark 22 as a sporadic ±4 undercut. For vouchers, Mark 22 was a persistent seller and Mark 01 the persistent buyer — we stepped inside Mark 01's bid. A sub-agent twice produced wrong IV calibration; our independent review process caught both errors before they shipped.

**Round 5** - Everything reset. 50 new products, position limits dropped 20×, counterparty names redacted again. We ran a 21-script research program that produced three headline findings:

1. **PEBBLES sum = 50,000 ± 2.8** - a hard generator constraint across 30,000 ticks
2. **Rolling-z beats prev-day-mean by 2× out-of-sample** - resolved a methodology war that was blocking the entire strategy
3. **100% of trades came from exactly 3 coordinated basket bots** — uninformed, random flow. No informed counterparty exists in R5.

We swept all **1,225 possible product pairs**, found **471 profitable OOS** (87% cross-category), built a 24-pair portfolio, then caught our own selection bias and honestly revised the headline from 552k down to **~155k after realistic fills**.

---

## Score Breakdown

| Phase | Score (XIRECs) |
|---|---|
| Phase 1 (R1 + R2) | 485,221 |
| Phase 2 / GOAT (R3 + R4 + R5) | 531,123 |

---

## Technical Details

- **Language:** Python (stdlib + numpy)
- **Backtester:** `prosperity4bt` community backtester
- **Research tools:** Custom bot fingerprinting (`tools/bots.py`), BS pricer + IV inverter (`tools/options.py`)
- **Verification:** Every major claim independently reviewed before shipping. Two IV calibration errors caught and corrected.
- **Total research scripts:** 21 numbered Python files producing 32 CSV outputs

---

*First-time competitors. Built research infrastructure from scratch in 5 weeks.*
