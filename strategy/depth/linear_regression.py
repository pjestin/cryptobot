import logging
import math

import numpy as np
from sklearn.linear_model import LinearRegression

from model import TradeAction
from strategy.indicators import Indicators


class DepthLinearRegressionStrategy:

    MIN_LOG_RETURN = .002

    @classmethod
    def depth_linear_regression(cls, units):
        cumulative_quantity = np.cumsum([unit[1] for unit in units])
        prices = np.array([unit[0] for unit in units]).reshape(-1, 1)
        regressor = LinearRegression().fit(prices, cumulative_quantity)
        return [regressor.coef_[0], regressor.intercept_]

    @classmethod
    def decide_action(cls, depth, acquired):
        bids_coef, bids_intercept = cls.depth_linear_regression(depth.bids)
        asks_coef, asks_intercept = cls.depth_linear_regression(depth.asks)
        intersection = (bids_intercept - asks_intercept) / (asks_coef - bids_coef)
        logging.debug('Bid price: {}; ask price: {}; intersection: {}'.format(
            depth.bids[0][0], depth.asks[0][0], intersection))
        if not acquired and math.log(intersection / depth.asks[0][0]) > cls.MIN_LOG_RETURN:
            return TradeAction('buy')
        if acquired and math.log(intersection / depth.bids[0][0]) < -cls.MIN_LOG_RETURN:
            return TradeAction('sell')
        return TradeAction(None)
