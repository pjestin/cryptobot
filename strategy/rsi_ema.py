import logging

from model import TradeAction
from strategy.indicators import Indicators


class KlinesRsiEmaStrategy:
    def decide_action(self, klines, acquired) -> TradeAction:
        close_prices = [kline.close_price for kline in klines]

        ema_short = Indicators.exp_moving_average(
            close_prices, len(close_prices) - 1, 20
        )
        ema_long = Indicators.exp_moving_average(
            close_prices, len(close_prices) - 1, 100
        )

        rsi = Indicators.rsi(close_prices, len(close_prices) - 24, len(close_prices))

        if not acquired and rsi < 0.45 and ema_short > ema_long:
            return TradeAction("buy")

        if acquired and rsi > 0.55 and ema_short < ema_long:
            return TradeAction("sell")

        return TradeAction(None)
