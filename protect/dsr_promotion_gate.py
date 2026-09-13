"""Bailey-Lopez de Prado Deflated Sharpe helpers + loose/strict promotion gate."""
import math


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p):
    p = min(max(p, 1e-12), 1 - 1e-12)
    a = [2.50662823884, -18.61500062529, 41.39119773534, -25.44106049637]
    b = [-8.47351093090, 23.08336743743, -21.06224101826, 3.13082909833]
    c = [
        0.3374755930061667, 0.9761690190917186, 0.1607979323686185,
        0.0276438810333863, 0.0038405729373609, 0.0003951896511919,
        0.0000321767881768, 0.0000002888167364, 0.0000003960315187,
    ]
    y = p - 0.5
    if abs(y) < 0.42:
        r = y * y
        return (y * (((a[3] * r + a[2]) * r + a[1]) * r + a[0])) / (
            ((((b[3] * r + b[2]) * r + b[1]) * r + b[0]) * r + 1)
        )
    r = p if y > 0 else 1 - p
    s = math.log(-math.log(r))
    t = c[0] + s * (
        c[1]
        + s
        * (
            c[2]
            + s
            * (
                c[3]
                + s
                * (c[4] + s * (c[5] + s * (c[6] + s * (c[7] + s * c[8]))))
            )
        )
    )
    return t if y > 0 else -t


def sr_variance(sr, n, skew=0.0, kurt=3.0):
    return (1.0 + 0.5 * sr * sr - skew * sr + ((kurt - 3.0) / 4.0) * sr * sr) / max(n - 1, 1)


def expected_max_sr(n_trials, sr_var):
    if n_trials <= 1:
        return 0.0
    em = 0.5772156649
    u = norm_ppf(1.0 - 1.0 / n_trials)
    emax_z = (1.0 - em) * u + em * norm_ppf(1.0 - 1.0 / (n_trials * math.e))
    return math.sqrt(max(sr_var, 1e-16)) * emax_z


def deflated_sharpe(sr_hat, n_obs, n_trials=200, skew=0.0, kurt=3.0):
    """DSR = Phi((SR_hat - SR*) / sqrt(V))."""
    if n_obs < 5:
        return None
    v = sr_variance(sr_hat, n_obs, skew, kurt)
    sr_star = expected_max_sr(n_trials, v)
    z = (sr_hat - sr_star) / math.sqrt(v)
    dsr = norm_cdf(z)
    return {
        "sr_hat": sr_hat,
        "n_obs": n_obs,
        "n_trials": n_trials,
        "sr_var": v,
        "sr_star": sr_star,
        "z": z,
        "DSR": dsr,
        "pass_95": dsr > 0.95,
        "pass_50": dsr > 0.5,
    }


def promote_loose(dsr, mc_frac_gt0, mean_exp, worst_dd):
    return bool(
        dsr
        and dsr.get("DSR", 0) > 0.5
        and mc_frac_gt0 >= 0.55
        and mean_exp > 0
        and worst_dd > -0.12
    )


def promote_strict(dsr, mc_sig05, mean_exp):
    return bool(dsr and dsr.get("pass_95") and mc_sig05 and mean_exp > 0)
