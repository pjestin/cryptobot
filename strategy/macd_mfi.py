import logging

import matplotlib.pyplot as plt

from strategy.indicators import Indicators
from model import TradeAction

class MacdMfiStrategy:
    
    MFI_GAP = .15
    MFI_RANGE = 14

    @classmethod
    def decide_action_from_data(cls, klines):
        if not klines:
            return TradeAction(None)
        typical_prices = [(kline.close_price + kline.high_price + kline.low_price) / 3 for kline in klines]
        volumes = [kline.volume for kline in klines]
        macd_last = Indicators.macd_difference(typical_prices, len(klines) - 1)
        macd_previous = Indicators.macd_difference(typical_prices, len(klines) - 2)
        condition_macd_buy = macd_last > 0. and macd_previous < 0.
        condition_macd_sell = macd_last < 0. and macd_previous > 0.
        mfi = Indicators.mfi(typical_prices, volumes, len(klines) - cls.MFI_RANGE, len(klines))
        condition_rsi_buy = mfi < .5 - cls.MFI_GAP
        condition_rsi_sell = mfi > .5 + cls.MFI_GAP
        logging.debug('MFI: {}; MACD difference: {}'.format(mfi, macd_last))
        if condition_macd_buy and condition_rsi_buy:
            return TradeAction('buy')
        elif condition_macd_sell and condition_rsi_sell:
            return TradeAction('sell')
        else:
            return TradeAction(None)

