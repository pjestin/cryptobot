#! /usr/bin/env python3
# coding: utf-8

import math
import time
import argparse
import logging
import sys
import json
from datetime import datetime, timedelta
import os
import re

from interface import read_data
from interface.binance_io import BinanceInterface

LOG_FILE = 'log/{}.log'
PROFILE_FILE = 'profiles.json'
RECENT_TRANSACTION_MIN = timedelta(hours=0)
N_REF = 1000
COMMISSION = 0.001


def probe_and_act_with_klines(klines, strat, binance, state):
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

    # Skip if recent transaction
    if state['last_transac_time'] and datetime.utcnow() - state['last_transac_time'] < RECENT_TRANSACTION_MIN:
        return

    action = strat.decide_action(klines, acquired)

    # Buy or sell
    if not acquired and action.is_buy():
        buy_quantity = float('%.3g' % quantity)
        logging.info('Buying {} at {}; money: {}'.format(
            buy_quantity, klines[-1].close_price, money))
        if simulate:
            price = binance.last_price(currency_pair)
        else:
            order = binance.create_order(
                is_buy=True, quantity=buy_quantity, currency_pair=currency_pair)
            price = float(order['fills'][0]['price'])
        state['previous_price'] = price
        state['nb_transactions'] += 1
        state['last_transac_time'] = datetime.utcnow()
        state['buy_quantity'] = buy_quantity
        state['acquired'] = (1 - commission) / price
        state['money'] -= 1.
    elif acquired and action.is_sell():
        logging.info('Selling {} at {}; money: {}'.format(
            buy_quantity, klines[-1].close_price, money))
        if simulate:
            price = binance.last_price(currency_pair)
        else:
            order = binance.create_order(
                is_buy=False, quantity=buy_quantity, currency_pair=currency_pair)
            price = float(order['fills'][0]['price'])
        state['previous_price'] = price
        state['nb_transactions'] += 1
        state['last_transac_time'] = datetime.utcnow()
        state['buy_quantity'] = None
        state['acquired'] = None
        state['money'] += (1 - commission) * acquired * price


def run(params):
    n_ref = params['n_ref']
    period = params['period']
    currency_pair = params['currency_pair']
    interval = params['interval']
    quantity = params['quantity']

    binance = BinanceInterface()

    last_trade = binance.last_trade(currency_pair)
    logging.info('Last trade in this currency pair: {}'.format(last_trade))
    acquired_price = last_trade.price if last_trade and last_trade.is_buy else None
    buy_quantity = float('%.3g' % (last_trade.quantity)
                         ) if last_trade and last_trade.is_buy else None
    start_price = binance.last_price(currency_pair)

    from strategy.bollinger_bands import KlinesBollingerBandsStrategy
    strat = KlinesBollingerBandsStrategy()

    state = {
        'money': -1. if acquired_price else 0.,
        'previous_price': acquired_price if acquired_price else float('inf'),
        'nb_transactions': 0,
        'last_transac_time': None,
        'acquired': 1. / acquired_price if acquired_price else None,
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
            logging.info('Run {}; money: {}; transactions: {}; price ratio to previous: {}; market: {}'
                            .format(i, state['money'], state['nb_transactions'], klines[-1].close_price / state['previous_price'], klines[-1].close_price / start_price - 1))
            probe_and_act_with_klines(klines, strat, binance, state)

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
    logging.basicConfig(format=log_format, level=logging.DEBUG)

    params = {
        "n_ref": N_REF,
        "commission": COMMISSION,
        "simulate": args.simulate
    }

    params = {**params, **read_profile(args.profile)}

    run(params)


if __name__ == '__main__':
    main()
