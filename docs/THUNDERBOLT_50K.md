# Thunderbolt-style 50k challenge mapping

From challenge card:
- Profit target 4%
- Daily drawdown 3%
- Max drawdown 6%
- Min trading 1 day, time limit 30 days

## Soft guards (must be tighter than firm limits)
- Soft day loss halt: 2.5%
- Soft max DD halt: 5.0%
- Max 2 opens, 1 per symbol
- Max 0.5 lots per position on 50k until validated
- Risk ~0.35% per trade

## Live 50k demo observation (2026-09-15)
Account 5055969871 MetaQuotes-Demo balance 50000
Open: EURUSD sell 3.33 lots + GBPUSD buy 3.33 lots + small ORB positions
**3.33 lots is NOT compliant** with 3%/6% DD budget if stacked stops hit.

## Autonomous loop
1. Overnight WFO+MC+DSR on candidate EAs
2. Promote only passers to `promoted` list
3. Live/challenge accounts load only promoted sleeves
4. Pulse/ThunderboltGuard demotes/halt on DD
5. Anti-stack blocks correlated duplicates
