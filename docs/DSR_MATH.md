# Deflated Sharpe Ratio (Bailey & Lopez de Prado)

## Formula

1. Estimate `SR_hat` from OOS returns.
2. Variance of SR estimator (non-normal correction):

```
V(SR) = (1 + 0.5*SR^2 - skew*SR + ((kurt-3)/4)*SR^2) / (n-1)
```

3. Expected maximum null Sharpe given `N` trials:

```
SR* = sqrt(V) * E[max of N standard normals]
```

4. Deflated Sharpe:

```
DSR = Phi( (SR_hat - SR*) / sqrt(V) )
```

Interpreted as: probability true SR exceeds the null after selection bias.

## Suggested gates
- Loose: DSR > 0.5, MC P(SR>0) >= 0.55, exp > 0, DD > -12%
- Strict: DSR > 0.95 and MC sign-null p < 0.05

Reference: Bailey DH, Lopez de Prado M. *The Deflated Sharpe Ratio*.
