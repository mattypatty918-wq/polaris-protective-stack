# Backtest overfitting risks

## Main risks
- Multiple testing without deflation
- Lookahead / same-bar leakage
- No purge/embargo between train and test
- Reporting in-sample Sharpe only
- Few trades + extreme Sharpe
- Ignoring spread and slippage
- Regime mismatch (fit in range, trade in trend)
- Parameter islands
- Reusing the same OOS set until it "passes"

## Mitigations in this stack
- Walk-forward folds
- Monte Carlo path / Sharpe distribution
- Expectancy + Sharpe floor + drawdown caps
- Reject absurd Sharpe with tiny trade counts
- Cost proxy in sims
- Deflated Sharpe (Bailey & Lopez de Prado)
- Demo forward before any prop/live unlock
