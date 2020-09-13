import math
import logging

import tensorflow as tf
import numpy as np

from model import TradeAction
from strategy.indicators import Indicators


class KlinesIndicatorIaStrategy:

    LOOK_AHEAD = 10
    INDICATOR_RANGE = 10
    MIN_LOG_RETURN = 0.0015
    N_EPOCHS = 3

    def __init__(self):
        self.buy_model = None
        self.sell_model = None

    def features(self, close_prices, i):
        features = []
        for k in range(i - self.INDICATOR_RANGE + 1, i + 1):
            price = close_prices[k]
            ema7 = Indicators.exp_moving_average(close_prices, k, 7)
            ema25 = Indicators.exp_moving_average(close_prices, k, 25)
            ema99 = Indicators.exp_moving_average(close_prices, k, 99)
            macd = Indicators.macd_difference(close_prices, k)
            rsi = Indicators.rsi(close_prices, k - 14, k)
            sma20 = Indicators.simple_moving_average(close_prices, k, 20)
            sd20 = Indicators.standard_deviation(close_prices, k, 20)

            features.extend([
                (price - ema7) / ema7,
                (price - ema25) / ema25,
                (price - ema99) / ema99,
                macd / ema25,
                rsi,
                (price - sma20) / sd20,
                sd20 / sma20,
            ])
        return features
    
    def should_take_action(self, klines, use_case, current, look_ahead):
        ahead_log_return = math.log(sum(klines[i].close_price for i in range(
                current + 1, look_ahead + 1)) / ((look_ahead - current) * klines[current].close_price))
        if use_case == 'buy':
            return ahead_log_return > self.MIN_LOG_RETURN
        elif use_case == 'sell':
            return ahead_log_return < -self.MIN_LOG_RETURN
        return False
    
    def gather_data(self, klines, use_case):
        X = []
        y = []
        close_prices = [kline.close_price for kline in klines]

        for i in range(self.INDICATOR_RANGE + 100, len(close_prices) - self.LOOK_AHEAD):
            X.append(self.features(close_prices, i))
            y.append(1 if self.should_take_action(klines, use_case, i, i + self.LOOK_AHEAD) else 0)

        return (np.array(X), np.array(y))

    def fit_model(self, klines, use_case):
        logging.debug("Use case: '{}'".format(use_case))

        X, y = self.gather_data(klines, use_case)

        model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(50, activation='tanh'),
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

    def decide_action(self, klines, acquired):
        close_prices = [kline.close_price for kline in klines]
        features = np.array(self.features(close_prices, len(klines) - 1)).reshape(1, -1)
        buy_prediction = self.buy_model.predict_on_batch(features)[0][0]
        sell_prediction = self.sell_model.predict_on_batch(features)[0][0]
        if not acquired and buy_prediction > 0.5:
            return TradeAction('buy')
        elif acquired and sell_prediction > 0.5:
            return TradeAction('sell')
        return TradeAction(None)
