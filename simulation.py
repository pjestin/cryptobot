#! /usr/bin/env python3
# coding: utf-8

import math
import logging
import argparse

import matplotlib.pyplot as plt

import read_data
from strategy.macd_rsi import MacdRsiStrategy
from strategy.macd_mfi import MacdMfiStrategy
from strategy.macd_ema_rsi import MacdEmaRsiStrategy
from strategy.resistance import ResistanceStrategy
from strategy.macd_ema import MacdEmaStrategy
from strategy.indicators import Indicators
from strategy.macd_ema_ratio import MacEmaRatioStrategy


def run_simulation(klines, n_ref, commission):
    n = len(klines)
    money = [0.]
    acquired = None
    previous_price = None

    for k in range(n_ref, n):
        klines_ref = klines[k-n_ref:k]
        price = klines_ref[-1].close_price
        logging.debug('Run {}; money: {}; price: {}'.format(k - n_ref, money[-1], price))

        # action = MacdRsiStrategy.decide_action_from_data(klines_ref)
        # action = MacdMfiStrategy.decide_action_from_data(klines_ref)
        # action = ResistanceStrategy.decide_action_from_data(klines_ref, previous_price, acquired)
        action = MacdEmaStrategy.decide_action_from_data(klines_ref)
        # action = MacdEmaRsiStrategy.decide_action_from_data(klines_ref)
        # action = MacEmaRatioStrategy.decide_action_from_data(klines_ref, previous_price, acquired)

        if not acquired and action.is_buy():
            acquired = (1 - commission) / price
            logging.info('Buying at {}'.format(price))
            previous_price = price
        elif acquired and action.is_sell():
            money.append((money[-1] - 1) + (1 - commission) * acquired * price)
            acquired = None
            logging.info('Selling at {}; money: {}'.format(price, money[-1]))
            previous_price = price

    if acquired:
        last_price = klines[-1].close_price
        money.append((money[-1] - 1) + (1 - commission) * acquired * last_price)
        acquired = None
        logging.info('Selling at {}; money: {}'.format(last_price, money[-1]))

    logging.info('Money: {}; Number of transactions: {}'.format(money[-1], len(money)))
    plt.plot(range(0, len(money)), money)
    plt.show()

    return money


def graph(klines):
    n_ref = 120
    klines_ref = klines[-n_ref:]
    prices = [kline.close_price for kline in klines_ref]
    ema_12 = [Indicators.exp_moving_average(prices, k, 12) for k in range(n_ref//2, n_ref)]
    ema_26 = [Indicators.exp_moving_average(prices, k, 26) for k in range(n_ref//2, n_ref)]
    macd = [Indicators.moving_average_conv_div(prices, k) for k in range(n_ref//2, n_ref)]
    signal = [Indicators.moving_average_conv_div_ema(prices, k) for k in range(n_ref//2, n_ref)]

    plt.plot(range(0, n_ref//2), ema_12)
    plt.plot(range(0, n_ref//2), ema_26)
    plt.plot(range(0, n_ref//2), macd)
    plt.plot(range(0, n_ref//2), signal)
    plt.plot(range(0, n_ref//2), prices[n_ref//2:])
    plt.show()


def simulate(**kwargs):

    parser = argparse.ArgumentParser(description='Simulation on crypto currency trading strategies')
    parser.add_argument('-v', '--verbose', help='Display more logs', action='store_true')
    args = parser.parse_args()

    log_format = '%(asctime)-15s %(message)s'
    if args.verbose:
        logging.basicConfig(format=log_format, level=logging.DEBUG)
        logging.info('Verbose output.')
    else:
        logging.basicConfig(format=log_format, level=logging.INFO)

    n_ref = 50
    commission = .001

    klines = read_data.read_klines_from_json(file_path='data/binance_klines_BTCUSDT_5m_1502942400000.json')

    run_simulation(klines, n_ref=n_ref, commission=commission)

    # graph(klines)


if __name__ == '__main__':
    simulate()
