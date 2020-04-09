#! /usr/bin/env python3
# coding: utf-8

import logging
import argparse

from interface.binance_io import BinanceInterface
from model import Kline


def main():

    parser = argparse.ArgumentParser(description='Retrieve kline data from Binance')
    parser.add_argument('-v', '--verbose', help='Display more logs', action='store_true')
    parser.add_argument('-c', '--currency-pair', help='Curreny pair for which to resturn data (e.g. BTCUSDT)', dest='currency_pair')
    parser.add_argument('-i', '--interval', help='Interval of klines (e.g. "2h")')
    parser.add_argument('-d', '--date', help='Start date from which to retrieve kline (e.g. "2 years ago"')
    args = parser.parse_args()

    log_format = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=log_format, level=logging.INFO)
    
    if not args.date:
        raise RuntimeError('Missing start date')
    elif not args.currency_pair:
        raise RuntimeError('Missing currency pair')
    elif not args.interval:
        raise RuntimeError('Missing interval')

    BinanceInterface().dump_historical_klines(args.interval, args.currency_pair, args.date, 'now')


if __name__ == '__main__':
    main()
