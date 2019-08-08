import logging

from strategy import supres
from strategy.indicators import Indicators
from model import TradeAction


class MacEmaRatioStrategy:

    RATIO_GAP = .05
    EMA_GAP = .01
    EMA_RANGE = 20

    @classmethod
    def decide_action_from_data(cls, klines, previous_price=None, acquired=None):
        current_price = klines[-1].close_price
        typical_prices = [(kline.close_price + kline.high_price + kline.low_price) / 3 for kline in klines]
        ema = Indicators.exp_moving_average(typical_prices, len(klines) - 1, cls.EMA_RANGE)
        macd_last = Indicators.macd_difference(typical_prices, len(klines) - 1)
        macd_previous = Indicators.macd_difference(typical_prices, len(klines) - 2)
        condition_macd_buy = macd_last > 0. and macd_previous < 0.
        condition_macd_sell = macd_last < 0. and macd_previous > 0.
        condition_ema_buy = current_price < (1 - cls.EMA_GAP) * ema
        condition_ema_sell = current_price > (1 + cls.EMA_GAP) * ema
        condition_ratio_buy = not acquired and previous_price and current_price < (1 - cls.RATIO_GAP) * previous_price
        condition_ratio_sell = acquired and previous_price and current_price > (1 + cls.RATIO_GAP) * previous_price
        
        if condition_macd_buy and (condition_ema_buy or condition_ratio_buy):
            return TradeAction('buy')
        elif condition_macd_sell and (condition_ema_sell or condition_ratio_sell):
            return TradeAction('sell')
        else:
            return TradeAction(None)
