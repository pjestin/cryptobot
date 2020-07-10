import logging
import math

import numpy as np

from model import TradeAction


class DepthOrderBookImbalanceStrategy:

    MAX_PRICE_SPREAD = 0.02
    MIN_QUANTITY_RATIO = 0.3

    @classmethod
    def decide_action(cls, depth, acquired):
        best_bid_price = depth.bids[0][0]
        bid_quantity = 0.
        for price, quantity in depth.bids:
            if math.log(price / best_bid_price) < -cls.MAX_PRICE_SPREAD:
                break
            bid_quantity += quantity

        best_ask_price = depth.asks[0][0]
        ask_quantity = 0.
        for price, quantity in depth.asks:
            if math.log(price / best_ask_price) > cls.MAX_PRICE_SPREAD:
                break
            ask_quantity += quantity

        quantity_log_ratio = math.log(bid_quantity / ask_quantity)
        logging.debug('Bid vs ask quantity ratio: {}'.format(quantity_log_ratio))
        if not acquired and quantity_log_ratio > cls.MIN_QUANTITY_RATIO:
            return TradeAction('buy')
        if acquired and quantity_log_ratio < -cls.MIN_QUANTITY_RATIO:
            return TradeAction('sell')
        return TradeAction(None)
