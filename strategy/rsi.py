import logging

from strategy.indicators import Indicators
from model import TradeAction


class RsiStrategy:

    RSI_RANGE = 70
    RSI_GAP = .01
    
    @classmethod
    def decide_action_from_data(cls, klines):
        if not klines:
            return TradeAction(None)
        typical_prices = [(kline.close_price + kline.high_price + kline.low_price) / 3. for kline in klines]

        rsi = Indicators.rsi(typical_prices, len(klines) - cls.RSI_RANGE, len(klines))
        if rsi > .5 + cls.RSI_GAP:
            return TradeAction('sell')
        elif rsi < .5 - cls.RSI_GAP:
            return TradeAction('buy')

        return TradeAction(None)
