# cryptobot

This repo contains tools for backtesting and running a cryptocurrency trading bot. The bot relies on Binance, so make sure you create a .binance file at the root of the repo, which contains your credentials on 2 lines.

## Setup

Make sure you have Python 3.9 and Pipenv available.

```
pipenv install
pipenv shell
```

## Tests

```
python -m discover
```

## Simulation

```
python simulate.py
```

## Launch bot

With the BTC USDT currency pair:

```
python bot_loop.py -p btcusd
```

Or configure currency pairs in `docker-compose.yml` and `config.json` and launch a Docker container:

```
docker-compose up
```

The published Docker image is designed to run on armv7 architecture. The idea is to keep a Raspberry Pi with 32-bit OS running 24h a day.

## Utilities

Various scripts can be used to communicate with Binance or run analysis

### Simulation with local data

Run simulation:

```
python simulate.py
```

### Retrieve data from binance

```
python dump_historical_klines.py -c BTCUSDT -i 1h -d "2 years ago"
```

### Analyse trades and compare to market

```
python analyse_trades.py -c BTCUSDT -d 2021-01-02
```
