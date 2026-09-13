"""Position watchdog - adverse score exit suggestions (log-only safe default)."""
from pathlib import Path
import json
from datetime import datetime, timezone

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

RT = Path("runtime")
STATE = RT / "position_watchdog_state.json"
LOG = RT / "position_watchdog.log"


def log(msg):
    RT.mkdir(parents=True, exist_ok=True)
    line = datetime.now(timezone.utc).isoformat() + " " + str(msg)
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def rsi(symbol, tf, n=14):
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, n + 30)
    if rates is None or len(rates) < n + 2:
        return 50.0
    closes = [r["close"] for r in rates]
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    ag = sum(gains[-n:]) / n
    al = sum(losses[-n:]) / n
    return 100 - (100 / (1 + ag / (al + 1e-12)))


def ema(symbol, tf, n):
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, n * 3)
    if rates is None or len(rates) < n:
        return None
    closes = [float(r["close"]) for r in rates]
    k = 2 / (n + 1)
    e = closes[0]
    for x in closes[1:]:
        e = x * k + e * (1 - k)
    return e


def adverse_score(side, symbol, tf):
    r = rsi(symbol, tf)
    e20 = ema(symbol, tf, 20)
    e50 = ema(symbol, tf, 50)
    tick = mt5.symbol_info_tick(symbol)
    if not tick or e20 is None or e50 is None:
        return 0.0
    px = tick.bid if side == "long" else tick.ask
    score = 0.0
    if side == "long":
        if r > 55:
            score += 0.25
        if r > 65:
            score += 0.2
        if e20 < e50:
            score += 0.25
        if px < e20:
            score += 0.15
    else:
        if r < 45:
            score += 0.25
        if r < 35:
            score += 0.2
        if e20 > e50:
            score += 0.25
        if px > e20:
            score += 0.15
    hr = datetime.now(timezone.utc).hour
    if hr in (21, 22, 23, 0, 1):
        score += 0.15
    return max(0.0, min(1.0, score))


def main(auto_close=False):
    if mt5 is None:
        raise RuntimeError("MetaTrader5 package required")
    mt5.initialize()
    ai = mt5.account_info()
    login = ai.login if ai else None
    positions = list(mt5.positions_get() or [])
    state = {}
    if STATE.exists():
        try:
            state = json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            state = {}
    streaks = state.get("streaks", {})
    report = {"ts": datetime.now(timezone.utc).isoformat(), "login": login, "positions": []}
    for p in positions:
        sym = p.symbol
        side = "long" if p.type == mt5.ORDER_TYPE_BUY else "short"
        score = adverse_score(side, sym, mt5.TIMEFRAME_H1)
        key = str(p.ticket)
        st = int(streaks.get(key, 0))
        st = st + 1 if score >= 0.7 else 0
        streaks[key] = st
        action = "hold"
        if st >= 3:
            action = "suggest_exit"
        rec = {
            "ticket": int(p.ticket),
            "symbol": sym,
            "side": side,
            "volume": float(p.volume),
            "profit": float(p.profit),
            "adverse_score": round(score, 3),
            "streak": st,
            "action": action,
        }
        report["positions"].append(rec)
        log(rec)
        # auto_close left False by default for safety
    state["streaks"] = streaks
    state["last"] = report
    RT.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    (RT / "position_watchdog_last.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    mt5.shutdown()


if __name__ == "__main__":
    main(auto_close=False)
