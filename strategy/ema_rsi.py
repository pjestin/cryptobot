import logging

from strategy.indicators import Indicators
from model import TradeAction


class EmaRsiStrategy:
    
    BULL_RSI_PARAMS = {
        'range': 15,
        'high': .9,
        'low': .5
    }
    BEAR_RSI_PARAMS = {
        'range': 15,
        'high': .5,
        'low': .1
    }
    
    SLOW_EMA_RANGE = 1000
    FAST_EMA_RANGE = 50
    
    @classmethod
    def decide_action_from_data(cls, klines):
        if not klines:
            return TradeAction(None)
        close_prices = [kline.close_price for kline in klines]

        slow_ema = Indicators.exp_moving_average(close_prices, len(klines) - 1, cls.SLOW_EMA_RANGE)
        fast_ema = Indicators.exp_moving_average(close_prices, len(klines) - 1, cls.FAST_EMA_RANGE)

        params = cls.BEAR_RSI_PARAMS if fast_ema < slow_ema else cls.BULL_RSI_PARAMS
        # params = cls.BEAR_RSI_PARAMS

        # logging.info('Current price: {}'.format(close_prices[-1]))
        # logging.info('Bear' if fast_ema < slow_ema else 'Bull')

        rsi = Indicators.rsi(close_prices, len(klines) - params['range'], len(klines))
        if rsi > params['high']:
            return TradeAction('sell')
        elif rsi < params['low']:
            return TradeAction('buy')

        return TradeAction(None)
