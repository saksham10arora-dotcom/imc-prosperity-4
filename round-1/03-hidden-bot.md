# 03 — The Hidden Bot: Alpha in Empty Books

## The Question

After identifying all visible bots from historical data (Bots 1–5), were there any bots we couldn't see? The historical data showed a market that never went to zero on either side — but what happens when one side is cleared?

## How It Was Found

**Historical data couldn't reveal it.** The wall bots post 10–30 units at ±8 and ±10.5. With an 80-unit position limit, clearing one side of the book requires aggressive buying across several ticks — a state that never occurs in the passive CSV replay.

The only way to discover this was live probing: submit a strategy that deliberately eats one side of the book and observe what happens.

## The Mechanism

When one side of the order book is completely emptied by a player:

- **Asks empty:** A hidden bot appears and bids at `FV + ~100`
- **Bids empty:** A hidden bot appears and asks at `FV - ~100`

The offset is approximately ±100 but slightly randomized (live data showed fills at 10100 and 10096).

## Why We Missed It

1. **Not in historical data.** The empty-book state never occurs in the CSV replay — both sides always have wall bot orders.
2. **Requires live probing.** You must submit code to the live platform to trigger the state.
3. **No statistical signal.** No amount of data analysis on the historical CSV would have revealed this. It only exists in live.

## The Impact

| Metric | Without Hidden Bot | With Hidden Bot |
|---|---|---|
| Live PnL | 10,700 | **12,200** |
| Improvement | — | **+1,500 (+14%)** |

The exploit contributed ~1.5K of the final 12.2K live score. Implementation required reserving 15 units of position capacity (soft limit 65 instead of 80) to leave room for fills.

## Lesson Learned

**Some edges only exist in live.** All our data analysis (V13–V16, asymmetry signal, bot sniping) produced zero incremental alpha. The hidden bot — discovered only through live probing — was worth +1.5K.

**Implication for future rounds:** Submit test strategies on Day 1 to probe for hidden bots. Don't wait for the data to tell you everything.

---

**Next:** [04-iawa-intel.md](04-iawa-intel.md) — What we learned from networking with a top competitor.
