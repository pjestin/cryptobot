import logging

import numpy as np
from sklearn.linear_model import LinearRegression

from model import TradeAction


class DepthLinearRegressionStrategy:

    MIN_RETURN = 1.0004

    @classmethod
    def depth_linear_regression(cls, units):
        cumulative_quantity = np.cumsum([unit.quantity for unit in units])
        prices = np.array([unit.price for unit in units]).reshape(-1, 1)
        regressor = LinearRegression().fit(prices, cumulative_quantity)
        return [regressor.coef_[0], regressor.intercept_]

    @classmethod
    def decide_action(cls, depth, acquired):
        # return sum(unit.quantity for unit in depth.bids) > sum(unit.quantity for unit in depth.asks) * 1.08
        bids_coef, bids_intercept = cls.depth_linear_regression(depth.bids)
        asks_coef, asks_intercept = cls.depth_linear_regression(depth.asks)
        intersection = (bids_intercept - asks_intercept) / (asks_coef - bids_coef)
        if not acquired and intersection > depth.asks[0].price * cls.MIN_RETURN:
            logging.info("Bid: {}; Ask: {}; Intersection: {}".format(depth.bids[0].price, depth.asks[0].price, intersection))
            return TradeAction('buy')
        if acquired and intersection < depth.bids[0].price / cls.MIN_RETURN:
            logging.info("Bid: {}; Ask: {}; Intersection: {}".format(depth.bids[0].price, depth.asks[0].price, intersection))
            return TradeAction('sell')
        return TradeAction(None)