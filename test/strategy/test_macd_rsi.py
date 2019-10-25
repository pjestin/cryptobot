import unittest

from strategy.macd_rsi import MacdRsiStrategy
from interface import read_data


class MacdRsiStrategyTest(unittest.TestCase):

    TEST_DATA_FILE_1 = 'test/data/binance_klines_BTCUSDT_1h_1569445200000.json'
    TEST_DATA_FILE_2 = 'test/data/binance_klines_BTCUSDT_1h_1569618000000.json'

    def setUp(self):
        MacdRsiStrategy.RSI_GAP = 0.
        MacdRsiStrategy.RSI_RANGE = 70
        self.klines1 = read_data.read_klines_from_json(file_path=self.TEST_DATA_FILE_1)
        self.klines2 = read_data.read_klines_from_json(file_path=self.TEST_DATA_FILE_2)

    def test_sell_trade_action(self):
        action = MacdRsiStrategy.decide_action_from_data(self.klines1)
        self.assertFalse(action.is_buy())
        self.assertTrue(action.is_sell())

    def test_buy_trade_action(self):
        action = MacdRsiStrategy.decide_action_from_data(self.klines2)
        self.assertTrue(action.is_buy())
        self.assertFalse(action.is_sell())
