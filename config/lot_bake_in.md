# Bake lots = 0.1 into all strategies

## Standard inputs (every EA)
- InpFixedLots = 0.1
- InpRiskPercent = 0.0 (prefer fixed lots until risk engine verified)
- InpMaxLots = 0.5
- Max positions per symbol = 1
- Max total open = 2

## Chart checklist
1. Open EA properties on each chart
2. Set FixedLots / Lots to 0.1
3. Disable money-risk mode if it computes 3.33 lots
4. Recompile if source default is 0.01
5. Close any open volume > 0.5 on Thunderbolt 50k

## Current issue
Demo 5055969871 still had EURUSD 3.33 lots from TS* — that must be closed or reduced; new default does not change open positions.
