from datetime import datetime
import logging

import tensorflow as tf
import numpy as np

from model import TradeAction
from strategy.indicators import Indicators


class KlinesGroundTruthStrategy:

    MIN_RETURN = 1.002
    N_EPOCHS = 5
    QUANTITY_FACTOR_POWER = 0.07
    
    def __init__(self, n_features):
        self.buy_model = None
        self.sell_model = None
        self.n_features = n_features
    
    @classmethod
    def _find_extrema(cls, A, factor):
        n = len(A)
        extrema = []
        for index in range(1, n - 1):
            if (A[index] - A[index - 1]) * factor < 0. \
                and (A[index] - A[index + 1]) * factor < 0.:
                extrema.append((index, A[index]))
        return extrema
    
    @classmethod
    def _find_valid_buys(cls, mins, maxes, prices):
        n = len(prices)
        valid_buys = set()
        right_max_index = 0
        for min_index in range(len(mins)):
            min_kline_index = mins[min_index][0]
            while right_max_index < len(maxes) and maxes[right_max_index][0] < min_kline_index:
                right_max_index += 1
            if right_max_index == len(maxes):
                return valid_buys
            max_buy_value = min(maxes[right_max_index - 1][1], maxes[right_max_index][1]) / cls.MIN_RETURN
            
            price_index = min_kline_index
            while price_index < n and prices[price_index] < max_buy_value:
                valid_buys.add(price_index)
                price_index += 1
            
            price_index = min_kline_index
            while price_index >= 0 and prices[price_index] < max_buy_value:
                valid_buys.add(price_index)
                price_index -= 1
        
        return valid_buys
    
    @classmethod
    def _find_valid_sells(cls, mins, maxes, prices):
        n = len(prices)
        valid_sells = set()
        right_min_index = 0
        for max_index in range(len(maxes)):
            max_kline_index = maxes[max_index][0]
            while right_min_index < len(mins) and mins[right_min_index][0] < max_kline_index:
                right_min_index += 1
            if right_min_index == len(mins):
                return valid_sells
            min_sell_value = max(mins[right_min_index - 1][1], mins[right_min_index][1]) * cls.MIN_RETURN
            
            price_index = max_kline_index
            while price_index < n and prices[price_index] > min_sell_value:
                valid_sells.add(price_index)
                price_index += 1
            
            price_index = max_kline_index
            while price_index >= 0 and prices[price_index] > min_sell_value:
                valid_sells.add(price_index)
                price_index -= 1
        
        return valid_sells


    def _gather_data(self, klines, use_case):
        n = len(klines)
        prices = [kline.close_price for kline in klines]
        mins = self._find_extrema(prices, 1.)
        maxes = self._find_extrema(prices, -1.)
        print('mins: {}, maxes: {}'.format(len(mins), len(maxes)))

        log_returns = Indicators.log_returns(
            [kline.close_price for kline in klines])
        X, y = [], []
        for k in range(self.n_features, n):
            log_returns_ref = log_returns[k - self.n_features + 1:k + 1]
            X.append(log_returns_ref)

        if use_case == 'buy':
            valid_buys = self._find_valid_buys(mins, maxes, prices)
            for k in range(self.n_features, n):
                y.append(1 if k in valid_buys else 0)
        else:
            valid_sells = self._find_valid_sells(mins, maxes, prices)
            for k in range(self.n_features, n):
                y.append(1 if k in valid_sells else 0)

        return (np.array(X), np.array(y))

    def fit_model(self, klines, use_case):
        logging.debug("Use case: '{}'".format(use_case))

        X, y = self._gather_data(klines, use_case)

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

    def evaluate_models(self, klines):
        X_buy, y_buy = self._gather_data(klines, 'buy')
        X_sell, y_sell = self._gather_data(klines, 'buy')
        self.buy_model.evaluate(X_buy, y_buy, verbose=2)
        self.sell_model.evaluate(X_sell, y_sell, verbose=2)

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
