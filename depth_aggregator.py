#! /usr/bin/env python3
# coding: utf-8

import argparse
import logging
import json
from datetime import date
import os
import time
from pathlib import Path

from interface.binance_io import BinanceInterface
from interface.depth_db import DepthDb

ORDER_BOOK_LIMITS = [100, 1000]
PERIOD = 60


def dump_depth(binance_interface, currency_pair, limit):
    depth = binance_interface.get_current_depth(currency_pair=currency_pair, limit=limit)
    if depth:
        DepthDb.extend(depth, currency_pair, limit)


def run(currency_pair):
    binance_interface = BinanceInterface()

    while True:
        begin_time = time.time()

        for limit in ORDER_BOOK_LIMITS:
            dump_depth(binance_interface, currency_pair, limit)
        
        duration = time.time() - begin_time
        if duration < PERIOD:
            time.sleep(PERIOD - duration)


def main():

    parser = argparse.ArgumentParser(description='Retrieve and store order book data from Binance')
    parser.add_argument('-c', '--currency-pair', help='Curreny pair for which to resturn data (e.g. BTCUSDT)', dest='currency_pair')
    args = parser.parse_args()

    log_format = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=log_format, level=logging.DEBUG)

    if not args.currency_pair:
        raise RuntimeError('Missing currency pair')

    run(currency_pair=args.currency_pair.upper())


if __name__ == '__main__':
    main()
