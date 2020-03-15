#! /usr/bin/env python3
# coding: utf-8

import math
import logging
import argparse
import time
from datetime import timedelta

import matplotlib.pyplot as plt

from interface import read_data
from strategy.indicators import Indicators
# from strategy.macd_rsi import MacdRsiStrategy
# from strategy.macd_mfi import MacdMfiStrategy
# from strategy.macd_ema_rsi import MacdEmaRsiStrategy
# from strategy.resistance import ResistanceStrategy
# from strategy.macd_ema import MacdEmaStrategy
# from strategy.ema import EmaStrategy
# from strategy.volume_ema import VolumeEmaStrategy
# from strategy.macd_ema_ratio import MacEmaRatioStrategy
# from strategy.macd import MacdStrategy
# from strategy.ema_rsi import EmaRsiStrategy
# from strategy.bull_bear_macd_ema import BullBearMacdEmaStrategy
# from strategy.rsi import RsiStrategy
# from strategy.logistic_regression import LogisticRegressionStrategy
# from strategy.tensorflow import TensorFlowStrategy
from strategy.regression_buy import RegressionBuyStrategy

TIME_DIFF_FACTOR = 0.


def run_simulation(klines, n_ref, commission):
    n = len(klines)
    start_time = time.time()
    money = [0.]
    acquired = None

    buy_times = []
    sell_times = []

    previous_transac_time = None
    previous_price = None

    for k in range(n_ref, n):
        klines_ref = klines[k-n_ref:k]
        price = klines_ref[-1].close_price
        current_time = klines_ref[-1].close_time
        logging.debug('Run {}; time: {}; money: {}; price: {}'.format(
            k - n_ref, current_time, money[-1], price))

        if previous_transac_time:
            time_diff = timedelta(milliseconds=(
                klines_ref[-1].close_time - previous_transac_time))
            reference_time_diff = timedelta(milliseconds=(
                klines_ref[1].close_time - klines_ref[0].close_time))
            if time_diff < TIME_DIFF_FACTOR * reference_time_diff:
                continue

        # action = MacdRsiStrategy.decide_action_from_data(klines_ref)
        # action = MacdMfiStrategy.decide_action_from_data(klines_ref)
        # action = ResistanceStrategy.decide_action_from_data(klines_ref, previous_price, acquired)
        # action = MacdStrategy.decide_action_from_data(klines_ref)
        # action = MacdEmaStrategy.decide_action_from_data(klines_ref)
        # action = MacdEmaRsiStrategy.decide_action_from_data(klines_ref)
        # action = MacEmaRatioStrategy.decide_action_from_data(klines_ref, previous_price, acquired)
        # action = EmaStrategy.decide_action_from_data(klines_ref)
        # action = VolumeEmaStrategy.decide_action_from_data(klines_ref)
        # action = EmaRsiStrategy.decide_action_from_data(klines_ref)
        # action = BullBearMacdEmaStrategy.decide_action_from_data(klines_ref)
        # action = RsiStrategy.decide_action_from_data(klines_ref)
        # action = LogisticRegressionStrategy.decide_action_from_data(
        #     klines_ref)
        # action = TensorFlowStrategy.decide_action_from_data(
        #     klines_ref)
        action = RegressionBuyStrategy.decide_action_from_data(klines_ref, previous_price, acquired)

        if not acquired and action.is_buy():
            acquired = (1 - commission) / price
            logging.info('Buying at {}'.format(price))
            previous_price = price
            previous_transac_time = current_time
            buy_times.append(current_time)
        elif acquired and action.is_sell():
            money.append((money[-1] - 1) + (1 - commission) * acquired * price)
            acquired = None
            logging.info('Selling at {}; money: {}; time: {}'.format(
                price, money[-1], current_time))
            previous_price = price
            previous_transac_time = current_time
            sell_times.append(current_time)

    if acquired:
        last_price = klines[-1].close_price
        money.append((money[-1] - 1) + (1 - commission)
                     * acquired * last_price)
        acquired = None
        logging.info('Selling at {}; money: {}'.format(last_price, money[-1]))
        sell_times.append(current_time)

    market = (klines[-1].close_price -
              klines[0].close_price) / klines[0].close_price
    duration = timedelta(milliseconds=(
        klines[-1].close_time - klines[0].close_time))
    avg_per_month = money[-1] * timedelta(days=30) / duration
    avg_per_year_multiplier = (avg_per_month + 1) ** 12
    logging.info('Money: {}; Number of transactions: {}; Market: {}'.format(
        money[-1], 2 * len(money), market))
    logging.info('Duration: {}; average money per month: {}; per year: {}'.format(
        duration, avg_per_month, avg_per_year_multiplier))
    logging.info('Time: {}'.format(time.time() - start_time))

    plot(klines, money, buy_times, sell_times)

    return money


def plot(klines, money, buy_times, sell_times):
    plt.subplot(2, 1, 1)
    plt.plot([klines[0].close_time] + sell_times, money)

    plt.subplot(2, 1, 2)
    x = [kline.close_time for kline in klines]
    y = [kline.close_price for kline in klines]
    plt.plot(x, y)
    for buy_time in buy_times:
        plt.axvline(x=buy_time, color='r')
    for sell_time in sell_times:
        plt.axvline(x=sell_time, color='g')
    macd = [Indicators.macd_difference(y, k) for k in range(50, len(klines))]
    plt.plot(x, ([0] * 50) + macd)
    plt.axhline(y=0)

    plt.show()


def simulate(**kwargs):

    parser = argparse.ArgumentParser(
        description='Simulation on crypto currency trading strategies')
    parser.add_argument('-v', '--verbose',
                        help='Display more logs', action='store_true')
    args = parser.parse_args()

    log_format = '%(asctime)-15s %(message)s'
    if args.verbose:
        logging.basicConfig(format=log_format, level=logging.DEBUG)
        logging.info('Verbose output.')
    else:
        logging.basicConfig(format=log_format, level=logging.INFO)

    n_ref = 1000
    commission = .001

    klines = read_data.read_klines_from_json(
        file_path='data/binance_klines_ETHUSDT_1h_1502942400000.json')

    run_simulation(klines, n_ref=n_ref, commission=commission)

    # graph(klines)


if __name__ == '__main__':
    simulate()
