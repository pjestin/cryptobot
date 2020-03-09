import math
import logging

import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split

from model import TradeAction


class TensorFlowStrategy:

    LOOK_AHEAD = 1
    MIN_LOG_RETURN = 0.
    N_FEATURES = 200

    TRAINING_SET_SCORES = np.array(0)
    TEST_SET_SCORES = np.array(0)

    @classmethod
    def get_log_returns(cls, prices):
        log_returns = [0.]
        previous_price = None
        for price in prices:
            if previous_price:
                log_returns.append(math.log(price / previous_price))
            previous_price = price
        return log_returns

    @classmethod
    def fit_model(cls, klines, use_case):
        logging.debug("Use case: '{}'".format(use_case))
        n = len(klines)
        log_returns = cls.get_log_returns(
            [kline.close_price for kline in klines])
        X = []
        y = []
        for k in range(cls.N_FEATURES, n - cls.LOOK_AHEAD):
            log_returns_ref = log_returns[k - cls.N_FEATURES + 1:k + 1]
            X.append(log_returns_ref)
            ahead_log_return = math.log(sum(klines[i].close_price for i in range(
                k + 1, k + cls.LOOK_AHEAD + 1)) / (cls.LOOK_AHEAD * klines[k].close_price))
            if use_case == 'buy':
                y.append(ahead_log_return > cls.MIN_LOG_RETURN)
            elif use_case == 'sell':
                y.append(ahead_log_return < -cls.MIN_LOG_RETURN)

        X = np.array(X)
        y = np.array(y)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, random_state=42)

        model = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(input_shape=(cls.N_FEATURES, )),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(10)
        ])

        model.compile(optimizer='adam',
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(
                          from_logits=True),
                      metrics=['accuracy'])

        model.fit(X_train, y_train, epochs=5, verbose=2)

        cls.TRAINING_SET_SCORES = np.append(
            cls.TRAINING_SET_SCORES, model.evaluate(X_train, y_train, verbose=2))
        cls.TEST_SET_SCORES = np.append(
            cls.TEST_SET_SCORES, model.evaluate(X_test, y_test, verbose=2))
        # logging.debug('Mean training set score: {}'.format(np.mean(cls.TRAINING_SET_SCORES)))
        logging.debug('Mean test set score: {}'.format(
            np.mean(cls.TEST_SET_SCORES)))

        # test_index = 0
        # print(X_test[test_index, :].reshape(1, -1))
        # print("Prediction: {}".format(model.predict(
        #     X_test[test_index, :].reshape(1, -1))))
        # print("Actual: {}".format(y[test_index]))

        return model

    @classmethod
    def decide_action_from_data(cls, klines):
        buy_model = cls.fit_model(klines, 'buy')
        sell_model = cls.fit_model(klines, 'sell')
        n = len(klines)
        latest_klines = klines[n-cls.N_FEATURES:n]
        log_returns = np.array(cls.get_log_returns(
            [kline.close_price for kline in latest_klines])).reshape(1, -1)
        if np.argmax(buy_model.predict(log_returns)[0]) == 1:
            return TradeAction('buy')
        elif np.argmax(sell_model.predict(log_returns)[0]) == 1:
            return TradeAction('sell')
        return TradeAction(None)
