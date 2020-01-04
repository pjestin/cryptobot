import logging

from strategy import supres
from strategy.indicators import Indicators
from model import TradeAction


class VolumeEmaStrategy:

    VOLUME_RANGE = .3

    @classmethod
    def get_ema_range(cls, klines):
        total_volume = sum(kline.volume for kline in klines)
        target_volume = cls.VOLUME_RANGE * total_volume
        aggregate_volume = 0
        for idx in range(0, len(klines)):
            aggregate_volume += klines[-idx].volume
            if aggregate_volume > target_volume:
                return idx
        return None

    @classmethod
    def decide_action_from_data(cls, klines):
        current_price = klines[-1].close_price
        close_prices = [kline.close_price for kline in klines]
        ema_range = cls.get_ema_range(klines)
        ema = Indicators.exp_moving_average(
            close_prices, len(klines) - 1, ema_range)
        previous_ema = Indicators.exp_moving_average(
            close_prices, len(klines) - 2, ema_range)
        condition_ema_buy = ema > previous_ema and current_price > ema
        condition_ema_sell = ema < previous_ema and current_price < ema
        logging.debug('Ratio to EMA: {}'.format(current_price / ema))
        if condition_ema_buy:
            return TradeAction('buy')
        elif condition_ema_sell:
            return TradeAction('sell')
        return TradeAction(None)
