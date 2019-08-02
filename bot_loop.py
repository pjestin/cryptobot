#! /usr/bin/env python3
# coding: utf-8

import math
import time
import argparse
import logging
import sys

from binance_interface import BinanceInterface
from strategy.macd_rsi import MacdRsiStrategy
from strategy.macd_ema import MacdEmaStrategy

LOG_FILE = 'log/{}.log'


def run(**params):
    n_ref = params['n_ref']
    commission = params['commission']
    period = params['period']
    simulate = params['simulate']
    currency_pair = params['currency_pair']
    quantity = params['quantity']
    interval = params['interval']
    acquired = params['acquired']

    money = 0.
    price = None
    previous_price = float('inf')
    nb_transactions = 0
    previous_transac_time = None
    previous_time = None

    binance = BinanceInterface()

    i = 0
    while True:
        i += 1
        begin_time = time.time()

        # Retrieve trade recent history
        # t, x = binance_interface.get_history(limit=n_ref, currency_pair=currency_pair)
        # price = x[-1]
        # action = Strategy.decide_action_from_data(t, x, previous_price, previous_transac_time, time.time(), previous_time)

        # Kline history
        klines = binance.get_klines(limit=n_ref, interval=interval, currency_pair=currency_pair)
        
        if klines:
            # action = MacdRsiStrategy.decide_action_from_data(klines)
            action = MacdEmaStrategy.decide_action_from_data(klines)
            logging.debug('Run {}; money: {}; transactions: {}; price ratio to previous: {}' \
                .format(i, money, nb_transactions, klines[-1].close_price / previous_price))

            # Buy or sell
            if not acquired and action.is_buy():
                nb_transactions += 1
                previous_transac_time = time.time()
                price = binance.last_price(currency_pair)
                previous_price = price
                acquired = (1 - commission) / price
                money -= 1
                logging.info('Buying at {}; money: {}'.format(price, money))
                if not simulate:
                    binance.create_order(is_buy=True, quantity=quantity, currency_pair=currency_pair)
            elif acquired and action.is_sell():
                nb_transactions += 1
                previous_transac_time = time.time()
                price = binance.last_price(currency_pair)
                previous_price = price
                money += (1 - commission) * acquired * price
                acquired = None
                logging.info('Selling at {}; money: {}'.format(price, money))
                if not simulate:
                    binance.create_order(is_buy=False, quantity=quantity, currency_pair=currency_pair)
        
        previous_time = time.time()
        
        # Sleep if duration was shorter than period
        duration = time.time() - begin_time
        if duration < period:
            time.sleep(period - duration)


def main():

    parser = argparse.ArgumentParser(description='Cryptocurrency trading bot')
    parser.add_argument('-c', '--currency-pair', dest='currency_pair', help='Specify currency pair on which to trade')
    parser.add_argument('-q', '--quantity', help='Quantity of target currency to trade')
    parser.add_argument('-i', '--interval', help='Interval of klines')
    parser.add_argument('-v', '--verbose', help='Display more logs', action='store_true')
    parser.add_argument('-a', '--acquired', help='Target currency already acquired')
    args = parser.parse_args()

    log_format = '%(asctime)-15s %(message)s'
    log_file = LOG_FILE.format(time.time())
    handlers = [
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
    if args.verbose:
        logging.basicConfig(format=log_format, level=logging.DEBUG, handlers=handlers)
        logging.info('Verbose output.')
    else:
        logging.basicConfig(format=log_format, level=logging.INFO, handlers=handlers)

    if not args.currency_pair:
        raise ValueError('No currency pair provided')

    run(
        n_ref=50,
        commission=0.001,
        period=10.,
        simulate=False,
        currency_pair=args.currency_pair,
        quantity=float(args.quantity) if args.quantity else 0.,
        interval=args.interval if args.interval else '5m',
        acquired=float(args.acquired) if args.acquired else None
    )


if __name__ == '__main__':
    main()
