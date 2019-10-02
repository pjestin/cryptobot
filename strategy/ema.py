import logging

from strategy import supres
from strategy.indicators import Indicators
from model import TradeAction


class EmaStrategy:

    EMA_RANGE = 10
    EMA_GAP = 0.001

    @classmethod
    def decide_action_from_data(cls, klines):
        current_price = klines[-1].close_price
        typical_prices = [(kline.close_price + kline.high_price + kline.low_price) / 3 for kline in klines]
        ema = Indicators.exp_moving_average(typical_prices, len(klines) - 1, cls.EMA_RANGE)
        condition_ema_buy = current_price < (1. - cls.EMA_GAP) * ema
        condition_ema_sell = current_price > (1. + cls.EMA_GAP) * ema
        logging.debug('Ratio to EMA: {}'.format(current_price / ema))
        if condition_ema_buy:
            return TradeAction('buy')
        elif condition_ema_sell:
            return TradeAction('sell')
        return TradeAction(None)
