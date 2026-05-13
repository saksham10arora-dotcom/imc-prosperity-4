# 03 — The Dumb Bot: Hidden Alpha in Empty Books

## The Question

After identifying all visible bots from historical data (Bots 1–5), were there any bots we couldn't see? The historical data showed a market that never went to zero on either side — but what happens when one side is cleared?

## How It Was Found

**We didn't find it. beast did.**

 **submit a strategy designed to eat one side of the order book entirely, then observe what happens in live.**

This is standard practice for experienced Prosperity players. In historical data, both sides of the book always have orders (from the wall bots), so the empty-book state never occurs. The only way to trigger it is to consume every ask (or every bid) in a live submission.

## The Mechanism

When one side of the order book is completely emptied by a player:

- **Asks empty:** A hidden bot appears and bids at `FV + ~100`
- **Bids empty:** A hidden bot appears and asks at `FV - ~100`

The offset is approximately ±100 but may be slightly randomized (live data showed fills at 10100 and 10096).

## Why We Missed It

1. **Not in historical data.** The wall bots post 10–30 units at ±8 and ±10.5. With an 80-unit position limit, a player can't clear 40+ units of depth in a single tick. But across several ticks, aggressive buying CAN empty the ask side.
2. **Requires live probing.** The historical CSV replay is purely observational — no player-driven orders. You must submit code to the live platform to trigger the empty-book state.
3. **Prior-year knowledge helps.** beast knew to look for this because similar hidden bots existed in Prosperity 2 and 3.

## The Impact

| Metric | Without Dumb Bot | With Dumb Bot |
|---|---|---|
| Live PnL | 10,700 | **12,200** |
| Improvement | — | **+1,500 (+14%)** |

The Dumb Bot exploit contributed ~1.5K of the final 12.2K live score. Implementation required reserving 15 units of position capacity (soft limit 65 instead of 80) to leave room for Dumb Bot fills.

## Lesson Learned

**The biggest PnL gain in Round 1 came from a competitor tip, not from data analysis.** All our research (V13–V16, asymmetry signal, bot sniping) produced zero incremental alpha. The Dumb Bot discovery — found by probing live, not by analyzing CSVs — was worth +1.5K.

**Implication for future rounds:** Submit test strategies on Day 1 to probe for hidden bots. Don't wait for the data to tell you everything — some edges only exist in live.

---

**Next:** [04-iawa-intel.md](04-iawa-intel.md) — What we learned from networking with a top competitor.
