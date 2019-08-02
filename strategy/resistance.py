import logging

import pandas as pd

from strategy import supres
from strategy.indicators import Indicators
from model import TradeAction


class ResistanceStrategy:

    GAIN = .02
    LOSS = .005

    @classmethod
    def decide_action_from_data(cls, klines, previous_price=None, acquired=None):
        if acquired and previous_price and \
            (klines[-1].close_price > (1 + cls.GAIN) * previous_price \
                or klines[-1].close_price < (1 - cls.LOSS) * previous_price):
            return TradeAction('sell')
        elif not acquired:
            kline_prices = [kline.close_price for kline in klines]
            # rsi = Indicators.rsi(kline_prices, 0, len(klines))
            # low = pd.Series([kline.low_price for kline in klines])
            # high = pd.Series([kline.high_price for kline in klines])
            prices = pd.Series(kline_prices)
            ret_df = supres.supres(prices, prices, n=20, min_touches=2, stat_likeness_percent=1.5, bounce_percent=5.)
            if ret_df['res_break'].iloc[-1]: #and rsi < .49:
                return TradeAction('buy')
        return TradeAction(None)
        # return ret_df