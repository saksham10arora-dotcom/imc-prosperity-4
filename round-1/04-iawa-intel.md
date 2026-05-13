# 04 - iawa / chrispyroberts: Competitive Intelligence Exchange

## The Question

After completing our independent analysis, we reached out to chrispyroberts (username: iawa), a top competitor who had published Prosperity analysis publicly. Goal: cross-validate our bot models and discover blind spots.

## What We Received

### 1. Taker Model Confirmation
Our estimate: Poisson 1/2300 per tick, 50/50 buy/sell, volume Uniform [2, 7].

iawa's response: **"About tight."** Our calibration was correct.

### 2. Inside Bot Offset Correction
We originally measured the inside bot (Bot 3/4) offset as a fixed ±2.5 from wall_mid. iawa revealed it **shifts across days:**

```
offset = round(FV + 2 + k),  where k ∈ [0.3, 0.7]
```

Our 2.5 was an average of the shifting parameter. This explained minor calibration mismatches across days.

### 3. Two Independent Inside Bots
iawa confirmed that splitting the inside-maker into two separate processes (passive + crossed) was correct. Both fire as independent Bernoulli trials per tick, not as a single correlated process. Our volume distribution fit improved after the split.

### 4. Anti-Overfitting MC Trick (Best Takeaway)

1. Calculate each bot parameter separately for each of the 3 training days → get 3 values
2. Fit Normal(mean, std) from those 3 values
3. For each MC simulation, **sample** from that distribution instead of using a fixed number

**Why this matters:** Using a single fixed estimate overfits to the training data. Sampling from Normal(mean, σ) across simulations covers parameter uncertainty naturally.

### 5. Fill Priority (Unanswered)
We asked how fill priority works when multiple participants quote at the same price level. iawa never answered this.

## What We Gave

| Intel Item | Detail |
|---|---|
| Bot model confirmation | Our 6-bot decomposition matched iawa's independently |
| Asymmetry signal | Level asymmetry predicts PEPPER direction at 91% accuracy |
| Cross-asset correlation | Osmium ⊥ Pepper (correlation < 0.02 all days) |

## Impact

The exchange didn't produce direct alpha but provided **confidence calibration** - knowing our bot models were independently validated gave us assurance to ship without second-guessing.

---

**Next:** [05-mc-simulator.md](05-mc-simulator.md) - Building a synthetic market from calibrated parameters.
