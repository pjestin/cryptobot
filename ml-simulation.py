#! /usr/bin/env python3
# coding: utf-8


from interface import read_data
import matplotlib.pyplot as plt
from datetime import timedelta
import time
import argparse
import logging
import math

N_REF = 200
TEST_FILE_PATH = 'data/binance_klines_ETHUSDT_15m_1504869300000.json'
COMMISSION = 0.001


def run_simulation(klines, n_ref, n_features, commission):
    n = len(klines)
    money = [0.]
    acquired = None

    for k in range(n_ref, n):
        klines_ref = klines[k-n_ref:k]

        buy_model = fit_model(klines_ref, n_features, 'buy')
        sell_model = fit_model(klines_ref, n_features, 'sell')

        price = klines_ref[-1].close_price
        current_time = klines_ref[-1].close_time
        logging.debug('Run {}; time: {}; money: {}; price: {}'.format(
            k - n_ref, current_time, money[-1], price))

        action = decide_action(
            klines[k-n_features:k], buy_model, sell_model)

        if not acquired and action.is_buy():
            acquired = (1 - commission) / price
            logging.info('Buying at {}'.format(price))
        elif acquired and action.is_sell():
            money.append((money[-1] - 1) + (1 - commission) * acquired * price)
            acquired = None
            logging.info('Selling at {}; money: {}; time: {}'.format(
                price, money[-1], current_time))

        # if action.is_buy():
        #     next_price = klines[k + LOOK_AHEAD - 1].close_price
        #     money.append((money[-1] - 1) + math.pow(1 -
        #                                             commission, 2) * next_price / price)
        #     logging.info('Buying at {}; selling at {}; money: {}, time: {}'.format(
        #         price, next_price, money[-1], current_time))

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

    return money


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

    klines = read_data.read_klines_from_json(
        file_path=TEST_FILE_PATH)

    run_simulation(klines, n_ref=N_REF, n_features=N_FEATURES,
                   commission=COMMISSION)


if __name__ == '__main__':
    simulate()
    # test()
