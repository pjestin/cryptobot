import unittest

from strategy.macd import MacdStrategy
import read_data


class MacdStrategyTest(unittest.TestCase):

    TEST_DATA_FILE_1 = 'data/binance_klines_BTCUSDT_1h_1569445200000.json'
    TEST_DATA_FILE_2 = 'data/binance_klines_BTCUSDT_1h_1569618000000.json'

    def setUp(self):
        MacdStrategy.MACD_TO_CURRENT_RATIO = 0.
        MacdStrategy.TIME_DIFF_FACTOR = .9
        self.klines1 = read_data.read_klines_from_json(file_path=self.TEST_DATA_FILE_1)
        self.klines2 = read_data.read_klines_from_json(file_path=self.TEST_DATA_FILE_2)

    def test_sell_trade_action(self):
        action = MacdStrategy.decide_action_from_data(self.klines1, None)
        self.assertFalse(action.is_buy())
        self.assertTrue(action.is_sell())

    def test_buy_trade_action(self):
        action = MacdStrategy.decide_action_from_data(self.klines2, None)
        self.assertTrue(action.is_buy())
        self.assertFalse(action.is_sell())

    def test_no_trade_previous_transac(self):
        action = MacdStrategy.decide_action_from_data(self.klines1, 1569702600000)
        self.assertFalse(action.is_buy())
        self.assertFalse(action.is_sell())

    def test_sell_trade_previous_transac(self):
        action = MacdStrategy.decide_action_from_data(self.klines1, 1569700000000)
        self.assertFalse(action.is_buy())
        self.assertTrue(action.is_sell())
