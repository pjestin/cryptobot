# cryptobot

This repo contains tools for backtesting and running a cryptocurrency trading bot. The bot relies on Binance, so make sure you create a .binance file at the root of the repo, which conatins your credentials on 2 lines.

## Setup

Make sure you have Python 3.7 available. 

```
python3 -m venv env
source env/bin/activate
pip install -r requirements-dev.txt
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
bot_loop.py -p btcusd
```

Or launch a Docker container:

```
docker build -t cryptobot .
docker run -d --name cryptobot-btcusdt -v ~/src/cryptobot:/app/cryptobot -e command="bot_loop.py -p btcusdt" cryptobot
```
