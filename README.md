# Polaris Protective Stack

Public export of the **protective / risk / adaptive** layer used with the PhD thesis MT5 workflow.

**Not financial advice.** Demo first. No API tokens, account numbers, or broker credentials are included.

## Public URL
https://github.com/mattypatty918-wq/polaris-protective-stack

## Components

| Module | Role |
|--------|------|
| **Polaris Pulse** | Prop-style detect & heal (day loss, DD, size cut, halt) |
| **Polaris Fade** | Regime-aware mean-reversion entries (companion) |
| **Adaptive control** | Regime arms, sizing, correlation soft-block, session, spreads |
| **Position watchdog** | Adverse-score exit suggestions |
| **Exit catalog** | ATR SL, trail, partial TP, session flat, adverse score |
| **Promotion gate** | Deflated Sharpe (Bailey–López de Prado) + MC Sharpe |
| **Regime advanced** | BOCPD, HMM, Hurst, variance ratio, GMM |
| **Microstructure policy** | Tick volume, spread, session liquidity proxies |

## Safety defaults
- Hard stop always on (ATR-based)
- Competition / prop accounts: prefer **lock new trades** until demo OOS evidence
- Never commit live API keys to git

## Quick layout
```
protect/
  polaris_pulse.py
  adaptive_control.py
  position_watchdog.py
  dsr_promotion_gate.py
  regime_advanced.py
mql5/
  PolarisPulse.mq5
  PolarisFade.mq5
config/
  exit_strategy_catalog.json
  microstructure_policy.json
  promotion_gate_policy.json
docs/
  OVERFITTING.md
  DSR_MATH.md
  REGIME.md
```

## License
MIT — use at your own risk.
