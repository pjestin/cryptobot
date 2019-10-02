import unittest

from strategy.macd import MacdStrategy
import read_data


class MacdStrategyTest(unittest.TestCase):

    TEST_DATA_FILE = 'data/binance_klines_BTCUSDT_1h_1569445200000.json'

    def setUp(self):
        MacdStrategy.MACD_TO_CURRENT_RATIO = 0.
        MacdStrategy.TIME_DIFF_FACTOR = .9
        self.klines = read_data.read_klines_from_json(file_path=self.TEST_DATA_FILE)

    def test_sell_trade_action(self):
        action = MacdStrategy.decide_action_from_data(self.klines, None)
        self.assertFalse(action.is_buy())
        self.assertTrue(action.is_sell())

    def test_no_trade_previous_transac(self):
        action = MacdStrategy.decide_action_from_data(self.klines, 1569702600000)
        self.assertFalse(action.is_buy())
        self.assertFalse(action.is_sell())
