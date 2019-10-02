import logging

from strategy.indicators import Indicators
from model import TradeAction


class BullBearMacdEmaStrategy:

    FAST_EMA_RANGE = 10
    SLOW_EMA_RANGE = 200
    EMA_GAP = .005

    bear_transactions_nb = 0
    bull_transactions_nb = 0

    @classmethod
    def decide_action_from_data(cls, klines):
        current_price = klines[-1].close_price
        typical_prices = [(kline.close_price + kline.high_price + kline.low_price) / 3 for kline in klines]

        slow_ema = Indicators.exp_moving_average(typical_prices, len(klines) - 1, cls.SLOW_EMA_RANGE)
        fast_ema = Indicators.exp_moving_average(typical_prices, len(klines) - 1, cls.FAST_EMA_RANGE)
    
        condition_ema_buy = current_price < (1. - cls.EMA_GAP) * fast_ema
        condition_ema_sell = current_price > (1. + cls.EMA_GAP) * fast_ema

        if fast_ema < slow_ema:
            # Bear
            macd_last = Indicators.macd_difference(typical_prices, len(klines) - 1)
            macd_previous = Indicators.macd_difference(typical_prices, len(klines) - 2)
            condition_macd_buy = macd_last > 0. and macd_previous < 0.
            condition_macd_sell = macd_last < 0. and macd_previous > 0.
            logging.debug('Bearish; MACD difference: {}; ratio to EMA: {}'.format(macd_last, current_price / fast_ema))
            if condition_ema_buy and condition_macd_buy:
                cls.bear_transactions_nb += 1
                return TradeAction('buy')
            elif condition_ema_sell and condition_macd_sell:
                cls.bear_transactions_nb += 1
                return TradeAction('sell')
        
        else:
            # Bull
            logging.debug('Bullish; Ratio to EMA: {}'.format(current_price / fast_ema))
            if condition_ema_buy:
                cls.bull_transactions_nb += 1
                return TradeAction('buy')
            elif condition_ema_sell:
                cls.bull_transactions_nb += 1
                return TradeAction('sell')

        return TradeAction(None)
