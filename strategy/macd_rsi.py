import logging

import matplotlib.pyplot as plt

from strategy.indicators import Indicators
from model import TradeAction

class MacdRsiStrategy:
    
    RSI_GAP = .0
    RSI_RANGE = 70

    @classmethod
    def decide_action_from_data(cls, klines):
        if not klines:
            return TradeAction(None)
        typical_prices = [(kline.close_price + kline.high_price + kline.low_price) / 3. for kline in klines]
        macd_last = Indicators.macd_difference(typical_prices, len(klines) - 1)
        condition_macd_buy = macd_last > 0.
        condition_macd_sell = macd_last < 0.
        rsi = Indicators.rsi(typical_prices, len(klines) - cls.RSI_RANGE, len(klines))
        condition_rsi_buy = rsi > .5 + cls.RSI_GAP
        condition_rsi_sell = rsi < .5 - cls.RSI_GAP
        logging.debug('RSI: {}; MACD difference: {}'.format(rsi, macd_last))
        if condition_macd_buy and condition_rsi_buy:
            return TradeAction('buy')
        elif condition_macd_sell and condition_rsi_sell:
            return TradeAction('sell')
        else:
            return TradeAction(None)
