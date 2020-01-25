import math

import numpy as np
from sklearn.linear_model import LogisticRegression
# from sklearn.ensemble import GradientBoostingClassifier
# from sklearn.model_selection import train_test_split

from model import TradeAction


class LogisticRegressionStrategy:

    LOOK_AHEAD = 10
    MIN_LOG_RETURN = 0.001
    N_FEATURES = 20

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

        # X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
        # model = xgb.XGBClassifier(learning_rate=0.01).fit(
        model = LogisticRegression(C=0.01).fit(
            # model = GradientBoostingClassifier(random_state=0, learning_rate=0.01).fit(
            X, y)
        # X_train, y_train)

        # print("Training set score: {:.2f}".format(model.score(X_train, y_train)))
        # print("Test set score: {:.2f}".format(model.score(X_test, y_test)))

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
        if buy_model.predict(log_returns)[0]:
            return TradeAction('buy')
        elif sell_model.predict(log_returns)[0]:
            return TradeAction('sell')
        return TradeAction(None)
