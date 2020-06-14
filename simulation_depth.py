#! /usr/bin/env python3
# coding: utf-8

import json
import os
import math
from datetime import datetime, timedelta
import logging

from interface import read_data
from interface.depth_db import DepthDb
from strategy.depth_linear_regression import DepthLinearRegressionStrategy

CURRENCY_PAIR = 'ETHUSDT'
# INTERVAL = '1m'
LIMIT = 1000
# TEST_FILE_PATH = 'data/klines/binance_klines_ETHUSDT_1m_1591467840000.json'
# LOOK_AHEAD = timedelta(hours=1)
COMMISSION = 0.001


def simulate():
    log_format = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=log_format, level=logging.INFO)

    depth_data = DepthDb.read(CURRENCY_PAIR, LIMIT)
    # klines = read_data.read_klines_from_json(file_path=TEST_FILE_PATH)

    money = 0.
    transactions = 0
    acquired = None
    # current_kline_index = 0
    # look_ahead_kline_index = 0
    for depth in depth_data:
        current_time = depth.time
        # look_ahead_time = depth.time + LOOK_AHEAD
        # while current_kline_index < len(klines) and \
        #         datetime.fromtimestamp(klines[current_kline_index].close_time / 1000.) < depth.time:
        #     current_kline_index += 1
        # while look_ahead_kline_index < len(klines) and \
        #         datetime.fromtimestamp(klines[look_ahead_kline_index].close_time / 1000.) < look_ahead_time:
        #     look_ahead_kline_index += 1
        
        # if current_kline_index >= len(klines) or look_ahead_kline_index >= len(klines):
        #     break

        # current_price = klines[current_kline_index].close_price
        # print('Price: {}'.format(current_price))
        # ahead_log_return = math.log(sum(klines[i].close_price for i in range(
        #         current_kline_index + 1, look_ahead_kline_index + 1)) /
        #         ((look_ahead_kline_index - current_kline_index) * current_price))

        action = DepthLinearRegressionStrategy.decide_action(depth, acquired)

        if action.is_buy():
            price = depth.asks[0].price
            acquired = (1 - COMMISSION) / price
            previous_price = price
            transactions += 1
            logging.info('Buying at {}'.format(price))
        elif acquired and action.is_sell():
            price = depth.bids[0].price
            money += ((1 - COMMISSION) * price - previous_price) * acquired
            acquired = None
            previous_price = price
            transactions += 1
            logging.info('Selling at {}; money: {}; date: {}'.format(
                price, money, current_time.date().isoformat()))

    print('Money: {}; Transactions: {}; Market: {}'.format(
        money, transactions, depth_data[-1].bids[0].price / depth_data[0].bids[0].price - 1.))


if __name__ == '__main__':
    simulate()
