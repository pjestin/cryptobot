import math
import logging
from datetime import datetime

import numpy as np
import tensorflow as tf

from model import TradeAction
from strategy.indicators import Indicators


class TensorFlowStrategy:

    LOOK_AHEAD = 40
    MIN_LOG_RETURN = 0.002
    N_EPOCHS = 3
    MIN_LOG_RETURN_SELL = 0.

    def __init__(self, n_features):
        self.buy_model = None
        self.sell_model = None
        self.n_features = n_features
    
    def gather_data(self, klines, use_case):
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
        return (np.array(X), np.array(y))

    def fit_model(self, klines, use_case):
        logging.debug("Use case: '{}'".format(use_case))

        X, y = self.gather_data(klines, use_case)

        model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(128, activation='tanh'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(2, activation='softmax')
        ])

        model.compile(optimizer='adam',
                        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                        metrics=['accuracy'])

        model.fit(X, y, epochs=self.N_EPOCHS, verbose=2)

        if use_case == 'buy':
            self.buy_model = model
        elif use_case == 'sell':
            self.sell_model = model

    def save_models(self):
        now = datetime.utcnow()
        self.buy_model.save('models/{}/buy-{}'.format(now.date().isoformat(), now.isoformat()))
        self.sell_model.save('models/{}/sell-{}'.format(now.date().isoformat(), now.isoformat()))

    def evaluate_models(self, klines):
        X_buy, y_buy = self.gather_data(klines, 'buy')
        X_sell, y_sell = self.gather_data(klines, 'buy')
        self.buy_model.evaluate(X_buy, y_buy, verbose=2)
        self.sell_model.evaluate(X_sell, y_sell, verbose=2)

    def load_model(self, path, use_case):
        if use_case == 'buy':
            self.buy_model = tf.keras.models.load_model(path)
        elif use_case == 'sell':
            self.sell_model = tf.keras.models.load_model(path)

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
