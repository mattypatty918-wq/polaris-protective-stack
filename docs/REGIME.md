# Regime detection

## Live rule stack (simple)
- Efficiency ratio → trend vs range
- ATR vs ATR average → high vs low vol
- EMA 20/50 slope → direction bias

Labels: `low_vol_range`, `high_vol_trend`, `low_vol_trend`, `high_vol_range`

## Advanced (research module)
| Method | Use |
|--------|-----|
| BOCPD | Bayesian online changepoint; spike in run-length=0 mass |
| HMM 2-state EM | Latent low/high vol; transition persistence |
| Hurst R/S | H<0.5 MR tendency; H>0.5 trend |
| Variance ratio | VR<1 MR-ish; VR>1 momentum-ish |
| GMM | Soft clusters on returns |

## Mapping to sleeves
- low_vol_range → arm mean reversion
- high_vol_trend → arm breakout / trend
- BOCPD spike → disarm MR briefly
