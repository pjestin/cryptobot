#! /usr/bin/env python3
# coding: utf-8

import json
import os
import math
from datetime import datetime, timedelta
import logging

from interface import read_data
from interface.depth_db import DepthDb
from strategy.depth.linear_regression import DepthLinearRegressionStrategy
from strategy.depth.deep_learning import DepthDeepLearningStrategy

CURRENCY_PAIR = 'ETHUSDT'
LIMIT = 1000
COMMISSION = 0.001
TEST_FILE_PATH = 'data/klines/binance_klines_ETHUSDT_1m_1591467840000.json'
TRAIN_FACTOR = 0.5


def simulate():
    log_format = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=log_format, level=logging.INFO)

    depth_data = DepthDb.read(CURRENCY_PAIR, LIMIT)

    # Deep learning
    n = len(depth_data)
    save = False
    n_start = n if save else int(n * TRAIN_FACTOR)
    klines = read_data.read_klines_from_json(file_path=TEST_FILE_PATH)
    strat = DepthDeepLearningStrategy()
    depth_train = depth_data[0:n_start]
    depth_test = depth_data[n_start:]
    for use_case in ['buy', 'sell']:
        strat.fit_model(klines, depth_train, use_case)
    
    # depth_test = depth_data

    money = 0.
    transactions = 0
    acquired = None
    for depth in depth_test:
        current_time = depth.time

        # action = DepthLinearRegressionStrategy.decide_action(depth, acquired)
        action = strat.decide_action(depth, acquired)

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
