import logging
import math

import numpy as np
from sklearn.linear_model import LinearRegression

from model import TradeAction
from strategy.indicators import Indicators


class DepthLinearRegressionStrategy:

    MIN_LOG_RETURN = .002

    @classmethod
    def decide_action(cls, depth, acquired):
        normalized_exp_weights = Indicators.get_exp_weights(len(depth.bids))
        bid_quantity_ema = np.dot(normalized_exp_weights, depth.bid_quantities())
        ask_quantity_ema = np.dot(normalized_exp_weights, depth.ask_quantities())
        quantity_sum_log_ratio = math.log(bid_quantity_ema / ask_quantity_ema)
        if not acquired and quantity_sum_log_ratio > .2:
            return TradeAction('buy')
        if acquired and quantity_sum_log_ratio < -.2:
            return TradeAction('sell')
        return TradeAction(None)
