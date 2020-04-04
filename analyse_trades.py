#! /usr/bin/env python3
# coding: utf-8

import logging
import argparse
import math
from datetime import datetime

import matplotlib.pyplot as plt

from interface.binance_io import BinanceInterface

COMMISSION = 0.001
CURRENCY_PAIRS = ['BNBUSDT', 'BTCUSDT', 'ETHUSDT']


def analyse_trades(currency_pairs, start_date=None):
    start_date_object = datetime.utcfromtimestamp(float(start_date))
    binance = BinanceInterface()

    for index, currency_pair in enumerate(currency_pairs):
        trades = binance.my_trade_history(currency_pair)
        money = 0.0
        acquired_price = None
        t = [start_date]
        x = [0.0]

        for trade in trades:
            if start_date and datetime.utcfromtimestamp(float(trade.time / 1000)) < start_date_object:
                continue
            if trade.is_buy:
                if acquired_price:
                    logging.error('Two buys in a row: {}, then {}'.format(acquired_price, trade.price))
                    continue
                acquired_price = trade.price
            else:
                if not acquired_price:
                    logging.error('Two sells in a row, second sell: {}'.format(trade.price))
                    continue
                money += trade.price / acquired_price * math.pow(1. - COMMISSION, 2) - 1.
                acquired_price = None
                t.append(trade.time)
                x.append(money)
    
        plt.subplot(len(CURRENCY_PAIRS), 1, index + 1)
        plt.title(currency_pair)
        plt.plot(t, x)
    
    plt.show()


def main():

    parser = argparse.ArgumentParser(description='Analyse history of Binance trades')
    parser.add_argument('-v', '--verbose', help='Display more logs', action='store_true')
    parser.add_argument('-c', '--currency-pair', help='Curreny pair for which to resturn data (e.g. BTCUSDT)', dest='currency_pair')
    parser.add_argument('-d', '--date', help='Start date from which to retrieve trade history')
    args = parser.parse_args()

    log_format = '%(asctime)-15s %(message)s'
    if args.verbose:
        logging.basicConfig(format=log_format, level=logging.DEBUG)
        logging.info('Verbose output.')
    else:
        logging.basicConfig(format=log_format, level=logging.INFO)
    
    currency_pairs = [args.currency_pair] if args.currency_pair else CURRENCY_PAIRS

    analyse_trades(currency_pairs, args.date)


if __name__ == '__main__':
    main()
