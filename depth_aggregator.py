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

ORDER_BOOK_LIMIT = 1000
PERIOD = 60


def dump_depth(binance_interface, currency_pair, limit):
    depth = binance_interface.get_current_depth(currency_pair=currency_pair, limit=limit)

    file_path = 'data/depth/binance_depth_{}_{}_{}.json'.format(
        currency_pair, limit, date.today().isoformat())
    logging.debug('Adding depth data to file {}'.format(file_path))
    if not os.path.isfile(file_path):
        with open(file_path, mode='a') as file:
            json.dump([], file)

    with open(file_path, mode='r') as file:
        existing_data = json.load(file)
    existing_data.append(depth.to_json())
    with open(file_path, mode='w') as file:
        json.dump(existing_data, file)


def run(currency_pair):
    binance_interface = BinanceInterface()

    while True:
        begin_time = time.time()

        dump_depth(binance_interface=binance_interface, currency_pair=currency_pair, limit=100)
        dump_depth(binance_interface=binance_interface, currency_pair=currency_pair, limit=1000)
        
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

    run(currency_pair=args.currency_pair)


if __name__ == '__main__':
    main()
