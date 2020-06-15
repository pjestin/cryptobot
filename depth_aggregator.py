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


def dump_depth(binance_interface, depth_db):
    depth = binance_interface.get_current_depth(currency_pair=depth_db.currency_pair,
        limit=depth_db.limit)
    if depth:
        depth_db.extend(depth)


def run(currency_pair):
    binance_interface = BinanceInterface()
    depth_dbs = [DepthDb(currency_pair, limit, date.today()) for limit in ORDER_BOOK_LIMITS]

    while True:
        begin_time = time.time()

        for depth_db in depth_dbs:
            dump_depth(binance_interface, depth_db)
        
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
