import logging
import math
import statistics

from model import TradeAction
from strategy.indicators import Indicators


class KlinesAvgLogRatioStrategy:

    NB_PERIODS = 72
    THRESHOLD = 0.0005

    def decide_action(self, klines, acquired):
        typical_prices = [(kline.close_price + kline.high_price +
                           kline.low_price) / 3 for kline in klines]

        log_ratios = [
                math.log(typical_prices[-self.NB_PERIODS + i] / typical_prices[-self.NB_PERIODS + i - 1])
                for i in range(self.NB_PERIODS)
            ]

        avg_log_ratio = statistics.fmean(log_ratios)
        #print(f'Avg log ratio: {avg_log_ratio}')

        if not acquired and avg_log_ratio > self.THRESHOLD:
            return TradeAction('buy')
        if acquired and avg_log_ratio < -self.THRESHOLD:
            return TradeAction('sell')
        return TradeAction(None)
