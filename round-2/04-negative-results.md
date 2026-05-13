# 04 — Negative Results & Lessons Learned

## 1. algov6 Import Dependency

`algov6_round2.py` imported from `algov5.py` — not standalone. IMC requires a single self-contained upload. Cost us time creating an inlined version.

**Lesson:** Every strategy file must be self-contained from the start.

## 2. Pepper Crash Guard — Built but Never Validated

`algov6_round2.py` included a crash guard (`_pepper_risk_state`) that was never tested against a real or synthetic crash. The MC simulator could test this but we never ran it.

**Lesson:** Don't ship safety mechanisms you haven't tested.

## 3. Backtester Rabbit Hole

Spent ~4 hours calibrating the Codex backtester to 0.04% accuracy, only to discover r1bt already handled everything we fixed.

**Lesson:** Audit existing tools before writing fixes.

## 4. No Live Probing on Day 1

We learned from beast's Scrooge discovery but didn't apply it to R2. Got lucky that nothing changed.

## 5. Official Backtester Incompatibility

`prosperity4btest` didn't support R2 data. Slower iteration cycle.

## Round 2 Summary

| Metric | Value |
|---|---|
| Final rank | **#277 globally** |
| Products | Osmium + Pepper (unchanged) |
| Key finding | 64% hidden fill rate → backtester calibration to 0.04% |
| Biggest miss | Not probing live, not validating crash guard |

The R1→R2 rank drop (90→277) was driven by the competitive field improving, not our strategy degrading.

---

**Final Round 2 Result:** Global Rank **#277** — Advanced to Round 3.
