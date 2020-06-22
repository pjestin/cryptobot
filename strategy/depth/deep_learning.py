import logging
import math
from datetime import datetime, timedelta

import tensorflow as tf
import numpy as np

from model import TradeAction


class DepthDeepLearningStrategy:

    LOOK_AHEAD = timedelta(minutes=60)
    MIN_LOG_RETURN = 0.002
    N_EPOCHS = 3
    QUANTITY_FACTOR_POWER = 0.

    def __init__(self):
        self.buy_model = None
        self.sell_model = None
    
    @classmethod
    def depth_features(cls, depth):
        return [unit.quantity for unit in depth.bids] \
                + [unit.quantity for unit in depth.asks]
    
    def should_take_action(self, klines, use_case, current, look_ahead):
        ahead_log_return = math.log(sum(klines[i].close_price for i in range(
                current + 1, look_ahead + 1)) / ((look_ahead - current) * klines[current].close_price))
        if use_case == 'buy':
            return ahead_log_return > self.MIN_LOG_RETURN
        elif use_case == 'sell':
            return ahead_log_return < -self.MIN_LOG_RETURN
        return False
    
    def gather_data(self, klines, depth_data, use_case):
        X = []
        y = []
        current_kline_index = 0
        look_ahead_kline_index = 0
        for depth in depth_data:
            look_ahead_time = depth.time + self.LOOK_AHEAD
            while current_kline_index < len(klines) and \
                    datetime.fromtimestamp(klines[current_kline_index].close_time / 1000.) < depth.time:
                current_kline_index += 1
            while look_ahead_kline_index < len(klines) and \
                    datetime.fromtimestamp(klines[look_ahead_kline_index].close_time / 1000.) < look_ahead_time:
                look_ahead_kline_index += 1
            
            if current_kline_index >= len(klines) or look_ahead_kline_index >= len(klines):
                break

            X.append(self.depth_features(depth))
            y.append(1 if self.should_take_action(klines, use_case, current_kline_index, look_ahead_kline_index) else 0)
    
        return (np.array(X), np.array(y))

    def fit_model(self, klines, depth_data, use_case):
        logging.debug("Use case: '{}'".format(use_case))

        X, y = self.gather_data(klines, depth_data, use_case)

        model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(50, activation='tanh'), #input_dim=len(X)
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

    def evaluate_models(self, klines, depth_data):
        X_buy, y_buy = self.gather_data(klines, depth_data, 'buy')
        X_sell, y_sell = self.gather_data(klines, depth_data, 'buy')
        self.buy_model.evaluate(X_buy, y_buy, verbose=2)
        self.sell_model.evaluate(X_sell, y_sell, verbose=2)

    def decide_action(self, depth, acquired):
        depth_features = np.array(self.depth_features(depth)).reshape(1, -1)
        buy_prediction = self.buy_model.predict_on_batch(depth_features)[0][0]
        sell_prediction = self.sell_model.predict_on_batch(depth_features)[0][0]
        if not acquired and buy_prediction > 0.5:
            return TradeAction('buy', quantity_factor=((float(buy_prediction) - 0.5) * 2.) ** self.QUANTITY_FACTOR_POWER)
        elif acquired and sell_prediction > 0.5:
            return TradeAction('sell', quantity_factor=((float(sell_prediction) - 0.5) * 2.) ** self.QUANTITY_FACTOR_POWER)
        return TradeAction(None)
