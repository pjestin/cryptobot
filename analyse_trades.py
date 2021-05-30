#! /usr/bin/env python3
# coding: utf-8

import logging
import argparse
import math
from datetime import datetime, date

import matplotlib.pyplot as plt

from interface.binance_io import BinanceInterface
from interface.config import Config

COMMISSION = 0.001


def analyse_trades(currency_pairs, start_date=None):
    binance = BinanceInterface()

    for index, currency_pair in enumerate(currency_pairs):
        trades = binance.my_trade_history(currency_pair)
        acquired_price = None
        previous_price = None
        first_price = None
        t_money = [start_date]
        t_prices = [start_date]
        money = [0.0]
        prices = [0.0]

        for trade in trades:
            if start_date and datetime.utcfromtimestamp(trade.time) < start_date:
                continue
            if not first_price:
                first_price = trade.price
            if trade.is_buy:
                if acquired_price:
                    logging.error(
                        "Two buys in a row: {}, then {}".format(
                            previous_price, trade.price
                        )
                    )
                    continue
                acquired_price = trade.price
                t_prices.append(datetime.fromtimestamp(trade.time))
                prices.append(trade.price / first_price - 1.0)
            else:
                if not acquired_price:
                    logging.error(
                        "Two sells in a row, {}, then {}".format(
                            previous_price, trade.price
                        )
                    )
                    continue
                t_money.append(datetime.fromtimestamp(trade.time))
                t_prices.append(datetime.fromtimestamp(trade.time))
                money.append(
                    money[-1]
                    + trade.price / acquired_price * math.pow(1.0 - COMMISSION, 2)
                    - 1.0
                )
                prices.append(trade.price / first_price - 1.0)
                acquired_price = None
            previous_price = trade.price

        plt.subplot(len(currency_pairs), 1, index + 1)
        plt.title(currency_pair)
        plt.plot(t_money, money, color="blue")
        plt.plot(t_prices, prices, color="red")

    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Analyse history of Binance trades")
    parser.add_argument(
        "-c",
        "--currency-pair",
        help="Curreny pair for which to resturn data (e.g. BTCUSDT)",
        dest="currency_pair",
    )
    parser.add_argument(
        "-d",
        "--date",
        help="Start date in ISO format from which to retrieve trade history.",
    )
    args = parser.parse_args()

    log_format = "%(asctime)-15s %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO)

    currency_pairs = (
        [args.currency_pair]
        if args.currency_pair
        else [profile.symbol for profile in Config().profiles.values()]
    )

    analyse_trades(
        currency_pairs,
        datetime.combine(date.fromisoformat(args.date), datetime.min.time()),
    )


if __name__ == "__main__":
    main()
