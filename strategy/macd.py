import logging
from datetime import datetime, timedelta

from strategy.indicators import Indicators
from model import TradeAction


class MacdStrategy:

    MACD_TO_CURRENT_RATIO = 0.

    @classmethod
    def decide_action_from_data(cls, klines):
        current_price = klines[-1].close_price
        typical_prices = [(kline.close_price + kline.high_price + kline.low_price) / 3. for kline in klines]
        macd = Indicators.macd_difference(typical_prices, len(klines) - 1)
        ratio = macd / current_price
        condition_macd_buy = ratio > cls.MACD_TO_CURRENT_RATIO
        condition_macd_sell = ratio < -cls.MACD_TO_CURRENT_RATIO
        logging.debug('MACD difference: {}; ratio: {}'.format(macd, ratio))
        if condition_macd_buy:
            return TradeAction('buy')
        elif condition_macd_sell:
            return TradeAction('sell')
        return TradeAction(None)
