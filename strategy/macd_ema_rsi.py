import logging

import matplotlib.pyplot as plt

from strategy.indicators import Indicators
from model import TradeAction

class MacdEmaRsiStrategy:
    
    RSI_RANGE = 40
    RSI_GAP = .2
    EMA_RANGE = 20
    EMA_GAP = .01

    @classmethod
    def decide_action_from_data(cls, klines):
        if not klines:
            return TradeAction(None)
        current_price = klines[-1].close_price
        typical_prices = [(kline.close_price + kline.high_price + kline.low_price) / 3 for kline in klines]
        macd_last = Indicators.macd_difference(typical_prices, len(klines) - 1)
        macd_previous = Indicators.macd_difference(typical_prices, len(klines) - 2)
        ema = Indicators.exp_moving_average(typical_prices, len(klines) - 1, cls.EMA_RANGE)
        condition_macd_buy = macd_last > 0. and macd_previous < 0.
        condition_macd_sell = macd_last < 0. and macd_previous > 0.
        rsi = Indicators.rsi(typical_prices, len(klines) - cls.RSI_RANGE, len(klines))
        condition_rsi_buy = rsi < .5 - cls.RSI_GAP
        condition_rsi_sell = rsi > .5 + cls.RSI_GAP
        condition_ema_buy = current_price < (1. - cls.EMA_GAP) * ema
        condition_ema_sell = current_price > (1. + cls.EMA_GAP) * ema
        logging.debug('RSI: {}; MACD difference: {}; ratio to EMA: {}'.format(rsi, macd_last, current_price / ema))
        if condition_macd_buy and (condition_rsi_buy or condition_rsi_buy):
            return TradeAction('buy')
        elif condition_macd_sell and (condition_ema_sell or condition_ema_sell):
            return TradeAction('sell')
        else:
            return TradeAction(None)

