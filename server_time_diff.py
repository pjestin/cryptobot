#! /usr/bin/env python3
# coding: utf-8

import logging

from interface.binance_io import BinanceInterface


def main():
    log_format = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=log_format, level=logging.INFO)
    BinanceInterface().server_time_diff()


if __name__ == '__main__':
    main()
