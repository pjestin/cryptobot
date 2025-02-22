#! /usr/bin/env python3
# coding: utf-8

import time
import argparse
import json
import logging
from datetime import datetime, timedelta

from interface.binance_io import BinanceInterface
from interface.config import Config

STATE_FILE = "state/{}.json"
COMMISSION = 0.001
N_REF = 150


def save_state(profile_name, state):
    try:
        with open(STATE_FILE.format(profile_name), "w") as f:
            json.dump(state, f)
    except Exception as e:
        logging.error(f"Unable to write state file: {e}")


def load_state(profile_name):
    try:
        with open(STATE_FILE.format(profile_name), "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Unable to load state file: {e}")
        return None


def probe_and_act(strat, binance, state, klines):
    previous_price = state["previous_price"]
    acquired = state["acquired"]
    quantity = state["quantity"]
    buy_quantity = state["buy_quantity"]
    commission = state["commission"]
    profit = state["profit"]
    simulate = state["simulate"]
    symbol = state["symbol"]

    action = strat.decide_action(klines, acquired)
    price = klines[-1].close_price

    # Buy or sell
    if not acquired and action.is_buy():
        buy_quantity = float("%.3g" % quantity)
        if not simulate:
            order = binance.create_order(
                is_buy=True, quantity=buy_quantity, symbol=symbol
            )
            price = float(order["fills"][0]["price"])
        logging.info("Buying {} at {}; profit: {}".format(buy_quantity, price, profit))
        state["previous_price"] = price
        state["nb_transactions"] += 1
        state["buy_quantity"] = buy_quantity
        state["acquired"] = (1 - commission) / price
        state["profit"] -= 1.0
    elif acquired and action.is_sell():
        if not simulate:
            order = binance.create_order(
                is_buy=False, quantity=buy_quantity, symbol=symbol
            )
            price = float(order["fills"][0]["price"])
        logging.info("Selling {} at {}; profit: {}".format(buy_quantity, price, profit))
        state["previous_price"] = price
        state["nb_transactions"] += 1
        state["buy_quantity"] = None
        state["acquired"] = None
        state["profit"] += (1 - commission) * acquired * price


def run(params):
    state = load_state(params["profile_name"])

    period = params["period"]
    symbol = params["symbol"]
    interval = params["interval"]

    binance = BinanceInterface()

    last_trade = binance.last_trade(symbol)
    logging.info("Last trade in this currency pair: {}".format(last_trade))
    acquired_price = last_trade.price if last_trade and last_trade.is_buy else None
    buy_quantity = (
        float("%.3g" % (last_trade.quantity))
        if last_trade and last_trade.is_buy
        else None
    )
    start_price = binance.last_price(symbol)

    from strategy.avg_log_ratio import KlinesAvgLogRatioStrategy

    strat = KlinesAvgLogRatioStrategy()

    if not state:
        state = {
            "profit": -1.0 if acquired_price else 0.0,
            "previous_price": acquired_price if acquired_price else float("inf"),
            "nb_transactions": 0,
            "acquired": 1.0 / acquired_price if acquired_price else None,
            "buy_quantity": buy_quantity,
            "start_price": start_price,
        }
        state = {**params, **state}

    i = 0
    while True:
        i += 1
        begin_time = time.time()

        klines = binance.get_klines(limit=N_REF, interval=interval, symbol=symbol)

        if not klines:
            logging.error("Could not retrieve klines")
            continue

        price = klines[-1].close_price
        logging.info(
            "Run {}; profit: {}; transactions: {}; price ratio to previous: {}; market: {}".format(
                i,
                state["profit"],
                state["nb_transactions"],
                price / state["previous_price"],
                price / state["start_price"] - 1,
            )
        )
        probe_and_act(strat, binance, state, klines)

        save_state(params["profile_name"], state)

        # Sleep if duration was shorter than period
        duration = time.time() - begin_time
        if duration < period:
            time.sleep(period - duration)


def read_profile(profile_name):
    if not profile_name:
        raise EnvironmentError("Profile name was not specified")
    return Config().profile_config(profile_name)


def main():
    parser = argparse.ArgumentParser(description="Cryptocurrency trading bot")
    parser.add_argument(
        "-s", "--simulate", help="Do not make order, simulate only", action="store_true"
    )
    parser.add_argument("-p", "--profile", help="Profile name")
    args = parser.parse_args()

    log_format = "%(asctime)-15s %(message)s"
    logging.basicConfig(format=log_format, level=logging.DEBUG)

    config = Config()
    profile = config.profile_config(args.profile)
    params = {
        "commission": COMMISSION,
        "simulate": args.simulate,
        "symbol": profile.symbol,
        "quantity": profile.quantity,
        "interval": config.interval,
        "period": config.period,
        "profile_name": args.profile,
    }

    run(params)


if __name__ == "__main__":
    main()
