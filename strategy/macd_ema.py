import logging

import pandas as pd

from strategy import supres
from strategy.indicators import Indicators
from model import TradeAction


class MacdEmaStrategy:

    EMA_RANGE = 20
    EMA_GAP = 0.01

    @classmethod
    def decide_action_from_data(cls, klines):
        current_price = klines[-1].close_price
        typical_prices = [(kline.close_price + kline.high_price + kline.low_price) / 3 for kline in klines]
        ema = Indicators.exp_moving_average(typical_prices, len(klines) - 1, cls.EMA_RANGE)
        macd_last = Indicators.macd_difference(typical_prices, len(klines) - 1)
        macd_previous = Indicators.macd_difference(typical_prices, len(klines) - 2)
        condition_macd_buy = macd_last > 0. and macd_previous < 0.
        condition_macd_sell = macd_last < 0. and macd_previous > 0.
        condition_ema_buy = current_price < (1. - cls.EMA_GAP) * ema
        condition_ema_sell = current_price > (1. + cls.EMA_GAP) * ema
        logging.debug('MACD difference: {}; ratio to EMA: {}'.format(macd_last, current_price / ema))
        if condition_ema_buy and condition_macd_buy:
            return TradeAction('buy')
        elif condition_ema_sell and condition_macd_sell:
            return TradeAction('sell')
        return TradeAction(None)