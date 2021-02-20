import logging

from model import TradeAction
from strategy.indicators import Indicators


class KlinesBollingerBandsStrategy:

    NB_PERIODS = 20
    STD_DEV_FACTOR = 1.

    def decide_action(self, klines, acquired):
        current_price = klines[-1].close_price

        typical_prices = [(kline.close_price + kline.high_price +
                           kline.low_price) / 3 for kline in klines]

        # Get current trend
        past_ma = Indicators.simple_moving_average(typical_prices, len(
            typical_prices) - self.NB_PERIODS, self.NB_PERIODS)

        # Get std deviation and MA until second to last close price (finished klines)
        std_deviation = Indicators.standard_deviation(
            typical_prices, len(typical_prices) - 2, self.NB_PERIODS)
        ma = Indicators.simple_moving_average(
            typical_prices, len(typical_prices) - 2, self.NB_PERIODS)

        if std_deviation != 0:
            logging.debug('Current price compared to Bollinger bands: {}; trend: {}'.format(
                (current_price - ma) / std_deviation, ma / past_ma - 1.))

        if not acquired and ma > past_ma and current_price < ma - self.STD_DEV_FACTOR * std_deviation:
            return TradeAction('buy')
        if acquired and ma < past_ma and current_price > ma + self.STD_DEV_FACTOR * std_deviation:
            return TradeAction('sell')
        return TradeAction(None)
