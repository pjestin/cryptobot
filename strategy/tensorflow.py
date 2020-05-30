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
    N_EPOCHS = 5
    QUANTITY_FACTOR_POWER = 0.07

    def __init__(self, n_features):
        self.buy_model = None
        self.sell_model = None
        self.n_features = n_features

    def should_take_action(self, klines, use_case, k):
        ahead_log_return = math.log(sum(klines[i].close_price for i in range(
                k + 1, k + self.LOOK_AHEAD + 1)) / (self.LOOK_AHEAD * klines[k].close_price))
        if use_case == 'buy':
            return ahead_log_return > self.MIN_LOG_RETURN
        elif use_case == 'sell':
            return ahead_log_return < -self.MIN_LOG_RETURN
        return False

    def gather_data(self, klines, use_case):
        n = len(klines)
        log_returns = Indicators.log_returns(
            [kline.close_price for kline in klines])
        X = []
        y = []
        for k in range(self.n_features, n - self.LOOK_AHEAD):
            log_returns_ref = log_returns[k - self.n_features + 1:k + 1]
            X.append(log_returns_ref)
            y.append(1 if self.should_take_action(klines, use_case, k) else 0)

        return (np.array(X), np.array(y))

    def fit_model(self, klines, use_case):
        logging.debug("Use case: '{}'".format(use_case))

        X, y = self.gather_data(klines, use_case)

        model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(50, input_dim=self.n_features, activation='tanh'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])

        model.compile(optimizer='adam',
                        loss='binary_crossentropy',
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

    def decide_action(self, klines, acquired):
        n = len(klines)
        latest_klines = klines[n-self.n_features:n]
        log_returns = np.array(Indicators.log_returns(
            [kline.close_price for kline in latest_klines])).reshape(1, -1)
        buy_prediction = self.buy_model.predict_on_batch(log_returns)[0][0]
        sell_prediction = self.sell_model.predict_on_batch(log_returns)[0][0]
        if not acquired and buy_prediction > 0.5:
            return TradeAction('buy', quantity_factor=((float(buy_prediction) - 0.5) * 2.) ** self.QUANTITY_FACTOR_POWER)
        elif acquired and sell_prediction > 0.5:
            return TradeAction('sell', quantity_factor=((float(sell_prediction) - 0.5) * 2.) ** self.QUANTITY_FACTOR_POWER)
        return TradeAction(None)
