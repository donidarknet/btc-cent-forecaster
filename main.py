#!/usr/bin/env python3
"""BTC cent forecast: median 240-minute ahead price for btc-cent-forecast-01.

Reads every *.in in $MAKEFUN_INPUT_DIR (else /input), writes <id>.out to
$MAKEFUN_OUTPUT_DIR (else /output) as {"forecasts": [{"case": id, "price": x}]}.

Model: the score is mean absolute error in cents, so the optimal point
forecast is the conditional median of the price 240 minutes ahead. We
estimate it as last_price * exp(median 240-minute log-return), where the
median is taken over overlapping 240-minute windows in the last 12 hours
of the case, sampled every 5 minutes, shrunk 0.5 towards 0. A pure
persistence forecast is the special case of a zero median return; the
median return only moves the guess when the recent 4-hour moves agree on
a direction. No drift extrapolation from short-term slopes: a trend fitted
on the last hour extrapolates noise and scored worse in backtests.

Stdlib only, deterministic, offline.
"""

import json
import math
import os
from pathlib import Path

HORIZON = 240
WINDOW_MIN = 720
STEP_MIN = 5
SHRINK = 0.5


def median(values):
    s = sorted(values)
    n = len(s)
    if n == 0:
        return 0.0
    mid = n // 2
    if n % 2:
        return s[mid]
    return 0.5 * (s[mid - 1] + s[mid])


def forecast(prices):
    last = prices[-1]
    if len(prices) <= HORIZON:
        return last
    window = prices[-WINDOW_MIN:] if len(prices) > WINDOW_MIN else prices
    logs = [math.log(p) for p in window if p > 0]
    if len(logs) <= HORIZON:
        return last
    moves = [logs[i] - logs[i - HORIZON] for i in range(HORIZON, len(logs), STEP_MIN)]
    if not moves:
        return last
    drift = SHRINK * median(moves)
    guess = last * math.exp(drift)
    if not (0 < guess < 10_000_000):
        return last
    return guess


def main():
    input_dir = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(input_dir.glob("*.in")):
        case = json.loads(path.read_text(encoding="utf-8"))
        markets = case["markets"]
        if len(markets) != 1:
            raise ValueError(f"{path.name} does not hold exactly one market")
        price = forecast(markets[0]["prices"])
        out = {"forecasts": [{"case": case["case"], "price": price}]}
        (output_dir / f"{path.stem}.out").write_text(json.dumps(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
