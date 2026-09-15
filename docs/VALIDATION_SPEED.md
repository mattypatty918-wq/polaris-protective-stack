# Speed up strategy validation

## Ranked levers (fastest first)
1. **Fewer symbols first** — EURUSD + GBPUSD + USDJPY only for pass/fail, expand later
2. **Higher TFs only** — H1/H4 not M1/M5 (far fewer bars)
3. **Kill-fast gates** — drop if OOS exp<=0 or WR random after first window; don't full MC
4. **Coarse grid then fine** — 5x5 params then refine winners only
5. **Parallel Strategy Tester agents** — multiple local agents / cloud agents
6. **Purged walk-forward 3 windows** not 10 for screening; 10 only for finalists
7. **MC 200 paths screen / 2000 final** — not 10k on every idea
8. **Shared feature cache** — precompute ATR/RSI once per symbol-TF
9. **Demote free-robot candle packs** unless they pass kill-fast in <2 min
10. **Promote list only** loads on challenge — research stays on demo

## Overnight job shape
- Phase A (2h): all candidates kill-fast H1
- Phase B (4h): survivors WFO 3-fold H1/H4
- Phase C (2h): MC+DSR finalists
- Output: promoted_strategies.json
