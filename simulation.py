#! /usr/bin/env python3
# coding: utf-8


from datetime import timedelta, date
import time
import argparse
import logging
import math
import re
import os

import matplotlib.pyplot as plt

from interface import read_data
from model import TradeAction

TEST_FILE_PATH = 'data/binance_klines_ADABNB_15m_1559347200000.json'
COMMISSION = 0.001
N_FEATURES = 1000


def run_simulation(klines, n_features, commission, save, validate):
    n = len(klines)
    n_start = 0
    money = [0.]
    acquired = None
    previous_price = float('inf')
    sell_times = []

    from strategy.bollinger_bands import KlinesBollingerBandsStrategy
    strat = KlinesBollingerBandsStrategy()

    for k in range(n_start + n_features, n):
        klines_ref = klines[k-n_features:k]

        price = klines_ref[-1].close_price
        current_time = klines_ref[-1].close_time

        action = strat.decide_action(klines_ref, acquired)

        if not acquired and action.is_buy():
            acquired = (1 - commission) / price
            previous_price = price
            logging.info('Buying at {}'.format(price))
        elif acquired and action.is_sell():
            money.append(money[-1] + (1. - commission) * price * acquired - 1.)
            acquired = None
            previous_price = price
            logging.info('Selling at {}; money: {}; date: {}'.format(
                price, money[-1], date.fromtimestamp(current_time / 1000).isoformat()))
            sell_times.append(current_time)

    market = (klines[-1].close_price -
              klines[n_start].close_price) / klines[n_start].close_price
    duration = timedelta(milliseconds=(
        klines[-1].close_time - klines[n_start].close_time))
    avg_per_month = money[-1] * timedelta(days=30) / duration
    avg_per_year_multiplier = (avg_per_month + 1) ** 12
    logging.info('Money: {}; Number of transactions: {}; Market: {}'.format(
        money[-1], 2 * len(money), market))
    logging.info('Duration: {}; average money per month: {}; per year: {}'.format(
        duration, avg_per_month, avg_per_year_multiplier))

    plot(klines, money, sell_times)

    return money


def plot(klines, money, sell_times):
    plt.subplot(2, 1, 1)
    plt.plot([klines[0].close_time] + sell_times, money)

    plt.subplot(2, 1, 2)
    x = [kline.close_time for kline in klines]
    y = [kline.close_price for kline in klines]
    plt.plot(x, y)
    plt.axhline(y=0)

    plt.show()


def simulate(**kwargs):

    parser = argparse.ArgumentParser(
        description='Simulation on crypto currency trading strategies')
    parser.add_argument('-s', '--save',
                        help='Save model', action='store_true')
    parser.add_argument('-v', '--validate',
                        help='Validate model', action='store_true')
    args = parser.parse_args()

    log_format = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=log_format, level=logging.INFO)

    if args.save and args.validate:
        raise RuntimeError('Cant save and validate')

    klines = read_data.read_klines_from_json(
        file_path=TEST_FILE_PATH)

    run_simulation(klines, n_features=N_FEATURES, commission=COMMISSION,
                   save=args.save, validate=args.validate)


if __name__ == '__main__':
    simulate()
