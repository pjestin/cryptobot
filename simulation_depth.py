#! /usr/bin/env python3
# coding: utf-8

import json
import os
import math
from datetime import datetime, timedelta, date
import logging

import matplotlib.pyplot as plt

from interface import read_data
from interface.depth_db import DepthDb
from strategy.depth.linear_regression import DepthLinearRegressionStrategy
from strategy.depth.deep_learning import DepthDeepLearningStrategy
from strategy.depth.order_book_imbalance import DepthOrderBookImbalanceStrategy

CURRENCY_PAIR = 'ETHUSDT'
LIMIT = 1000
COMMISSION = 0.001
KLINE_FILE_PATH = 'data/klines/binance_klines_ETHUSDT_1m_1587136800000.json'
TRAIN_FACTOR = 0.5


def simulate():
    log_format = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=log_format, level=logging.INFO)

    depth_db = DepthDb(CURRENCY_PAIR, LIMIT)
    depth_data = list(depth_db.read())
    n = depth_db.data_count()

    # Deep learning
    save = False
    n_start = n if save else int(n * TRAIN_FACTOR)
    klines = read_data.read_klines_from_json(file_path=KLINE_FILE_PATH)
    strat = DepthDeepLearningStrategy()
    depth_train = depth_data[0:n_start]
    depth_test = depth_data[n_start:]
    for use_case in ['buy', 'sell']:
        strat.fit_model(klines, depth_train, use_case)
    
    depth_test = depth_data

    money = [0.]
    transactions = 0
    acquired = None
    start_price, end_price = None, None
    start_time, end_time = None, None
    sell_times = []
    times = []
    prices = []
    for depth in depth_test:
        current_time = depth.time
        if not start_price:
            start_price = depth.bids[0][0]
        end_price = depth.bids[0][0]
        if not start_time:
            start_time = depth.time
        end_time = depth.time
        if not sell_times:
            sell_times.append(depth.time)

        times.append(current_time)
        prices.append(end_price / start_price - 1.)

        # action = DepthLinearRegressionStrategy.decide_action(depth, acquired)
        action = DepthOrderBookImbalanceStrategy.decide_action(depth, acquired)
        # action = strat.decide_action(depth, acquired)

        if action.is_buy():
            price = depth.asks[0][0]
            acquired = (1 - COMMISSION) / price
            transactions += 1
            logging.info('Buying at {}'.format(price))
        elif acquired and action.is_sell():
            price = depth.bids[0][0]
            money.append(money[-1] + (1. - COMMISSION) * price * acquired - 1.)
            acquired = None
            transactions += 1
            logging.info('Selling at {}; money: {}; date: {}'.format(
                price, money[-1], current_time.date().isoformat()))
            sell_times.append(current_time)

    if acquired:
        price = depth.bids[0][0]
        money.append(money[-1] + (1. - COMMISSION) * price * acquired - 1.)
        acquired = None
        transactions += 1
        logging.info('Selling at {}; money: {}; date: {}'.format(
            price, money[-1], current_time.date().isoformat()))
        sell_times.append(current_time)

    data_time_span = end_time - start_time
    market = end_price / start_price - 1.
    monthly_gain = money[-1] * (timedelta(days=30).total_seconds() / data_time_span.total_seconds())
    yearly_gain_factor = (monthly_gain + 1.) ** 12
    logging.info('Money: {}; Transactions: {}; Market: {}; Time: {}; Estimated year gain: {}'.format(
        money[-1], transactions, market, str(data_time_span), yearly_gain_factor))
    
    plt.plot(sell_times, money)
    plt.plot(times, prices)
    plt.show()


if __name__ == '__main__':
    simulate()
