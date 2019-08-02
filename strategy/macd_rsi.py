import logging

import matplotlib.pyplot as plt

from strategy.indicators import Indicators
from model import TradeAction

class MacdRsiStrategy:
    
    RSI_GAP = .19
    RSI_RANGE = 14

    @classmethod
    def decide_action_from_data(cls, klines):
        if not klines:
            return TradeAction(None)
        kline_prices = [kline.close_price for kline in klines]
        macd_last = Indicators.macd_difference(kline_prices, len(klines) - 1)
        macd_previous = Indicators.macd_difference(kline_prices, len(klines) - 2)
        condition_macd_buy = macd_last > 0. and macd_previous < 0.
        condition_macd_sell = macd_last < 0. and macd_previous > 0.
        rsi = Indicators.rsi(kline_prices, len(klines) - cls.RSI_RANGE, len(klines))
        condition_rsi_buy = rsi < .5 - cls.RSI_GAP
        condition_rsi_sell = rsi > .5 + cls.RSI_GAP
        logging.debug('RSI: {}; MACD difference: {}'.format(rsi, macd_last))
        if condition_macd_buy and condition_rsi_buy:
            return TradeAction('buy')
        elif condition_macd_sell and condition_rsi_sell:
            return TradeAction('sell')
        else:
            return TradeAction(None)

