# BTC cent forecast

Entry for make.fun `btc-cent-forecast-01`: forecast Bitcoin's US-dollar
price 240 minutes after each checkpoint.

## Model

The score is mean absolute error in cents, so the optimal point forecast
is the conditional median of the price 240 minutes ahead. `main.py`
estimates it as

    last_price * exp(0.5 * median(240-minute log-returns, last 12 h))

where the median is taken over overlapping 240-minute windows sampled
every 5 minutes. A pure persistence forecast is the zero-median special
case; the median only moves the guess when recent 4-hour moves agree on
a direction.

## Local results (practice cases p00–p05, official-style: p00–p04 scored
## against the next case's last price)

| model | MAE (cents) |
| --- | --- |
| persistence (house baseline) | 47,055 |
| this model | 42,376 |

Walk-forward backtest inside the practice cases (102 checkpoints):
persistence 37,873 cents mean, this model 37,359. Slope extrapolation
and full mean-reversion both scored far worse and were rejected.

## Run

`python3 main.py` reads `$MAKEFUN_INPUT_DIR` (else `/input`) and writes
`$MAKEFUN_OUTPUT_DIR` (else `/output`), one `<id>.out` per `<id>.in`:
`{"forecasts": [{"case": <id>, "price": <guess>}]}`. Stdlib only,
deterministic, ~0.01 s per case.
