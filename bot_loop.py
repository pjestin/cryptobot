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
import re

from interface import read_data
from interface.binance_io import BinanceInterface

LOG_FILE = 'log/{}.log'
PROFILE_FILE = 'profiles.json'
TIME_DIFF_FACTOR = 4.
N_REF = 1000
COMMISSION = 0.001
ROUND_DECIMAL = 6


def fit(strat, currency_pair, interval, model_version):
    rootdir = "models/{}".format(model_version)
    for use_case in ['buy', 'sell']:
        regex = re.compile('{}-{}-{}-.*'.format(currency_pair.upper(), interval, use_case))
        for dir in os.listdir(rootdir):
            if regex.match(dir):
                strat.load_model(os.path.join(rootdir, dir), use_case)
                break
    if strat.buy_model is None:
        logging.error('No data file matched for buy model')
    if strat.sell_model is None:
        logging.error('No data file matched for sell model')
    

def probe_and_act(klines, strat, binance, state):
    previous_transac_time = state['previous_transac_time']
    previous_price = state['previous_price']
    acquired = state['acquired']
    nb_transactions = state['nb_transactions']
    quantity = state['quantity']
    buy_quantity = state['buy_quantity']
    commission = state['commission']
    money = state['money']
    simulate = state['simulate']
    currency_pair = state['currency_pair']
    period = state['period']

    if previous_transac_time:
        time_diff = timedelta(milliseconds=(
            klines[-1].close_time - previous_transac_time))
        reference_time_diff = timedelta(milliseconds=(
            klines[1].close_time - klines[0].close_time))
        if time_diff < TIME_DIFF_FACTOR * reference_time_diff:
            time.sleep(period)
            return

    action = strat.decide_action(klines, acquired)

    # Buy or sell
    if not acquired and action.is_buy():
        buy_quantity_factor = action.quantity_factor
        buy_quantity = float('%.3g' % (quantity * buy_quantity_factor))
        logging.info('Buying {} at {}; money: {}'.format(buy_quantity, klines[-1].close_price, money))
        if simulate:
            price = binance.last_price(currency_pair)
        else:
            order = binance.create_order(
                is_buy=True, quantity=buy_quantity, currency_pair=currency_pair)
            price = float(order['fills'][0]['price'])
        state['nb_transactions'] += 1
        state['previous_transac_time'] = klines[-1].close_time
        state['buy_quantiy'] = buy_quantity
        state['buy_quantity_factor'] = buy_quantity_factor
        state['acquired'] = (1 - commission) * buy_quantity_factor / price
        state['money'] -= buy_quantity_factor
    elif acquired and action.is_sell():
        logging.info('Selling {} at {}; money: {}'.format(buy_quantity, klines[-1].close_price, money))
        if simulate:
            price = binance.last_price(currency_pair)
        else:
            order = binance.create_order(
                is_buy=False, quantity=buy_quantity, currency_pair=currency_pair)
            price = float(order['fills'][0]['price'])
        state['previous_price'] = price
        state['nb_transactions'] += 1
        state['previous_transac_time'] = klines[-1].close_time
        state['buy_quantiy'] = None
        state['buy_quantity_factor'] = None
        state['acquired'] = None
        state['money'] += (1 - commission) * acquired * price


def run(params):
    n_ref = params['n_ref']
    period = params['period']
    currency_pair = params['currency_pair']
    interval = params['interval']
    model_version = params['model_version']
    quantity = params['quantity']

    binance = BinanceInterface()

    last_trade = binance.last_trade(currency_pair)
    logging.info('Last trade in this currency pair: {}'.format(last_trade))
    acquired_price = last_trade.price if last_trade and last_trade.is_buy else None
    buy_quantity = last_trade.quantity if last_trade and last_trade.is_buy else None
    buy_quantity_factor = float('%.3g' % (buy_quantity / quantity)) if buy_quantity else None

    from strategy.tensorflow import TensorFlowStrategy
    strat = TensorFlowStrategy(n_features=n_ref)
    fit(strat, currency_pair, interval, model_version)
    
    state = {
        'money': -buy_quantity_factor if buy_quantity_factor else 0.,
        'previous_price': acquired_price if acquired_price else float('inf'),
        'nb_transactions': 0,
        'previous_transac_time': None,
        'acquired': buy_quantity_factor / acquired_price if acquired_price else None,
        'buy_quantity_factor': buy_quantity_factor,
        'buy_quantity': buy_quantity,
    }

    state = {**params, **state}

    i = 0
    while True:
        i += 1
        begin_time = time.time()

        # Kline history
        klines = binance.get_klines(
            limit=n_ref, interval=interval, currency_pair=currency_pair)

        if klines:
            logging.info('Run {}; money: {}; transactions: {}; price ratio to previous: {}'
                    .format(i, state['money'], state['nb_transactions'], klines[-1].close_price / state['previous_price']))
            probe_and_act(klines, strat, binance, state)

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
            raise EnvironmentError('Profile name does not exist')
        return profiles[profile_name]


def main():

    parser = argparse.ArgumentParser(description='Cryptocurrency trading bot')
    parser.add_argument(
        '-s', '--simulate', help='Do not make order, simulate only', action='store_true')
    parser.add_argument('-p', '--profile', help='Profile name')
    args = parser.parse_args()

    log_format = '%(asctime)-15s %(message)s'
    log_file = LOG_FILE.format(time.time())
    handlers = [
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
    logging.basicConfig(format=log_format, level=logging.DEBUG, handlers=handlers)

    params = {
        "n_ref": N_REF,
        "commission": COMMISSION,
        "simulate": args.simulate
    }

    params = {**params, **read_profile(args.profile)}

    run(params)


if __name__ == '__main__':
    main()
