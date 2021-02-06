import logging

from model import TradeAction
from strategy.indicators import Indicators


class KlinesBollingerBandsStrategy:

    NB_PERIODS = 20
    STD_DEV_FACTOR = 1.
    
    def decide_action(self, klines, acquired):
        prices = [kline.close_price for kline in klines]

        # Get std deviation and MA until second to last close price (finished klines)
        std_deviation = Indicators.standard_deviation(prices, len(prices) - 2, self.NB_PERIODS)
        ma = Indicators.simple_moving_average(prices, len(prices) - 2, self.NB_PERIODS)

        # Compare with current price
        current_price = prices[-1]

        logging.debug('Current price compared to Bollinger bands: {}'.format((current_price - ma) / std_deviation))

        if not acquired and current_price < ma - self.STD_DEV_FACTOR * std_deviation:
            return TradeAction('buy')
        if acquired and current_price > ma + self.STD_DEV_FACTOR * std_deviation:
            return TradeAction('sell')
        return TradeAction(None)
