import math
import logging

import numpy as np
import tensorflow as tf

from model import TradeAction
from strategy.indicators import Indicators


class TensorFlowStrategy:

    LOOK_AHEAD = 20
    MIN_LOG_RETURN = 0.001
    MIN_LOG_RETURN_SELL = 0.02

    def __init__(self, n_features, verbose=False):
        self.buy_model = None
        self.sell_model = None
        self.n_features = n_features
        self.verbose = verbose

    def fit_model(self, klines, use_case):
        logging.debug("Use case: '{}'".format(use_case))
        n = len(klines)
        log_returns = Indicators.log_returns(
            [kline.close_price for kline in klines])
        X = []
        y = []
        for k in range(self.n_features, n - self.LOOK_AHEAD):
            log_returns_ref = log_returns[k - self.n_features + 1:k + 1]
            X.append(log_returns_ref)
            ahead_log_return = math.log(sum(klines[i].close_price for i in range(
                k + 1, k + self.LOOK_AHEAD + 1)) / (self.LOOK_AHEAD * klines[k].close_price))
            if use_case == 'buy':
                y.append(ahead_log_return > self.MIN_LOG_RETURN)
            elif use_case == 'sell':
                y.append(ahead_log_return < -self.MIN_LOG_RETURN)

        X = np.array(X)
        y = np.array(y)

        model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(128, activation='tanh'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(10)
        ])

        model.compile(optimizer='adam',
                        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                        metrics=['accuracy'])

        model.fit(X, y, epochs=5, verbose=2 if self.verbose else 0)

        if use_case == 'buy':
            self.buy_model = model
        elif use_case == 'sell':
            self.sell_model = model

    def decide_action(self, klines, acquired, previous_price):
        n = len(klines)
        potential_return = klines[-1].close_price / previous_price
        potential_log_return = math.log(potential_return) if potential_return != 0 else 1.
        if abs(potential_log_return) < self.MIN_LOG_RETURN_SELL:
            return TradeAction(None)
        latest_klines = klines[n-self.n_features:n]
        log_returns = np.array(Indicators.log_returns(
            [kline.close_price for kline in latest_klines])).reshape(1, -1)
        if not acquired and np.argmax(self.buy_model.predict_on_batch(log_returns)[0]) == 1:
            return TradeAction('buy')
        elif acquired and np.argmax(self.sell_model.predict_on_batch(log_returns)[0]) == 1:
            return TradeAction('sell')
        return TradeAction(None)
