import logging
import math

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

from model import TradeAction


class DepthLinearRegressionStrategy:

    MIN_LOG_RETURN = .0013

    @classmethod
    def depth_linear_regression(cls, units):
        cumulative_quantity = np.cumsum([unit.quantity for unit in units])
        prices = np.array([unit.price for unit in units]).reshape(-1, 1)
        regressor = LinearRegression().fit(prices, cumulative_quantity)
        return [regressor.coef_[0], regressor.intercept_]

    @classmethod
    def decide_action(cls, depth, acquired):
        # if not acquired and sum(unit.quantity for unit in depth.bids) > sum(unit.quantity for unit in depth.asks) * cls.MIN_RETURN:
        #     return TradeAction('buy')
        # if acquired and sum(unit.quantity for unit in depth.bids) < sum(unit.quantity for unit in depth.asks) / cls.MIN_RETURN:
        #     return TradeAction('sell')
        # return TradeAction(None)
        bids_coef, bids_intercept = cls.depth_linear_regression(depth.bids)
        asks_coef, asks_intercept = cls.depth_linear_regression(depth.asks)
        intersection = (bids_intercept - asks_intercept) / (asks_coef - bids_coef)
        logging.debug('Bid price: {}; ask price: {}; intersection: {}'.format(
            depth.bids[0].price, depth.asks[0].price, intersection))
        if not acquired and math.log(intersection / depth.asks[0].price) > cls.MIN_LOG_RETURN:
            # cls.plot(depth, bids_coef, bids_intercept, asks_coef, asks_intercept)
            return TradeAction('buy')
        if acquired and math.log(intersection / depth.bids[0].price) < -cls.MIN_LOG_RETURN:
            # cls.plot(depth, bids_coef, bids_intercept, asks_coef, asks_intercept)
            return TradeAction('sell')
        return TradeAction(None)
    
    @classmethod
    def plot(cls, depth, bids_coef, bids_intercept, asks_coef, asks_intercept):
        plt.plot(depth.bid_prices(), np.cumsum(depth.bid_quantities()))
        plt.plot(depth.ask_prices(), np.cumsum(depth.ask_quantities()))

        x = np.concatenate((depth.bid_prices(), depth.ask_prices()))
        plt.plot(x, bids_coef * x + bids_intercept)
        plt.plot(x, asks_coef * x + asks_intercept)

        plt.show()
