"""Polaris Pulse - prop account detect & heal (no secrets)."""
from pathlib import Path
import json
from datetime import datetime, timezone

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

PROFILES = {
    "TRADINGCOM_10K": {
        "day_loss_pct": 2.0, "hard_dd_pct": 10.0, "soft_dd_pct": 5.0,
        "max_open": 2, "max_lots": 0.08, "risk_pct": 0.4,
    },
    "GENERIC_PROP": {
        "day_loss_pct": 3.0, "hard_dd_pct": 8.0, "soft_dd_pct": 4.0,
        "max_open": 3, "max_lots": 0.1, "risk_pct": 0.5,
    },
    "DEMO_VALIDATE": {
        "day_loss_pct": 5.0, "hard_dd_pct": 15.0, "soft_dd_pct": 8.0,
        "max_open": 3, "max_lots": 0.08, "risk_pct": 0.5,
    },
}

# Optional: list of logins that must stay locked (fill locally, never commit real IDs if public)
FORCE_LOCK_LOGINS = set()


def detect_profile(login, balance, server=""):
    server = (server or "").lower()
    if "trading.com" in server:
        return "TRADINGCOM_10K"
    if balance and 5000 <= balance <= 15000:
        return "TRADINGCOM_10K"
    if balance and balance > 50000:
        return "DEMO_VALIDATE"
    return "GENERIC_PROP"


def run(state_path=None, out_path=None):
    if mt5 is None:
        raise RuntimeError("MetaTrader5 package required on the trading host")
    mt5.initialize()
    ai = mt5.account_info()
    if not ai:
        print("NO_ACCOUNT")
        return None
    login = ai.login
    bal = float(ai.balance)
    eq = float(ai.equity)
    server = getattr(ai, "server", "") or ""
    profile_name = detect_profile(login, bal, server)
    prof = PROFILES[profile_name]

    state_path = Path(state_path or "runtime/polaris_pulse_state.json")
    out_path = Path(out_path or "runtime/polaris_pulse_status.json")
    state_path.parent.mkdir(parents=True, exist_ok=True)

    state = {}
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if state.get("day") != today:
        state = {"day": today, "day_start_eq": eq, "peak_eq": eq, "heal_level": 0}
    state["peak_eq"] = max(float(state.get("peak_eq") or eq), eq)
    day_start = float(state.get("day_start_eq") or eq)
    day_loss_pct = 100.0 * (eq - day_start) / day_start if day_start else 0
    dd_pct = 100.0 * (eq - state["peak_eq"]) / state["peak_eq"] if state["peak_eq"] else 0

    heal = 0
    if dd_pct <= -prof["hard_dd_pct"] or day_loss_pct <= -prof["day_loss_pct"]:
        heal = 2
    elif dd_pct <= -prof["soft_dd_pct"] or day_loss_pct <= -prof["day_loss_pct"] * 0.7:
        heal = 1

    if login in FORCE_LOCK_LOGINS:
        heal = 2

    if heal >= 2:
        allow_new, size_mult, profile = 0, 0.0, "POLARIS_PULSE_HARD_HALT"
    elif heal == 1:
        allow_new, size_mult, profile = 1, 0.35, "POLARIS_PULSE_SOFT_HEAL"
    else:
        allow_new, size_mult, profile = 1, 1.0, "POLARIS_PULSE_OK"

    lots = min(prof["max_lots"], max(0.01, eq * prof["risk_pct"] / 100.0 / 1000.0))
    if heal >= 1:
        lots = min(lots, prof["max_lots"] * 0.5)
    if heal >= 2:
        lots = 0.0

    gate = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "product": "Polaris Pulse",
        "login": login,
        "balance": bal,
        "equity": eq,
        "server": server,
        "detected_profile": profile_name,
        "heal_level": heal,
        "day_loss_pct": round(day_loss_pct, 3),
        "dd_pct": round(dd_pct, 3),
        "allow_new": allow_new,
        "size_mult": size_mult,
        "max_open": prof["max_open"],
        "max_lots": round(lots, 2),
        "profile": profile,
    }
    state["heal_level"] = heal
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    out_path.write_text(json.dumps(gate, indent=2), encoding="utf-8")
    print(json.dumps(gate))
    mt5.shutdown()
    return gate


if __name__ == "__main__":
    run()
