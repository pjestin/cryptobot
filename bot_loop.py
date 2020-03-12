#! /usr/bin/env python3
# coding: utf-8

import math
import time
import argparse
import logging
import sys
import json
from datetime import timedelta
import os

from interface.binance_io import BinanceInterface
from strategy.macd_rsi import MacdRsiStrategy
from strategy.macd_ema import MacdEmaStrategy
from strategy.macd import MacdStrategy
from strategy.ema import EmaStrategy
from strategy.logistic_regression import LogisticRegressionStrategy
from strategy.tensorflow import TensorFlowStrategy

LOG_FILE = 'log/{}.log'
PROFILE_FILE = 'profiles.json'
TIME_DIFF_FACTOR = 15.


def run(params):
    n_ref = params['n_ref']
    commission = params['commission']
    period = params['period']
    simulate = params['simulate']
    currency_pair = params['currency_pair']
    quantity = params['quantity']
    interval = params['interval']
    acquired_price = params['acquired_price']

    money = -1. if acquired_price else 0.
    price = None
    previous_price = acquired_price if acquired_price else float('inf')
    nb_transactions = 0
    previous_transac_time = None
    previous_time = None
    acquired = 1 / acquired_price if acquired_price else None

    binance = BinanceInterface()

    i = 0
    while True:
        i += 1
        begin_time = time.time()

        # Kline history
        klines = binance.get_klines(
            limit=n_ref, interval=interval, currency_pair=currency_pair)

        if klines:

            if previous_transac_time:
                time_diff = timedelta(milliseconds=(
                    klines[-1].close_time - previous_transac_time))
                reference_time_diff = timedelta(milliseconds=(
                    klines[1].close_time - klines[0].close_time))
                if time_diff < TIME_DIFF_FACTOR * reference_time_diff:
                    time.sleep(period)
                    continue

            # action = MacdRsiStrategy.decide_action_from_data(klines)
            # action = MacdEmaStrategy.decide_action_from_data(klines)
            # action = MacdStrategy.decide_action_from_data(klines)
            # action = EmaStrategy.decide_action_from_data(klines)
            # action = LogisticRegressionStrategy.decide_action_from_data(
            #     klines)
            action = TensorFlowStrategy.decide_action_from_data(klines)
            logging.debug('Run {}; money: {}; transactions: {}; price ratio to previous: {}'
                          .format(i, money, nb_transactions, klines[-1].close_price / previous_price))

            # Buy or sell
            if not acquired and action.is_buy():
                nb_transactions += 1
                previous_transac_time = klines[-1].close_time
                price = binance.last_price(currency_pair)
                previous_price = price
                acquired = (1 - commission) / price
                money -= 1
                logging.info('Buying at {}; money: {}'.format(price, money))
                if not simulate:
                    binance.create_order(
                        is_buy=True, quantity=quantity, currency_pair=currency_pair)
            elif acquired and action.is_sell():
                nb_transactions += 1
                previous_transac_time = klines[-1].close_time
                price = binance.last_price(currency_pair)
                previous_price = price
                money += (1 - commission) * acquired * price
                acquired = None
                logging.info('Selling at {}; money: {}'.format(price, money))
                if not simulate:
                    binance.create_order(
                        is_buy=False, quantity=quantity, currency_pair=currency_pair)

        previous_time = time.time()

        # Sleep if duration was shorter than period
        duration = time.time() - begin_time
        if duration < period:
            time.sleep(period - duration)


def read_profile(profile_name):
    if not profile_name:
        raise EnvironmentError('Profile name was not specified')
    with open(PROFILE_FILE, newline='') as file:
        profiles = json.load(file)
        if profile_name not in profiles:
            raise EnvironmentError('Profile file does not exist')
        return profiles[profile_name]


def main():

    parser = argparse.ArgumentParser(description='Cryptocurrency trading bot')
    parser.add_argument('-v', '--verbose',
                        help='Display more logs', action='store_true')
    parser.add_argument(
        '-s', '--simulate', help='Do not make order, simulate only', action='store_true')
    parser.add_argument('-a', '--acquired-price',
                        help='Price at which target currency was acquired', dest='acquired_price')
    parser.add_argument('-p', '--profile', help='Profile name')
    args = parser.parse_args()

    log_format = '%(asctime)-15s %(message)s'
    log_file = LOG_FILE.format(time.time())
    handlers = [
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
    if args.verbose:
        logging.basicConfig(format=log_format,
                            level=logging.DEBUG, handlers=handlers)
        logging.info('Verbose output.')
    else:
        logging.basicConfig(format=log_format,
                            level=logging.INFO, handlers=handlers)

    params = {
        "n_ref": 200,
        "commission": 0.001,
        "simulate": args.simulate,
    }
    params['acquired_price'] = float(
        args.acquired_price) if args.acquired_price else None

    params = {**params, **read_profile(args.profile)}

    run(params)


if __name__ == '__main__':
    main()
