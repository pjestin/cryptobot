import math
import logging

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from model import TradeAction


class RegressionBuyStrategy:

    LOOK_AHEAD = 10
    MIN_LOG_RETURN_BUY = 0.002
    MIN_LOG_RETURN_SELL = 0.02
    MAX_LOG_LOSS = 0.01
    N_FEATURES = 50

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
    def fit_model_buy(cls, klines):
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
            y.append(ahead_log_return > cls.MIN_LOG_RETURN_BUY)

        X = np.array(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, random_state=42)
        model = LogisticRegression(C=0.01).fit(
            X_train, y_train)

        logging.debug("Training set score: {:.2f}".format(
            model.score(X_train, y_train)))
        logging.debug("Test set score: {:.2f}".format(
            model.score(X_test, y_test)))

        return model

    @classmethod
    def decide_action_from_data(cls, klines, previous_price, acquired):
        if not acquired:
            buy_model = cls.fit_model_buy(klines)
            n = len(klines)
            latest_klines = klines[n-cls.N_FEATURES:n]
            log_returns = np.array(cls.get_log_returns(
                [kline.close_price for kline in latest_klines])).reshape(1, -1)
            if buy_model.predict(log_returns)[0]:
                return TradeAction('buy')
        else:
            potential_log_return = math.log(klines[-1].close_price / previous_price)
            sell_condition = potential_log_return > cls.MIN_LOG_RETURN_SELL \
                or potential_log_return < -cls.MAX_LOG_LOSS
            if sell_condition:
                return TradeAction('sell')
        return TradeAction(None)
